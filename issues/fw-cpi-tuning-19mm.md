---
title: Tune CPI, scaling and scroll divisors for the 19 mm ball
type: task
priority: P2
status: open
area: fw
created: 2026-11-05
---

# Tune CPI, scaling and scroll divisors for the 19 mm ball

## Context

A 19.05 mm ball rotates about 1.3 times more per millimetre of finger travel than a 25 mm ball and
1.8 times more than a 34 mm Keyball ball, and it has almost no inertia (no flicks). Community
Keyball39 ZMK configs run 1200 CPI on 34 mm and some apply per-axis scaling because the sensor sees
the ball at an angle. The r2 default is `res-cpi = <600>` (r1 started at 400 for 25 mm); the real
value, the scroll divisor and the auto mouse layer movement threshold must be found on hardware.

## Acceptance criteria

- [ ] Default `res-cpi`, scroll tick and snipe CPI chosen on real hardware and recorded in the keymap
- [ ] Per-axis scaling checked (move the ball 10 cm along x and along y, counts should match)
- [ ] Auto mouse layer threshold checked against accidental palm contact with the lower ball
- [ ] `spec/05-firmware.md` tuning section updated

## Notes

Renamed from fw-cpi-tuning-25mm on 2026-11-06.

r2.4 (PAW3222 module tilted 65 degrees beside the ball): the sensor sees the ball 25 degrees
below the equator, so thumb motion across the tilt plane reaches it at only
cos 65 = 0.42 of the speed of motion along it. Since r2.4b the tilt plane is the layout x-z
plane (sensor towards +x): motion along it is screen X and arrives on the sensor's Y axis,
motion across it is screen Y on the sensor's X axis. The starting point is
`res-cpi = <1444>` with `zip_y_scaler 11 26` followed by the axis swap (`BALL_TILT` in
`k0d3ball35_right.overlay`), about 610 counts per inch on both axes. Check first whether the sensor's X axis really runs
across the tilt plane: if the cursor is fast up/down and slow sideways, move the scale to
`zip_x_scaler`. The driver only accepts multiples of 38 CPI between 608 and 4826.
