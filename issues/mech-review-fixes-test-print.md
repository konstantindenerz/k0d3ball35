---
title: Test print after the 2026-11-12 review fixes
type: task
priority: P1
status: open
area: mech
created: 2026-11-12
---

# Test print after the 2026-11-12 review fixes

## Context

A review of the whole repository found faults that no test had noticed, because every test
checked a part against its own numbers and none against its neighbours: the lid lip stood 0.45 mm
inside the keycaps, the battery well was shallower than its own stack-up (and the left cell lies
under sockets), two standoffs sat in hot-swap sockets and on switch pegs, the USB opening took
5.3 mm overmolds, the reset button's plunger pointed along the board over a hole in the floor,
M2 x 6 bottomed out, and the trackball axes were exchanged in the firmware. The assembly test
written afterwards (`tests/test_assembly_interference.py`) found two more on its first run: the
controller board, which overhangs the main PCB by 0.9 mm, stood 0.7 mm inside the USB wall, and
the end knuckles of the two lid plates overlapped by 0.2 mm. All of these are fixed
and have a test now. What a test cannot show is listed here for the first print.

## Acceptance criteria

Before the boards are ordered the print uses the PCB test plates (`hardware/case/stl/pcb-test-*.stl`)
and, until the ball arrives, the glued test ball (`hardware/trackball-cradle/stl/ball-19mm-test-half.stl`).

- [ ] PCB test plate: drops into each tray with 0.2 mm all round, all five holes meet their standoffs, switches seat in every position
- [ ] Lid: goes on over the keycaps and holds. The lip now stands only where the caps leave room (outer edge, step faces, thumb corner), so the friction hold is weaker than drawn before; if the lid is loose, add magnets or a detent rather than more lip
- [ ] Battery: both cells lie loose in the well with the PCB screwed down (right 5.7 mm, left 4 mm under the inner column's sockets); JST plug and leads fit beside the cell
- [ ] Standoffs: inserts set flush in the 5.6 mm standoffs without the 1.2 mm wall bulging into a socket or peg (0.44 mm of air)
- [ ] Sockets: with the PCB screwed down, a switch pressed in does not lift a socket (the floor is 0.25 mm under them); the PCB sits flat on all five standoffs
- [ ] USB: three different USB-C cables seat fully; the cap's tongue closes the slot
- [ ] Controller: drops onto its sockets with the PCB in the tray; its board end sits in the pocket of the USB wall with air all round
- [ ] Hinge: the two lid plates go together and fold freely, also at the two end knuckles
- [ ] Reset: a paper clip through the hole in the inner wall resets the controller, both halves
- [ ] Sensor sleeve: the 0.5 mm roof over the slot (65 degree overhang, no supports) printed without sagging and the module slides in; the rib behind the module leaves the cradle free to drop into the pocket
- [ ] Guard: lies flat under the switch flanges, does not rattle (`mech-pcb-guard`)
- [ ] Retainer clip: pins survive five on/off cycles (0.12 mm undercut, 0.65 mm prongs; `mech-ball-retainer-clip`)
- [ ] FFC: the S-fold (0.6 mm radius) and the fold over the PCB edge leave the cable undamaged after the pocket cover is on

## Notes

Tests added by the review: `tests/test_assembly_interference.py` (every printed and bought part of
the closed half, cut every 0.4 mm, nothing may overlap), `tests/test_print_parts.py`,
`tests/mesh_tools.py`, and in
`tests/test_case.py` `test_lid_stays_clear_of_the_keycaps`, `test_usb_plug_overmold_reaches_the_receptacle`,
`test_reset_pin_reaches_the_plunger`, `test_module_backstop_behind_the_sensor`; in
`tests/test_pcb_review.py` `test_case_standoffs_clear_the_underside` and
`test_reset_plunger_faces_the_inner_edge`; in `tests/test_firmware_build_config.py`
`test_ball_axes_follow_the_sensor_position`.
