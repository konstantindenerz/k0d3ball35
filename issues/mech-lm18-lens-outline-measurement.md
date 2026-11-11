---
title: Measure the real LM18-LSI lens outline
type: task
priority: P1
status: wontfix
area: mech
created: 2026-11-05
---

# Measure the real LM18-LSI lens outline

## Context

The LM18-LSI datasheet (PMS0039 R1.03, figure 1) gives the base flange (12.90 x 8.25), the upper body
(10.29 x 6.55) and the height (5.95), and the sensor footprint carries those on `Dwgs.User`. What the
drawing does not fix well enough is the flange position along the pin row relative to the aperture and
the clip positions; the cradle's `lens_l` / `lens_w` (assembly dummy only) are still over-estimates.

## Acceptance criteria

- [ ] A physical lens measured with calipers (length, width, height, clip positions, aperture offset)
- [x] Footprint envelope in hardware/sensor-pcb/generate.py updated from the datasheet (12.90 x 8.25 flange, 10.29 x 6.55 body, 2026-11-06)
- [ ] Cradle `lens_l` / `lens_w` in hardware/trackball-cradle/params.scad (21.5 x 11.5, assembly dummy only) shrunk after the measurement; pocket printed oversized until then
- [ ] Numbers recorded in spec/08-trackball-module.md

## Notes

Order the lens with the first sensor batch; see the order plan in spec/03-bom.md.

2026-11-11 (r2.4): wontfix. The LM18-LSI belonged to the PMW3610 board, which the bought PAW3222
module replaced. The module's own nominal values are checked on the first print
(`mech-ball-height-23mm`).
