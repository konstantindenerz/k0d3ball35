---
title: Main PCB revision 1 (reversible, 18 keys, controller, FPC, battery)
type: feature
priority: P0
status: in-progress
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

- [ ] Schematic generated and ERC clean (`make erc`)
- [ ] PCB routed, DRC clean with schematic parity (`make drc`), 2 layers, 1.6 mm
- [ ] Mirror check: left half equals the flipped right half (reversible), all footprints on one side
- [ ] Gerbers, drill, STEP and PNG renders exported into `hardware/main-pcb/`
- [ ] `docs/02-layout.md` and `docs/06-fabrication.md` updated

## Notes

None yet.
