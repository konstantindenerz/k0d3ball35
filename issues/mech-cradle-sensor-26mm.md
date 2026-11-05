---
title: Update the cradle for the 26 x 25 mm sensor board
type: task
priority: P1
status: open
area: mech
created: 2026-11-05
---

# Update the cradle for the 26 x 25 mm sensor board

## Context

The cradle (`hardware/trackball-cradle/cradle.scad`) was modelled for a 22 x 25 mm sensor board. The finished
sensor PCB is 26 x 25 mm: the 17 mm sensor body cutout needs a routing channel on each side. The two M2 holes stay
20 mm apart on the vertical 25 mm axis with the optical centre between them; the LM18-LSI lens runs along the
26 mm side (horizontal in `hardware/sensor-pcb/generate.py`, see the Dwgs.User lens envelope). Measured stack:
lens flange to ball surface 2.40 mm, PCB lens-side face to ball surface 5.80 mm, component-side face 7.40 mm,
tallest component 9.05 mm.

## Acceptance criteria

- [ ] cradle.scad sensor pocket takes a 26 x 25 x 1.6 mm board, lens pocket oriented along the 26 mm side, holes unchanged
- [ ] Lens-side PCB face sits 5.80 mm from the ball surface; stack.json regenerated and tests/test_cradle.py updated
- [ ] Clearance for the FPC connector and passives on the component side (9.05 mm from the ball surface)
- [ ] hardware/sensor-pcb/renders cross-checked against the printed pocket

## Notes

The sensor body protrudes 0.7 mm from the lens-side face; the lens base plate size is still an estimate (mech-lm18-lens-outline-measurement).
