---
title: Boxy angular 3D printed case with raised controller box and ball pocket
type: feature
priority: P2
status: open
area: mech
created: 2026-11-05
---

# Boxy angular 3D printed case with raised controller box and ball pocket

## Context

Separate phase after the r2 hardware is frozen. Two-part printed case per half in the style of the
reference build (Keyball39ish-LP in a self-designed case): a flat, boxy tray whose walls follow the
stepped PCB outline from `hardware/layout/output/outline-left.dxf` and `outline-right.dxf` (90 degree
steps, no rounding), walls flush with the keycap skirts, a raised rectangular box over the
controller block at the inner edge (room for the controller on sockets, the 702025 cell on the
right half, the power switch slot, the reset hole, the USB-C opening and a window for the
controller LED), a 32 mm pocket beside the right PCB for the trackball module
(`mech-case-ball-pocket`), five M2 standoffs per half on the PCB holes, rubber feet.

## Acceptance criteria

- [ ] Parametric CAD in `hardware/case/` using the per-half layout outlines and the pocket data from `points-right.json`
- [ ] Both halves printable without supports (pocket well and controller box included)
- [ ] Controller box height: sockets 3.5 mm + controller 1.6 mm + USB-C shell, LED window on the inner wall
- [ ] Image prompts for renders in `docs/images/PROMPTS.md` (`img-case-concept` already describes the look)

## Notes

Blocked by hw-two-pcbs-r2 (final outlines) and mech-case-ball-pocket. Optional tenting feet later.
