#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check that the ZMK shield uses the pins defined in docs/01-design-spec.md.

The PCB is reversible: the left half is the same board flipped, so the two
controller pin columns swap and each half has its own pin table. The spec
section 2 carries a "Right half" table and a "Left half" table; this script
parses both and compares them with the devicetree overlays. If the left table
is not in the spec yet, the values agreed with the hardware design are used
and a note is printed.

No Zephyr toolchain needed; devicetree is parsed with regular expressions.
Exit code 1 on any mismatch so the check can run in CI and pytest.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SPEC = ROOT / "docs" / "01-design-spec.md"
SHIELD = ROOT / "firmware" / "zmk-config" / "config" / "boards" / "shields" / "k0d3ball36"

# nice!nano v2: Pro Micro number -> (port, pin)
PRO_MICRO = {
    0: (0, 8), 1: (0, 6), 2: (0, 17), 3: (0, 20), 4: (0, 22), 5: (0, 24), 6: (1, 0),
    7: (0, 11), 8: (1, 4), 9: (1, 6), 10: (0, 9), 14: (1, 11), 15: (1, 13), 16: (0, 10),
    18: (1, 15), 19: (0, 2), 20: (0, 29), 21: (0, 31),
}

SIGNALS = [f"COL{i}" for i in range(5)] + [f"ROW{i}" for i in range(4)] + [
    "TB_SCLK", "TB_SDIO", "TB_NCS", "TB_MOT",
]

# Expected pin sets (Pro Micro numbers). Right = design spec, left = flipped board.
EXPECTED = {
    "right": dict(zip(SIGNALS, [4, 5, 6, 7, 8, 21, 20, 19, 18, 15, 16, 10, 14])),
    "left": dict(zip(SIGNALS, [19, 18, 15, 14, 16, 2, 3, 4, 5, 6, 8, 9, 7])),
}


def spec_tables() -> dict[str, dict[str, int]]:
    """Return {'right': {...}, 'left': {...}} parsed from spec section 2.

    A table belongs to the side named by the closest preceding heading or bold
    label containing "left half" / "right half"; a table before any such label is
    the right half (the primary design table).
    """
    tables: dict[str, dict[str, int]] = {"right": {}, "left": {}}
    side = "right"
    in_section = False
    for line in SPEC.read_text().splitlines():
        if line.startswith("## "):
            in_section = line.startswith("## 2.")
            continue
        if not in_section:
            continue
        low = line.lower()
        if "left half" in low and not low.startswith("|"):
            side = "left"
        elif "right half" in low and not low.startswith("|"):
            side = "right"
        m = re.match(r"\|\s*([A-Z_0-9]+)[^|]*\|\s*D(\d+)\s*\|", line)
        if m and m.group(1) in SIGNALS:
            tables[side][m.group(1)] = int(m.group(2))
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


def main() -> int:
    errors: list[str] = []
    notes: list[str] = []

    spec = spec_tables()
    for side in ("right", "left"):
        if not spec[side]:
            notes.append(f"spec has no '{side} half' pin table yet; using the agreed hardware values")
            continue
        for sig in SIGNALS:
            if sig in spec[side] and spec[side][sig] != EXPECTED[side][sig]:
                errors.append(f"spec {side} {sig}=D{spec[side][sig]} disagrees with agreed value D{EXPECTED[side][sig]}")

    dtsi = (SHIELD / "k0d3ball36.dtsi").read_text()
    overlays = {
        "right": strip_comments((SHIELD / "k0d3ball36_right.overlay").read_text()),
        "left": strip_comments((SHIELD / "k0d3ball36_left.overlay").read_text()),
    }

    if "row-gpios" in strip_comments(dtsi) or "col-gpios" in strip_comments(dtsi):
        errors.append("kscan GPIOs must live in the per-side overlays, not in k0d3ball36.dtsi")

    for side, text in overlays.items():
        want = EXPECTED[side]
        rows = [want[f"ROW{i}"] for i in range(4)]
        cols = [want[f"COL{i}"] for i in range(5)]
        if dts_gpios(text, "row-gpios") != rows:
            errors.append(f"{side} row-gpios {dts_gpios(text, 'row-gpios')} != {rows}")
        if dts_gpios(text, "col-gpios") != cols:
            errors.append(f"{side} col-gpios {dts_gpios(text, 'col-gpios')} != {cols}")

    # Sensor: active only on the right half in r1
    right = overlays["right"]
    want = EXPECTED["right"]
    for func, sig in (("SPIM_SCK", "TB_SCLK"), ("SPIM_MOSI", "TB_SDIO"), ("SPIM_MISO", "TB_SDIO")):
        if psel(right, func) != PRO_MICRO[want[sig]]:
            errors.append(f"right {func} {psel(right, func)} != {PRO_MICRO[want[sig]]}")
    if gpio_ref(right, "cs-gpios") != PRO_MICRO[want["TB_NCS"]]:
        errors.append(f"right cs-gpios {gpio_ref(right, 'cs-gpios')} != {PRO_MICRO[want['TB_NCS']]}")
    if gpio_ref(right, "motion-gpios") != PRO_MICRO[want["TB_MOT"]]:
        errors.append(f"right motion-gpios {gpio_ref(right, 'motion-gpios')} != {PRO_MICRO[want['TB_MOT']]}")

    # The documented left-ball pin set (inside comments) must also be correct
    left_raw = (SHIELD / "k0d3ball36_left.overlay").read_text()
    want = EXPECTED["left"]
    for func, sig in (("SPIM_SCK", "TB_SCLK"), ("SPIM_MOSI", "TB_SDIO")):
        if psel(left_raw, func) != PRO_MICRO[want[sig]]:
            errors.append(f"left-ball {func} {psel(left_raw, func)} != {PRO_MICRO[want[sig]]}")
    if gpio_ref(left_raw, "cs-gpios") != PRO_MICRO[want["TB_NCS"]]:
        errors.append(f"left-ball cs-gpios != {PRO_MICRO[want['TB_NCS']]}")
    if gpio_ref(left_raw, "motion-gpios") != PRO_MICRO[want["TB_MOT"]]:
        errors.append(f"left-ball motion-gpios != {PRO_MICRO[want['TB_MOT']]}")

    if "col-offset = <5>" not in right:
        errors.append("right overlay must set col-offset = <5>")
    if dtsi.count("RC(") != 36:
        errors.append(f"matrix transform has {dtsi.count('RC(')} cells, expected 36")
    layouts = (SHIELD / "k0d3ball36-layouts.dtsi").read_text()
    if layouts.count("&key_physical_attrs") != 36:
        errors.append("physical layout must list 36 keys")

    for n in notes:
        print("NOTE:", n)
    for e in errors:
        print("MISMATCH:", e)
    if not errors:
        print("pins match docs/01-design-spec.md (right and left half)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
