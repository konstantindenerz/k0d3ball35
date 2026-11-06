# Printed case

The case is the last phase of r2: two printed parts per half plus a removable lid. The CAD
lives in `hardware/case/` (OpenSCAD, parametric, both halves from one set of sources); this
document explains what the parts are, the heights they are built on and how they go
together. Tickets: [mech-case](../issues/mech-case.md),
[mech-case-ball-pocket](../issues/mech-case-ball-pocket.md),
[mech-case-lid](../issues/mech-case-lid.md). Build notes and the parameter list are in
[hardware/case/README.md](../hardware/case/README.md).

![Exploded view of one half](images/img-case-exploded.png)

## 1. Parts

| Part | STL | What it is |
|------|-----|------------|
| Tray | `tray-left.stl`, `tray-right.stl` | the case body: angular walls on the stepped PCB outline, key floor 3 mm under the PCB, battery well, controller box walls, pocket for the cradle (right), five standoffs with M2 heat-set inserts, four foot magnet pockets from below, feet recesses |
| Box cap | `box-cap-left.stl`, `box-cap-right.stl` | roof of the controller box: a plate in a rebate plus an L-shaped skirt towards the keys and the thumb keys, two M2 screws into corner bosses |
| Lid | `lid-left.stl`, `lid-right.stl` | transport cover over keys and ball, held on top by an inner lip; under the half it is a foot held by four magnets in the roof |
| Pocket test | `pocket-test-right.stl` | the 50 x 50 mm corner of the right tray around the ball, for the first test print with the cradle |

The layout facts (outline, holes, bay, courtyards, pocket, controller block) are generated
from `hardware/layout/k0d3ball35.yaml` by `scripts/gen_case.py` into `hardware/case/data.scad`;
every offset and height is a parameter in `params.scad`. `make case` renders everything.

![Tray from above](images/img-case-tray-top.png)

## 2. Heights

z = 0 is the PCB top, from `hardware/case/stack.json`:

| Level | left | right | Note |
|-------|------|-------|------|
| Underside | -14.1 | -14.1 | flat, 2.5 mm under the deepest well |
| Battery well and pocket floor | -11.6 | -11.6 | same plane as the cradle's `floor_z` |
| Key floor | -4.6 | -4.6 | hot-swap sockets 1.8 mm, diodes 1.1 mm, air |
| PCB | -1.6 to 0 | -1.6 to 0 | on 3.0 mm standoffs |
| Rim | +5.0 | +5.0 | flush with the keycap skirts, below the cup rim (+6.6) |
| Controller box cap, under / top | +6.7 / +8.7 | +6.7 / +8.7 | controller top +5.7 plus 1 mm |
| Keycap top | +11.0 | +11.0 | Choc V1 |
| Ball top | - | +17.1 | cradle `ball_top_above_pcb_top` |
| Lid roof, under / top | +12.0 / +15.0 | +18.1 / +21.1 | 1 mm over the tallest thing, 3 mm roof with the magnets inside |
| Lid lip bottom | +2.0 | +2.0 | 3 mm below the rim, inside the wall |

The two halves have different lid heights on purpose: a 21 mm lid over the left half would
only add bulk. A `lid_mode = "dome"` variant keeps the right lid at 14 mm with a round turret
over the ball; it renders but is not part of the default build.

## 3. Pocket

![Section through the pocket](images/img-case-pocket-detail.png)

The cradle stands on the case floor in a well beside the right PCB
(`docs/08-trackball-module.md`, `hardware/trackball-cradle/README.md`): the housing well is
30 x 30 mm (housing 29 x 29 plus 0.5 mm) in a 34 x 34 mm block, floor at -11.6, two 2.2 mm
holes 20 mm apart on the y axis for the M2 x 10 case screws from below, counterbored so the
cradle sees the 2.0 mm floor it assumes. Above the PCB plane the cavity is the PCB notch
(apothem 15 mm, square corner towards the keys) plus 0.2 mm, so the printed wall continues the
PCB edge around the cup with a 2 mm wall. The rim stops at +5.0, 1.6 mm below the cup rim, and
the thumb reaches the ball at its equator from the key side. The FFC needs nothing from the
tray: it climbs the 2.95 mm gap between the cup and the notch inside the cradle's own wall
channel and folds over the board edge into J1 on the key side; only the lid's lip keeps clear of
J1 and of that corridor (`fpc_clear`). The 25 mm fallback ball is a parameter set
(`-D ball_d=25 -D notch_apothem=16.5 -D pocket_d=35 -D ball_top_z=23.05`) and needs a
different PCB notch; it is documented, not printed.

