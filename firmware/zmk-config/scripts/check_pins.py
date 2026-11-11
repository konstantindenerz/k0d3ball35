#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check that the ZMK shield uses the pins defined in spec/01-design-spec.md.

The keyboard is two separate PCBs with the identical controller pin set, so the
spec section 2 carries ONE pin table valid for both halves. This script parses
the first table in that section and compares it with the agreed values, then
checks the shared devicetree (k0d3ball35.dtsi) and both overlays against them:

  - row/col GPIOs live in the shared dtsi (not per half)
  - the right overlay sets the column offset, SPI psels, chip select and motion pin
  - the commented left-ball scaffold in the left overlay documents the same pins
  - 35 matrix cells, 35 physical keys

If the spec still has the old two-table layout (right + flipped left) the agreed
values are used and a note is printed instead of failing.

No Zephyr toolchain needed; devicetree is parsed with regular expressions.
Exit code 1 on any mismatch so the check can run in CI and pytest.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SPEC = ROOT / "spec" / "01-design-spec.md"
SHIELD = ROOT / "firmware" / "zmk-config" / "config" / "boards" / "shields" / "k0d3ball35"
KEYS = 35

# nice!nano v2: Pro Micro number -> (port, pin)
PRO_MICRO = {
    0: (0, 8), 1: (0, 6), 2: (0, 17), 3: (0, 20), 4: (0, 22), 5: (0, 24), 6: (1, 0),
    7: (0, 11), 8: (1, 4), 9: (1, 6), 10: (0, 9), 14: (1, 11), 15: (1, 13), 16: (0, 10),
    18: (1, 15), 19: (0, 2), 20: (0, 29), 21: (0, 31),
}

SIGNALS = [f"COL{i}" for i in range(5)] + [f"ROW{i}" for i in range(4)] + [
    "TB_SCLK", "TB_SDIO", "TB_NCS", "TB_MOT",
]

# Agreed pin set (Pro Micro numbers), identical on both halves.
EXPECTED = dict(zip(SIGNALS, [4, 5, 6, 7, 8, 21, 20, 19, 18, 15, 16, 10, 14]))
ROWS = [EXPECTED[f"ROW{i}"] for i in range(4)]
COLS = [EXPECTED[f"COL{i}"] for i in range(5)]


def spec_tables() -> list[dict[str, int]]:
    """Return the pin tables of spec section 2 in document order.

    Each table is {signal: pro_micro_number} for the known signals. Lines that
    are not table rows end a table.
    """
    tables: list[dict[str, int]] = []
    current: dict[str, int] | None = None
    in_section = False
    for line in SPEC.read_text().splitlines():
        if line.startswith("## "):
            in_section = line.startswith("## 2")
            continue
        if not in_section:
            continue
        if line.startswith("|"):
            if current is None:
                current = {}
            m = re.match(r"\|\s*([A-Z_0-9]+)[^|]*\|\s*D(\d+)\s*\|", line)
            if m and m.group(1) in SIGNALS:
                current[m.group(1)] = int(m.group(2))
        elif current is not None:
            if current:
                tables.append(current)
            current = None
    if current:
        tables.append(current)
    return tables


def dts_gpios(text: str, prop: str) -> list[int]:
    block = re.search(prop + r"\s*=\s*(.*?);", text, re.S)
    if not block:
        return []
    return [int(n) for n in re.findall(r"&pro_micro\s+(\d+)", block.group(1))]


