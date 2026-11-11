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
| Ball centre (layout frame, right half) | (-13.0, +66.0), +4.4 mm; ball top +13.95 mm |
| PCB notch | octagon, apothem 15.5 mm, with the corner towards the keys squared off so the module can be lowered past the board edge (`mech-cradle-notch-relief`), vertices in `trackball.notch` |
| Pocket wall above the PCB plane | circle 32 mm (`pocket_diameter`), cut at +2.925, 0.5 mm under the cup rim, so the thumb reaches the ball at its equator |
| Pocket floor | -7.1 mm (battery well -7.6, underside -9.6; the floor is 2.5 mm thick under the pocket) |
| Cradle floor footprint | cup skirt plus the module sleeve's tab, 27.73 x 24.05 mm (x by y) with 0.5 mm clearance, leaning towards layout +x (under the middle column, since r2.4b); `hardware/trackball-cradle/dxf/floor-19mm-pocket.dxf` |
| Pocket well | the 29 x 24 mm housing box (centred 2.55 mm off the ball towards +x) plus 0.5 mm; it contains the footprint |
| Case screws | 2x M2 x 8 countersunk self-tapping from below through the floor into the cup skirt, 20 mm apart on the y axis, 2.2 mm holes with a 4.8 mm, 1.3 mm deep countersink |
| Cable | the FFC leaves the sleeve below the PCB, climbs the gap between cup and notch, runs round the cup and folds over the board edge into J1 at (-20.6, +47). The tray needs no cable channel |
| Cup | 23.05 mm outer diameter, rim at +3.425 mm (1 mm below the equator), nothing above the rim |

The cup is open: the ball is held by gravity and, in transport, by the case lid (`mech-case-lid`)
or the optional clip-on retainer (`mech-ball-retainer-clip`), so the pocket itself needs no lip.

## Acceptance criteria

- [x] Parametric pocket in `hardware/case/` built from the layout (notch polygon, housing box and footprint, case screws via `scripts/gen_case.py`), checked against `floor-19mm-pocket.dxf` in `tests/test_case.py`
- [x] Floor at -7.1 mm under the module, two 2.2 mm holes 20 mm apart on the y axis for the M2 x 8 case screws (countersunk, 1.2 mm floor left at the bore)
- [ ] Test print of the pocket corner alone with the cradle and a scrap PCB with the notch: 0.3 mm gap all round, the module drops in and lifts out vertically with the board in place, FFC folds over the board edge into J1 without a crease
- [x] Image prompt for the pocket detail in `spec/images/PROMPTS.md` (`img-case-pocket-detail`)

## Notes

Mounting the cradle on top of the PCB was rejected (about 12 mm taller). The pocket keeps the sensor
board on the case floor like the r1 cutout did while the PCB loses the cutout and the flange ring.
The transport lid that keeps the ball in the open cup is `mech-case-lid`.

2026-11-06: CAD done in `hardware/case/` (`part="pocket_test"` is the 50 x 50 mm corner for the
test print, `stl/pocket-test-right.stl`). Pocket floor -11.6, housing well 30 x 30 in a 34 x 34
block, case screws (-13, 56) and (-13, 76), cavity above the PCB plane is the notch plus
0.2 mm, rim +5.0 under the cup rim +6.575.
`tests/test_case.py` checks the floor DXF against the cradle's and the rendered mesh against
`hardware/trackball-cradle/stack.json`. Open: the test print with the cradle and a scrap PCB.
See `spec/11-case.md`.

2026-11-06 (r2.2): the pocket follows `mech-cradle-notch-relief` and `hw-j1-top-side`. Housing
29 x 29 in a 30 x 30 well inside a 34 x 34 block, notch corner towards the keys square, no FFC
channel in the tray any more (the cradle carries the cable up its own wall), and the lid lip keeps
clear of J1 and the cable corridor on the key side.

2026-11-11 (r2.4): tilted PAW3222 module beside the ball. Pocket floor -11.6 -> -7.1, decoupled
from the battery well (-7.6); the footprint is no longer a 29 x 29 / 30 x 30 box but cup plus
sleeve (24.05 x 26.84), well 25 x 30; pocket wall cut below the cup rim; the 25 mm fallback is
gone (`hw-25mm-cradle-fallback`). Open: the test print, see `mech-ball-height-23mm`.
