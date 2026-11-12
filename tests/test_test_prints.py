# SPDX-License-Identifier: MIT
"""The two stand-ins for the test fit: the printed PCB plate and the printed ball.

The plate replaces the main board until the boards are ordered, so it has to be that board: the
committed STLs are read as a slicer reads them (print frame) and compared with the KiCad files,
outline and every non-plated drill of the switches and the mounting holes. A plate mirrored in x
or y, or with the thumb keys turned the wrong way, fails here.
"""
from __future__ import annotations

import math
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from shapely.geometry import Point, Polygon

from mesh_tools import section
from test_case_handedness import PCB_T, board, to_print

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "hardware" / "case"
CRADLE = ROOT / "hardware" / "trackball-cradle"
BALL_D = 19.05
FPC_H = 2.0          # J1 on the key side of the right board (tray.scad pcb_test)

trimesh = pytest.importorskip("trimesh")
np = pytest.importorskip("numpy")


def _param(name: str) -> float:
    return float(re.search(rf"^{name}\s*=\s*([\d.]+);", (CASE / "params.scad").read_text(), re.M)[1])


def drills(half: str) -> list[tuple[float, float, float]]:
    """Every non-plated hole of the switches and the mounting holes: x, y (print frame), diameter."""
    text = (ROOT / "hardware" / f"{half}-pcb" / f"k0d3ball35-{half}.kicad_pcb").read_text()
    out = []
    for fp in re.split(r"\n\t\(footprint ", text)[1:]:
        if not fp.startswith(('"k0d3ball35:SW_Choc', '"k0d3ball35:MountingHole')):
            continue
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", fp)
        fx, fy, rot = float(at[1]), float(at[2]), math.radians(float(at[3] or 0))
        for m in re.finditer(r"\(pad \"\" np_thru_hole circle\s*\(at ([-\d.]+) ([-\d.]+)[^)]*\)\s*\(size [^)]*\)\s*\(drill ([\d.]+)\)", fp):
            x, y, d = float(m[1]), float(m[2]), float(m[3])
            # KiCad turns a footprint counter-clockwise on the screen, where y points down
            kx = fx + x * math.cos(rot) + y * math.sin(rot)
            ky = fy - x * math.sin(rot) + y * math.cos(rot)
            out.append((*to_print(kx, ky), d))
    return out


@pytest.mark.parametrize("half", ["left", "right"])
def test_pcb_test_plate_is_the_board(half):
    mesh = trimesh.load(CASE / "stl" / f"pcb-test-{half}.stl", force="mesh")
    lo, hi = mesh.bounds
    assert abs(lo[2] + PCB_T) < 0.01
    assert abs(hi[2] - (FPC_H if half == "right" else 0.0)) < 0.01
    cut = section(mesh, -PCB_T / 2)
    assert cut.geom_type == "Polygon", "one plate"
    outline = Polygon(board(half)["outline"])
    assert Polygon(cut.exterior).symmetric_difference(outline).area < 0.5, "not the board outline"

    fit = _param("test_hole_fit")
    want = drills(half)
    assert len(want) > 100 and len(want) % 6 == 5, f"five mounting holes and six drills per switch, got {len(want)}"
    holes = [Polygon(r) for r in cut.interiors]
    assert len(holes) == len(want), (len(holes), len(want))
    for x, y, d in want:
        hit = [h for h in holes if h.contains(Point(x, y))]
        assert len(hit) == 1, f"{half}: no hole at ({x:.2f}, {y:.2f})"
        c = hit[0].centroid
        assert math.hypot(c.x - x, c.y - y) < 0.05, (half, x, y, c.x, c.y)
        got = 2 * math.sqrt(hit[0].area / math.pi)
        assert abs(got - (d + fit)) < 0.08, f"{half}: hole at ({x:.2f}, {y:.2f}) is {got:.2f}, drill {d} + {fit}"


def test_pcb_test_plate_carries_j1():
    b = board("right")
    mesh = trimesh.load(CASE / "stl" / "pcb-test-right.stl", force="mesh")
    block = section(mesh, FPC_H / 2)
    j1 = Point(b["refs"]["J1"])
    assert block.area > 30 and block.buffer(0.01).contains(j1), "J1's body is not where the board has J1"


def test_ball_half():
    mesh = trimesh.load(CRADLE / "stl" / "ball-19mm-test-half.stl", force="mesh")
    lo, hi = mesh.bounds
    assert abs(lo[2]) < 0.01 and abs(hi[2] - BALL_D / 2) < 0.01, "flat face on the bed, one radius high"
    for axis in (0, 1):
        assert abs(hi[axis] - lo[axis] - BALL_D) < 0.02
    r = np.linalg.norm(mesh.vertices[mesh.vertices[:, 2] > 4.5], axis=1)
    assert abs(r - BALL_D / 2).max() < 0.01, "not a sphere about the centre of the flat face"
    pin = section(mesh, 2.0).interiors
    assert len(pin) == 1 and abs(2 * math.sqrt(Polygon(pin[0]).area / math.pi) - 1.9) < 0.05


def _openscad():
    exe = shutil.which("openscad") or "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    return exe if Path(exe).exists() else None


@pytest.mark.skipif(_openscad() is None, reason="openscad not installed")
@pytest.mark.parametrize("scad, defs, stl", [
    (CASE / "case.scad", {"part": "pcb_test", "half": "left"}, CASE / "stl" / "pcb-test-left.stl"),
    (CASE / "case.scad", {"part": "pcb_test", "half": "right"}, CASE / "stl" / "pcb-test-right.stl"),
    (CRADLE / "cradle.scad", {"part": "ball_test_half"}, CRADLE / "stl" / "ball-19mm-test-half.stl"),
], ids=["pcb-test-left", "pcb-test-right", "ball-half"])
def test_committed_stl_is_fresh(tmp_path, scad, defs, stl):
    out = tmp_path / stl.name
    cmd = [_openscad(), "--backend", "manifold"]
    for k, v in defs.items():
        cmd += ["-D", f'{k}="{v}"']
    res = subprocess.run(cmd + ["-o", str(out), str(scad)], capture_output=True, text=True, timeout=600)
    assert res.returncode == 0, res.stderr
    assert "WARNING" not in res.stderr and "ERROR" not in res.stderr
    new, old = trimesh.load(out, force="mesh"), trimesh.load(stl, force="mesh")
    assert np.allclose(new.bounds, old.bounds, atol=1e-3) and abs(new.volume - old.volume) < 0.01
