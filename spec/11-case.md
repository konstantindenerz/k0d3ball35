# Printed case

The case is the last phase of r2: two printed parts per half plus a hinged two-plate lid. The CAD
lives in `hardware/case/` (OpenSCAD, parametric, both halves from one set of sources); this
document explains what the parts are, the heights they are built on, how they go
together and how the wordmark is engraved into them. Tickets: [mech-case](../issues/mech-case.md),
[mech-case-ball-pocket](../issues/mech-case-ball-pocket.md),
[mech-case-lid](../issues/mech-case-lid.md). Build notes and the parameter list are in
[hardware/case/README.md](../hardware/case/README.md).

![Exploded view of one half](images/img-case-exploded.png)

## 1. Parts

| Part | STL | What it is |
|------|-----|------------|
| Tray | `tray-left.stl`, `tray-right.stl` | the case body: angular walls on the stepped PCB outline, key floor 3 mm under the PCB, battery well, controller box walls, pocket for the cradle (right), five standoffs with M2 heat-set inserts, four foot magnet pockets from below, feet recesses |
| Box cap | `box-cap-left.stl`, `box-cap-right.stl` | roof of the controller box: a plate in a rebate plus an L-shaped skirt towards the keys and the thumb keys, two M2 screws into corner bosses |
| Lid, outer plate | `lid-outer-left.stl`, `lid-outer-right.stl` | pinky-side half of the transport cover: the four roof magnets, the even hinge knuckles including both ends; as a foot it lies under the controller half |
| Lid, inner plate | `lid-inner-left.stl`, `lid-inner-right.stl` | controller-notch and thumb-side half: the odd knuckles; folded down beyond the inner edge it is the kickstand of the tenting foot |
| Lid, closed pair | `lid-left.stl`, `lid-right.stl` | both plates joined by a 2 mm steel pin, held on top by an inner lip; for the exploded view, not for printing |
| PCB guard | `guard-left.stl`, `guard-right.stl` (`dxf/guard-*.dxf` for a laser-cut sheet) | 0.8 mm plate on the PCB top between the switches, like the Keyball39 cover plate; held by the switch flanges, no screws, no extra height (section 5a) |
| Pocket cover | `pocket-cover-right.stl` | flush 1.2 mm plate over the cradle opening, a bezel over the cup rim with a 20.55 mm hole (0.75 mm round the ball), two M2 x 6 countersunk screws |
| Retainer clip | `pocket-clip-right.stl` | optional: C-ring on the cover with two claws over the ball, two snap pins into the cover; keeps the ball in upside down |
| Pocket test | `pocket-test-right.stl` | the 50 x 50 mm corner of the right tray around the ball, for the first test print with the cradle |

The tray and the box cap carry the owner wordmark as an engraved relief (section 9).

The layout facts (outline, holes, bay, courtyards, pocket, controller block) are generated
from `hardware/layout/k0d3ball35.yaml` by `scripts/gen_case.py` into `hardware/case/data.scad`;
every offset and height is a parameter in `params.scad`. `make case` renders everything;
the [project page](../docs/index.html) loads the STLs straight from the repository (the Case
tab shows every printable part, the Explorer tab the assembled halves), so it shows the new parts as
soon as they are committed; `make site` refreshes the part facts it lists.

![Tray from above](images/img-case-tray-top.png)


Broken edges (`edge_chamfer` 0.5 mm, `rim_chamfer` 0.3 mm in `params.scad`): both parts print
with a large flat face on the bed - the tray floor down, the lid roof down - and that first layer
squashes out by a tenth or two. A 45 degree taper on those two outer edges keeps the half sitting
flat, takes the sharp edge off the line that rides on the desk, and gives the lid a lead-in. The
rim gets a smaller one: it is what the hand touches with the lid off and what meets the lid skirt
with the lid on, where it reads as a shadow line rather than a seam. It stops short of the
controller box, whose walls stand on the rim. The vertical corners stay sharp - the nozzle rounds
them to about 0.2 mm anyway and the angular outline is the point. The taper is built as a stack of
inset slices `chamfer_step` (0.1 mm) tall, finer than a print layer: OpenSCAD has no offset in z
and a hull over this outline would fill its steps.

