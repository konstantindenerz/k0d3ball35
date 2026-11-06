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

Order 5 left PCBs, 5 right PCBs and 5 sensor PCBs (three designs since r2). Settings: 2 layers,
1.6 mm, 1 oz, ENIG, black or white soldermask, remove order number or specify location. Checklist in
`docs/06-fabrication.md`. Gerber zips: `hardware/left-pcb/k0d3ball35-left-gerbers.zip`,
`hardware/right-pcb/k0d3ball35-right-gerbers.zip`, `hardware/sensor-pcb/`.

## Acceptance criteria

- [ ] Blocked until `make drc` passes for all three boards and the pocket cradle test print confirms the sensor height and the notch clearance
- [ ] Gerber zip from the CI artifact of the tagged commit
- [ ] Order confirmation and cost recorded in the ticket

## Notes

Blocked by hw-two-pcbs-r2, hw-sensor-pcb-r1, mech-trackball-cradle. Ticket name kept; it is the first order of the r2 boards.
