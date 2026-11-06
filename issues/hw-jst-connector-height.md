---
title: JST-PH battery connector is 6 mm tall
type: task
priority: P2
status: done
area: hw
created: 2026-11-05
---

# JST-PH battery connector is 6 mm tall

## Context

S2B-PH-SM4-TB (J3) is 6 mm tall (5.5 mm per the datasheet), which is more than the 2 mm target for
bottom-side parts. Originally it was optional and the default was to solder the battery leads to the
pads J2 (B+ square pad, 2.54 mm pitch).

## Acceptance criteria

- [x] Case design (mech-case) decides whether J3 is populated and provides the pocket if so
- [x] Build guide tells builders how J3 is used

## Notes

A Molex Pico-EZmate (1.9 mm tall) is the low-profile alternative if a connector is wanted.

2026-11-06: resolved by `hw-battery-bay-both-halves`. Both halves now have a 9 mm deep battery
well under the controller block, J3 at (-56, 44) lies inside it below the bay, so J3 is populated on both halves
and the LP552035's JST-PH plug is the default connection (build guide chapter 7, BOM section 4).
