---
title: Left half uses the mirrored controller pins
type: task
priority: P1
status: done
area: fw
created: 2026-11-05
---

# Left half uses the mirrored controller pins

## Context

The main PCB is reversible and the controller footprint is a plain 2x12 through-hole pattern. Flipping the board
swaps the two Pro Micro pin columns, so the same copper lines see different controller pins on the left half:
COL0..COL4 = D19, D18, D15, D14, D16 and ROW0..ROW3 = D2, D3, D4, D5. D0 is tied to GND on both halves and the
RAW, RST and VCC rows are selected with the solder jumpers JP1, JP2 and JP3.

## Acceptance criteria

- [x] `k0d3ball36_left.overlay` uses the mirrored pin set, rows and columns live in the per-side overlays
- [x] docs/01-design-spec.md section 2 lists both pin tables
- [x] `firmware/zmk-config/scripts/check_pins.py` verifies both halves

## Notes

Left-ball build would use TB_SCLK D6, TB_SDIO D8, TB_NCS D9, TB_MOT D7; a prepared block sits in the left overlay as a comment.