Consequence worth knowing: the half now rocks on the chamfered line, `edge_chamfer` inside the
outer wall, so `foot_pivot_x` and everything the foot solve derives from it moved by that much.

## 2. Heights

z = 0 is the PCB top, from `hardware/case/stack.json`:

| Level | left | right | Note |
|-------|------|-------|------|
| Desk | -9.8 | -9.8 | 1 mm rubber feet in 0.8 mm recesses |
| Underside | -9.6 | -9.6 | flat, 2.0 mm under the battery well |
| Battery well floor | -8.1 | -8.1 | 6.5 mm under the PCB underside: 5.7 mm cell, 0.4 mm solder joints, 0.1 mm Kapton, 0.3 mm air; 1.5 mm floor |
| Pocket floor | - | -7.1 | the cradle's `floor_z`; 2.5 mm of floor under it for the countersunk screws |
| Key floor | -4.6 | -4.6 | hot-swap sockets 1.8 mm, diodes 1.1 mm, air |
| PCB | -1.6 to 0 | -1.6 to 0 | on 3.0 mm standoffs |
| PCB guard | 0 to +0.8 | 0 to +0.8 | 1.2 mm under a pressed keycap skirt (+2.0) |
| Pocket wall top | - | +2.9 | 0.5 mm under the cup rim (+3.4), so the thumb reaches the ball's equator |
| Rim | +5.0 | +5.0 | flush with the keycap skirts |
| Controller box cap, under / top | +6.7 / +8.7 | +6.7 / +8.7 | controller top +5.7 plus 1 mm |
| Keycap top | +11.0 | +11.0 | Choc V1; 20.8 mm over the desk |
| Ball top | - | +13.95 | cradle `ball_top_above_pcb_top`; 23.75 mm over the desk |
| Hinge strip underside | +12.5 | +12.5 | roof thickened to 5 mm within 6 mm of the hinge line, 1.5 mm over the caps |
| Lid roof, under / top | +14.5 / +17.5 | +14.5 / +17.5 | 3.5 mm over the caps (`lid_clear`), 3 mm roof with the magnets inside; 27.3 mm over the desk |
| Hinge axis | +15.0 | +15.0 | knuckles of 5 mm flush with the roof top |
| Lid lip bottom | +2.0 | +2.0 | 3 mm below the rim, inside the wall |

The ball top sits under the roof underside, so both halves share one lid without a ball window.

## 3. Pocket

![Section through the pocket](images/img-case-pocket-detail.png)

The cradle stands on the case floor in a well beside the right PCB
(`spec/08-trackball-module.md`, `hardware/trackball-cradle/README.md`). Its floor footprint is
the cup skirt plus the sensor sleeve's tab, 27.73 x 24.05 mm (x by y) with clearance, leaning
towards +x; the well around it is the 29 x 24 mm housing box from the layout (centred 2.55 mm off
the ball towards +x) plus 0.5 mm. Floor at -7.1, two 2.2 mm holes 20 mm apart on the y axis through the ball for
the M2 x 8 case screws from below into the cup skirt. The screws are countersunk flat heads:
a 4.8 mm, 1.3 mm deep 90 degree cone (`case_screw_cs_d`, `case_screw_cs_h`) puts the head 0.2 mm
inside the flat underside; 1.2 mm of floor is left at the bore.

