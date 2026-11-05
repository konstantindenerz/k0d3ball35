# Trackball module: sensor board, lens and cradle

The trackball module is the one part of k0d3ball36 that is not covered by the Keyball39 heritage:
Keyball never published its sensor board or its ball holder. This document describes the sensor
daughterboard that lives in `hardware/sensor-pcb/`, the optical stack it needs, and the rules the
cradle (`hardware/trackball-cradle/`) has to follow.

## 1. Why a daughterboard

* The main PCB stays reversible: it only carries a 6-pin FPC connector, no optics.
* The sensor height is the critical dimension of the whole module. A separate board can be moved
  up and down by the cradle without touching the main PCB.
* 34 mm or a different sensor later means a new daughterboard and cradle, not a new keyboard.

## 2. Sensor board at a glance

| Item | Value |
|------|-------|
| Sensor | PixArt PMW3610DM-SUDU, 16-pin molded lead-frame DIP, 3-wire SPI, motion interrupt |
| Lens | PixArt LM18-LSI (sold together with the sensor on AliExpress, LCSC part C42442560 for the IC) |
| Supply | 3.3 V from the main PCB (controller VCC). 1.8 V core rail from an XC6206P182MR LDO on the board |
| Logic level | VDDIO = 3.3 V, so SCLK, SDIO, NCS and MOTION connect to the nRF52840 directly. No level shifter |
| Current | 0.6 mA tracking, 36 uA rest 1, 16 uA rest 2, 3 uA shutdown (datasheet, VDD 1.8 V) |
| Board | 26 x 25 mm, 1.6 mm FR4, 2 layer, 2x M2 holes on the vertical centre line 20 mm apart |
| Connector | 0.5 mm pitch, 6 contacts, bottom contact, Hirose FH12-6S-0.5SH or an LCSC clone (C2764370) |
| Optical centre | exactly between the two mounting holes (board centre). The ball axis goes through it |

The sensor body passes through a 16.96 x 8.60 mm cutout in the board (datasheet figure 5) and
protrudes 0.7 mm on the lens side. Its leads are soldered on the component side. The lens clips
onto the sensor body on the lens side. The board therefore has a clear "BALL SIDE" (silkscreen
label) and a component side; the FPC connector sits on the component side.

Image prompt: *Isometric product render of a small green PCB, 26 by 25 millimetres, with a black
rectangular optical mouse sensor and a clear plastic lens protruding from its top face, two M2 holes
on the centre line, a tiny white FPC connector on the underside, soft studio lighting, white
background, technical illustration style.*

### 2.1 Schematic

Image prompt: *Clean electronics schematic drawn in KiCad style: a 16-pin sensor block labelled
PMW3610DM-SUDU in the centre, a SOT-23 regulator XC6206 1.8 V on the left feeding VDD, decoupling
capacitors near each supply pin, a 6-pin FPC connector on the far left with pins labelled MOT, NCS,
SDIO, SCLK, GND, VCC, net labels on orthogonal wires, black lines on white.*

Parts and their purpose (also in `fab/k0d3ball36-sensor-r1-bom.csv` with LCSC numbers):

| Ref | Value | Purpose |
|-----|-------|---------|
| U1 | PMW3610DM-SUDU | sensor |
| U2 | XC6206P182MR | 1.8 V core supply from 3.3 V |
| C1 | 1 uF | regulator input |
| C2, C3, C4 | 1 uF, 3.3 uF X7R, 100 nF | 1.8 V rail, C4 right at pin 14 |
| C5 | 100 nF | VDDIO decoupling at pin 6 |
| C6 | 100 nF X7R | charge pump capacitor between CP and CN (pins 12, 13) |
| C7 | 10 nF X7R | VCSEL supply, between +VCSEL/PASS_T (pins 1, 10) and GND |
| C8, C9 | 10 uF X7R, 10 nF X7R | VCP reservoir at pin 9 |
| R1 | 10 k | NRESET pull-up to VDDIO (the reset pin is not brought out) |
| R2 | 10 k | NCS pull-up: keeps the sensor deselected while the controller boots |
| R3 | 1 k | in series with MOTION; limits the current if the FFC is inserted mirrored |
| TP1..TP7 | test points | VCC, 1V8, SCLK, SDIO, NCS, MOT, NRESET |

