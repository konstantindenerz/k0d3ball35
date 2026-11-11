# SPDX-License-Identifier: MIT
"""Checks for the parametric trackball cradle (hardware/trackball-cradle).

The cradle stands in a case pocket beside the right PCB with the 19.05 mm ball (the only size since
r2.4) and holds a bought PAW3222 module tilted 65 degrees in a sleeve beside the cup. The cup has
nothing above its rim: the rim stays ``rim_drop`` below the equator. Keeping the ball in when the
half is turned over is the job of the optional clip on the case's pocket cover (checked by
``retention.py``) or of the case lid. Two M2 case screws come up through the case floor into the
cup skirt; there are no screw ears. The OpenSCAD dependent tests are skipped when no OpenSCAD binary is available.
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
from scad_frame import load_layout_frame, layout_y

ROOT = Path(__file__).resolve().parents[1]
CRADLE = ROOT / "hardware" / "trackball-cradle"
SCAD = CRADLE / "cradle.scad"
LAYOUT = ROOT / "hardware" / "layout" / "k0d3ball35.yaml"

# The optical window is a datasheet property and stays a literal here. The lens height and the
# module thickness are NOT: since r2.4 they describe a bought PAW3222 module whose assembly
# drawing PixArt does not publish, so they are nominal values in params.scad that get corrected
# against the real part. Reading them from params.scad keeps this file from pinning a guess.
LENS_Z_MIN, LENS_Z_MAX = 2.2, 2.6


def _param(name: str) -> float:
    m = re.search(rf"^{name}\s*=\s*([-\d.]+)", (CRADLE / "params.scad").read_text(), re.M)
    assert m, f"{name} missing from params.scad"
    return float(m.group(1))


LENS_H = _param("lens_h")
SENSOR_PCB_T = _param("sensor_pcb_t")
PCB_T = 1.6
RIM_DROP = 1.0   # params.scad rim_drop: cup rim this far below the ball equator
HOUSING_X, HOUSING_Y = _param("sensor_pcb_w") + 3.0, _param("sensor_pcb_l") + 4.0
CASE_SCREW_SP = 20.0                # case_screw_sp: the screws go up into the cup skirt
EAR_RE = re.compile(r"\bears?\b", re.I)


def openscad():
    for cand in (shutil.which("openscad"), "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"):
        if cand and Path(cand).exists():
            return cand
    return None


def run_scad(overrides, out):
    cmd = [openscad(), "--backend", "manifold", "-D", 'part="cradle"']
    for k, v in overrides.items():
        cmd += ["-D", f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"]
    cmd += ["-o", str(out), str(SCAD)]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    assert res.returncode == 0, res.stderr
    values = {m.group(1): float(m.group(2)) for m in re.finditer(r'STACK (\w+)=(-?[\d.]+)', res.stderr + res.stdout)}
    return values, res.stderr


@pytest.fixture(scope="module")
def stack():
    return json.loads((CRADLE / "stack.json").read_text())["variants"]


@pytest.fixture(scope="module")
def trackball_cfg():
    return yaml.safe_load(LAYOUT.read_text())["trackball"]


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_module_can_be_inserted(tmp_path):
    """The bought module must be able to get INTO its sleeve: along its own axis from the back,
    until the board rests on the shoulder round the lens cavity. r2.4 first shipped a sleeve
    closed on every side, which no clearance check notices because the seated module touches
    nothing. Swept 40 mm back from the seat, the board must not meet the cradle anywhere."""
    out = tmp_path / "insert.stl"
    res = subprocess.run([openscad(), "--backend", "manifold", "-D", 'part="insert_path"',
                          "-o", str(out), str(SCAD)], capture_output=True, text=True, timeout=600)
    assert "Current top level object is empty" in res.stderr, "the module's way into the sleeve is blocked"


def test_sources_present():
    assert SCAD.exists()
    params = (CRADLE / "params.scad").read_text()
    assert (CRADLE / "README.md").exists()
    assert "lens_z" in params
    assert re.search(r"^ball_d\s*=\s*19\.05", params, re.M), "19.05 mm ball must be the default"
    assert re.search(r"^rim_drop\s*=\s*1\.0", params, re.M)
    # the retainer clip lives on the case's pocket cover since the cover became a bezel
    # (tests/test_retainer.py); the old peg-in-hole ring (removed 2026-11-06) does not come back
    scad = SCAD.read_text()
    for name in ("peg_d", "peg_h", "retainer_claws", "retainer_claw_az", "retainer_fingers"):
        assert not re.search(rf"^{name}\s*=", params, re.M), name
    assert "peg" not in scad.lower()
    assert "module retainer" not in scad


def test_no_screw_ears():
    """The case screws go through the sensor posts; the housing has no ears and no ear parameters."""
    params = (CRADLE / "params.scad").read_text()
    scad = SCAD.read_text()
    for name in ("ear_r", "ear_x", "ear_w"):
        assert not re.search(rf"^{name}\s*=", params, re.M), name
        assert name not in scad, name
    assert re.search(r"^case_screw_d\s*=\s*2\.0", params, re.M)
    assert re.search(r"^case_screw_sp\s*=\s*20", params, re.M)
    # r2.4: one mount, one ball size, and the sensor tilted beside the ball
    assert not re.search(r"^mount\s*=", params, re.M), "the r1 cutout mount is gone"
    assert re.search(r"^sensor_angle\s*=\s*65", params, re.M), "the solved tilt"
    assert re.search(r"^sensor_az\s*=\s*180", params, re.M), "module leans to +x, under the middle column"
    readme = (CRADLE / "README.md").read_text()
    for text, name in ((params, "params.scad"), (scad, "cradle.scad"), (readme, "README.md")):
        assert not EAR_RE.search(text), name
    assert "43 x 29" not in readme and "36 mm apart" not in readme
    assert "M2 x 8" in readme


def test_stack_json_values(stack):
    assert set(stack) == {"19mm-pocket"}, "19.05 mm is the only supported ball since r2.4"
    for name, v in stack.items():
        assert LENS_Z_MIN <= v["lens_reference_plane_dist"] <= LENS_Z_MAX, name
        # sensor PCB plane = ball radius + lens distance + lens height
        assert abs(v["sensor_pcb_plane_dist"] - (v["ball_d"] / 2 + v["lens_reference_plane_dist"] + LENS_H)) < 1e-6, name
        # nothing below the agreed envelope (case floor 10 mm under the PCB underside)
        assert min(v["lowest_plastic_z"], v["lowest_sensor_board_z"]) >= -(PCB_T + v["depth_below_pcb_bottom"]) - 1e-6, name
        # open cup: the rim stays rim_drop below the equator so the ball lifts out freely
        assert abs(v["rim_below_equator"] - RIM_DROP) < 1e-6, name
        assert abs((v["ball_centre_z"] - v["rim_z"]) - RIM_DROP) < 1e-6, name
        assert v["rim_z"] < v["ball_centre_z"] < v["ball_top_above_pcb_top"], name
        # the module stands on the case floor and keeps clear of the PCB underside
        assert abs(v["lowest_plastic_z"] - v["floor_z"]) < 1e-6, name
        assert v["housing_top_z"] <= v["rim_z"] + 1e-6, name
        # everything above the PCB fits into the notch with clearance
        assert v["envelope_d_above_pcb"] / 2 < v["notch_apothem"] - 0.3, name
        # The sleeve is the module plus walls. Since r2.4 the case screws no longer go through
        # sensor posts - they go straight up into the cup skirt - so the floor footprint is the
        # cup plus the clipped sleeve and is NOT the sleeve rectangle any more.
        assert v["housing_x"] == HOUSING_X and v["housing_y"] == HOUSING_Y, name
        assert v["case_screw_sp"] == CASE_SCREW_SP, name
        assert v["case_screw_sp"] / 2 > v["cup_outer_d"] / 2 - 2.0, name   # screws bite the skirt


def test_default_variant_matches_layout(stack, trackball_cfg):
    """The 19 mm pocket cradle is what the layout's clearance check and PCB notch assume."""
    v = stack["19mm-pocket"]
    assert v["ball_d"] == trackball_cfg["ball_diameter"]
    assert v["envelope_d_above_pcb"] <= trackball_cfg["cradle_diameter"]
    assert v["notch_apothem"] == trackball_cfg["cradle_diameter"] / 2 + trackball_cfg["pocket"]["notch_clearance"]
    # Since r2.4 the ball height is NOT a literal: the cup floor sets it (see
    # test_the_cup_floor_sets_the_ball_height_not_the_module), so derive it rather than pin it.
    # The window below is a sanity check, not the specification.
    assert abs(v["ball_centre_z"] - (v["floor_z"] + v["drop_cup"])) < 1e-6
    assert abs(v["ball_top_above_pcb_top"] - (v["ball_centre_z"] + v["ball_d"] / 2)) < 1e-6
    assert 12.0 < v["ball_top_above_pcb_top"] < 15.0, "ball height left its design window"
    assert v["lowest_sensor_board_z"] >= v["floor_z"] - 1e-6


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_render_19mm_pocket_stl(tmp_path):
    out = tmp_path / "cradle.stl"
    values, log = run_scad({"ball_d": 19.05, "mount": "pocket"}, out)
    assert "WARNING" not in log and "ERROR" not in log
    assert out.stat().st_size > 100_000
    assert LENS_Z_MIN <= values["lens_reference_plane_dist"] <= LENS_Z_MAX
    trimesh = pytest.importorskip("trimesh")
    mesh = load_layout_frame(out)
    assert mesh.is_watertight
    assert mesh.volume > 1000
    v = mesh.vertices
    # stands on the case floor, never reaches into the PCB slab beside the notch
    assert abs(v[:, 2].min() - values["floor_z"]) < 0.05
    above = v[v[:, 2] > -PCB_T - 0.3 + 0.05]
    # The PCB notch is an OCTAGON, so the bound is its apothem measured on each of the eight face
    # normals - not a circle. A circular bound happens to be right only while the part stays
    # inside the inscribed circle, which it did until the tilted sleeve in r2.4 reached the
    # corners; it then rejects legal geometry at up to apothem / cos(22.5 deg).
    apothem = values["notch_apothem"] - 0.3
    normals = [math.radians(45 * k) for k in range(8)]
    reach = max(float(np.max(above[:, 0] * math.cos(a) + above[:, 1] * math.sin(a)))
                for a in normals)
    assert reach <= apothem + 1e-3, f"{reach:.3f} mm past the notch apothem {apothem:.3f}"
    # nothing printed above the rim (no claws), rim 1 mm below the ball centre
    assert v[:, 2].max() <= values["rim_z"] + 1e-3
    assert abs(values["ball_centre_z"] - values["rim_z"] - RIM_DROP) < 1e-6
    # Footprint on the floor: the cup skirt plus the tilted sleeve where it is clipped off, and
    # nothing else (no ears, no screw posts since r2.4). The sleeve leans along sensor_az, so the
    # footprint is deliberately NOT symmetric about the ball axis.
    on_floor = v[v[:, 2] < values["floor_z"] + 0.5]
    cup_r = values["cup_outer_d"] / 2
    # measured in the lean frame (along / across window_az), so the checks hold for any azimuth
    # and catch a sleeve that points somewhere else than the window
    along, across = _lean_frame(on_floor[:, 0], on_floor[:, 1], values["window_az"])
    assert abs(-along.min() - cup_r) < 0.6, "the cup skirt sets the edge away from the sleeve"
    lean = along.max()
    assert lean > cup_r + 1.0, "the sleeve does not reach past the cup skirt towards the window"
    assert lean <= values["board_reach"] + 2.0 + 1e-3, "the sleeve reaches further than the module"
    # The old bound was the sleeve rectangle. Since r2.4 the cup skirt is the widest thing on the
    # floor across the lean, and the sleeve only sticks out along it.
    assert abs(across).max() <= cup_r + 0.05
    # footprint_x / footprint_y are the body's plan (across / along the lean), the same at every
    # height (the slot only opens the floor under the module); the site publishes them
    along_all, _ = _lean_frame(v[:, 0], v[:, 1], values["window_az"])
    assert abs(values["footprint_x"] - 2 * cup_r) < 1e-6
    assert abs(values["footprint_y"] - (cup_r + along_all.max())) < 0.05
    # The case screws changed in r2.4: with the module beside the ball the floor under the ball is
    # solid plastic, so the two M2 x 8 go straight up into the cup skirt instead of through
    # sensor posts. Check the 1.6 mm pilot is there, well above the floor so a short bore fails.
    for sy in (-1, 1):
        axis_y = sy * CASE_SCREW_SP / 2     # on the y axis, clear of the +x sleeve
        r = np.hypot(v[:, 0], v[:, 1] - axis_y)
        pilot = v[(np.abs(r - 0.8) < 0.05) & (v[:, 2] >= values["floor_z"] - 1e-6)]
        assert len(pilot) > 0, f"no 1.6 mm screw pilot at y = {axis_y}"
        thread = pilot[:, 2].max() - values["floor_z"]
        assert thread >= 4.0, f"only {thread:.2f} mm of thread in the skirt at y = {axis_y}"


