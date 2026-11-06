# SPDX-License-Identifier: MIT
"""Key geometry for k0d3ball36 (r2: two separate PCBs).

Everything is derived from hardware/layout/k0d3ball36.yaml. Coordinates are in mm,
x outward (pinky), y downward (towards the user), origin at the centre of the
middle-column top key. Both halves use this frame; the left half is mirrored for
display only. This matches KiCad's screen coordinate system, so the PCB generator
can use the values unchanged (after adding a page offset).

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
LAYOUT_FILE = REPO / "hardware" / "layout" / "k0d3ball36.yaml"
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
        """Octagonal notch in the PCB edge where the ball pocket docks."""
        if not self.has_ball:
            return None
        tb = self.cfg["trackball"]
        return octagon(*self.ball_center, tb["cradle_diameter"] / 2 + tb["pocket"]["notch_clearance"])

    def pocket_polygon(self) -> Polygon | None:
        """Outer wall of the case pocket around the cradle (reference for the case)."""
        if not self.has_ball:
            return None
        tb = self.cfg["trackball"]
        return Point(*self.ball_center).buffer(tb["cradle_diameter"] / 2 + tb["pocket"]["wall"], 64)

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
                  # sensor board (26 x 25 mm) centred under the ball, long side along x
                  "sensor_board": {"width": 26.0, "height": 25.0, "x": self.ball_center[0], "y": self.ball_center[1]}}
        return {
            "name": self.cfg["name"],
            "revision": self.cfg["revision"],
            "half": self.half,
            "pitch": self.cfg["pitch"],
            "keycap": self.cfg["keycap"],
            "keys": [asdict(k) for k in self.keys],
            "trackball": tb,
            "controller": self.cfg["controller"],
            "fpc": self.cfg.get("fpc"),
            "outline": [[round(x, 3), round(y, 3)] for x, y in self.outline.exterior.coords],
            "bounds": {"min_x": minx, "min_y": miny, "max_x": maxx, "max_y": maxy,
                       "width": maxx - minx, "height": maxy - miny},
            "mounting_holes": self.cfg["mounting_holes"],
        }


def rotated_box(cx: float, cy: float, w: float, h: float, rotation_deg: float) -> Polygon:
    b = box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    # KiCad positive rotation is counter-clockwise on screen (y down). Shapely rotates
    # counter-clockwise in a y-up frame, so negate to get the same on-screen result.
    return affinity.rotate(b, -rotation_deg, origin=(cx, cy))


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
    parts.append(box(cx - c["size"]["x"] / 2 - 4.5, cy - c["size"]["y"] / 2 - cm, inner["x"], block_bottom))
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
        poly = poly.difference(octagon(*ball_center, tb["cradle_diameter"] / 2 + tb["pocket"]["notch_clearance"]))
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
    ctrl = box(c["center"]["x"] - c["size"]["x"] / 2, c["center"]["y"] - c["size"]["y"] / 2,
               c["center"]["x"] + c["size"]["x"] / 2, c["center"]["y"] + c["size"]["y"] / 2)
    for ref, poly in caps.items():
        if poly.intersects(ctrl):
            problems.append(f"controller overlaps {ref}")
    if not layout.outline.contains(ctrl):
        problems.append("controller not inside the PCB outline")
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
        f = cfg.get("fpc")
        if f:
            fp = box(f["center"]["x"] - 4.5, f["center"]["y"] - 3.0, f["center"]["x"] + 4.5, f["center"]["y"] + 3.0)
            if not layout.outline.contains(fp):
                problems.append("FPC connector not inside the PCB outline")
            for ref, poly in caps.items():
                body = rotated_box(layout.key(int(ref[2]), int(ref[3])).x, layout.key(int(ref[2]), int(ref[3])).y,
                                   cfg["switch_body"], cfg["switch_body"], layout.key(int(ref[2]), int(ref[3])).rotation)
                if body.intersects(fp):
                    problems.append(f"FPC connector collides with switch {ref}")
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
        if layout.has_ball and p.distance(Point(*layout.ball_center)) < cfg["trackball"]["cradle_diameter"] / 2 + 2:
            problems.append(f"mounting hole at ({hole['x']}, {hole['y']}) collides with the cradle")
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
    for h in layout.cfg["mounting_holes"]:
        msp.add_circle((h["x"], h["y"]), 1.1, dxfattribs={"layer": "HOLES"})
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
        ax.add_patch(Circle((sx * bx, by), tb["cradle_diameter"] / 2, fc="none", ec="#999", ls=":"))
        ax.add_patch(Circle((sx * bx, by), tb["ball_diameter"] / 2, fc="white", ec="#333"))
        minx, miny = min(minx, bx - pocket_r), min(miny, by - pocket_r)
        maxx, maxy = max(maxx, bx + pocket_r), max(maxy, by + pocket_r)
        f = layout.cfg.get("fpc")
        if f:
            ax.add_patch(MplPoly([(sx * (f["center"]["x"] - 4.5), f["center"]["y"] - 3), (sx * (f["center"]["x"] + 4.5), f["center"]["y"] - 3),
                                  (sx * (f["center"]["x"] + 4.5), f["center"]["y"] + 3), (sx * (f["center"]["x"] - 4.5), f["center"]["y"] + 3)],
                                 closed=True, fc="#ffe082", ec="#8d6e63"))
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
