# Trackball module: sensor board, lens and cradle

The trackball module is the one part of k0d3ball35 that is not covered by the Keyball39 heritage:
Keyball never published its sensor board or its ball holder. This document describes the sensor
daughterboard that lives in `hardware/sensor-pcb/`, the optical stack it needs, the 19.05 mm
ball decision, and the rules the cradle (`hardware/trackball-cradle/`) has to follow in the r2
pocket mount.

## 1. Why a daughterboard

* The main PCB stays a plain key matrix board: it only carries a 6-pin FPC connector, no optics.
  Since r2 the module does not even pass through the PCB; it stands in a case pocket beside it.
* The sensor height is the critical dimension of the whole module. A separate board can be moved
  up and down by the cradle and the case floor without touching the main PCB.
* A 25 mm ball or a different sensor later means a new cradle and pocket, not a new keyboard.

## 2. Sensor board at a glance

| Item | Value |
|------|-------|
| Sensor | PixArt PMW3610DM-SUDU, 16-pin molded lead-frame DIP, 3-wire SPI, motion interrupt |
| Lens | PixArt LM18-LSI (sold together with the sensor on AliExpress, LCSC part C42442560 for the IC) |
| Supply | 3.3 V from the right PCB (controller VCC). 1.8 V core rail from an XC6206P182MR LDO on the board |
| Logic level | VDDIO = 3.3 V, so SCLK, SDIO, NCS and MOTION connect to the nRF52840 directly. No level shifter |
| Current | 0.6 mA tracking, 36 uA rest 1, 16 uA rest 2, 3 uA shutdown (datasheet, VDD 1.8 V) |
| Board | 26 x 25 mm, 1.6 mm FR4, 2 layer, 2x M2 holes on the vertical centre line 20 mm apart |
| Connector | 0.5 mm pitch, 6 contacts, bottom contact, Hirose FH12-6S-0.5SH or an LCSC clone (C2764370) |
| Optical centre | exactly between the two mounting holes (board centre). The ball axis goes through it |
| Position | on the case floor under the ball, centred at layout (-13, +66) of the right half, component side down |

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

Parts and their purpose (also in `fab/k0d3ball35-sensor-r1-bom.csv` with LCSC numbers):

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

### 2.2 Connector pin order, cable type and why J1 sits on the key side

Right PCB connector J1 (fixed by `docs/01-design-spec.md`):

| Pin | 1 | 2 | 3 | 4 | 5 | 6 |
|-----|---|---|---|---|---|---|
| Right PCB (J1) | VCC | GND | SCLK | SDIO | NCS | MOT |
| Sensor board | VCC | GND | SCLK | SDIO | NCS | MOT |

Reasoning. Both connectors are bottom-contact parts: the cable's exposed contacts have to face
the board the connector is soldered to. The sensor board hangs its connector under itself (the
component side faces the case floor), so there the contacts point **up**. J1 sits on the key side
of the right PCB with the cable lying on top of the board, so there they point **down**. The
cable therefore needs its contacts on opposite faces at its two ends, which is exactly a
**type B** FFC. A type A cable (same face at both ends, the usual default) does not work here:
one end would present its insulation to the contacts and simply not connect.

Since the cable is not twisted and not folded back on itself, every conductor keeps its side of
the cable from end to end, so the two connectors are wired alike: pin 1 to pin 1. The right PCB's
J1 is a front-face part, whose pad set is not mirrored, and the sensor board's is a flipped
part - the two pin-1 pads end up at the same place across the cable. `tests/test_ffc_pin_order.py`
derives this from the two board files and fails if either side is edited in isolation.

Why J1 moved to the key side in r2.2: underneath the board its lock sat in the 3 mm gap between
the PCB and the case floor, unreachable once the PCB was screwed down, and the cable had 1 mm of
horizontal run to drop 8 mm into the cradle - two creases right at the connector lip. On the key
side the cable climbs the 3 mm gap between the cradle cup and the PCB notch, folds over the board
edge with a 1.5 mm radius and goes straight into the mouth, which ends 0.5 mm short of the edge.
It is the last connection of the build and the first one to undo for service.

```
                  ball
                 (     )        FFC, contacts DOWN on top of the board
 keys             \___/     ___________
 ────────────────────────────            PCB top, J1 [1 2 3 4 5 6] mouth towards the notch
 ═══════════════════════════╗  |  ╔════════════════════════════ right PCB (1.6 mm)
                            ║  |  ║ cup
   cradle wall channel ->   ║  |  ║            the cable turns up inside the key-facing
                            ║ /   ║            wall of the cradle housing
 sensor board, component side DOWN, connector contacts UP
 ───────────────────────────────────── case floor at -11.6 mm ─────────────────────────────
```

