---
title: Cradle drawn for the real PAW3222 module, FFC 40 mm, type A warning
type: bug
priority: P0
status: done
area: mech
created: 2026-11-12
---

# Cradle drawn for the real PAW3222 module, FFC 40 mm, type A warning

## Context

The r2.4 cradle was drawn for a "14 x 8 mm PAW3222 module with its FPC connector on the back".
No source was given for it. The maker's drawing and photo
(github.com/sekigon-gonnoc/small-mouse-sensor-module, `img/size.png`, `img/image.png`) and the
torabo-tsuki LP build guide photos show a different part:

| | assumed until now | real (maker drawing) |
|---|---|---|
| board | 14 x 8 mm | 13.4 x 7.4 mm |
| lens body | 6 x 5 mm, cavity 7 x 6 | 9.06 x 7.4 mm, the full board width, flush with one short end |
| optical centre | board centre | 6.79 mm from the lens end (0.09 mm off centre) |
| connector | on the back, cable out of the bottom | Hirose FH19C on the LENS side at the other short end, cable out of that end in the board plane, 2.3 mm insertion |

So the lens body did not fit its cavity, the cable exit was on the wrong side, and the FFC length
(30 to 40 mm, never calculated) and the type B reasoning ("type A connects nothing") rested on
the wrong part.

## Acceptance criteria

- [x] `params.scad`: real module dimensions with their source; `lens_far`, `conn_zone`, `conn_h`,
  `conn_end` (connector towards the keys), `ffc_w`; window slot 4 x 8 mm shifted 2 mm towards the lens
  end, over both lens apertures (0.64 and 3.12 mm from the optical centre), like the maker's case
- [x] `cradle.scad`: the optical centre sits on the axis. The lens cavity is exactly `lens_h` deep, so
  the lens face rests on its floor and sets the lens distance (no shoulder, the lens is full width).
  Connector cavity. FFC exit slot through the key-side end wall, open to the back, so the module
  slides in with the cable plugged. 4 x 8 mm window slot for both lens apertures. Dummy and insert
  path follow the real part.
- [x] Tests, each one checked by putting the old fault back:
  - real module ∩ cradle = 0
  - lens face seated (0.05 mm taller collides, shorter is free)
  - insert path free
  - cable exits towards the keys
  - rays from both lens apertures to the ball (a centred slot clipped the outer one, found in review)
  - skin over the lens cavity ≥ 0.45 mm (0.51 measured; the first version of this test probed the wrong
    side of the ball and passed without measuring, found in review; now one shared transform)
- [x] `scripts/k0d3/ffc_route.py`: straight 2.1 mm out through the end-wall slot, then 81 deg round the
  cup; 33.6 mm with both insertions; band top 2.35 under the clip pins (3.30). The layout's `fpc.cable_length` 40 is
  held against it by `tests/test_ffc_route.py`, and so are the docs.
- [x] Type A warning: with the free 90 degree twist a type A cable makes contact and reverses the
  pin order, 3.3 V onto GND. Spec 01/08, BOM, order checklist and build guide say so, and
  `tests/test_ffc_pin_order.py` checks the docs.
- [x] 13.4 x 7.4 everywhere, layout `sensor_board` projection updated; case, site and previews
  regenerated

## Notes

- Still nominal and to be measured on the part: `lens_z`, `lens_h`, board thickness, `conn_h`. The
  ball height does not depend on them; the lens distance now depends only on the lens face and
  the cavity floor.
- The skin between the lens cavity's upper edge and the cradle top is 0.51 mm at its thinnest.
  It is a wedge that thickens quickly, and it prints with 0.12 mm layers (build guide).
- Open before ordering: a 6-way 0.5 mm type B ("reverse", Molex "Type D") cable of 40 mm. Molex
  stocks 30 mm (shorter than the 33.6 mm route) and 51 mm (17 mm of slack has nowhere to go
  without a fold). Find a 40 mm listing (AliExpress / LCSC) before the order.
- Reviewed by a fresh agent against the maker's drawing and case STEP: the window was moved over
  both apertures and the skin test was made to really measure (both found there). A suspected clash
  of the cable exit with the PCB notch facet is not real: there is no PCB within 9 mm of the exit.
