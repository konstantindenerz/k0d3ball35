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
import re
import sys
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, box
from shapely.affinity import translate
from shapely.ops import unary_union

from k0d3.geometry import HALVES, Layout, load_layout

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "hardware" / "case" / "data.scad"
PARAMS = REPO / "hardware" / "case" / "params.scad"


def scad_param(name: str) -> float:
    """A numeric literal from params.scad, so the guard outline below uses the same fits as the
    SCAD sources instead of a copy (changing one of these needs `make data`)."""
    m = re.search(rf"^{name}\s*=\s*(-?[\d.]+);", PARAMS.read_text(), flags=re.M)
    if m is None:
        raise SystemExit(f"params.scad: no numeric {name}")
    return float(m[1])

BOX_INNER_X = -45.5      # key-side wall of the controller box (params.scad box_inner_x)
BOX_CAP_CLEAR = 1.0      # controller box keeps this to every keycap
WELL_GROW = 1.0          # well = bay + J3 + RB1 courtyards grown by this
WALL_GUESS = 3.2         # pcb_clear + wall, only for the sanity checks here
FOOT_D = 10.5
LIP_IN = 0.2 - 0.15 - 0.5   # params.scad pcb_clear - lid_fit - lid_lip_chamfer
MAGNET_D = 6.2           # foot magnet pocket (params.scad magnet_d)
MAGNET_INSET = 8.0       # foot magnet centres this far inside the PCB outline / the hinge line
HINGE_X = -13.0          # lid hinge line (x = const, runs front to back) on a half without a ball
POCKET_RING_R = 17.2     # notch apothem 15 + 0.2 clearance + 2 mm pocket wall (params.scad)
HINGE_POCKET_CLEAR = 0.8 # on the ball half the hinge line sits this far inboard of that ring
HINGE_STRIP = 6.0        # the hinge strip under the lid roof, no roof pocket within this of the line
WALL_LID = 3.2           # pcb_clear + wall: the lid skirt outer face beyond the PCB outline
FOOT_OVERHANG = 3.0      # as a foot the hinge axis sits this far outside the inner tray wall
WINDOW_D = 16.0          # ball window in the lid roof (params.scad ball_window_d)
CTRL_CLEAR = 1.0         # boss protrusions keep this to the controller board
# Ball pocket "in one piece" (r2.4 fix): the case edge runs square around the pocket like it does
# around the keys, the tray is solid up to the rim there, and only a rectangular opening for the
# cradle stays open. A flush cover plate sits on a ledge in that opening.
POCKET_LEDGE = 4.0       # cover overlap on the tray beyond the opening (params.scad pocket_ledge)
POCKET_WALL = 2.0        # tray wall outside the ledge
COVER_SCREW_IN = 1.8     # cover screws: this far outside the opening (pilot 1.6 keeps 1.0 to it)
COVER_SCREW_EDGE = 2.2   # ... and on the thumb side this far inside the cover edge
COVER_PCB_CLEAR = 0.2    # rebate edge = PCB cavity edge (pcb_clear): no skin between the two cuts
CLOSE_R = 9.0            # orthogonal closing radius that merges the pocket block into the edge


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


def hinge_x(layout: Layout) -> float:
    """The hinge line has to clear the ball pocket, so on the ball half it follows the ball
    instead of being a constant: the pocket ring would otherwise sit on the line and the lid's
    ball window would be cut in half."""
    if not layout.has_ball:
        return HINGE_X
    return round(layout.ball_center[0] - POCKET_RING_R - HINGE_POCKET_CLEAR, 1)


def foot_dx(layout: Layout) -> float:
    """As a foot the lid is shifted inward until its hinge axis sits FOOT_OVERHANG outside the
    inner tray wall: the outer plate lies under the controller half, the inner plate folds down
    beyond the inner edge as the kickstand. Board x = lid x + foot_dx."""
    minx = layout.outline.bounds[0]
    return round(minx - WALL_LID - FOOT_OVERHANG - hinge_x(layout), 3)