Cross-check: torabo-tsuki-lp puts both connectors on the undersides of its two boards and uses a
type A cable, which mirrors the pin order (its keyboard side is wired 1 GND, 2 SCLK, 3 SDIO,
4 MOTION, 5 CS, 6 VCC against 1 3.3V, 2 CS, 3 MOTION, 4 SDIO, 5 SCLK, 6 GND on its module). Same
physics, one board turned the other way round.

Safety net: a type A cable, a cable put in upside down or a cable swapped end for end all end up
with the contacts facing away from the connector's own contacts at one end, so nothing connects
and nothing is powered the wrong way. R3 (1 k) in series with MOTION stays anyway: it costs
nothing and covers a cable with its contact window on the wrong face. Test points TP6 (MOT) and
TP1 (VCC) make the check easy with a multimeter.

### 2.3 Layout

| Area | Content |
|------|---------|
| centre | sensor cutout, optical centre at the board centre, pin rows above and below |
| top row of pins (component side view) | 9 VCP, 10 +VCSEL, 11 GND, 12 CP, 13 CN, 14 VDD, 15 XYLASER, 16 -VCSEL |
| bottom row of pins | 8 MOTION, 7 NRESET, 6 VDDIO, 5 NCS, 4 NC, 3 SCLK, 2 SDIO, 1 +VCSEL (square pad) |
| top left | VCP, charge-pump and VDD capacitors |
| top right | FPC connector, cable exits over the top edge (towards the keys in the pocket) |
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
must therefore hold the ball so that its lowest point is **5.80 mm away from the lens-side face of
the sensor PCB**, and it must provide the "base plate" that the lens flange rests on, 2.40 mm from
the ball surface. The lens locates the sensor; the PCB only has to follow.

```
                 ball (19.05 mm)
               _______________
             /                 \
            |         O         |      centre 9.5 mm above the lowest point, +7.6 mm above the PCB top
             \_______ _ _______/
                     ^ tracking surface
                     | 2.40  lens flange rests on the cradle "base plate"
          ===========|============  lens LM18-LSI, clipped on the sensor body
                     | 3.40  air gap / lens body
    ─────────────────┴──────────────  PCB, lens-side face (BALL SIDE silkscreen), -7.75 mm
    ////////////////////////////////  PCB 1.6 mm, sensor body passes through the cutout
    ─────────────────────────────────  component side down: leads, passives, FPC connector
    ───────────────────────────────── case floor, -11.6 mm below the main PCB top
```

Image prompt: *Technical cross-section drawing: a 19 mm sphere resting on three tiny ceramic balls
inside a cup that stands on a flat case floor beside a thin green keyboard PCB; below the sphere a
short optical lens block and a thin green sensor PCB with a chip inserted through it, lying on the
floor; dimension lines mark 2.4 mm between lens and sphere, 5.8 mm between PCB and sphere and 17 mm
from the keyboard PCB top to the top of the sphere; monochrome line art with blue dimension text.*

### 3.1 Resulting stack in the pocket mount

From `hardware/trackball-cradle/stack.json` (z = 0 is the main PCB top, floor at -11.6):

| | 19.05 mm (default) | 25 mm (fallback) |
|---|---|---|
| case floor (lowest point of the sensor board) | -11.6 mm | -11.6 mm |
| sensor PCB lens-side face | -7.75 mm | -7.75 mm |
| housing top (0.3 mm under the PCB underside) | -1.9 mm | -1.9 mm |
| ball bottom | -1.95 mm | -1.95 mm |
| ball centre | +7.6 mm | +10.6 mm |
| cup rim (1 mm below the equator, nothing above it) | +6.6 mm | +9.6 mm |
| ball top | **+17.1 mm** | +23.05 mm |
| cup outer diameter | 23.1 mm | 29.0 mm |
| largest diameter above the PCB (bearing bosses) | 24.1 mm | 29.0 mm |
| PCB notch apothem needed | 15.0 mm (r2 boards) | 16.5 mm (different PCB) |

Choc V1 caps top out at about 11 mm, so the 19 mm ball stands 6 mm proud of the keys, roughly what
the torabo-tsuki LP review describes as "keycaps and ball at the same height" with its 19 mm
option. The r1 25 mm ball stood 12 mm proud, which is why the ball size was reduced
(`issues/mech-ball-height-23mm.md`).

### 3.2 Consequences for the cradle

