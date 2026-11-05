# SPDX-License-Identifier: MIT
"""Geometry checks for the key layout (hardware/layout/k0d3ball36.yaml)."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
from shapely.geometry import Point

from k0d3.geometry import REPO, check_layout, load_layout

SPEC_STAGGER = {0: 10.44, 1: 4.19, 2: 0.0, 3: 2.23, 4: 4.46}


@pytest.fixture(scope="module")
def layout():
    return load_layout()


def test_key_count(layout):
    assert len(layout.keys) == 18
    assert sum(k.kind == "finger" for k in layout.keys) == 15
    assert sum(k.kind == "thumb" for k in layout.keys) == 3


def test_finger_pitch(layout):
    px, py = layout.pitch
    assert (px, py) == (18.0, 17.0)
    for col in range(5):
        ys = [layout.key(r, col).y for r in range(3)]
        xs = {layout.key(r, col).x for r in range(3)}
        assert len(xs) == 1
        assert ys[1] - ys[0] == pytest.approx(py, abs=1e-6)
        assert ys[2] - ys[1] == pytest.approx(py, abs=1e-6)
    for col in range(4):
        assert layout.key(0, col).x - layout.key(0, col + 1).x == pytest.approx(px, abs=1e-6)


def test_stagger_matches_spec(layout):
    mid = layout.key(0, 2).y
    for col, off in SPEC_STAGGER.items():
        assert layout.key(0, col).y - mid == pytest.approx(off, abs=0.01)


def test_thumb_arc(layout):
    thumbs = sorted((k for k in layout.keys if k.kind == "thumb"), key=lambda k: k.col)
    assert [t.row for t in thumbs] == [3, 3, 3]
    assert [t.col for t in thumbs] == [2, 3, 4]
    assert [t.rotation for t in thumbs] == [0, 10, 20]
    for a, b in zip(thumbs, thumbs[1:]):
        # Keyball39 arc pitch 21.63 mm scaled to the Choc pitch gives about 20.4 mm
        assert 19.5 <= math.dist((a.x, a.y), (b.x, b.y)) <= 21.0
        assert b.y > a.y  # inner thumb keys sit lower


def test_check_layout_clean(layout):
    assert check_layout(layout) == []


def test_no_keycap_overlap(layout):
    caps = [(k.ref, layout.keycap_polygon(k)) for k in layout.keys]
    for i, (ra, pa) in enumerate(caps):
        for rb, pb in caps[i + 1:]:
            assert pa.intersection(pb).area < 0.01, f"{ra} overlaps {rb}"


def test_cradle_clearance(layout):
    cradle = layout.cradle_polygon()
    need = layout.cfg["trackball"]["min_keycap_clearance"]
    assert need >= 1.0
    for k in layout.keys:
        assert layout.keycap_polygon(k).distance(cradle) >= need, k.ref


def test_cutout_inside_outline(layout):
    cutout = Point(*layout.ball_center).buffer(layout.cfg["trackball"]["pcb_cutout_diameter"] / 2, 64)
    assert layout.outline.contains(cutout)
    assert layout.outline.contains(layout.cradle_polygon())


def test_flange_holes_inside_outline(layout):
    tb = layout.cfg["trackball"]
    r = tb["flange_hole_circle"] / 2
    for ang in tb["flange_hole_angles"]:
        hole = Point(layout.ball_center[0] + r * math.cos(math.radians(ang)),
                     layout.ball_center[1] + r * math.sin(math.radians(ang))).buffer(1.1 + 0.3, 32)
        assert layout.outline.contains(hole), f"flange hole at {ang} deg breaks the board edge"


def test_outline_size(layout):
    b = layout.to_dict()["bounds"]
    assert 100 <= b["width"] <= 140
    assert 80 <= b["height"] <= 100
    assert layout.outline.is_valid and layout.outline.geom_type == "Polygon"


def test_mirror_symmetry(layout):
    """The left half is the right half mirrored in x: every key maps to a mirrored key."""
    right = {(k.row, k.col): (k.x, k.y, k.rotation) for k in layout.keys}
    left = {(r, c): (-x, y, -rot) for (r, c), (x, y, rot) in right.items()}
    for cell, (x, y, rot) in left.items():
        rx, ry, rrot = right[cell]
        assert (x, y, rot) == (-rx, ry, -rrot)
    assert len(left) == 18
    # mirrored keycaps must still be collision free
    from k0d3.geometry import rotated_box

    w, h = layout.keycap
    polys = [rotated_box(x, y, w, h, rot) for (x, y, rot) in left.values()]
    for i, a in enumerate(polys):
        for b in polys[i + 1:]:
            assert a.intersection(b).area < 0.01


def test_points_json_up_to_date(layout):
    path = REPO / "hardware" / "layout" / "output" / "points.json"
    if not path.exists():
        pytest.skip("points.json not generated yet (run scripts/gen_layout.py)")
    data = json.loads(path.read_text())
    assert len(data["keys"]) == 18
    by_cell = {(k["row"], k["col"]): k for k in data["keys"]}
    for k in layout.keys:
        j = by_cell[(k.row, k.col)]
        assert j["x"] == pytest.approx(k.x, abs=0.01)
        assert j["y"] == pytest.approx(k.y, abs=0.01)
        assert j["rotation"] == pytest.approx(k.rotation, abs=0.01)
    assert data["trackball"]["center"]["x"] == pytest.approx(layout.ball_center[0], abs=0.01)
    assert data["trackball"]["center"]["y"] == pytest.approx(layout.ball_center[1], abs=0.01)
