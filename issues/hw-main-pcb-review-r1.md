---
title: Manual review of the main PCB before ordering
type: task
priority: P0
status: open
area: hw
created: 2026-11-05
---

# Manual review of the main PCB before ordering

## Context

The board is generated and autorouted; a human pass in the KiCad GUI with 3D models is still required before
money is spent.

## Acceptance criteria

- [ ] Socket pad orientation matches a real CPG135001S30 on both faces
- [ ] FH12-6S orientation: contacts towards the controller side, cable exits towards the ball zone
- [ ] MSK12C02 actuator reaches the inner board edge and can be moved from outside the case
- [ ] Jumper silkscreen (JP1 RAW, JP2 RST, JP3 VCC) readable on both faces
- [ ] Controller USB-C overhang at the top edge, socket height vs battery underneath
- [ ] Mounting hole positions clear switch bodies and sockets
- [ ] Cradle holes on the 36 mm circle, 30 mm cutout
- [ ] Test pad labels correct per half
- [ ] Routed tracks reviewed for ugly detours near the controller and the thumb cluster

## Notes

Use `kicad-cli pcb render` outputs in `hardware/main-pcb/renders/` for a first look, then the GUI.
