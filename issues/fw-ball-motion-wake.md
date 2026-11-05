---
title: Wake from deep sleep on ball motion
type: feature
priority: P3
status: open
area: fw
created: 2026-11-05
---

# Wake from deep sleep on ball motion

## Context

Deep sleep is key-wake only. Moving the ball does not wake the keyboard; the first key press does.

## Acceptance criteria

- [ ] Decide whether the MOT line should be a wake source (costs idle current)
- [ ] If implemented: documented in docs/05-firmware.md

## Notes

Keep off by default; most users accept a key press to wake.
