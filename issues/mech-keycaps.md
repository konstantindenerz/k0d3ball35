---
title: Printed dished Choc keycap set
type: feature
priority: P3
status: in-progress
area: mech
created: 2026-11-05
---

# Printed dished Choc keycap set

## Context

The reference build uses self-designed dished low profile caps with smoothed thumb caps. A parametric cap in OpenSCAD lets people print the grey/white/orange set at home.

## Acceptance criteria

- [x] Parametric 1u Choc cap with dish depth and thumb smoothing parameters
- [x] STL set for 35 keys (18 left, 17 right) exported, print settings documented
- [ ] Fit test printed, `stem_fit` set from the tab that holds on a Choc V1 switch
- [ ] One cap of each kind printed and checked on a switch: pressed skirt clears the flange, lid closes

## Notes

- 2026-11-23: `hardware/keycaps`: one body (17.4 x 16.4 mm, 1.0 mm wall, top +10.6, skirt +6.7
  at rest) with three tops: a 0.6 mm cylindrical dish on the finger keys, the same with a rounded
  bar on `index_1` (F, J), and a flat top with a 1.5 mm round-over on the thumbs (`dish_depth`,
  `thumb_edge_r`). Choc V1 legs 1.20 x 3.00 nominal at 5.70 mm, minus `stem_fit` (0.10 for FDM
  until the fit test says otherwise). Printed standing on the back face, support under the legs
  only. Inside the case's keycap envelope, so no case check changes. The page shows the caps in
  the Explorer and lists them in the Case tab; the release zip carries them in `keycaps/` and the
  fit test in `test-prints/`.
