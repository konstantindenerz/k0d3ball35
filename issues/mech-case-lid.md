---
title: Removable lid per half that doubles as a tenting foot
type: feature
priority: P2
status: in-progress
area: mech
created: 2026-11-06
---

# Removable lid per half that doubles as a tenting foot

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
- [x] Lid holds on top by a 1 mm inner lip (3 mm into the tray, `lid_fit` 0.15), no magnets and no visible pads; four 6 x 2 mm magnets in the tray floor and four in the lid roof (0.6 mm skin, invisible) hold the foot position
- [x] Lid clears the ball top (+17.1 mm over the PCB top, roof under +18.1) and the controller box (+8.7, lid skirt notch to +9.0) with at least 1 mm; the ball cannot leave the cup with the lid on (`tests/test_case.py`)
- [x] Works as a foot on both halves in CAD: flat lift 13 mm (left) / 19.1 mm (right), `tent_wedge_deg` adds a wedge for tenting; rubber feet stay usable without it. Rocking is checked on the print
- [x] Both lids print without supports (roof down, no overhanging faces in the mesh); test print open
- [x] Image prompts in `docs/images/PROMPTS.md` (`img-case-lid-transport`, `img-case-lid-foot`)

## Notes

Depends on `mech-case` and `mech-case-ball-pocket`. The cradle has no retainer by design, see the
cradle README; if the lid turns out impractical, the fallback is a shallow bayonet ring on the cup
rim, not a change to the cup. The 25 mm fallback ball (+23.05 mm) only needs a taller lid over the
pocket; keep the lid height a parameter.

2026-11-06: CAD done in `hardware/case/lid.scad`. One height per half: left roof under +12.0,
top +14.0; right roof under +18.1, top +20.1; skirt on the rim at +5.0 with a notch over the
controller box walls; four 6 x 2 mm magnets per part. `lid_mode="dome"` keeps the right lid
at 14 mm with a turret over the ball (optional). Open: test fit and the rocking check as a
foot. See `docs/11-case.md`.

2026-11-06, later: the four 9 x 7 mm magnet pads on the outer wall are gone. Decision: the lid
holds on top without magnets, by a 1.0 mm lip on the inside of the skirt that reaches 3.0 mm
into the tray (`lid_lip_t`, `lid_lip_depth`, `lid_fit` = 0.15); the outer wall is smooth and
the lid sits flush on the rim. Magnets only hold the foot position: four 6 x 2 mm discs from
below in the tray floor near the corners (`foot_magnets` in `data.scad`, placed clear of the
wells, the FFC channel, the standoffs and the feet) and four in the lid roof, inserted from
the roof underside with 0.6 mm of roof above them (roof now 3.0 mm). The lid goes under the
half the same way up, roof against the tray; lift 13.0 mm (left) / 19.1 mm (right). Polarity:
floor north down, roof south up. 8 magnets per half, 16 in total. Open: `lid_fit` on the first
print.
