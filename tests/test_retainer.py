# SPDX-License-Identifier: MIT
"""Checks for the optional retainer clip on the pocket cover (hardware/case, part = "pocket_clip").

The clip is a flat C-ring on the cover round its hole, open towards the thumb, with two claws over
the ball's shoulders and two split snap pins in two holes of the cover (issues/mech-ball-retainer-clip.md).
Until the cover became a bezel round the ball it was a ring snapped onto the cup rim, and the cover
needed a 26.5 mm hole for it. What it has to do:

* keep the ball in when the half is turned over, with room for print error
  (hardware/case/retention.py: configuration-space flood fill, committed as retention.json),
* never touch the ball in use, and not drag it along when it is pulled off,
* leave the thumb side open,
* fit: no overlap with cover, tray or cradle, pins clear of the cup and of the FFC corridor,
  under the closed lid,
* come off by hand: a small snap undercut on prongs that do not overstrain.
"""
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "hardware" / "case"
CRADLE = ROOT / "hardware" / "trackball-cradle"
LAYOUT_OUT = ROOT / "hardware" / "layout" / "output" / "points-right.json"

MIN_GUARANTEED_MARGIN = 0.5   # mm of combined looseness (print error, small ball, claw flex) the trap survives
MIN_REST_GAP = 0.35           # design gap 0.4 (clip_ball_gap) less facetting
MIN_OPEN_SECTOR = 150         # degrees free of the clip, centred on the thumb side
MIN_THUMB_TO_CLAW = 60        # degrees between a thumb key's direction and the clip's furthest reach
MAX_PRONG_STRAIN = 0.025      # PLA takes about 2.5 %, PETG about 4 %


def openscad():
    for cand in [shutil.which("openscad"), "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"]:
        if cand and Path(cand).exists():
            return cand
    return None


def _param(name: str) -> float:
    m = re.search(rf"^{name}\s*=\s*([-\d.]+)", (CASE / "params.scad").read_text(), re.M)
    assert m, f"{name} missing from hardware/case/params.scad"
    return float(m.group(1))


@pytest.fixture(scope="module")
def stack():
    return json.loads((CASE / "stack.json").read_text())["variants"]["right"]


@pytest.fixture(scope="module")
def retention():
    return json.loads((CASE / "retention.json").read_text())["variants"]["19mm-pocket"]


def test_ball_is_trapped_with_margin(retention):
    # negative control: the same analysis lets the ball out of the open cup
    assert retention["without_clip_trapped"] is False
    assert retention["trapped"] is True
    assert retention["guaranteed_margin"] >= MIN_GUARANTEED_MARGIN, retention["guaranteed_margin"]
    assert retention["guaranteed_margin"] < retention["critical_margin"]


def test_claws_stay_off_the_ball(retention):
    assert retention["rest_gap"] >= MIN_REST_GAP
    # pulling the clip straight up never brings a claw closer than it is at rest
    assert retention["pull_off_min_gap"] >= retention["rest_gap"] - 0.01
    # the ball can rattle a little but not lift far (the sensor loses it above 2.6 mm anyway)
    assert 0.3 <= retention["ball_lift_play"] <= 1.2


def test_thumb_side_is_open(retention, stack):
    assert retention["open_sector_deg"] >= MIN_OPEN_SECTOR
    assert abs(retention["clip_max_abs_az"] - stack["clip_open_az"]) < 2


def test_thumb_keys_point_into_the_open_sector(retention):
    pts = json.loads(LAYOUT_OUT.read_text())
    bx, by = pts["trackball"]["center"]["x"], pts["trackball"]["center"]["y"]
    reach = retention["clip_max_abs_az"]
    thumbs = [k for k in pts["keys"] if k["kind"] == "thumb"]
    assert thumbs
    for k in thumbs:
        az = abs(math.degrees(math.atan2(k["y"] - by, k["x"] - bx)))
        assert az - reach >= MIN_THUMB_TO_CLAW, (k["name"], az, reach)


def test_pins_clear_the_cradle_and_the_ffc(retention, stack):
    assert retention["pin_cradle_clearance"] is not None
    assert retention["pin_cradle_clearance"] >= 0.3, retention["pin_cradle_clearance"]
    # the FFC climbs from the module to J1 over the board edge in the cable corridor
    pts = json.loads(LAYOUT_OUT.read_text())
    bx, by = pts["trackball"]["center"]["x"], pts["trackball"]["center"]["y"]
    corr = pts["trackball"]["pocket"].get("cable_corridor") or pts["trackball"]["cable_corridor"]
    xs, ys = [p[0] for p in corr], [p[1] for p in corr]
    for s in (-1, 1):
        a = math.radians(s * stack["clip_pin_az"])
        px, py = bx + stack["clip_pin_r"] * math.cos(a), by + stack["clip_pin_r"] * math.sin(a)
        dx = max(min(xs) - px, 0, px - max(xs))
        dy = max(min(ys) - py, 0, py - max(ys))
        assert math.hypot(dx, dy) > 3.0, (px, py)


