# SPDX-License-Identifier: MIT
"""Electrical model checks per half: matrix, controller holes, connectors, against spec/01-design-spec.md."""
from __future__ import annotations

import re
from collections import Counter, defaultdict

import pytest

from k0d3.footprints import all_footprints
from k0d3.geometry import HALVES, REPO, load_layout
from k0d3.netlist import FPC_PINS, HOLE_PIN, build_components, hole_net, net_names, spare_pad_nets

SPEC = REPO / "spec" / "01-design-spec.md"
KEYS = {"left": 18, "right": 17}
THUMB_COLS = {"left": [2, 3, 4], "right": [3, 4]}   # r2.3: the ball takes the outer position


@pytest.fixture(scope="module", params=HALVES)
def half(request):
    return request.param


@pytest.fixture(scope="module")
def comps(half):
    return build_components(load_layout(half))


def _spec_tables(text: str) -> list[list[list[str]]]:
    tables, cur = [], []
    for line in text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            cur.append(cells)
        elif cur:
            tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    return tables


def _spec_pin_table() -> dict[str, str]:
    """Signal -> Pro Micro pin from the single controller pin table (section 2 of the spec)."""
    text = SPEC.read_text()
    sec = text.split("## 2.")[1].split("## 3.")[0]
    tables = _spec_tables(sec)
    if len(tables) != 1 or re.search(r"\*\*Left half\*\*", sec):
        pytest.skip("spec/01-design-spec.md section 2 still has the r1 two-table pin layout; "
                    "r2 expects one pin table valid for both halves")
    out = {}
    for row in tables[0][1:]:
        signal, pin = row[0], row[1]
        m = re.match(r"(COL\d|ROW\d|TB_\w+)", signal)
        if m:
            out[m.group(1)] = pin
    return out


def _spec_fpc_table() -> dict[int, str]:
    text = SPEC.read_text()
    sec = text.split("## 3.")[1].split("## 4.")[0]
    table = _spec_tables(sec)[0]
    return {int(row[0]): row[1] for row in table[1:]}


def test_switch_and_diode_counts(half, comps):
    assert sum(c.kind == "switch" for c in comps) == KEYS[half]
    assert sum(c.kind == "diode" for c in comps) == KEYS[half]
    thumbs = sorted(c.extra["col"] for c in comps if c.kind == "switch" and c.extra["row"] == 3)
    assert thumbs == THUMB_COLS[half]


def test_matrix_pads(comps):
    for c in comps:
        if c.kind == "switch":
            r, col = c.extra["row"], c.extra["col"]
            assert c.pads == {"1": f"COL{col}", "2": f"SW{r}{col}"}, c.ref
        if c.kind == "diode":
            r, col = c.extra["row"], c.extra["col"]
            assert c.pads == {"1": f"ROW{r}", "2": f"SW{r}{col}"}, c.ref


def test_switch_nets_have_switch_and_diode(half, comps):
    members = defaultdict(list)
    for c in comps:
        for pad, net in c.pads.items():
            if net.startswith("SW"):
                members[net].append(c.kind)
    assert len(members) == KEYS[half]
    for net, kinds in members.items():
        assert sorted(kinds) == ["diode", "switch"], net


def test_hole_map_identical_matrix_and_power():
    """Both halves use the same controller pins; only the four sensor holes differ."""
    left, right = hole_net("left"), hole_net("right")
    assert set(left) == set(right) == set(range(1, 25))
    for h in range(1, 21):
        assert left[h] == right[h], h
    assert [right[h] for h in (21, 22, 23, 24)] == ["TB_SCLK", "TB_MOT", "TB_SDIO", "TB_NCS"]
    assert [left[h] for h in (21, 22, 23, 24)] == ["TP_D15", "TP_D14", "TP_D16", "TP_D10"]
    assert {right[h] for h in (3, 4, 14)} == {"GND"}
    assert right[13] == "RAW" and right[15] == "RST" and right[16] == "VCC"
    assert right[1] == "TP_D1" and right[2] == "TP_D0", "D0 and D1 are free again (no grounded D0)"
    assert [right[h] for h in range(7, 12)] == [f"COL{i}" for i in range(5)]
    assert [right[h] for h in range(17, 21)] == [f"ROW{i}" for i in range(4)]


