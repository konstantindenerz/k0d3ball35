# Trackball cradle

Parametric OpenSCAD model of the trackball holder: a cup with three static ceramic
bearings, a housing for the PMW3610 sensor daughterboard underneath, and, since r2, a base
that stands on the case floor in a pocket beside the right PCB. A separate claw ring keeps
the ball from falling out when a half is lifted or turned over.

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
| `pocket` | 19.05 | case pocket beside the right PCB, PCB notch apothem 15 mm | `cradle-19mm-pocket.stl`, `retainer-19mm.stl` | r2 default |
| `pocket` | 25 | same, but needs a PCB notch apothem of 16.5 mm and a 35 mm pocket | `cradle-25mm-pocket.stl`, `retainer-25mm.stl` | fallback, different PCB |
| `cutout` | 25 | through a 30 mm round cutout of the PCB, flange under the PCB | `cradle-25mm-cutout.stl`, `retainer-25mm.stl` | r1, kept for reference |

The 19.05 mm (3/4 inch) ball is the smallest size with a working precedent in keyboards
(torabo-tsuki LP ships 19.05 mm POM balls, LiNEA40 uses 19 mm on a PMW3610); see
`docs/00-feasibility.md`. Nothing smaller exists as a keyboard trackball.

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
| 25 mm, pocket | +10.55 | +23.05 mm | +9.55 | -7.75 | -11.6 | 29.0 mm | 29.6 mm |
| 25 mm, cutout (r1) | +10.55 | +23.05 mm | +9.55 | -7.75 | n.a. (-7.75 lowest plastic) | 29.0 mm | 40 mm flange under the PCB |

Numbers are reproduced by `make stack` into `stack.json`. The ball top height is
`2 R - 1.95 mm` as long as the sensor sits straight below the ball and the floor stays at
-11.6: lowering the floor lowers the ball by the same amount, there is no other lever.
With Choc caps at about 11 mm the 19 mm ball stands 6 mm proud of the keycaps; the 25 mm
ball stood 12 mm proud.

### Pocket mount (r2)

- The housing is a 30 x 29 mm box (sensor board 26 x 25 plus 2 mm walls) that runs from the
  floor up to 0.3 mm under the PCB underside. The sensor board slides in from below with its
  lens against the housing face at z = -7.75 and is fastened with two M2 screws into the
  same two posts as before. Its component side (FPC connector, passives, sensor leads)
  faces the floor; the 2.25 mm gap between board and floor takes the solder and the FFC.
- The key-facing (-y) wall is open below the board plane (a 24 mm wide slot), the FFC leaves
  through it towards connector J1 on the PCB underside.
- Two ears with 1.6 mm pilot holes sit on the floor at +x and -x (overall footprint
  43 x 29 mm, see `dxf/floor-19mm-pocket.dxf` with 0.5 mm clearance added). M2 self-tapping
  screws come up through the case floor into the ears; the PCB is not touched.
- Above the PCB underside nothing is wider than 24.1 mm for the 19 mm ball, so the module
  passes through the PCB's octagonal notch (apothem 15 mm = layout `cradle_diameter` 28 / 2
  plus 1 mm) with margin. A keep-out cut in the model enforces this; the 25 mm pocket
  variant needs `notch_apothem = 16.5`, which is a different PCB.
- `part = "floor2d"` exports the floor footprint for the case design.

### Tilted sensor, evaluated and not recommended

`sensor_angle` rotates the sensor housing about the ball centre towards +x (cutout mount
only). The idea is the torabo-tsuki / Rollino layout where the sensor looks at the ball from
the side so the ball can sit lower. For this module it does not pay off: up to about 45 deg
the 26 mm wide sensor board swings down and becomes the lowest point, at 60 deg there is no
gain and the housing reaches 23 mm out from the axis into the key area. With the 19 mm ball
the straight-down stack is already 6 mm lower than r1 was, so the topic is closed.

### Ball retention

The cup rim stops 1 mm below the equator all around, so the thumb reaches the ball freely.
The separate retainer is a 1.2 mm ring sitting on that rim with three claws that follow
the ball with the same 0.4 mm gap as the cup and rise 4.8 mm above the ring. The 19 mm ball
can lift 0.85 mm before the claws block it (25 mm: 1.15 mm). Three pegs press into holes in
the rim; pull the ring off to take the ball out for cleaning. The claws sit at 30, 150 and
270 degrees so none of them is in the way of the thumb coming from the inner side.

### Bearings

Three ZrO2 balls of 2.0 mm at 60, 180 and 300 degrees, 35 degrees below the equator, so
the contact circle has a radius of 7.8 mm (19 mm ball) and the ball cannot tip. Seats are
1.9 mm holes, 1.6 mm deep, drilled radially: the bearing bottoms out in the hole with its
centre exactly one radius behind the cup surface and touches the trackball. Printed holes
come out slightly undersize; ream with a 1.9 to 2.0 mm bit if a bearing does not press in,
and fix each one with a dot of cyanoacrylate at the rim of the seat (not under the ball).

### Interfaces that other parts of the project rely on

- Right PCB (`docs/01-design-spec.md` section 5, `hardware/layout/output/points-right.json`):
  ball centre (+5, +64), octagonal notch with apothem 15 mm around it, no copper or parts
  needed around the notch. The cradle never touches the PCB.
