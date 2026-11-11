---
title: Hinged lid per half that doubles as a tenting foot
type: feature
priority: P2
status: in-progress
area: mech
created: 2026-11-06
---

# Hinged lid per half that doubles as a tenting foot

## Context

The trackball cradle's cup is open by design (`hardware/trackball-cradle/README.md`, "Ball
retention"): the cup rim stops 1 mm below the ball equator so the thumb reaches the ball from
every side, and the ball sits on its three bearings by gravity alone. That is fine on the desk and
wrong in a bag, where the ball would roll out of the open cup. This ticket was the reason the r1
claw ring could go; since 2026-11-10 an optional clip-on retainer (`mech-ball-retainer-clip`)
covers the case where the lid is off.

Each half gets a removable lid that

- (a) covers the keys and the ball for transport, so nothing can fall out of the open cradle and
  the switches are protected, and
- (b) comes off and attaches under the half as a stand or foot, either raising the half flat or
  tenting it, held by magnets or a comparable snap system, so the lid is never a loose part.

Heights the lid has to clear, z = 0 is the PCB top (`hardware/trackball-cradle/stack.json`,
`issues/mech-case.md`): ball top +13.95 mm on the right half (19.05 mm ball, r2.4), controller top +5.7 mm (lid over the controller block about +7.5 mm), Choc V1 caps about +11 mm. The lid outline follows the case
outline from `hardware/layout/output/outline-left.dxf` / `outline-right.dxf` plus the ball pocket
of the right half.

## Acceptance criteria

- [x] Parametric CAD in `hardware/case/` sharing the layout data with `mech-case` (`lid.scad`); one lid model per half, the left one mirrored
- [x] Lid holds on top by a 1 mm inner lip (3 mm into the tray, `lid_fit` 0.15), no magnets and no visible pads; four 6 x 2 mm magnets in the tray floor and four in the outer lid plate's roof (0.6 mm skin, invisible) hold the foot position
- [x] Lid clears the caps (roof under +14.5, `lid_clear` 3.5; hinge strip under +12.5, 1.5 mm over the caps), the controller box (+8.7, lid skirt notch to +9.0) and the ball (top +13.95, 0.55 mm under the roof), so both halves get the same lid, top +17.5, without a ball window; the ball cannot leave the cup with the lid on (`tests/test_case.py`)
- [x] Two plates per half joined by a pin hinge along x = -13: 9 knuckles flush with the roof top, axis +15.0, 2 mm steel rod in a 2.2 mm hole inserted from the back edge into a blind end knuckle (1.75 mm filament as fallback)
- [x] Stop in the cut: below the axis the cut faces lean outward by `hinge_stop_deg` = half the solved fold (28.5 right, 21.6 left), meet flat on flat at the fold (`hinge_fold_deg` 56.9 right, 43.2 left) and carry the load; knuckle and groove never do
- [x] Works as a foot on both halves in CAD: the folded lid shifted inward by `foot_dx` so the hinge axis sits 3 mm outside the inner tray wall, outer plate roof-up on the floor magnets under the controller half, inner plate folded down beyond the inner edge as the kickstand pointing towards the other half; the half stands on its outer bottom edge and on the hinge above the kickstand, no cantilever. Tilt `tent_deg` = 18 is the input, the fold is solved so the kickstand's lip edge reaches the desk; hinge axis 37.8 mm (right; 37.8 left) above the desk, kickstand reach 34.5 mm (53.3), free end of the outer plate 1.6 mm (7.2) above the desk (`tests/test_case.py` asserts more than 0.5); rubber feet stay usable without it. Rocking is checked on the print
- [x] All four lid plates print without supports (roof down; only the pin hole and the knuckle halves past the line overhang); test print open
- [x] Image prompts in `spec/images/PROMPTS.md` (`img-case-lid-transport`, `img-case-lid-foot`, `img-case-lid-folded`, `img-case-lid-hinge`)

## Notes

Depends on `mech-case` and `mech-case-ball-pocket`. The cup is open by design, see the cradle
README; the optional clip-on retainer (`mech-ball-retainer-clip`) clears the closed lid roof by
5.1 mm and the hinge strip, so lid and retainer can be used together.

2026-11-06: CAD done in `hardware/case/lid.scad`. One height per half at the time: left roof
under +12.0, top +15.0; right roof under +18.1, top +21.1 (3 mm roof); skirt on the rim at +5.0
with a notch over the controller box walls; four 6 x 2 mm magnets per part. `lid_mode="dome"`
kept the right lid at the left height with a turret over the ball (optional). Open: test fit
and the rocking check as a foot. See `spec/11-case.md`. (Heights superseded below.)

2026-11-06, later: the four 9 x 7 mm magnet pads on the outer wall are gone. Decision: the lid
holds on top without magnets, by a 1.0 mm lip on the inside of the skirt that reaches 3.0 mm
into the tray (`lid_lip_t`, `lid_lip_depth`, `lid_fit` = 0.15); the outer wall is smooth and
the lid sits flush on the rim. Magnets only hold the foot position: four 6 x 2 mm discs from
below in the tray floor near the corners (`foot_magnets` in `data.scad`, placed clear of the
wells, the FFC channel, the standoffs and the feet) and four in the lid roof, inserted from
the roof underside with 0.6 mm of roof above them (roof now 3.0 mm). The lid goes under the
half the same way up, roof against the tray; lift 13.0 mm (left) / 19.1 mm (right), a
`tent_wedge_deg` wedge on the roof for tenting. Polarity: floor north down, roof south up. 8
magnets per half, 16 in total. Open: `lid_fit` on the first print.

