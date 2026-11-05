---
title: Support left-ball and dongle builds via zmk,input-split
type: feature
priority: P3
status: open
area: fw
created: 2026-11-05
---

# Support left-ball and dongle builds via zmk,input-split

## Context

The reversible PCB allows the ball on either half, and a three-piece dongle setup makes both halves
peripherals. ZMK supports forwarding pointer events from a peripheral with `zmk,input-split`. The r1
firmware scaffolds the node; this ticket makes it a tested build variant.

## Acceptance criteria

- [ ] Build variant with the sensor on the left half
- [ ] Build variant with a dongle central (nice!nano or XIAO) and both halves as peripherals
- [ ] Latency and battery impact noted in `docs/05-firmware.md`

## Notes

None yet.