def _lean_frame(x, y, az_deg):
    """(along, across) the sensor lean: along points at the window azimuth (layout frame)."""
    a = math.radians(az_deg)
    return x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a)


def _dxf_loops(path):
    ezdxf = pytest.importorskip("ezdxf")
    doc = ezdxf.readfile(str(path))
    loops = []
    for e in doc.modelspace():
        if e.dxftype() == "LWPOLYLINE":
            loops.append([(p[0], layout_y(p[1])) for p in e.get_points()])
        elif e.dxftype() == "CIRCLE":
            c, r = e.dxf.center, e.dxf.radius
            cy = layout_y(c.y)
            loops.append([(c.x + r, cy), (c.x - r, cy), (c.x, cy + r), (c.x, cy - r)])
    return loops


def test_floor_dxf_is_housing_with_two_screw_holes():
    """dxf/floor-19mm-pocket.dxf: the module's footprint on the case floor, plus the two screws.

    Until r2.4 this was a plain 30 x 30 square because the module was a box under the ball. It is
    now the cup skirt unioned with the TILTED sleeve where the floor clips it, so it is wider than
    the cup on one side only (the window side) and symmetric about the lean axis. Getting this wrong makes the case cut a pocket
    well of the wrong size, which is how an oversized well slipped through once in r2.4: a formula
    placed the unclipped sleeve 21.4 mm from the axis instead of the real 14.3.
    """
    loops = _dxf_loops(CRADLE / "dxf" / "floor-19mm-pocket.dxf")
    assert len(loops) == 3, len(loops)
    loops.sort(key=lambda pts: (max(p[0] for p in pts) - min(p[0] for p in pts))
               * (max(p[1] for p in pts) - min(p[1] for p in pts)), reverse=True)
    outer, *holes = (np.array(pts) for pts in loops)
    stack = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    cup_r = stack["cup_outer_d"] / 2
    az = stack["window_az"]
    # The module leans towards layout +x (window_az 0), under the middle column where the PCB
    # already ends; until r2.4b it leaned towards +y and made the case 5 mm deeper.
    assert az == 0
    along, across = _lean_frame(outer[:, 0], outer[:, 1], az)
    # across the lean the cup sets the width, and it is centred on the ball axis
    assert abs(across.max() - across.min() - 2 * (cup_r + 0.5)) < 0.05
    assert abs(across.max() + across.min()) < 0.05, "the footprint is symmetric about the lean axis"
    # along the lean it is not: the sleeve adds to the window side, the cup bounds the other
    lean, back = along.max(), -along.min()
    assert abs(back - (cup_r + 0.5)) < 0.05, "the cup bounds the side away from the sleeve"
    assert cup_r + 1.0 < lean <= stack["board_reach"] + 2.0, f"sleeve reach {lean:.2f} mm"
    # and the DXF agrees with the STL: both files are in the print frame, so the floor section of
    # the printed part must lean the same way as its footprint. A doubled mirror in floor2d()
    # once flipped only the DXF, and the line above, written against that DXF, agreed with it.
    mesh = load_layout_frame(CRADLE / "stl" / "cradle-19mm-pocket.stl")
    v = mesh.vertices
    foot = v[v[:, 2] < v[:, 2].min() + 0.5]
    f_along, _ = _lean_frame(foot[:, 0], foot[:, 1], az)
    assert f_along.max() > -f_along.min() + 1.0, "STL leans the other way than the DXF"
    assert abs(f_along.max() + 0.5 - lean) < 0.6, (f_along.max(), lean)
    # case screws on the axis ACROSS the lean, clear of the sleeve
    centres = sorted(_lean_frame(h[:, 0].mean(), h[:, 1].mean(), az)[1] for h in holes)
    for h in holes:
        a, _ = _lean_frame(h[:, 0].mean(), h[:, 1].mean(), az)
        assert abs(a) < 0.05, "case screws sit on the axis across the lean, through the ball"
        assert abs(h[:, 0].max() - h[:, 0].min() - 2.2) < 0.1, "M2 clearance hole"
    assert abs(centres[0] + CASE_SCREW_SP / 2) < 0.05
    assert abs(centres[1] - CASE_SCREW_SP / 2) < 0.05


