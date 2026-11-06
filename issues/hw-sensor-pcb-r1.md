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

- [x] Schematic and PCB in `hardware/sensor-pcb/`, ERC and DRC clean
- [ ] Connector pin order matches hw-ffc-pin-order-verification
- [ ] Lens footprint and the two lens pins placed per the LM18-LSI drawing; sensor inserted from the back as in Keyball
- [x] Gerbers exported, BOM lines in `docs/03-bom.md`

## Notes

2026-11-06: `build/k0d3ball35-sensor.drc.json` reports 0 violations, 0 unconnected items, 0 schematic
parity issues; `build/k0d3ball35-sensor.erc.json` 0 violations. Gerbers (9 layers, PTH/NPTH drills, job
file) in `hardware/sensor-pcb/gerbers/`, zip, BOM and CPL in `hardware/sensor-pcb/fab/`, BOM lines in
`docs/03-bom.md` section 6.

Geometry against the cradle verified in `tests/test_sensor_pcb_vs_cradle.py` (table in
`issues/hw-sensor-pcb-constraints.md`): outline 26 x 25, holes 20 mm apart with the optical centre between
them, sensor cutout 16.96 x 8.60 at the datasheet position, tallest part 2.0 mm (J1) in the 2.25 mm gap,
J1 inside the 24 mm cable slot.

Lens: the LM18-LSI datasheet (PMS0039 R1.03, figure 1) gives a 12.90 x 8.25 mm base flange, a 10.29 x 6.55
upper body and two 0.90 mm guide posts, 5.95 mm tall overall. The posts engage the sensor body, not the
PCB, so the board needs no lens holes; the upper body passes the 16.96 x 8.60 cutout. The footprint's
`Dwgs.User` envelope still shows the earlier 17 x 17 guess and should be replaced by 12.9 x 8.25 in
`generate.py` before the lens item is ticked. The connector pin order needs the physical cable
(hw-ffc-pin-order-verification).
