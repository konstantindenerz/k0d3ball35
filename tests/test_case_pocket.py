# SPDX-License-Identifier: MIT
"""The ball pocket is part of the case, not a box stuck to it.

r2.4 shipped a pocket that stood in front of the stepped edge as a rounded block, open from
above down to the cradle well, and a lid that ended at the PCB edge so the ball stuck out in
transport. Every numeric check passed; it took a look at the site to see it. These tests pin
what the eye caught:

- the lid covers the whole tray footprint (both halves),
- seen from above, tray plus pocket cover are closed at rim height everywhere outside the key
  cavity, except the funnel to the ball,
- the pocket part of the case edge runs in 90 degree steps like the rest of the edge,
- the cover sits flush in its rebate and clears the cradle.
"""
import json
import math
import re
from pathlib import Path

import numpy as np
import pytest

shapely = pytest.importorskip("shapely")
trimesh = pytest.importorskip("trimesh")
from shapely.geometry import LineString, Point, Polygon, box  # noqa: E402

from scad_frame import load_layout_frame  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "hardware" / "case"
CRADLE = ROOT / "hardware" / "trackball-cradle"


def _data() -> dict:
    out: dict = {}
    for m in re.finditer(r"^(\w+)_(left|right) = (.*);$", (CASE / "data.scad").read_text(), re.M):
        out.setdefault(m.group(1), {})[m.group(2)] = json.loads(m.group(3))
    return out


DATA = _data()
STACK = json.loads((CASE / "stack.json").read_text())["variants"]
GRID = 1.0


def _top_z(mesh, xy):
    """Highest surface over each (x, y), NaN where the mesh is not hit (layout frame)."""
    origins = np.column_stack([xy, np.full(len(xy), 100.0)])
    dirs = np.tile([0.0, 0.0, -1.0], (len(xy), 1))
    loc, idx, _ = mesh.ray.intersects_location(origins, dirs, multiple_hits=False)
    z = np.full(len(xy), np.nan)
    z[idx] = loc[:, 2]
    return z


def _grid(poly, step=GRID):
    x0, y0, x1, y1 = poly.bounds
    # a quarter step off the mm grid keeps the samples off the axis-aligned edges
    xs = np.arange(x0 + step / 4, x1, step)
    ys = np.arange(y0 + step / 4, y1, step)
    pts = np.array([(x, y) for x in xs for y in ys])
    return pts[[poly.contains(Point(p)) for p in pts]]


def _mirror(half, pts):
    """data.scad is in the layout frame of the right-handed model; the left STL is mirrored in x."""
    return pts * [-1, 1] if half == "left" else pts


def _outline(half):
    pcb = Polygon(DATA["outline"][half]).buffer(3.2, join_style=2)
    extra = DATA.get("case_outline", {}).get(half) or DATA.get("housing_footprint", {}).get(half)
    return pcb.union(Polygon(extra)) if extra else pcb


@pytest.mark.parametrize("half", ["left", "right"])
def test_lid_covers_the_whole_tray(half):
    tray = load_layout_frame(CASE / "stl" / f"tray-{half}.stl")
    lid = load_layout_frame(CASE / "stl" / f"lid-{half}.stl")
    # the flush pin hinge shows its knuckle clearance from above: a designed slit, not a hole
    hx, r = DATA["hinge_x"][half], STACK[half]["hinge_knuckle_d"] / 2 + 1.0
    area = _outline(half).buffer(-0.6, join_style=2).difference(box(hx - r, -500, hx + r, 500))
    pts = _mirror(half, _grid(area))
    under = ~np.isnan(_top_z(tray, pts))
    covered = ~np.isnan(_top_z(lid, pts))
    bare = pts[under & ~covered]
    assert len(bare) == 0, f"{half}: {len(bare)} mm2 of tray outside the lid, e.g. {bare[:3].tolist()}"


