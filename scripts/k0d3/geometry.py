# SPDX-License-Identifier: MIT
"""Key geometry for k0d3ball35 (r2: two separate PCBs).

Everything is derived from hardware/layout/k0d3ball35.yaml. Coordinates are in mm,
x outward (pinky), y downward (towards the user), origin at the centre of the
middle-column top key. Both halves use this frame, which is handedness-neutral: it
describes the right half as seen from the top and the left half as seen through the
board. Every physical artefact of the left half (PCB, case, lid) therefore mirrors x
(`Layout.to_board`, `Layout.board_sx`); the frame itself, points-*.json, outline-*.dxf
and the docs tables stay in frame coordinates. The frame matches KiCad's screen
coordinate system, so the PCB generator only adds the mirror and a page offset.

`load_layout("left")` and `load_layout("right")` return a Layout whose `cfg` is the
global configuration merged with the half's block from `halves:` (lists are
concatenated, mappings merged, scalars taken from the half).
"""
from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Iterable

import yaml
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity

REPO = Path(__file__).resolve().parents[2]
LAYOUT_FILE = REPO / "hardware" / "layout" / "k0d3ball35.yaml"
HALVES = ("left", "right")


@dataclass
class Key:
    name: str
    row: int
    col: int
    x: float
    y: float
    rotation: float = 0.0  # degrees, KiCad convention (positive = counter-clockwise)
    kind: str = "finger"   # finger | thumb

    @property
    def ref(self) -> str:
        return f"SW{self.row}{self.col}"

    @property
    def diode_ref(self) -> str:
        return f"D{self.row}{self.col}"

    @property
    def net(self) -> str:
        return f"SW{self.row}{self.col}"


