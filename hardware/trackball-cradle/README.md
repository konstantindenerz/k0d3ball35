# Trackball cradle

Parametric OpenSCAD model of the trackball holder: a cup with three static ceramic
bearings, a housing for the PMW3610 sensor daughterboard underneath, and, since r2, a base
that stands on the case floor in a pocket beside the right PCB. There is no retainer: the
rim stays below the ball equator, the ball rests in the cup by gravity and lifts straight
out for cleaning. The removable case lid (`issues/mech-case-lid.md`) covers it in transport.

Files

| File | Purpose |
|------|---------|
| `cradle.scad` | the model, `part` selects what is rendered |
| `params.scad` | every dimension, documented; `mount` and `ball_d` pick the variant |
| `Makefile` | builds STL, DXF (floor footprint / PCB cutout), PNG previews and `stack.json` |
| `stack.py` | collects the computed stack heights into `stack.json` |
| `stl/` | printable parts: 19.05 mm pocket (default), 25 mm pocket (fallback), 25 mm cutout (r1) |
| `dxf/` | 2D footprint on the case floor per pocket variant, PCB clearance for the cutout variant |
| `preview/` | rendered section and assembly views |

Requires OpenSCAD 2025 or newer with the Manifold backend (tested with 2026.10.11,
`brew install --cask openscad@snapshot`). Build everything with `make`.

## Variants

| `mount` | `ball_d` | Where it sits | STL | Status |
|---------|----------|---------------|-----|--------|
| `pocket` | 19.05 | case pocket beside the right PCB, PCB notch apothem 15 mm | `cradle-19mm-pocket.stl` | r2 default |
| `pocket` | 25 | same, but needs a PCB notch apothem of 16.5 mm and a 35 mm pocket | `cradle-25mm-pocket.stl` | fallback, different PCB |
| `cutout` | 25 | through a 30 mm round cutout of the PCB, flange under the PCB | `cradle-25mm-cutout.stl` | r1, kept for reference |

The 19.05 mm (3/4 inch) ball is the smallest size with a working precedent in keyboards
(torabo-tsuki LP ships 19.05 mm POM balls, LiNEA40 uses 19 mm on a PMW3610); see
`spec/00-feasibility.md`. Nothing smaller exists as a keyboard trackball.

## Geometry and stack

Coordinate system: z up, z = 0 is the top surface of the main PCB, the ball centre is on
the z axis, +x points outward (towards the pinky), +y towards the user. The sensor optical
axis points straight down through the ball centre.

The vertical stack is taken from the PMW3610DM-SUDU datasheet (figure 4, assembly drawing
with the LM18-LSI lens):

| Element | Height | Source |
|---------|--------|--------|
| ball surface to lens reference plane (Z) | 2.4 mm (2.2 min, 2.6 max) | table 2 |
| lens reference plane to sensor PCB | 3.4 mm | figure 4, "gap between PCB and base plate" |
| sensor PCB | 1.6 mm | figure 4 |
| sensor package and solder on the far side | 2.25 mm | figure 4 (1.65) + margin |

So the sensor PCB plane sits `R + 2.4 + 3.4` below the ball centre, and the lowest point
of the module is another 3.85 mm further down. In the pocket mount that lowest point is the
case floor: `depth_below_pcb = 10` puts the floor 10 mm under the PCB underside, i.e. at
z = -11.6, the same plane the r1 cutout design used. The resulting heights:

| Variant | Ball centre | Ball top above PCB top | Cup rim | Sensor PCB plane | Floor | Cup outer | Largest diameter above the PCB |
|---------|-------------|------------------------|---------|------------------|-------|-----------|-------------------------------|
| 19.05 mm, pocket | +7.58 | **+17.1 mm** | +6.58 | -7.75 | -11.6 | 23.1 mm | 24.1 mm (bearing bosses) |
| 25 mm, pocket | +10.55 | +23.05 mm | +9.55 | -7.75 | -11.6 | 29.0 mm | 29.0 mm |
| 25 mm, cutout (r1) | +10.55 | +23.05 mm | +9.55 | -7.75 | n.a. (-7.75 lowest plastic) | 29.0 mm | 40 mm flange under the PCB |