The pocket is part of the case edge, not a box in front of it: the outline
(`case_outline` in `data.scad`, from `scripts/gen_case.py`) runs in 90 degree steps around it
like it does around the keys, and the tray is solid up to the rim there. Only a rectangle over
the cradle stays open (`pocket_opening`: the well, the 28.4 mm cradle circle and the cable path
to the board edge). A flush cover (`pocket_cover`, 1.2 mm, from +3.8 to the rim at +5.0) sits on
a 4 mm ledge in that opening and reaches over the cup rim (0.375 mm above it) as a bezel: its
20.55 mm hole leaves 0.75 mm round the ball, hides the cup and still lets the ball lift out. Two
M2 x 6 countersunk screws on the user-side ledge into 1.6 mm pilots hold it. The optional
retainer clip (`pocket_clip`) is a C-ring on the cover with two claws over the ball's shoulders,
open towards the thumb, held by two split snap pins in two 2.4 mm holes of the cover;
`hardware/case/retention.py` proves it keeps the ball in (0.67 mm tolerance) and stays off it. On the thumb side the
cover ends at the PCB edge, so the seam runs straight. The lid follows the same outline and
covers the ball (ball top +13.95, roof underside +14.5). The FFC needs nothing from the tray: it
climbs from the module and folds over the board edge into J1 on the key side under the cover;
only the lid's lip keeps clear of J1 and that corridor (`fpc_clear`).

## 4. Controller box

![Section through the controller box](images/img-case-controller-box-section.png)

The controller sits on 2.5 mm sockets, so its top is at +5.7 and the box roof needs +6.7.
The tray only carries the two box walls that are outside the PCB (the outer wall and the
USB wall, up to +8.7); a roof in the tray would block dropping the PCB in and be a 65 mm
bridge. The other two walls hang from the separate cap and stand on the PCB top. Two M2
screws go into corner bosses on the outer wall (heat-set inserts, same as the standoffs).
The USB-C opening is 11 x 5.8 mm in the USB wall, the LED window 3 x 3 mm in the outer wall
8 mm from the USB end, the slide switch lever has a 7 x 3 mm slot in the outer wall directly
under the PCB and the reset button a 3 mm pin hole in the floor of the well. The cap plate
carries the wordmark (section 9).

## 5. Assembly order

This order is the only one the hardware allows, and the build guide
(`spec/04-build-guide.md`, chapter 12) follows it step by step.

1. Press the seven M2 heat-set inserts (five standoffs, two bosses) with a soldering iron at
   about 200 C. Do this before anything else goes into the tray.
