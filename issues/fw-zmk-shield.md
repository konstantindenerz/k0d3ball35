---
title: ZMK shield k0d3ball36 with trackball on the central half
type: feature
priority: P0
status: in-progress
area: fw
created: 2026-11-05
---

# ZMK shield k0d3ball36 with trackball on the central half

## Context

ZMK config for the board per section 6 of the design spec: shield files, matrix transform, physical
layout, PMW3610 node on the right half using the upstream Zephyr driver, input listeners with
auto mouse layer, scroll and snipe processors, keymap with 8 layers, ZMK Studio enabled, pinned ZMK
revision, GitHub Actions build.

## Acceptance criteria

- [ ] `k0d3ball36_left` and `k0d3ball36_right` build for `nice_nano//zmk` in CI, plus `settings_reset`
- [ ] Pin assignments match the design spec table exactly
- [ ] Keymap documented in `docs/05-firmware.md` with flashing and pairing steps
- [ ] Sleep and idle timeouts set with battery life in mind

## Notes

None yet.
