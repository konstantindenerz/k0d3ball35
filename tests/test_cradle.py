# SPDX-License-Identifier: MIT
"""Checks for the parametric trackball cradle (hardware/trackball-cradle).

r2 mounts the module in a case pocket beside the right PCB (``mount = "pocket"``) with a
19.05 mm ball; the 25 mm pocket and the r1 cutout mount stay as variants. The cup has nothing
above its rim: the rim stays ``rim_drop`` below the equator. Keeping the ball in when the half is
turned over is the job of the optional clip-on retainer (``part = "retainer"``, two claws away
from the thumb, checked by ``retention.py``) or of the case lid. The housing has no screw ears: the two case screws (M2 x 10) come up through
the case floor and the sensor board into the sensor posts, so the floor footprint is the bare
housing. The OpenSCAD dependent tests are skipped when no OpenSCAD binary is available.
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


def test_sources_present():
    assert SCAD.exists()
    params = (CRADLE / "params.scad").read_text()
    assert (CRADLE / "README.md").exists()
    assert "lens_z" in params
    assert re.search(r"^ball_d\s*=\s*19\.05", params, re.M), "19.05 mm ball must be the default"
    assert re.search(r"^rim_drop\s*=\s*1\.0", params, re.M)
    # the retainer is a separate, optional part: the cradle module never grows claws, and the
    # old peg-in-hole ring (removed 2026-11-06) does not come back
    scad = SCAD.read_text()
    for name in ("retainer_claw_az", "retainer_claw_h", "retainer_fingers", "retainer_nub"):
        assert re.search(rf"^{name}\s*=", params, re.M), name
    for name in ("peg_d", "peg_h", "retainer_claws"):
        assert not re.search(rf"^{name}\s*=", params, re.M), name
    assert "peg" not in scad.lower()
    assert "module retainer()" in scad and 'part == "retainer"' in scad
    cradle_body = re.search(r"^module cradle\(\) \{\n(.*?)^\}", scad, re.M | re.S).group(1)
    assert "retainer" not in cradle_body
    makefile = (CRADLE / "Makefile").read_text()
    assert "stl/retainer-19mm.stl" in makefile and "retention.json" in makefile


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
    assert re.search(r"^sensor_az\s*=\s*270", params, re.M), "tilt towards +y, away from the keys"
    readme = (CRADLE / "README.md").read_text()
    for text, name in ((params, "params.scad"), (scad, "cradle.scad"), (readme, "README.md")):
        assert not EAR_RE.search(text), name
    assert "43 x 29" not in readme and "36 mm apart" not in readme
    assert "M2 x 10" in readme


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
    assert abs(on_floor[:, 0].max() - cup_r) < 0.6, "the cup skirt sets the +x edge"
    lean = max(-on_floor[:, 1].min(), on_floor[:, 1].max())
    assert lean > cup_r + 1.0, "the sleeve does not reach past the cup skirt on the floor"
    assert lean <= values["board_reach"] + 2.0 + 1e-3, "the sleeve reaches further than the module"
    # The old bound was the sleeve rectangle. Since r2.4 the cup skirt is the widest thing on the
    # floor across the lean, and the sleeve only sticks out along it.
    assert abs(on_floor[:, 0]).max() <= cup_r + 0.05
    assert values["footprint_x"] == values["housing_x"]
    # The case screws changed in r2.4: with the module beside the ball the floor under the ball is
    # solid plastic, so the two M2 x 10 go straight up into the cup skirt instead of through
    # sensor posts. Check the 1.6 mm pilot is there, well above the floor so a short bore fails.
    for sy in (-1, 1):
        axis_y = sy * CASE_SCREW_SP / 2
        r = np.hypot(v[:, 0], v[:, 1] - axis_y)
        pilot = v[(np.abs(r - 0.8) < 0.05) & (v[:, 2] >= values["floor_z"] - 1e-6)]
        assert len(pilot) > 0, f"no 1.6 mm screw pilot at y = {axis_y}"
        thread = pilot[:, 2].max() - values["floor_z"]
        assert thread >= 4.0, f"only {thread:.2f} mm of thread in the skirt at y = {axis_y}"


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
    the cup on one side only and symmetric about x. Getting this wrong makes the case cut a pocket
    well of the wrong size, which is how an oversized well slipped through once in r2.4: a formula
    placed the unclipped sleeve 21.4 mm from the axis instead of the real 14.3.
    """
    loops = _dxf_loops(CRADLE / "dxf" / "floor-19mm-pocket.dxf")
    assert len(loops) == 3, len(loops)
    boxes = []
    for pts in loops:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        boxes.append((min(xs), max(xs), min(ys), max(ys)))
    boxes.sort(key=lambda b: (b[1] - b[0]) * (b[3] - b[2]), reverse=True)
    outer, *holes = boxes
    stack = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    cup_r = stack["cup_outer_d"] / 2
    # across the lean the cup sets the width, and it is centred on the ball axis
    assert abs(outer[1] - outer[0] - 2 * (cup_r + 0.5)) < 0.05
    assert abs(outer[0] + outer[1]) < 0.05, "the footprint is symmetric about x"
    # along the lean it is not: the sleeve adds to one side, the cup bounds the other. The sleeve
    # leans towards layout +y (window_az 90, the back edge), never towards the keys.
    assert stack["window_az"] == 90
    lean, back = outer[3], -outer[2]
    assert abs(back - (cup_r + 0.5)) < 0.05, "the cup bounds the side away from the sleeve"
    assert cup_r + 1.0 < lean <= stack["board_reach"] + 2.0, f"sleeve reach {lean:.2f} mm"
    # and the DXF agrees with the STL: both files are in the print frame, so the floor section of
    # the printed part must lean the same way as its footprint. A doubled mirror in floor2d()
    # once flipped only the DXF, and the line above, written against that DXF, agreed with it.
    mesh = load_layout_frame(CRADLE / "stl" / "cradle-19mm-pocket.stl")
    v = mesh.vertices
    foot = v[v[:, 2] < v[:, 2].min() + 0.5]
    assert foot[:, 1].max() > -foot[:, 1].min() + 1.0, "STL leans the other way than the DXF"
    assert abs(foot[:, 1].max() + 0.5 - lean) < 0.6, (foot[:, 1].max(), lean)
    centres = sorted(((b[0] + b[1]) / 2, (b[2] + b[3]) / 2) for b in holes)
    for (cx, cy), b in zip(centres, sorted(holes, key=lambda b: (b[2] + b[3]) / 2)):
        assert abs(cx) < 0.05
        assert abs(b[1] - b[0] - 2.2) < 0.1, "M2 clearance hole"
    assert abs(centres[0][1] + CASE_SCREW_SP / 2) < 0.05
    assert abs(centres[1][1] - CASE_SCREW_SP / 2) < 0.05


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_render_other_variants(tmp_path):
    for overrides in (
        {"ball_d": 25, "mount": "pocket", "notch_apothem": 16.5},
        {"ball_d": 25, "mount": "cutout"},
    ):
        out = tmp_path / "part.stl"
        values, log = run_scad(overrides, out)
        assert "ERROR" not in log
        assert out.stat().st_size > 10_000
        if overrides.get("mount") == "cutout":
            assert values["cup_outer_d"] < values["pcb_cutout_d"]


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
    boss - which is the reason bearing_az was rotated 30 degrees in r2.4. Without this check the
    rotation looks like an arbitrary edit and the next person undoes it.
    """
    tilt = _param("sensor_angle")
    # NOT _param("sensor_az"): the window sits at -sensor_az (see STACK window_az). Reading the
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
    az = v["sensor_angle"] and v.get("sensor_az", 270)
    # the module leans along +y of the layout frame for sensor_az = 270
    assert az == 270, "this check assumes the r2.4 azimuth; re-derive the signs if it changes"
    for key in ("housing_offset", "sensor_board_offset"):
        off = pk.get(key)
        assert off is not None, f"{key} missing from the layout"
        assert off["x"] == 0, f"{key} must not lean in x while the tilt is along y"
        assert off["y"] > 0, f"{key} leans the wrong way for sensor_az = {az}"
    # the corridor has to cover where the module really is
    far = pk["sensor_board_offset"]["y"] + pk["sensor_board"]["y"] / 2
    near = pk["sensor_board_offset"]["y"] - pk["sensor_board"]["y"] / 2
    assert abs(far - v["module_reach"]) <= 0.5, f"corridor ends at {far:.2f}, module at {v['module_reach']:.2f}"
    assert near > 0, "the corridor must start off the ball axis, on the side the module leans to"
    assert near <= v["board_reach"], f"corridor starts at {near:.2f}, past the module's near face"
