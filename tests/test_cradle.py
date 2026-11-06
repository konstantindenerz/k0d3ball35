# SPDX-License-Identifier: MIT
"""Checks for the parametric trackball cradle (hardware/trackball-cradle).

r2 mounts the module in a case pocket beside the right PCB (``mount = "pocket"``) with a
19.05 mm ball; the 25 mm pocket and the r1 cutout mount stay as variants. The cradle has no
retainer: the rim stays ``rim_drop`` below the equator and the case lid keeps the ball in
for transport. The housing has no screw ears: the two case screws (M2 x 10) come up through
the case floor and the sensor board into the sensor posts, so the floor footprint is the bare
housing. The OpenSCAD dependent tests are skipped when no OpenSCAD binary is available.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CRADLE = ROOT / "hardware" / "trackball-cradle"
SCAD = CRADLE / "cradle.scad"
LAYOUT = ROOT / "hardware" / "layout" / "k0d3ball35.yaml"

# PMW3610DM-SUDU datasheet, table 2 and figure 4
LENS_Z_MIN, LENS_Z_MAX = 2.2, 2.6
LENS_H, SENSOR_PCB_T = 3.4, 1.6
PCB_T = 1.6
RIM_DROP = 1.0   # params.scad rim_drop: cup rim this far below the ball equator
CLAW_KEYS = {"claw_top_z", "retainer_ball_play"}
HOUSING_X, HOUSING_Y = 29.0, 29.0   # sensor board 26 x 25 plus walls (1.5 on x, 2 on y)
CASE_SCREW_SP = 20.0                # sensor_hole_sp: the case screws go into the sensor posts
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
    assert re.search(r'^mount\s*=\s*"pocket"', params, re.M), "pocket mount must be the default"
    assert re.search(r"^ball_d\s*=\s*19\.05", params, re.M), "19.05 mm ball must be the default"
    assert re.search(r"^rim_drop\s*=\s*1\.0", params, re.M)
    # no retainer anywhere: no claw ring parameters, no retainer part, no peg holes
    scad = SCAD.read_text()
    for name in ("retainer_t", "retainer_claws", "claw_w", "claw_h", "claw_grip", "peg_d", "peg_h"):
        assert not re.search(rf"^{name}\s*=", params, re.M), name
    assert "module retainer" not in scad
    assert 'part == "retainer"' not in scad
    assert "peg" not in scad.lower()
    assert "claw" not in scad.lower()
    makefile = (CRADLE / "Makefile").read_text()
    assert "retainer" not in makefile
    assert not list((CRADLE / "stl").glob("retainer*"))


def test_no_screw_ears():
    """The case screws go through the sensor posts; the housing has no ears and no ear parameters."""
    params = (CRADLE / "params.scad").read_text()
    scad = SCAD.read_text()
    for name in ("ear_r", "ear_x", "ear_w"):
        assert not re.search(rf"^{name}\s*=", params, re.M), name
        assert name not in scad, name
    assert re.search(r"^case_screw_d\s*=\s*2\.0", params, re.M)
    assert re.search(r"^sensor_hole_sp\s*=\s*20", params, re.M)
    readme = (CRADLE / "README.md").read_text()
    for text, name in ((params, "params.scad"), (scad, "cradle.scad"), (readme, "README.md")):
        assert not EAR_RE.search(text), name
    assert "43 x 29" not in readme and "36 mm apart" not in readme
    assert "M2 x 10" in readme


def test_stack_json_values(stack):
    assert {"19mm-pocket", "25mm-pocket", "25mm-cutout"} <= set(stack)
    for name, v in stack.items():
        assert LENS_Z_MIN <= v["lens_reference_plane_dist"] <= LENS_Z_MAX, name
        # sensor PCB plane = ball radius + lens distance + lens height
        assert abs(v["sensor_pcb_plane_dist"] - (v["ball_d"] / 2 + v["lens_reference_plane_dist"] + LENS_H)) < 1e-6, name
        # nothing below the agreed envelope (case floor 10 mm under the PCB underside)
        assert min(v["lowest_plastic_z"], v["lowest_sensor_board_z"]) >= -(PCB_T + v["depth_below_pcb_bottom"]) - 1e-6, name
        # no retainer: the rim stays rim_drop below the equator so the ball lifts out freely
        assert not CLAW_KEYS & set(v), name
        assert abs(v["rim_below_equator"] - RIM_DROP) < 1e-6, name
        assert abs((v["ball_centre_z"] - v["rim_z"]) - RIM_DROP) < 1e-6, name
        assert v["rim_z"] < v["ball_centre_z"] < v["ball_top_above_pcb_top"], name
        if v["mount_pocket"]:
            # the module stands on the case floor and keeps clear of the PCB underside
            assert abs(v["lowest_plastic_z"] - v["floor_z"]) < 1e-6, name
            assert v["housing_top_z"] <= -PCB_T - 0.3 + 1e-6, name
            # everything above the PCB fits into the notch with clearance
            assert v["envelope_d_above_pcb"] / 2 < v["notch_apothem"] - 0.3, name
            # no ears: the floor footprint is the housing, the case screws sit in the sensor posts
            assert v["housing_x"] == HOUSING_X and v["housing_y"] == HOUSING_Y, name
            assert v["footprint_x"] == v["housing_x"] and v["footprint_y"] == v["housing_y"], name
            assert v["case_screw_sp"] == CASE_SCREW_SP, name
            assert v["case_screw_sp"] < v["housing_y"] - 2 * 2.5, name   # posts stay inside the walls
        else:
            # cup fits through the PCB cutout; the case screw spacing is a pocket-mount value
            assert v["cup_outer_d"] < v["pcb_cutout_d"], name
            assert "case_screw_sp" not in v, name


def test_default_variant_matches_layout(stack, trackball_cfg):
    """The 19 mm pocket cradle is what the layout's clearance check and PCB notch assume."""
    v = stack["19mm-pocket"]
    assert v["ball_d"] == trackball_cfg["ball_diameter"]
    assert v["envelope_d_above_pcb"] <= trackball_cfg["cradle_diameter"]
    assert v["notch_apothem"] == trackball_cfg["cradle_diameter"] / 2 + trackball_cfg["pocket"]["notch_clearance"]
    # ball top about 17 mm above the PCB top, sensor board on the floor 11.6 mm below it
    assert 16.5 < v["ball_top_above_pcb_top"] < 17.5
    assert abs(v["lowest_sensor_board_z"] + 11.6) < 1e-6
    # 25 mm fallback needs the wider notch
    assert stack["25mm-pocket"]["envelope_d_above_pcb"] > trackball_cfg["cradle_diameter"]


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_render_19mm_pocket_stl(tmp_path):
    out = tmp_path / "cradle.stl"
    values, log = run_scad({"ball_d": 19.05, "mount": "pocket"}, out)
    assert "WARNING" not in log and "ERROR" not in log
    assert out.stat().st_size > 100_000
    assert LENS_Z_MIN <= values["lens_reference_plane_dist"] <= LENS_Z_MAX
    trimesh = pytest.importorskip("trimesh")
    mesh = trimesh.load(out, force="mesh")
    assert mesh.is_watertight
    assert mesh.volume > 1000
    v = mesh.vertices
    # stands on the case floor, never reaches into the PCB slab beside the notch
    assert abs(v[:, 2].min() - values["floor_z"]) < 0.05
    above = v[v[:, 2] > -PCB_T - 0.3 + 0.05]
    radius = (above[:, :2] ** 2).sum(axis=1) ** 0.5
    assert radius.max() <= values["notch_apothem"] - 0.3 + 1e-3
    assert radius.max() <= values["envelope_d_above_pcb"] / 2 + 1e-3
    # nothing printed above the rim (no claws), rim 1 mm below the ball centre
    assert v[:, 2].max() <= values["rim_z"] + 1e-3
    assert abs(values["ball_centre_z"] - values["rim_z"] - RIM_DROP) < 1e-6
    # housing footprint on the floor: sensor board plus walls, nothing else (no ears)
    on_floor = v[v[:, 2] < values["floor_z"] + 0.5]
    assert abs(on_floor[:, 0].max() - values["housing_x"] / 2) < 0.6
    assert abs(on_floor[:, 1].max() - values["housing_y"] / 2) < 0.6
    assert abs(on_floor[:, 0]).max() <= HOUSING_X / 2 + 0.5
    assert abs(on_floor[:, 1]).max() <= HOUSING_Y / 2 + 0.5
    assert values["footprint_x"] == values["housing_x"]
    # the case screw path is open from the floor to the posts: a ray at (0, +-10) from below hits
    # the pilot hole, i.e. the mesh has vertices of the 1.6 mm pilot right above the board plane
    for sy in (-1, 1):
        near = v[(abs(v[:, 0]) < 1.0) & (abs(v[:, 1] - sy * CASE_SCREW_SP / 2) < 1.0)
                 & (v[:, 2] > values["sensor_pcb_plane_z"] - 0.1) & (v[:, 2] < values["sensor_pcb_plane_z"] + 1.0)]
        assert len(near) > 0, sy
        r = ((near[:, 0]) ** 2 + (near[:, 1] - sy * CASE_SCREW_SP / 2) ** 2) ** 0.5
        assert abs(r.max() - 0.8) < 0.1, r.max()   # flange_pilot_d / 2