# --------------------------------------------------------------------- r2.4: the tilted module
# Four checks that did not exist before r2.4 and that each caught a real mistake while it was
# being designed. A vertical sensor under the ball cannot break any of them, which is why they
# were never needed - and why their absence was not obvious.


def test_tilt_is_the_solved_angle(stack):
    """65 degrees is a solved value, not a preference: see the window check below."""
    assert stack["19mm-pocket"]["sensor_angle"] == 65.0


def test_tilted_module_stays_under_the_cup_rim(stack):
    """The upper edge of the module and of its sleeve must stay below the cup rim.

    THIS is what limits the tilt, and only the downward swing (drop_board) used to be checked.
    Tilted, one edge of the board swings down and the other swings UP. At 65 degrees a 13 mm wide
    board - the narrowest a PMW3610 can be, because its moulded package needs a 16.96 x 8.60 mm
    cutout through the board - puts its upper edge 2.2 mm ABOVE the rim, where it would stand in
    the open beside the ball at thumb height. The 8 mm PAW3222 module clears it. Believing
    otherwise is what made an early r2.4 review sheet quote a ball height that cannot be built.
    """
    v = stack["19mm-pocket"]
    assert v["board_top_z"] <= v["rim_z"], "the module's upper edge rises above the cup rim"
    assert v["sleeve_top_z"] <= v["rim_z"], "the sleeve's upper edge rises above the cup rim"