def foot_magnets(layout: Layout, box_r, keep_out: list[Polygon], dx: float) -> list[tuple[float, float]]:
    """Four 6 x 2 mm magnets in the tray floor for the lid-as-foot, returned in the board frame.
    They sit in the roof of the outer lid plate (lid frame: x > HINGE_X + the hinge strip, inside
    the outline by MAGNET_INSET, clear of the ball window) and, shifted by foot_dx, in thick
    floor of the tray (board frame: clear of the battery well, the pocket well and the FFC
    channel by 2 mm, of the standoffs by 3, of the feet recesses by 1 and of the controller box
    bosses). The search walks the inset contour of the allowed region from each of its corners
    in both directions until a free point is found."""
    poly = layout.outline
    minx, miny, maxx, maxy = poly.bounds
    inset = poly.buffer(-MAGNET_INSET, join_style=2)
    hx = hinge_x(layout)
    lid_region = inset.intersection(box(hx + HINGE_STRIP + MAGNET_D / 2 + 0.5, miny - 1, maxx + 1, maxy + 1))
    board_region = translate(inset, -dx, 0)
    allowed = lid_region.intersection(board_region)
    assert allowed.geom_type == "Polygon", allowed.geom_type
    ring_ls = LineString(allowed.exterior.coords)
    length = ring_ls.length
    ax0, ay0, ax1, ay1 = allowed.bounds
    corners = [(ax0, ay0), (ax1, ay0), (ax1, ay1), (ax0, ay1)]
    x0, y0, x1, y1 = box_r
    bosses = [box(x0 - 0.2, y0 - 0.2, x0 + 3.3, y0 + 3.3), box(x0 - 0.2, y1 - 6.6, x0 + 3.3, y1)]
    holes = [Point(h["x"], h["y"]).buffer(3.0) for h in layout.cfg["mounting_holes"]]
    foot_circles = [Point(f).buffer(FOOT_D / 2 + 1.0) for f in feet(layout, box_r)]
    board_blocked = unary_union(keep_out + bosses + holes + foot_circles)
    blocked = translate(board_blocked, -dx, 0)          # into the lid frame
    if layout.has_ball:
        blocked = unary_union([blocked, Point(layout.ball_center).buffer(WINDOW_D / 2 + 1.0)])
    magnets = []
    for corner in corners:
        t0 = ring_ls.project(Point(corner))
        found = None
        step = 0.5
        for k in range(int(length / step) + 1):
            for sign in ((1, -1) if k else (1,)):
                t = (t0 + sign * k * step) % length
                c = ring_ls.interpolate(t)
                disc = c.buffer(MAGNET_D / 2)
                if disc.intersects(blocked):
                    continue
                if any(Point(m).distance(Point(c.x + dx, c.y)) < MAGNET_D + 2.0 for m in magnets):
                    continue
                found = (round(c.x + dx, 3), round(c.y, 3))
                break
            if found:
                break
        assert found is not None, f"no foot magnet position near corner {corner}"
        magnets.append(found)
    return magnets


def feet(layout: Layout, box_r) -> list[tuple[float, float]]:
    """Rubber feet: the five mounting holes projected onto the floor plus two under the
    controller block so the half does not rock when a thumb key is pressed."""
    holes = [(h["x"], h["y"]) for h in layout.cfg["mounting_holes"]]
    bay = layout.battery_bay().bounds
    c = layout.cfg["controller"]["center"]["x"]
    extra = [(c, round(bay[1] + 4.0, 3)), (c, round(bay[3] - 4.0, 3))]
    return holes + extra


def pocket_opening(layout: Layout) -> Polygon:
    """The rectangle left open over the cradle: its well, the cradle circle and the cable path
    over the PCB edge to J1. Nothing else of the old PCB notch has to stay open."""
    tb = layout.cfg["trackball"]
    parts = [layout.housing_box().buffer(0.5, join_style=2),
             Point(layout.ball_center).buffer(tb["cradle_diameter"] / 2 + 0.2, 64)]
    if layout.cable_corridor() is not None:
        parts.append(layout.cable_corridor())
    return box(*unary_union(parts).bounds)


def cover_rect(layout: Layout) -> tuple[float, float, float, float]:
    """The rebate the cover sits in: the opening plus the ledge, but on the thumb side only up to
    the PCB edge at the notch, so the seam runs straight instead of around the PCB corner."""
    x0, y0, x1, y1 = pocket_opening(layout).bounds
    nx0 = layout.notch_polygon().bounds[0]
    return (round(max(x0 - POCKET_LEDGE, nx0 + COVER_PCB_CLEAR), 3), round(y0 - POCKET_LEDGE, 3),
            round(x1 + POCKET_LEDGE, 3), round(y1 + POCKET_LEDGE, 3))


