---
title: Case pocket for the 19 mm ball beside the right PCB
type: feature
priority: P1
status: open
area: mech
created: 2026-11-06
---

# Case pocket for the 19 mm ball beside the right PCB

## Context

Since r2 the trackball module does not pass through the PCB. The cradle stands on the case floor in
a pocket beside the right PCB; the PCB edge only has an octagonal notch around the cup. The case
phase has to provide that pocket. All numbers come from `hardware/layout/output/points-right.json`
(`trackball` block) and `hardware/trackball-cradle/stack.json` (`19mm-pocket`), z = 0 is the PCB top:

| Item | Value |
|------|-------|
| Ball centre (layout frame, right half) | (+5.0, +64.0) |
| PCB notch | regular octagon, apothem 15.0 mm, vertices in `trackball.notch` |
| Pocket wall above the PCB plane | circle 32 mm (`pocket_diameter`): 28 mm cradle clearance + 2 mm wall |
| Floor under the module | -11.6 mm (sensor board component side down; a floor of 1.6 mm below the PCB underside is NOT enough, the pocket is a deep well like the r1 cutout zone was) |
| Housing footprint on the floor | 30 x 29 mm box plus two screw ears on the x axis: 43 x 29 mm overall, 0.5 mm clearance in `hardware/trackball-cradle/dxf/floor-19mm-pocket.dxf`. The box corners reach outside the 32 mm circle below the PCB plane, so the well is the union of the circle and the rectangle |
| Case screws | 2x M2 self-tapping from below through the floor into the ears, 36 mm apart on the x axis through the ball centre |
| Sensor board | 26 x 25 mm (`trackball.sensor_board`), lies inside the housing; the FFC leaves the housing through the slot in its key-facing wall and runs under the PCB to J1 at (-8, +46.5) |
| Cup | 23.1 mm outer diameter, rim at +6.6 mm (1 mm below the equator), nothing above the rim; ball top +17.1 mm |
| Clearance | nothing of the cradle is closer than 0.3 mm to the PCB underside; the case must not add anything between the housing top (-1.9 mm) and the PCB |

Where the housing lies under the PCB (towards the keys), it shares the general case cavity; the
case floor there must also be at -11.6 mm or deeper. The pocket wall must stay below the cup rim
(+6.6 mm) or at least leave the thumb side open so the thumb reaches the ball at its equator
(+7.6 mm) from the inner side. The cradle has no retainer: the ball is held by gravity and, in
transport, by the removable case lid (`mech-case-lid`), so the pocket itself needs no lip.

## Acceptance criteria

- [ ] Parametric pocket in `hardware/case/` built from `points-right.json` (notch polygon, pocket circle, sensor board rectangle) and `floor-19mm-pocket.dxf`
- [ ] Floor depth -11.6 mm under the module, two M2 holes, drainage for dust optional
- [ ] Test print of the pocket corner alone with the cradle and a scrap PCB with the notch: 0.3 mm gap all round, FFC routes to J1 without a sharp bend
- [ ] 25 mm fallback documented as a parameter (notch apothem 16.5 mm, pocket 35 mm) but not printed
- [ ] Image prompt for the pocket detail in `docs/images/PROMPTS.md`

## Notes

Mounting the cradle on top of the PCB was rejected (about 12 mm taller). The pocket keeps the sensor
board on the case floor like the r1 cutout did while the PCB loses the cutout and the flange ring.
The transport lid that keeps the ball in the open cup is `mech-case-lid`.
