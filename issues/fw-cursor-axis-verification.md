---
title: Verify trackball cursor axes on the first board
type: task
priority: P1
status: open
area: fw
created: 2026-11-05
---

# Verify trackball cursor axes on the first board

## Context

The axis mapping of the PAW3222 module (`BALL_TILT` in `k0d3ball35_right.overlay`: scale, swap, Y invert) is
derived from the cradle geometry and has never been seen on hardware. The sensor sits beside the ball towards
+x since r2.4b, so its fast axis is screen X and the axes are swapped (the overlay still had the +y maths
without a swap until the 2026-11-12 review). Which way the sensor's X and Y run on the module is an assumption:
the signs, and whether the scale belongs on Y or X, are decided on the first board.

## Acceptance criteria

- [ ] Cursor moves in the expected direction on the first assembled right half
- [ ] Overlay updated if needed, note added to spec/05-firmware.md

## Notes

Keyball community configs needed per-axis scaling because of ball/sensor geometry; check whether that applies here.