def test_tilted_module_stays_inside_the_pcb_notch(stack):
    """Where the module passes the main PCB plane it has to fit the notch."""
    v = stack["19mm-pocket"]
    # Use the SLAB reach, not the absolute far corner. The module's far corner (module_reach) sits
    # above the PCB top, where there is no board to foul; what has to fit the notch is how far it
    # gets while it is inside the 1.6 mm slab. Checking the wrong one of the three rejects legal
    # geometry by 0.7 mm.
    assert v["module_slab_reach"] <= v["notch_apothem"], (
        f"the module reaches {v['module_slab_reach']:.3f} mm inside the PCB slab, notch apothem "
        f"is {v['notch_apothem']:.3f}")
    assert v["board_reach"] <= v["module_reach"] + 1e-6


def test_the_cup_floor_sets_the_ball_height_not_the_module(stack):
    """Why the unmeasured lens numbers do not endanger the ball height.

    PixArt publishes no assembly drawing for the PAW3222 + PNSR-015-RB3 pair, so lens_z, lens_h
    and the module thickness in params.scad are nominal and feed drop_board. As long as drop_cup
    is the largest of the three terms, the ball height comes from the cup floor - geometry we
    dimension ourselves - and a measured correction (lens_shim) slides the module along its axis
    without moving the ball.

    If this fails, the measured stack has taken over and the ball height became a function of a
    number nobody measured. Re-solve the angle or the sleeve wall; do NOT relax this assert.
    """
    v = stack["19mm-pocket"]
    cup, board, sleeve = v["drop_cup"], v["drop_board"], v["drop_housing"]
    assert cup >= board, f"the module ({board:.3f}) sets the ball height, not the cup ({cup:.3f})"
    assert cup >= sleeve, f"the sleeve ({sleeve:.3f}) sets the ball height, not the cup ({cup:.3f})"


