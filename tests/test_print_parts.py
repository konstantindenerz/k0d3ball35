# SPDX-License-Identifier: MIT
"""Every committed STL that goes to the printer: one closed body, nothing loose, fits the bed.

A slicer repairs most defects silently and prints the result, so they have to be caught here: a
second body is a stray sliver on the bed (the inner lid plates carried one of 2 mm3), an edge
shared by four faces is a zero-thickness contact between two cuts, and an open edge is a hole.
The files are the committed ones, i.e. what a builder downloads; test_case.py and test_cradle.py
check that they match the sources.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mesh_tools import bad_edges, bodies
from scad_frame import load_layout_frame

ROOT = Path(__file__).resolve().parents[1]
CASE_STL = ROOT / "hardware" / "case" / "stl"
CRADLE_STL = ROOT / "hardware" / "trackball-cradle" / "stl"

# What is printed. lid-*.stl and lid-folded-*.stl show both plates together for the page and the
# previews; the plates are printed one by one.
PRINTED = sorted(p for p in list(CASE_STL.glob("*.stl")) + list(CRADLE_STL.glob("*.stl"))
                 if not p.name.startswith(("lid-left", "lid-right", "lid-folded")))
BED = 180.0     # the smallest common bed (Prusa Mini, Bambu A1 mini)


def test_the_list_is_complete():
    names = {p.name for p in PRINTED}
    for half in ("left", "right"):
        for part in ("tray", "box-cap", "guard", "lid-outer", "lid-inner"):
            assert f"{part}-{half}.stl" in names
    assert {"pocket-cover-right.stl", "pocket-clip-right.stl", "cradle-19mm-pocket.stl"} <= names


@pytest.mark.parametrize("path", PRINTED, ids=lambda p: p.name)
def test_print_part_is_one_closed_body(path):
    pytest.importorskip("trimesh")
    mesh = load_layout_frame(path)
    assert len(mesh.faces) > 100
    parts = bodies(mesh)
    assert len(parts) == 1, f"{path.name}: {len(parts)} separate bodies (face counts {parts[:4]})"
    bad = bad_edges(mesh)
    assert not bad, f"{path.name}: {len(bad)} open or non-manifold edges, e.g. {bad[:2]}"
    assert mesh.volume > 50.0, f"{path.name}: inside-out or empty"


@pytest.mark.parametrize("path", PRINTED, ids=lambda p: p.name)
def test_print_part_fits_a_small_bed(path):
    pytest.importorskip("trimesh")
    x, y, z = load_layout_frame(path).extents
    assert max(x, y) <= BED and min(x, y) <= BED, f"{path.name}: {x:.1f} x {y:.1f} mm"
    assert z <= 60.0


def test_ci_renders_the_parts():
    """The render tests skip where OpenSCAD is missing, and for a long time that was every CI
    job: nothing in tests/test_case.py or tests/test_cradle.py ever ran on a push. One job has to
    carry OpenSCAD and run them."""
    import yaml

    jobs = yaml.safe_load((ROOT / ".github" / "workflows" / "tests.yml").read_text())["jobs"]
    scad = [j for j in jobs.values() if "openscad" in str(j.get("container", {}).get("image", ""))]
    assert len(scad) == 1, "one job in an OpenSCAD image"
    runs = " ".join(str(s.get("run", "")) for s in scad[0]["steps"])
    for name in ("test_case.py", "test_cradle.py", "test_retainer.py", "test_thin_walls.py", "test_print_parts.py",
                 "test_case_pocket.py", "test_case_guard.py", "test_assembly_interference.py"):
        assert f"tests/{name}" in runs, f"{name} is not run with OpenSCAD in CI"
    assert "openscad --version" in runs
