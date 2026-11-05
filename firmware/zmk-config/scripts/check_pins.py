#!/usr/bin/env python3
"""Check that the ZMK shield uses the pins defined in docs/01-design-spec.md.

Parses the devicetree sources with regular expressions (no Zephyr toolchain
needed) and compares against the pin table in the design spec. Exit code 1 on
any mismatch so that the check can run in CI and pytest.
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


def spec_pins() -> dict[str, int]:
    """Signal name -> Pro Micro number from the spec table (rows like `| COL0 (pinky) | D4 | ...`)."""
    pins: dict[str, int] = {}
    for line in SPEC.read_text().splitlines():
        m = re.match(r"\|\s*([A-Z_0-9]+)[^|]*\|\s*D(\d+)\s*\|", line)
        if m:
            pins[m.group(1)] = int(m.group(2))
    return pins


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


def main() -> int:
    spec = spec_pins()
    errors: list[str] = []
    dtsi = (SHIELD / "k0d3ball36.dtsi").read_text()
    right = (SHIELD / "k0d3ball36_right.overlay").read_text()
    left = (SHIELD / "k0d3ball36_left.overlay").read_text()

    want_rows = [spec[f"ROW{i}"] for i in range(4)]
    want_cols = [spec[f"COL{i}"] for i in range(5)]
    if dts_gpios(dtsi, "row-gpios") != want_rows:
        errors.append(f"row-gpios {dts_gpios(dtsi, 'row-gpios')} != spec {want_rows}")
    for name, text in (("left", left), ("right", right)):
        if dts_gpios(text, "col-gpios") != want_cols:
            errors.append(f"{name} col-gpios {dts_gpios(text, 'col-gpios')} != spec {want_cols}")

    checks = {
        "SPIM_SCK": PRO_MICRO[spec["TB_SCLK"]],
        "SPIM_MOSI": PRO_MICRO[spec["TB_SDIO"]],
        "SPIM_MISO": PRO_MICRO[spec["TB_SDIO"]],
    }
    for func, want in checks.items():
        got = psel(right, func)
        if got != want:
            errors.append(f"{func} {got} != spec {want}")
    if gpio_ref(right, "cs-gpios") != PRO_MICRO[spec["TB_NCS"]]:
        errors.append(f"cs-gpios {gpio_ref(right, 'cs-gpios')} != spec {PRO_MICRO[spec['TB_NCS']]}")
    if gpio_ref(right, "motion-gpios") != PRO_MICRO[spec["TB_MOT"]]:
        errors.append(f"motion-gpios {gpio_ref(right, 'motion-gpios')} != spec {PRO_MICRO[spec['TB_MOT']]}")

    if "col-offset = <5>" not in right:
        errors.append("right overlay must set col-offset = <5>")
    if dtsi.count("RC(") != 36:
        errors.append(f"matrix transform has {dtsi.count('RC(')} cells, expected 36")
    layouts = (SHIELD / "k0d3ball36-layouts.dtsi").read_text()
    if layouts.count("&key_physical_attrs") != 36:
        errors.append("physical layout must list 36 keys")

    for e in errors:
        print("MISMATCH:", e)
    if not errors:
        print("pins match docs/01-design-spec.md")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