* Sensor PCB lens-side face sits 5.80 mm below the ball surface at the optical axis; total module
  depth below the ball contact point is 5.8 + 1.6 + 2.25 (leads, connector) = 9.65 mm with the
  sensor looking straight up. That is the floor depth of the pocket: 11.6 mm below the PCB top.
* The sensor board lies in the housing with its lens side up against the housing face and is
  clamped to two M2 posts from below. The two holes are 20.0 mm apart on the board's long axis,
  symmetric to the optical centre.
* The posts double as the case fastening: their 1.6 mm pilot holes run through to the housing
  underside and two M2 x 10 countersunk self-tapping screws come up from below through the
  case floor (2.5 mm), the 2.25 mm component gap and the board into the posts (`case_screw_sp` = 20 mm in
  `stack.json`). The housing therefore has no screw ears; its floor footprint is the bare
  29 x 29 mm box (`footprint_x` / `footprint_y`), and the case pocket below the PCB plane is a
  34 x 34 mm rounded rectangle around it (`issues/mech-case-ball-pocket.md`). The housing is 1 mm
  narrower than the notch is wide across its flats, so it clears the board edge by 0.5 mm while
  the module is lowered into the pocket.
* The FPC connector (top right, 9 x 5 mm) and the passives (max height 1.0 mm) face the floor;
  the 2.25 mm gap between board and floor is where the FFC runs out through the slot in the
  key-facing wall of the housing. From the board plane up, the same wall carries a 6 mm wide
  channel in line with that connector: the cable turns up there and climbs past the PCB plane in
  the gap between the cup and the notch (`cable_channel_x` / `cable_channel_w` in the cradle's
  `stack.json`; the tests check it against J1's position on both boards).
* The corner of the module that faces the keys and the inner column would be covered by the PCB
  if the notch were a plain octagon: the facet overhung the housing by 5.86 mm and the sensor
  board by 3.03 mm. That corner of the notch is square instead, so the whole module drops in and
  lifts out vertically with the PCB fitted (`issues/mech-cradle-notch-relief.md`).
* A tilted sensor (looking at the ball from the side, as torabo-tsuki and Rollino do) was
  evaluated in r1 and does not pay off with a 26 mm wide board: see the cradle README. The 19 mm
  ball brought the 6 mm that the tilt would have promised.
* Lens footprint: the LM18-LSI datasheet (PMS0039 R1.03, figure 1) gives a 12.90 x 8.25 mm base
  flange (the reference surface that rests on the sensor-side face of the PCB), a 10.29 x 6.55 mm
  upper body that passes the 16.96 x 8.60 mm sensor cutout, and two 0.90 mm guide posts that
  engage the sensor body, not the PCB, so the board has no lens holes. The footprint carries both
  rectangles dashed on `Dwgs.User`, centred on the optical centre; the flange clears the cradle post
  columns by 3.4 mm per side. Still to measure on a physical lens: the flange position along the pin
  row relative to the aperture, and the clip positions
  (`issues/mech-lm18-lens-outline-measurement.md`).
* The PCB does not need to be square to the ball axis in the horizontal plane; the optical centre
  must be on the ball axis within about 0.5 mm, Z within the 2.2 to 2.6 mm window.
* No retainer. The cup rim ends 1 mm below the ball equator all round and there is no claw ring,
  lip or peg above it: the ball rests on the three bearings by gravity, the thumb reaches it at
  its widest point from every side, and it lifts straight out for cleaning. In transport the
  removable case lid covers keys and ball (`issues/mech-case-lid.md`); a bare half without its
  lid should travel without the ball.

### 3.3 Why 19.05 mm, and the 25 mm fallback

Research summary (details and links in `docs/00-feasibility.md`, section 4a): torabo-tsuki LP
ships with 25 or 19.05 mm POM balls on the same PMW3610-class sensor module, LiNEA40 tracks a
19 mm ball with a PMW3610 directly on its PCB, and a seven-month review of the 19 mm torabo-tsuki
LP reports no tracking problems. PandaKB sells a 19 mm phenolic ball made for split keyboards,
and 3/4 inch POM bearing balls cost a few euros per pack. Nothing smaller than 19 mm exists as a
keyboard trackball, so 19.05 mm is the floor.

The optics are independent of ball diameter; the same sensor board works for both sizes with a
different cradle. What changes:

| | 19.05 mm | 25 mm |
|---|---|---|
| finger travel per revolution | 59.8 mm | 78.5 mm |
| counts per mm of finger travel at the same CPI | identical (the sensor measures surface travel) |
| perceived sensitivity | the fingertip covers more of the ball, so the same CPI feels about 30 percent faster per thumb movement; start at 600 CPI (r1 started at 400 for 25 mm) | 400 to 800 CPI |
| inertia and flicks | little inertia, no long flicks; precise for short moves | some inertia |
| ball top above the PCB | +17.1 mm | +23.05 mm |
| bearings | 3x 2.0 mm ZrO2 ceramic balls | 3x 2.0 mm ZrO2 |
| ball sources | 3/4 inch POM bearing balls (Amazon, AliExpress), PandaKB TB19 phenolic | Perixx PERIPRO-305, Elecom M-B25SV/RD |
| PCB | r2 boards (notch apothem 15 mm) | wider notch (16.5 mm) and a 35 mm pocket: a PCB revision, `issues/hw-25mm-cradle-fallback.md` |

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
7. Plug the type B FFC into the sensor board now (the connector is unreachable once the board is
   in the housing), connect the other end to J1, power the right half, read register 0x00
   (product ID 0x3E). ZMK logs the product ID at boot when `CONFIG_INPUT_LOG_LEVEL_DBG` is
   enabled; TP3/TP4/TP5 allow probing SPI with a logic analyser.
8. Slide the board lens-first into the cradle housing from below, cable out through the slot and
   up the channel in the key-facing wall, stand the module in the pocket and fasten board and
   module together with the two M2 x 10 countersunk case screws from below the floor (short M2 x 5 screws for
   a bench test without the case).
9. Fold the cable over the board edge into J1 on the key side, close the lock, drop in the ball
   and test tracking. For service the order reverses: open the lock, pull the cable out of J1,
   undo the two screws from below and lift the whole module out of the pocket - the PCB and the
   keycaps stay where they are.

Image prompt: *Hands-on macro photo of someone pressing a small black optical sensor through a cutout
in a green PCB from the back side, a pair of tweezers holding a clear plastic lens next to it, soft
workshop lighting, shallow depth of field.*

The case side of this is in `docs/11-case.md` section 3: the two floor holes are countersunk at
90 degrees so the flat heads sit 0.2 mm inside the underside, and the lid's lip keeps clear of J1 and of the cable
corridor on the key side of the board.

## 5. Test procedure

| Step | Expected |
|------|----------|
| VCC to GND resistance before power | more than 10 kOhm |
| 1V8 (TP2) with 3.3 V applied | 1.75 to 1.85 V |
| supply current, sensor idle (no ball) | below 1 mA |
| SPI read 0x00 | 0x3E (product ID), 0x01 inversion 0xC1 |
| MOTION (TP6) | high when idle, pulses low when the ball moves |
| ZMK | cursor moves, `res-cpi` changes take effect |

## 6. Open questions (tickets)

* **LM18-LSI outline** (mech, P1): the footprint envelope now follows the datasheet (12.90 x 8.25
  flange, 10.29 x 6.55 body). Measure a physical lens for the flange offset along the pin row and
  the clip positions, then shrink the cradle's `lens_l` / `lens_w` assembly dummy (21.5 x 11.5).
  `issues/mech-lm18-lens-outline-measurement.md`
* **FFC type and orientation check** (hw, P1): the cable must be type B (contacts on opposite
  faces at its two ends) and the pin order is straight through. Confirm both with the first
  physical cable and connectors before ordering PCBs in quantity; the analysis is solid but cheap
  to check. `issues/hw-ffc-pin-order-verification.md`
* **Ball surface** (hw, P1): POM balls vary; test two or three from the pack and the PandaKB
  phenolic ball on the sensor before choosing a colour. `issues/hw-ball-colour-tracking-test.md`
* **Reverse-cable safe pinout** (hw, P3): a palindromic power pinout (VCC on 1 and 6, GND on 2 and 5)
  would make the cable orientation irrelevant for power; costs two signal pins, so it needs an 8-pin
  connector. Consider for a later revision. Less urgent since r2.2: a wrong cable now presents
  insulation to the contacts instead of swapping power pins.
* **Cable tidiness** (mech, P3): the FFC is visible for about 5 mm in the gap between the cup and
  the pocket wall. A small printed tab on the pocket wall could cover it.
  `issues/mech-ffc-cover-tab.md`
* **Case pocket** (mech, P1): the pocket well, its floor depth and the two case-screw holes
  (20 mm apart on the y axis, under the sensor posts) come from `points-right.json` and
  `hardware/trackball-cradle/dxf/floor-19mm-pocket.dxf`.
  `issues/mech-case-ball-pocket.md`
