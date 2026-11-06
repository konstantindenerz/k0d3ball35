---
title: Parametric trackball cradle with ceramic ball seats (19 mm pocket mount, 25 mm variant)
type: feature
priority: P0
status: done
area: mech
created: 2026-11-05
---

# Parametric trackball cradle with ceramic ball seats (19 mm pocket mount, 25 mm variant)

## Context

3D printed cradle holding the ball on three 2 mm ZrO2 ceramic balls at 120 degrees, with a pocket
for the sensor PCB giving a lens-to-ball distance of 2.4 to 2.9 mm, and a flange screwed to the main
PCB cradle holes (r1; since r2 the module stands on the case floor). Parametric in
ball diameter (19.05 mm pocket mount default since r2, 25 mm pocket as fallback, the r1 25 mm cutout mount kept for reference).

## Acceptance criteria

- [ ] OpenSCAD or CadQuery source in `hardware/trackball-cradle/` with ball diameter, bearing diameter, lens distance and wall thickness as parameters
- [x] STL exported for 19.05 mm pocket, 25 mm pocket and 25 mm cutout; floor footprint DXF for the case
- [ ] Printed test fit checklist in `docs/08-trackball-module.md` (ball spins freely, no wobble, sensor reads at the target distance)
- [ ] The cradle is the first part to print, before any PCB order

## Notes

Depends on hw-sensor-stack-height for the final sensor orientation.

2026-11-05: cradle.scad renders 25 mm and 34 mm variants, retainer ring, tilted variant evaluated; stack heights in stack.json. Ball height follow-up in mech-ball-height-23mm.

2026-11-06: retainer (claw ring, pegs, rim holes) removed by decision: the rim stays 1 mm below the equator, the ball is held by gravity, the removable case lid (`mech-case-lid`) covers it in transport. `stack.json` lost `claw_top_z` / `retainer_ball_play` and gained `rim_below_equator`.

2026-11-06: `mount = "pocket"` added for r2: the module stands on the case floor beside the right PCB (housing 30 x 29 mm plus two screw ears, cable slot towards the keys), 19.05 mm default, ball top +17.1 mm, 24.1 mm wide above the PCB (fits the 15 mm notch apothem); 25 mm pocket needs a 16.5 mm apothem. Test print still pending.
