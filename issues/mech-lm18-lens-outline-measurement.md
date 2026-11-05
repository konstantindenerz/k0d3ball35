---
title: Measure the real LM18-LSI lens outline
type: task
priority: P1
status: open
area: mech
created: 2026-11-05
---

# Measure the real LM18-LSI lens outline

## Context

The exact base plate dimensions of the LM18-LSI lens are not in the public datasheet. The sensor footprint
carries an approximate envelope on `Dwgs.User` and the cradle lens pocket is sized from the same guess.

## Acceptance criteria

- [ ] A physical lens measured with calipers (length, width, height, clip positions, aperture offset)
- [ ] Footprint envelope in hardware/sensor-pcb/generate.py and the cradle pocket updated; pocket printed oversized until then
- [ ] Numbers recorded in docs/08-trackball-module.md

## Notes

Order the lens with the first sensor batch; see the order plan in docs/03-bom.md.