2. Glue the magnets (four in the tray floor, four in the outer lid plate's roof) and pin the two
   lid plates together with the 2 mm rod, see section 7.
3. Right half: trackball module into the pocket (bearings in, sensor module and cable already
   in the sleeve), then the two M2 x 8 case screws from below. Do it now because the module is easier to handle and to gauge while the
   tray is empty - it can also go in, or come out, after the PCB is screwed down: it only moves
   vertically past the square notch corner (section 3).
4. Cell onto the back of the PCB in the dashed bay, plug into J3. The battery well is fully
   covered by the board, so the cell travels with the PCB and cannot go in afterwards.
5. PCB into the tray over the cup, keycaps off, five M2 x 5 or x 6 machine screws from the top.
6. Controller on, box cap on, two M2 screws.
7. PCB guard onto the PCB top (holes over the screw heads), then the switches through it into
   the sockets: their flanges hold it down. Keycaps on.
8. Right half: fold the FFC over the board edge into J1 on the key side, close the lock. Last
   connection of the build, and the only one you can reach with everything assembled.
9. Right half: pocket cover on, two M2 x 6 countersunk screws from the top. Ball in through
   the bezel, optional retainer clip on, rubber feet on, lid on.

Service: the trackball module comes out without touching keycaps or PCB. Take the pocket cover
off (two screws from the top), open J1's lock, pull the cable out, undo the two screws from below
and lift the module out of the pocket. Everything
else (cell, controller, switches) needs the five PCB screws out, which means the keycaps come off
first: their skirts overhang the screw heads by 1.5 mm. The guard has holes over the screw
heads, so the screws come out without it; the guard itself only comes off with the switches.

### 5a. PCB guard

The Keyball39 has a plate over the PCB between the switches. Here it is a printed 0.8 mm plate
(`guard`) that lies directly on the PCB top. It adds no height because it only fills air that is
already there: the keycap skirt sits at +5.0 and bottoms out at +2.0 after the 3 mm travel, and
nothing else is on the PCB top between the switches (diodes and sockets are on the bottom
face). That leaves 1.2 mm over the guard (`guard_min_air` 0.8 is the asserted minimum). Rim,
keycap top and lid stay where they are.

- Cut-outs: a 14.2 mm square per switch (13.8 mm lower housing plus `guard_fit` 0.2), rotated
  with the thumb keys. The 15 mm upper housing flange reaches over the edge and holds the guard
  down, so it needs no screws.
- Holes of 3.7 mm over the five PCB screws (heads max 3.5 mm, BOM): the heads keep sitting on
  the PCB, because a head on top of the guard would stand above a pressed keycap.
- Left open: J1's body and contact tails (not its courtyard) and the FFC path, the cradle, and
  the inside of the controller box. Along the key side and the thumb side of the box the guard
  runs on under the box cap's skirt, and the skirt stands on the guard (`box_skirt_z`).
- Nothing green from above: keycaps, guard, box, J1, screw heads and the pocket cover cover the
  whole PCB except the fit gaps (0.1 mm round a head, 0.2 mm round J1).
  `tests/test_case_guard.py` (`test_no_bare_pcb_from_above`) fails on any wider strip. The first
  version left 43 mm2 of bare PCB beside J1, at the thumb screw and along the box.
- One piece: the screw holes cut into some of the webs between the keys. `scripts/gen_case.py`
  (`guard_polygon`) therefore cuts every web narrower than `guard_min_web` (1.0 mm, two
  perimeters of a 0.4 mm nozzle), keeps the largest piece and grows it back with square
  corners, so no loose strip can end up in the case. The outline is in `data.scad`, the fits
  in `params.scad`.
- Since the keycaps are 17.5 x 16.5 on an 18 x 17 pitch, the guard mostly shows at the thumb
  keys and along the edge. What it does is keep dust and crumbs off the board and cover the top
  pads of the reversible footprints.
- Print it flat, PLA or PETG, 0.2 mm layers. Or cut it from 0.8 mm acrylic or FR4 with
  `dxf/guard-*.dxf`. Do not make it thicker than 1.2 mm without measuring a pressed keycap
  first (`cap_skirt_z`, `switch_travel`).

## 6. Printing

Tray flat on the bed with the cavities open upwards; the only bridges are the USB opening,
the switch slot, the LED window and the four foot magnet pockets from below. Cap and both lid
plates print roof down; the outer plate's roof magnet pockets open towards the roof underside
and print as plain holes, the horizontal 2.2 mm pin hole and the knuckle halves that reach past
the hinge line are the only small overhangs, the knuckle grooves in the skirt ends the only
upward faces. No supports anywhere, 0.2 mm layers (0.12 mm for the pocket test), 3 perimeters.
The engraved wordmark on the cap plate and the case underside is one more set of bridges, all
of them one groove wide (1.0 mm on the cap, 0.9 mm on the floor) and 0.6 mm tall, on the face
that lies on the bed. Print
`pocket-test-right.stl` first and check it with the cradle and a scrap PCB with the notch:
0.3 mm all round, the module drops in and lifts out vertically with the board in place, and the
FFC reaches J1 over the board edge without a crease.

## 7. Lid, hinge and magnets

![Lid on for transport](images/img-case-lid-transport.png)

The lid is two plates per half, split along the hinge line x = -13 in the layout frame
(`hinge_x`, generated by `scripts/gen_case.py`; the left half is mirrored like everything
else). The outer plate on the pinky side carries all four roof magnets, the
inner plate the controller box notch and the thumb cluster. On top the lid holds without
magnets: a 1 mm lip on the inside of its skirt reaches 3 mm into the tray (0.15 mm to the
wall) and holds by friction, the skirt sits on the rim flush with the outer wall. The lip stops
at the controller box walls and at the pocket cup. The ball top (+13.95) stays 0.55 mm under the
roof, so the closed lid keeps the ball in the cup.

![Hinge close-up](images/img-case-lid-hinge.png)

The hinge runs the full depth of the lid along the line: 9 knuckles of 8.77 mm with 0.3 mm
gaps from y = -9.72 to +71.6 (span 81.3 mm), the outer plate owning the even knuckles and so
both ends. The knuckles are 5 mm round and flush with the roof top, the axis at +15.0; within
6 mm of the line the roof is thickened downward to 5 mm (underside +12.5, 1.5 mm over the Choc
caps) to carry them. A knuckle turns in a groove of the other plate with 0.3 mm radial
clearance; the strip next to a groove is cleared so no thin lip remains. The pin is a 2 mm
steel rod about 80 mm long in a 2.2 mm hole, pushed in from the back edge (y-min, away from
the user); the last knuckle towards the user is blind, so the pin cannot walk out. A piece of
1.75 mm filament works as a fallback (`-D hinge_pin_d=1.75`). Above the axis the two plates'
vertical cut faces are 0.2 mm apart.

The stop is in the cut itself. Below the axis each plate's cut face is a plane through the
axis leaning outward by `hinge_stop_deg`, half the solved fold (28.5 degrees right, 21.6
left), so closed there is a V slit at the skirt bottom (about 7.5 mm wide at the front and
back skirt, 1.5 mm under the strip), and when the lid is folded by `hinge_fold_deg` (56.9
degrees right, 43.2 left) the two faces meet flat on flat along the whole cut - skirt ends
and strip underside - and carry the load. Knuckle and groove are round and never take it.

Magnets only hold the foot position: four 6 x 2 mm discs from below in the tray floor under
the key area next to the battery well (right (-36.94, 9.69), (-26.35, 17.69), (-26.35, 45.19),
(-37.0, 38.94); left (-37.25, 9.69), (-29.478, 17.19), (-29.478, 45.19), (-37.19, 38.94)),
placed by the generator where the outer plate's roof region and the tray floor region shifted
by `foot_dx` overlap, kept 2 mm clear of the wells, J1 and the cable corridor, and four in
the outer plate's roof at the same points shifted by -`foot_dx` (lid x about 28 to 38, clear
of the hinge strip), pushed in from the roof underside with 0.6 mm of
roof left on top, so nothing is visible from outside. Polarity: tray floor pockets north
down, lid roof pockets south up. Eight per half, sixteen in total. Glue them after printing,
check the snap with a loose magnet before the glue sets.

