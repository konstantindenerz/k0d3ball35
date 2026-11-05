# SPDX-License-Identifier: MIT
"""Key geometry for k0d3ball36.

Everything is derived from hardware/layout/k0d3ball36.yaml. Coordinates are in mm,
right half, x outward (pinky), y downward (towards the user), origin at the centre of
the middle-column top key. This matches KiCad's screen coordinate system, so the PCB
generator can use the values unchanged (after adding a page offset).
"""
from __future__ import annotations

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
    cfg: dict
    keys: list[Key]
    outline: Polygon
    ball_center: tuple[float, float]
    source: Path = field(default=LAYOUT_FILE)

    # ----- convenience -------------------------------------------------------
    @property
    def pitch(self) -> tuple[float, float]:
        return self.cfg["pitch"]["x"], self.cfg["pitch"]["y"]

    @property
    def keycap(self) -> tuple[float, float]:
        return self.cfg["keycap"]["width"], self.cfg["keycap"]["height"]

    def key(self, row: int, col: int) -> Key:
        for k in self.keys:
            if k.row == row and k.col == col:
                return k
        raise KeyError((row, col))

    def keycap_polygon(self, key: Key) -> Polygon:
        w, h = self.keycap
        return rotated_box(key.x, key.y, w, h, key.rotation)

    def cradle_polygon(self) -> Polygon:
        d = self.cfg["trackball"]["cradle_diameter"]
        return Point(*self.ball_center).buffer(d / 2, 64)

    def bounds(self) -> tuple[float, float, float, float]:
        return self.outline.bounds

    # ----- export -------------------------------------------------------------
    def to_dict(self) -> dict:
        minx, miny, maxx, maxy = self.outline.bounds
        return {
            "name": self.cfg["name"],
            "revision": self.cfg["revision"],
            "pitch": self.cfg["pitch"],
            "keycap": self.cfg["keycap"],
            "keys": [asdict(k) for k in self.keys],
            "trackball": {**self.cfg["trackball"], "center": {"x": self.ball_center[0], "y": self.ball_center[1]}},
            "controller": self.cfg["controller"],
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


def load_config(path: Path = LAYOUT_FILE) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)


def build_keys(cfg: dict) -> list[Key]:
    keys: list[Key] = []
    py = cfg["pitch"]["y"]
    cols = {c["col"]: c for c in cfg["columns"]}
    for c in cfg["columns"]:
        for r in range(cfg["rows"]):
            keys.append(Key(name=f"{c['name']}_{r}", row=r, col=c["col"],
                            x=c["x"], y=c["stagger"] + r * py))
    inner = cols[max(cols)]
    inner_bottom = (inner["x"], inner["stagger"] + (cfg["rows"] - 1) * py)
    for t in cfg["thumbs"]:
        keys.append(Key(name=t["name"], row=t["row"], col=t["col"],
                        x=round(inner_bottom[0] + t["dx"], 3),
                        y=round(inner_bottom[1] + t["dy"], 3),
                        rotation=t["rotation"], kind="thumb"))
    keys.sort(key=lambda k: (k.row, k.col))
    return keys


def build_outline(cfg: dict, keys: Iterable[Key]) -> Polygon:
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
    # Controller block: controller, jumpers above it, reset/battery below, power switch at the edge
    c = cfg["controller"]
    cx, cy = c["center"]["x"], c["center"]["y"]
    inner = min(cols, key=lambda col: col["x"])
    parts.append(box(cx - c["size"]["x"] / 2 - 4.5, cfg["jumpers"]["start"]["y"] - 3.0,
                     inner["x"], cfg["battery_jst"]["center"]["y"] + 6.0))
    # Ball zone and the bridges that tie it to the key block and the outer thumb key
    tb = cfg["trackball"]
    bx, by = tb["center"]["x"], tb["center"]["y"]
    parts.append(Point(bx, by).buffer(tb["cradle_diameter"] / 2 + o["ball_margin"], 64))
    parts.append(box(bx - 21, by - 25, bx + 15, by))
    thumb_outer = next(k for k in keys if k.kind == "thumb" and k.rotation == 0)
    parts.append(box(thumb_outer.x, thumb_outer.y - 8, bx, thumb_outer.y + 8))
    union = unary_union(parts)
    r = o["corner_radius"]
    # Round outer corners (buffer out then in) and remove tiny inner notches (in then out).
    smooth = union.buffer(r, 32).buffer(-2 * r, 32).buffer(r, 32)
    if smooth.geom_type != "Polygon":
        smooth = max(smooth.geoms, key=lambda g: g.area)
    return Polygon(smooth.exterior).simplify(0.02)


