# SPDX-License-Identifier: MIT
"""Checks for the optional clip-on ball retainer (hardware/trackball-cradle, part = "retainer").

The retainer is a ring that snaps onto the cup and puts two claws over the ball's shoulders, one
on each side of the thumb's approach (issues/mech-ball-retainer-clip.md). What it has to do:

* keep the ball in when the half is turned over, with room for print error
  (retention.py: configuration-space flood fill, committed as retention.json),
* never touch the ball in use, and not drag it along when it is pulled off,
* leave the thumb side open above the cup rim,
* fit the cradle (no overlap, clear of whatever of it stands outside the cup wall above the board
  plane - the bearing bosses, and since r2.4 the tilted sensor sleeve) and the case (pocket wall,
  lid roof, lid hinge strip, FFC corridor),
* come off by hand: a snap with a small undercut on fingers that do not overstrain.
"""
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
import yaml
from scad_frame import load_layout_frame

ROOT = Path(__file__).resolve().parents[1]
CRADLE = ROOT / "hardware" / "trackball-cradle"
SCAD = CRADLE / "cradle.scad"
CASE = ROOT / "hardware" / "case"
LAYOUT_OUT = ROOT / "hardware" / "layout" / "output" / "points-right.json"

# One variant since r2.4: the 25 mm ball and the r1 "cutout" mount (cup through a round PCB
# cutout, flange under the board) were dropped, and with them the `mount` parameter, so the
# three-variant table collapsed to the single supported build (params.scad, "mounting").
VARIANTS = {
    "19mm-pocket": {"ball_d": 19.05},
}
MIN_GUARANTEED_MARGIN = 0.5   # mm of combined looseness (print error, small ball, claw flex) the trap survives
MIN_REST_GAP = 0.35           # design gap 0.4 (ball_gap) less facetting
MIN_OPEN_SECTOR = 150         # degrees above the rim free of retainer, centred on the thumb side
MIN_THUMB_TO_CLAW = 60        # degrees between a thumb key's direction and the nearest claw edge


def openscad():
    for cand in (shutil.which("openscad"), "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"):
        if cand and Path(cand).exists():
            return cand
    return None


