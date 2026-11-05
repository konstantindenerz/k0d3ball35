---
title: Interactive 3D exploded view of one half
type: feature
priority: P2
status: in-progress
area: doc
created: 2026-11-05
---

# Interactive 3D exploded view of one half

## Context

Readers (and the case phase) need to see where case, PCB, controller, battery, sockets, cradle,
sensor board and ball sit relative to each other before anything is printed. A single
self-contained HTML page (`docs/exploded-view/index.html`, three.js from cdnjs) animates the
stack of the right half from assembled to fully exploded, with labels, a section view through
the ball and a left-half mirror toggle. The page is generated from the layout data by
`docs/exploded-view/build.py`, so it follows `hardware/layout/k0d3ball36.yaml`.

## Acceptance criteria

- [ ] Explode slider, auto-rotate, layer visibility, mirror and section toggles work
- [ ] Geometry follows points.json / stack.json (ball top +23 mm, PCB 1.6 mm, controller on 3.5 mm sockets)
- [ ] Light and dark theme, responsive, no external hosts besides cdnjs and Google Fonts
- [ ] Linked from README and published as an artifact

## Notes

Case shell and plate are placeholders; the real case comes in the case phase (`mech-case`).
