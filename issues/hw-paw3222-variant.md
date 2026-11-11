---
title: PAW3222 sensor module as the trackball sensor
type: feature
priority: P1
status: in-progress
area: hw
created: 2026-11-05
---

# PAW3222 sensor module as the trackball sensor

## Context

Since r2.4 the trackball sensor is the bought 14 x 8 mm PAW3222 module (the one torabo-tsuki LP
uses), not our own PMW3610 board. It is narrow enough in the tilt plane to sit 65 degrees beside
the ball, which made the flatter stack possible (`mech-ball-height-23mm`), it draws roughly half
the PMW3610's tracking current, and it takes a board out of fabrication.

Source: beekeeb (ships worldwide, free shipping from 80 USD) or BOOTH; shipping to the EU is
accepted (`spec/03-bom.md`, `spec/12-order-checklist.md`).

## Acceptance criteria

- [x] Cradle with the tilted sleeve for the module (`hardware/trackball-cradle/`)
- [x] J1 on the right PCB re-ordered to the module's pinout: 1 3.3V, 2 CS, 3 MOTION, 4 SDIO, 5 SCLK, 6 GND (`hw-ffc-pin-order-verification`)
- [x] `hardware/sensor-pcb/` and its tests removed; spec, BOM and build guide describe the module
- [ ] Module ordered and its pinout checked on arrival
- [ ] ZMK: `sekigon-gonnoc/zmk-driver-paw3222` as a second west project, `CONFIG_INPUT_PAW32XX`, the sensor node's `compatible`, and axis scaling for the 65 degree tilt in the `trackball_listener` (`fw-cpi-tuning-19mm`)
- [ ] Measured current comparison in `spec/08-trackball-module.md`

## Notes

Was a P3 "sensor board variant for lower power" until 2026-11-11. The module's lens values are
nominal (no PixArt assembly drawing); the ball height does not depend on them.
