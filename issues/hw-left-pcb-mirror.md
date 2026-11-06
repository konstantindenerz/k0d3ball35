---
title: Left PCB is not mirrored (second right-handed board)
type: bug
priority: P0
status: done
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

- [x] `netlist.build_components` and `pcb.build_pcb` place everything through `Layout.to_board`
      (components, outline, silkscreen, keep-out ring, stitching vias, pour bounds, manual routes)
- [x] Left board regenerated and rerouted, ERC and DRC (with schematic parity) clean
- [x] Left gerbers, zip, STEP, renders, BOM and position file refreshed; right board untouched
- [x] Mirror test: on the left board SW00 sits at frame x = -36, U1 at +58, the outline bounds are
      the mirrored layout bounds (`tests/test_pcb_review.py`, `tests/test_gerbers.py`)
- [x] Docs state the rule (01-design-spec, 02-layout) and the fabrication checklist notes that the two
      boards are not interchangeable

## Notes

2026-11-06: done. `Layout.board_sx` / `Layout.to_board` in `scripts/k0d3/geometry.py`;
`netlist.build_components` places every part through it with `rotation -> -rotation` (the diodes
at 0/10/20 degrees, PS1 at 270 -> 90 so the actuator still points through the inner edge);
`pcb.build_pcb` mirrors the outline, pocket reference, bay silkscreen, title text, edge keep-out,
stitching vias, pour bounds and the free points of the hand routes. Footprint-local offsets (joiner
stub, column bus at x - 2.6, FPC stub) stay local.

The left hand routes had to be redesigned, not just mirrored: pad references (`D33:1`, `SW24:bus`,
`SW34:pad2`) resolve on the unmirrored footprint while the free points mirror, so the old points
crossed switch holes and diode pads. The new routes are documented in the yaml. The rerouted left
board is DRC clean (0 violations, 0 unconnected, 0 parity issues) and ERC clean; the right board is
byte-identical.

Follow-up found on the way: the inner column's hot-swap sockets reach 2.8 mm into the left battery
bay (`hw-left-bay-inner-sockets`).
