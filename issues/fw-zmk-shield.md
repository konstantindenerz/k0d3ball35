---
title: ZMK shield k0d3ball35 with trackball on the central half
type: feature
priority: P0
status: done
area: fw
created: 2026-11-05
---

# ZMK shield k0d3ball35 with trackball on the central half

## Context

ZMK config for the board per section 6 of the design spec: shield files, matrix transform, physical
layout, PMW3610 node on the right half using the upstream Zephyr driver, input listeners with
auto mouse layer, scroll and snipe processors, keymap with 8 layers, ZMK Studio enabled, pinned ZMK
revision, GitHub Actions build.

## Acceptance criteria

- [ ] `k0d3ball35_left` and `k0d3ball35_right` build for `nice_nano//zmk` in CI, plus `settings_reset`
- [ ] Pin assignments match the design spec table exactly
- [ ] Keymap documented in `spec/05-firmware.md` with flashing and pairing steps
- [ ] Sleep and idle timeouts set with battery life in mind

## Notes

2026-11-05: left, right and settings_reset build in Docker against the pinned ZMK commit; `scripts/check_pins.py` passes. Remaining items are tracked in fw-physical-layout-exact-coords, fw-battery-drain-measurement, fw-cursor-axis-verification, doc-zmk-yml-repo-url and fw-ball-motion-wake.