def load_layout(path: Path = LAYOUT_FILE) -> Layout:
    cfg = load_config(path)
    keys = build_keys(cfg)
    tb = cfg["trackball"]["center"]
    return Layout(cfg=cfg, keys=keys, outline=build_outline(cfg, keys), ball_center=(tb["x"], tb["y"]), source=path)


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
    cradle = layout.cradle_polygon()
    need = cfg["trackball"]["min_keycap_clearance"]
    for ref, poly in caps.items():
        d = poly.distance(cradle)
        if d < need:
            problems.append(f"cradle too close to {ref}: {d:.2f} mm < {need} mm")
    c = cfg["controller"]
    ctrl = box(c["center"]["x"] - c["size"]["x"] / 2, c["center"]["y"] - c["size"]["y"] / 2,
               c["center"]["x"] + c["size"]["x"] / 2, c["center"]["y"] + c["size"]["y"] / 2)
    for ref, poly in caps.items():
        if poly.intersects(ctrl):
            problems.append(f"controller overlaps {ref}")
    if not layout.outline.contains(cradle.buffer(-0.01)):
        problems.append("cradle flange not inside the PCB outline")
    for ref, poly in caps.items():
        if not layout.outline.buffer(cfg["outline"]["margin"] + 0.05).contains(poly):  # noqa
            problems.append(f"keycap {ref} sticks out of the PCB outline")
    for h in cfg["mounting_holes"]:
        p = Point(h["x"], h["y"])
        if layout.outline.exterior.distance(p) < 2.0:
            problems.append(f"mounting hole at ({h['x']}, {h['y']}) too close to the edge")
        for ref, poly in caps.items():
            # switch body is the hard limit, keycaps may overhang holes
            body = rotated_box(layout.key(int(ref[2]), int(ref[3])).x, layout.key(int(ref[2]), int(ref[3])).y,
                               cfg["switch_body"], cfg["switch_body"], layout.key(int(ref[2]), int(ref[3])).rotation)
            if body.distance(p) < 0.9:
                problems.append(f"mounting hole at ({h['x']}, {h['y']}) collides with switch {ref}")
        if p.distance(Point(*layout.ball_center)) < cfg["trackball"]["cradle_diameter"] / 2 + 2:
            problems.append(f"mounting hole at ({h['x']}, {h['y']}) collides with the cradle")
    if len(layout.keys) != 18:
        problems.append(f"expected 18 keys per half, got {len(layout.keys)}")
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
    tb = layout.cfg["trackball"]
    msp.add_circle(layout.ball_center, tb["pcb_cutout_diameter"] / 2, dxfattribs={"layer": "CUTOUT"})
    for h in layout.cfg["mounting_holes"]:
        msp.add_circle((h["x"], h["y"]), 1.1, dxfattribs={"layer": "HOLES"})
    for k in layout.keys:
        poly = rotated_box(k.x, k.y, layout.cfg["switch_body"], layout.cfg["switch_body"], k.rotation)
        msp.add_lwpolyline(list(poly.exterior.coords), close=True, dxfattribs={"layer": "SWITCHES"})
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(out)


def write_preview(layout: Layout, out: Path, mirror: bool = False) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPoly, Circle

    sx = -1 if mirror else 1
    fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
    ox, oy = zip(*layout.outline.exterior.coords)
    ax.add_patch(MplPoly(list(zip([sx * x for x in ox], oy)), closed=True, fc="#2e7d32", ec="#1b5e20", alpha=0.25))
    w, h = layout.keycap
    for k in layout.keys:
        poly = layout.keycap_polygon(k)
        xs, ys = zip(*poly.exterior.coords)
        color = "#ff8a3d" if k.kind == "thumb" else "#f5f1e8"
        ax.add_patch(MplPoly(list(zip([sx * x for x in xs], ys)), closed=True, fc=color, ec="#555", lw=0.8))
        ax.text(sx * k.x, k.y, k.ref, ha="center", va="center", fontsize=6, color="#333")
    tb = layout.cfg["trackball"]
    ax.add_patch(Circle((sx * layout.ball_center[0], layout.ball_center[1]), tb["cradle_diameter"] / 2, fc="none", ec="#999", ls="--"))
    ax.add_patch(Circle((sx * layout.ball_center[0], layout.ball_center[1]), tb["ball_diameter"] / 2, fc="white", ec="#333"))
    c = layout.cfg["controller"]
    ax.add_patch(MplPoly([(sx * (c["center"]["x"] - 9), c["center"]["y"] - 16.75), (sx * (c["center"]["x"] + 9), c["center"]["y"] - 16.75),
                          (sx * (c["center"]["x"] + 9), c["center"]["y"] + 16.75), (sx * (c["center"]["x"] - 9), c["center"]["y"] + 16.75)],
                         closed=True, fc="#90caf9", ec="#1565c0"))
    for hole in layout.cfg["mounting_holes"]:
        ax.add_patch(Circle((sx * hole["x"], hole["y"]), 1.1, fc="white", ec="#333"))
    ax.set_aspect("equal")
    ax.invert_yaxis()
    minx, miny, maxx, maxy = layout.outline.bounds
    ax.set_xlim(sx * minx - 5 if not mirror else -maxx - 5, sx * maxx + 5 if not mirror else -minx + 5)
    ax.set_ylim(maxy + 5, miny - 5)
    ax.set_title(f"{layout.cfg['name']} {layout.cfg['revision']} - {'left' if mirror else 'right'} half (top view)")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.grid(True, lw=0.3, alpha=0.5)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
