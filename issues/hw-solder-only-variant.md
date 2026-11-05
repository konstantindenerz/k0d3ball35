---
title: Solder-only PCB variant without hot-swap sockets
type: feature
priority: P3
status: open
area: hw
created: 2026-11-05
---

# Solder-only PCB variant without hot-swap sockets

## Context

r1 is hot-swap only (`hw-hotswap-only`). A solder-only footprint (1.2 mm plated pin holes, no socket pads) would allow a thinner case and cheaper build.

## Acceptance criteria

- [ ] Footprint option in `scripts/k0d3/footprints.py`, selectable in the layout yaml
- [ ] Separate gerber set, DRC clean
- [ ] Build guide section for soldering switches directly

## Notes

None yet.