def test_pocket_is_closed_at_rim_height():
    half = "right"
    tray = load_layout_frame(CASE / "stl" / f"tray-{half}.stl")
    cover = load_layout_frame(CASE / "stl" / f"pocket-cover-{half}.stl")
    both = trimesh.util.concatenate([tray, cover])
    s = STACK[half]
    rim = s["rim_z"]
    bx, by = DATA["ball_center"][half]
    funnel = Point(bx, by).buffer(s["cover_hole_d"] / 2 + 0.4 + 0.3)        # the hole and its top chamfer
    x0, y0, x1, y1 = DATA["cover_rect"][half]
    seam = box(x0, y0, x1, y1).exterior.buffer(0.4)            # the 0.15 fit gap around the cover
    screws = [Point(p).buffer(2.3) for p in DATA["cover_screws"][half]]
    # the two holes for the optional clip's pins
    screws += [Point(bx + s["clip_pin_r"] * math.cos(math.radians(a)), by + s["clip_pin_r"] * math.sin(math.radians(a))).buffer(1.6)
               for a in (s["clip_pin_az"], -s["clip_pin_az"])]
    region = (_outline(half).buffer(-0.8, join_style=2)        # rim chamfer at the outer edge
              .difference(Polygon(DATA["outline"][half]).buffer(0.2 + 0.5, join_style=2))   # key cavity
              .difference(funnel).difference(seam)
              .intersection(box(x0, y0, x1, y1).buffer(20, join_style=2)))   # the pocket and its neighbours
    for sc in screws:
        region = region.difference(sc)
    pts = _grid(region)
    z = _top_z(both, pts)
    low = pts[~(z > rim - 0.05)]
    assert len(low) == 0, f"{len(low)} mm2 open or below the rim outside the key cavity, e.g. {low[:3].tolist()}"


def test_pocket_edge_runs_in_right_angles():
    """Every edge the pocket adds to the case outline is axis-aligned."""
    case = DATA["case_outline"]["right"]
    pcb = Polygon(DATA["outline"]["right"]).buffer(3.2, join_style=2)
    n = len(case)
    added = []
    for i in range(n):
        a, b = case[i], case[(i + 1) % n]
        seg = LineString([a, b])
        if pcb.exterior.buffer(0.01).contains(seg):
            continue                                            # the old edge around the keys
        added.append((a, b))
        assert abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6, f"slanted pocket edge {a} -> {b}"
    assert added, "no pocket edges found"
    assert not Polygon(case).interiors


def test_pocket_cover_is_flush_and_clears_the_cradle():
    s = STACK["right"]
    cover = load_layout_frame(CASE / "stl" / "pocket-cover-right.stl")
    assert cover.is_watertight
    assert abs(cover.bounds[1][2] - s["rim_z"]) < 0.01, "cover top not flush with the rim"
    assert abs(cover.bounds[0][2] - s["cover_z0"]) < 0.01
    cr = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    # the cover is a bezel over the cup rim: more than a print layer above the whole cradle ...
    assert cr["sleeve_top_z"] < s["cover_z0"] - 0.3
    assert cr["housing_top_z"] < s["cover_z0"] - 0.3
    assert cr["rim_z"] < s["cover_z0"] - 0.3
    # ... its hole hides the cup (smaller than the cup's outer wall) ...
    assert s["cover_hole_d"] < cr["cup_outer_d"] - 2.0
    # ... and stays off the ball even with cradle and cover 0.3 mm off each other; the ball radius
    # under the cover top is what the hole has to clear, and the ball still lifts out through it
    r_ball, zc = cr["ball_d"] / 2, cr["ball_centre_z"]
    widest = max(math.sqrt(max(0.0, r_ball ** 2 - (z - zc) ** 2)) for z in (s["cover_z0"], s["rim_z"], zc)
                 if s["cover_z0"] <= z <= s["rim_z"])
    assert s["cover_hole_d"] / 2 - widest - 0.3 >= 0.4
    assert s["cover_hole_d"] > cr["ball_d"]
    # the cover stays out of the key cavity (keycaps and J1 sit there)
    keys = Polygon(DATA["outline"]["right"]).buffer(0.2, join_style=2)
    v = cover.vertices
    inside = [Point(x, y) for x, y in v[:, :2] if keys.buffer(-0.05).contains(Point(x, y))]
    assert not inside, f"cover reaches over the PCB at {inside[:3]}"
