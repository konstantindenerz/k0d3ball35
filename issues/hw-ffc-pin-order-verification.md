---
title: Verify the 6-pin FFC pin order between main PCB and sensor PCB
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Verify the 6-pin FFC pin order between main PCB and sensor PCB

## Context

Both FPC connectors are bottom-contact and sit on the top side of their boards. With a same-side
(type A) 0.5 mm cable the pin order either maps 1 to 1 or mirrored depending on how the two connectors
face each other. The main PCB pin order is fixed in the design spec (3V3, GND, SCLK, SDIO, NCS, MOT).
The sensor PCB chooses its order to match. A mistake here swaps 3V3 and MOT and may kill the sensor.

## Acceptance criteria

- [ ] Pin order on both boards drawn in one diagram with the cable in between, in `docs/08-trackball-module.md`
- [ ] Physical check with a cable and two connectors on breakout boards, or a continuity test on the first PCBs before the sensor is connected
- [ ] `tests/test_netlist.py` cross-checks main PCB connector nets against the sensor PCB connector nets

## Notes

torabo-tsuki-lp uses a 6-pin FFC between main board and sensor module; its schematics are a cross-check.
