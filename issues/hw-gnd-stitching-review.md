---
title: Review the automatic GND stitching vias and the pours
type: task
priority: P2
status: open
area: hw
created: 2026-11-05
---

# Review the automatic GND stitching vias and the pours

## Context

`scripts/route.py` routes GND as a normal net, adds the pours afterwards, places GND vias on a 6 mm grid wherever both pours have copper around the point, and removes vias that would only anchor islands. The result passes DRC but has not been looked at by a person.

## Acceptance criteria

- [x] No via where the case or a bumper needs a flat area: moot in r2, nothing bears on the PCB underside except the five M2 holes; bumpers and standoffs sit on the case (`mech-case`)
- [x] Pours not fragmented into thin slivers around the socket pads: `tests/test_pcb_review.py::test_gnd_zones_have_no_slivers` (every filled GND polygon at least 2 mm2 and anchored by a GND via or pad, so no isolated islands)
- [x] Decision: the 6 mm grid stays, DRC is clean on both boards; a hand-picked set is not worth a re-route for r2

## Notes

2026-11-06: criteria resolved as above. Not blocking for the r2 order (`hw-jlcpcb-order-r1`). For
the visual pass look at the layer renders `tests/test_gerbers.py` writes to `build/gerber-check/`
(`left-top.png`, `left-bottom.png`, `right-top.png`, `right-bottom.png`; the bottom views are
mirrored). The one small GND polygon on the right board's B.Cu (about 2 mm2, between the controller's
GND holes) is anchored by those pads and is harmless; the sliver test keeps it from shrinking further. Status
stays open only for the eyeball pass of the renders, which the user does together with the review
in `hw-main-pcb-review-r1`.
