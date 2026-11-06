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

- [ ] `firmware/zmk-config/scripts/gen_physical_layout.py` reads points-left.json and points-right.json
- [ ] dtsi and json regenerated, ZMK Studio shows the correct geometry
- [ ] Firmware builds in CI

## Notes

Rotation and position units differ between ZMK (hundredths of key units, rotation origin) and the generator (mm).
