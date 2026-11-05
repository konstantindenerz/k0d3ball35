---
title: Cradle flange holes too close to the PCB edge
type: bug
priority: P1
status: done
area: hw
created: 2026-11-05
---

# Cradle flange holes too close to the PCB edge

## Context

The ball-zone outline ring used a 2 mm margin around the 34 mm cradle circle, which left the three M2 flange holes on the 36 mm circle with less than 0.3 mm of material to the edge. Found by the geometry test (xfail at the time).

## Acceptance criteria

- [x] `ball_margin` in hardware/layout/k0d3ball36.yaml raised to 3.5 mm (cradle radius 17 + 3.5)
- [x] Geometry test passes, docs/01-design-spec.md section 5 states the margin

## Notes

Fixed in the layout generator on 2026-11-05.
