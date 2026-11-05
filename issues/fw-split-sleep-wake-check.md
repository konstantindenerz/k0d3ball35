---
title: Verify peripheral wake from deep sleep
type: task
priority: P2
status: open
area: fw
created: 2026-11-05
---

# Verify peripheral wake from deep sleep

## Context

torabo-tsuki users report the peripheral occasionally not waking. Our config uses a 30 min deep sleep timeout on both halves.

## Acceptance criteria

- [ ] After first assembly: 20 sleep/wake cycles on the peripheral, all wake within 2 s
- [ ] Timeouts adjusted in the shield conf if needed

## Notes

None yet.
