# SPDX-License-Identifier: MIT
"""Geometry checks for the key layout (hardware/layout/k0d3ball35.yaml), both halves."""
from __future__ import annotations

import json
import math

import pytest
from shapely.geometry import Point

from k0d3.geometry import HALVES, REPO, check_layout, load_layout, rotated_box

SPEC_STAGGER = {0: 10.44, 1: 4.19, 2: 0.0, 3: 2.23, 4: 4.46}
THUMB_COLS = {"left": [2, 3, 4], "right": [2, 3]}


@pytest.fixture(scope="module", params=HALVES)
def layout(request):
    return load_layout(request.param)


def test_key_count(layout):
    assert sum(k.kind == "finger" for k in layout.keys) == 15
    assert [t.col for t in sorted(layout.thumbs, key=lambda k: k.col)] == THUMB_COLS[layout.half]
    assert len(layout.keys) == 15 + len(THUMB_COLS[layout.half])


def test_total_key_count():
    assert sum(len(load_layout(h).keys) for h in HALVES) == 35


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
    thumbs = sorted(layout.thumbs, key=lambda k: k.col)
    assert all(t.row == 3 for t in thumbs)
    assert [t.rotation for t in thumbs] == [0, 10, 20][: len(thumbs)]
    for a, b in zip(thumbs, thumbs[1:]):
        # Keyball39 arc pitch 21.63 mm scaled to the Choc pitch gives about 20.4 mm
        assert 19.5 <= math.dist((a.x, a.y), (b.x, b.y)) <= 21.0
        assert b.y > a.y  # inner thumb keys sit lower


def test_same_thumb_positions_on_both_halves():
    """The right half uses the two outer thumb keys at exactly the left half's positions."""
    left, right = load_layout("left"), load_layout("right")
    for t in right.thumbs:
        l = left.key(t.row, t.col)
        assert (l.x, l.y, l.rotation) == (t.x, t.y, t.rotation)


def test_check_layout_clean(layout):
    assert check_layout(layout) == []


def test_no_keycap_overlap(layout):
    caps = [(k.ref, layout.keycap_polygon(k)) for k in layout.keys]
    for i, (ra, pa) in enumerate(caps):
        for rb, pb in caps[i + 1:]:
            assert pa.intersection(pb).area < 0.01, f"{ra} overlaps {rb}"


def test_ball_only_on_the_right(layout):
    assert layout.has_ball == (layout.half == "right")
    assert (layout.cfg.get("fpc") is not None) == (layout.half == "right")


def test_cradle_clearance_and_pocket_outside_pcb():
    layout = load_layout("right")
    cradle = layout.cradle_polygon()
    tb = layout.cfg["trackball"]
    assert tb["ball_diameter"] == pytest.approx(19.05)
    need = tb["min_keycap_clearance"]
    assert need >= 1.0
    for k in layout.keys:
        assert layout.keycap_polygon(k).distance(cradle) >= need, k.ref
    # the cradle sits beside the PCB, inside the octagonal notch, never over copper
    assert not layout.outline.intersects(cradle)
    assert layout.outline.distance(cradle) >= tb["pocket"]["notch_clearance"] - 0.05
    ball = Point(*layout.ball_center).buffer(tb["ball_diameter"] / 2)
    assert not layout.outline.intersects(ball)


def test_outline_is_angular(layout):
    """Variant A: only straight edges, no arcs (few vertices), 90 degree steps on the finger block."""
    pts = list(layout.outline.exterior.coords)[:-1]
    assert len(pts) < 80, "outline looks rounded (too many vertices)"
    assert layout.cfg["outline"]["corner_radius"] == 0
    # every edge of the finger block (y < 40) is axis aligned
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        if max(y1, y2) < 40:
            assert math.isclose(x1, x2, abs_tol=0.01) or math.isclose(y1, y2, abs_tol=0.01), ((x1, y1), (x2, y2))


def test_outline_size(layout):
    b = layout.to_dict()["bounds"]
    assert 100 <= b["width"] <= 125
    assert 75 <= b["height"] <= 90
    assert layout.outline.is_valid and layout.outline.geom_type == "Polygon"


def test_mounting_holes_clear(layout):
    for h in layout.cfg["mounting_holes"]:
        p = Point(h["x"], h["y"])
        assert layout.outline.exterior.distance(p) >= 2.0
        for k in layout.keys:
            body = rotated_box(k.x, k.y, layout.cfg["switch_body"], layout.cfg["switch_body"], k.rotation)
            assert body.distance(p) >= 0.9, (h, k.ref)


