---
title: Box cap screw heads stand in the closed lid
type: bug
priority: P1
status: done
area: mech
created: 2026-11-12
---

# Box cap screw heads stand in the closed lid

## Context

The two M2 x 5 screws of the controller box cap have pan heads on the cap top (+8.7). Their
axes are 0.5 mm inside the box wall's inner face, so each 3.5 mm head reaches 1.25 mm over the
wall. The lid's notch over the box walls ends at +9.0 (`lid_box_clear` 0.3): everything of a head
above that is inside the lid skirt. Found by `tests/test_assembly_interference.py` once the cap
screws were in it: `lid_inner / cap screw head`, 5.24 mm2 at z 9.03, on both halves. The lid
would rest on the two heads instead of the rim.

## Decision

Countersunk screws, flush in the cap: M2 x 5 machine screws with a 90 degree flat head into the
same boss inserts, in 0.7 mm countersinks (`cap_screw_d`, `cap_screw_head_d` in `params.scad`).
1.3 mm of the 2.0 mm roof stay at the bore. The BOM gets a line of four.

Tried first and dropped: two reliefs in the lid skirt over pan heads. It cleared the lid, but
the heads still stood 1.5 mm proud on the cap, beside the flush pocket cover screws.

## Acceptance criteria

- [x] Countersinks in `box_cap()`, lid reliefs removed again
- [x] `test_nothing_overlaps_in_the_closed_half` passes on both halves with countersunk cap screws
- [x] BOM, order checklist, build guide, `spec/11-case.md` and the case README name the screw

## Notes

Not printed yet, so nothing to rework.
