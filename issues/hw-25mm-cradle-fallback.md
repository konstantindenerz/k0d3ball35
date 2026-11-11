---
title: 25 mm pocket cradle as fallback (needs a wider notch)
type: feature
priority: P3
status: wontfix
area: hw
created: 2026-11-05
---

# 25 mm pocket cradle as fallback (needs a wider notch)

## Context

r2 ships a 19.05 mm ball. If 19 mm balls do not track well or feel too light, the parametric cradle
already renders the 25 mm pocket variant (`hardware/trackball-cradle/stl/cradle-25mm-pocket.stl`,
ball top +23.05 mm). Above the PCB plane it is 29.6 mm wide, so it does not fit the r2 notch
(apothem 15 mm, 28 mm cradle clearance): the fallback needs a right PCB with `cradle_diameter: 31`
(notch apothem 16.5 mm, pocket circle 35 mm) and the ball centre moved so the wider circle keeps
1 mm to the caps. That is a PCB revision, not a drop-in.

## Acceptance criteria

- [x] 25 mm pocket STL and floor DXF exported from the parametric cradle (`make -C hardware/trackball-cradle`)
- [ ] Layout variant with `cradle_diameter: 31` checked by the generator (keycap clearance, outline), size impact recorded
- [ ] Noted as an option in the build guide only if the 19 mm tests fail

## Notes

Was hw-34mm-cradle-option (34 mm ball through the r1 cutout board) until 2026-11-06; 34 mm is out of
scope since the ball moved beside the PCB.

2026-11-11 (r2.4): wontfix. 19.05 mm is the only supported ball; the 25 mm variant and the r1 cutout
mount were removed from the cradle and the case. A larger ball would mean a new PCB notch and a
new sensor geometry, not a parameter change.