Numbers are reproduced by `make stack` into `stack.json`. The ball top height is
`2 R - 1.95 mm` as long as the sensor sits straight below the ball and the floor stays at
-11.6: lowering the floor lowers the ball by the same amount, there is no other lever.
With Choc caps at about 11 mm the 19 mm ball stands 6 mm proud of the keycaps; the 25 mm
ball stood 12 mm proud.

### Pocket mount (r2)

- The housing is a 29 x 29 mm box (sensor board 26 x 25 plus walls of 1.5 mm on x and 2 mm on
  y) that runs from the floor up to 0.3 mm under the PCB underside. On x it is 1 mm narrower
  than the notch is wide across its flats, so it clears the PCB edge by 0.5 mm while the module
  is lowered into its pocket. The sensor board slides in from below with its
  lens against the housing face at z = -7.75 and is clamped to the same two M2 posts as
  before. Its component side (FPC connector, passives, sensor leads) faces the floor; the
  2.25 mm gap between board and floor takes the solder and the FFC.
- The key-facing (-y) wall is open below the board plane (a 23 mm wide slot), the FFC leaves the
  sensor connector through it. From the board plane up, the same wall carries a 6 mm wide channel
  in line with the connector (`cable_ch_x`, `cable_ch_w`): the cable turns up there, climbs the
  2.95 mm gap between the cup and the PCB notch and folds over the board edge into J1 on the key
  side of the main PCB. Nothing of the cable runs under the PCB any more.
- The two sensor posts double as the case fastening: their 1.6 mm pilot holes run straight
  down to the housing underside, and two M2 x 10 countersunk (90 degree flat head)
  self-tapping screws come up from below through the case floor (2.5 mm, the head sinks into
  a cone in its underside), the 2.25 mm component gap and the sensor board (1.6 mm) into the
  posts (`case_screw_sp` = 20 mm on the y axis through the ball centre, about 3.8 mm of
  thread in each post). The board stays clamped to the posts as before, the housing walls
  stand on the floor, and there are no lugs or extra holes: the floor footprint is the bare
  29 x 29 mm housing (`dxf/floor-19mm-pocket.dxf`: 30 x 30 mm outline with 0.5 mm clearance
  and two 2.2 mm holes). The PCB is not touched.
- Above the PCB underside nothing is wider than 24.1 mm for the 19 mm ball, so the module
  passes through the PCB's notch (apothem 15 mm = layout `cradle_diameter` 28 / 2
  plus 1 mm) with margin. A keep-out cut in the model enforces this; the 25 mm pocket
  variant needs `notch_apothem = 16.5`, which is a different PCB.
- The notch's corner towards the keys and the inner column is square, not a 45 degree facet:
  otherwise the board would overhang the housing by 5.86 mm and the module could neither be
  lowered into the pocket nor taken out with the PCB fitted
  (`issues/mech-cradle-notch-relief.md`).
- `part = "floor2d"` exports the floor footprint for the case design.

### Tilted sensor, evaluated and not recommended

`sensor_angle` rotates the sensor housing about the ball centre towards +x (cutout mount
only). The idea is the torabo-tsuki / Rollino layout where the sensor looks at the ball from
the side so the ball can sit lower. For this module it does not pay off: up to about 45 deg
the 26 mm wide sensor board swings down and becomes the lowest point, at 60 deg there is no
gain and the housing reaches 23 mm out from the axis into the key area. With the 19 mm ball
the straight-down stack is already 6 mm lower than r1 was, so the topic is closed.

### Ball retention

There is none, by design. The cup rim stops `rim_drop` = 1 mm below the equator all around
(`rim_z` = ball centre minus 1 mm, `rim_below_equator` in `stack.json`), so the thumb reaches
the ball at its widest point from every side and nothing above the rim can touch it. The ball
sits on the three bearings by gravity and lifts straight out for cleaning. In use the half
lies flat and the ball cannot leave the cup; for transport the removable case lid
(`issues/mech-case-lid.md`) covers keys and ball, which is why a claw ring, lip or bayonet
retainer was dropped. If you carry a bare half without the lid, take the ball out first.

### Bearings

