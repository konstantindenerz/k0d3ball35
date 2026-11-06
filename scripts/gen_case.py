#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Layout facts for the printed case (hardware/case/data.scad).

Reads both halves through k0d3.geometry.load_layout and writes one OpenSCAD file with
per-half arrays plus selector functions (``outline("left")`` and so on). Only layout facts
are emitted: polygons in the layout frame (x outward, y towards the user, origin at the
middle-column top key), hole positions, courtyards. Every offset and every z value lives in
the SCAD sources so that ``-D wall=2.5`` stays live. The left half is written in the frame
too; case.scad mirrors it once at the top level.

Usage: scripts/gen_case.py [output]      (default hardware/case/data.scad)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from k0d3.geometry import HALVES, Layout, load_layout

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "hardware" / "case" / "data.scad"

BOX_INNER_X = -45.5      # key-side wall of the controller box (params.scad box_inner_x)
BOX_CAP_CLEAR = 1.0      # controller box keeps this to every keycap
WELL_GROW = 1.0          # well = bay + J3 + RB1 courtyards grown by this
PAD_ALONG = 9.0          # magnet pad length along the PCB edge (params.scad pad_size[0])
PAD_OUT = 7.0            # magnet pad depth beyond the wall (params.scad pad_size[1])
PAD_MIN_EDGE = PAD_ALONG + 2.0
WALL_GUESS = 3.2         # pcb_clear + wall, only for the sanity checks here
FOOT_D = 10.5
CTRL_CLEAR = 1.0         # boss protrusions keep this to the controller board


def fmt(v: float) -> str:
    v = round(float(v), 3)
    if v == 0:
        v = 0.0
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def pts(seq) -> str:
    return "[" + ", ".join(f"[{fmt(x)}, {fmt(y)}]" for x, y in seq) + "]"


def ring(poly: Polygon) -> list[tuple[float, float]]:
    coords = list(poly.exterior.coords)
    if coords[0] == coords[-1]:
        coords = coords[:-1]
    # counter-clockwise in the mathematical sense keeps OpenSCAD's polygon() happy
    if Polygon(coords).exterior.is_ccw is False:
        coords.reverse()
    return [(round(x, 3), round(y, 3)) for x, y in coords]


def controller_rect(layout: Layout) -> tuple[float, float, float, float]:
    c = layout.cfg["controller"]
    cx, cy = c["center"]["x"], c["center"]["y"] + c.get("pcb_offset_y", 0.0)
    return (cx - c["size"]["x"] / 2, cy - c["size"]["y"] / 2, cx + c["size"]["x"] / 2, cy + c["size"]["y"] / 2)


def box_rect(layout: Layout) -> tuple[float, float, float, float]:
    """Controller block rectangle: outer PCB edge to BOX_INNER_X, top PCB edge down to the block
    bottom, shortened where a thumb keycap (plus clearance) reaches into that x range."""
    minx, miny, maxx, maxy = layout.outline.bounds
    c = layout.cfg["controller"]
    # the block's outer edge and top edge: the outline around the controller itself
    strip = box(minx - 1, miny - 1, BOX_INNER_X, c["center"]["y"] + c["size"]["y"] / 2)
    block = layout.outline.intersection(strip)
    x0, y0 = block.bounds[0], block.bounds[1]
    tp = layout.cfg["test_pads"]
    thumb_top = min(k.y for k in layout.thumbs) - 2.0
    block_bottom = max(layout.cfg["battery_pads"]["center"]["y"] + 6.0, tp["start"]["y"] + 3.0, thumb_top)
    y1 = block_bottom
    for k in layout.keys:
        b = layout.keycap_polygon(k).bounds
        # thumb caps reaching into the block (the inner column stops 0.75 mm short of the wall)
        if b[2] > x0 and b[0] < BOX_INNER_X - 0.75 and b[1] - BOX_CAP_CLEAR < y1:
            y1 = b[1] - BOX_CAP_CLEAR
    y1 = math.floor(y1 * 10) / 10
    assert y1 > c["center"]["y"] + c["size"]["y"] / 2 + 2, "controller box too short for the controller"
    return (round(x0, 3), round(y0, 3), BOX_INNER_X, round(y1, 3))


def well_polygon(layout: Layout) -> Polygon:
    parts = layout.back_parts()
    well = unary_union([layout.battery_bay().buffer(WELL_GROW, join_style=2),
                        parts["J3"].buffer(WELL_GROW, join_style=2),
                        parts["RB1"].buffer(WELL_GROW, join_style=2)])
    well = well.buffer(0.5, join_style=2).buffer(-0.5, join_style=2)
    assert well.geom_type == "Polygon", well.geom_type
    return Polygon(well.exterior).simplify(0.01)


def outward_normal(poly: Polygon, a, b) -> tuple[float, float]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    nx, ny = dy / n, -dx / n
    mid = ((a[0] + b[0]) / 2 + nx * 0.5, (a[1] + b[1]) / 2 + ny * 0.5)
    if poly.contains(Point(mid)):
        nx, ny = -nx, -ny
    return nx, ny