@dataclass
class Layout:
    half: str
    cfg: dict                       # global config merged with the half's block
    keys: list[Key]
    outline: Polygon
    ball_center: tuple[float, float] | None
    source: Path = field(default=LAYOUT_FILE)

    # ----- convenience -------------------------------------------------------
    @property
    def pitch(self) -> tuple[float, float]:
        return self.cfg["pitch"]["x"], self.cfg["pitch"]["y"]

    @property
    def keycap(self) -> tuple[float, float]:
        return self.cfg["keycap"]["width"], self.cfg["keycap"]["height"]

    @property
    def has_ball(self) -> bool:
        return self.ball_center is not None

    # ----- board frame ---------------------------------------------------------
    @property
    def board_sx(self) -> int:
        """x sign from the layout frame to the physical board: -1 on the left half, else 1."""
        return -1 if self.half == "left" else 1

    def to_board(self, x: float, y: float) -> tuple[float, float]:
        """Layout-frame point to board coordinates (top view, before the page offset)."""
        return (self.board_sx * x, y)

    @property
    def thumbs(self) -> list[Key]:
        return [k for k in self.keys if k.kind == "thumb"]

    def key(self, row: int, col: int) -> Key:
        for k in self.keys:
            if k.row == row and k.col == col:
                return k
        raise KeyError((row, col))

    def keycap_polygon(self, key: Key) -> Polygon:
        w, h = self.keycap
        return rotated_box(key.x, key.y, w, h, key.rotation)

    def cradle_polygon(self) -> Polygon | None:
        if not self.has_ball:
            return None
        return Point(*self.ball_center).buffer(self.cfg["trackball"]["cradle_diameter"] / 2, 64)

    def notch_polygon(self) -> Polygon | None:
        """Notch in the PCB edge where the ball pocket docks: an octagon whose corner towards
        the keys and the inner column is square, so the cradle housing and the sensor board
        pass it on their way into the pocket (issues/mech-cradle-notch-relief.md)."""
        if not self.has_ball:
            return None
        tb = self.cfg["trackball"]
        return notch_shape(*self.ball_center, tb["cradle_diameter"] / 2 + tb["pocket"]["notch_clearance"],
                           tb["pocket"].get("square_corner", False))

    def pocket_polygon(self) -> Polygon | None:
        """Outer wall of the case pocket around the cradle (reference for the case)."""
        if not self.has_ball:
            return None
        tb = self.cfg["trackball"]
        return Point(*self.ball_center).buffer(tb["cradle_diameter"] / 2 + tb["pocket"]["wall"], 64)

    def housing_box(self) -> Polygon | None:
        """Cradle housing on the case floor (below the PCB plane).

        Since r2.4 the sensor module is tilted and sits beside the ball rather than under it, so
        the housing is no longer symmetric: `housing_offset` shifts the box off the ball centre
        towards the side the module leans to (+x for sensor_az = 180, the window azimuth is sensor_az + 180).
        """
        if not self.has_ball:
            return None
        pk = self.cfg["trackball"]["pocket"]
        h = pk["housing"]
        off = pk.get("housing_offset", {"x": 0.0, "y": 0.0})
        bx = self.ball_center[0] + off.get("x", 0.0)
        by = self.ball_center[1] + off.get("y", 0.0)
        return box(bx - h["x"] / 2, by - h["y"] / 2, bx + h["x"] / 2, by + h["y"] / 2)

    def housing_footprint(self) -> Polygon | None:
        """Pocket outline at floor level: housing plus clearance plus case wall, 3 mm corner radius."""
        if not self.has_ball:
            return None
        pk = self.cfg["trackball"]["pocket"]
        grow = pk["housing_clearance"] + pk["wall"]
        return self.housing_box().buffer(grow - 3.0, join_style=2).buffer(3.0, 16).simplify(0.05)

    def case_screws(self) -> list[tuple[float, float]]:
        if not self.has_ball:
            return []
        # On the y axis through the ball: the sensor sleeve sits on +x and the bearings at 60, 180
        # and 300 degrees, so 90/270 is the free pair (cradle.scad, tests/test_cradle.py).
        sp = self.cfg["trackball"]["pocket"]["case_screw_spacing"]
        bx, by = self.ball_center
        return [(bx, round(by - sp / 2, 3)), (bx, round(by + sp / 2, 3))]

    @property
    def fpc_side(self) -> str:
        """Face J1 is assembled on: "top" (key side, r2.2) or "bottom"."""
        f = self.cfg.get("fpc")
        return f.get("side", "bottom") if f else ""

    def fpc_box(self) -> Polygon | None:
        """J1 courtyard in the layout frame (FH12 footprint: 9.2 x 5.6 around a centre
        offset 0.6 mm towards the cable mouth, which is the connector's local +y)."""
        f = self.cfg.get("fpc")
        if not f:
            return None
        return rotated_box(f["center"]["x"], f["center"]["y"], 9.2, 5.6, f["rotation"], offset=(0.0, 0.6))

    def fpc_mouth(self) -> tuple[float, float] | None:
        """Centre of the cable mouth (front face of the connector body), layout frame."""
        f = self.cfg.get("fpc")
        if not f:
            return None
        th = math.radians(f["rotation"])
        return (f["center"]["x"] + 3.0 * math.sin(th), f["center"]["y"] + 3.0 * math.cos(th))

    def cable_corridor(self) -> Polygon | None:
        """Where the FFC lies on the board: a band from the cable mouth out past the notch edge.

        Only meaningful for the top-side connector of r2.2. No part and no piece of the case
        (in particular the lid lip) may sit in it."""
        if not self.has_ball or self.fpc_side != "top":
            return None
        pk = self.cfg["trackball"]["pocket"]
        w = pk["cable_width"]
        mx, my = self.fpc_mouth()
        bx, by = self.ball_center
        band = box(mx - w / 2, min(my, by), mx + w / 2, max(my, by))
        return band.intersection(self.outline.buffer(1.0, join_style=2))

    def sensor_board(self) -> Polygon:
        """Plan view of the sensor module in the layout frame.

        Since r2.4 the module is tilted, so this is its PROJECTION, not the board itself, and it
        does not sit on the ball axis: `sensor_board_offset` moves it along the tilt azimuth.
        Both numbers come from the cradle (STACK board_reach / sensor_angle in
        hardware/trackball-cradle/stack.json) the same way cup_envelope does.
        """
        pk = self.cfg["trackball"]["pocket"]
        sb = pk["sensor_board"]
        off = pk.get("sensor_board_offset", {"x": 0.0, "y": 0.0})
        bx = self.ball_center[0] + off.get("x", 0.0)
        by = self.ball_center[1] + off.get("y", 0.0)
        return box(bx - sb["x"] / 2, by - sb["y"] / 2, bx + sb["x"] / 2, by + sb["y"] / 2)

    def insertion_corridor(self) -> Polygon | None:
        """Plan view of the trackball module: cradle housing plus the sensor board inside it.

        Everything in this area passes the PCB plane when the module is lowered into its
        pocket, so the board must not cover any of it: that is what makes the module a
        cartridge that drops in and lifts out with the PCB fitted
        (issues/mech-cradle-notch-relief.md)."""
        if not self.has_ball:
            return None
        return unary_union([self.housing_box(), self.sensor_board()])

    def battery_bay(self) -> Polygon:
        """Rectangle on the back of the PCB where the cell lies (in the case well under the controller)."""
        b = self.cfg["battery"]["bay"]
        return box(b["center"]["x"] - b["size"]["x"] / 2, b["center"]["y"] - b["size"]["y"] / 2,
                   b["center"]["x"] + b["size"]["x"] / 2, b["center"]["y"] + b["size"]["y"] / 2)

    def back_parts(self) -> dict[str, Polygon]:
        """Courtyards of everything that is assembled on the back of the PCB (layout frame):
        power switch, reset button, JST, battery pads, hot-swap sockets and the FPC connector.
        Switch bodies are included because the socket boss holes sit inside them."""
        cfg = self.cfg
        parts: dict[str, Polygon] = {}
        ps = cfg["power_switch"]
        parts["PS1"] = rotated_box(ps["center"]["x"], ps["center"]["y"], 8.4, 5.4, ps["rotation"], offset=(0.0, 0.6))
        rb = cfg["reset_button"]
        parts["RB1"] = rotated_box(rb["center"]["x"], rb["center"]["y"], 5.4, 3.5, rb["rotation"])
        j3 = cfg["battery_jst"]
        parts["J3"] = rotated_box(j3["center"]["x"], j3["center"]["y"], 9.4, 8.4, j3["rotation"], offset=(0.0, 0.3))
        j2 = cfg["battery_pads"]
        parts["J2"] = rotated_box(j2["center"]["x"], j2["center"]["y"], 4.6, 2.6, j2["rotation"])
        for k in self.keys:
            parts[k.ref] = rotated_box(k.x, k.y, cfg["switch_body"], cfg["switch_body"], k.rotation)
            # CPG135001S30 hot-swap socket on the back incl. its solder tabs: board-local x
            # -4.8..10.2, y -8.9..-2.0. The footprint is chiral and NOT mirrored on the left board,
            # so in the (mirrored) layout frame the socket points the other way there.
            parts[k.ref + " socket"] = rotated_box(k.x, k.y, 15.0, 6.9, k.rotation, offset=(self.board_sx * 2.7, -5.45))
            # SOD-123 diode 6 mm south of the key centre (netlist.build_components), courtyard 4.6 x 2.2
            parts[k.diode_ref] = rotated_box(k.x, k.y, 4.6, 2.2, k.rotation, offset=(0.0, 6.0))
        fp = self.fpc_box()
        if fp is not None and self.fpc_side == "bottom":
            parts["J1"] = fp
        return parts

    def under_switch(self, key: Key) -> list[tuple[str, Polygon, float]]:
        """What stands out of the PCB underside at one switch, as (name, polygon in the layout
        frame, height in mm): the hot-swap socket body (outline from the kiswitch footprint
        SW_Hotswap_Kailh_Choc_V1, B.Fab), its two solder tabs on their pads, the switch's two side
        pegs and its centre post (they come about 1 mm through a 1.6 mm board) and the diode.
        Board-local shapes are mirrored in x on the left half, like everything physical."""
        sx = self.board_sx
        local = [
            ("socket body", box(-2.275, -8.275, 2.475, -3.625), SOCKET_H),
            ("socket body", box(2.475, -6.075, 7.575, -1.425), SOCKET_H),
            ("socket tab", box(-4.775, -7.45, -2.225, -5.45), SOCKET_H),
            ("socket tab", box(7.225, -5.05, 9.775, -2.55), SOCKET_H),
            ("side peg", Point(-5.5, 0).buffer(0.85, 32), PEG_OUT),
            ("side peg", Point(5.5, 0).buffer(0.85, 32), PEG_OUT),
            ("centre post", Point(0, 0).buffer(1.7, 32), PEG_OUT),
            ("diode", box(-2.3, 4.9, 2.3, 7.1), 1.2),
        ]
        out = []
        for name, shape, h in local:
            # board frame: rotate about the switch (KiCad sign), then mirror into the layout frame
            g = affinity.rotate(shape, -sx * key.rotation, origin=(0, 0))
            g = affinity.scale(g, xfact=sx, origin=(0, 0))
            out.append((f"{key.ref} {name}", affinity.translate(g, key.x, key.y), h))
        return out

    def front_parts(self) -> dict[str, Polygon]:
        """Courtyards of everything assembled on the key side of the PCB besides switches and
        keycaps: since r2.2 that is J1 and the FFC corridor on the right half."""
        parts: dict[str, Polygon] = {}
        fp = self.fpc_box()
        if fp is not None and self.fpc_side == "top":
            parts["J1"] = fp
            corr = self.cable_corridor()
            if corr is not None and not corr.is_empty:
                parts["FFC"] = corr
        return parts

    def bounds(self) -> tuple[float, float, float, float]:
        return self.outline.bounds

    # ----- export -------------------------------------------------------------
    def to_dict(self) -> dict:
        minx, miny, maxx, maxy = self.outline.bounds
        tb = None
        if self.has_ball:
            t = self.cfg["trackball"]
            tb = {**t, "center": {"x": self.ball_center[0], "y": self.ball_center[1]},
                  "notch": [[round(x, 3), round(y, 3)] for x, y in self.notch_polygon().exterior.coords],
                  "pocket_diameter": t["cradle_diameter"] + 2 * t["pocket"]["wall"],
                  "housing_footprint": [[round(x, 3), round(y, 3)] for x, y in self.housing_footprint().exterior.coords],
                  "case_screws": [[x, y] for x, y in self.case_screws()],
                  # plan projection of the tilted module, centred where sensor_board() puts it
                  # (pocket.sensor_board_offset off the ball, towards the window)
                  "sensor_board": {"width": t["pocket"]["sensor_board"]["x"], "height": t["pocket"]["sensor_board"]["y"],
                                   "x": round(self.sensor_board().centroid.x, 3),
                                   "y": round(self.sensor_board().centroid.y, 3)},
                  # plan view of the module on its way into the pocket (chamfered corner)
                  "module_footprint": [[round(x, 3), round(y, 3)] for x, y in self.insertion_corridor().exterior.coords],
                  "cable_corridor": ([[round(x, 3), round(y, 3)] for x, y in self.cable_corridor().exterior.coords]
                                     if self.cable_corridor() is not None else [])}
        return {
            "name": self.cfg["name"],
            "revision": self.cfg["revision"],
            "half": self.half,
            "pitch": self.cfg["pitch"],
            "keycap": self.cfg["keycap"],
            "keys": [asdict(k) for k in self.keys],
            "trackball": tb,
            "controller": self.cfg["controller"],
            "battery": {**self.cfg["battery"],
                        "bay_polygon": [[round(x, 3), round(y, 3)] for x, y in self.battery_bay().exterior.coords],
                        "well_floor_z": round(-1.6 - self.cfg["battery"]["depth_below_pcb"], 3)},
            "fpc": self.cfg.get("fpc"),
            "outline": [[round(x, 3), round(y, 3)] for x, y in self.outline.exterior.coords],
            "bounds": {"min_x": minx, "min_y": miny, "max_x": maxx, "max_y": maxy,
                       "width": maxx - minx, "height": maxy - miny},
            "mounting_holes": self.cfg["mounting_holes"],
        }


