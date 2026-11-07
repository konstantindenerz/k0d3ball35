---
title: Verify trackball cursor axes on the first board
type: task
priority: P1
status: open
area: fw
created: 2026-11-05
---

# Verify trackball cursor axes on the first board

## Context

`invert-x`, `invert-y` and the axis mapping of the PMW3610 node are untested guesses. Sensor orientation inside
the cradle decides the real directions.

## Acceptance criteria

- [ ] Cursor moves in the expected direction on the first assembled right half
- [ ] Overlay updated if needed, note added to spec/05-firmware.md

## Notes

Keyball community configs needed per-axis scaling because of ball/sensor geometry; check whether that applies here.
