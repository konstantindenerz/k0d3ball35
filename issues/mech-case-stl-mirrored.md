---
title: Case and cradle STLs are the mirror image of the boards
type: bug
priority: P0
status: done
area: mech
created: 2026-11-10
---

# Case and cradle STLs are the mirror image of the boards

## Context

The layout frame is x outward (pinky), y towards the user. The KiCad boards use it with a pure
translation (KiCad = layout + (120, 60), e.g. SW00 layout (36.00, 10.44) -> KiCad (156, 70.44)),
and KiCad's y also points towards the user, so the boards are correct. The OpenSCAD case and
cradle put the same x and y under z up. x outward, y towards the user, z up is a left-handed
frame, but an STL is always read right-handed. So every exported part is mirrored in y.

Seen from above in a slicer, `tray-right.stl` has its ball pocket at Y = +66, on the far side of
the key rows (row 0 at y 4.3, row 2 at y 38.3). On the real right board the pocket is on the near
side. Turning the tray 180 degrees brings the pocket to the near side but puts the pinky column on
the left: no rigid motion makes the tray fit the board. The left half has the same problem
(`mirror_left` only mirrors x).

Found while building the Trackball tab of the project page: placing the sensor board GLB so that
J1 lines up with the cradle's cable channel (`cable_channel_x` -7.6) needed a reflection, not a
rotation. The exploded view never showed it, because `docs/build.py` (now
`docs/js/tabs/explorer.js`) swaps y and z, which is itself a reflection and cancels this one.

## Acceptance criteria

- [x] Decide where to flip: once at the top level of `case.scad` (`print_frame`) and `cradle.scad` (`mirror([0, 1, 0])` around the dispatch); the sources stay in the layout frame, `logo.scad` mirrors the wordmark back
- [x] Re-render all STLs, DXFs and previews (preview cameras mirrored with the scene); `stack.json` and `retention.json` unchanged; the render tests convert back to the layout frame in one place, `tests/scad_frame.py`
- [x] `tests/test_case_handedness.py` compares the tray outline, controller box, ball pocket and the cradle cable slot with the KiCad boards in the print frame; it fails on the old files
- [x] Explorer transform and the trackball tab's sensor placement follow the fix (both are rotations now)
- [x] Physical check moved: the `pocket-test-right.stl` print against the real right PCB is the open test-print item of `mech-case-ball-pocket`

## Notes

Nothing of the case has been printed as of 2026-11-10 (the cradle test print is still open), so
no printed part is lost. The PCB files are not affected.
