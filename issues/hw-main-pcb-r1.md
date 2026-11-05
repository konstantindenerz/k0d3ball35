---
title: Main PCB revision 1 (reversible, 18 keys, controller, FPC, battery)
type: feature
priority: P0
status: done
area: hw
created: 2026-11-05
---

# Main PCB revision 1 (reversible, 18 keys, controller, FPC, battery)

## Context

The reversible main PCB per `docs/01-design-spec.md`: 3x5 + 3 thumb keys at 18 x 17 mm, Choc V1 hot-swap
plus solder pads, 1N4148W SOD-123 diodes, socketed Pro Micro footprint for nice!nano v2, 6-pin FPC
connector, JST-PH battery pads plus bare-lead pads, MSK-12C02 power switch, reset button, ball zone
cutout with cradle holes, M2 case mounting holes. Geometry comes from `hardware/layout/k0d3ball36.yaml`.

## Acceptance criteria

- [x] Schematic generated and ERC clean (`make erc`)
- [x] PCB routed, DRC clean with schematic parity (`make drc`), 2 layers, 1.6 mm
- [x] Mirror check: left half equals the flipped right half (reversible), all footprints on one side
- [x] Gerbers, drill, STEP and PNG renders exported into `hardware/main-pcb/`
- [x] `docs/02-layout.md` and `docs/06-fabrication.md` updated

## Notes

2026-11-05: schematic generated, ERC clean at all severities; board autorouted with freerouting through `scripts/build_board.sh` (retries until clean), the rotated thumb keys and the controller legs of COL3/COL4/ROW3 are hand-routed in `manual_routes`; DRC with schematic parity reports zero errors (warnings only: diode courtyards under the switches, silkscreen overlaps); gerbers, drill, STEP, schematic PDF, BOM, position file and renders exported with `scripts/export.sh`. r1 is hot-swap only (see hw-hotswap-only). Ordering is gated by `hw-main-pcb-review-r1`, `test-fab-gerber-viewer` and `hw-jlcpcb-order-r1`.
