# Image catalogue

The documentation references images that do not exist as files yet. Every image is defined here
as a generation prompt so that it can be produced with an image model or replaced by a real photo
or render later.

Convention: a document embeds an image as `![alt text](images/<id>.png)`. The `<id>` is the heading
of the matching entry below. When a real file is added, put it at `spec/images/<id>.png` and keep
the prompt as documentation of the intended content.

Style anchor for all photographic prompts: a low-profile split keyboard in two halves, each in a
boxy, angular matte beige-grey 3D printed case whose stepped outline follows the column stagger,
with a slightly raised rectangular controller box at the inner edge whose roof plate carries a
narrow labyrinth wordmark engraved into it, white and light-grey
low-profile keycaps, three bright orange thumb keycaps on the left half and two on the right, a
matte white 19 mm trackball sitting low in a round pocket of the case directly beside the right
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
matte white 19 mm trackball sitting in a round pocket of the case right next to its two thumb
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
two inner thumb keys and a matte white 19 mm trackball in a round pocket directly beside them below the
middle and ring finger columns, white keycaps with orange thumb caps, matte grey boxy cases with a
raised controller box at each inner edge, a narrow labyrinth wordmark engraved into the roof
plate of each controller box, even soft light, photorealistic.
```

## img-layout-top

Aspect 2:1. Diagram of key positions.

```prompt
Technical diagram, white background, both halves of a split keyboard drawn as rounded squares of
17 x 16 mm on an 18 x 17 mm grid, five columns with vertical offsets (from the outside in: 10.4,
4.2, 0, 2.2, 4.5 mm lower than the middle column), angular stepped board outlines following the
stagger, the left half with three thumb keys in an arc below the inner columns rotated 0, 10 and
20 degrees, the right half with the two inner thumb keys and a dashed circle of 28 mm inside an
notch beside them labelled "ball pocket", thin grey lines, orange highlight on the thumb
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
a Choc switch 11 mm tall, a hot-swap socket under a 1.6 mm PCB, a controller board on 2.5 mm
low-profile sockets with nothing underneath, below the PCB a flat 6 mm battery on a thin foam pad
lying in a 9 mm deep well of the printed case floor, rubber bumpers under the floor, dimension
arrows on the right with millimetre values, orange accent on the battery, sans-serif labels.
```

## img-cradle-section

Aspect 1:1. Trackball cradle cross-section.

```prompt
Technical cross-section drawing of a trackball module in a case pocket: a 19 mm ball resting on
three small 2 mm ceramic balls set in a printed cup, the cup standing on a rectangular housing that
reaches down to the case floor beside a 1.6 mm PCB (the PCB ends with a small gap next to the cup),
two long screws coming up through the floor and the sensor board into the housing, a small
sensor board with a lens inside the housing under the ball
with a dimension arrow "2.4 mm" between lens and ball surface, a second arrow "17 mm" from the PCB
top to the ball top, the ball's top a little above the keycap height, white background, thin lines,
orange accent on the dimensions, sans-serif labels.
```

## img-cradle-exploded

Aspect 4:3. Exploded view of the trackball module.

```prompt
Exploded technical rendering on white, vertically stacked with thin guide lines: a white 19 mm
ball, a beige printed cup whose rim ends just below the ball's equator on a plain rectangular housing
and three small ceramic balls shown slightly lifted out of their seats, a small green sensor board
with a black lens and a flat flex cable sliding into the housing from below, two long M2 screws
that pass the case floor and the board into the housing, a beige case floor with a rounded
rectangular pocket and two screw holes, soft studio lighting, clean.
```

## img-exploded-half

Aspect 3:4. Exploded view of the right half.

```prompt
Exploded view rendering on white of the right half of a split keyboard: from top, 17 white and
orange low-profile keycaps, 17 low-profile switches, the angular main PCB with a notch
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
Technical diagram, white background, two PCBs drawn in side view connected by a flat flex cable,
the upper board's flip-lock connector on its top face and the lower board's underneath it, the
cable climbing from the lower board and folding over the upper board's edge, its exposed contacts
marked in orange on the lower face at the top end and on the upper face at the bottom end, pin 1
marked on each connector with a triangle, labels "main PCB, key side", "sensor PCB", "type B:
contacts on opposite faces", sans-serif.
```

## img-parts-flatlay

Aspect 3:2. All parts before assembly.

```prompt
Flat lay photo on light grey paper, neatly arranged: two different bare black keyboard PCBs with
angular stepped outlines (one with a pocket notch), a tiny sensor PCB, two small wireless
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