Three ZrO2 balls of 2.0 mm at 60, 180 and 300 degrees, 35 degrees below the equator, so
the contact circle has a radius of 7.8 mm (19 mm ball) and the ball cannot tip. Seats are
1.9 mm holes, 1.6 mm deep, drilled radially: the bearing bottoms out in the hole with its
centre exactly one radius behind the cup surface and touches the trackball. Printed holes
come out slightly undersize; ream with a 1.9 to 2.0 mm bit if a bearing does not press in,
and fix each one with a dot of cyanoacrylate at the rim of the seat (not under the ball).

### Interfaces that other parts of the project rely on

- Right PCB (`spec/01-design-spec.md` section 5, `hardware/layout/output/points-right.json`):
  ball centre (-13, +66), notch with apothem 15 mm around it (square corner towards the keys), no copper or parts
  needed around the notch. The cradle never touches the PCB.
- Case (`issues/mech-case-ball-pocket.md`): pocket wall circle 32 mm around the ball centre
  above the PCB plane, below the PCB plane a rounded rectangle of 34 x 34 mm around the
  housing (0.5 mm clearance plus a 2 mm wall) that merges into the cavity under the PCB,
  floor at -11.6 mm under the module with the footprint from `dxf/floor-19mm-pocket.dxf`,
  two M2 holes 20 mm apart on the y axis (`case_screw_sp` in `stack.json`).
- Sensor daughterboard (`hardware/sensor-pcb`): 26 x 25 mm, two M2 holes 20 mm apart along
  the 25 mm axis, the sensor optical centre at the board centre, the LM18-LSI lens and the
  sensor body cutout running along the 26 mm side. The board is screwed with its lens side
  ("BALL SIDE", sensor body protruding 0.7 mm) against the flat housing face. The lens-side
  pocket is 3.8 mm deep and 24 x 23 mm wide, so the FPC connector and every other part sit on
  the component side facing the floor. Resulting stack from the ball surface: lens flange
  2.40 mm, lens-side PCB face 5.80 mm, component-side face 7.40 mm, sensor top 9.05 mm
  (matches `spec/08-trackball-module.md`).

## Printing

- Material: PETG or PLA, any colour.
- Layer height 0.12 mm, 3 perimeters, 30 percent infill, no supports.
- Cradle: print upright (housing down, open side on the bed), the cup interior and the lens
  cavity are closed at 45 degree or steeper angles. The three bearing bosses print as small overhangs on the
  outside, fine at 0.12 mm. The cable slot bridges the key-facing wall at the board plane in two
  spans of about 8 mm (the vertical cable channel interrupts it in the middle); both print fine at
  0.12 mm, add a support blocker only if your printer sags.
- Deburr the rim with a fingernail or a fine file: it is the only printed edge near the ball
  and a stray strand of filament there is what makes a ball scrape.

## Assembly

1. Press the three ceramic balls into their seats from inside the cup, add a dot of glue
   at each seat rim. Let it cure, then roll the trackball in the cup: it must spin without
   a click or scrape.
2. Peel the protective films off the sensor and clip the LM18-LSI lens onto the PMW3610.
3. Plug the type B FFC into the sensor board first (the connector is unreachable once the board
   is in the housing), then slide the board lens-first into the housing from below, cable out
   through the slot and up the channel in the key-facing wall. For a bench test without the case
   hold it with two short M2 x 5 self-tapping screws; they come out again in the next step. The
   lens must sit flat in its pocket and the aperture must be centred in the 9 mm hole when you
   look into the cup.
4. Stand the module on the case floor in the pocket, screw holes on the y axis, slot towards
   the keys; fasten with two M2 x 10 countersunk self-tapping screws from underneath the
   case, up through the floor, the component gap and the sensor board into the posts (or
   M2 x 10 countersunk machine screws into heat-set inserts if you set `flange_pilot_d =
   3.2`). The flat head disappears into the 90 degree cone in the case underside. Snug, not
   tight: the screws clamp the board and hold the module at the same time.
5. Fold the cable over the PCB edge into J1 on the key side, contacts down, close the lock.
6. Drop the ball in. It must spin freely in every direction without touching the rim.

For service the order reverses: open the lock, pull the cable out of J1, undo the two screws from
below and lift the module out of the pocket. Keycaps and PCB stay where they are.

## Test-fit checklist (do this before ordering PCBs)

