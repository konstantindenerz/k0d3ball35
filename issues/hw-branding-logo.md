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
off at the top; the generator mirrors the foot in to close it. An uncropped SVG would still be
welcome for the silkscreen path.

## Acceptance criteria

- [x] Logo file added to the repo (`docs/images/logo.png`), ownership noted in `NOTICE`
- [ ] PCB: logo as a silkscreen footprint in `hardware/lib/k0d3ball35.pretty/` (generated from the
      SVG with `kicad-cli` / bitmap2component or a small script in `scripts/`), placed by
      `scripts/k0d3/pcb.py` from a `branding:` block in the layout yaml (position, size, layer,
      per half), on the top face in the free area of the controller block beside the title text
      and on the bottom face under the thumb bridge; no silkscreen over pads (DRC gate stays clean,
      `tests/test_pcb_review.py` silk allowlist unchanged)
- [x] Case: the logo engraved 0.6 mm into the box cap plate (18.0 x 52.5 mm, 1.0 mm strokes) and
      into the flat case underside (52.5 x 18.0 mm, 0.9 mm strokes, turned 90 degrees), as
      parameters of the case model (`logo.scad`, `logo_*` in `params.scad`); printable without
      supports because both faces lie on the bed and no groove bridges further than one cell
- [ ] Transport lid (`mech-case-lid`) still has no logo; decide whether it needs one
- [ ] Silkscreen minimum feature 0.15 mm line / 0.8 mm text respected after scaling; checked on
      the renders and in the gerber viewer (`tests/test_gerbers.py` mask-overlap check stays at 0)
- [x] Image prompts in `docs/images/PROMPTS.md` updated (new `img-case-logo-cap`, the style
      anchor and the hero shots show the engraved wordmark)

## Notes

The case part is done (2026-11-06): generator, model, tests and docs are in `hardware/case/` and
`docs/11-case.md` section 8. What is left is the PCB silkscreen: that needs the artwork as a
KiCad footprint, so either an SVG from the owner or a converter from the same cell grid the case
uses - `logo_data.scad` already has the rectangles, a silkscreen generator could read the same
`gen_logo.build()` output.