The datasheet asks for the CP, CN and VCP capacitors to be X7R, 6.3 V or better, and placed as
close to the pins as possible with short traces. The layout keeps them within 3 mm.

### 2.2 Connector pin order and why it is mirrored

Main PCB connector (fixed by `docs/01-design-spec.md`):

| Pin | 1 | 2 | 3 | 4 | 5 | 6 |
|-----|---|---|---|---|---|---|
| Main PCB | VCC | GND | SCLK | SDIO | NCS | MOT |
| Sensor board | MOT | NCS | SDIO | SCLK | GND | VCC |

Reasoning. A bottom-contact FPC connector has its contacts between the cable and the PCB. A
"type A" FFC has its exposed contacts on the same face at both ends. Lay the cable flat with the
contacts facing down: both ends must plug into connectors whose contacts face up, i.e. connectors
mounted on the top side of their boards, which means the two boards face each other end to end and
one connector is rotated 180 degrees relative to the other when seen from above. The conductor on
the left edge of the cable reaches pin 1 of one connector and pin 6 of the other. The same holds in
our stacked arrangement, where the sensor board hangs below the main PCB with its component side
pointing down: the cable leaves the main PCB on its top side, folds down through the ball cutout,
and enters the sensor connector from below, again with the pin order reversed. Only a twist in the
cable or a type B (opposite-side contacts) cable would make it 1:1.

```
 main PCB (component side up)         FFC, contacts down        sensor board (component side DOWN)
 ┌──────────────┐                                                ┌──────────────┐
 │   [1 2 3 4 5 6]════════════════════════╗                      │              │
 └──────────────┘                         ║ fold                 │  [6 5 4 3 2 1]│ <- connector on the
                                          ╚══════════════════════╧══════════════┘    underside
```

Cross-check: torabo-tsuki-lp uses the same connector family; its keyboard side is wired
1 GND, 2 SCLK, 3 SDIO, 4 MOTION, 5 CS, 6 VCC and its sensor module 1 3.3V, 2 CS, 3 MOTION, 4 SDIO,
5 SCLK, 6 GND, i.e. mirrored, and its author notes explicitly that a same-side FFC reverses the pin
order at the opposing connector.

Safety net: if a cable with the wrong contact side is used, VCC lands on MOTION and GND on NCS.
R3 (1 k) limits the current into the MOTION output to about 3 mA, the other swapped lines are
inputs, and the sensor's VDDIO pin only sees the controller's weak pull-up. Nothing is destroyed;
the trackball simply does not work until the cable is replaced. Test point TP6 (MOT) and TP1 (VCC)
make the check easy with a multimeter.

### 2.3 Layout

| Area | Content |
|------|---------|
| centre | sensor cutout, optical centre at the board centre, pin rows above and below |
| top row of pins (component side view) | 9 VCP, 10 +VCSEL, 11 GND, 12 CP, 13 CN, 14 VDD, 15 XYLASER, 16 -VCSEL |
| bottom row of pins | 8 MOTION, 7 NRESET, 6 VDDIO, 5 NCS, 4 NC, 3 SCLK, 2 SDIO, 1 +VCSEL (square pad) |
| top left | VCP, charge-pump and VDD capacitors |
| top right | FPC connector, cable exits over the top edge |
| bottom left | pull-ups, VDDIO capacitor, regulator with its capacitors |
| bottom right | VCSEL capacitor, series resistor, serial test points |
| both layers | GND pours, stitched with vias |