![Lid folded as a tenting foot](images/img-case-lid-folded.png)

As a foot the lid folds and goes under the controller half of the tray: the whole folded lid
is shifted inward by `foot_dx` (-49.8 mm right, -67.8 left, `data.scad`) so that the hinge
axis sits 3 mm (`foot_overhang`) outside the inner tray wall. The outer plate lies roof-up
against the tray underside, its four magnets on the four floor magnets, and the inner plate
folds down beyond the inner edge as a kickstand that points inward, towards the other half.
The half stands on its own outer bottom edge and on the hinge directly above the kickstand's
lip edge, so nothing is cantilevered: a thumb press or a resting palm cannot pivot the board
against the magnets, which only keep the plate aligned. The tilt `tent_deg` = 18 degrees is the
input; the fold is solved so that the kickstand's lip edge reaches the desk (`hinge_fold_deg`
56.9 degrees right, 43.2 left), and the stop is cut at half of that. In numbers
(`stack.json`, right; left in brackets): the kickstand hangs 38.9 degrees (25.2) below the
tray (`foot_beta_deg`), the hinge axis is 37.8 mm (37.8) above the desk (`foot_hinge_h`), the
kickstand's foot stands 34.5 mm (53.3) beyond the inner wall (`foot_reach`), and the outer
plate's free end floats 1.6 mm (7.2) above the desk (`foot_free_end_h`). The right half is the
tight one: 1.6 mm is all the clearance the outer plate has, so a warped print or a desk mat puts
its free end down and the half rocks. Below about 13
degrees of tilt the lid thickness alone would hold the board up, so `tent_deg` must stay
above that (`tests/test_case.py` asserts more than 0.5 mm of clearance). The rubber feet at
(-58, 1), (-58, 34), (-27, 8) and (-32, 61) rest on the lid roof, the others are off the
plate; the feet stay usable without the lid.