def render(part, overrides, out):
    cmd = [openscad(), "--backend", "manifold", "-D", f'part="{part}"']
    for k, v in overrides.items():
        cmd += ["-D", f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"]
    cmd += ["-o", str(out), str(SCAD)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=600)


def finger_table():
    """retainer_fingers from params.scad as [[azimuth, width], ...]."""
    params = (CRADLE / "params.scad").read_text()
    m = re.search(r"^retainer_fingers\s*=\s*(\[.*?\]);", params, re.M | re.S)
    return json.loads(m.group(1))


def scad_values(path):
    """name = number assignments of a .scad file (simple literals only)."""
    vals = {}
    for m in re.finditer(r"^(\w+)\s*=\s*(-?[\d.]+)\s*;", path.read_text(), re.M):
        vals[m.group(1)] = float(m.group(2))
    return vals


@pytest.fixture(scope="module")
def stack():
    return json.loads((CRADLE / "stack.json").read_text())["variants"]


@pytest.fixture(scope="module")
def retention():
    return json.loads((CRADLE / "retention.json").read_text())["variants"]


# ------------------------------------------------------------------ committed analysis

def test_retention_json_covers_every_variant(retention):
    assert set(retention) == set(VARIANTS)


@pytest.mark.parametrize("name", list(VARIANTS))
def test_ball_is_trapped_with_margin(retention, name):
    v = retention[name]
    # negative control: the same analysis lets the ball out of the open cup
    assert v["without_retainer_trapped"] is False
    assert v["trapped"] is True
    assert v["guaranteed_margin"] >= MIN_GUARANTEED_MARGIN, v["guaranteed_margin"]
    assert v["guaranteed_margin"] < v["critical_margin"]


@pytest.mark.parametrize("name", list(VARIANTS))
def test_claws_stay_off_the_ball(retention, stack, name):
    v, s = retention[name], stack[name]
    assert v["rest_gap"] >= MIN_REST_GAP
    assert abs(s["retainer_ball_gap"] - 0.4) < 1e-9
    # pulling the ring straight up never brings a claw closer than it is at rest
    assert v["pull_off_min_gap"] >= v["rest_gap"] - 0.01
    # the ball can rattle a little but not lift far (the sensor loses it above 2.6 mm anyway)
    assert 0.3 <= v["ball_lift_play"] <= 1.2
    # analytic play from the model agrees with the measured one
    assert abs(v["ball_lift_play"] - s["retainer_ball_play"]) < 0.1


@pytest.mark.parametrize("name", list(VARIANTS))
def test_thumb_side_is_open(retention, stack, name):
    v, s = retention[name], stack[name]
    assert v["open_sector_deg"] >= MIN_OPEN_SECTOR
    assert abs(v["open_sector_deg"] - s["retainer_open_deg"]) < 3


def test_thumb_keys_point_into_the_open_sector(retention):
    """The open sector faces the thumb keys of the right half, with room on both sides."""
    pts = json.loads(LAYOUT_OUT.read_text())
    bx, by = pts["trackball"]["center"]["x"], pts["trackball"]["center"]["y"]
    reach = retention["19mm-pocket"]["above_rim_max_abs_az"]   # claws within +-reach of +x
    thumbs = [k for k in pts["keys"] if k["kind"] == "thumb"]
    assert thumbs
    for k in thumbs:
        az = abs(math.degrees(math.atan2(k["y"] - by, k["x"] - bx)))
        assert az - reach >= MIN_THUMB_TO_CLAW, (k["name"], az, reach)


def test_retainer_clears_the_cradle_outside_the_cup(retention):
    """Clearance to whatever of the cradle stands outside the cup wall above the board plane.

    Up to r2.3 that was only the three bearing bosses, which is why retention.json still calls the
    number boss_clearance (docs/gen/parts.py publishes it under that name). Since r2.4 the bosses
    top out below the ring's bottom edge and the thing the ring has to dodge is the tilted sensor
    sleeve, which stands beside the cup and is clipped flat at the rim plane: it fills the ring's
    annulus over about 113 degrees of azimuth, so the skirt is relieved there and the collar
    crosses the gap (hardware/trackball-cradle/params.scad, retainer_sleeve_clear).
    """
    for name, v in retention.items():
        assert v["boss_clearance"] is None or v["boss_clearance"] >= 0.5, name


# ------------------------------------------------------------------ fit in the case and the layout

def test_retainer_fits_pocket_lid_and_hinge(stack, retention):
    s = stack["19mm-pocket"]
    case = scad_values(CASE / "params.scad")
    data = scad_values(CASE / "data.scad")
    layout = yaml.safe_load((ROOT / "hardware" / "layout" / "k0d3ball35.yaml").read_text())
    r_out = s["retainer_outer_d"] / 2
    # inside the round pocket of the tray (and so inside the layout's cradle clearance circle,
    # which the keycap clearance check of the layout uses), with room for a finger to flex out
    assert r_out <= case["cradle_d"] / 2 - 0.5
    assert 2 * r_out <= layout["trackball"]["cradle_diameter"]
    assert r_out < s["notch_apothem"] - 0.3
    # under the lid roof with the lid closed
    roof_under = case["cap_top_z"] + case["lid_clear"]
    assert s["retainer_top_z"] <= roof_under - 0.5
    # The hinge strip under the roof (x = hinge_x_right +- hinge_strip_w, from the roof top down by
    # hinge_knuckle_d) must never meet the ring. Up to r2.3 the claws reached into that band and
    # had to dodge it sideways, which is what this used to assert; r2.4 dropped the ball by 3.15 mm
    # and the claw tops now end clear underneath the strip, so height alone settles it. Assert the
    # gap, and keep the sideways check for anything that does reach that high.
    strip_bottom = roof_under + case["lid_roof_t"] - case["hinge_knuckle_d"]
    strip_x = (data["hinge_x_right"] - case["hinge_strip_w"], data["hinge_x_right"] + case["hinge_strip_w"])
    ball_x = layout["halves"]["right"]["trackball"]["center"]["x"]
    trimesh = pytest.importorskip("trimesh")
    stl = CRADLE / "stl" / "retainer-19mm.stl"
    v = load_layout_frame(stl).vertices
    assert s["retainer_top_z"] <= strip_bottom - 0.5, (s["retainer_top_z"], strip_bottom)
    high = v[v[:, 2] > strip_bottom - 0.5]
    assert len(high) == 0 or (high[:, 0] + ball_x > strip_x[1] + 0.5).all()


def test_retainer_clears_ffc_corridor():
    trimesh = pytest.importorskip("trimesh")
    pts = json.loads(LAYOUT_OUT.read_text())
    tb = pts["trackball"]
    bx, by = tb["center"]["x"], tb["center"]["y"]
    corr = np.array(tb["pocket"]["cable_corridor"]) if "cable_corridor" in tb.get("pocket", {}) else np.array(tb["cable_corridor"])
    x0, x1 = corr[:, 0].min() - bx, corr[:, 0].max() - bx
    y0, y1 = corr[:, 1].min() - by, corr[:, 1].max() - by
    v = load_layout_frame(CRADLE / "stl" / "retainer-19mm.stl").vertices
    dx = np.maximum(0, np.maximum(x0 - v[:, 0], v[:, 0] - x1))
    dy = np.maximum(0, np.maximum(y0 - v[:, 1], v[:, 1] - y1))
    assert np.hypot(dx, dy).min() >= 1.0


# ------------------------------------------------------------------ snap

@pytest.mark.parametrize("name", list(VARIANTS))
def test_snap_is_gentle(stack, name):
    s = stack[name]
    assert 0.15 <= s["retainer_snap_undercut"] <= 0.4
    assert s["retainer_finger_strain"] <= 0.025      # PETG takes about 4 %; PLA about 2.5 %
    assert s["retainer_bottom_z"] > 0.5             # finger tips stay above the PCB top


def test_fingers_key_the_ring():
    """The ring only fits one way round, so the claws cannot end up on the thumb side.

    A rotation can only put the fingers back in their pockets if it maps the whole set of finger
    azimuths onto itself, and then the two different finger widths have to stop it: a wide finger
    has to land on a narrow pocket. Since r2.4 the fingers all live in the one arc that has both
    skirt and collar, so no rotation maps the set onto itself at all and the positions key the ring
    on their own - but the widths stay, both as the second key and because they tune the snap, and
    this still fails if someone makes the set symmetric with equal widths.
    """
    fingers = finger_table()
    widths = {}
    for az, w in fingers:
        widths[az % 360] = w
    for rot in range(1, 360):
        rotated = {(az + rot) % 360: w for az, w in widths.items()}
        if set(rotated) == set(widths):
            # same positions after this rotation: a wide finger must land on a narrow pocket
            assert any(rotated[a] > widths[a] for a in widths), rot


# ------------------------------------------------------------------ rendered geometry

@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
@pytest.mark.parametrize("name", list(VARIANTS))
def test_retainer_and_cradle_do_not_overlap(tmp_path, name):
    out = tmp_path / "clash.stl"
    res = render("clash", VARIANTS[name], out)
    # OpenSCAD exits non-zero when there is nothing to export, which is the result we want
    assert "ERROR" not in res.stderr.replace("Current top level object is empty", ""), res.stderr
    assert "Current top level object is empty" in res.stderr, "retainer and cradle overlap"
    assert not out.exists()


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_retainer_mesh(tmp_path, stack):
    trimesh = pytest.importorskip("trimesh")
    out = tmp_path / "retainer.stl"
    res = render("retainer", VARIANTS["19mm-pocket"], out)
    assert res.returncode == 0 and "WARNING" not in res.stderr, res.stderr
    mesh = load_layout_frame(out)
    assert mesh.is_watertight
    assert 50 < mesh.volume < 1000
    s = stack["19mm-pocket"]
    v = mesh.vertices
    assert abs(v[:, 2].max() - s["retainer_top_z"]) < 0.05
    assert abs(v[:, 2].min() - s["retainer_bottom_z"]) < 0.05
    # flat bottom: the skirt and finger tips are the first layer, nothing hangs below them
    assert abs(v[:, 2].min() - s["retainer_bottom_z"]) < 1e-3
    # nothing above the cup rim on the thumb side (x < 0 half, within the open sector)
    above = v[v[:, 2] > s["rim_z"] + 0.01]
    az = np.degrees(np.arctan2(above[:, 1], above[:, 0]))
    assert np.abs(az).max() <= 180 - MIN_OPEN_SECTOR / 2
    # the committed STL is this one
    committed = load_layout_frame(CRADLE / "stl" / "retainer-19mm.stl")
    assert abs(committed.volume - mesh.volume) < 0.01


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_cradle_carries_seat_and_pockets(stack):
    """The cradle STL has the rim chamfer and the four finger pockets, and still nothing above the rim."""
    trimesh = pytest.importorskip("trimesh")
    s = stack["19mm-pocket"]
    mesh = load_layout_frame(CRADLE / "stl" / "cradle-19mm-pocket.stl")
    v = mesh.vertices
    assert v[:, 2].max() <= s["rim_z"] + 1e-3
    r = np.hypot(v[:, 0], v[:, 1])
    r_out = s["cup_outer_d"] / 2
    # Chamfer: the rim's outer edge is 0.8 mm in, so no vertex at full radius on the rim plane.
    # Only the cup's own rim counts - since r2.4 the tilted sensor sleeve stands beside the cup and
    # is clipped flat at the rim plane as well, so its top face and the corners the PCB notch cuts
    # out of it also lie at rim_z, but out at r 12.5 to 15.9.
    on_rim = (np.abs(v[:, 2] - s["rim_z"]) < 1e-3) & (r < r_out + 0.5)
    assert on_rim.any()
    assert r[on_rim].max() < r_out - 0.7
    # pockets: vertices inside the cup wall radius at the nub height, at every finger azimuth
    band = (v[:, 2] > s["retainer_bottom_z"]) & (v[:, 2] < s["retainer_bottom_z"] + 2.5) & (r < r_out - 0.2) & (r > r_out - 0.6)
    az = np.degrees(np.arctan2(v[band, 1], v[band, 0])) % 360
    for target, _w in finger_table():
        assert (np.abs((az - target + 180) % 360 - 180) < 10).any(), target


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_retention_json_is_current(retention):
    """Re-run the 19 mm analysis: the committed retention.json must match the model."""
    pytest.importorskip("trimesh")
    import sys
    sys.path.insert(0, str(CRADLE))
    import retention as rt
    build = CRADLE / "build"
    fresh = rt.analyse(openscad(), "19mm-pocket", VARIANTS["19mm-pocket"], build)
    old = retention["19mm-pocket"]
    for key in ("trapped", "without_retainer_trapped"):
        assert fresh[key] == old[key], key
    for key in ("critical_margin", "guaranteed_margin", "ball_lift_play", "rest_gap", "open_sector_deg",
                "retainer_top_z", "retainer_outer_r"):
        assert abs(fresh[key] - old[key]) < 0.02, (key, fresh[key], old[key])
