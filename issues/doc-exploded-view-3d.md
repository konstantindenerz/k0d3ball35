---
title: Interactive 3D exploded view of one half
type: feature
priority: P2
status: done
area: doc
created: 2026-11-05
---

# Interactive 3D exploded view of one half

## Context

Readers (and the case phase) need to see where case, PCB, controller, battery, sockets, cradle,
sensor board and ball sit relative to each other before anything is printed. A single
self-contained HTML page (`docs/index.html`, three.js from cdnjs) animates the
stack of the right half from assembled to fully exploded, with labels, a section view through
the ball and a left-half mirror toggle. The page is generated from the layout data by
`docs/build.py`, so it follows `hardware/layout/k0d3ball35.yaml`.

## Acceptance criteria

- [x] Explode slider, auto-rotate, layer visibility, mirror and section toggles work
- [x] Geometry follows points-left.json / points-right.json / stack.json (r2: ball top +17.1 mm in the pocket beside the right PCB, PCB 1.6 mm, controller on 2.5 mm sockets, 702025 cell in the bay under the controller on both halves)
- [x] Light and dark theme, responsive, no external hosts besides cdnjs and Google Fonts
- [x] Linked from README; the page is self-contained and opens from the repo

## Notes

Case shell and plate are placeholders; the real case comes in the case phase (`mech-case`).
