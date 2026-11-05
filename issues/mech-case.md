---
title: Low profile 3D printed case with battery pocket and LED window
type: feature
priority: P2
status: open
area: mech
created: 2026-11-05
---

# Low profile 3D printed case with battery pocket and LED window

## Context

Separate phase after r1 hardware is frozen. Two-part printed case per half in the style of the
reference build: flat tray, walls flush with the switch plate height, pocket for a 702025 cell on the
trackball half, a window for the controller LED, cutouts for USB-C, power switch and reset, rubber
feet. Uses the DXF outline exported from the layout.

## Acceptance criteria

- [ ] Parametric CAD in `hardware/case/` using the layout outline
- [ ] Both halves printable without supports
- [ ] Image prompts for renders in `docs/images/PROMPTS.md`

## Notes

Blocked by hw-main-pcb-r1 and hw-sensor-stack-height.
