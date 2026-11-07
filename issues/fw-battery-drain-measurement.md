---
title: Measure real battery drain per half
type: task
priority: P2
status: open
area: fw
created: 2026-11-05
---

# Measure real battery drain per half

## Context

spec/05-firmware.md gives datasheet-based runtime estimates. Real numbers depend on sleep settings, BLE interval,
sensor rest modes and the actual cells.

## Acceptance criteria

- [ ] Current measured on both halves (idle, typing, trackball use) with the production config
- [ ] spec/05-firmware.md estimates replaced by measured values

## Notes

Needs an assembled board. Use a USB power meter on the battery line or a Nordic PPK2.
