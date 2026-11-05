---
title: PMW3610 sensor daughterboard revision 1
type: feature
priority: P0
status: in-progress
area: hw
created: 2026-11-05
---

# PMW3610 sensor daughterboard revision 1

## Context

Own 22 x 25 mm sensor board: PMW3610DM-SUDU, LM18-LSI lens, 1.8 V LDO from 3.3 V, decoupling,
6-pin 0.5 mm FPC connector, 2x M2 holes at 20 mm spacing. Reference circuit: bullwinkle3000/pmw3610-pcb
(CERN-OHL-P-2.0). Hand-solderable; JLCPCB can place the sensor (part C42442560) for a later batch.

## Acceptance criteria

- [ ] Schematic and PCB in `hardware/sensor-pcb/`, ERC and DRC clean
- [ ] Connector pin order matches hw-ffc-pin-order-verification
- [ ] Lens footprint and the two lens pins placed per the LM18-LSI drawing; sensor inserted from the back as in Keyball
- [ ] Gerbers exported, BOM lines in `docs/03-bom.md`

## Notes

None yet.
