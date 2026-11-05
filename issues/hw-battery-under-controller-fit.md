---
title: Verify the 3.3 mm cell fits under the socketed controller
type: task
priority: P2
status: open
area: hw
created: 2026-11-05
---

# Verify the 3.3 mm cell fits under the socketed controller

## Context

The plain half carries a 301230 cell (32 x 11.5 x 3.3 mm) between the main PCB and the controller.
Socket height (1.27 mm mill-max about 3.5 mm, conthrough about 2.5 mm) plus the controller's bottom
components must leave room for the cell and its leads, and nothing on the main PCB may sit under the
controller except the pads. Thermal and mechanical stress on the cell must be avoided.

## Acceptance criteria

- [ ] Keep-out under the controller on the main PCB verified in the layout
- [ ] Socket type chosen and listed in the BOM with its stacked height
- [ ] Test fit on the first PCB with the cell and a 1 mm foam pad

## Notes

None yet.
