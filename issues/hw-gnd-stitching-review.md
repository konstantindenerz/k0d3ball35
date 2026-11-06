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

- [ ] Open `hardware/left-pcb/k0d3ball35-left.kicad_pcb` and `hardware/right-pcb/k0d3ball35-right.kicad_pcb` in KiCad, show only the copper layers, check that no via sits where the case or a bumper needs a flat area
- [ ] Check that the pours are not fragmented into thin slivers around the socket pads
- [ ] Decide whether the 6 mm grid stays or a hand-picked set of vias replaces it

## Notes

None yet.
