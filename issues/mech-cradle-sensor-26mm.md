---
title: Update the cradle for the 26 x 25 mm sensor board
type: task
priority: P1
status: done
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

- [x] cradle.scad sensor pocket takes a 26 x 25 x 1.6 mm board, lens pocket oriented along the 26 mm side, holes unchanged
- [x] Lens-side PCB face sits 5.80 mm from the ball surface; stack.json regenerated and tests/test_cradle.py updated
- [x] Clearance for the FPC connector and passives on the component side (9.05 mm from the ball surface)
- [x] hardware/sensor-pcb/renders cross-checked against the printed pocket

## Notes

The sensor body protrudes 0.7 mm from the lens-side face; the lens base plate size is still an estimate (mech-lm18-lens-outline-measurement).

## Resolution (2026-11-05)

`params.scad` now carries `sensor_pcb_w = 26` (lens axis) and `sensor_pcb_l = 25` (hole axis); the pocket is 24 x 23 mm,
3.8 mm deep, holes unchanged at 20 mm. Stack from the ball surface: lens flange 2.40, lens-side PCB face 5.80,
component side 7.40, sensor top 9.05 mm; the component side faces the open side of the housing, so the FPC connector
has free clearance. Ball top stays at 23.05 mm above the main PCB; housing reach grows from 13 to 15 mm from the axis.
The tilted-sensor variant no longer gains any height with the wider board and stays documented as not recommended.
STL, DXF, previews and `stack.json` regenerated, `tests/test_cradle.py` passes.