Aspect 3:2. Controller on low-profile sockets.

```prompt
Macro photo of a small wireless controller board sitting almost flat on two rows of very low
machined socket strips above a keyboard PCB, only a 2.5 mm gap with nothing in it, USB-C port
facing the board edge, a pair of flush-cut socket pins visible on the board's other face in the
background, shallow depth of field.
```

## img-build-step-ffc

Aspect 3:2. Inserting the flex cable.

```prompt
Macro photo of fingers lifting the brown flip lock of a tiny 6-pin flat flex connector on the top
face of a keyboard PCB, right beside the notch of a trackball pocket, and sliding in a white flat
flex cable that curves up out of the pocket and folds over the board edge, a second identical
connector on a small sensor board below, bright even light.
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
Clean bar chart on white comparing estimated battery life in days for three cases: plain half
with 350 mAh, trackball half with 350 mAh in normal mode, trackball half with 350 mAh with the
sensor forced awake; bars in grey with the recommended configuration in orange, axis labels and
values, sans-serif.
```

## img-cradle-render-19-25

Aspect 2:1. Two cradle sizes.

```prompt
Rendering on white of two beige 3D printed trackball cradles side by side, the left one holding a
19 mm white ball, the right one a 25 mm white ball, both standing on the same plain rectangular
housing with a cable slot and two screw holes underneath, a small ruler for scale, soft studio
light.
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

Aspect 3:2. Battery in the bay under the controller.

```prompt
Macro photo of the underside of a keyboard PCB: a flat 350 mAh lithium polymer pouch cell, about
20 x 37 mm, stuck on a thin foam pad inside a dashed white silkscreen rectangle, its red and black
leads ending in a tiny white JST plug inserted into a low side-entry connector next to the
rectangle, a slide switch in the off position, a multimeter probe touching a nearby plated hole,
shallow depth of field.
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

## img-case-exploded

Aspect 4:3. The right half's case parts pulled apart.

```prompt
Exploded assembly drawing of the right half of a low-profile split keyboard in its printed
case, from bottom to top: a flat beige-grey tray with angular stepped walls, a deep rectangular
well under the controller end and a square pocket beside the thumb keys, a green PCB with an
octagonal notch floating above it, a small cradle module with a white 19 mm ball dropping into
the pocket from above and two long screws coming up through the floor, a flat beige roof plate
with an L-shaped skirt over the controller end, and a translucent lid with smooth plain walls
and a thin lip along the inside of its skirt hovering over everything, isometric, pastel colours, labelled parts, white background.
```

## img-case-tray-top

Aspect 3:2. Empty tray from above.

```prompt
Top-down rendering of an empty beige-grey 3D printed keyboard case tray with an angular stepped
outline, a flat key floor with five round standoffs, a deep rectangular battery well at the
inner end, a square pocket with two screw holes at the outer lower corner, smooth plain outer
walls without any tabs, a USB-C cutout and a tiny slot in the end wall, clean CAD line-art
style, white background.
```

## img-case-pocket-detail

Aspect 4:3. Cross-section through the ball pocket.

```prompt
Technical cross-section illustration of a beige-grey printed keyboard case corner holding a
trackball module beside the PCB: a 19 mm white ball in a thin blue cup, the cup standing on a
rectangular housing that reaches down into a deep square well in the case floor, two long screws
coming up through the floor into the housing, a green 1.6 mm PCB ending 1 mm from the cup with an
angular notch, the case wall around the cup stopping just below the cup rim, a flat ribbon
cable curving from the PCB underside down into the housing, dimension lines for the 11.6 mm
floor depth and the 17 mm ball height, clean CAD line-art style, white background.
```