SOCKET_H = 1.85        # CPG135001S30 body height under the PCB
PEG_OUT = 1.1          # Choc V1 posts are 2.65 mm long: this much comes through a 1.6 mm board
STANDOFF_D = 5.6       # case standoff under a mounting hole (hardware/case/params.scad standoff_d)
STANDOFF_CLEAR = 0.3   # air between a standoff and anything on the PCB underside
CELL_AIR = 0.3         # a pouch cell must lie loose


def rotated_box(cx: float, cy: float, w: float, h: float, rotation_deg: float,
                offset: tuple[float, float] = (0.0, 0.0)) -> Polygon:
    """Axis box of w x h centred at (cx, cy) plus a local offset, rotated about (cx, cy).
    KiCad's positive rotation is counter-clockwise on screen (y down), which is clockwise in the
    mathematical frame shapely uses, hence the sign."""
    ox, oy = offset
    b = box(cx + ox - w / 2, cy + oy - h / 2, cx + ox + w / 2, cy + oy + h / 2)
    return affinity.rotate(b, -rotation_deg, origin=(cx, cy))


def notch_shape(cx: float, cy: float, apothem: float, square_corner: bool = False) -> Polygon:
    """Notch cut into the PCB edge for the ball pocket: a regular octagon, optionally with its
    -x / -y corner squared off (that is the only corner where PCB material would otherwise
    overhang the cradle housing and block the module's way into the pocket)."""
    poly = octagon(cx, cy, apothem)
    if square_corner:
        # the union leaves duplicate and collinear vertices on the two merged facets
        poly = Polygon(unary_union([poly, box(cx - apothem, cy - apothem, cx, cy)]).exterior).simplify(0.001)
    return poly


