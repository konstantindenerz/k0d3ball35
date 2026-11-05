---
title: Parametric 25 mm trackball cradle with ceramic ball seats
type: feature
priority: P0
status: done
area: mech
created: 2026-11-05
---

# Parametric 25 mm trackball cradle with ceramic ball seats

## Context

3D printed cradle holding the ball on three 2 mm ZrO2 ceramic balls at 120 degrees, with a pocket
for the sensor PCB giving a lens-to-ball distance of 2.4 to 2.9 mm, a retention lip so the ball does
not fall out when the half is lifted, and a flange screwed to the main PCB cradle holes. Parametric in
ball diameter (25 mm default, 34 mm option).

## Acceptance criteria

- [ ] OpenSCAD or CadQuery source in `hardware/trackball-cradle/` with ball diameter, bearing diameter, lens distance and wall thickness as parameters
- [ ] STL exported for 25 mm and 34 mm
- [ ] Printed test fit checklist in `docs/08-trackball-module.md` (ball spins freely, no wobble, sensor reads at the target distance)
- [ ] The cradle is the first part to print, before any PCB order

## Notes

Depends on hw-sensor-stack-height for the final sensor orientation.

2026-11-05: cradle.scad renders 25 mm and 34 mm variants, retainer ring, tilted variant evaluated; stack heights in stack.json. Ball height follow-up in mech-ball-height-23mm.
