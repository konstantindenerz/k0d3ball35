---
title: Check the battery plug polarity of both cells against J3 before first power
type: task
priority: P0
status: open
area: hw
created: 2026-11-12
---

# Check the battery plug polarity of both cells against J3 before first power

## Context

There is no standard for which pin of a JST-PH plug carries the battery plus. On the boards J3
pin 1 is BAT+ (`scripts/k0d3/netlist.py`), printed as `+` and `-` beside the pads since the
2026-11-12 review; before that only a 0.6 mm "1" marked it. A reversed cell destroys the
controller's charger at once. Two different cells are used (LP552035 right, LP402025 left), from
possibly different makers, so each one has to be checked on its own.

## Acceptance criteria

- [ ] Right cell (LP552035): red lead ends on the `+` pad of J3 when the plug is held over the connector; if not, lift the two crimp contacts and swap them
- [ ] Left cell (LP402025): the same check
- [ ] With the cell plugged and the switch off: + 3.7 to 4.2 V between the J3 `+` pad and GND, measured before the controller goes onto its sockets
- [ ] Result (which shop, which polarity) noted here and in spec/03-bom.md

## Notes

Build guide chapter 7 describes the measurement. Found in the 2026-11-12 review.
