---
title: r2 - two PCBs (15+3 / 15+2), stepped outline, 19 mm ball pocket beside the right PCB
type: feature
priority: P0
status: in-progress
area: hw
created: 2026-11-06
---

# r2 - two PCBs (15+3 / 15+2), stepped outline, 19 mm ball pocket beside the right PCB

## Context

r1 used one reversible PCB for both halves. That forced three solder jumpers for the power rows, a
sacrificed D0, a mirrored controller pin map on the left half, a dead 30 mm ball cutout on the left,
and a 25 mm ball whose top sat 23 mm above the PCB. The user rejected it as not flat and compact
enough. r2 (decided 2026-11-06, see `docs/01-design-spec.md`):

- Two separate PCBs: left 15 finger + 3 thumb keys, right 15 finger + 2 thumb keys (the two outer
  ones at 0 and 10 degrees, same positions as on the left). 35 keys. Identical controller wiring on
  both boards, no jumpers, D0 free again.
- Outline variant A "steps": 90 degree steps following the column stagger, corner radius 0,
  rectangular controller block at the inner edge, thumb bridge. Left 121.0 x 86.7 mm, right
  117.8 x 80.4 mm.
- 19.05 mm POM ball in a case pocket beside the right PCB (centre (+5, +64), octagonal notch with
  apothem 15 mm, pocket circle 32 mm, sensor board on the case floor 11.6 mm below the PCB top).
  25 mm stays a cradle parameter. Research behind the size in `docs/00-feasibility.md` section 4a.
- Ball top drops from about 23 to 17.1 mm above the PCB top.

## Acceptance criteria

- [x] Layout yaml with a `halves:` section, geometry per half, `points-left.json` / `points-right.json`,
      `outline-*.dxf`, previews, layout checks (18 / 17 keys, pocket clearance) - commit cb2d951
- [x] Cradle `mount = "pocket"` variant, 19.05 mm default, `stack.json`, STL / DXF exports, tests
- [x] Documentation r2: design spec, layout, BOM, build guide, firmware, fabrication, testing,
      trackball module, roadmap, lessons, feasibility, README, image prompts, exploded view, tickets
- [ ] Netlist, schematic and PCB generators per half; `hardware/left-pcb/` and `hardware/right-pcb/`
      generated, ERC clean
- [ ] Both boards routed (freerouting plus hand routes), DRC clean with schematic parity, gerbers,
      renders, schematic PDFs, BOM and position files exported; `hardware/main-pcb/` removed
- [ ] Firmware: shield with 35 keys, one shared kscan pin set, transform row 3 per half,
      `res-cpi = <600>`, physical layout regenerated, pin checker against the single spec table
- [ ] `make test` green, CI workflows point at the new paths
- [ ] Optional last step: rename to k0d3ball35 (folder, shield, libraries, yaml)

## Notes

Agent split: geometry (done), netlist/schematic/pcb/scripts, firmware, cradle + docs + tickets
(done), then one pass with freerouting per half and the README renders. The right PCB render must
show the octagonal notch with no copper inside it.
