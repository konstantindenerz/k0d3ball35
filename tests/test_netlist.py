# SPDX-License-Identifier: MIT
"""Electrical model checks: matrix, controller holes, connectors, against docs/01-design-spec.md."""
from __future__ import annotations

import re
from collections import Counter, defaultdict

import pytest

from k0d3.footprints import all_footprints
from k0d3.geometry import REPO, load_layout
from k0d3.netlist import FPC_PINS, HOLE_NET, HOLE_PIN_LEFT, HOLE_PIN_RIGHT, JUMPERS, build_components, net_names

SPEC = REPO / "docs" / "01-design-spec.md"


@pytest.fixture(scope="module")
def comps():
    return build_components(load_layout())


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
    """Signal -> Pro Micro pin from the first (right half) controller pin table."""
    text = SPEC.read_text()
    sec = text.split("## 2.")[1].split("## 3.")[0]
    table = _spec_tables(sec)[0]
    out = {}
    for row in table[1:]:
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


def test_switch_and_diode_counts(comps):
    assert sum(c.kind == "switch" for c in comps) == 18
    assert sum(c.kind == "diode" for c in comps) == 18


def test_matrix_pads(comps):
    for c in comps:
        if c.kind == "switch":
            r, col = c.extra["row"], c.extra["col"]
            assert c.pads == {"1": f"COL{col}", "2": f"SW{r}{col}"}, c.ref
        if c.kind == "diode":
            r, col = c.extra["row"], c.extra["col"]
            assert c.pads == {"1": f"ROW{r}", "2": f"SW{r}{col}"}, c.ref


def test_switch_nets_have_switch_and_diode(comps):
    members = defaultdict(list)
    for c in comps:
        for pad, net in c.pads.items():
            if net.startswith("SW"):
                members[net].append(c.kind)
    assert len(members) == 18
    for net, kinds in members.items():
        assert sorted(kinds) == ["diode", "switch"], net


def test_controller_holes_match_spec(comps):
    spec = _spec_pin_table()
    assert spec, "could not parse the pin table in the design spec"
    hole_by_net = {net: hole for hole, net in HOLE_NET.items()}
    for signal, pin in spec.items():
        assert signal in hole_by_net, signal
        assert HOLE_PIN_RIGHT[hole_by_net[signal]] == pin, f"{signal}: spec {pin}, copper {HOLE_PIN_RIGHT[hole_by_net[signal]]}"
    u1 = next(c for c in comps if c.ref == "U1")
    assert u1.pads == {str(h): n for h, n in HOLE_NET.items()}
    assert len(u1.pads) == 24


def test_left_half_pin_swap():
    for h in range(1, 25):
        other = h + 12 if h <= 12 else h - 12
        assert HOLE_PIN_LEFT[h] == HOLE_PIN_RIGHT[other]
    assert HOLE_PIN_LEFT[7] == "D19" and HOLE_PIN_LEFT[17] == "D2"


def test_d0_grounded_and_jumpers():
    assert HOLE_NET[2] == "GND" and HOLE_NET[14] == "GND"
    assert [(j[2], j[3]) for j in JUMPERS] == [(1, 13), (3, 15), (4, 16)]
    assert [j[1] for j in JUMPERS] == ["RAW", "RST", "VCC"]


def test_jumper_components(comps):
    for ref, net, h1, h3 in JUMPERS:
        jp = next(c for c in comps if c.ref == ref)
        assert jp.pads == {"1": HOLE_NET[h1], "2": net, "3": HOLE_NET[h3]}


def test_fpc_pin_order_matches_spec(comps):
    spec = _spec_fpc_table()
    assert spec == {1: "VCC 3.3 V", 2: "GND", 3: "TB_SCLK", 4: "TB_SDIO", 5: "TB_NCS", 6: "TB_MOT"}
    assert FPC_PINS == {1: "VCC", 2: "GND", 3: "TB_SCLK", 4: "TB_SDIO", 5: "TB_NCS", 6: "TB_MOT"}
    j1 = next(c for c in comps if c.ref == "J1")
    assert j1.pads == {str(p): n for p, n in FPC_PINS.items()}


def test_power_path(comps):
    ps = next(c for c in comps if c.kind == "power_switch")
    assert ps.pads["2"] == "BAT+" and ps.pads["1"] == "RAW" and ps.pads["3"] == ""
    for ref in ("J2", "J3"):
        bat = next(c for c in comps if c.ref == ref)
        assert bat.pads == {"1": "BAT+", "2": "GND"}
    rb = next(c for c in comps if c.kind == "reset")
    assert rb.pads == {"1": "RST", "2": "GND"}


def test_every_net_has_two_pads(comps):
    count = Counter()
    for c in comps:
        for net in c.pads.values():
            if net:
                count[net] += 1
    for net in net_names(comps):
        assert count[net] >= 2, net


def test_unique_references(comps):
    refs = [c.ref for c in comps]
    assert len(refs) == len(set(refs))
    assert all(re.match(r"^[A-Z]+\d+$", r) for r in refs), [r for r in refs if not re.match(r"^[A-Z]+\d+$", r)]


def test_footprints_exist(comps):
    fps = all_footprints(HOLE_PIN_RIGHT, HOLE_PIN_LEFT)
    for c in comps:
        assert c.footprint in fps, c.ref
        fp_pads = {p.number for p in fps[c.footprint].pads if p.number}
        assert set(c.pads) <= fp_pads, f"{c.ref}: pads {set(c.pads) - fp_pads} missing in {c.footprint}"
