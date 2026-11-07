---
title: Cradle screw heads should sit flush in the case floor
type: bug
priority: P3
status: done
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

- [x] Decided: countersunk M2 screws with a 90 degree flat head. The floor under the pocket
      block cannot get thicker (the underside is flat at `base_z` and the pocket floor sets the
      ball height), and a deeper counterbore would leave 1.0 mm of shelf; a cone takes its load
      into the full 2.5 mm around the bore instead
- [x] `tray.scad` cuts a 4.8 mm, 1.3 mm deep cone (`case_screw_cs_d`, `case_screw_cs_h`,
      `case_screw_head_d` 4.4 = the widest M2 flat head). A head sinks until the cone is as
      wide as it is, so it ends up 0.2 mm inside the underside; 1.2 mm of floor is left at the
      bore and the cradle's thread engagement stays about 3.8 mm
- [x] Exploded view draws the heads in the cone (`template.html`, cradle layer, from the new
      `case_screw_*` stack keys in `build.py`): the underside now reads as two holes
- [x] `tests/test_case.py` checks the cone in the tray mesh (mouth 4.8 at `base_z`, bore 2.2 at
      `base_z + cs_h`, no counterbore shelf) and the stack (`case_screw_head_z` at or above
      `base_z`, recess at least as deep as the head cone, floor left at least 1.0 mm)

## Notes

Found on 2026-11-07 while looking at the underside in the exploded view. Related:
`mech-case-ball-pocket`, `doc-exploded-view-3d`.

2026-11-07: done. BOM, order checklist, build guide, case and cradle README now ask for
M2 x 10 **countersunk** self-tapping screws (DIN 7982 ST2.2, head 4.4 mm; countersunk machine
screws into heat-set inserts work too, their 3.8 mm head just sinks 0.3 mm deeper). Nothing was
ordered yet, so the change costs nothing. Print check: the cone opens to the bed, so it needs no
support; whether the head really disappears is on the test print with the rest of the fits.
