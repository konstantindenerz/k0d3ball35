# Image catalogue

The documentation references images that do not exist as files yet. Every image is defined here
as a generation prompt so that it can be produced with an image model or replaced by a real photo
or render later.

Convention: a document embeds an image as `![alt text](images/<id>.png)`. The `<id>` is the heading
of the matching entry below. When a real file is added, put it at `docs/images/<id>.png` and keep
the prompt as documentation of the intended content.

Style anchor for all photographic prompts: a low-profile split keyboard in two halves, each in a
boxy, angular matte beige-grey 3D printed case whose stepped outline follows the column stagger,
with a slightly raised rectangular controller box at the inner edge, white and light-grey
low-profile keycaps, three bright orange thumb keycaps on the left half and two on the right, a
glossy white 19 mm trackball sitting low in a round pocket of the case directly beside the right
thumb keys (ball top only a little above the keycaps), no cables, on an oiled oak desk with a silver laptop in the background, soft daylight from the left,
shallow depth of field, product-photography look. Diagram prompts use a clean technical style:
white background, thin dark-grey lines, one accent colour (orange), sans-serif labels.

---

## img-hero-desk

Aspect 16:9. Hero photo.

```prompt
Product photo, two halves of a low-profile split mechanical keyboard on an oiled oak desk, matte
beige-grey 3D printed cases with flat tops, white and light-grey low-profile keycaps in a
column-staggered 3x5 grid, three thumb keys on the left half and two on the right, orange thumb
keycaps, boxy angular cases with a raised controller box at the inner edge, the right half has a
glossy white 19 mm trackball sitting in a round pocket of the case right next to its two thumb
keys, no cables anywhere, a
silver laptop and a tablet blurred in the background, soft daylight from the left, shallow depth
of field, 45 degree three-quarter view, photorealistic.
```

## img-hero-topdown

Aspect 3:2. Straight top-down of both halves.

```prompt
Top-down product photo of a 35-key wireless split keyboard, two halves 10 cm apart on light oak,
column-staggered keys with the pinky column noticeably lower, angular stepped case outlines, the
left half with three fanned thumb keys rotated 0, 10 and 20 degrees, the right half with only the
two outer thumb keys and a white 19 mm trackball in a round pocket directly beside them below the
middle and ring finger columns, white keycaps with orange thumb caps, matte grey boxy cases with a
raised controller box at each inner edge, even soft light, photorealistic.
```

## img-layout-top

Aspect 2:1. Diagram of key positions.

```prompt
Technical diagram, white background, both halves of a split keyboard drawn as rounded squares of
17 x 16 mm on an 18 x 17 mm grid, five columns with vertical offsets (from the outside in: 10.4,
4.2, 0, 2.2, 4.5 mm lower than the middle column), angular stepped board outlines following the
stagger, the left half with three thumb keys in an arc below the inner columns rotated 0, 10 and
20 degrees, the right half with the two outer thumb keys and a dashed circle of 28 mm inside an
octagonal notch beside them labelled "ball pocket", thin grey lines, orange highlight on the thumb
keys, dimension arrows with millimetre labels, sans-serif font.
```

## img-layout-compare-keyball

Aspect 2:1. Overlay of Keyball39 and k0d3ball35 geometry.

```prompt
Technical overlay diagram, white background, two key layouts drawn as outlines on top of each
other: grey outlines of a 19.05 mm pitch layout with 39 keys and a 34 mm ball circle, orange
outlines of an 18 x 17 mm pitch layout with 35 keys and a 19 mm ball circle beside the right thumb keys, same column stagger
proportions, legend in the corner, thin lines, sans-serif labels.
```

## img-matrix-diagram

Aspect 4:3. Key matrix wiring.

