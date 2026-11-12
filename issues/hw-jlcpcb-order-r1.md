---
title: Order the first PCBs (left and right) at JLCPCB
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Order the first PCBs (left and right) at JLCPCB

## Context

Order 5 left PCBs and 5 right PCBs (two designs; since r2.4 the sensor is a bought PAW3222 module,
there is no sensor board of ours). Settings in `spec/06-fabrication.md`: 2 layers, 1.6 mm, 1 oz,
ENIG, tented vias, white silkscreen, remove order number. Gerber zips:
`hardware/left-pcb/k0d3ball35-left-gerbers.zip`, `hardware/right-pcb/k0d3ball35-right-gerbers.zip`.
Shop-by-shop checklist in `spec/12-order-checklist.md`.

The boards changed in the 2026-11-12 review (`mech-review-fixes-test-print`): mounting holes H1/H2
moved off the hot-swap sockets, the reset button turned to the inner edge, + / - printed at J3.
Zips older than that review must not be ordered.

## Acceptance criteria

- [ ] `make erc drc test` green on the committed boards (`build/k0d3ball35-left.drc.json`, `build/k0d3ball35-right.drc.json`: 0 errors, 0 unconnected, parity only PS1 pad 3, which is unconnected on purpose)
- [x] Ticket `hw-left-pcb-mirror` done (the left board is the x mirror of the layout frame since 2026-11-06)
- [x] Ticket `hw-msk12c02-pad-pitch` done (pads equal KiCad's SW_SPDT_Shouhan_MSK12C02)
- [ ] JLCPCB upload preview of the two zips checked: 2 layers, about 121 x 87 mm, no DFM complaint about the notch (user; `test-fab-gerber-viewer`)
- [ ] 1:1 paper check of a CPG135001S30 socket, the MSK12C02 and the EVQ-P7A on the printed plot, parts in hand (user; `hw-main-pcb-review-r1`). Socket pad 1 is 0.45 mm off the kiswitch position on purpose
- [ ] Order placed with the parameters from `spec/06-fabrication.md`, the two zips as committed at the tag
- [ ] Order number, cost and the git tag `v0.2.0-r2-order` recorded here

## Notes

Blockers: hw-two-pcbs-r2 done, hw-sensor-pcb-r1 done, mech-trackball-cradle done, hw-left-pcb-mirror done.
The sensor board tickets (hw-sensor-pcb-r1, hw-sensor-vcsel-pins) ended with the board in r2.4.
The committed zips at the tag are the reference.
Ticket name kept; it is the first order of the r2 boards.
