---
title: Plug-on sensor board with a floor hatch instead of the FFC
type: question
priority: P3
status: open
area: mech
created: 2026-11-06
---

# Plug-on sensor board with a floor hatch instead of the FFC

## Context

Keyball plugs its sensor board straight onto the main PCB instead of using a cable. The same idea
was evaluated for k0d3ball35 while fixing the assembly order and not taken; this ticket records
it so it can still be picked up before the boards are ordered in quantity.

The variant: the sensor board grows a tab on its key-facing edge that reaches under the right
PCB through the slot in the cradle wall, carries a 1x6 2.54 mm socket, and mates with a male
header on the underside of the right PCB. No FFC, no 0.5 mm FPC connectors (the two hardest
solder joints in the build), no cable type to get wrong.

Why it was not taken:

* Anything that mates vertically has to sit under the board, and anything under the board blocks
  the module's way out: the cartridge could then only be removed downwards, so the pocket floor
  would have to become a fourth printed part (a hatch on two screws).
* The blind mate rests on the printed tolerance chain between the pocket well and the PCB
  standoffs, about +-0.5 mm. A 2.54 mm header takes that, but it is a new risk.
* The sensor board needs a new revision (tab, header, pin order) and the cradle a new wall.

The cable route keeps the module removable from above and lets the cable absorb every tolerance,
which is why it won for r2.2 (`hw-j1-top-side`).

## Acceptance criteria

- [ ] Decide before the first PCB order in quantity whether the plug-on variant is worth the hatch
- [ ] If yes: sensor board r2 with the tab, cradle wall opening, tray floor opening with a seating shoulder, hatch part, blind-mate tolerance analysis

## Notes

The 6.15 mm gap between the sensor board plane (-7.75) and the PCB underside (-1.6) is what the
header has to span: a low profile 2.54 mm socket (body 6 mm) on the tab plus 6 mm pins pointing
down from the PCB would fit.
