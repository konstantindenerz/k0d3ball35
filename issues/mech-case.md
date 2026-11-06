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
controller block at the inner edge (room for the controller on 2.5 mm sockets, the power switch
slot, the reset hole, the USB-C opening and a window for the controller LED; raising the box is
now a styling choice, the controller top is only +5.7 mm), a 9 mm deep battery well under the
controller block on both halves (`battery` block in `points-left.json` / `points-right.json`:
bay 21 x 28 mm centred (-58, 11), floor at -10.6 mm or the pocket level -11.6 mm, J3 at
(-56, 42) inside the same well), a 32 mm pocket beside the right PCB for the trackball module
(`mech-case-ball-pocket`), five M2 standoffs per half on the PCB holes, rubber feet.

## Acceptance criteria

- [ ] Parametric CAD in `hardware/case/` using the per-half layout outlines and the pocket data from `points-right.json`
- [ ] Both halves printable without supports (pocket well and controller box included)
- [ ] Controller block: lid clears the controller top (+5.7 mm: 2.5 mm sockets + 1.6 mm PCB + 1.6 mm USB-C shell) by 1 mm, LED window on the inner wall
- [ ] Battery well under the controller block on both halves: 9.0 mm below the PCB underside over the bay rectangle plus J3, from `battery` in `points-*.json`
- [ ] Image prompts for renders in `docs/images/PROMPTS.md` (`img-case-concept` already describes the look)

## Notes

Blocked by hw-two-pcbs-r2 (final outlines) and mech-case-ball-pocket. Each half also gets a
removable lid that covers keys and ball for transport and attaches under the half as a foot
(`mech-case-lid`); the cradle has no ball retainer, so the lid is what keeps the ball in a bag.
Provide magnet pockets on the case top rim and floor for it.
