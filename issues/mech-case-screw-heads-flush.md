---
title: Cradle screw heads should sit flush in the case floor
type: bug
priority: P3
status: open
area: mech
created: 2026-11-07
---

# Cradle screw heads should sit flush in the case floor

## Context

The two M2 x 10 screws that hold the trackball cradle go in from below through the pocket
block of the right tray (`case_screws` (5, 54) and (5, 74)). The floor there is 2.5 mm thick
and the counterbore is only 0.5 mm deep (`case_screw_cb_d` 4.5, `case_screw_cb_h` =
`floor_t - 2.0`), so a 1.5 mm pan head stands 1 mm proud of the underside. In the exploded
view (`docs/exploded-view`) the heads show as two grey discs floating under the pocket block
and do not read as holes at all; on the printed part they would scratch the desk and the lid
plate that lies against the floor in the foot position does not reach the block anyway, but a
head standing proud is still wrong.

## Acceptance criteria

- [ ] Decide: deeper counterbore (needs 2.0 mm of floor under the cradle, so either a thicker
      floor under the pocket block or flat-head M2 screws with a 90 degree countersink), or
      low-profile screws
- [ ] `tray.scad` and the cradle stack agree on the head recess; heads flush or below
      `base_z`
- [ ] Exploded view draws the heads inside the recess (`template.html`, cradle layer) so the
      underside reads as two holes, not two discs
- [ ] `tests/test_case.py` checks the recess depth against the head height

## Notes

Found on 2026-11-07 while looking at the underside in the exploded view. Related:
`mech-case-ball-pocket`, `doc-exploded-view-3d`.
