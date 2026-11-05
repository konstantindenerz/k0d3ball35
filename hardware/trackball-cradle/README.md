# Trackball cradle

Parametric OpenSCAD model of the trackball holder: a cup with three static ceramic
bearings, a housing for the PMW3610 sensor daughterboard underneath, and a flange that
bolts the whole module to the main PCB from below. A separate claw ring keeps the ball
from falling out when a half is lifted or turned over.

Files

| File | Purpose |
|------|---------|
| `cradle.scad` | the model, `part` selects what is rendered |
| `params.scad` | every dimension, documented |
| `Makefile` | builds STL, DXF (PCB cutout), PNG previews and `stack.json` |
| `stack.py` | collects the computed stack heights into `stack.json` |
| `stl/` | printable parts for 25 mm (default), 34 mm and the tilted-sensor experiment |
| `dxf/` | 2D outline of the clearance the main PCB needs, per variant |
| `preview/` | rendered section and assembly views |

Requires OpenSCAD 2025 or newer with the Manifold backend (tested with 2026.10.11,
`brew install --cask openscad@snapshot`). Build everything with `make`.

## Geometry and stack

Coordinate system: z up, z = 0 is the top surface of the main PCB, the ball centre is on
the z axis. The sensor optical axis points straight down through the ball centre
(`sensor_angle = 0`).

The vertical stack is taken from the PMW3610DM-SUDU datasheet (figure 4, assembly drawing
with the LM18-LSI lens):

| Element | Height | Source |
|---------|--------|--------|
| ball surface to lens reference plane (Z) | 2.4 mm (2.2 min, 2.6 max) | table 2 |
| lens reference plane to sensor PCB | 3.4 mm | figure 4, "gap between PCB and base plate" |
| sensor PCB | 1.6 mm | figure 4 |
| sensor package and solder on the far side | 2.25 mm | figure 4 (1.65) + solder |

So the sensor PCB plane sits `R + 2.4 + 3.4` below the ball centre, and the lowest point
of the module is another 3.85 mm further down. With `depth_below_pcb = 10` (lowest point
10 mm under the main PCB underside) the resulting heights are:

| Variant | Ball centre | Ball top above PCB top | Lowest plastic | Lowest sensor board | Housing reach from axis |
|---------|-------------|------------------------|----------------|---------------------|-------------------------|
| 25 mm, sensor below | +10.55 | **+23.05 mm** | -7.75 | -11.6 | 15.0 mm |
| 25 mm, sensor tilted 60 deg | +10.73 | +23.23 mm | -11.41 | -11.6 | 23.3 mm |
| 34 mm, sensor below | +15.05 | +32.05 mm | -7.75 | -11.6 | 15.0 mm |

Numbers are reproduced by `make stack` into `stack.json`. Lowering `depth_below_pcb`
raises the ball by the same amount; the ball top height is `depth + 1.6` less than
`R + 2.4 + 3.4 + 3.85 + R`, there is no other lever as long as the sensor sits below the ball.

### Tilted sensor, evaluated and not recommended

`sensor_angle` rotates the sensor housing about the ball centre towards +x. The idea is
the torabo-tsuki / Rollino layout where the sensor looks at the ball from the side so the
ball can sit lower. For this module it does not pay off:

- Up to about 45 deg the tilt makes things worse, because the 26 mm wide sensor board
  swings down and becomes the lowest point.
- At 60 deg there is no gain at all with the 26 mm board (the board edge becomes the lowest point), and the housing reaches 23 mm out from
  the axis and crosses the main PCB plane, so the PCB needs a keyhole cutout
  (`dxf/cutout-25mm-tilted.dxf`) and the sensor board stands above the PCB surface on the
  outer side, inside the key area.
- At 75 deg the ball drops 5 mm, with the same keyhole problem plus the module sitting next
  to the ball at keycap height.

The straight-down variant keeps the 30 mm round cutout from the design spec and all the
depth under the PCB where the case has room anyway. The STL for the 60 deg variant is
shipped for people who want to experiment with a slotted PCB.

### Ball retention

The cup rim stops 1 mm below the equator all around, so the thumb reaches the ball freely.
The separate retainer is a 1.2 mm ring sitting on that rim with three claws that follow
the ball with the same 0.4 mm gap as the cup and rise 4.8 mm above the equator. The ball
can lift 1.15 mm before the claws block it. Three pegs press into holes in the rim; pull
the ring off to take the ball out for cleaning. The claws sit at 30, 150 and 270 degrees
so none of them is in the way of the thumb coming from the inner side.

### Bearings

Three ZrO2 balls of 2.0 mm at 60, 180 and 300 degrees, 35 degrees below the equator, so
the contact circle has a radius of 10.2 mm and the ball cannot tip. Seats are 1.9 mm
holes, 1.6 mm deep, drilled radially: the bearing bottoms out in the hole with its centre
exactly one radius behind the cup surface and touches the trackball. Printed holes come
out slightly undersize; ream with a 1.9 to 2.0 mm bit if a bearing does not press in, and
fix each one with a dot of cyanoacrylate at the rim of the seat (not under the ball).