def octagon(cx: float, cy: float, apothem: float) -> Polygon:
    """Regular octagon with flat top/bottom/sides at distance `apothem` from the centre."""
    r = apothem / math.cos(math.pi / 8)
    return Polygon([(cx + r * math.cos(math.radians(22.5 + 45 * i)), cy + r * math.sin(math.radians(22.5 + 45 * i)))
                    for i in range(8)])


def load_config(path: Path = LAYOUT_FILE) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)


def half_config(cfg: dict, half: str) -> dict:
    """Merge the half's block into a copy of the global configuration."""
    if half not in HALVES:
        raise ValueError(f"half must be one of {HALVES}, got {half!r}")
    merged = copy.deepcopy({k: v for k, v in cfg.items() if k != "halves"})
    block = cfg.get("halves", {}).get(half, {})
    for key, value in block.items():
        if isinstance(value, list) and isinstance(merged.get(key), list) and key != "thumbs":
            merged[key] = merged[key] + value
        elif isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    merged["half"] = half
    return merged


def build_keys(cfg: dict) -> list[Key]:
    """Keys of one half: all finger keys plus the thumbs named in cfg['thumbs'] (a list of
    names when merged from halves.<side>.thumbs; the full thumb table lives in cfg['thumb_table'])."""
    keys: list[Key] = []
    py = cfg["pitch"]["y"]
    cols = {c["col"]: c for c in cfg["columns"]}
    for c in cfg["columns"]:
        for r in range(cfg["rows"]):
            keys.append(Key(name=f"{c['name']}_{r}", row=r, col=c["col"],
                            x=c["x"], y=c["stagger"] + r * py))
    inner = cols[max(cols)]
    inner_bottom = (inner["x"], inner["stagger"] + (cfg["rows"] - 1) * py)
    table = {t["name"]: t for t in cfg["thumb_table"]}
    wanted = cfg["thumbs"]
    if wanted and isinstance(wanted[0], dict):      # unmerged global config: all thumbs
        wanted = [t["name"] for t in wanted]
    for name in wanted:
        t = table[name]
        keys.append(Key(name=t["name"], row=t["row"], col=t["col"],
                        x=round(inner_bottom[0] + t["dx"], 3),
                        y=round(inner_bottom[1] + t["dy"], 3),
                        rotation=t["rotation"], kind="thumb"))
    keys.sort(key=lambda k: (k.row, k.col))
    return keys


