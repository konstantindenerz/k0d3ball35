---
title: PCB guard between the switches without extra height
type: feature
priority: P3
status: in-progress
area: mech
created: 2026-11-11
---

# PCB guard between the switches without extra height

## Context

The Keyball39 has a plate over the PCB between the switches that protects the board. The
question was whether k0d3ball35 can have one without getting taller. It can: between the PCB
top and a pressed keycap skirt (+5.0 at rest, 3 mm travel, so +2.0) there are 2 mm of air,
and the top face carries nothing between the switches (diodes and sockets are on the bottom).
A 0.8 mm plate lying on the PCB keeps 1.2 mm of that. Rim, keycap top and lid stay where they
are.

## Acceptance criteria

- [x] Part `guard` per half (`hardware/case`, STL plus DXF for a laser-cut sheet): the PCB
      minus a 14.2 mm square per switch, 4.4 mm holes over the PCB screw heads (a head on top
      of the guard would stand above a pressed keycap), open over the controller box, J1/FFC
      and the cradle opening. Held by the switch flanges, no screws
- [x] One piece with no web under `guard_min_web`: the outline comes from
      `scripts/gen_case.py` (`guard_polygon`, shapely: cut through thin webs, keep the
      largest piece, grow it back). Done in OpenSCAD, an opening left an L-shaped strip
      beside J1 hanging on a 0.5 mm neck
- [x] Height check as an assert in `common.scad` (`guard_air` >= `guard_min_air`) and in
      `tests/test_case_guard.py` (plus one piece, clearances, covered webs, STL and DXF
      against the outline, left mirrored)
- [x] Spec (`spec/11-case.md` section 5a, parts, heights, assembly order), build guide
      chapter 12, case README, project page (explorer layer, parts list)
- [ ] Measure a real Choc V1 with an MBK cap pressed all the way down: does the skirt clear
      the guard (1.2 mm expected)?
- [ ] Test print: the guard lies flat, the flanges hold it, and no switch sits higher in its
      socket

## Notes

Rejected: a real Choc switch plate (1.2 mm at the clip height). It is also height-neutral,
but the clips need tight print tolerances and the plate adds nothing to the protection.