def test_sensor_window_clears_the_rim_and_every_bearing():
    """The optical path through the cup wall must miss the cup rim and all three bearing bosses.

    The window sits (90 - sensor_angle) degrees below the equator and is as wide as the lens body.
    Its upper edge has to stay below the rim line, and in azimuth it has to clear every bearing
    boss - which is the reason bearing_az leaves 60 degrees either side of the window. Without this check the
    rotation looks like an arbitrary edit and the next person undoes it.
    """
    tilt = _param("sensor_angle")
    # NOT _param("sensor_az"): the window sits at sensor_az + 180 (see STACK window_az). Reading the
    # parameter directly is exactly how a bearing seat ended up inside the window in r2.4 while
    # this test stayed green.
    az = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]["window_az"]
    ball_d, gap = _param("ball_d"), _param("ball_gap")
    # the hole through the CUP WALL is sized on the aperture, not on the lens body: the lens sits
    # in its own cavity on the far side of the wall and never passes through it
    optical = _param("optical_d")
    r_in = ball_d / 2 + gap

    half = math.degrees(math.asin((optical / 2) / r_in))       # angular half-width of the window
    below = 90.0 - tilt                                        # window centre below the equator
    rim = math.degrees(math.asin(_param("rim_drop") / (ball_d / 2)))
    assert below - half >= rim - 1e-6, (
        f"the window's upper edge is {below - half:.1f} deg below the equator but the rim is at "
        f"{rim:.1f} deg: it would cut through the cup rim")

    params = (CRADLE / "params.scad").read_text()
    m = re.search(r"^bearing_az\s*=\s*\[([^\]]+)\]", params, re.M)
    assert m, "bearing_az missing from params.scad"
    seat_r = (_param("bearing_d") - 2 * _param("bearing_fit") + 3.2) / 2      # boss_r in cradle.scad
    boss_half = math.degrees(math.asin(seat_r / (ball_d / 2 + _param("bearing_d") / 2)))
    elev = _param("bearing_elev")
    for az_text in m.group(1).split(","):
        bearing = float(az_text)
        if abs(elev - below) >= half + boss_half:
            continue                     # the boss sits outside the window's elevation band
        d = abs((bearing - az + 180) % 360 - 180)
        assert d > half + boss_half, (
            f"bearing boss at azimuth {bearing:g} is {d:.1f} deg from the sensor window, needs "
            f"more than {half + boss_half:.1f} deg")