def test_controller_holes_match_spec(half, comps):
    spec = _spec_pin_table()
    assert spec, "could not parse the pin table in the design spec"
    nets = hole_net(half)
    hole_by_net = {net: hole for hole, net in nets.items()}
    for signal, pin in spec.items():
        if signal.startswith("TB_") and half == "left":
            # the sensor pins are free on the left and broken out as test pads
            assert f"TP_{pin}" in hole_by_net, f"{signal} pin {pin} should be a test pad on the left"
            continue
        assert signal in hole_by_net, signal
        assert HOLE_PIN[hole_by_net[signal]] == pin, f"{signal}: spec {pin}, copper {HOLE_PIN[hole_by_net[signal]]}"
    u1 = next(c for c in comps if c.ref == "U1")
    assert u1.pads == {str(h): n for h, n in nets.items()}
    assert len(u1.pads) == 24


def test_test_pads(half, comps):
    tps = sorted((c for c in comps if c.kind == "testpoint"), key=lambda c: int(c.ref[2:]))
    want = spare_pad_nets(half)
    assert [c.pads["1"] for c in tps] == want
    assert len(tps) == (9 if half == "left" else 5)
    assert [c.ref for c in tps] == [f"TP{i + 1}" for i in range(len(tps))]
    hole_nets = set(hole_net(half).values())
    for c in tps:
        assert c.pads["1"] in hole_nets, c.ref
    layout = load_layout(half)
    tp_cfg = layout.cfg["test_pads"]
    for a, b in zip(tps, tps[1:]):
        if tp_cfg.get("direction", "y") == "x":   # the row runs along +x in the frame, mirrored on the left board
            assert b.x - a.x == pytest.approx(layout.board_sx * tp_cfg["pitch"]) and a.y == b.y
        else:
            assert b.y - a.y == pytest.approx(tp_cfg["pitch"]) and a.x == b.x


def test_fpc_only_on_the_right(half, comps):
    fpc = [c for c in comps if c.kind == "fpc"]
    if half == "right":
        assert [c.ref for c in fpc] == ["J1"]
        spec = _spec_fpc_table()
        assert spec == {1: "VCC 3.3 V", 2: "GND", 3: "TB_SCLK", 4: "TB_SDIO", 5: "TB_NCS", 6: "TB_MOT"}
        assert FPC_PINS == {1: "VCC", 2: "GND", 3: "TB_SCLK", 4: "TB_SDIO", 5: "TB_NCS", 6: "TB_MOT"}
        assert fpc[0].pads == {str(p): n for p, n in FPC_PINS.items()}
    else:
        assert fpc == []
        assert not any(n.startswith("TB_") for n in net_names(comps))


def test_no_jumpers_or_cradle_holes(comps):
    kinds = {c.kind for c in comps}
    assert "jumper" not in kinds and "cradle_hole" not in kinds
    assert not any(c.ref.startswith(("JP", "HB")) for c in comps)
    assert not any(n.startswith("MCU_") for n in net_names(comps))


def test_mounting_holes(half, comps):
    holes = [c for c in comps if c.kind == "hole"]
    assert len(holes) == len(load_layout(half).cfg["mounting_holes"])
    assert [c.ref for c in holes] == [f"H{i + 1}" for i in range(len(holes))]


def test_power_path(comps):
    ps = next(c for c in comps if c.kind == "power_switch")
    assert ps.pads["2"] == "BAT+" and ps.pads["1"] == "RAW" and ps.pads["3"] == ""
    for ref in ("J2", "J3"):
        bat = next(c for c in comps if c.ref == ref)
        assert bat.pads == {"1": "BAT+", "2": "GND"}
    rb = next(c for c in comps if c.kind == "reset")
    assert rb.pads == {"1": "RST", "2": "GND"}


def test_every_net_has_two_pads(half, comps):
    count = Counter()
    for c in comps:
        for net in c.pads.values():
            if net:
                count[net] += 1
    # VCC only feeds the sensor board, so on the left it ends at the controller hole
    single_ok = {"VCC"} if half == "left" else set()
    for net in net_names(comps):
        assert count[net] >= 2 or net in single_ok, net


def test_unique_references(comps):
    refs = [c.ref for c in comps]
    assert len(refs) == len(set(refs))
    assert all(re.match(r"^[A-Z]+\d+$", r) for r in refs), [r for r in refs if not re.match(r"^[A-Z]+\d+$", r)]


def test_footprints_exist(comps):
    fps = all_footprints(HOLE_PIN)
    for c in comps:
        assert c.footprint in fps, c.ref
        fp_pads = {p.number for p in fps[c.footprint].pads if p.number}
        assert set(c.pads) <= fp_pads, f"{c.ref}: pads {set(c.pads) - fp_pads} missing in {c.footprint}"
