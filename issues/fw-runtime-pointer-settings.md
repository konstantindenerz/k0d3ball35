---
title: Runtime CPI steps, sniping toggle and auto-mouse timeout keys
type: feature
priority: P2
status: open
area: fw
created: 2026-11-05
---

# Runtime CPI steps, sniping toggle and auto-mouse timeout keys

## Context

holykeebs firmware exposes `HK_P_SET_*`, `HK_AML_UP/DN`, save and reset keycodes; Keyball has `CPI_I100`, `AML_I50`. Our keymap only has fixed values in the devicetree.

## Acceptance criteria

- [ ] CPI up/down and auto-mouse timeout up/down bound on the system layer
- [ ] Values persist across reboots or are editable in ZMK Studio
- [ ] Documented in docs/05-firmware.md

## Notes

None yet.
