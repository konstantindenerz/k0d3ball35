---
title: Assembly order in the docs did not match the hardware
type: bug
priority: P1
status: in-progress
area: doc
created: 2026-11-06
---

# Assembly order in the docs did not match the hardware

## Context

Three documents described the build and contradicted each other and the hardware:

* `spec/11-case.md` section 5 put the PCB in (step 3) before the cradle (step 5). With the old
  notch the module could not enter its pocket at all once the PCB was in
  (`mech-cradle-notch-relief`), and J1's lock was unreachable under the board
  (`hw-j1-top-side`).
* `spec/04-build-guide.md` chapter 7 glues the cell to the underside of the PCB and plugs it into
  J3 before the PCB goes in - the only order that works, because the battery well is fully
  covered by the board. `spec/11-case.md` section 5 step 6 had the battery going into the well
  after the PCB was screwed down.
* The build guide has no case chapter at all, so chapters 7 and 11 half assume a case that is
  never mentioned.
* `spec/11-case.md` section 7 had already been brought in line with the lip lid and the four floor
  magnets (`mech-case-lid`) while this was being written; nothing left to do there.

## Decision

One assembly order, written once in `spec/11-case.md` and referenced from the build guide, which
gets its own case chapter. The order follows the hardware:

1. Heat-set inserts, then the four foot magnets.
2. Bearings into the cup, sensor board plus cable into the cradle, module into the pocket, two
   M2 x 10 from below.
3. Cell onto the back of the PCB, plug into J3.
4. PCB into the tray over the cup, five M2 screws from the top.
5. Controller, box cap, keycaps.
6. FFC over the board edge into J1, ball in, lid on.

Service reverses steps 6 and 2: the trackball module comes out without touching keycaps or PCB.

## Acceptance criteria

- [x] `spec/11-case.md` section 5 rewritten, service section added, section 7 updated for the lip lid
- [x] `spec/04-build-guide.md`: case chapter, chapter 11 rewritten, chapter 7 aligned, troubleshooting rows and the printable checklist updated
- [x] `spec/08-trackball-module.md` section 4 in the same order
- [x] `tests/test_docs.py` checks that both documents list the same order
- [ ] Walk the order once on the real build