def case_outline(layout: Layout) -> Polygon:
    """Outer edge of the tray on the ball half: the wall around the PCB plus the pocket block
    (cover rebate + wall; on the thumb side it stays right of the lid hinge line), closed square so the edge steps at 90 degrees into the thumb edge
    and the inner column instead of standing out as a separate box. Only the fill pieces that
    touch the pocket block are taken, so the steps along the keys stay exactly as they are."""
    body = layout.outline.buffer(WALL_LID, join_style=2)
    block = box(*cover_rect(layout)).buffer(POCKET_WALL, join_style=2)
    both = body.union(block)
    closed = both.buffer(CLOSE_R, join_style=2, cap_style=3).buffer(-CLOSE_R, join_style=2, cap_style=3)
    # keep only the fill pieces that touch the pocket block: the steps along the keys stay as they are
    gaps = closed.difference(both)
    pieces = [g for g in getattr(gaps, "geoms", [gaps]) if g.area > 0.01 and g.distance(block) < 0.01]
    out = unary_union([both, *pieces]).simplify(0.001)
    assert out.geom_type == "Polygon" and not out.interiors, out.geom_type
    return out


def cover_screws(layout: Layout) -> list[tuple[float, float]]:
    """Two screws on the user-side ledge (the other side of the cover ends at the PCB)."""
    x0, y0, x1, y1 = pocket_opening(layout).bounds
    cx0 = cover_rect(layout)[0]
    k = COVER_SCREW_IN
    return [(round(cx0 + COVER_SCREW_EDGE, 3), round(y1 + k, 3)), (round(x1 + k, 3), round(y1 + k, 3))]


def guard_polygon(layout: Layout, box_r) -> Polygon:
    """The PCB guard (params.scad, PCB guard): a plate on the PCB top between the switches. The
    PCB area minus a square per switch housing, the PCB screw heads, the controller box, J1 and
    the FFC path and the cradle opening. It is built here and not in OpenSCAD because it has to
    come out as ONE piece without thin necks: the screw head holes sit in the webs between the
    keys and cut some strips off; such a strip would lie loose in the case. So every web
    narrower than guard_min_web is cut through, only the largest piece is kept, and it grows
    back to its full outline."""
    fit, web = scad_param("guard_fit"), scad_param("guard_min_web")
    side = scad_param("switch_lower") + 2 * fit
    pcb_clear, fpc_clear = scad_param("pcb_clear"), scad_param("fpc_clear")
    plate = layout.outline.buffer(pcb_clear - fit, join_style=2) if pcb_clear != fit else layout.outline
    cuts = []
    for k in layout.keys:
        sq = box(-side / 2, -side / 2, side / 2, side / 2)
        a = math.radians(-k.rotation)          # tray.scad: rotate(-k[2])
        c, s_ = math.cos(a), math.sin(a)
        cuts.append(Polygon([(k.x + x * c - y * s_, k.y + x * s_ + y * c) for x, y in sq.exterior.coords]))
    cuts += [Point(h["x"], h["y"]).buffer(scad_param("guard_screw_d") / 2, 64) for h in layout.cfg["mounting_holes"]]
    x0, y0, _, y1 = box_r
    cuts.append(box(x0, y0, BOX_INNER_X, y1).buffer(fit, join_style=2))
    if layout.has_ball:
        cuts.append(layout.fpc_box().buffer(fpc_clear + fit, join_style=2))
        if layout.cable_corridor() is not None:
            cuts.append(layout.cable_corridor().buffer(fpc_clear + fit, join_style=2))
        cuts.append(Point(layout.ball_center).buffer(scad_param("cradle_d") / 2 + fit, 64))
        cuts.append(layout.notch_polygon().buffer(pcb_clear + fit, join_style=2))
        cuts.append(pocket_opening(layout).buffer(fit, join_style=2))
    raw = plate.difference(unary_union(cuts))
    core = raw.buffer(-web / 2, 32)
    core = max(getattr(core, "geoms", [core]), key=lambda g: g.area)
    out = core.buffer(web / 2, 32).intersection(raw).simplify(0.01)
    if out.geom_type != "Polygon":       # slivers of the intersection along the cuts
        out = max(out.geoms, key=lambda g: g.area)
    return out