## 4. Controller box

![Section through the controller box](images/img-case-controller-box-section.png)

The controller sits on 2.5 mm sockets, so its top is at +5.7 and the box roof needs +6.7.
The tray only carries the two box walls that are outside the PCB (the outer wall and the
USB wall, up to +8.7); a roof in the tray would block dropping the PCB in and be a 65 mm
bridge. The other two walls hang from the separate cap and stand on the PCB top. Two M2
screws go into corner bosses on the outer wall (heat-set inserts, same as the standoffs).
The USB-C opening is 11 x 5.8 mm in the USB wall, the LED window 3 x 3 mm in the outer wall
8 mm from the USB end, the slide switch lever has a 7 x 3 mm slot in the outer wall directly
under the PCB and the reset button a 3 mm pin hole in the floor of the well.

## 5. Assembly order

This order is the only one the hardware allows, and the build guide
(`docs/04-build-guide.md`, chapter 12) follows it step by step.

1. Press the seven M2 heat-set inserts (five standoffs, two bosses) with a soldering iron at
   about 200 C. Do this before anything else goes into the tray.
2. Glue the magnets (four in the tray floor, four in the lid roof), see section 7.
3. Right half: trackball module into the pocket (bearings in, sensor board and cable already
   inside the cradle, cable slot and wall channel towards the keys), then the two M2 x 10 case
   screws from below. Do it now because the module is easier to handle and to gauge while the
   tray is empty - it can also go in, or come out, after the PCB is screwed down: it clears the
   board edge by 0.5 mm all round and only moves vertically (section 3).
4. Cell onto the back of the PCB in the dashed bay, plug into J3. The battery well is fully
   covered by the board, so the cell travels with the PCB and cannot go in afterwards.
5. PCB into the tray over the cup, keycaps off, five M2 x 5 or x 6 machine screws from the top.
6. Controller on, box cap on, two M2 screws. Keycaps on.
7. Right half: fold the FFC over the board edge into J1 on the key side, close the lock. Last
   connection of the build, and the only one you can reach with everything assembled.
8. Ball in, rubber feet on, lid on.

Service: the trackball module comes out without touching keycaps or PCB. Open J1's lock, pull
the cable out, undo the two screws from below and lift the module out of the pocket. Everything
else (cell, controller, switches) needs the five PCB screws out, which means the keycaps come off
first: their skirts overhang the screw heads by 1.5 mm.

## 6. Printing

Tray flat on the bed with the cavities open upwards; the only bridges are the USB opening,
the switch slot, the LED window and the four foot magnet pockets from below. Cap and lid
print roof down; the lid's roof magnet pockets open towards the roof underside and print as
plain holes. No supports anywhere, 0.2 mm layers (0.12 mm for the pocket test), 3 perimeters. Print
`pocket-test-right.stl` first and check it with the cradle and a scrap PCB with the notch:
0.3 mm all round, the module drops in and lifts out vertically with the board in place, and the
FFC reaches J1 over the board edge without a crease.

## 7. Lid and magnets

![Lid on for transport](images/img-case-lid-transport.png)

On top the lid holds without magnets: a 1 mm lip on the inside of its skirt reaches 3 mm
into the tray (0.15 mm to the wall) and holds by friction, the skirt sits on the rim flush
with the outer wall. The lip stops at the controller box walls and at the pocket cup.

Magnets only hold the foot position: four 6 x 2 mm discs from below in the tray floor near
the corners (8 mm inside the PCB edge, in the thick floor under the keys) and four in the
lid roof, pushed in from the roof underside with 0.6 mm of roof left on top, so nothing is
visible from outside. Polarity: tray floor pockets north down, lid roof pockets south up.
Glue them after printing, check the snap with a loose magnet before the glue sets.

![Lid as a foot](images/img-case-lid-foot.png)

As a foot the lid goes under the half the same way up (roof against the tray underside) and
lifts it flat by 13 mm (left) or 19 mm (right); the rubber feet stay usable without it. Tenting is a parameter: `-D tent_wedge_deg=6` adds a wedge to the lid
roof that rises towards the inner edge, so the lid-as-foot tilts the half by that angle
while the cover position is unchanged.

## 8. Open points

- LED window position is a guess at the nice!nano LED; verify on the controller.
- `box_inner_x` = -45.5: 0.75 mm to the inner column caps, 1.5 mm to the controller.
- `lid_fit` (0.15 mm between lip and wall) is set for a 0.4 mm nozzle; adjust after the
  first lid print.
- First print: pocket test, then the right tray, then the lids.
