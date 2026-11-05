"""Checks for the parametric trackball cradle (hardware/trackball-cradle).

The OpenSCAD dependent tests are skipped when no OpenSCAD binary is available.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CRADLE = ROOT / "hardware" / "trackball-cradle"
SCAD = CRADLE / "cradle.scad"

# PMW3610DM-SUDU datasheet, table 2 and figure 4
LENS_Z_MIN, LENS_Z_MAX = 2.2, 2.6
LENS_H, SENSOR_PCB_T = 3.4, 1.6


def openscad():
    for cand in (shutil.which("openscad"), "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"):
        if cand and Path(cand).exists():
            return cand
    return None


def run_scad(overrides, out):
    cmd = [openscad(), "--backend", "manifold", "-D", 'part="cradle"']
    for k, v in overrides.items():
        cmd += ["-D", f"{k}={v}"]
    cmd += ["-o", str(out), str(SCAD)]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    assert res.returncode == 0, res.stderr
    values = {m.group(1): float(m.group(2)) for m in re.finditer(r'STACK (\w+)=(-?[\d.]+)', res.stderr + res.stdout)}
    return values, res.stderr


def test_sources_present():
    assert SCAD.exists()
    assert (CRADLE / "params.scad").exists()
    assert (CRADLE / "README.md").exists()
    assert "lens_z" in (CRADLE / "params.scad").read_text()


def test_stack_json_values():
    data = json.loads((CRADLE / "stack.json").read_text())
    for name, v in data["variants"].items():
        assert LENS_Z_MIN <= v["lens_reference_plane_dist"] <= LENS_Z_MAX, name
        # sensor PCB plane = ball radius + lens distance + lens height
        assert abs(v["sensor_pcb_plane_dist"] - (v["ball_d"] / 2 + v["lens_reference_plane_dist"] + LENS_H)) < 1e-6, name
        # nothing below the agreed envelope
        assert min(v["lowest_plastic_z"], v["lowest_sensor_board_z"]) >= -(1.6 + v["depth_below_pcb_bottom"]) - 1e-6, name
        # retainer must capture the ball with limited play
        assert 0 < v["retainer_ball_play"] < 2.0, name
        # cup fits through the PCB cutout
        assert v["cup_outer_d"] < v["pcb_cutout_d"], name
    d25 = data["variants"]["25mm"]
    assert d25["ball_top_above_pcb_top"] < 24.0


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_render_25mm_stl(tmp_path):
    out = tmp_path / "cradle.stl"
    values, log = run_scad({"ball_d": 25}, out)
    assert "WARNING" not in log and "ERROR" not in log
    assert out.stat().st_size > 100_000
    assert LENS_Z_MIN <= values["lens_reference_plane_dist"] <= LENS_Z_MAX
    trimesh = pytest.importorskip("trimesh")
    mesh = trimesh.load(out, force="mesh")
    assert mesh.is_watertight
    assert mesh.volume > 1000
    # the cup must fit through the 30 mm cutout: nothing wider than 29.5 mm inside the PCB slab
    v = mesh.vertices
    in_slab = (v[:, 2] > -1.5) & (v[:, 2] < -0.1)
    assert in_slab.any()
    radius = (v[in_slab, :2] ** 2).sum(axis=1) ** 0.5
    assert radius.max() <= values["pcb_cutout_d"] / 2 - 0.4


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_render_retainer_and_34mm(tmp_path):
    for overrides in ({"ball_d": 34}, {"ball_d": 25, "part": '"retainer"'}):
        out = tmp_path / "part.stl"
        _, log = run_scad(overrides, out)
        assert "ERROR" not in log
        assert out.stat().st_size > 10_000
