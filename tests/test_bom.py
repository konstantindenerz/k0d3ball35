# SPDX-License-Identifier: MIT
"""docs/03-bom.md must cover every placed part with at least the placed quantity (both halves)."""
from __future__ import annotations

import re

import pytest

from k0d3.geometry import HALVES, REPO, load_layout
from k0d3.netlist import build_components

BOM = REPO / "docs" / "03-bom.md"


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
        pytest.skip("docs/03-bom.md has no parsable tables")
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
    assert _qty(rows, r"fpc connector|ffc connector") >= placed["fpc"] + 1 == 2  # right PCB + sensor PCB
    assert _qty(rows, r"lipo") >= 2
    assert _qty(rows, r"lipo.*552035") == 2, "one LP552035 cell per half, the same bay on both"
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


SENSOR_FAB_BOM = REPO / "hardware" / "sensor-pcb" / "fab" / "k0d3ball35-sensor-r1-bom.csv"


def test_sensor_bom_matches_fab_export():
    """Section 6 of docs/03-bom.md lists every LCSC code of the sensor board fab export with at
    least the exported quantity (summed over the rows that carry the code)."""
    import csv

    fab: dict[str, int] = {}
    with SENSOR_FAB_BOM.open(newline="") as f:
        for row in csv.DictReader(f):
            fab[row["LCSC"]] = fab.get(row["LCSC"], 0) + int(row["Quantity"])
    assert fab, "fab BOM is empty"

    text = BOM.read_text()
    start = text.index("## 6.")
    end = text.index("## 7.")
    section = text[start:end]
    docs: dict[str, int] = {}
    for row in _rows_from(section):
        m = re.search(r"\bC\d{3,}\b", row.get("lcsc", ""))
        if m:
            docs[m.group(0)] = docs.get(m.group(0), 0) + row["_qty"]
    missing = {code: qty for code, qty in fab.items() if docs.get(code, 0) < qty}
    assert not missing, f"docs/03-bom.md section 6 short of the fab export: {missing} (docs: {docs})"


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