def build_outline(cfg: dict, keys: Iterable[Key], ball_center: tuple[float, float] | None) -> Polygon:
    """Stepped, angular outline (r2 variant A): the union of all key boxes, the stepped
    bridges between staggered columns, the controller block and the thumb bridge, closed
    with mitre joins (no rounding). On the ball half an octagonal notch is cut for the pocket."""
    keys = list(keys)
    o = cfg["outline"]
    w, h = cfg["keycap"]["width"], cfg["keycap"]["height"]
    sx = o.get("socket_margin", 0.0)
    parts = [rotated_box(k.x, k.y, w + 2 * (o["margin"] + sx), h + 2 * o["margin"], k.rotation) for k in keys]
    # Fill the gaps between the staggered columns so the top/bottom edges are stepped
    # like the Keyball rather than jagged: connect neighbouring column boxes.
    cols = sorted(cfg["columns"], key=lambda c: c["x"])
    py = cfg["pitch"]["y"]
    for a, b in zip(cols, cols[1:]):
        top = max(a["stagger"], b["stagger"]) - h / 2 - o["margin"]
        bot = min(a["stagger"], b["stagger"]) + (cfg["rows"] - 1) * py + h / 2 + o["margin"]
        parts.append(box(a["x"], top, b["x"], bot))
    # Controller block: a rectangle at the inner edge from above the controller down to the
    # thumb cluster (power switch, reset, battery pads and test pads live in it). It doubles
    # as the routing corridor between the thumb keys and the controller.
    c = cfg["controller"]
    cx, cy = c["center"]["x"], c["center"]["y"]
    inner = min(cols, key=lambda col: col["x"])
    cm = o.get("controller_margin", 2.0)
    thumbs = [k for k in keys if k.kind == "thumb"]
    thumb_top = min(k.y for k in thumbs) - 2.0
    tp = cfg["test_pads"]
    block_bottom = max(cfg["battery_pads"]["center"]["y"] + 6.0, tp["start"]["y"] + 3.0, thumb_top)
    # Top edge of the block: the USB-C shell must stick out of the PCB by usb_overhang so the case
    # wall can be flush with it. Shell end = controller board top edge - usb_shell.
    board_top = cy + c.get("pcb_offset_y", 0.0) - c["size"]["y"] / 2
    block_top = board_top - c.get("usb_shell", 0.0) + c["usb_overhang"]
    parts.append(box(cx - c["size"]["x"] / 2 - 4.5, block_top, inner["x"], block_bottom))
    # Thumb bridge: fills the slot between the index/inner bottom keys and the thumb keys
    # (FPC connector and routes live here). On the ball half it runs to the ball axis so
    # the notch cuts a clean edge.
    outer = max(thumbs, key=lambda k: k.x)
    index_col = cols[-2]
    bridge_top = index_col["stagger"] + (cfg["rows"] - 1) * py + h / 2 + o["margin"] - 1.0
    bridge_right = ball_center[0] if ball_center else outer.x + w / 2 + o["margin"] + sx
    parts.append(box(inner["x"], bridge_top, bridge_right, outer.y))
    union = unary_union(parts)
    # Close slivers and tiny notches with mitre joins so every corner stays sharp.
    closed = union.buffer(1.5, join_style=2).buffer(-1.5, join_style=2)
    if closed.geom_type != "Polygon":
        closed = max(closed.geoms, key=lambda g: g.area)
    poly = Polygon(closed.exterior)
    if ball_center:
        tb = cfg["trackball"]
        poly = poly.difference(notch_shape(*ball_center, tb["cradle_diameter"] / 2 + tb["pocket"]["notch_clearance"],
                                           tb["pocket"].get("square_corner", False)))
        if poly.geom_type != "Polygon":
            poly = max(poly.geoms, key=lambda g: g.area)
        poly = Polygon(poly.exterior)
    return poly.simplify(0.02)


def load_layout(half: str = "right", path: Path = LAYOUT_FILE) -> Layout:
    raw = load_config(path)
    cfg = half_config(raw, half)
    cfg["thumb_table"] = raw["thumbs"]
    keys = build_keys(cfg)
    tb = cfg.get("trackball", {})
    ball = (tb["center"]["x"], tb["center"]["y"]) if tb and tb.get("center") else None
    return Layout(half=half, cfg=cfg, keys=keys, outline=build_outline(cfg, keys, ball), ball_center=ball, source=path)


def load_layouts(path: Path = LAYOUT_FILE) -> dict[str, Layout]:
    return {half: load_layout(half, path) for half in HALVES}


