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

The trackball cradle has no retainer by design (`hardware/trackball-cradle/README.md`, "Ball
retention"): the cup rim stops 1 mm below the ball equator so the thumb reaches the ball from
every side, and the ball sits on its three bearings by gravity alone. That is fine on the desk and
wrong in a bag, where the ball would roll out of the open cup. This ticket is the reason the
retainer could go.

Each half gets a removable lid that

- (a) covers the keys and the ball for transport, so nothing can fall out of the open cradle and
  the switches are protected, and
- (b) comes off and attaches under the half as a stand or foot, either raising the half flat or
  tenting it, held by magnets or a comparable snap system, so the lid is never a loose part.

Heights the lid has to clear, z = 0 is the PCB top (`hardware/trackball-cradle/stack.json`,
`issues/mech-case.md`): ball top +17.1 mm on the right half (19.05 mm ball; 25 mm fallback
+23.05 mm), controller top +5.7 mm (lid over the controller block about +7.5 mm), Choc V1 caps about +11 mm. The lid outline follows the case
outline from `hardware/layout/output/outline-left.dxf` / `outline-right.dxf` plus the ball pocket
of the right half.

## Acceptance criteria

- [x] Parametric CAD in `hardware/case/` sharing the layout data with `mech-case` (`lid.scad`); one lid model per half, the left one mirrored
- [x] Lid holds on top by a 1 mm inner lip (3 mm into the tray, `lid_fit` 0.15), no magnets and no visible pads; four 6 x 2 mm magnets in the tray floor and four in the outer lid plate's roof (0.6 mm skin, invisible) hold the foot position
- [x] Lid clears the caps (roof under +14.0, `lid_clear` 3.0; hinge strip under +12.0, 1 mm over the caps) and the controller box (+8.7, lid skirt notch to +9.0); the 19.05 mm ball looks through a 16 mm roof window with its top flush with the roof top (+17.0) and cannot leave the cup with the lid on (`tests/test_case.py`)
- [x] Two plates per half joined by a pin hinge along x = -13: 9 knuckles flush with the roof top, axis +14.5, 2 mm steel rod in a 2.2 mm hole inserted from the back edge into a blind end knuckle (1.75 mm filament as fallback)
- [x] Stop in the cut: below the axis the cut faces lean outward by `tent_deg` = 15, meet flat on flat at the 30 degree fold and carry the load; knuckle and groove never do
- [x] Works as a foot on both halves in CAD: outer plate roof-up on the floor magnets, inner plate folded down as the leg, tilt about 15 degrees with the inner edge up (14.9 right, 15.3 left), hinge axis 27.2 mm and outer tray edge 13.6 mm above the desk; rubber feet stay usable without it. Rocking is checked on the print
- [x] All four lid plates print without supports (roof down; only the pin hole and the knuckle halves past the line overhang); test print open
- [x] Image prompts in `docs/images/PROMPTS.md` (`img-case-lid-transport`, `img-case-lid-foot`, `img-case-lid-folded`, `img-case-lid-hinge`)

## Notes

Depends on `mech-case` and `mech-case-ball-pocket`. The cradle has no retainer by design, see the
cradle README; if the lid turns out impractical, the fallback is a shallow bayonet ring on the cup
rim, not a change to the cup. The 25 mm fallback ball (+23.05 mm) only needs a taller lid over the
pocket; keep the lid height a parameter.

2026-11-06: CAD done in `hardware/case/lid.scad`. One height per half at the time: left roof
under +12.0, top +15.0; right roof under +18.1, top +21.1 (3 mm roof); skirt on the rim at +5.0
with a notch over the controller box walls; four 6 x 2 mm magnets per part. `lid_mode="dome"`
kept the right lid at the left height with a turret over the ball (optional). Open: test fit
and the rocking check as a foot. See `docs/11-case.md`. (Heights superseded below.)

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
into the plates: below the axis the cut faces lean outward by `tent_deg` = 15 and meet flat on
flat at the 30 degree fold, so the knuckles never carry the load. As a foot the outer plate
lies roof-up on the floor magnets and the inner plate hangs down: tilt 14.9 degrees (right,
15.3 left), hinge axis 27.2 mm and outer tray edge 13.6 mm above the desk. The magnets moved
under the outer plate (kept 2 mm clear of J1 and the cable corridor), the `tent_wedge_deg`
wedge and the flat lift are gone. New parts `lid_outer`, `lid_inner`, `lid_folded`,
`stl/lid-{outer,inner}-{left,right}.stl`; `lid-{left,right}.stl` is the closed pair for the
exploded view. Open: `lid_fit`, `hinge_clear` and `hinge_pin_fit` on the first print, rocking
as a foot.
