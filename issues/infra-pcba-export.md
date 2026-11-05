---
title: PCBA order option (position file, BOM with LCSC numbers)
type: feature
priority: P3
status: open
area: infra
created: 2026-11-05
---

# PCBA order option (position file, BOM with LCSC numbers)

## Context

For builders who do not want to solder diodes and sockets, JLCPCB assembly needs a BOM with LCSC part numbers and a position file; `scripts/export.sh` already writes `k0d3ball36-pos.csv` and a BOM without LCSC fields. The PMW3610 is C42442560 (extended part).

## Acceptance criteria

- [ ] BOM export carries LCSC numbers for diodes, sockets, connectors, switch and reset button
- [ ] Position file verified against the JLCPCB preview (rotation of the sockets)
- [ ] Documented in docs/06-fabrication.md

## Notes

None yet.
