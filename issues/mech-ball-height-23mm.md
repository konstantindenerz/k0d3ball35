---
title: Ball sits 23 mm above the main PCB with the sensor straight below
type: question
priority: P1
status: done
area: mech
created: 2026-11-05
---

# Ball sits 23 mm above the main PCB with the sensor straight below

## Context

With the PMW3610 mounted directly under the ball (Keyball style) the stack below the ball surface is fixed by the
parts: 2.4 mm lens-to-surface gap + 3.4 mm LM18-LSI lens + 1.6 mm sensor board + 2.25 mm package and solder.
For a 25 mm ball the cradle puts the ball top at about +23 mm above the main PCB top surface and the lowest
plastic 7.75 mm below the PCB underside (see `hardware/trackball-cradle/stack.json`). Choc caps top out around
11 mm, so the ball forms a dome like on the Keyball39ish-LP in the reference video.

## Acceptance criteria

- [x] Decide between: accept the dome (default), tilted sensor (evaluated: only helps beyond 60 deg and needs a keyhole cutout), PAW3222 thin module (hw-paw3222-variant), or moving the ball zone off the PCB
- [x] Decision recorded in docs/08-trackball-module.md and docs/09-roadmap.md
- [ ] Case design (mech-case) uses the chosen stack

## Notes

The tilted variant stays available as `sensor_angle` in `hardware/trackball-cradle/params.scad` (cutout mount only) but is not built or recommended.

2026-11-06: resolved by r2. Decision: 19.05 mm ball (research in `docs/00-feasibility.md` section 4a) in a case pocket beside the right PCB; sensor stack unchanged, ball top +17.1 mm above the PCB top, 6 mm above the caps (`hw-two-pcbs-r2`, `mech-case-ball-pocket`). The tilted sensor and the PAW3222 variant stay documented as further levers.