def test_layout_pocket_offsets_follow_the_real_tilt(stack, trackball_cfg):
    """The layout's pocket boxes must lean the same way as the cradle actually does.

    hardware/layout/k0d3ball35.yaml carries housing_offset and sensor_board_offset so the pocket
    well and the insertion corridor follow the tilted module. They are hand-copied facts, like
    cup_envelope, and nothing compared them with the cradle until r2.4 - when the layout check
    passed green while the box and the module leaned in OPPOSITE directions.
    """
    v = stack["19mm-pocket"]
    pk = trackball_cfg["pocket"]
    az = v["window_az"]
    for key in ("housing_offset", "sensor_board_offset"):
        off = pk.get(key)
        assert off is not None, f"{key} missing from the layout"
        along, across = _lean_frame(off["x"], off["y"], az)
        assert abs(across) < 1e-9, f"{key} must not lean across the tilt"
        assert along > 0, f"{key} leans the wrong way for window_az = {az}"
    # the corridor has to cover where the module really is: sensor_board is (x, y) in the layout,
    # its extent along the lean is the projection, across it the 14 mm module length
    a = math.radians(az)
    sb_along = abs(pk["sensor_board"]["x"] * math.cos(a)) + abs(pk["sensor_board"]["y"] * math.sin(a))
    sb_across = abs(pk["sensor_board"]["x"] * math.sin(a)) + abs(pk["sensor_board"]["y"] * math.cos(a))
    off_along, _ = _lean_frame(pk["sensor_board_offset"]["x"], pk["sensor_board_offset"]["y"], az)
    far = off_along + sb_along / 2
    near = off_along - sb_along / 2
    assert abs(far - v["module_reach"]) <= 0.5, f"corridor ends at {far:.2f}, module at {v['module_reach']:.2f}"
    assert near > 0, "the corridor must start off the ball axis, on the side the module leans to"
    assert near <= v["board_reach"], f"corridor starts at {near:.2f}, past the module's near face"
    assert sb_across >= _param("sensor_pcb_l"), "the corridor is narrower than the module"


def _seg_line_dist(p0, p1, q, steps=400):
    """Smallest distance between the segment p0-p1 and the vertical line through q (x, y, ztop),
    counting only the line below ztop."""
    best = 1e9
    for t in np.linspace(0.0, 1.0, steps):
        p = p0 + t * (p1 - p0)
        d = math.hypot(p[0] - q[0], p[1] - q[1]) if p[2] <= q[2] else math.dist(p, (q[0], q[1], q[2]))
        best = min(best, d)
    return best


