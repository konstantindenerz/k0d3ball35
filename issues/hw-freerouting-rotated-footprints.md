---
title: Autorouter does not reach footprints rotated by 10 or 20 degrees
type: task
priority: P3
status: done
area: hw
created: 2026-11-05
---

# Autorouter does not reach footprints rotated by 10 or 20 degrees

## Context

Freerouting 2.5 fails every connection to the three thumb keys (rotated 10 and 20 degrees) and to their diodes, and in consequence gives up on COL3, COL4 and ROW3. Baking the rotation into the pads of a router copy did not change the result. The Specctra session also carries a placement block with the copy's 0 degree rotations that KiCad would apply on import.

## Acceptance criteria

- [x] Thumb cluster and the controller legs of COL3, COL4 and ROW3 are locked hand routes in `manual_routes` of `hardware/layout/k0d3ball35.yaml`
- [x] `scripts/route.py` strips the placement block from the SES before import
- [x] DRC with schematic parity clean after `scripts/build_board.sh`

## Notes

Resolved by the manual routes and the SES fix. If the thumb geometry changes, the manual routes in the layout file must be checked again (the pre-route DRC in `build_board.sh` catches collisions).
