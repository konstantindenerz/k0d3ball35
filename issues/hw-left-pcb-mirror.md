---
title: Left PCB is not mirrored (second right-handed board)
type: bug
priority: P0
status: open
area: hw
created: 2026-11-06
---

# Left PCB is not mirrored (second right-handed board)

## Context

`hardware/left-pcb/k0d3ball35-left.kicad_pcb` and `hardware/right-pcb/k0d3ball35-right.kicad_pcb`
have identical footprint coordinates: SW00 at (156.0, 70.44) and U1 at (62.0, 71.7) on both boards
(page offset (120, 60), so frame x = +36 and -58 on both). The layout frame ("x outward towards the
pinky, y towards the user, origin middle-column top key") is shared by both halves and
`netlist.build_components` / `pcb.build_pcb` copied it 1:1 onto both boards. The left board was
therefore a second right-handed board: controller block at the pinky side, thumb arc bending the
wrong way. r1 was one reversible PCB that was flipped over for the left half; r2 dropped the flip and
the mirror never came. This blocks the PCB order.

## Rule

The layout frame is handedness-neutral. Every physical artefact of the left half (PCB, case, lid)
mirrors x: `Layout.to_board(x, y) = (board_sx * x, y)` with `board_sx = -1` on the left. The frame
itself, `points-*.json`, `outline-*.dxf`, the docs tables and `tests/test_geometry.py` stay unchanged.
Footprints are not mirrored (parts are chiral, nets hang on pads); rotations become `-rot`.

## Acceptance criteria

- [ ] `netlist.build_components` and `pcb.build_pcb` place everything through `Layout.to_board`
      (components, outline, silkscreen, keep-out ring, stitching vias, pour bounds, manual routes)
- [ ] Left board regenerated and rerouted, ERC and DRC (with schematic parity) clean
- [ ] Left gerbers, zip, STEP, renders, BOM and position file refreshed; right board untouched
- [ ] Mirror test: on the left board SW00 sits at frame x = -36, U1 at +58, the outline bounds are
      the mirrored layout bounds (`tests/test_pcb_review.py`, `tests/test_gerbers.py`)
- [ ] Docs state the rule (01-design-spec, 02-layout) and the fabrication checklist notes that the two
      boards are not interchangeable