# ----- checks -------------------------------------------------------------------
def check_layout(layout: Layout) -> list[str]:
    """Return a list of human readable problems; empty list means the layout is sound."""
    problems: list[str] = []
    cfg = layout.cfg
    caps = {k.ref: layout.keycap_polygon(k) for k in layout.keys}
    refs = list(caps)
    for i, a in enumerate(refs):
        for b in refs[i + 1:]:
            if caps[a].intersects(caps[b]) and caps[a].intersection(caps[b]).area > 0.01:
                problems.append(f"keycaps overlap: {a} / {b}")
    c = cfg["controller"]
    off = c.get("pcb_offset_y", 0.0)
    ctrl = box(c["center"]["x"] - c["size"]["x"] / 2, c["center"]["y"] + off - c["size"]["y"] / 2,
               c["center"]["x"] + c["size"]["x"] / 2, c["center"]["y"] + off + c["size"]["y"] / 2)
    for ref, poly in caps.items():
        if poly.intersects(ctrl):
            problems.append(f"controller overlaps {ref}")
    # the controller board may overhang the top edge (USB side) but nothing else
    from shapely.geometry import LineString
    top_edge = layout.outline.intersection(LineString([(c["center"]["x"], -500), (c["center"]["x"], 500)])).bounds[1]
    outside = ctrl.difference(layout.outline)
    if not outside.is_empty and outside.bounds[3] > top_edge + 0.05:
        problems.append("controller not inside the PCB outline (only the USB end may overhang the top edge)")
    shell_end = ctrl.bounds[1] - c.get("usb_shell", 0.0)
    if abs((top_edge - shell_end) - c["usb_overhang"]) > 0.05:
        problems.append(f"USB-C shell overhang is {top_edge - shell_end:.2f} mm, spec {c['usb_overhang']} mm")
    for ref, poly in caps.items():
        if not layout.outline.buffer(cfg["outline"]["margin"] + 0.05).contains(poly):  # noqa
            problems.append(f"keycap {ref} sticks out of the PCB outline")
    if layout.has_ball:
        cradle = layout.cradle_polygon()
        need = cfg["trackball"]["min_keycap_clearance"]
        for ref, poly in caps.items():
            d = poly.distance(cradle)
            if d < need:
                problems.append(f"cradle too close to {ref}: {d:.2f} mm < {need} mm")
        clear = cfg["trackball"]["pocket"]["notch_clearance"]
        d = layout.outline.distance(cradle)
        if d < clear - 0.05:
            problems.append(f"cradle flange only {d:.2f} mm from the PCB edge (notch clearance {clear} mm)")
        if layout.outline.intersects(Point(*layout.ball_center).buffer(cfg["trackball"]["ball_diameter"] / 2)):
            problems.append("ball overlaps the PCB")
        housing = layout.housing_box()
        for ref in caps:
            k = layout.key(int(ref[2]), int(ref[3]))
            body = rotated_box(k.x, k.y, cfg["switch_body"], cfg["switch_body"], k.rotation)
            if body.intersects(housing):
                problems.append(f"cradle housing collides with switch {ref}")
        # r2.2: the module is lowered into the pocket as one piece and lifted out again with
        # the PCB fitted, so its plan view (housing and sensor board, both chamfered on the
        # corner that faces the notch facet) must stay clear of the board.
        corridor = layout.insertion_corridor()
        pk = cfg["trackball"]["pocket"]
        need = pk["corner_clearance"]
        overlap = corridor.intersection(layout.outline)
        if not overlap.is_empty and overlap.area > 0.001:
            problems.append(f"trackball module cannot be lowered past the PCB: {overlap.area:.2f} mm2 of the board "
                            f"covers it (grow trackball.pocket.corner_chamfer)")
        else:
            d = corridor.distance(layout.outline)
            if d < need - 0.005:
                problems.append(f"trackball module only {d:.2f} mm from the PCB edge on its insertion path "
                                f"(need {need} mm)")
        fp = layout.fpc_box()
        if fp is not None:
            d = housing.distance(fp)
            if d < 0.5:
                problems.append(f"cradle housing only {d:.2f} mm from the FPC connector (need 0.5 mm)")
            if not layout.outline.contains(fp):
                problems.append("FPC connector not inside the PCB outline")
            for ref, poly in caps.items():
                body = rotated_box(layout.key(int(ref[2]), int(ref[3])).x, layout.key(int(ref[2]), int(ref[3])).y,
                                   cfg["switch_body"], cfg["switch_body"], layout.key(int(ref[2]), int(ref[3])).rotation)
                if body.intersects(fp):
                    problems.append(f"FPC connector collides with switch {ref}")
            if layout.fpc_side == "top":
                # The cable climbs the gap between the cup and the notch, folds over the board
                # edge and enters the connector from +y: the corridor must be free and the
                # mouth must sit a little inside the edge so the fold has somewhere to land.
                mouth_y = layout.fpc_mouth()[1]
                edge = layout.outline.exterior.distance(Point(layout.fpc_mouth()))
                if edge < 0.3:
                    problems.append(f"FPC cable mouth only {edge:.2f} mm from the PCB edge (need 0.3 mm)")
                if edge > 3.0:
                    problems.append(f"FPC cable mouth {edge:.2f} mm from the PCB edge: the cable cannot fold "
                                    f"over the edge into it (max 3 mm)")
                corr = layout.cable_corridor()
                for name, poly in layout.back_parts().items():
                    if poly.intersects(corr) or poly.intersects(fp):
                        problems.append(f"{name} collides with the FFC corridor on the key side")
                for ref, poly in caps.items():
                    if poly.intersects(corr):
                        problems.append(f"keycap {ref} covers the FFC corridor")
                for hole in cfg["mounting_holes"]:
                    if Point(hole["x"], hole["y"]).buffer(3.0).intersects(fp.union(corr)):
                        problems.append(f"mounting hole at ({hole['x']}, {hole['y']}) collides with J1 or the FFC corridor")
                cup = Point(*layout.ball_center).buffer(pk["cup_envelope"] / 2, 64)
                gap = pk["notch_clearance"] + (cfg["trackball"]["cradle_diameter"] - pk["cup_envelope"]) / 2
                if gap < pk["cable_gap_min"]:
                    problems.append(f"only {gap:.2f} mm between the cradle cup envelope and the PCB notch: the "
                                    f"FFC cannot climb beside the cup (need {pk['cable_gap_min']} mm)")
                if cup.intersects(layout.outline):
                    problems.append("cradle cup envelope overlaps the PCB")
    for hole in cfg["mounting_holes"]:
        p = Point(hole["x"], hole["y"])
        if layout.outline.exterior.distance(p) < 2.0:
            problems.append(f"mounting hole at ({hole['x']}, {hole['y']}) too close to the edge")
        for ref, poly in caps.items():
            # switch body is the hard limit, keycaps may overhang holes
            k = layout.key(int(ref[2]), int(ref[3]))
            body = rotated_box(k.x, k.y, cfg["switch_body"], cfg["switch_body"], k.rotation)
            if body.distance(p) < 0.9:
                problems.append(f"mounting hole at ({hole['x']}, {hole['y']}) collides with switch {ref}")
        # the case standoff under the hole must clear everything on the underside
        for k in layout.keys:
            for name, poly, _ in layout.under_switch(k):
                gap = poly.distance(p) - STANDOFF_D / 2
                if gap < STANDOFF_CLEAR - 1e-6:
                    problems.append(f"standoff at ({hole['x']}, {hole['y']}) only {gap:.2f} mm from {name} "
                                    f"(needs {STANDOFF_CLEAR})")
        if layout.has_ball and p.distance(Point(*layout.ball_center)) < cfg["trackball"]["cradle_diameter"] / 2 + 2:
            problems.append(f"mounting hole at ({hole['x']}, {hole['y']}) collides with the cradle")
    bay = layout.battery_bay()
    clear = cfg["battery"]["edge_clearance"]
    if not layout.outline.contains(bay):
        problems.append("battery bay not inside the PCB outline")
    elif layout.outline.exterior.distance(bay) < clear - 0.05:
        problems.append(f"battery bay only {layout.outline.exterior.distance(bay):.2f} mm from the PCB edge (need {clear} mm)")
    cell = cfg["battery"]["size"]
    b = cfg["battery"]["bay"]["size"]
    if cell["x"] > b["x"] or cell["y"] > b["y"]:
        problems.append(f"battery cell {cell['x']} x {cell['y']} mm does not fit the bay {b['x']} x {b['y']} mm")
    # Parts on the back inside the bay are only allowed if the cell still fits under them.
    depth = cfg["battery"]["depth_below_pcb"]
    for name, poly in layout.back_parts().items():
        if not poly.intersects(bay):
            continue
        if not name.endswith(" socket"):
            problems.append(f"battery bay collides with {name} on the back of the PCB")
        elif SOCKET_H + cell["z"] + CELL_AIR > depth + 1e-6:
            problems.append(f"{name} reaches into the battery bay: socket {SOCKET_H} + cell {cell['z']} + "
                            f"{CELL_AIR} air does not fit the {depth} mm well")
    expected = 15 + len(cfg["thumbs"])
    if len(layout.keys) != expected:
        problems.append(f"expected {expected} keys on the {layout.half} half, got {len(layout.keys)}")
    if not layout.outline.is_valid:
        problems.append("outline polygon is not valid")
    return problems


