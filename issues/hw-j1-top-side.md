---
title: Move J1 to the key side of the right PCB and use a type B FFC
type: bug
priority: P1
status: done
area: hw
created: 2026-11-06
---

# Move J1 to the key side of the right PCB and use a type B FFC

## Context

J1 sat on the back of the right PCB at (0, +45.5) with its cable mouth 1.0 mm from the cradle
housing wall at y = 49.5, and the sensor connector sits 8 mm lower. A flat cable needs roughly
twice its bend radius of horizontal run for a step of that kind, so the documented "cable drops
straight into its slot" came out as two creases right at the connector lip. On top of that the
flip lock faced into the 3 mm gap between the PCB and the case floor: once the PCB was screwed
down, the connector could not be opened at all, so both ends of the cable had to be plugged while
the PCB was still in the hand, and the trackball could only be serviced by taking the PCB out.

## Decision

J1 moves to the key side at (-20.6, +47.4) (r2.3; it was (-2.6, +45.5) when this was written),
rotation 0, footprint `FPC_0.5mm_6P_FH12-6S_top`
(same part, front-face pad set). Its mouth ends 0.5 mm short of the notch edge. The cable leaves
the sensor board under its own connector, turns up in a 6 mm channel inside the key-facing wall
of the cradle housing, climbs the 2.95 mm gap between the cup envelope and the notch edge and
folds over the board edge into the mouth.

Consequences:

* Both connectors stay bottom contact, but they now look at the cable from opposite faces, so the
  cable must be a **type B** FFC (contacts on opposite faces at its two ends).
* The pin order is straight through, 1 to 1, because a front-face footprint is not mirrored.
* x = ball x - 7.6 is where the sensor board's connector sits (its J1 is 7.6 mm off the optical centre and
  the board is turned over), so the cable runs straight with no lateral offset.
* J1 is the last connection of the build and the first to undo for service: lock open, cable out,
  two screws from below, module out of the pocket. Keycaps and PCB stay in place.

## Acceptance criteria

- [x] `fpc.side: top` in the layout yaml, front-face footprint, GND stub and via on F.Cu, ERC/DRC clean, gerbers regenerated
- [x] Courtyard inside the outline, 1.05 mm to the nearest keycap (the lock is reachable), 2.2 mm to the diode below it; checked in `check_layout` and `tests/test_pcb_review.py`
- [x] Pin order and cable type derived from both board files in `tests/test_ffc_pin_order.py`
- [x] Lid lip and tray keep out of J1 and the cable corridor (`fpc_keepout_2d` in the case)
- [ ] Verified with the first physical type B cable (`hw-ffc-pin-order-verification`)

## Notes

A cable window through the board was considered first: the free band between the bottom-row
keycaps and the notch edge is only 6.75 mm, which is not enough for a window plus the connector
plus a fold, and the window would have had to sit on top of the switch bodies.
