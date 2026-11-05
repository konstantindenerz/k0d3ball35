---
title: Revision 1 is hot-swap only
type: task
priority: P2
status: done
area: hw
created: 2026-11-05
---

# Revision 1 is hot-swap only

## Context

The reversible Choc footprint needs the socket boss hole of the mirrored orientation right next to the socket
pad of the other face. Plated holes there short the column and switch nets, so all three socket boss holes are
3.05 mm non-plated holes. Switches are therefore held by the CPG135001S30 sockets only, exactly like the Keyball.

## Acceptance criteria

- [x] Footprint `SW_Choc_V1_HS_reversible` uses NPTH boss holes and DRC reports no shorts
- [x] docs/01-design-spec.md R2 says hot-swap only
- [ ] Solder-only variant tracked for a later revision (docs/09-roadmap.md)

## Notes

Pad next to the centre pin is a 2.55 x 2.0 mm pill shifted 0.45 mm north so it clears the mirrored boss hole by 0.25 mm.
