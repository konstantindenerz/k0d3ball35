---
title: Ball-bottom-to-sensor stack height vs low profile
type: question
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Ball-bottom-to-sensor stack height vs low profile

## Context

With the sensor directly below the ball (Keyball style) the stack under the ball is: ball bottom,
lens-to-ball gap 2.4 to 2.9 mm, LM18-LSI lens (about 3.4 mm above the sensor package reference plane),
PMW3610 package, 1.6 mm sensor PCB. The main PCB is 1.6 mm and the Choc switch top sits about 11 mm
above the PCB top, so a 25 mm ball whose centre sits at switch-top height already reaches 7 to 9 mm
below the main PCB bottom. That is the tallest point of the case and defines its minimum height.
The reference build and torabo-tsuki-lp tilt or side-mount the sensor to keep the housing low.

## Acceptance criteria

- [ ] Stack drawing with real numbers (sensor datasheet, lens drawing, cradle wall) in `docs/08-trackball-module.md`
- [ ] Decision between (a) sensor straight below the ball through the main PCB cutout, (b) sensor at 30 to 45 degrees beside the ball bottom, (c) ball raised with a taller cradle; recorded in the design spec
- [ ] Cradle parameters updated accordingly (mech-trackball-cradle)

## Notes

Option (b) lets the ball bottom sit almost on the case floor; the sensor sees the ball at an angle, which PixArt allows as long as the lens-to-surface distance holds at the optical axis.
