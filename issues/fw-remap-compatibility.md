---
title: Remap (remap-keys.app) compatibility
type: feature
priority: P3
status: open
area: fw
created: 2026-11-05
---

# Remap (remap-keys.app) compatibility

## Context

The user would like to configure the keyboard with https://remap-keys.app/ as on the Keyball. Remap speaks the
VIA protocol (QMK) and the BLE Micro Pro firmware; ZMK uses ZMK Studio instead and Remap cannot talk to it.
Possible paths:

- (a) BLE Micro Pro controller (Pro Micro footprint, pin compatible with the socket) running BMP firmware,
  configured with Remap. Wireless stays. Trackball support depends on a PMW3610 driver for BMP (the Keyball
  wireless kits use a PMW3360 daughterboard, so a driver port is needed).
- (b) Wired RP2040 Pro Micro (0xCB Helios, Sea-Picro) with QMK + VIA. QMK has a PMW3610 driver. Loses wireless.
- (c) Wait for Remap to support ZMK (not announced).

## Acceptance criteria

- [ ] A documented firmware variant that Remap can configure, in `firmware/` next to the ZMK config
- [ ] spec/05-firmware.md explains which controller/firmware combination to pick
- [ ] PMW3610 driver availability stated for the chosen path

## Notes

Pick this up when the ZMK build is proven on real hardware. ZMK Studio covers the keymap editing need until then.
