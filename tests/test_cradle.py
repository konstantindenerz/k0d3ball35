# SPDX-License-Identifier: MIT
"""Checks for the parametric trackball cradle (hardware/trackball-cradle).

r2 mounts the module in a case pocket beside the right PCB (``mount = "pocket"``) with a
19.05 mm ball; the 25 mm pocket and the r1 cutout mount stay as variants. The OpenSCAD
dependent tests are skipped when no OpenSCAD binary is available.
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


def test_stack_json_values(stack):
    assert {"19mm-pocket", "25mm-pocket", "25mm-cutout"} <= set(stack)
    for name, v in stack.items():
        assert LENS_Z_MIN <= v["lens_reference_plane_dist"] <= LENS_Z_MAX, name
        # sensor PCB plane = ball radius + lens distance + lens height
        assert abs(v["sensor_pcb_plane_dist"] - (v["ball_d"] / 2 + v["lens_reference_plane_dist"] + LENS_H)) < 1e-6, name
        # nothing below the agreed envelope (case floor 10 mm under the PCB underside)
        assert min(v["lowest_plastic_z"], v["lowest_sensor_board_z"]) >= -(PCB_T + v["depth_below_pcb_bottom"]) - 1e-6, name
        # retainer must capture the ball with limited play
        assert 0 < v["retainer_ball_play"] < 2.0, name
        if v["mount_pocket"]:
            # the module stands on the case floor and keeps clear of the PCB underside
            assert abs(v["lowest_plastic_z"] - v["floor_z"]) < 1e-6, name
            assert v["housing_top_z"] <= -PCB_T - 0.3 + 1e-6, name
            # everything above the PCB fits into the notch with clearance
            assert v["envelope_d_above_pcb"] / 2 < v["notch_apothem"] - 0.3, name
        else:
            # cup fits through the PCB cutout
            assert v["cup_outer_d"] < v["pcb_cutout_d"], name


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
    # housing footprint on the floor: sensor board plus walls plus the two ears
    on_floor = v[v[:, 2] < values["floor_z"] + 0.5]
    assert abs(on_floor[:, 0].max() - values["footprint_x"] / 2) < 0.6
    assert abs(on_floor[:, 1].max() - values["footprint_y"] / 2) < 0.6


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_render_other_variants(tmp_path):
    for overrides in (
        {"ball_d": 25, "mount": "pocket", "notch_apothem": 16.5},
        {"ball_d": 25, "mount": "cutout"},
        {"ball_d": 19.05, "mount": "pocket", "part": "retainer"},
    ):
        out = tmp_path / "part.stl"
        values, log = run_scad(overrides, out)
        assert "ERROR" not in log
        assert out.stat().st_size > 10_000
        if overrides.get("mount") == "cutout":
            assert values["cup_outer_d"] < values["pcb_cutout_d"]
