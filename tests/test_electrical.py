# SPDX-License-Identifier: MIT
"""The electrical side of the main PCBs: does the copper do what the circuit says.

The geometry tests ask whether the board can be made; these ask whether it will work. They
cross the three descriptions that have to agree and are written by different people at
different times - the netlist generator, the ZMK shield and the finished board - and they
check the few numbers a fab or a battery cares about.
"""
from __future__ import annotations

import json
import math

import pytest
from shapely.geometry import LineString, Point
from shapely.affinity import translate

from k0d3.geometry import HALVES, REPO, load_layout
from k0d3.netlist import FPC_PINS, build_components, hole_net, net_classes

from test_pcb_review import BOARDS, OFFSET, _load

SHIELD = REPO / "firmware" / "zmk-config" / "config" / "boards" / "shields" / "k0d3ball35"
SPEC = REPO / "docs" / "01-design-spec.md"


@pytest.fixture(scope="module", params=HALVES)
def half(request) -> str:
    return request.param


@pytest.fixture(scope="module")
def comps(half):
    return {c.ref: c for c in build_components(load_layout(half))}


@pytest.fixture(scope="module")
def board(half):
    if not BOARDS[half].exists():
        pytest.skip(f"{half} board not generated")
    return _load(half)


# ----------------------------------------------------------------- the matrix
def test_diode_direction_matches_the_firmware(comps, half):
    """Current runs column -> switch -> diode anode -> cathode -> row, so the scan is col2row.
    If the generator ever flips the diode, ZMK reads a transposed matrix and every key is
    wrong; nothing else in the build would notice."""
    for ref, c in comps.items():
        if c.kind != "switch":
            continue
        row, col = c.extra["row"], c.extra["col"]
        diode = comps[f"D{row}{col}"]
        assert c.pads["1"] == f"COL{col}", f"{ref}: switch pad 1 should carry the column"
        assert c.pads["2"] == ref, f"{ref}: switch pad 2 should carry the key node"
        assert diode.pads["2"] == ref, f"D{row}{col}: anode (pad 2) should sit on the key node"
        assert diode.pads["1"] == f"ROW{row}", f"D{row}{col}: cathode (pad 1) should carry the row"
    dtsi = (SHIELD / "k0d3ball35.dtsi").read_text()
    assert 'diode-direction = "col2row"' in dtsi, \
        "the copper scans col2row; the shield must say so"


def test_every_key_has_its_own_node_and_sits_on_one_row_and_column(comps, half):
    nodes = [c.pads["2"] for c in comps.values() if c.kind == "switch"]
    assert len(nodes) == len(set(nodes)), "two keys share a node: they would press together"
    rows = {c.pads["1"] for c in comps.values() if c.kind == "diode"}
    cols = {c.pads["1"] for c in comps.values() if c.kind == "switch"}
    assert rows <= {f"ROW{i}" for i in range(4)} and cols <= {f"COL{i}" for i in range(5)}


# ----------------------------------------------------------------- power
def test_the_battery_runs_through_the_switch_into_the_controller(comps, half):
    """Cell -> J2/J3 -> PS1 -> RAW. The switch has to sit in the positive line: in the ground
    line it would leave the cell tied to the controller's ground with the board off, and the
    nice!nano's charger expects the cell on RAW."""
    for ref in ("J2", "J3"):
        assert comps[ref].pads == {"1": "BAT+", "2": "GND"}, f"{ref}: battery polarity"
    ps = comps["PS1"].pads
    assert {ps["1"], ps["2"]} == {"RAW", "BAT+"}, "PS1 must switch the battery positive into RAW"
    assert ps["3"] == "", "the third SPDT pin stays open"
    assert hole_net(half)[13] == "RAW", "controller hole 13 is RAW"
    assert comps["RB1"].pads == {"1": "RST", "2": "GND"}, "reset button pulls RST to ground"
    spec = SPEC.read_text()
    assert "battery positive, through the power switch" in spec


def test_power_tracks_are_wide_enough_for_the_cell(board, half):
    """RAW and BAT+ carry the charge current of the nice!nano (up to about 100 mA) plus the
    peak draw of the radio. 0.4 mm of 35 um copper is good for roughly 1 A, so the class width
    is the thing to assert - and that it actually reached the board."""
    want = net_classes()["Power"]["track_width"]
    seen = {n: [] for n in ("RAW", "BAT+")}
    for layer, net, width, a, b in board.segments:
        if net in seen:
            seen[net].append(width)
    for net, widths in seen.items():
        assert widths, f"{half}: {net} has no copper"
        assert min(widths) >= want - 1e-6, f"{half}: {net} drops to {min(widths)} mm, class says {want}"


