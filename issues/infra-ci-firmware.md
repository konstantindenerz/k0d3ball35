---
title: CI build of both halves with ZMK
type: task
priority: P1
status: open
area: infra
created: 2026-11-05
---

# CI build of both halves with ZMK

## Context

GitHub Actions workflow building `k0d3ball36_left`, `k0d3ball36_right` and `settings_reset`
for `nice_nano//zmk` from `firmware/zmk-config`, uploading UF2 artifacts, plus a scheduled build so
breakage from ZMK main surfaces early.

## Acceptance criteria

- [ ] `.github/workflows/firmware.yml` green
- [ ] Weekly scheduled run
- [ ] UF2 files attached to GitHub releases on tags

## Notes

None yet.
