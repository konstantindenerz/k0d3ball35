---
title: JST-PH battery connector is 6 mm tall
type: task
priority: P2
status: open
area: hw
created: 2026-11-05
---

# JST-PH battery connector is 6 mm tall

## Context

S2B-PH-SM4-TB (J3) is 6 mm tall, which is more than the 2 mm target for bottom-side parts. It is optional; the
default is to solder the battery leads to the pads J2 (B+ square pad, 2.54 mm pitch).

## Acceptance criteria

- [ ] Case design (mech-case) decides whether J3 is populated and provides the pocket if so
- [ ] Build guide tells builders to leave J3 empty unless the case allows it

## Notes

A Molex Pico-EZmate (1.9 mm tall) is the low-profile alternative if a connector is wanted.
