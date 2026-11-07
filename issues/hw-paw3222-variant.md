---
title: Sensor board variant with PAW3222 for lower power
type: feature
priority: P3
status: open
area: hw
created: 2026-11-05
---

# Sensor board variant with PAW3222 for lower power

## Context

The PAW3222 draws roughly half the running current of the PMW3610 and comes as a flat module
in torabo-tsuki-lp. A pin-compatible 6-pin sensor board variant would extend battery life on the
trackball half without touching the main PCB.

## Acceptance criteria

- [ ] Sensor board variant with the same 6-pin pinout and mounting holes
- [ ] ZMK build using sekigon-gonnoc/zmk-driver-paw3222
- [ ] Measured current comparison in `spec/08-trackball-module.md`

## Notes

None yet.
