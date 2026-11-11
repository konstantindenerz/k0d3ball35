---
title: Ball-bottom-to-sensor stack height vs low profile
type: question
priority: P1
status: done
area: hw
created: 2026-11-05
---

# Ball-bottom-to-sensor stack height vs low profile

## Context

With the sensor directly below the ball (Keyball style) the stack under the ball is: ball bottom,
lens-to-ball gap 2.4 to 2.9 mm, LM18-LSI lens (about 3.4 mm above the sensor package reference plane),
PMW3610 package, 1.6 mm sensor PCB. The main PCB is 1.6 mm and the Choc switch top sits about 11 mm
above the PCB top, so a 25 mm ball whose centre sits at switch-top height already reaches 7 to 9 mm (r2: 19.05 mm ball, centre +7.6 mm, top +17.1 mm, module in a case pocket beside the PCB)
below the main PCB bottom. That is the tallest point of the case and defines its minimum height.
The reference build and torabo-tsuki-lp tilt or side-mount the sensor to keep the housing low.

## Acceptance criteria

- [ ] Stack drawing with real numbers (sensor datasheet, lens drawing, cradle wall) in `spec/08-trackball-module.md`
- [ ] Decision between (a) sensor straight below the ball on the case floor in a pocket beside the PCB (r2 choice, was: through the main PCB cutout), (b) sensor at 30 to 45 degrees beside the ball bottom, (c) ball raised with a taller cradle; recorded in the design spec
- [ ] Cradle parameters updated accordingly (mech-trackball-cradle)

## Notes

Option (b) lets the ball bottom sit almost on the case floor; the sensor sees the ball at an angle, which PixArt allows as long as the lens-to-surface distance holds at the optical axis.

Sensor angle (from spec/08 section 6, folded in here): decide between straight-up mounting (simplest; the cradle
default) and an angled mount once the cradle prototype exists. The tilted cradle variant was evaluated and only
pays off beyond 60 degrees (see mech-ball-height-23mm).

## The tolerance stack (r2.3 review, 2026-11-07)

The datasheet window is 2.2 / 2.4 / 2.6 mm, i.e. +-0.2 mm, and nothing in the design adjusts it: the
lens flange seats on a printed housing face and the ball floats on three 2.0 mm ceramic balls pressed
into printed radial seats.

The bearing seats are the sensitive term, and they amplify. The bearings sit `bearing_elev` = 35
degrees below the equator, so a radial protrusion error d moves the ball centre vertically by
d * cot(35) = **1.43 d**:

| bearing protrusion error | ball rises | resulting lens distance |
|--------------------------|-----------|-------------------------|
| +0.05 mm (half a layer)  | +0.07 mm  | 2.47 mm, inside |
| +0.10 mm                 | +0.14 mm  | 2.54 mm, 0.06 mm left |
| +0.15 mm                 | +0.21 mm  | **2.61 mm, out of spec** |

0.15 mm of radial error on an FDM-printed 1.9 mm seat is entirely plausible -- the README itself says
printed holes come out undersize and to ream them -- and it stacks with the printed housing face
(+-0.1 to 0.2 mm in z at 0.12 mm layers). The nominal 2.40 sits dead centre of the window with no
bias, while every realistic error pushes the distance up.

Mitigation, since the cradle is a print and reprinting is free: `lens_shim` in
`hardware/trackball-cradle/params.scad` (added 2026-11-07, default 0) shifts the sensor board along
the axis, positive away from the ball. Measure with the feeler gauge, set the difference, reprint. The
README acceptance window was tightened to 2.3 to 2.5 mm so there is room left when the real lens and a
second print disagree.

2026-11-11 (r2.4): closed. The stack no longer sits under the ball: the PAW3222 module is tilted
65 degrees beside it (`hw-paw3222-variant`) and the cup floor, not the sensor, sets the ball height.
Ball top 23.75 mm over the desk, keycaps 20.8 (`spec/08-trackball-module.md`). The tolerance stack
above still applies along the tilted axis; `lens_shim` moves the module along it without raising the
ball. The print check moved to `mech-ball-height-23mm`.