def test_points_json_up_to_date(layout):
    path = REPO / "hardware" / "layout" / "output" / f"points-{layout.half}.json"
    if not path.exists():
        pytest.skip("points not generated yet (run scripts/gen_layout.py)")
    data = json.loads(path.read_text())
    assert data["half"] == layout.half
    assert len(data["keys"]) == len(layout.keys)
    by_cell = {(k["row"], k["col"]): k for k in data["keys"]}
    for k in layout.keys:
        j = by_cell[(k.row, k.col)]
        assert j["x"] == pytest.approx(k.x, abs=0.01)
        assert j["y"] == pytest.approx(k.y, abs=0.01)
        assert j["rotation"] == pytest.approx(k.rotation, abs=0.01)
    if layout.has_ball:
        assert data["trackball"]["center"]["x"] == pytest.approx(layout.ball_center[0], abs=0.01)
        assert data["trackball"]["center"]["y"] == pytest.approx(layout.ball_center[1], abs=0.01)
        assert len(data["trackball"]["notch"]) == 9
    else:
        assert data["trackball"] is None


def test_housing_footprint_and_case_screws():
    """The cradle housing (30 x 29 on the case floor) is exported for the case and keeps clear of the FPC."""
    right, left = load_layout("right"), load_layout("left")
    assert left.housing_box() is None and left.case_screws() == []
    pk = right.cfg["trackball"]["pocket"]
    hb = right.housing_box()
    assert (hb.bounds[2] - hb.bounds[0], hb.bounds[3] - hb.bounds[1]) == (pk["housing"]["x"], pk["housing"]["y"])
    fp = right.housing_footprint()
    grow = 2 * (pk["housing_clearance"] + pk["wall"])
    assert fp.bounds[2] - fp.bounds[0] == pytest.approx(pk["housing"]["x"] + grow, abs=0.1)
    assert fp.bounds[3] - fp.bounds[1] == pytest.approx(pk["housing"]["y"] + grow, abs=0.1)
    s = right.case_screws()
    assert len(s) == 2 and s[0][0] == s[1][0] == right.ball_center[0]
    assert math.dist(s[0], s[1]) == pytest.approx(pk["case_screw_spacing"])
    assert hb.distance(right.fpc_box()) >= 0.5
    for k in right.keys:
        assert not rotated_box(k.x, k.y, right.cfg["switch_body"], right.cfg["switch_body"], k.rotation).intersects(hb), k.ref
    data = json.loads((REPO / "hardware" / "layout" / "output" / "points-right.json").read_text())
    assert len(data["trackball"]["case_screws"]) == 2
    assert len(data["trackball"]["housing_footprint"]) > 8


def test_battery_bay_identical_on_both_halves():
    left, right = load_layout("left"), load_layout("right")
    assert left.cfg["battery"] == right.cfg["battery"]
    assert left.battery_bay().equals(right.battery_bay())
    assert left.cfg["controller"]["socket_height"] <= 3.0


def test_battery_bay_fits_cell_and_board(layout):
    """The 702025 cell lies under the PCB below the controller: inside the outline, away from the
    edge, clear of everything assembled on the back and fully under the controller's footprint."""
    bay = layout.battery_bay()
    bat = layout.cfg["battery"]
    assert bat["cell"] == "LP552035"
    assert bat["bay"]["size"]["x"] - bat["size"]["x"] >= 0.5 and bat["bay"]["size"]["y"] - bat["size"]["y"] >= 1.0
    assert bat["size"]["z"] + 1.5 <= bat["depth_below_pcb"]
    assert layout.outline.contains(bay)
    assert layout.outline.exterior.distance(bay) >= bat["edge_clearance"] - 0.05
    for name, poly in layout.back_parts().items():
        assert not poly.intersects(bay), name
    c = layout.cfg["controller"]
    ctrl = rotated_box(c["center"]["x"], c["center"]["y"], c["size"]["x"], c["size"]["y"], 0, offset=(0, c["pcb_offset_y"]))
    assert ctrl.intersection(bay).area >= 0.5 * bay.area, "bay must lie mostly under the controller"
    inner = min(col["x"] for col in layout.cfg["columns"])
    assert bay.bounds[2] < inner - layout.cfg["switch_body"] / 2, "bay must stay clear of the inner column's switch holes"


def test_battery_bay_in_points_json(layout):
    path = REPO / "hardware" / "layout" / "output" / f"points-{layout.half}.json"
    if not path.exists():
        pytest.skip("points not generated yet (run scripts/gen_layout.py)")
    data = json.loads(path.read_text())
    bat = data["battery"]
    assert bat["cell"] == layout.cfg["battery"]["cell"]
    assert bat["well_floor_z"] == pytest.approx(-1.6 - layout.cfg["battery"]["depth_below_pcb"])
    assert len(bat["bay_polygon"]) == 5
    assert data["controller"]["socket_height"] == layout.cfg["controller"]["socket_height"]


def test_battery_bay_marked_on_both_pcbs(layout):
    pcb = REPO / "hardware" / f"{layout.half}-pcb" / f"k0d3ball35-{layout.half}.kicad_pcb"
    if not pcb.exists():
        pytest.skip("PCB not generated yet")
    text = pcb.read_text()
    assert f"{layout.cfg['battery']['cell']} cell" in text
    assert text.count('(layer "B.SilkS")') >= 4
