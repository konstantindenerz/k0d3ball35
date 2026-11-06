---
title: Expose and test-print thumb arc variants
type: task
priority: P2
status: open
area: mech
created: 2026-11-05
---

# Expose and test-print thumb arc variants

## Context

Keyball owners report the thumb keys being hit by ball swipes and the arc not fitting all hand sizes. The arc offsets and rotations live in `hardware/layout/k0d3ball36.yaml`.

## Acceptance criteria

- [ ] Two arc variants printed as a flat switch-plate test piece
- [ ] Decision recorded in docs/02-layout.md
- [ ] Manual routes in the layout file re-checked after a change

## Notes

2026-11-06: since r2 the right half has only the two outer thumb keys (0 and 10 degrees) at the same
positions as on the left; the inner 20 degree key exists on the left only. Variants therefore go
into `thumbs:` (shared positions) plus `halves.<side>.thumbs` (which keys a half uses); the right
half's ball pocket (centre (+5, +64), 28 mm clearance circle) limits how far the outer thumb key can
move outward.
