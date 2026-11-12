---
title: Sensor module leans to +x, the ball pocket shrinks the case by 5 mm
type: task
priority: P1
status: done
area: mech
created: 2026-11-11
---

# Sensor module leans to +x, the ball pocket shrinks the case by 5 mm

## Context

In r2.4 the tilted PAW3222 module leaned towards the user (`sensor_az` 270, layout +y). The
housing box grew to 24 x 29 mm towards +y, and the pocket block became the lowest part of the
right case (101.5 mm deep). The reason given was "+x is blocked by the keys and J1". That was
wrong. Under the middle column the PCB already ends at y 42.8, while the module sits at
y 59..73 and x up to +2.7, so +x is free.

Three variants were compared as top views of the real layout:

| | Change | Case depth |
|---|---|---|
| A | unchanged, module towards +y | 101.5 mm |
| B | module towards +x | 98.2 mm |
| C | B, plus a pocket opening sized on the real cup | **96.5 mm** (chosen) |

## Acceptance criteria

- [x] `sensor_az` 180: the module leans to +x and the window sits at azimuth 0.
- [x] `bearing_az` [60, 180, 300].
- [x] The case screws moved to the y axis through the ball (on x they would hit the sleeve).
- [x] Sign fix in `cradle.scad`: the window and the tab point at `sensor_az + 180`. The old
  `-sensor_az` only happened to be right at 90 and 270, so a 0 or 180 would have put the tab
  opposite the module.
- [x] Layout:
  - `housing` 29 x 24, offset (+2.55, 0)
  - `sensor_board` 4.4 x 14, offset (+13.5, 0)
  - `case_screws()` on the y axis
- [x] `gen_case.pocket_opening` sizes the cup circle on `cup_envelope` + `housing_clearance`
  towards the user instead of `cradle_diameter` (the 28 mm r1 flange). On the key side that
  circle stays open for the FFC round the cup and over the square notch corner.
  `cradle_diameter` still sizes the PCB notch, so the PCBs did not change.
- [x] Clip snap pins moved from +-25 to +-56 deg, between the new sensor tab and the claws.
- [x] `tests/test_cradle.py` measures the footprint, DXF, STL and layout offsets in the lean frame
  of `window_az`, so it checks the direction and does not assume an axis.
- [x] Spec 02/08/11 and the cradle/case READMEs are updated.

## Notes

- The FFC route was re-done with the real module in `mech-cradle-real-module`.
- Found in review, on main since r2.4 and fixed here: the optical window was cut along local +z,
  away from the sensor, so the whole cup wall stood solid in front of the lens. It is now cut
  along -z, and `test_optical_window_is_open_along_the_axis` casts rays through the mesh.
  `test_module_sits_at_the_window_azimuth` checks the slot against the window independently.
- The 16.2 mm back-side dummy is gone with `mech-cradle-real-module`.
