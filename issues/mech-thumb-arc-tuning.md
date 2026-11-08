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
- [ ] Decision recorded in spec/02-layout.md
- [ ] Manual routes in the layout file re-checked after a change

## Notes

2026-11-06: since r2.3 the right half has only the two INNER thumb keys (10 and 20 degrees) at the same
positions as on the left; the inner 20 degree key exists on the left only. Variants therefore go
into `thumbs:` (shared positions) plus `halves.<side>.thumbs` (which keys a half uses); the right
half's ball pocket (centre (-13, +66), 28 mm clearance circle) limits how far the thumb keys can
move outward.

## Measured thumb reach (r2.3 review, 2026-11-07)

Numbers for the print check, so there is something to compare against instead of a feeling. Right
half, nearest thumb key is `thumb_middle` at (-42.14, 61.26), ball centre (-13.0, 66.0), radius
9.525 mm:

- thumb key centre to ball **centre**: 29.5 mm
- thumb key centre to ball **surface**, which is what the thumb actually touches: **20.0 mm**
- ball equator at z +7.58 mm, keycap tops at +11.0 mm, so the thumb has to drop **3.4 mm below the
  keycap plane** to reach the widest point of the ball
- the equator sits in a 4.5 mm wide annular trench between the ball and the pocket wall
  (`cradle_d` 28, inner radius 14, ball radius 9.525), with the tray rim at +5.0

That is a longer reach and a deeper drop than the Keyball39, where a 34 mm ball brings its surface
much closer to the thumb at the same centre distance. The layout comment "the ball sits where the
outer thumb key used to be" is true of the ball's near **surface** (about (-22.4, 64.4), 4.8 mm from
the old key centre at (-21.78, 59.65)) but not of its centre, which is 8.8 mm further outboard and
6.4 mm closer to the user.

This is the only review finding whose fix is a layout change, so it has to be answered before the
PCB order rather than after. Print both sheets from `make print-check`, put a real Choc switch with
an MBK cap on them, stack something 17.1 mm tall at the ball position and try the motion. Variant C
of the outline artefact (right thumb pair pulled 4 mm outward) is the fallback.

**2026-11-08:** the sheet now carries what this decision needs instead of leaving it to be worked
out on the desk. Each travel line gets a tick where it crosses the ball circle and a legend line
for the reach to that crossing (SW33 20.0 mm, SW34 39.39 mm) - the centre distance alone reads as
reachable when it is not - and section 3 names the stack height, read from the cradle's
`stack.json`, so the 25 mm fallback would change the paper by itself.
