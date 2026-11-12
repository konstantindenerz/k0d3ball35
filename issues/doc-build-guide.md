---
title: Step-by-step build guide
type: task
priority: P1
status: open
area: doc
created: 2026-11-05
---

# Step-by-step build guide

## Context

`spec/04-build-guide.md` following the structure of the Keyball39 guide: parts check, tools,
diodes, sockets, FPC connector, switches, controller on sockets with the battery underneath, sensor
board and lens, cradle and ceramic balls, ball, flashing, verification, finishing, troubleshooting.
Every picture is a prompt block.

## Acceptance criteria

- [x] All chapters written, each with an image prompt (`spec/04-build-guide.md`, 16 chapters)
- [x] Cross-references to BOM, firmware and testing docs resolve (checked by `tests/test_docs.py`)
- [x] Chapters 11 and 12 carry pictures rendered from the case model (`hardware/case/preview/guide-*.png`, `make case`); the soldering chapters keep their prompt blocks until there are photos
- [ ] Reviewed against the r2 PCB silkscreen on the first assembled boards

## Notes

Review on the first assembled r2 boards, see `hw-jlcpcb-order-r1`.