- Case (`issues/mech-case-ball-pocket.md`): pocket wall circle 32 mm around the ball centre
  above the PCB plane, floor at -11.6 mm under the module with the footprint from
  `dxf/floor-19mm-pocket.dxf`, two M2 holes 36 mm apart on the x axis.
- Sensor daughterboard (`hardware/sensor-pcb`): 26 x 25 mm, two M2 holes 20 mm apart along
  the 25 mm axis, the sensor optical centre at the board centre, the LM18-LSI lens and the
  sensor body cutout running along the 26 mm side. The board is screwed with its lens side
  ("BALL SIDE", sensor body protruding 0.7 mm) against the flat housing face. The lens-side
  pocket is 3.8 mm deep and 24 x 23 mm wide, so the FPC connector and every other part sit on
  the component side facing the floor. Resulting stack from the ball surface: lens flange
  2.40 mm, lens-side PCB face 5.80 mm, component-side face 7.40 mm, sensor top 9.05 mm
  (matches `docs/08-trackball-module.md`).

## Printing

- Material: PETG or PLA, any colour. PETG is less brittle for the retainer pegs.
- Layer height 0.12 mm, 3 perimeters, 30 percent infill, no supports.
- Cradle: print upright (ears down), the cup interior and the lens cavity are closed at
  45 degree or steeper angles. The three bearing bosses print as small overhangs on the
  outside, fine at 0.12 mm. The cable slot is a bridge of 24 mm at the board plane; it
  prints fine at 0.12 mm, add a support blocker only if your printer sags.
- Retainer: print upside down (claw tips on the bed) so the pegs point up; the chamfered
  claw tips are then the first layers.
- Print one spare retainer; the pegs are the first thing to break.

## Assembly

1. Press the three ceramic balls into their seats from inside the cup, add a dot of glue
   at each seat rim. Let it cure, then roll the trackball in the cup: it must spin without
   a click or scrape.
2. Peel the protective films off the sensor and clip the LM18-LSI lens onto the PMW3610.
3. Plug the FFC into the sensor board first (the connector is unreachable once the board is
   in the housing), then slide the board lens-first into the housing from below, cable out
   through the slot, and fasten it with two M2x5 self-tapping screws from the floor side.
   The lens must sit flat in its pocket and the aperture must be centred in the 9 mm hole
   when you look into the cup.
4. Stand the module on the case floor in the pocket, ears on the x axis, slot towards the
   keys; fasten with two M2x6 self-tapping screws from underneath the case (or M2x6 machine
   screws into heat-set inserts if you set `flange_pilot_d = 3.2`).
5. Route the FFC to J1 on the PCB underside, insert, close the lock.
6. Put the ball in, push the retainer onto the rim.

## Test-fit checklist (do this before ordering PCBs)

- Ball spins freely in every direction and settles without wobble: bearings seated.
- Lift the half, turn it over, shake gently: ball stays in.
- Lens distance: with the ball out, lay a 2.0 mm feeler gauge on the lens aperture through
  the 9 mm hole and check that it is flush with the cup surface at the bottom (the ball
  rests 0.4 mm above the cup surface, so 2.0 mm gauge plus 0.4 mm design gap gives the
  2.4 mm the datasheet asks for). Anything between 2.2 and 2.6 mm total is inside the window.
- Notch clearance: lay the printed module next to a 1.6 mm board with the octagonal notch
  (print the notch from `hardware/layout/output/outline-right.dxf`): at least 0.3 mm all
  round between the cup and the notch edge.
- Thumb clearance: check that the thumb reaches the ball at its equator from the inner side
  without touching a claw.
- Flash the firmware and watch the cursor: a 19 mm ball at 600 cpi should move the cursor
  about one screen width per half turn. Jitter at rest means the lens is not seated.

## Open points

- The ball top at +17.1 mm (19 mm ball) is set by physics (sensor straight below the ball,
  floor at -11.6). The next levers are a thinner sensor stack (PAW3222 module, 3.3 mm from
  board to ball) or a deeper floor under the pocket only.
- Retainer pegs rely on friction. If they loosen, switch to a bayonet ring.
- Bearing seat size is tuned for FDM; resin prints will need `bearing_fit` set to 0.

## Image prompts

```prompt
Technical cross-section illustration of a 3D printed trackball module standing in a case
pocket beside a keyboard PCB: a 19 mm white ball sitting in a thin blue cup, three small
ceramic bearings at 35 degrees below the equator, a flat orange retainer ring with three
claws above the equator, below the cup a rectangular housing reaching down to the case floor
with a green sensor PCB inside and a grey lens block looking up at the ball, two small screw
ears on the floor, the 1.6 mm green PCB ending 1 mm away from the cup with an angular notch,
dimension lines for 2.4 mm lens distance and 17 mm ball height, clean CAD line-art style,
white background.
```

```prompt
Exploded assembly drawing of a trackball module: from top to bottom a 19 mm white ball, a
thin retainer ring with three claws and three pegs, a cup with three tiny ceramic balls on a
rectangular housing with two screw ears, a 26 x 25 mm sensor board with a lens sliding in
from below, two M2 screws, a flat ribbon cable leaving sideways through a slot, two longer
screws coming up through a beige case floor, isometric, pastel colours, labelled parts.
```
