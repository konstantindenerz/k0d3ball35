---
title: Branding on the PCBs and the case with the owner's logo
type: feature
priority: P2
status: in-progress
area: hw
created: 2026-11-06
---

# Branding on the PCBs and the case with the owner's logo

## Context

Both main PCBs currently carry only the text `k0d3ball35 r2  CERN-OHL-P-2.0` and `LEFT half` /
`RIGHT half` on the top silkscreen (placed by `scripts/k0d3/pcb.py` next to the controller). The
case has no branding at all yet. The owner's logo should appear on the PCBs and on the case so
the keyboard is recognisable as this project.

Logo source: the owner supplied the `kode` labyrinth wordmark as a two-colour PNG, stored as
`docs/images/logo.png`. It is drawn on a strict cell grid, so `scripts/gen_logo.py` recovers the
grid instead of tracing the bitmap: 18 x 35 cells, one stroke per cell. The crop cuts the frame
off at the top; the generator mirrors the foot in to close it. `scripts/gen_logo.py` also writes `docs/images/logo.svg` from the same rectangles, so the
vector master exists in the repo and nothing downstream has to touch the raster again.

## Acceptance criteria

- [x] Logo file added to the repo (`docs/images/logo.png` and the generated
      `docs/images/logo.svg`), ownership noted in `NOTICE`
- [x] PCB: wordmark on the **back** silkscreen under the thumb bridge, centre (-35, 48.4),
      13.9 x 4.7 mm, 0.26 mm strokes, from a `silkscreen.logo` block in the layout yaml and
      emitted by `scripts/k0d3/pcb.py` as 34 filled `gr_poly` polygons from `k0d3.logo`. Not a
      footprint and not on the front, see Notes. No silkscreen over pads, DRC clean on the first
      routing attempt for both halves, `SILK_OVER_COPPER_ACCEPTED` unchanged
- [x] Case: the logo engraved 0.6 mm into the box cap plate (18.0 x 52.5 mm, 1.0 mm strokes), as
      parameters of the case model (`logo.scad`, `logo_*` in `params.scad`); printable without
      supports because the face lies on the bed and no groove bridges further than one cell.
      The floor engraving (52.5 x 18.0 mm, 0.9 mm strokes, turned 90 degrees) was dropped on
      2026-11-07 (did not look right); it stays in the model behind `logo_on_floor = false`
- [ ] Transport lid (`mech-case-lid`) still has no logo; decide whether it needs one
- [x] Silkscreen minimum feature respected: strokes and gaps are 0.26 mm, 1.7 times the 0.15 mm
      a fab holds; `tests/test_gerbers.py` mask overlap still 0 on all six faces and the rendered
      bottom layer shows strokes and gaps cleanly separated
- [x] Image prompts in `docs/images/PROMPTS.md` updated (new `img-case-logo-cap`, the style
      anchor and the hero shots show the engraved wordmark)

## Notes

The case part is done (2026-11-06): generator, model, tests and docs are in `hardware/case/` and
`docs/11-case.md` section 8. The PCB silkscreen is done (2026-11-06) with two deliberate deviations from the criteria above.

**Back face only, not both.** The mark is 18 x 35 cells, a 1 : 2.96 aspect. Measured against
pads, courtyards and the existing silk, the widest free bands are about 5 mm tall on either
face, so the stroke width is what the band height buys: 0.26 mm on the back under the thumb
bridge (39 mm of width to spare), 0.24 mm on the front squeezed between the title text and the
reset and JST courtyards, with 0.07 mm to the title - close enough that `silk_overlap` would
flag it and `test_pcb_review` does not tolerate that on the front. One legible mark beat two
cramped ones.

**A board polygon, not a footprint.** The wordmark has no pads and no net. As a footprint it
would be a part without a schematic symbol, which `kicad-cli pcb drc --schematic-parity`
reports; `scripts/k0d3/pcb.py` already draws board-level `gr_poly` on silkscreen for the battery
bay, so the mark follows that.

What is left: whether the transport lid gets the logo too (`mech-case-lid`).