def _dxf_loops(path):
    ezdxf = pytest.importorskip("ezdxf")
    doc = ezdxf.readfile(str(path))
    loops = []
    for e in doc.modelspace():
        if e.dxftype() == "LWPOLYLINE":
            loops.append([(p[0], p[1]) for p in e.get_points()])
        elif e.dxftype() == "CIRCLE":
            c, r = e.dxf.center, e.dxf.radius
            loops.append([(c.x + r, c.y), (c.x - r, c.y), (c.x, c.y + r), (c.x, c.y - r)])
    return loops


def test_floor_dxf_is_housing_with_two_screw_holes():
    """dxf/floor-19mm-pocket.dxf: 30 x 30 mm outline (0.5 mm clearance) and two 2.2 mm holes 20 mm apart."""
    loops = _dxf_loops(CRADLE / "dxf" / "floor-19mm-pocket.dxf")
    assert len(loops) == 3, len(loops)
    boxes = []
    for pts in loops:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        boxes.append((min(xs), max(xs), min(ys), max(ys)))
    boxes.sort(key=lambda b: b[1] - b[0], reverse=True)
    outer, *holes = boxes
    assert abs(outer[1] - outer[0] - (HOUSING_X + 1.0)) < 0.05
    assert abs(outer[3] - outer[2] - (HOUSING_Y + 1.0)) < 0.05
    assert abs(outer[0] + outer[1]) < 0.05 and abs(outer[2] + outer[3]) < 0.05
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
