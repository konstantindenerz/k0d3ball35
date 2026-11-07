---
title: Order the first PCBs (left, right and sensor) at JLCPCB
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Order the first PCBs (left, right and sensor) at JLCPCB

## Context

Order 5 left PCBs, 5 right PCBs and 5 sensor PCBs (three designs since r2). Settings in
`docs/06-fabrication.md`: 2 layers, 1.6 mm, 1 oz, ENIG, tented vias, white silkscreen, remove order
number. Gerber zips: `hardware/left-pcb/k0d3ball35-left-gerbers.zip`,
`hardware/right-pcb/k0d3ball35-right-gerbers.zip`, `hardware/sensor-pcb/fab/k0d3ball35-sensor-r1-gerbers.zip`.
Shop-by-shop checklist in `docs/12-order-checklist.md`.

The pocket cradle test print is no longer a gate for the PCBs: the sensor height comes from
`hardware/trackball-cradle/params.scad`, not from any PCB; the right PCB notch is fixed by the layout
and its tests (`test_octagonal_notch`, apothem 15 mm, the 24.1 mm cradle inside the 30 mm notch); the
only outcome of the print that would change a PCB ("25 mm instead of 19 mm") cannot be tested without
the sensor PCB, so gating the order on it is circular. Exposure: one right-hand batch, about 30 to 40 EUR.

## Acceptance criteria

- [ ] `make erc drc test` green on the committed boards (`build/k0d3ball35-left.drc.json`, `build/k0d3ball35-right.drc.json`, `build/k0d3ball35-sensor.drc.json` with 0 violations, 0 unconnected, 0 parity issues)
- [x] Ticket `hw-left-pcb-mirror` done (the left board is the x mirror of the layout frame since 2026-11-06)
- [ ] Ticket `hw-sensor-vcsel-pins` resolved (P0): the PMW3610 laser pins confirmed against PMS0039.
      Blocks the **sensor** board only
- [ ] Ticket `hw-msk12c02-pad-pitch` resolved (P1): the three terminal pads confirmed against a physical
      switch. Blocks **both main** boards
- [ ] JLCPCB upload preview of the three zips checked: 2 layers, dimensions, no DFM complaint about the notch or the sensor window (user; `test-fab-gerber-viewer`)
- [ ] 1:1 paper check of a CPG135001S30 socket and the MSK12C02 on the printed plot (user; `hw-main-pcb-review-r1`)
- [ ] Order placed with the parameters from `docs/06-fabrication.md`, the three zips as committed at the tag
- [ ] Order number, cost and the git tag `v0.2.0-r2-order` recorded here

## Notes

Blockers: hw-two-pcbs-r2 done, hw-sensor-pcb-r1 done, mech-trackball-cradle done, hw-left-pcb-mirror done.
Open since the r2.3 review (2026-11-07): hw-sensor-vcsel-pins (P0, sensor board) and
hw-msk12c02-pad-pitch (P1, both main boards).
The committed zips at the tag are the reference.
Ticket name kept; it is the first order of the r2 boards.