def test_clip_fits_under_the_lid(retention, stack):
    assert retention["clip_top_z"] < stack["lid_roof_under_z"] - 3.0
    assert abs(retention["clip_bottom_z"] - stack["clip_barb_bottom_z"]) < 0.06
    # the claws keep 0.5 mm under the hinge strip's x band (hinge_x is far on the thumb side)
    data = (CASE / "data.scad").read_text()
    hx = float(re.search(r"^hinge_x_right = (.*);", data, re.M).group(1))
    bx = json.loads(LAYOUT_OUT.read_text())["trackball"]["center"]["x"]
    assert bx - retention["clip_outer_r"] * math.cos(math.radians(180 - stack["clip_open_az"])) > hx + _param("hinge_strip_w") + 0.5


def test_snap_is_gentle():
    """Each prong bends like a cantilever from the slit's top (0.4 under the ring top) down to the
    middle of the barb: strain 1.5 t y / L^2, with y the undercut against the hole."""
    t = (_param("clip_pin_d") - _param("clip_pin_slit")) / 2
    undercut = _param("clip_pin_barb") - (_param("cover_pin_hole_d") - _param("clip_pin_d")) / 2
    assert 0.1 <= undercut <= 0.25
    rim, cover_t, ring_t = _param("rim_z"), _param("cover_t"), _param("clip_ring_t")
    barb_mid = rim - cover_t - 0.05 - _param("clip_pin_barb")
    length = (rim + ring_t - 0.4) - barb_mid
    strain = 1.5 * t * undercut / length ** 2
    assert strain <= MAX_PRONG_STRAIN, f"prong strain {strain:.3%}"


def _render(part, out):
    res = subprocess.run([openscad(), "--backend", "manifold", "-D", f'part="{part}"', "-D", 'half="right"',
                          "-o", str(out), str(CASE / "case.scad")], capture_output=True, text=True, timeout=600)
    return res.stdout + res.stderr


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_clip_overlaps_nothing(tmp_path):
    """Clip against cover, tray and cradle: at most the faces where the ring lies on the cover."""
    trimesh = pytest.importorskip("trimesh")
    out = tmp_path / "clash.stl"
    log = _render("clip_clash", out)
    if "Current top level object is empty" in log or not out.exists() or out.stat().st_size < 200:
        return
    m = trimesh.load(out, force="mesh")
    assert abs(m.volume) < 0.01, f"clip overlaps by {m.volume:.3f} mm3 at {m.bounds.tolist()}"


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_clip_mesh(stack):
    trimesh = pytest.importorskip("trimesh")
    m = trimesh.load(CASE / "stl" / "pocket-clip-right.stl", force="mesh")
    assert m.is_watertight
    assert m.bounds[1][2] == pytest.approx(stack["clip_top_z"], abs=0.02)
    # ball-centred like the cradle STL: the ring's bore is on the z axis
    assert max(m.bounds[1][0], m.bounds[1][1]) == pytest.approx(stack["clip_ro"], abs=0.05)


def test_cradle_has_no_retainer_left():
    params = (CRADLE / "params.scad").read_text()
    scad = (CRADLE / "cradle.scad").read_text()
    assert not re.search(r"^retainer_", params, re.M)
    assert "module retainer" not in scad and "nub_profile" not in scad
    assert not (CRADLE / "stl" / "retainer-19mm.stl").exists()


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_retention_json_is_current(retention):
    """Re-run the analysis: the committed retention.json must match the model."""
    pytest.importorskip("trimesh")
    import sys
    sys.path.insert(0, str(CASE))
    import retention as rt
    fresh = rt.analyse(openscad(), "19mm-pocket", {"ball_d": 19.05}, CASE / "build")
    for key in ("trapped", "without_clip_trapped"):
        assert fresh[key] == retention[key], key
    for key in ("critical_margin", "guaranteed_margin", "ball_lift_play", "rest_gap", "open_sector_deg",
                "clip_top_z", "clip_outer_r"):
        assert abs(fresh[key] - retention[key]) < 0.02, (key, fresh[key], retention[key])
