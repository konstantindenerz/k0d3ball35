---
title: Manual review of both main PCBs (r2) before ordering
type: task
priority: P0
status: open
area: hw
created: 2026-11-05
---

# Manual review of both main PCBs (r2) before ordering

## Context

Both r2 boards (`hardware/left-pcb/k0d3ball35-left.kicad_pcb`, `hardware/right-pcb/k0d3ball35-right.kicad_pcb`)
are generated and autorouted; a human pass in the KiCad GUI with 3D models is still required before money is spent.

## Acceptance criteria

- [ ] Socket pad orientation matches a real CPG135001S30 (both boards)
- [ ] FH12-6S orientation on the right board: contacts towards the keys, cable exits towards the pocket (+y)
- [ ] MSK12C02 actuator reaches the inner board edge and can be moved from outside the case
- [ ] Silkscreen: `LEFT half` / `RIGHT half`, revision r2, pin names at the controller
- [ ] Controller USB-C overhang at the top edge, socket height vs battery underneath
- [ ] Five mounting holes per board clear switch bodies and sockets
- [ ] Right board: octagonal notch (apothem 15 mm) present, no copper, pour or via inside the notch or within 0.3 mm of its edge; no cradle holes anywhere
- [ ] Left board: three thumb positions, no FPC footprint, nine test pads (D0, D1, D2, D3, D9, D10, D14, D15, D16); right board: two thumb positions, five test pads
- [ ] Routed tracks reviewed for ugly detours near the controller and the thumb cluster on both boards

## Notes

Use `kicad-cli pcb render` outputs in `hardware/left-pcb/renders/` and `hardware/right-pcb/renders/` for a first look, then the GUI. Title kept for history; it covers both r2 boards.