- Ball spins freely in every direction and settles without wobble: bearings seated.
- Rim clearance: with the ball in, a strip of paper slides between the ball and the rim all
  the way round; the ball must touch only the three bearings. The equator stands 1 mm above
  the rim.
- Lift the ball out with two fingers: nothing holds it. (It is retained in transport by the
  case lid, not by the cradle.)
- Lens distance: with the ball out, lay a 2.0 mm feeler gauge on the lens aperture through
  the 9 mm hole and check that it is flush with the cup surface at the bottom (the ball
  rests 0.4 mm above the cup surface, so 2.0 mm gauge plus 0.4 mm design gap gives the
  2.4 mm the datasheet asks for). The datasheet window is 2.2 to 2.6, but **aim for 2.3 to
  2.5**: every error in this stack is printed, and the ones that matter push the distance
  up, not down. If you are outside that, set `lens_shim` in `params.scad` to the measured
  difference (negative moves the board towards the ball) and print the cradle again.
  The sensitive term is the bearing seats, not the housing face. They sit 35 degrees below
  the equator, so a radial seat error d lifts the ball centre by d * cot(35) = 1.43 d: 0.1 mm
  of seat error is already 0.14 mm of lens distance, and 0.15 mm puts you out of spec. If the
  gauge reads high, suspect the seats before the face -- check that each ceramic ball is fully
  bottomed out in its hole.
- Case screws: with the module standing on a 2 mm test floor, an M2 x 10 screw from below
  must reach at least 3 mm into the post (in the case it passes 2.5 mm floor less the 1.3 mm
  countersink, 2.25 mm gap and 1.6 mm board first); the sensor board must sit flat on the posts and not bow when the screws are snug.
- Notch clearance: lay the printed module next to a 1.6 mm board with the notch (print the
  outline from `hardware/layout/output/outline-right.dxf`): at least 0.3 mm all round between
  the cup and the notch edge.
- Cartridge check: with that scrap board held at the PCB plane, lower the module into the pocket
  and lift it out again vertically. Nothing may catch: the housing clears the board edge by
  0.5 mm, which is what the square notch corner is for.
- Cable path: the FFC must run from the sensor connector through the slot, up the channel and
  over the board edge into J1 without a crease; the free gap beside the cup is 2.95 mm.
- Thumb clearance: check that the thumb reaches the ball at its equator from the inner side
  without touching the rim.
- Flash the firmware and watch the cursor: a 19 mm ball at 600 cpi should move the cursor
  about one screen width per half turn. Jitter at rest means the lens is not seated.

## Open points

- The ball top at +17.1 mm (19 mm ball) is set by physics (sensor straight below the ball,
  floor at -11.6). The next levers are a thinner sensor stack (PAW3222 module, 3.3 mm from
  board to ball) or a deeper floor under the pocket only.
- No retainer: the ball only stays in while the half lies flat or the case lid is on
  (`issues/mech-case-lid.md`). If that turns out to be a nuisance, a shallow bayonet ring on
  the rim is the fallback; the cup geometry does not change.
- Bearing seat size is tuned for FDM; resin prints will need `bearing_fit` set to 0.

## Image prompts

```prompt
Technical cross-section illustration of a 3D printed trackball module standing in a case
pocket beside a keyboard PCB: a 19 mm white ball sitting in a thin blue cup, three small
ceramic bearings at 35 degrees below the equator, the cup rim ending just below the ball's
equator with nothing above it, below the cup a rectangular housing reaching down to the case floor
with a green sensor PCB inside and a grey lens block looking up at the ball, two long screws
coming up through the floor and the sensor board into the housing, the 1.6 mm green PCB ending
1 mm away from the cup with an angular notch,
dimension lines for 2.4 mm lens distance and 17 mm ball height, clean CAD line-art style,
white background.
```

```prompt
Exploded assembly drawing of a trackball module: from top to bottom a 19 mm white ball, a
cup with three tiny ceramic balls on a plain
rectangular housing, a 26 x 25 mm sensor board with a lens sliding in from below, a flat
ribbon cable leaving sideways through a slot, two long M2 screws coming up through a beige
case floor and the sensor board into the housing, isometric, pastel colours, labelled parts.
```
