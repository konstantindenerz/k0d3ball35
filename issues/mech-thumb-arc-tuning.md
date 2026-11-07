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

Keyball owners report the thumb keys being hit by ball swipes and the arc not fitting all hand sizes. The arc offsets and rotations live in `hardware/layout/k0d3ball35.yaml`.

## Acceptance criteria

- [ ] Two arc variants printed as a flat switch-plate test piece
- [ ] Decision recorded in docs/02-layout.md
- [ ] Manual routes in the layout file re-checked after a change

## Notes

2026-11-06: since r2.3 the right half has only the two INNER thumb keys (10 and 20 degrees) at the same
positions as on the left; the inner 20 degree key exists on the left only. Variants therefore go
into `thumbs:` (shared positions) plus `halves.<side>.thumbs` (which keys a half uses); the right
half's ball pocket (centre (-13, +66), 28 mm clearance circle) limits how far the thumb keys can
move outward.
