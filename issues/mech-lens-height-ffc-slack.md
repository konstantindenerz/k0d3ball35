---
title: Lens height from the datasheet, 50 mm FFC with an S-fold
type: bug
priority: P1
status: done
area: mech
created: 2026-11-12
---

# Lens height from the datasheet, 50 mm FFC with an S-fold

## Context

The module rework (`mech-cradle-real-module`) left two loose ends:

1. **`lens_h` was an unsourced 2.5 mm.** PixArt's PAW3204LU datasheet covers the same lens family
   as the PAW3222's PNSR-015-RB3. It gives PCB to tracking surface 5.85 mm and lens plane to
   surface 2.4 mm, so the board sits 3.45 mm (+-0.15) behind the lens face. The maker's own 12 mm
   case puts its lens ceiling 3.4 mm over the board. Both say the module sits 0.95 mm further from
   the ball than modelled.
2. **No 40 mm cable is stocked.** No 6-way 0.5 mm type B (Molex "Type D", "reverse") cable is
   stocked between 30 mm (too short) and 50 / 50.8 mm (GCT, Molex, Würth, JUSHUO checked).
   Putting the connector on the user side, so the cable runs round the thumb side, gives a
   47.9 mm route, which leaves a 50 mm cable 2.1 mm: too tight.

## Acceptance criteria

- [x] `lens_h` 3.45 with its source. Ball height unchanged at 13.95 (the cup floor still binds). The
  module now reaches 16.0 mm from the axis inside the PCB slab, past the 15.5 mm notch apothem.
  It reaches that far towards +x, where the nearest board edge is 13 mm away.
  - The notch test became a test against the real PCB outline: at least 1 mm gap. A module
    leaning to the keys fails it.
  - Layout projection of the module: 5.0 x 13.4 at +13.9.
- [x] Cable 50 mm (GCT 05-06-D-0050-A-4-06-4-G, or JUSHUO JS05B-06P-050-3-4 at LCSC). The route
  is 34.4 mm with both insertions, which leaves 15.6 mm of slack. That slack goes into an
  upright S-fold in the free corner of the pocket beside J1, towards the thumb
  (`ffc_route.SLACK_ZONE`). The fold holds up to 33.9 mm.
  - `tests/test_ffc_route.py` checks that the zone is free of the cradle mesh, the PCB, the case
    screws and the clip pins, and that it lies inside the pocket opening under the cover. A
    zone moved onto the cup fails it.
- [x] Docs: BOM, order checklist, build guide (the S-fold step), spec 01/08 and the cradle README.

## Notes

- Still to measure on the part: board thickness (unknown; the maker's old 19 mm slot allows board
  plus back parts up to 1.85 mm with a 3.45 mm lens) and the lens height itself (+-0.15).
- The maker's two cases were drawn for the earlier 13.4 x 13 mm board. Only their lens heights
  carry over to the current one.