```prompt
Schematic-style diagram, white background, a 4 by 5 grid of switch symbols each in series with a
diode, five vertical column lines labelled COL0 to COL4 on top, four horizontal row lines labelled
ROW0 to ROW3 on the right, diode cathodes pointing towards the row lines, the two unused cells in
the bottom row drawn dashed, labels "D4 D5 D6 D7 D8" above the columns and "D21 D20 D19 D18" next to
the rows, orange highlight on the thumb cells (three on the left half's diagram, two on the right
half's, drawn side by side), clean thin lines.
```

## img-pinout-controller

Aspect 3:4. Controller pin assignment.

```prompt
Technical diagram of a Pro Micro form factor wireless controller board seen from above, 12 pins
on each long edge, USB-C at the top, each pin labelled with a short tag: left side from top D1, D0,
GND, GND, D2, D3, D4 COL0, D5 COL1, D6 COL2, D7 COL3, D8 COL4, D9; right side from top RAW B+, GND,
RST, VCC, D21 ROW0, D20 ROW1, D19 ROW2, D18 ROW3, D15 SCLK, D14 MOT, D16 SDIO, D10 NCS; matrix pins
in grey, trackball pins in orange, white background, sans-serif.
```

## img-stackup-section

Aspect 3:1. Cross-section of one half.

```prompt
Technical cross-section drawing, white background, from top to bottom: a low-profile keycap,
a Choc switch 11 mm tall, a hot-swap socket under a 1.6 mm PCB, a controller board on 3.5 mm
sockets with a thin 3.3 mm battery lying underneath it between the sockets, a 1.5 mm printed case
floor with rubber bumpers, dimension arrows on the right with millimetre values, orange accent on
the battery, sans-serif labels.
```

## img-cradle-section

Aspect 1:1. Trackball cradle cross-section.

```prompt
Technical cross-section drawing of a trackball module in a case pocket: a 19 mm ball resting on
three small 2 mm ceramic balls set in a printed cup, the cup standing on a rectangular housing that
reaches down to the case floor beside a 1.6 mm PCB (the PCB ends with a small gap next to the cup),
two screw ears on the floor, a small sensor board with a lens inside the housing under the ball
with a dimension arrow "2.4 mm" between lens and ball surface, a second arrow "17 mm" from the PCB
top to the ball top, the ball's top a little above the keycap height, white background, thin lines,
orange accent on the dimensions, sans-serif labels.
```

## img-cradle-exploded

Aspect 4:3. Exploded view of the trackball module.

```prompt
Exploded technical rendering on white, vertically stacked with thin guide lines: a white 19 mm
ball, a thin retainer ring with three claws, a beige printed cup on a rectangular housing with two
screw ears and three small ceramic balls shown slightly lifted out of their seats, a small green
sensor board with a black lens and a flat flex cable sliding into the housing from below, two M2
screws for the board and two for the case floor, a beige case floor with a round pocket, soft
studio lighting, clean.
```

## img-exploded-half

Aspect 3:4. Exploded view of the right half.

```prompt
Exploded view rendering on white of the right half of a split keyboard: from top, 17 white and
orange low-profile keycaps, 17 low-profile switches, the angular main PCB with an octagonal notch
at its lower outer edge, hot-swap sockets and diodes on the underside, a controller on socket
strips, a flat battery, a trackball cradle with a 19 mm ball standing beside the PCB notch, a beige
boxy printed case bottom with a round pocket, all parts aligned vertically with thin guide lines,
soft light.
```

## img-sensor-board

Aspect 4:3. Sensor PCB top and bottom.

```prompt
Product photo on a white background of a tiny 26 x 25 mm green PCB shown twice side by side: top
side with a black 16-pin optical sensor chip and a small lens clipped onto it, bottom side with a
6-pin flat flex connector, a SOT-23 regulator and a few 0603 capacitors, two M2 holes, macro lens,
soft shadows.
```

## img-ffc-orientation

Aspect 2:1. FFC cable orientation diagram.

```prompt
Technical diagram, white background, two PCBs drawn in side view connected by a flat flex cable
with contacts on one side, both flip-lock connectors on the top side of their boards, the cable's
contact side marked in orange, pin 1 marked on each connector with a triangle, labels "main PCB",
"sensor PCB", "contacts face down into both connectors", sans-serif.
```

