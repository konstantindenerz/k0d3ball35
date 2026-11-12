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
