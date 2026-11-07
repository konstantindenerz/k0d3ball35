---
title: D0 (P0.08) is tied to GND on both halves
type: task
priority: P3
status: wontfix
area: hw
created: 2026-11-05
---

# D0 (P0.08) is tied to GND on both halves

## Context

Row 2 of the Pro Micro footprint holds D0 on one column and GND on the other. Because the board is reversible,
both holes are connected to GND so that one GND pin is always connected without a jumper. D0 is therefore
unusable on both halves.

## Acceptance criteria

- [x] Documented in spec/01-design-spec.md and the shield README
- [x] Firmware never configures P0.08

## Notes

Harmless for the nRF52840 as long as the pin stays an input without pull-up.

2026-11-06: obsolete. r2 uses two separate PCBs with identical controller wiring; D0 goes to a test
pad and is free again on both halves (`hw-two-pcbs-r2`). Closed as wontfix because the r1 reversible
board that needed this no longer exists.
