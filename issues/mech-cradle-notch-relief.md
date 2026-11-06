---
title: Make the trackball module a cartridge that clears the PCB notch
type: bug
priority: P1
status: done
area: mech
created: 2026-11-06
---

# Make the trackball module a cartridge that clears the PCB notch

## Context

The r2 pocket mount could not be assembled in the documented order. Measured against
`hardware/case/data.scad` and `hardware/layout/output/points-right.json`:

* The notch was a regular octagon (apothem 15 mm), so its 45 degree facet towards the keys and
  the inner column ran along `x + y = 47.787` in the layout frame. The cradle housing
  (30 x 29 mm, `x -10..20`, `y 49.5..78.5`) reached 5.86 mm past that line, the 26 x 25 mm sensor
  board inside it 3.03 mm.
* The pocket well leaves 0.5 mm of clearance around the housing, so the module could not be
  tilted or slid in either: with the PCB screwed down there was no way to get it into its pocket,
  and no way to take it out again for service.
* `docs/11-case.md` section 5 (PCB in step 3, cradle in step 5) and `docs/04-build-guide.md`
  chapter 11 therefore described an assembly that cannot be carried out.

## Decision

The module becomes a cartridge: it drops into the pocket and lifts straight out with the PCB
fitted. Two changes, both on parts that were not ordered yet:

* The notch keeps its octagon shape except for the corner towards the keys, which is square
  (`trackball.pocket.square_corner` in the layout yaml, `notch_shape()` in
  `scripts/k0d3/geometry.py`). That removes 34 mm2 of board at an edge where nothing is routed.
* The housing is 29 mm wide instead of 30 (walls 1.5 mm on x, 2 mm on y, `housing_wall_x` in the
  cradle params), 1 mm narrower than the notch across its flats.

Result: housing and sensor board clear the board edge by 0.50 mm all the way in. A 45 degree
chamfer on the housing and the sensor board was the alternative; it needed 8.5 mm and 6 mm legs,
cut into the sensor board's corner where its FPC connector sits, and was dropped.

## Acceptance criteria

- [x] `Layout.insertion_corridor()` (housing plus sensor board) checked against the outline in `check_layout`, with `trackball.pocket.corner_clearance` as the minimum gap
- [x] Squared notch corner in the generated outline, the gerbers and `data.scad`; `tests/test_gerbers.py` asserts there is no 45 degree side left and that the fab outline encloses the same area as the generated one
- [x] Housing 29 x 29 everywhere: layout, cradle `stack.json`, floor DXFs, case pocket well (30 x 30), `tests/test_cradle.py` and `tests/test_sensor_pcb_vs_cradle.py`
- [ ] Confirmed on the pocket test print with the printed cradle and a scrap board with the notch

## Notes

The square corner leaves a dead triangle beside the cup in the case pocket; it fits the boxy
look. The 25 mm fallback cradle keeps the same relief rule.