def pad_rect(anchor, normal, out0: float, out1: float) -> Polygon:
    ax, ay = anchor
    nx, ny = normal
    tx, ty = -ny, nx
    corners = []
    for d, s in ((out0, -1), (out0, 1), (out1, 1), (out1, -1)):
        corners.append((ax + nx * d + tx * s * PAD_ALONG / 2, ay + ny * d + ty * s * PAD_ALONG / 2))
    return Polygon(corners)


def magnet_pads(layout: Layout, box_r, keep_out: list[Polygon]) -> list[tuple[float, float, float, float]]:
    """One pad per bounding-box corner: anchor on the nearest long enough outline edge plus the
    outward unit normal. Pads never sit on a controller box wall or in the pocket."""
    poly = layout.outline
    minx, miny, maxx, maxy = poly.bounds
    corners = [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]
    coords = list(poly.exterior.coords)
    edges = [(coords[i], coords[i + 1]) for i in range(len(coords) - 1)]
    box_zone = box(*box_r).buffer(WALL_GUESS + 1.0, join_style=2)
    pads = []
    for corner in corners:
        best = None
        for a, b in edges:
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            if length < PAD_MIN_EDGE:
                continue
            seg = LineString([a, b])
            t = seg.project(Point(corner))
            t = min(max(t, PAD_ALONG / 2 + 1.0), length - PAD_ALONG / 2 - 1.0)
            anchor = seg.interpolate(t)
            anchor = (anchor.x, anchor.y)
            normal = outward_normal(poly, a, b)
            rect = pad_rect(anchor, normal, 0.01, WALL_GUESS + PAD_OUT)
            if rect.intersects(box_zone) or any(rect.intersects(k) for k in keep_out):
                continue
            if rect.buffer(-0.02).intersects(poly):
                continue
            d = Point(corner).distance(Point(anchor))
            if best is None or d < best[0]:
                best = (d, anchor, normal)
        assert best is not None, f"no magnet pad position near corner {corner}"
        _, (ax, ay), (nx, ny) = best
        pads.append((round(ax, 3), round(ay, 3), round(nx, 4), round(ny, 4)))
    return pads


def feet(layout: Layout, box_r) -> list[tuple[float, float]]:
    """Rubber feet: the five mounting holes projected onto the floor plus two under the
    controller block so the half does not rock when a thumb key is pressed."""
    holes = [(h["x"], h["y"]) for h in layout.cfg["mounting_holes"]]
    bay = layout.battery_bay().bounds
    c = layout.cfg["controller"]["center"]["x"]
    extra = [(c, round(bay[1] + 4.0, 3)), (c, round(bay[3] - 4.0, 3))]
    return holes + extra


def half_data(layout: Layout) -> dict:
    d: dict = {}
    d["outline"] = ring(layout.outline)
    d["holes"] = [(h["x"], h["y"]) for h in layout.cfg["mounting_holes"]]
    d["bay"] = ring(layout.battery_bay())
    well = well_polygon(layout)
    d["well"] = ring(well)
    parts = layout.back_parts()
    d["j3"] = ring(parts["J3"])
    d["rb1"] = ring(parts["RB1"])
    d["ps1"] = ring(parts["PS1"])
    rb = layout.cfg["reset_button"]["center"]
    d["reset"] = (rb["x"], rb["y"])
    ps = layout.cfg["power_switch"]["center"]
    d["switch"] = (ps["x"], ps["y"])
    d["ctrl_rect"] = controller_rect(layout)
    br = box_rect(layout)
    d["box_rect"] = br
    tp = layout.cfg["test_pads"]
    step = tp["pitch"]
    d["test_pads"] = [(round(tp["start"]["x"] + i * step, 3), tp["start"]["y"]) for i in range(9)]
    d["keys"] = [(k.x, k.y, k.rotation) for k in layout.keys]
    d["has_ball"] = layout.has_ball
    if layout.has_ball:
        d["ball_center"] = layout.ball_center
        d["housing_footprint"] = ring(layout.housing_footprint())
        d["housing_box"] = ring(layout.housing_box())
        d["case_screws"] = layout.case_screws()
        d["notch"] = ring(layout.notch_polygon())
        d["fpc_box"] = ring(layout.fpc_box())
        keep = [layout.housing_footprint().buffer(1.0), layout.pocket_polygon().buffer(1.0)]
    else:
        d["ball_center"] = (0.0, 0.0)
        d["housing_footprint"] = []
        d["housing_box"] = []
        d["case_screws"] = []
        d["notch"] = []
        d["fpc_box"] = []
        keep = []
    d["magnet_pads"] = magnet_pads(layout, br, keep)
    d["feet"] = feet(layout, br)
    sanity(layout, d, well)
    return d


