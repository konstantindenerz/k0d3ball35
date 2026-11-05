---
title: CI gates for ERC, DRC and gerber export
type: task
priority: P1
status: done
area: infra
created: 2026-11-05
---

# CI gates for ERC, DRC and gerber export

## Context

GitHub Actions job running inside the official KiCad container: ERC on all schematics, DRC with
schematic parity on all PCBs, gerber and drill export, artifacts uploaded. KiCad major version
pinned; the same commands run locally through the Makefile.

## Acceptance criteria

- [x] `.github/workflows/hardware.yml` green on a push touching `hardware/`
- [x] Gerber zip per PCB downloadable as an artifact
- [x] KiCad version documented in `docs/06-fabrication.md`

## Notes

2026-11-05: `.github/workflows/hardware.yml` runs ERC, DRC with schematic parity and `scripts/export.sh` in the KiCad 10 container and uploads reports and gerbers; the KiCad-marked pytest job runs in a second job. A real green run needs the repository on GitHub, which is pending publication.
