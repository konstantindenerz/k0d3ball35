---
title: Order r1 PCBs (main and sensor) at JLCPCB
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Order r1 PCBs (main and sensor) at JLCPCB

## Context

Order 5 main PCBs and 5 sensor PCBs. Settings: 2 layers, 1.6 mm, 1 oz, ENIG, black or white
soldermask, remove order number or specify location. Checklist in `docs/06-fabrication.md`.

## Acceptance criteria

- [ ] Blocked until `make drc` passes for both boards and the cradle test print confirms the sensor height
- [ ] Gerber zip from the CI artifact of the tagged commit
- [ ] Order confirmation and cost recorded in the ticket

## Notes

Blocked by hw-main-pcb-r1, hw-sensor-pcb-r1, mech-trackball-cradle.
