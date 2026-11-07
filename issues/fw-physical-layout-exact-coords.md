---
title: Regenerate the physical layout from the exact key coordinates
type: task
priority: P2
status: open
area: fw
created: 2026-11-05
---

# Regenerate the physical layout from the exact key coordinates

## Context

`k0d3ball35-layouts.dtsi` and the keymap-editor JSON were generated from the approximate coordinates in the design
spec. The layout generator now exports exact values in `hardware/layout/output/points-left.json` and `points-right.json` (35 keys since r2).

## Acceptance criteria

- [x] `firmware/zmk-config/scripts/gen_physical_layout.py` reads points-left.json and points-right.json
- [ ] dtsi and json regenerated, ZMK Studio shows the correct geometry
- [ ] Firmware builds in CI

## Notes

Rotation and position units differ between ZMK (hundredths of key units, rotation origin) and the generator (mm).

2026-11-07: `k0d3ball35-layouts.dtsi` did not parse. The generator prints the value of the `keys`
property only, and commit 242cbe3 pasted that output over the whole file, so the
`k0d3ball35_layout` node — the label `k0d3ball35.dtsi` points `zmk,physical-layout` at — was gone
and the file started with a bare `= <&key_physical_attrs ...>`. Every target failed with
`devicetree error: k0d3ball35-layouts.dtsi:14 (column 1): parse error: expected '/' or label
reference (&foo)`. Nothing caught it: `tests/test_firmware_pins.py` only asserted that the
generator output appears in the file, which a paste-over satisfies, and CI never got that far
because the west workspace failed first (`issues/infra-ci-firmware.md`).

The node is restored around the regenerated `keys` value, the file comment and
`spec/05-firmware.md` now say that the generator emits the property value and not the file, and
`test_physical_layout_matches_generator` additionally checks the `zmk,physical-layout` node, the
`keys` property, the label referenced from `k0d3ball35.dtsi` and balanced braces. Verified in
`zmkfirmware/zmk-build-arm:stable` on the pinned ZMK commit: all three targets build and write
`zmk.uf2` — right 276052 B flash / 73470 B RAM, left 190628 B / 37824 B, settings_reset
52508 B / 12840 B, matching the sizes recorded on 2026-11-06.