Image prompt: *Top-down photo-realistic render of a small two-layer PCB with a large rectangular
cutout in the middle, two rows of eight plated through-holes above and below the cutout, a white
0.5 mm FPC connector in the top right corner, 0603 passives along the top and bottom edges, round
test pads along the bottom edge, dark green solder mask, ENIG gold pads.*

## 3. Optical stack

Numbers from the PMW3610DM-SUDU datasheet, figure 4 (assembly drawing with LM18-LSI lens):

| Dimension | Value |
|-----------|-------|
| PCB thickness assumed by PixArt | 1.60 mm |
| lens reference plane (lens flange underside) to tracking surface, Z | 2.40 mm nominal (2.20 to 2.60 working range) |
| gap between PCB lens-side face and base plate top | 3.40 mm |
| PCB lens-side face to tracking surface | 5.80 mm |
| PCB component-side face to tracking surface | 7.40 mm |
| top of sensor body (component side) to tracking surface | 9.05 mm, so the body sticks out 1.65 mm on the component side |

For a ball the tracking surface is the ball surface directly under the optical centre. The cradle
must therefore hold the ball so that its lowest point (or the point on the optical axis, if the
sensor looks at the ball from an angle) is **5.80 mm away from the lens-side face of the sensor
PCB**, and it must provide the "base plate" that the lens flange rests on, 2.40 mm from the ball
surface. The lens locates the sensor; the PCB only has to follow.

```
                 ball (25 mm)
             ___________________
           /                     \
          |          O            |      centre 12.5 mm above the lowest point
           \_________ _ _________/
                     ^ tracking surface
                     | 2.40  lens flange rests on the cradle "base plate"
          ===========|============  lens LM18-LSI, clipped on the sensor body
                     | 3.40  air gap / lens body
    ─────────────────┴──────────────  PCB, lens-side face (BALL SIDE silkscreen)
    ////////////////////////////////  PCB 1.6 mm, sensor body passes through the cutout
    ─────────────────────────────────  component side: leads, passives, FPC connector (about 1.0 mm)
```

Image prompt: *Technical cross-section drawing: a 25 mm sphere resting on three tiny ceramic balls
inside a cup; below the sphere a short optical lens block and a thin green PCB with a chip inserted
through it; dimension lines mark 2.4 mm between lens and sphere and 5.8 mm between PCB and sphere;
monochrome line art with blue dimension text.*

### 3.1 Consequences for the cradle

* Sensor PCB lens-side face sits 5.80 mm below the ball surface at the optical axis; total module
  depth below the ball contact point is about 5.8 + 1.6 + 1.0 (connector and cable) = 8.4 mm when
  the sensor looks straight up.
* Mounting the sensor at an angle (the sensor can read the ball anywhere on its surface) moves the
  module to the side and lowers the stack under the ball. Looking at the ball from 30 to 45 degrees
  below the equator is what most low-profile designs do (torabo-tsuki-lp, Rollino). The cradle
  generator exposes the angle as a parameter; the Z distance rule stays the same along the optical
  axis.
* The two M2 holes are 20.0 mm apart on the board's long axis, symmetric to the optical centre.
  Screw bosses in the cradle must leave room for the connector (top right, 9 x 5 mm) and the
  passives (max height 1.0 mm) on the component side, and for the sensor body plus lens on the
  lens side.
* Lens footprint: PixArt only gives the sensor body (16.2 x 10.1 mm, 3.96 mm tall) and marks a
  "lens interference" zone of 2.3 mm beyond pin 1. The LM18-LSI base plate is larger than the
  body; measure the physical lens before closing the cradle pocket (see open questions). The
  footprint carries a dashed 17 x 17 mm placeholder on `Dwgs.User`.
* The PCB does not need to be square to the ball axis in the horizontal plane; the optical centre
  must be on the ball axis within about 0.5 mm, Z within the 2.2 to 2.6 mm window.

### 3.2 25 mm versus 34 mm

The optics are independent of ball diameter; the same sensor board works for a 34 mm ball with
a different cradle. What changes:

