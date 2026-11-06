---
title: Removable lid per half that doubles as a tenting foot
type: feature
priority: P2
status: open
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
+23.05 mm), controller box +11 mm, Choc V1 caps about +11 mm. The lid outline follows the case
outline from `hardware/layout/output/outline-left.dxf` / `outline-right.dxf` plus the ball pocket
of the right half.

## Acceptance criteria

- [ ] Parametric CAD in `hardware/case/` sharing the outline DXFs and the pocket data with `mech-case`; one lid model per half, mirrored where the outline allows it
- [ ] Magnet pockets in lid and case (e.g. 6 x 2 mm neodymium discs, same pockets on the case top rim and on the case floor), polarity marked so the lid snaps on in both positions; a mechanical snap or clip is acceptable instead if it holds as well
- [ ] Lid clears the ball top (+17.1 mm over the PCB top) and the controller box (+11 mm) with at least 1 mm; the ball cannot leave the cup with the lid on
- [ ] Works as a foot on both halves: attached under the half it either raises it flat or tents it by a documented angle, without rocking, and the rubber feet of the case stay usable without it
- [ ] Both lids print without supports
- [ ] Image prompts in `docs/images/PROMPTS.md` (lid on for transport, lid under the half as a foot)

## Notes

Depends on `mech-case` and `mech-case-ball-pocket`. The cradle has no retainer by design, see the
cradle README; if the lid turns out impractical, the fallback is a shallow bayonet ring on the cup
rim, not a change to the cup. The 25 mm fallback ball (+23.05 mm) only needs a taller lid over the
pocket; keep the lid height a parameter.