def test_case_screws_miss_the_bearing_seats():
    """The M2 case screws run up into the cup skirt; until this check the screw at layout y -10
    ran straight through the 270 degree bearing seat, and driving it would have pushed the
    ceramic ball out. Every pilot keeps 0.5 mm of plastic to every seat."""
    stack = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    params = (CRADLE / "params.scad").read_text()
    scad = SCAD.read_text()
    az = json.loads(re.search(r"^bearing_az\s*=\s*(\[[^\]]*\])", params, re.M).group(1))
    elev = math.radians(_param("bearing_elev"))
    r_in = _param("ball_d") / 2 + _param("ball_gap")
    seat_d = _param("bearing_d") - 2 * _param("bearing_fit")
    seat_depth = _param("bearing_d") - _param("ball_gap")
    pilot_d = _param("screw_pocket_d")
    zc = stack["ball_centre_z"]
    floor_z, rim_z = stack["floor_z"], stack["rim_z"]
    screw_top = floor_z + min(_param("case_screw_len") - 2.0, rim_z - floor_z - 1.0)
    sp = stack["case_screw_sp"]
    # where the screws are drawn: on the local x or y axis
    m = re.search(r"translate\(\[([^\]]*)\]\)\s*\n?\s*cylinder\(d = screw_pocket_d", scad)
    assert m, "case screw pilots not found in cradle.scad"
    on_x = m.group(1).split(",")[0].strip() != "0"
    screws = [(s * sp / 2, 0.0) if on_x else (0.0, s * sp / 2) for s in (-1, 1)]
    for a in az:
        u = np.array([math.cos(elev) * math.cos(math.radians(a)), math.cos(elev) * math.sin(math.radians(a)), -math.sin(elev)])
        c = np.array([0.0, 0.0, zc])
        p0, p1 = c + u * r_in, c + u * (r_in + seat_depth)
        for sx, sy in screws:
            d = _seg_line_dist(p0, p1, (sx, sy, screw_top))
            assert d >= seat_d / 2 + pilot_d / 2 + 0.5, f"screw at ({sx}, {sy}) cuts the {a} deg bearing seat ({d:.2f} mm)"
    # and the screw thread (M2, 1.0 radius) keeps 0.5 mm of plastic to the ball cavity at its tip
    for sx, sy in screws:
        r_cup = math.sqrt(max(0.0, r_in ** 2 - (zc - screw_top) ** 2))
        assert math.hypot(sx, sy) - 1.0 - r_cup >= 0.5, f"screw tip breaks into the cup ({math.hypot(sx, sy) - 1.0 - r_cup:.2f} mm)"


def test_optical_window_is_open_along_the_axis():
    """The sensor must see the ball: a bundle of rays from the ball centre along the optical axis
    (window_az, sensor_angle) has to leave the committed cradle without touching plastic until it
    reaches the module. Until r2.4b the window cylinder was cut along local +z, away from the
    sensor, and the whole 1.6 mm cup wall stayed solid in front of the lens; the trigonometric
    window checks above stayed green because they never looked at the mesh."""
    trimesh = pytest.importorskip("trimesh")
    s = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    mesh = load_layout_frame(CRADLE / "stl" / "cradle-19mm-pocket.stl")
    th, a = math.radians(s["sensor_angle"]), math.radians(s["window_az"])
    u = np.array([math.sin(th) * math.cos(a), math.sin(th) * math.sin(a), -math.cos(th)])
    side = np.array([-math.sin(a), math.cos(a), 0.0])
    up = np.cross(u, side)
    c = np.array([0.0, 0.0, s["ball_centre_z"]])
    ts = np.arange(s["ball_d"] / 2, s["sensor_pcb_plane_dist"] - _param("lens_h"), 0.1)
    r = 0.8 * _param("optical_d") / 2
    for off in (np.zeros(3), r * side, -r * side, r * up, -r * up):
        pts = c + off + np.outer(ts, u)
        hit = mesh.contains(pts)
        assert not hit.any(), f"plastic on the optical path at t = {ts[hit][0]:.2f} mm (offset {off.round(2)})"


def test_module_sits_at_the_window_azimuth():
    """The sleeve's slot (and so the module) must point where the window and the tab point.
    tab_2d and STACK window_az share one formula, so checking them against each other proves
    nothing; the module dummy is placed through sensor_frame() and is the independent witness."""
    if openscad() is None:
        pytest.skip("openscad not installed")
    trimesh = pytest.importorskip("trimesh")
    import tempfile
    s = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "dummy.stl"
        res = subprocess.run([openscad(), "--backend", "manifold", "-D", 'part="sensor_dummy"', "-o", str(out), str(SCAD)],
                             capture_output=True, text=True, timeout=600)
        assert res.returncode == 0, res.stderr
        v = load_layout_frame(out).vertices
    cx, cy = v[:, 0].mean(), v[:, 1].mean()
    az = math.degrees(math.atan2(cy, cx)) % 360
    assert abs((az - s["window_az"] + 180) % 360 - 180) < 2.0, f"module at {az:.1f} deg, window at {s['window_az']}"