def test_no_track_is_thinner_than_the_fab_minimum(board, half):
    limit = json.loads(BOARDS[half].with_suffix(".kicad_pro").read_text())["board"]["design_settings"]["rules"]["min_track_width"]
    for layer, net, width, a, b in board.segments:
        assert width >= limit - 1e-6, f"{half}: {net} on {layer} is {width} mm, fab minimum is {limit}"


def test_every_track_is_at_least_as_wide_as_its_net_class(board, half):
    classes = net_classes()
    want = {}
    for name, c in classes.items():
        for n in c.get("nets", []):
            want[n] = c["track_width"]
    default = classes["Default"]["track_width"]
    for layer, net, width, a, b in board.segments:
        if net == "GND":            # the pour carries ground; its tracks are only stubs
            continue
        assert width >= want.get(net, default) - 1e-6, \
            f"{half}: {net} on {layer} is {width} mm, its class asks for {want.get(net, default)}"


# ----------------------------------------------------------------- sensor bus
def test_the_sensor_bus_fits_the_connector_pitch(half):
    """A track centred on an FH12 contact must still clear the neighbouring contact. With
    0.5 mm pitch and 0.3 mm pads: gap = 0.5 - w/2 - 0.15. At 0.25 mm that is 0.225 mm, above
    the 0.2 mm rule; at 0.3 mm it would be exactly at it and at 0.35 mm it would fail."""
    pitch, pad_w = 0.5, 0.3
    cls = net_classes()["FPC"]
    gap = pitch - cls["track_width"] / 2 - pad_w / 2
    assert gap >= cls["clearance"] - 1e-9, \
        f"a {cls['track_width']} mm track leaves {gap:.3f} mm to the next contact, rule is {cls['clearance']}"


def test_the_sensor_bus_carries_its_supply_and_a_ground_beside_the_clock(half):
    """Six conductors: the supply and its return at one end, then the three SPI lines, then the
    interrupt. The ground sits next to the clock, which is the only fast edge on the cable."""
    order = [FPC_PINS[i] for i in sorted(FPC_PINS)]
    assert order == ["VCC", "GND", "TB_SCLK", "TB_SDIO", "TB_NCS", "TB_MOT"], order
    assert abs(order.index("GND") - order.index("TB_SCLK")) == 1, "the return must sit beside the clock"
    assert abs(order.index("VCC") - order.index("GND")) == 1, "supply and return must be a pair"


# ----------------------------------------------------------------- ground
def test_every_ground_pad_reaches_the_pour(board, half):
    """Ground is poured, not routed. A GND pad the pour cannot reach would float: KiCad reports
    it as unconnected only after a fill, and a stale fill hides it."""
    fills = [poly for net, layer, polys in board.zones if net == "GND" for poly in polys]
    assert fills, f"{half}: no filled GND zone"
    tracks = [LineString([a, b]).buffer(w / 2) for layer, net, w, a, b in board.segments if net == "GND"]
    vias = [Point(x, y).buffer(s / 2) for net, x, y, s, _ in board.vias if net == "GND"]
    for ref, fp in board.footprints.items():
        for p in fp.pads:
            if not p.copper or p.net != "GND":
                continue
            poly = p.poly().buffer(0.05)
            assert any(poly.intersects(f) for f in fills) or any(poly.intersects(t) for t in tracks) \
                or any(poly.intersects(v) for v in vias), \
                f"{half}: {ref} pad {p.number} is on GND but touches neither pour, track nor via"


def test_the_controller_ground_pins_connect_solidly(board, half):
    """Thermal reliefs on the pins that carry the ground return of the whole half starve: four
    spokes of 0.5 mm are a worse connection than the pour itself. The GND holes get
    zone_connect 2, every other controller hole keeps its relief for hand soldering."""
    gnd_holes = [h for h, n in hole_net(half).items() if n == "GND"]
    assert gnd_holes == [3, 4, 14], gnd_holes
    from test_pcb_review import _kid, _kids, _parse, _s

    tree = _parse(BOARDS[half].read_text(encoding="utf-8"))
    u1 = next(fp for fp in _kids(tree, "footprint")
              if any(_s(pr[2]) == "U1" for pr in _kids(fp, "property") if _s(pr[1]) == "Reference"))
    solid = {int(_s(pad[1])) for pad in _kids(u1, "pad")
             if _kid(pad, "zone_connect") and _kid(pad, "zone_connect")[1] == "2"}
    assert solid == set(gnd_holes), f"{half}: solid pour connection on holes {sorted(solid)}, expected {gnd_holes}"
