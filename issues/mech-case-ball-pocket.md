---
title: Case pocket for the 19 mm ball beside the right PCB
type: feature
priority: P1
status: in-progress
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
| PCB notch | octagon, apothem 15.0 mm, with the corner towards the keys squared off so the module can be lowered past the board edge (`mech-cradle-notch-relief`), vertices in `trackball.notch` |
| Pocket wall above the PCB plane | circle 32 mm (`pocket_diameter`): 28 mm cradle clearance + 2 mm wall |
| Floor under the module | -11.6 mm (sensor board component side down; a floor of 1.6 mm below the PCB underside is NOT enough, the pocket is a deep well like the r1 cutout zone was) |
| Housing footprint on the floor | 29 x 29 mm box, no ears (`footprint_x` / `footprint_y` in `stack.json`); `hardware/trackball-cradle/dxf/floor-19mm-pocket.dxf` is that outline with 0.5 mm clearance (30 x 30 mm) plus the two screw holes |
| Case screws | 2x M2 x 10 self-tapping from below through the case floor (2 mm), the 2.25 mm component gap and the sensor board into the cradle's sensor posts; 20 mm apart on the y axis through the ball centre (`case_screw_sp`), 2.2 mm clearance holes in the floor. The same screws clamp the sensor board, there are no separate cradle-to-case screws |
| Pocket at floor level | rounded rectangle 34 x 34 mm with 3 mm corner radius around the housing (29 x 29 + 2 x 0.5 mm clearance + 2 mm wall) centred on the ball, from the floor up to the PCB underside; it merges into the general cavity under the PCB on the key side. The 32 mm circle applies only above the PCB plane |
| Sensor board | 26 x 25 mm (`trackball.sensor_board`), lies inside the housing; the FFC leaves the housing through the slot in its key-facing wall, turns up the 6 mm channel in the same wall and climbs the gap between cup and notch to J1 at (-2.6, +45.5) on the key side of the PCB. The tray needs no cable channel |
| Cup | 23.1 mm outer diameter, rim at +6.6 mm (1 mm below the equator), nothing above the rim; ball top +17.1 mm |
| Clearance | nothing of the cradle is closer than 0.3 mm to the PCB underside; the case must not add anything between the housing top (-1.9 mm) and the PCB |

Where the housing lies under the PCB (towards the keys), it shares the general case cavity; the
case floor there must also be at -11.6 mm or deeper. The pocket wall must stay below the cup rim
(+6.6 mm) or at least leave the thumb side open so the thumb reaches the ball at its equator
(+7.6 mm) from the inner side. The cradle has no retainer: the ball is held by gravity and, in
transport, by the removable case lid (`mech-case-lid`), so the pocket itself needs no lip.

## Acceptance criteria

- [x] Parametric pocket in `hardware/case/` built from the layout (notch polygon, housing box and footprint, case screws via `scripts/gen_case.py`), checked against `floor-19mm-pocket.dxf` in `tests/test_case.py`
- [x] Floor depth -11.6 mm under the module, two 2.2 mm holes 20 mm apart on the y axis for the M2 x 10 case screws (counterbored, 2.0 mm floor remains), drainage for dust optional
- [ ] Test print of the pocket corner alone with the cradle and a scrap PCB with the notch: 0.3 mm gap all round, the module drops in and lifts out vertically with the board in place, FFC folds over the board edge into J1 without a crease
- [x] 25 mm fallback documented as a parameter (notch apothem 16.5 mm, pocket 35 mm) but not printed
- [x] Image prompt for the pocket detail in `docs/images/PROMPTS.md` (`img-case-pocket-detail`)

## Notes

Mounting the cradle on top of the PCB was rejected (about 12 mm taller). The pocket keeps the sensor
board on the case floor like the r1 cutout did while the PCB loses the cutout and the flange ring.
The transport lid that keeps the ball in the open cup is `mech-case-lid`.

2026-11-06: CAD done in `hardware/case/` (`part="pocket_test"` is the 50 x 50 mm corner for the
test print, `stl/pocket-test-right.stl`). Pocket floor -11.6, housing well 30 x 30 in a 34 x 34
block, case screws (5, 54) and (5, 74), cavity above the PCB plane is the notch plus
0.2 mm, rim +5.0 under the cup rim +6.575.
`tests/test_case.py` checks the floor DXF against the cradle's and the rendered mesh against
`hardware/trackball-cradle/stack.json`. Open: the test print with the cradle and a scrap PCB.
See `docs/11-case.md`.

2026-11-06 (r2.2): the pocket follows `mech-cradle-notch-relief` and `hw-j1-top-side`. Housing
29 x 29 in a 30 x 30 well inside a 34 x 34 block, notch corner towards the keys square, no FFC
channel in the tray any more (the cradle carries the cable up its own wall), and the lid lip keeps
clear of J1 and the cable corridor on the key side.