## 8. Wordmark

![Box cap with the engraved wordmark](images/img-case-logo-cap.png)

The `kode` wordmark is drawn on a strict cell grid, one stroke per cell. `scripts/gen_logo.py`
recovers that grid from `spec/images/logo.png`, completes the frame foot that the supplied crop
cut off and writes the ink as 34 cell rectangles into `hardware/case/logo_data.scad` (18 x 35
cells, cell aspect 1.52). `logo.scad` scales them to millimetres and subtracts them; nothing
about the artwork is hard-coded, so a redrawn logo only means re-running the generator.

The same run writes `spec/images/logo.svg`, a 1 kB vector master in which one user unit is one
cell wide and `logo_aspect` units tall. That file, not the PNG, is what anything downstream
should start from - the PCB silkscreen footprint, a web page, a sticker.
`tests/test_case.py` rasterises it and compares it cell by cell with the grid.

| Where | Size | Stroke | Parameters |
|-------|------|--------|------------|
| Box cap plate, centred at (-59.525, 21.9) | 18.0 x 52.5 mm | 1.0 mm | `logo_cell`, `logo_stretch` |
| Case underside, centred at (0, 25.5), turned 90 degrees (off by default) | 52.5 x 18.0 mm | 0.9 mm | `logo_on_floor`, `logo_floor_cell`, `logo_floor_rot` |

Only the cap carries the wordmark by default; the floor engraving stayed in the model as an
option (`logo_on_floor = true`) after it was dropped in the review of 2026-11-07.

The relief is engraved, not raised: both faces lie on the bed when the part is printed, where
raised lines would need support. `logo_depth` is 0.6 mm, three layers at 0.2, and no groove
bridges further than one cell. `logo_invert = true` engraves the field instead, leaving the
lines standing 0.6 mm proud - it looks more like a relief but puts only the thin strokes on the
bed. For a two-colour cap, keep the default and put a filament change at 0.6 mm: the wordmark
then comes out flush in the second colour.

On the cap the wordmark keeps 5.0 mm to the long edges, 2.45 mm to the ends and 1.5 mm to both
screw holes; on the floor it keeps at least 1.1 mm to the nearest foot recess. `case.scad`
mirrors the left half as a whole and flips y for the export (print frame, see
`hardware/case/README.md`), so `logo.scad` mirrors the wordmark back for both - it reads the same
way round on both halves, which `tests/test_case.py` checks on the rendered meshes.

Set `logo_on_cap = false` for a plain case.

## 9. Open points

- LED window position is a guess at the nice!nano LED; verify on the controller.
- `box_inner_x` = -45.5: 0.75 mm to the inner column caps, 1.5 mm to the controller.
- `lid_fit` (0.15 mm between lip and wall), `hinge_clear` (0.3 mm around a knuckle) and
  `hinge_pin_fit` (0.2 mm around the rod) are set for a 0.4 mm nozzle; adjust after the first
  lid print, and check that the folded lid does not rock as a foot.
- The kickstand reaches about 54 mm (right; 57 left) inward beyond the inner wall; the two
  halves need that gap between them.
- First print: pocket test, then the right tray, then the four lid plates.
- PCB guard: `cap_skirt_z` 5.0 and `switch_travel` 3.0 come from the keycap model and the Choc
  V1 data. Press a real MBK-capped switch all the way down and check that the skirt clears
  the guard (1.2 mm expected). Check also that the flange holds the guard without lifting the
  switch out of its socket.
- The supplied wordmark is cropped at the top; the frame foot is mirrored in to close it. If
  the owner supplies the uncropped original, drop `close_frame` in `scripts/gen_logo.py`.
