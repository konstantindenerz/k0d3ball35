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

## Options

1. Two reliefs in the lid over the heads (4.5 mm wide, up to +10.5). Lid only, no change to the
   BOM or the cap.
2. Countersunk screws flush in the cap. The cap roof is 2.0 mm: a 0.9 mm countersink leaves
   1.1 mm, and the BOM gets another screw type.

## Acceptance criteria

- [x] Option 1: `lid_box_notch` cuts a 4.3 mm relief over each head up to +10.5 (`cap_screw_head_d`, `cap_screw_head_h`, `lid_screw_clear` in `params.scad`); 1.35 mm of the 3 mm skirt stay
- [x] `test_nothing_overlaps_in_the_closed_half` passes on both halves

## Notes

Not printed yet, so nothing to rework.