### Interfaces that other parts of the project rely on

- Main PCB (`docs/01-design-spec.md` section 5): round cutout 30 mm, three M2 holes on a
  36 mm bolt circle at 90, 210 and 330 degrees, nothing on the PCB underside within a
  40 mm circle (flange). `dxf/cutout-25mm.dxf` is the exact clearance including the holes.
  A 34 mm ball needs a 39 mm cutout and a 45 mm bolt circle: a different PCB revision.
- Sensor daughterboard (`hardware/sensor-pcb`): 26 x 25 mm, two M2 holes 20 mm apart along
  the 25 mm axis, the sensor optical centre at the board centre, the LM18-LSI lens and the
  sensor body cutout running along the 26 mm side. The board is screwed with its lens side
  ("BALL SIDE", sensor body protruding 0.7 mm) against the flat housing face. The lens-side
  pocket is 3.8 mm deep and 24 x 23 mm wide, so the FPC connector and every other part sit on
  the component side facing away from the ball, where the housing is open. Resulting stack
  from the ball surface: lens flange 2.40 mm, lens-side PCB face 5.80 mm, component-side
  face 7.40 mm, sensor top 9.05 mm (matches `docs/08-trackball-module.md`).

## Printing

- Material: PETG or PLA, any colour. PETG is less brittle for the retainer pegs.
- Layer height 0.12 mm, 3 perimeters, 30 percent infill, no supports.
- Cradle: print upright (flange down), the cup interior and the lens cavity are closed at
  45 degree or steeper angles. The three bearing bosses print as small overhangs on the
  outside, fine at 0.12 mm.
- Retainer: print upside down (claw tips on the bed) so the pegs point up; the chamfered
  claw tips are then the first layers.
- Print one spare retainer; the pegs are the first thing to break.

## Assembly

1. Press the three ceramic balls into their seats from inside the cup, add a dot of glue
   at each seat rim. Let it cure, then roll the trackball in the cup: it must spin without
   a click or scrape.
2. Peel the protective films off the sensor and clip the LM18-LSI lens onto the PMW3610.
3. Place the sensor board lens-first into the housing pocket and fasten it with two M2x5
   self-tapping screws from the pin side. The lens must sit flat in its pocket and the
   aperture must be centred in the 9 mm hole when you look into the cup.
4. Route the 6-pin FPC out of the housing towards the controller.
5. Drop the cradle into the PCB cutout from below until the flange touches the PCB, fasten
   with three M2x6 self-tapping screws from the top (or M2x6 machine screws into heat-set
   inserts if you set `flange_pilot_d = 3.2`).
6. Put the ball in, push the retainer onto the rim.

## Test-fit checklist (do this before ordering PCBs)

- Ball spins freely in every direction and settles without wobble: bearings seated.
- Lift the half, turn it over, shake gently: ball stays in.
- Lens distance: with the ball out, lay a 2.4 mm stack of paper or a feeler gauge on the
  lens aperture through the 9 mm hole and check that it is flush with the cup surface at
  the bottom (the ball rests 0.4 mm above the cup surface, so 2.0 mm gauge plus 0.4 mm
  design gap). Anything between 2.2 and 2.6 mm total is inside the datasheet window.
- Thumb clearance: with the module in a scrap of 1.6 mm board, check that the thumb reaches
  the ball at its equator from the inner side without touching a claw.
- Flash the firmware and watch the cursor: a 25 mm ball at 400 cpi should move the cursor
  about one screen width per half turn. Jitter at rest means the lens is not seated.

## Open points

- The ball height of 23 mm above the PCB is set by physics (sensor below the ball). If a
  lower ball is wanted, the next lever is a thinner sensor stack (PAW3222 module, 3.3 mm
  from board to ball) or moving the ball zone off the PCB entirely as torabo-tsuki does.
- Retainer pegs rely on friction. If they loosen, switch to a bayonet ring.
- Bearing seat size is tuned for FDM; resin prints will need `bearing_fit` set to 0.

## Image prompts

- Section view: "Technical cross-section illustration of a 3D printed trackball cradle:
  a 25 mm white ball sitting in a thin blue cup, three small ceramic bearings at 35 degrees
  below the equator, a flat orange retainer ring with three claws above the equator, below
  the cup a rectangular housing holding a green sensor PCB with a grey lens block looking up
  at the ball, a flange bolted under a 1.6 mm green PCB, dimension lines for 2.4 mm lens
  distance and 23 mm ball height, clean CAD line-art style, white background."
- Exploded view: "Exploded assembly drawing of a trackball module: from top to bottom a
  25 mm ball, a thin retainer ring with three claws and three pegs, a cup with three tiny
  ceramic balls, three M2 screws, a 22 x 25 mm sensor board with a lens, two M2 screws,
  a flat ribbon cable leaving to the side, isometric, pastel colours, labelled parts."