## img-case-logo-cap

Aspect 1:2. The controller box cap seen from above, wordmark engraved.

```prompt
Straight top-down CAD render of a small rectangular 3D printed roof plate, 28 by 57 mm, matte
beige-grey, with a countersunk screw hole at each short end along one long edge. Engraved 0.6 mm
into its face is a tall narrow labyrinth wordmark: a rectangular frame with a short foot at each
end, filled with long parallel vertical strokes of even width that connect into the letters k, o,
d and e turned on their side. The grooves read as shadowed channels in the surface, not as
printed lines. Clean technical style, white background, soft even light, no reflections.
```

---

## img-case-controller-box-section

Aspect 4:3. Cross-section through the controller box.

```prompt
Technical cross-section illustration of the raised controller box of a beige-grey printed
keyboard case: a blue controller board on short sockets above a green PCB, a flat printed roof
plate sitting in a rebate of the two outer walls with a thin skirt hanging down to the PCB on
the key side, a small screw boss in the corner with a brass threaded insert, a USB-C plug
entering through an opening in the end wall, a battery cell lying in a deep well under the PCB,
dimension lines for the 5.7 mm controller top and the 8.7 mm box top, clean CAD line-art
style, white background.
```

## img-case-lid-transport

Aspect 3:2. Lid on for transport.

```prompt
Product photo of a right keyboard half in a beige-grey printed case with its matching lid
snapped on top, the lid a plain angular shell 12 mm tall following the stepped outline with a
flat roof, split front to back by a straight hinge line of short round knuckles flush with the
roof, a round 16 mm window in the roof through which the top of a matte white trackball shows
flush with the surface, smooth plain outer walls flush with the case below, no tabs or
fasteners visible, a controller box corner poking through a notch in the lid skirt, the half
lying in an open canvas bag, soft daylight.
```

## img-case-lid-foot

Aspect 3:2. Lid under the half as a foot.

```prompt
Three-quarter photo of a low-profile split keyboard half with a white 19 mm trackball standing
on its own folded lid, the beige-grey lid's outer plate lying roof-up against the flat underside
of the case under the controller half of the board, held there invisibly by magnets, its inner
plate folded down at the hinge just beyond the inner edge as a kickstand pointing inward towards
the other half, the outer edge of the case resting directly on the oak desk so the half tilts
by about 18 degrees with the inner edge raised, a second lid-less half beside it lying flat,
soft studio light.
```

## img-case-lid-folded

Aspect 3:2. The folded lid as a tenting stand under the right half, seen from the inner edge.

```prompt
Low three-quarter photo from the inner edge of a right keyboard half in a beige-grey printed
case with a matte white 19 mm trackball, tilted by about 18 degrees with the inner edge up and
standing on its own hinged lid: the lid's outer plate lies flat and roof-up against the case
underside under the controller half of the board, the hinge line sits just outside the inner
edge of the case about 38 mm above the desk, and from it the inner plate folds down and inward
at about 58 degrees as a kickstand pointing towards where the other half would stand, its thin
skirt edge on the oak desk about 34 mm from the case, the outer bottom edge of the case resting
on the desk, the free end of the outer plate floating a few millimetres above it, no magnets or
fasteners visible, soft daylight, shallow depth of field.
```

## img-case-lid-hinge

Aspect 4:3. Close-up of the hinge knuckles, the pin and the V slit.

```prompt
Macro photo of the hinge of a beige-grey 3D printed keyboard lid lying roof-up on an oak desk:
nine short round knuckles of 5 mm diameter flush with the flat roof in one straight line,
alternating between the two plates with hair-thin gaps, the end of a 2 mm bright steel rod just
entering the first knuckle from the back edge, and below the knuckle line at the skirt end a
narrow V-shaped slit between the two plates that widens towards the bottom edge, no other
hardware, soft directional light, shallow depth of field.
```
