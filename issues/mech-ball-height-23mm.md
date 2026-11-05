---
title: Ball sits 23 mm above the main PCB with the sensor straight below
type: question
priority: P1
status: open
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

- [ ] Decide between: accept the dome (default), tilted sensor (evaluated: only helps beyond 60 deg and needs a keyhole cutout), PAW3222 thin module (hw-paw3222-variant), or moving the ball zone off the PCB
- [ ] Decision recorded in docs/08-trackball-module.md and docs/09-roadmap.md
- [ ] Case design (mech-case) uses the chosen stack

## Notes

The tilted STL and its cutout DXF are kept in `hardware/trackball-cradle/` for reference but are not recommended.