def guard_rings(poly: Polygon) -> list[list[tuple[float, float]]]:
    """Outer ring first, then the holes (each counter-clockwise, see ring())."""
    return [ring(poly)] + [ring(Polygon(i)) for i in poly.interiors]


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
        d["case_outline"] = ring(case_outline(layout))
        d["pocket_opening"] = tuple(round(c, 3) for c in pocket_opening(layout).bounds)
        d["cover_rect"] = cover_rect(layout)
        d["cover_screws"] = cover_screws(layout)
        d["case_screws"] = layout.case_screws()
        d["notch"] = ring(layout.notch_polygon())
        d["fpc_box"] = ring(layout.fpc_box())
        d["cable_corridor"] = ring(layout.cable_corridor()) if layout.cable_corridor() is not None else []
        keep = [layout.housing_box().buffer(0.5, join_style=2).buffer(2.0, join_style=2),
                layout.notch_polygon().buffer(2.0, join_style=2),
                layout.fpc_box().buffer(2.0, join_style=2)]
        if layout.cable_corridor() is not None:
            keep.append(layout.cable_corridor().buffer(2.0, join_style=2))
    else:
        d["ball_center"] = (0.0, 0.0)
        d["housing_footprint"] = []
        d["housing_box"] = []
        d["case_outline"] = []
        d["pocket_opening"] = (0.0, 0.0, 0.0, 0.0)
        d["cover_rect"] = (0.0, 0.0, 0.0, 0.0)
        d["cover_screws"] = []
        d["case_screws"] = []
        d["notch"] = []
        d["fpc_box"] = []
        d["cable_corridor"] = []
        keep = []
    keep.append(well.buffer(2.0, join_style=2))
    # Two candidates touch the desk when the kickstand folds down, and which one wins depends
    # on the fold: the lip sits 3 mm lower, the skirt's outer face 3.65 mm further out, so the
    # skirt takes over above about 39 degrees. Both are the true extremes of their own ring -
    # on an outline with mitred corners that is not minx of the outline plus an offset.
    d["lip_min_x"] = round(layout.outline.buffer(LIP_IN, join_style=2).bounds[0], 3)
    d["skirt_min_x"] = round(layout.outline.buffer(WALL_LID, join_style=2).bounds[0], 3)
    d["hinge_x"] = hinge_x(layout)
    d["foot_dx"] = foot_dx(layout)
    d["foot_magnets"] = foot_magnets(layout, br, keep, d["foot_dx"])
    d["feet"] = feet(layout, br)
    d["guard"] = guard_rings(guard_polygon(layout, br))
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
    keep_outs = [well.buffer(2.0, join_style=2)] + [Point(x, y).buffer(3.0) for x, y in d["holes"]]
    if pocket_well is not None:
        keep_outs += [pocket_well.buffer(2.0, join_style=2)]
    if len(d["foot_magnets"]) != 4:
        problems.append("four foot magnets expected")
    for x, y in d["foot_magnets"]:
        disc = Point(x, y).buffer(MAGNET_D / 2)
        if not layout.outline.buffer(WALL_GUESS - 0.5, join_style=2).contains(disc):
            problems.append(f"foot magnet at ({x}, {y}) outside the case floor")
        if any(disc.intersects(k) for k in keep_outs):
            problems.append(f"foot magnet at ({x}, {y}) in a well, channel or standoff")
        lx = x - d["foot_dx"]
        if lx - MAGNET_D / 2 < d["hinge_x"] + HINGE_STRIP + 0.5:
            problems.append(f"foot magnet at ({x}, {y}) under the hinge strip of the lid roof")
        if not layout.outline.buffer(-3.0, join_style=2).contains(Point(lx, y).buffer(MAGNET_D / 2)):
            problems.append(f"foot magnet at ({x}, {y}) outside the lid roof")
        if d["has_ball"] and Point(lx, y).distance(Point(d["ball_center"])) < WINDOW_D / 2 + MAGNET_D / 2 + 1.0:
            problems.append(f"foot magnet at ({x}, {y}) in the ball window")
    # as a foot every rubber foot is either fully on the outer lid plate or fully off it
    plate_x1 = layout.outline.bounds[2] + WALL_LID + d["foot_dx"]
    for x, y in d["feet"]:
        if abs(x - plate_x1) < FOOT_D / 2 + 0.5:
            problems.append(f"foot at ({x}, {y}) straddles the lid plate edge at x {plate_x1:.2f}")
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
             "case_outline", "pocket_opening", "cover_rect", "cover_screws",
             "notch", "fpc_box", "cable_corridor", "hinge_x", "lip_min_x", "skirt_min_x", "foot_dx", "foot_magnets", "feet", "guard"]
    for name in names:
        for half in HALVES:
            v = data[half][name]
            if name == "has_ball":
                s = "true" if v else "false"
            elif name in ("hinge_x", "lip_min_x", "skirt_min_x", "foot_dx"):
                s = fmt(v)
            elif name in ("reset", "switch", "ball_center"):
                s = f"[{fmt(v[0])}, {fmt(v[1])}]"
            elif name in ("ctrl_rect", "box_rect", "pocket_opening", "cover_rect"):
                s = "[" + ", ".join(fmt(c) for c in v) + "]"
            elif name == "guard":
                s = "[" + ", ".join(pts(r) for r in v) + "]"
            elif name == "keys":
                s = "[" + ", ".join(f"[{fmt(x)}, {fmt(y)}, {fmt(r)}]" for x, y, r in v) + "]"
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
        print(f"{half:5s} outline {len(d['outline'])} pts, box {d['box_rect']}, foot magnets {d['foot_magnets']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv)