# ----- exports ------------------------------------------------------------------
def write_points(layout: Layout, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(layout.to_dict(), indent=2) + "\n")


def write_outline_dxf(layout: Layout, out: Path) -> None:
    import ezdxf

    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    pts = list(layout.outline.exterior.coords)
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "OUTLINE"})
    if layout.has_ball:
        tb = layout.cfg["trackball"]
        msp.add_circle(layout.ball_center, tb["ball_diameter"] / 2, dxfattribs={"layer": "BALL"})
        msp.add_circle(layout.ball_center, tb["cradle_diameter"] / 2, dxfattribs={"layer": "CRADLE"})
        msp.add_circle(layout.ball_center, tb["cradle_diameter"] / 2 + tb["pocket"]["wall"], dxfattribs={"layer": "POCKET"})
        msp.add_lwpolyline(list(layout.housing_footprint().exterior.coords), close=True, dxfattribs={"layer": "POCKET_FLOOR"})
        for sx_, sy_ in layout.case_screws():
            msp.add_circle((sx_, sy_), 1.0, dxfattribs={"layer": "HOLES"})
    for h in layout.cfg["mounting_holes"]:
        msp.add_circle((h["x"], h["y"]), 1.1, dxfattribs={"layer": "HOLES"})
    msp.add_lwpolyline(list(layout.battery_bay().exterior.coords), close=True, dxfattribs={"layer": "BATTERY_BAY"})
    for k in layout.keys:
        poly = rotated_box(k.x, k.y, layout.cfg["switch_body"], layout.cfg["switch_body"], k.rotation)
        msp.add_lwpolyline(list(poly.exterior.coords), close=True, dxfattribs={"layer": "SWITCHES"})
    c = layout.cfg["controller"]
    msp.add_lwpolyline([(c["center"]["x"] - c["size"]["x"] / 2, c["center"]["y"] - c["size"]["y"] / 2),
                        (c["center"]["x"] + c["size"]["x"] / 2, c["center"]["y"] - c["size"]["y"] / 2),
                        (c["center"]["x"] + c["size"]["x"] / 2, c["center"]["y"] + c["size"]["y"] / 2),
                        (c["center"]["x"] - c["size"]["x"] / 2, c["center"]["y"] + c["size"]["y"] / 2)],
                       close=True, dxfattribs={"layer": "CONTROLLER"})
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(out)


