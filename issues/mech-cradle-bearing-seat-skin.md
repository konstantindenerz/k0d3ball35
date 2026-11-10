---
title: Bearing seats in the cradle start exactly at the cup surface
type: bug
priority: P3
status: open
area: mech
created: 2026-11-10
---

# Bearing seats in the cradle start exactly at the cup surface

## Context

In `hardware/trackball-cradle/stl/cradle-*.stl` each bearing seat hole starts at the cup radius
(R + 0.4). The cup sphere is faceted, so between the facets the hole is covered by a skin up to
0.04 mm thick and is a closed void under the cup surface instead of an opening. A slicer will
usually drop a skin that thin, but some treat the void oddly.

Found while building the Trackball tab of the project page.

## Acceptance criteria

- [ ] Start the seat a little inside the cup (for example R + 0.4 - 0.2) so the hole always cuts through
- [ ] A test checks the seat opening in the exported STL is open (no closed void)
