---
title: Bought parts in the assembly, the interference test and the Explorer
type: task
priority: P2
status: done
area: mech
created: 2026-11-12
---

# Bought parts in the assembly, the interference test and the Explorer

## Context

The assembly views, the interference test and the Explorer left out the sensor module, the FFC,
the cradle, cover and cap screws, the rubber feet and everything on the controller. Two things
depend on them: whether the closed half really has room for them, and pictures for the
mechanical chapters of the build guide.

## Decision

Model what answers one of those two questions, as simple bodies from the numbers that already
exist. No threads, no vendor STEP files, no single parts on the controller.

| Part | Body | Source |
|---|---|---|
| Sensor module | lens, board, connector as boxes | `cradle.scad` `sensor_dummy`, exported to `hardware/trackball-cradle/ref/sensor-module.stl` |
| FFC, 50 mm | 3.5 mm band along a nominal lay: round the cup, S-fold, flat into J1 | `scripts/k0d3/ffc_route.py` `path()`, in `data.scad` and `layout.json` |
| Cradle, cover and cap screws | shank and head | `tray.scad`, positions from `data.scad` |
| Rubber feet | 10 x 1 mm discs | `data.scad` `feet` |
| Controller | socket strips and one slab up to the receptacle top | `tray.scad`, test prisms |

Magnets, inserts and the hinge pin sit in pockets of their own size and stay out.

## Acceptance criteria

- [x] Dummies in `hardware/case/tray.scad`, part of `assembly`
- [x] `tests/test_assembly_interference.py`: prisms for screws, feet, controller sockets and parts, the FFC; the sensor module as a mesh; a self-test with an M2 x 10 in the cradle
- [x] `tests/mesh_tools.py` `section`: a ring left open by rounding made a screw hole read as solid; it now retries on a coarser grid
- [x] Explorer layers for sensor module, FFC and feet, cover and cap screw heads; the Trackball sheet shows the module
- [x] `docs/gen/layout.py` takes the seven feet from the case generator instead of four of its own
- [x] Build guide pictures, see `doc-build-guide`
- [x] Lid against the cap screw heads, see `mech-cap-screw-heads-under-lid`
- [x] Explorer and Trackball sheet looked at in a browser, both halves (headless Chrome, no console errors)

## Notes

The FFC lay is nominal: the cable is put in by hand. The test draws it 0.3 mm thick and leaves out
the leaning piece in the sleeve (`tests/test_cradle.py` has it) and the twist before J1.
