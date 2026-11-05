---
title: Sensor PCB must match the cradle geometry
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Sensor PCB must match the cradle geometry

## Context

The cradle (`hardware/trackball-cradle/cradle.scad`) fixes how the sensor board mounts: optical centre of the
PMW3610 at the board centre, two M2 holes 20 mm apart along the 25 mm axis, the lens along the 26 mm side
(the board came out 26 x 25 mm, see mech-cradle-sensor-26mm), FPC connector and anything taller than 3.4 mm on the pin side only. The main PCB underside must stay
free within a 40 mm circle around the ball centre for the flange.

## Acceptance criteria

- [ ] hardware/sensor-pcb outline, holes and lens orientation match the cradle parameters
- [ ] Main PCB has no bottom-side parts within 20 mm of the ball centre (only the socket of SW32 is close; check)
- [ ] tests/test_geometry.py checks the 40 mm flange circle against bottom-side parts

## Notes

Cradle preview and stack numbers in `hardware/trackball-cradle/`.
