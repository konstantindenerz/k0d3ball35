---
title: Tune CPI, scaling and scroll divisors for the 25 mm ball
type: task
priority: P2
status: open
area: fw
created: 2026-11-05
---

# Tune CPI, scaling and scroll divisors for the 25 mm ball

## Context

A 25 mm ball rotates about 1.36 times more per millimetre of finger travel than a 34 mm ball.
Community Keyball39 ZMK configs run 1200 CPI on 34 mm and some apply per-axis scaling because the
sensor sees the ball at an angle. The r1 default is 400 CPI; the real value must be found on hardware.

## Acceptance criteria

- [ ] Default `res-cpi`, scroll tick and snipe CPI chosen on real hardware and recorded in the keymap
- [ ] Per-axis scaling checked (move the ball 10 cm along x and along y, counts should match)
- [ ] `docs/05-firmware.md` tuning section updated

## Notes

None yet.