## img-parts-flatlay

Aspect 3:2. All parts before assembly.

```prompt
Flat lay photo on light grey paper, neatly arranged: two different bare black keyboard PCBs with
angular stepped outlines (one with an octagonal notch), a tiny sensor PCB, two small wireless
controller boards, 35 low-profile switches in rows, 30 white and 5 orange keycaps, a strip of SMD
diodes on tape, hot-swap sockets, two small flat LiPo batteries, a white 19 mm ball, three tiny
ceramic balls in a dish, a flat flex cable, M2 screws, top-down, soft light.
```

## img-build-step-diodes

Aspect 3:2. Soldering diodes.

```prompt
Macro photo of a black keyboard PCB on a silicone mat, a pair of tweezers placing a tiny SOD-123
diode onto two pads, a soldering iron tip approaching, several already soldered diodes in a row
with their cathode bands all pointing the same way towards a printed line on the silkscreen,
shallow depth of field.
```

## img-build-step-sockets

Aspect 3:2. Hot-swap sockets.

```prompt
Macro photo of the underside of a keyboard PCB with low-profile hot-swap sockets being soldered,
one socket held in place by a finger, soldered sockets with shiny fillets on both pads, flux
residue, tweezers in the corner, warm workshop light.
```

## img-build-step-controller

Aspect 3:2. Controller on sockets with battery underneath.

```prompt
Macro photo of a small wireless controller board sitting on two rows of thin socket strips above
a keyboard PCB, a thin flat 3 mm battery visible in the gap under the controller with its red and
black wires routed to a tiny white connector, USB-C port facing the board edge, shallow depth of
field.
```

## img-build-step-ffc

Aspect 3:2. Inserting the flex cable.

```prompt
Macro photo of fingers lifting the brown flip lock of a tiny 6-pin flat flex connector on a
keyboard PCB and sliding in a white flat flex cable with its blue stiffener facing up, a second
identical connector on a small sensor board next to it, bright even light.
```

## img-build-step-cradle

Aspect 3:2. Fitting ceramic balls into the cradle.

```prompt
Macro photo of a beige 3D printed trackball cup held between two fingers, a toothpick pressing a
tiny white 2 mm ceramic ball into one of three seats, two seats already filled, a white 19 mm ball
waiting on the desk behind, soft light.
```

## img-build-step-ball

Aspect 3:2. Trackball module mounted.

```prompt
Photo of the right half of a low-profile split keyboard without keycaps, the beige trackball cup
standing in a round pocket of the case beside the two thumb switches, inside an octagonal notch of
the PCB edge, a white 19 mm ball dropped in, switches installed in the hot-swap sockets, the
controller visible in the raised box at the inner edge, three-quarter view, oak desk.
```

## img-build-step-flash

Aspect 3:2. Flashing the firmware.

```prompt
Photo of a laptop screen showing a file manager window with a removable drive named NICENANO and
a UF2 file being dragged onto it, a half of a split keyboard connected by a short USB-C cable in
the foreground, its reset button being pressed with a fingernail, shallow depth of field.
```

## img-firmware-layers

Aspect 16:9. Layer overview diagram.

```prompt
Infographic on white, eight small keyboard layouts of 35 keys (three thumb keys left, two right) arranged in two rows of four,
each labelled: Base, Nav, Num, Sym, Mouse, Scroll, Snipe, System, with the thumb keys that
activate each layer highlighted in orange and a few representative key labels on each layout,
clean sans-serif typography, thin grey lines.
```

## img-power-budget

Aspect 16:9. Battery life chart.

```prompt
Clean bar chart on white comparing estimated battery life in days for four cases: plain half with
110 mAh, plain half with 300 mAh, trackball half with 300 mAh in normal mode, trackball half with
300 mAh with the sensor forced awake; bars in grey with the recommended configuration in orange,
axis labels and values, sans-serif.
```