| | 25 mm | 34 mm |
|---|---|---|
| finger travel per revolution | 78.5 mm | 106.8 mm |
| counts per mm of finger travel at the same CPI | identical (the sensor measures surface travel) |
| perceived sensitivity | higher, because the fingertip covers more of the ball; start at 400 CPI and scale in ZMK | Keyball users typically run 500 to 1200 CPI |
| bearings | 3x 2.0 mm ZrO2 ceramic balls | 3x 2.0 to 2.5 mm ZrO2 |
| ball sources | Perixx PERIPRO-305, Elecom M-B25SV/RD | Perixx PERIPRO-303, Elecom M-B34 |
| Keyball 25 mm conversion reports | twitchier, more thumb travel for long moves, sensor height was the real problem | reference |

## 4. Assembly order

1. Solder all SMD parts on the component side (regulator, passives, resistors, FPC connector).
   The connector's flip lock must face away from the board edge; the cable enters from the edge.
2. From the **ball side**, push the sensor body through the cutout until it seats; the square pad
   marks pin 1. Solder the 16 leads on the component side. The sensor is rated for wave soldering;
   with an iron keep each joint short and never let flux reach the optical aperture.
3. Clean flux residue with isopropyl alcohol, keep it away from the aperture.
4. Peel the two protective Kapton films from the sensor's optical aperture and VCSEL window.
5. Clip the LM18-LSI lens onto the sensor body (its guide posts engage the body). Do not touch
   the optical surfaces; hold the lens by its flange.
6. Check with a multimeter: no short between VCC and GND, no short between 1V8 and GND.
7. Plug the FFC, power the main board, read register 0x00 (product ID 0x3E). ZMK logs the product
   ID at boot when `CONFIG_INPUT_LOG_LEVEL_DBG` is enabled; TP3/TP4/TP5 allow probing SPI with a
   logic analyser.
8. Mount the board in the cradle with two M2 screws, drop in the ball, test tracking.

Image prompt: *Hands-on macro photo of someone pressing a small black optical sensor through a cutout
in a green PCB from the back side, a pair of tweezers holding a clear plastic lens next to it, soft
workshop lighting, shallow depth of field.*

## 5. Test procedure

| Step | Expected |
|------|----------|
| VCC to GND resistance before power | more than 10 kOhm |
| 1V8 (TP2) with 3.3 V applied | 1.75 to 1.85 V |
| supply current, sensor idle (no ball) | below 1 mA |
| SPI read 0x00 | 0x3E (product ID), 0x01 inversion 0xC1 |
| MOTION (TP6) | high when idle, pulses low when the ball moves |
| ZMK | cursor moves, `res-cpi` changes take effect |

## 6. Open questions (tickets to file)

* **LM18-LSI outline** (mech, P1): the exact base plate dimensions of the lens are not in the
  public datasheet. Measure a physical lens and update the `Dwgs.User` placeholder in the footprint
  and the cradle pocket. Until then print the cradle pocket oversized.
* **FFC orientation check** (hw, P1): verify the mirrored pin order with the first physical cable
  and connectors before ordering main PCBs in quantity; the analysis is solid but cheap to confirm.
* **Sensor angle** (mech, P1): decide between straight-up (simplest, 8.4 mm under the ball) and an
  angled mount (lower profile) once the cradle prototype exists.
* **Reverse-cable safe pinout** (hw, P3): a palindromic power pinout (VCC on 1 and 6, GND on 2 and 5)
  would make the cable orientation irrelevant for power; costs two signal pins, so it needs an 8-pin
  connector. Consider for r2.
* **Board size** (hw, P3): the board is 26 x 25 mm instead of the 22 x 25 mm estimate in the design
  spec, because the sensor cutout plus one routing channel on each side needs 21 mm, and the
  connector needs clearance from the mounting hole. The design spec should be updated.
* **Connector family** (doc, P3): the design spec still names FH19SC; the project decided on
  FH12-6S-0.5SH (same pitch, same bottom-contact arrangement, larger KiCad library coverage).
