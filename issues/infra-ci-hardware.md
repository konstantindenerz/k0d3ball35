---
title: CI gates for ERC, DRC and gerber export
type: task
priority: P1
status: open
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
- [x] KiCad version documented in `spec/06-fabrication.md`

## Notes

2026-11-05: `.github/workflows/hardware.yml` runs ERC, DRC with schematic parity and `scripts/export.sh` in the KiCad 10 container and uploads reports and gerbers; the KiCad-marked pytest job runs in a second job. A real green run needs the repository on GitHub, which is pending publication.

2026-11-07: reopened. The first runs on GitHub failed in both jobs, because `ghcr.io/kicad/kicad:10.0` is a bare Debian trixie that carries nothing beyond KiCad: `kicad-gates` died on `make: not found`, `kicad-pytest` on `ensurepip is not available` from `python3 -m venv`. Both jobs now install what they use first — `make` and `zip` (`scripts/export.sh` zips the gerbers) for the gates, `python3-venv` for the tests.

Verified in the container (`docker run ghcr.io/kicad/kicad:10.0`, same image and KiCad 10.0 as CI, repository mounted): `make erc` 0 violations on all three schematics, `make drc` 0 violations / 0 unconnected / 0 schematic parity issues on all three PCBs, `make gerbers` exports gerbers, drill, zip, STEP, renders, schematic PDF, BOM and position file for both halves, and `pytest -m kicad` is 8 passed.

Open from that run: `scripts/export.sh` takes `left|right` only, so the `gerbers` artifact has no `sensor-pcb/` even though the upload step lists it (`if-no-files-found: ignore` hides this). The second criterion stays unticked until the sensor PCB is exported too.
