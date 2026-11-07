---
title: Move the ball inboard and give the right half the two inner thumb keys
type: feature
priority: P1
status: done
area: hw
created: 2026-11-07
---

# Move the ball inboard and give the right half the two inner thumb keys

## Context

Until r2.3 the ball sat at (+5, 64): outboard of the whole thumb cluster, under the ring column,
and the right half dropped its INNER thumb key to make room. On the 1:1 measuring sheet the thumb
had to stretch outward for it.

Two things say that was the wrong way round. The geometry: the outer thumb key is the only thing
holding the ball out there - the cradle's 28 mm circle plus 1 mm of keycap clearance needs about
24 mm from the ball centre to the nearest thumb key centre, and the outer key sits at x -21.78, so
the ball cannot come inside x +2. Drop that key instead and the middle one at -42.14 allows the
ball down to about -15.

And the reference designs, read out of their own CAD rather than their marketing: Keyball 39/44/61
(Yowkees' KiCad plus gerbers) and torabo-tsuki LP (KiCad plus the ZMK layout) both drop the
OUTERMOST thumb key on the ball half and keep the inner ones; the Charybdis drops the two
outermost. None puts the ball under the ring or pinky column.

There is also an effect specific to a small ball: the thumb touches the ball's near surface, not
its centre, so going from Keyball's 34 mm to our 19.05 mm moves the touchable surface 7.5 mm
further away at the same centre. kepeo ships 7 mm and 10 mm inward-shifted cases for his 25 mm
conversion, and Kz - whose Keyball39ish this project starts from - calls his board the
"10 mm offset adapter". Keyball's constant scaled to our 18 mm pitch and radius-corrected lands at
index column + 6 mm; torabo-tsuki, same ball size, independently sits at + 7 mm.

## Acceptance criteria

- [x] Right half uses `thumb_middle` (10 deg) and `thumb_inner` (20 deg); the ball takes the outer
      position. Ball centre (-13.0, +66.0) = index column + 5 mm, 29.5 mm from the middle thumb key
- [x] `check_layout` clean on both halves; the left half's keys and outline are untouched
- [x] J1 follows the ball at `ball_x - 7.6` (the cradle's `cable_ch_x`), y chosen so the mouth stays
      inside the notch edge and the body keeps 0.5 mm from the index keycap
- [x] The fifth mounting hole, the test pad row and the back wordmark found new homes: the thumb
      cluster now occupies their old ones. All three are per-half in the layout file
- [x] Right board re-routed: seven hand routes for the 20 deg key and the crowded controller
      corridor, found by grid search and verified before the router ran. DRC clean with schematic
      parity, zero unconnected, first attempt
- [x] Firmware: right thumbs are matrix columns 3 and 4, transform cells `RC(3,9) RC(3,8)`;
      physical layout and keymap JSON regenerated, `check_pins` updated
- [x] Case: the hinge line follows the ball (`ball_x - 18`, so -31 on the right), `tent_deg` 15 to 18
      because the shorter kickstand needs a steeper fold, previews and exploded view rebuilt
- [x] Docs: design spec, layout, firmware, fabrication, feasibility, lessons, README

## Notes

Numbers after the move (right half): board 121.0 x 86.7 mm, the same as the left - the inner thumb
key is what sets both. Cradle to nearest keycap 5.18 mm (was 4.03). Ball to the two thumb keys 29.5
and 48.9 mm, against 27.1 and 47.2 before: the group moves as a whole, so the thumb's travel pattern
is unchanged and only its position relative to the fingers moves.

Kickstand reach dropped from 54 to 33.5 mm, i.e. the halves need less free desk between them.

Four variants of the move were drawn to scale before the decision.

Open for the test print: the thumb now has to reach x -62 for the inner key. If that turns out too
far, variant C of those four (the right half's thumb pair pulled 4 mm outward) is the fallback;
`mech-thumb-arc-tuning` is the ticket for it.