def sanity(layout: Layout, d: dict, well: Polygon) -> None:
    problems = []
    pocket_well = Polygon(d["housing_box"]).buffer(0.5, join_style=2) if d["housing_box"] else None
    for x, y in d["holes"]:
        p = Point(x, y)
        if well.buffer(3.0).contains(p):
            problems.append(f"mounting hole ({x}, {y}) inside the battery well (standoff needs floor)")
        if pocket_well is not None and pocket_well.buffer(3.0).intersects(p):
            problems.append(f"mounting hole ({x}, {y}) inside the pocket well")
    pcb_wall = layout.outline.buffer(WALL_GUESS, join_style=2)
    for ax, ay, nx, ny in d["magnet_pads"]:
        rect = pad_rect((ax, ay), (nx, ny), WALL_GUESS, WALL_GUESS + PAD_OUT)
        if rect.buffer(-0.05).intersects(pcb_wall):
            problems.append(f"magnet pad at ({ax}, {ay}) overlaps the PCB plus wall")
    x0, y0, x1, y1 = d["box_rect"]
    ctrl = box(*d["ctrl_rect"]).buffer(CTRL_CLEAR, join_style=2)
    # boss protrusions into the box (see tray.scad boss_2d): 3.5 mm along the outer wall
    bosses = [box(x0 - 0.2, y0 - 0.2, x0 + 3.3, y0 + 3.3), box(x0 - 0.2, y1 - 6.6, x0 + 3.3, y1)]
    pads = [Point(p).buffer(1.0) for p in d["test_pads"]]
    for b in bosses:
        if b.intersects(ctrl):
            problems.append("controller box boss hits the controller courtyard")
        if any(b.intersects(p) for p in pads):
            problems.append("controller box boss hits a test pad")
    boxp = box(x0, y0, x1, y1)
    for k in layout.keys:
        if layout.keycap_polygon(k).buffer(0.5, join_style=2).intersects(boxp):
            problems.append(f"controller box overlaps keycap {k.ref}")
    if not boxp.contains(box(*d["ctrl_rect"]).intersection(layout.outline)):
        problems.append("controller board not inside the controller box")
    for x, y in d["feet"]:
        f = Point(x, y).buffer(FOOT_D / 2)
        if not layout.outline.buffer(WALL_GUESS - 0.3, join_style=2).contains(f):
            problems.append(f"foot at ({x}, {y}) outside the case floor")
        if Point(*d["reset"]).distance(Point(x, y)) < FOOT_D / 2 + 2.0:
            problems.append(f"foot at ({x}, {y}) over the reset hole")
        for sx, sy in d["case_screws"]:
            if Point(sx, sy).distance(Point(x, y)) < FOOT_D / 2 + 2.5:
                problems.append(f"foot at ({x}, {y}) over a case screw")
    if problems:
        raise SystemExit(f"{layout.half}: " + "; ".join(problems))


def render(data: dict[str, dict]) -> str:
    lines = ["// generated by scripts/gen_case.py, do not edit",
             "// Layout facts for both halves in the layout frame (mm): x outward (pinky), y towards",
             "// the user, origin at the middle-column top key. z is not part of this file.",
             "// Selector functions take the half name: outline(\"left\"), holes(\"right\"), ...", ""]
    names = ["outline", "holes", "bay", "well", "j3", "rb1", "ps1", "reset", "switch", "ctrl_rect", "box_rect",
             "test_pads", "keys", "has_ball", "ball_center", "housing_footprint", "housing_box", "case_screws",
             "notch", "fpc_box", "magnet_pads", "feet"]
    for name in names:
        for half in HALVES:
            v = data[half][name]
            if name == "has_ball":
                s = "true" if v else "false"
            elif name in ("reset", "switch", "ball_center"):
                s = f"[{fmt(v[0])}, {fmt(v[1])}]"
            elif name in ("ctrl_rect", "box_rect"):
                s = "[" + ", ".join(fmt(c) for c in v) + "]"
            elif name == "keys":
                s = "[" + ", ".join(f"[{fmt(x)}, {fmt(y)}, {fmt(r)}]" for x, y, r in v) + "]"
            elif name == "magnet_pads":
                s = "[" + ", ".join(f"[{fmt(x)}, {fmt(y)}, {fmt(nx)}, {fmt(ny)}]" for x, y, nx, ny in v) + "]"
            else:
                s = pts(v)
            lines.append(f"{name}_{half} = {s};")
        lines.append(f'function {name}(h) = h == "left" ? {name}_left : {name}_right;')
        lines.append("")
    return "\n".join(lines)


def build() -> dict[str, dict]:
    return {half: half_data(load_layout(half)) for half in HALVES}


def write_data(path: Path = DEFAULT_OUT) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(build()))
    return path


def main(argv: list[str]) -> None:
    out = Path(argv[1]) if len(argv) > 1 else DEFAULT_OUT
    write_data(out)
    data = build()
    for half in HALVES:
        d = data[half]
        print(f"{half:5s} outline {len(d['outline'])} pts, box {d['box_rect']}, pads {[(p[0], p[1]) for p in d['magnet_pads']]}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv)