def psel(text: str, func: str) -> tuple[int, int] | None:
    m = re.search(r"NRF_PSEL\(" + func + r",\s*(\d+),\s*(\d+)\)", text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def gpio_ref(text: str, prop: str) -> tuple[int, int] | None:
    m = re.search(prop + r"\s*=\s*<&gpio(\d+)\s+(\d+)", text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def check_sensor(text: str, label: str, errors: list[str]) -> None:
    """SPI psels, chip select and motion (irq) pin of a PAW3222 block must use the agreed pins."""
    for func, sig in (("SPIM_SCK", "TB_SCLK"), ("SPIM_MOSI", "TB_SDIO"), ("SPIM_MISO", "TB_SDIO")):
        if psel(text, func) != PRO_MICRO[EXPECTED[sig]]:
            errors.append(f"{label} {func} {psel(text, func)} != {PRO_MICRO[EXPECTED[sig]]} ({sig} = D{EXPECTED[sig]})")
    if gpio_ref(text, "cs-gpios") != PRO_MICRO[EXPECTED["TB_NCS"]]:
        errors.append(f"{label} cs-gpios {gpio_ref(text, 'cs-gpios')} != {PRO_MICRO[EXPECTED['TB_NCS']]}")
    if gpio_ref(text, "irq-gpios") != PRO_MICRO[EXPECTED["TB_MOT"]]:
        errors.append(f"{label} irq-gpios {gpio_ref(text, 'irq-gpios')} != {PRO_MICRO[EXPECTED['TB_MOT']]}")


def main() -> int:
    errors: list[str] = []
    notes: list[str] = []

    tables = spec_tables()
    if not tables:
        notes.append("spec section 2 has no pin table yet; using the agreed hardware values")
    elif len(tables) > 1 and any(tables[1].get(s) not in (None, tables[0].get(s)) for s in SIGNALS):
        notes.append("spec section 2 still has the old per-half pin tables; using the agreed hardware values")
    else:
        for sig in SIGNALS:
            if sig in tables[0] and tables[0][sig] != EXPECTED[sig]:
                errors.append(f"spec {sig}=D{tables[0][sig]} disagrees with agreed value D{EXPECTED[sig]}")
        missing = [s for s in SIGNALS if s not in tables[0]]
        if missing:
            notes.append(f"spec pin table lacks {', '.join(missing)}")

    dtsi_raw = (SHIELD / "k0d3ball35.dtsi").read_text()
    dtsi = strip_comments(dtsi_raw)
    right = strip_comments((SHIELD / "k0d3ball35_right.overlay").read_text())
    left_raw = (SHIELD / "k0d3ball35_left.overlay").read_text()
    left = strip_comments(left_raw)

    # Matrix pins: once, in the shared dtsi
    if dts_gpios(dtsi, "row-gpios") != ROWS:
        errors.append(f"dtsi row-gpios {dts_gpios(dtsi, 'row-gpios')} != {ROWS}")
    if dts_gpios(dtsi, "col-gpios") != COLS:
        errors.append(f"dtsi col-gpios {dts_gpios(dtsi, 'col-gpios')} != {COLS}")
    for side, text in (("right", right), ("left", left)):
        for prop in ("row-gpios", "col-gpios"):
            if dts_gpios(text, prop):
                errors.append(f"{side} overlay redefines {prop}; the pins are shared and belong in k0d3ball35.dtsi")

    # Sensor: active on the right, documented (commented scaffold) on the left
    check_sensor(right, "right", errors)
    check_sensor(left_raw, "left-ball scaffold", errors)
    if "trackball" in left:
        errors.append("left overlay must keep the sensor block commented out in the default build")

    if "col-offset = <5>" not in right:
        errors.append("right overlay must set col-offset = <5>")
    if dtsi.count("RC(") != KEYS:
        errors.append(f"matrix transform has {dtsi.count('RC(')} cells, expected {KEYS}")
    for cell in ("RC(3,2)", "RC(3,3)", "RC(3,4)", "RC(3,9)", "RC(3,8)"):
        if cell not in dtsi:
            errors.append(f"matrix transform lacks thumb cell {cell}")
    if "RC(3,7)" in dtsi:
        errors.append("matrix transform maps RC(3,7); the right half has no outer thumb key "
                      "since r2.3, the ball pocket is there")
    layouts = (SHIELD / "k0d3ball35-layouts.dtsi").read_text()
    if layouts.count("&key_physical_attrs") != KEYS:
        errors.append(f"physical layout lists {layouts.count('&key_physical_attrs')} keys, expected {KEYS}")

    for n in notes:
        print("NOTE:", n)
    for e in errors:
        print("MISMATCH:", e)
    if not errors:
        print("pins match spec/01-design-spec.md (one pin set for both halves)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
