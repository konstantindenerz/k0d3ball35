---
title: Branding on the PCBs and the case with the owner's logo
type: feature
priority: P2
status: open
area: hw
created: 2026-11-06
---

# Branding on the PCBs and the case with the owner's logo

## Context

Both main PCBs currently carry only the text `k0d3ball35 r2  CERN-OHL-P-2.0` and `LEFT half` /
`RIGHT half` on the top silkscreen (placed by `scripts/k0d3/pcb.py` next to the controller). The
case has no branding at all yet. The owner's logo should appear on the PCBs and on the case so
the keyboard is recognisable as this project.

Logo source: a vector file (SVG, single colour, no gradients) supplied by the owner and stored in
`docs/images/logo.svg`; a monochrome PNG works for the silkscreen path as a fallback.

## Acceptance criteria

- [ ] Logo file added to the repo (`docs/images/logo.svg`), licence/ownership noted in `NOTICE`
- [ ] PCB: logo as a silkscreen footprint in `hardware/lib/k0d3ball35.pretty/` (generated from the
      SVG with `kicad-cli` / bitmap2component or a small script in `scripts/`), placed by
      `scripts/k0d3/pcb.py` from a `branding:` block in the layout yaml (position, size, layer,
      per half), on the top face in the free area of the controller block beside the title text
      and on the bottom face under the thumb bridge; no silkscreen over pads (DRC gate stays clean,
      `tests/test_pcb_review.py` silk allowlist unchanged)
- [ ] Case: the same logo embossed or debossed on the case bottom (centre of the controller
      block well is flat and large enough) and on the transport lid (`mech-case-lid`), as a
      parameter of the case model in `hardware/case/`; printable without supports
- [ ] Silkscreen minimum feature 0.15 mm line / 0.8 mm text respected after scaling; checked on
      the renders and in the gerber viewer (`tests/test_gerbers.py` mask-overlap check stays at 0)
- [ ] Image prompts in `docs/images/PROMPTS.md` updated (hero shots show the logo on the case)

## Notes

Blocked on the logo file. The PCB part can be done before the case phase; the case part belongs
to `mech-case` and `mech-case-lid`.