2026-11-06, later still: the lid is now a hinge. The flat lid under the board was just a lid,
not a stand: it lifted the half without tenting it, and the wedge bought a few degrees at the
price of a thicker roof. Decision (after a video of a cover that hinges in the middle on a
metal pin and goes under the board on magnets): the lid is split along x = -13 (`hinge_x`,
`HINGE_X` in `scripts/gen_case.py`) into an outer plate (pinky side, ball window, all four roof
magnets) and an inner plate (controller notch, thumb cluster, the leg), joined by 9 knuckles
flush with the roof top on a 2 mm steel rod (hole 2.2, about 80 mm, blind towards the user).
`lid_clear` went from 1.0 to 3.0, so both halves share roof under +14.0 / top +17.0 and the
hinge strip (5 mm thick within 6 mm of the line) still clears the caps by 1 mm; the right ball
looks through a 16 mm window with its top flush with the roof instead of a 21 mm lid over it
(`lid_mode="flat"` keeps the old roof for the 25 mm fallback: +26.1 / +29.1). The stop is cut
into the plates: below the axis the cut faces lean outward by `tent_deg` = 18 and meet flat on
flat at the 30 degree fold, so the knuckles never carry the load. As a foot the outer plate
lies roof-up on the floor magnets and the inner plate hangs down: tilt 14.9 degrees (right,
15.3 left), hinge axis 27.2 mm and outer tray edge 13.6 mm above the desk. The magnets moved
under the outer plate (kept 2 mm clear of J1 and the cable corridor), the `tent_wedge_deg`
wedge and the flat lift are gone. New parts `lid_outer`, `lid_inner`, `lid_folded`,
`stl/lid-{outer,inner}-{left,right}.stl`; `lid-{left,right}.stl` is the closed pair for the
exploded view. Open: `lid_fit`, `hinge_clear` and `hinge_pin_fit` on the first print, rocking
as a foot. (Foot pose superseded below.)

2026-11-06, evening: the foot moved from the pinky half to the controller half. With the
outer plate under the pinky half and the hinge line in the middle of the board, the
controller and thumb half hung 62 mm beyond the hinge: a thumb press or a resting palm could
pivot the board about the hinge edge against the four magnets, which were the only thing
holding that side down. Decision (as in the video that inspired the hinge): the whole folded
lid is shifted inward by `foot_dx` (`data.scad`, generated: -64.7 mm right, -67.8 left) so
the hinge axis sits 3 mm (`foot_overhang`, `FOOT_OVERHANG` in `gen_case.py`) outside the inner
tray wall. The outer plate (ball window, roof magnets) lies roof-up under the controller half,
the inner plate folds down beyond the inner edge as a kickstand that points inward, between
the halves. The half stands on its own outer bottom edge and on the hinge directly above the
kickstand; the magnets only keep the plate aligned. The tilt `tent_deg` = 18 is now the input
and the fold `hinge_fold_deg` is derived so that the kickstand's lip edge reaches the desk
(57.6 degrees right, 43.7 left); the stop faces lean by `hinge_stop_deg` = half the fold
(28.8 / 21.9) instead of `tent_deg`. Numbers (`stack.json`, right; left in brackets):
kickstand 39.6 degrees (25.7) below the tray (`foot_beta_deg`), hinge axis 37.8 mm (37.8)
above the desk (`foot_hinge_h`), kickstand reach 34.3 mm (53.2) beyond the inner wall
(`foot_reach`), free end of the outer plate 2.1 mm (7.7) above the desk (`foot_free_end_h`;
below about 13 degrees of tilt the lid thickness alone would hold the board up, so the test
asserts more than 0.5 mm). `foot_outer_h` and the solved `foot_tilt_deg` are gone,
`foot_tilt_deg` now echoes `tent_deg`; `hinge_fold_override` (`params.scad`, -1) shows another
fold in `lid_folded` for the collision test only. The magnets moved to the floor under the key
area next to the battery well (right (-36.94, 9.69), (-26.35, 17.69), (-26.35, 45.19),
(-37.0, 38.94); left (-37.25, 9.69), (-29.478, 17.19), (-29.478, 45.19), (-37.19, 38.94)); the
generator searches the intersection of the lid roof region and the tray floor region shifted
by `foot_dx` and checks that every rubber foot is either fully on the outer plate or fully
off it (plate free edge at board x -15.15 right / -18.3 left; the foot at (-9, 40) is off).
Still 6 x 2 mm, four plus four per half, 16 in total, polarity unchanged. Consequence: the
kickstand needs about 34 mm (53 left) of free desk inward of each half. The 25 mm fallback
lid (`lid_mode="flat"`) does not work as a foot at 18 degrees: its thicker outer plate would
touch down before the kickstand (`foot_free_end_h` -9.4). Open as before: fits on the first
print, rocking as a foot.

2026-11-11 (r2.4): the ball dropped to +13.95, under the roof underside, so the ball window and
`lid_mode` are gone and both halves share one lid height: `lid_clear` 3.5, roof under +14.5,
top +17.5, hinge axis +15.0. Transport height 27.3 mm over the desk (was 31.7). Foot values from
`hardware/case/stack.json`: fold 56.9 degrees right (43.2 left), kickstand reach 34.5 mm (53.3),
free end 1.6 mm (7.2) above the desk. A window would not lower the lid: the roof underside is
bound by the hinge strip over the caps, not by the ball.
