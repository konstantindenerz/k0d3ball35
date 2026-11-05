---
title: CI gates for ERC, DRC and gerber export
type: task
priority: P1
status: in-progress
area: infra
created: 2026-11-05
---

# CI gates for ERC, DRC and gerber export

## Context

GitHub Actions job running inside the official KiCad container: ERC on all schematics, DRC with
schematic parity on all PCBs, gerber and drill export, artifacts uploaded. KiCad major version
pinned; the same commands run locally through the Makefile.

## Acceptance criteria

- [ ] `.github/workflows/hardware.yml` green on a push touching `hardware/`
- [ ] Gerber zip per PCB downloadable as an artifact
- [ ] KiCad version documented in `docs/06-fabrication.md`

## Notes

None yet.
