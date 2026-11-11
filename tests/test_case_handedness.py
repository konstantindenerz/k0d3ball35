# SPDX-License-Identifier: MIT
"""The exported case and cradle files are the real parts, not their mirror images.

The SCAD sources model in the layout frame (x outward, y towards the user, z up), which is
left-handed; the export flips y once (issues/mech-case-stl-mirrored.md). The other tests undo
that flip and compare with the layout. This file does not: it reads the committed STLs as a
slicer does (right-handed, z up) and compares them with the KiCad boards seen from above, the
other source of truth. KiCad's y points down the screen, towards the user, so a board point
(kx, ky) lies at (kx - 120, 60 - ky) in the print frame (KiCad = layout + (120, 60), left board
mirrored in x like the left case). A y-mirrored export puts the controller box, the ball pocket
and the cradle's cable slot on the wrong side and fails here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "hardware" / "case"
CRADLE = ROOT / "hardware" / "trackball-cradle"
OFFSET = (120.0, 60.0)
PCB_T = 1.6

trimesh = pytest.importorskip("trimesh")
np = pytest.importorskip("numpy")


def to_print(kx: float, ky: float) -> tuple[float, float]:
    return kx - OFFSET[0], OFFSET[1] - ky


def board(half: str) -> dict:
    """Footprint positions and the Edge.Cuts outline of a main board, in the print frame."""
    text = (ROOT / "hardware" / f"{half}-pcb" / f"k0d3ball35-{half}.kicad_pcb").read_text()
    refs = {}
    for m in re.finditer(r'\(footprint "[^"]+"(.*?)\(property "Reference" "([^"]+)"', text, flags=re.S):
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)", m[1])
        refs[m[2]] = to_print(float(at[1]), float(at[2]))
    edge = text.index('(layer "Edge.Cuts")')
    poly = text[text.rindex("(gr_poly", 0, edge):edge]
    outline = [to_print(float(x), float(y)) for x, y in re.findall(r"\(xy ([-\d.]+) ([-\d.]+)\)", poly)]
    return {"refs": refs, "outline": np.array(outline)}


def stack(half: str) -> dict:
    return json.loads((CASE / "stack.json").read_text())["variants"][half]


@pytest.mark.parametrize("half", ["left", "right"])
def test_tray_lies_on_the_board_not_on_its_mirror_image(half):
    b = board(half)
    v = trimesh.load(CASE / "stl" / f"tray-{half}.stl", force="mesh").vertices
    lo, hi = b["outline"].min(axis=0), b["outline"].max(axis=0)
    # the tray encloses the board outline with its wall (a few mm), on both axes
    for axis in (0, 1):
        assert 0 < lo[axis] - v[:, axis].min() < 8, (half, axis, lo[axis], v[:, axis].min())
        assert 0 < v[:, axis].max() - hi[axis] < 8, (half, axis, hi[axis], v[:, axis].max())
    # the controller box (the highest walls) stands over the controller U1
    top = v[v[:, 2] > stack(half)["box_top_z"] - 0.3][:, :2].mean(axis=0)
    u1 = np.array(b["refs"]["U1"])
    assert np.hypot(*(top - u1)) < 10, (half, top, u1)
    assert np.hypot(*(top - u1 * [1, -1])) > 20, "the box would also fit the mirrored board"


def _covered_above(mesh, xy, zmin):
    """True if a vertical line through xy meets the mesh anywhere above zmin."""
    t = mesh.triangles
    a, b, c = t[:, 0, :2], t[:, 1, :2], t[:, 2, :2]
    p = np.asarray(xy, dtype=float)

    def cross(u, v, w):
        return (v[:, 0] - u[:, 0]) * (w[1] - u[:, 1]) - (v[:, 1] - u[:, 1]) * (w[0] - u[:, 0])

    d1, d2, d3 = cross(a, b, p), cross(b, c, p), cross(c, a, p)
    inside = ((d1 >= 0) & (d2 >= 0) & (d3 >= 0)) | ((d1 <= 0) & (d2 <= 0) & (d3 <= 0))
    hits = t[inside]
    if not len(hits):
        return False
    # z of each hit triangle at xy, from its plane
    v0, v1, v2 = hits[:, 0], hits[:, 1], hits[:, 2]
    n = np.cross(v1 - v0, v2 - v0)
    ok = np.abs(n[:, 2]) > 1e-12
    z = v0[ok, 2] - (n[ok, 0] * (p[0] - v0[ok, 0]) + n[ok, 1] * (p[1] - v0[ok, 1])) / n[ok, 2]
    return bool((z > zmin).any())


def test_ball_pocket_sits_in_the_board_notch():
    b = board("right")
    right = json.loads((ROOT / "hardware/layout/output/points-right.json").read_text())
    tb = right["trackball"]["center"]
    ball = np.array(to_print(tb["x"] + OFFSET[0], tb["y"] + OFFSET[1]))
    # the KiCad outline has its octagonal notch around that point (apothem 15)
    d = np.hypot(*(b["outline"] - ball).T)
    assert 14.9 < d.min() < 16.5, d.min()
    v = trimesh.load(CASE / "stl" / "tray-right.stl", force="mesh").vertices
    above = v[v[:, 2] > -PCB_T + 0.05]
    r = np.hypot(above[:, 0] - ball[0], above[:, 1] - ball[1])
    assert r.min() >= 14.0, "nothing of the tray in the cradle circle"
    assert ((r > 14.0) & (r < 20.0)).sum() > 0, "the pocket wall stands where the board is not"
    # The notch corner towards the keys is SQUARE so the FFC can fold over the board edge there
    # into J1 (r2.2). Nothing of the tray may stand in that corner above the PCB. A stale regular
    # octagon in the case once put the pocket wall right into it (r2.4).
    mesh = trimesh.load(CASE / "stl" / "tray-right.stl", force="mesh")
    corner = ball + 0.89 * np.array([-15.5, 15.5])        # 2.4 mm inside the square corner (print frame)
    assert not _covered_above(mesh, corner, -PCB_T + 0.05), "tray material in the FFC corner"


def test_tilted_sensor_leans_away_from_the_keys():
    """The tilted module must sit away from the keys, and its FFC notch must face them.

    Until r2.4 the sensor sat straight under the ball in an axis-aligned housing, so this test
    looked for a slot at a fixed coordinate in that wall. The module is tilted now (sensor_az), so
    there is no such wall; what still has to hold is the DIRECTION. The sleeve has to lean away
    from the keys - towards the sleeve the PCB carries the thumb bridge and J1, and a sleeve on
    that side does not fit - and the cable has to leave towards the keys to reach J1 through the
    2.95 mm annular gap between the cup envelope and the PCB notch.

    Two frames meet here and both bit the author of r2.4: the STACK values and sensor_az are in
    the LAYOUT frame, while cradle.scad flips y once for the export, so the printed part has the
    keys at +y. A wrong azimuth, or forgetting the flip, puts the module on the keys - which is
    what this test catches.
    """
    b = board("right")
    right = json.loads((ROOT / "hardware/layout/output/points-right.json").read_text())
    ball_y = OFFSET[1] - (right["trackball"]["center"]["y"] + OFFSET[1])
    keys_y = np.mean([p[1] for ref, p in b["refs"].items() if re.fullmatch(r"SW\d+", ref)])
    assert keys_y > ball_y, "the keys are on +y of the ball in the print frame"

    s = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    v = trimesh.load(CRADLE / "stl" / "cradle-19mm-pocket.stl", force="mesh").vertices
    cup_r = s["cup_outer_d"] / 2

    # everything beyond the cup's own radius is the tilted sleeve
    sleeve = v[np.hypot(v[:, 0], v[:, 1]) > cup_r + 0.2]
    assert len(sleeve) > 0, "no sleeve outside the cup radius - is the sensor still tilted?"
    reach_keys, reach_away = sleeve[:, 1].max(), -sleeve[:, 1].min()
    assert reach_away > reach_keys, (
        f"the sleeve reaches {reach_keys:.2f} mm towards the keys but only {reach_away:.2f} mm "
        "away from them: the tilt azimuth or the export's y flip is wrong")
    assert reach_away > cup_r, "the sleeve does not reach past the cup at all"
