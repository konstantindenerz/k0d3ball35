# SPDX-License-Identifier: MIT
"""spec/03-bom.md must cover every placed part with at least the placed quantity (both halves)."""
from __future__ import annotations

import re

import pytest

from k0d3.geometry import HALVES, REPO, load_layout
from k0d3.netlist import build_components

BOM = REPO / "spec" / "03-bom.md"


def _rows() -> list[dict]:
    rows, header = [], None
    for line in BOM.read_text().splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        row = dict(zip(header, cells))
        m = re.match(r"\s*(\d+)", row.get("qty", ""))
        row["_qty"] = int(m.group(1)) if m else 0
        row["_text"] = " ".join(cells).lower()
        rows.append(row)
    return rows


@pytest.fixture(scope="module")
def rows():
    r = _rows()
    if not r:
        pytest.skip("spec/03-bom.md has no parsable tables")
    return r


def _qty(rows, *patterns) -> int:
    total = 0
    for row in rows:
        if all(re.search(p, row["_text"]) for p in patterns):
            total += row["_qty"]
    return total


@pytest.fixture(scope="module")
def placed():
    """Component counts summed over the left and the right PCB (one keyboard)."""
    counts: dict[str, int] = {}
    for half in HALVES:
        for c in build_components(load_layout(half)):
            counts[c.kind] = counts.get(c.kind, 0) + 1
    return counts


def test_placed_counts_per_half():
    left = [c.kind for c in build_components(load_layout("left"))]
    right = [c.kind for c in build_components(load_layout("right"))]
    assert left.count("switch") == 18 and right.count("switch") == 17
    assert left.count("fpc") == 0 and right.count("fpc") == 1
    assert "jumper" not in left and "jumper" not in right


def test_bom_covers_placed_parts(rows, placed):
    assert placed["switch"] == 35
    assert _qty(rows, r"hot-swap socket|hotswap socket") >= placed["switch"]
    assert _qty(rows, r"choc v1 switch") >= placed["switch"]
    assert _qty(rows, r"keycap") >= placed["switch"]
    assert _qty(rows, r"1n4148w") >= placed["diode"] == 35
    assert _qty(rows, r"nice!nano") >= placed["mcu"] == 2
    assert _qty(rows, r"msk-?12c02") >= placed["power_switch"] == 2
    assert _qty(rows, r"reset button") >= placed["reset"] == 2
    assert _qty(rows, r"fpc connector|ffc connector") >= placed["fpc"] + 1 == 2  # the right PCB's J1 plus a spare
    assert _qty(rows, r"lipo") >= 2
    # one cell per half, each the one the layout names for that half (the left one lies under
    # the inner column's sockets and is thinner)
    from k0d3.geometry import load_layout
    for h in ("left", "right"):
        cell = load_layout(h).cfg["battery"]["cell"]
        assert _qty(rows, rf"lipo.*{cell[2:]}") == 1, f"the BOM must list one {cell} for the {h} half"
    assert not any(re.search(r"301230", r.get("part", "")) and r["_qty"] for r in rows), "the 301230 does not fit the bay"
    assert _qty(rows, r"bearing ball|zirconia|zro2") >= 3
    assert _qty(rows, r"ball 19\.05 mm|19\.05 mm ball|3/4 inch") >= 1
    assert _qty(rows, r"jst s2b-ph|s2b-ph-sm4") >= 2
    assert _qty(rows, r"left pcb") >= 1 and _qty(rows, r"right pcb") >= 1
    assert not any(re.search(r"solder jumper", r.get("part", "").lower()) and r["_qty"] for r in rows)


GENERIC = re.compile(r"screw|standoff|spacer|bumper|flux|solder wick|shipping", re.I)


def test_bom_rows_have_source(rows):
    missing = [r["part"] for r in rows
               if r["_qty"] and not GENERIC.search(r["part"])
               and not re.search(r"https?://|mouser|lcsc|reichelt|aliexpress|amazon|jlcpcb|with the|hardware store|printed on pcb", r["_text"])]
    assert not missing, f"BOM rows without a source: {missing}"


def test_bom_connector_part_matches_pcb(rows):
    """The right PCB uses the Hirose FH12-6S-0.5SH footprint; the BOM must name a compatible part."""
    text = " ".join(r["_text"] for r in rows)
    assert re.search(r"fh12-6s|fh12", text), "BOM does not mention the FH12-6S-0.5SH connector used on the PCB"


# r2.4: test_sensor_bom_matches_fab_export is gone with its subject. It compared section 6 of
# spec/03-bom.md against hardware/sensor-pcb/fab/k0d3ball35-sensor-r1-bom.csv, the JLCPCB export
# of our own PMW3610 daughterboard. The sensor is now a bought PAW3222 module, so there is no
# second board, no fab BOM to export and no per-component LCSC list to keep in step: the module
# is one line in the BOM like the ball or the controller (issues/hw-paw3222-variant.md).


def _rows_from(markdown: str) -> list[dict]:
    rows, header = [], None
    for line in markdown.splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        row = dict(zip(header, cells))
        m = re.match(r"\s*(\d+)", row.get("qty", ""))
        row["_qty"] = int(m.group(1)) if m else 0
        rows.append(row)
    return rows