## img-cradle-render-19-25

Aspect 2:1. Two cradle sizes.

```prompt
Rendering on white of two beige 3D printed trackball cradles side by side, the left one holding a
19 mm white ball, the right one a 25 mm white ball, both standing on the same rectangular housing
with two screw ears and a cable slot, a small ruler for scale, soft studio light.
```

## img-case-concept

Aspect 16:9. Case concept for the later phase.

```prompt
Concept rendering of a low-profile boxy beige-grey printed case for the right half of a split
keyboard, angular stepped outline following the key columns, flat top flush with the keycap skirts,
a raised rectangular controller box at the inner edge with a small round window glowing faintly
blue from the controller LED, a visible USB-C opening and a tiny slide switch slot on that box, a
round pocket beside the two thumb keys holding a white 19 mm trackball whose top is just above the
keycaps, oak desk, soft light.
```

## img-testing-bench

Aspect 3:2. Bench test.

```prompt
Photo of a multimeter probe touching a diode pad on an unpopulated keyboard PCB, the meter showing
a diode-test reading, a printed checklist next to it with ticked boxes, a USB meter inline on a
cable to a controller, workshop light.
```

## img-build-identify-halves

Aspect 3:2. Which face is up for which half.

```prompt
Top-down photo of two bare green keyboard PCBs side by side on a cutting mat, near mirror images
of each other with angular stepped outlines, the right-hand board with an octagonal notch at its
lower outer edge and only two thumb key positions, the left-hand board with three thumb positions,
each with a small silkscreen text below the controller outline reading "k0d3ball35 r2 LEFT half"
and "RIGHT half", even light, no components.
```

## img-build-step-power-switch

Aspect 3:2. Bottom-face parts near the controller.

```prompt
Macro photo of the underside corner of a keyboard PCB: a small black slide switch with its
actuator pointing to the board edge next to an "ON" silkscreen label, a tiny 3.5 mm tactile button
below it, and a white 6-pin flat flex connector with its flip lock open further along the board,
all soldered, tweezers at the edge of the frame, warm workshop light.
```

## img-build-step-battery

Aspect 3:2. Battery wired to the pads.

```prompt
Macro photo of a thin 110 mAh lithium polymer pouch cell with red and black leads soldered to two
small plated pads on a keyboard PCB, the red lead on a square pad marked "+", a multimeter probe
touching a nearby controller hole, a slide switch in the off position, shallow depth of field.
```

## img-build-step-smoke-test

Aspect 3:2. Matrix test before switches are installed.

```prompt
Photo of a keyboard PCB without switches connected to a laptop by a USB-C cable, a hand holding a
short piece of wire across the two contacts of one hot-swap socket, the laptop screen showing a text
editor with a single typed character, oak desk, daylight.
```

## img-build-step-sensor-lens

Aspect 3:2. Sensor and lens on the daughterboard.

```prompt
Macro photo of a small green 26 by 25 millimetre PCB held in a helping-hands clamp, a black
16-pin optical sensor pushed through a rectangular cutout from the back, its leads freshly soldered
on the front, a clear plastic LM18 style lens with two guide posts held in tweezers about to be
clipped onto the sensor body, bright even light.
```

## img-build-step-lens-gauge

Aspect 3:2. Checking the lens distance.

```prompt
Macro photo looking into a beige 3D printed trackball cup without the ball, a thin steel feeler
gauge laid flat across the 9 millimetre hole at the bottom of the cup over the lens aperture,
three tiny white ceramic bearings visible around the cup wall, a finger holding the gauge, soft
light.
```

## img-build-step-switches

Aspect 3:2. Installing switches and keycaps.

```prompt
Photo of a low-profile split keyboard half with most Choc switches installed in their hot-swap
sockets, a thumb pressing the last switch into a rotated thumb position while a finger supports the
PCB from below, a pile of white and light-grey low-profile keycaps and two orange ones next to it,
oak desk, three-quarter view.
```