def write_preview(layout: Layout, out: Path) -> None:
    """Top view of the half; the left half is drawn mirrored so it looks like on the desk."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPoly, Circle

    mirror = layout.half == "left"
    sx = -1 if mirror else 1
    fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
    ox, oy = zip(*layout.outline.exterior.coords)
    ax.add_patch(MplPoly(list(zip([sx * x for x in ox], oy)), closed=True, fc="#2e7d32", ec="#1b5e20", alpha=0.25))
    for k in layout.keys:
        poly = layout.keycap_polygon(k)
        xs, ys = zip(*poly.exterior.coords)
        color = "#ff8a3d" if k.kind == "thumb" else "#f5f1e8"
        ax.add_patch(MplPoly(list(zip([sx * x for x in xs], ys)), closed=True, fc=color, ec="#555", lw=0.8))
        ax.text(sx * k.x, k.y, k.ref, ha="center", va="center", fontsize=6, color="#333")
    minx, miny, maxx, maxy = layout.outline.bounds
    if layout.has_ball:
        tb = layout.cfg["trackball"]
        bx, by = layout.ball_center
        pocket_r = tb["cradle_diameter"] / 2 + tb["pocket"]["wall"]
        ax.add_patch(Circle((sx * bx, by), pocket_r, fc="#e0e0e0", ec="#777", ls="--", lw=0.8))
        hx, hy = zip(*layout.housing_footprint().exterior.coords)
        ax.add_patch(MplPoly(list(zip([sx * x for x in hx], hy)), closed=True, fc="none", ec="#777", ls=":", lw=0.8))
        for sx_, sy_ in layout.case_screws():
            ax.add_patch(Circle((sx * sx_, sy_), 1.0, fc="white", ec="#777", lw=0.6))
        ax.add_patch(Circle((sx * bx, by), tb["cradle_diameter"] / 2, fc="none", ec="#999", ls=":"))
        ax.add_patch(Circle((sx * bx, by), tb["ball_diameter"] / 2, fc="white", ec="#333"))
        minx, miny = min(minx, bx - pocket_r), min(miny, by - pocket_r)
        maxx, maxy = max(maxx, bx + pocket_r), max(maxy, by + pocket_r)
        f = layout.cfg.get("fpc")
        if f:
            ax.add_patch(MplPoly([(sx * (f["center"]["x"] - 4.5), f["center"]["y"] - 3), (sx * (f["center"]["x"] + 4.5), f["center"]["y"] - 3),
                                  (sx * (f["center"]["x"] + 4.5), f["center"]["y"] + 3), (sx * (f["center"]["x"] - 4.5), f["center"]["y"] + 3)],
                                 closed=True, fc="#ffe082", ec="#8d6e63"))
    bay = layout.battery_bay()
    bxs, bys = zip(*bay.exterior.coords)
    ax.add_patch(MplPoly(list(zip([sx * x for x in bxs], bys)), closed=True, fc="#c8e6c9", ec="#2e7d32", ls="--", lw=1.0))
    ax.text(sx * bay.centroid.x, bay.bounds[3] - 1.5, f"{layout.cfg['battery']['cell']} (back)", ha="center", va="bottom", fontsize=5, color="#2e7d32")
    c = layout.cfg["controller"]
    ax.add_patch(MplPoly([(sx * (c["center"]["x"] - 9), c["center"]["y"] - 16.75), (sx * (c["center"]["x"] + 9), c["center"]["y"] - 16.75),
                          (sx * (c["center"]["x"] + 9), c["center"]["y"] + 16.75), (sx * (c["center"]["x"] - 9), c["center"]["y"] + 16.75)],
                         closed=True, fc="#90caf9", ec="#1565c0"))
    for hole in layout.cfg["mounting_holes"]:
        ax.add_patch(Circle((sx * hole["x"], hole["y"]), 1.1, fc="white", ec="#333"))
    ax.set_aspect("equal")
    lo, hi = (-maxx - 5, -minx + 5) if mirror else (minx - 5, maxx + 5)
    ax.set_xlim(lo, hi)
    ax.set_ylim(maxy + 5, miny - 5)
    b = layout.outline.bounds
    ax.set_title(f"{layout.cfg['name']} {layout.cfg['revision']} - {layout.half} half (top view), PCB {b[2]-b[0]:.1f} x {b[3]-b[1]:.1f} mm")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.grid(True, lw=0.3, alpha=0.5)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
