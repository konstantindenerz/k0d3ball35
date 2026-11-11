# Trackball module: sensor, cradle and ball

The trackball module is the one part of k0d3ball35 that is not covered by the Keyball39 heritage.
Since r2.4 it is a bought PAW3222 sensor module, tilted 65 degrees beside a 19.05 mm ball in a
printed cradle (`hardware/trackball-cradle/`). The cradle stands on the case floor in a pocket
beside the right PCB and is connected to the PCB only by a 6-pin flat cable.

## 1. Sensor module

| Item | Value |
|------|-------|
| Module | PixArt PAW3222 sensor with its lens on a 14 x 8 mm board, the module torabo-tsuki LP uses (sekigon-gonnoc / nogikes-ya design) |
| Source | beekeeb (ships worldwide, free shipping from 80 USD) or BOOTH; see `spec/03-bom.md` |
| Supply | 3.3 V from the controller's VCC on the right PCB |
| Interface | 3-wire SPI plus motion interrupt, 6-pin 0.5 mm FPC connector on the back of the module |
| Pinout | 1 3.3V, 2 CS, 3 MOTION, 4 SDIO, 5 SCLK, 6 GND |
| Driver | `sekigon-gonnoc/zmk-driver-paw3222` (firmware port open, `issues/hw-paw3222-variant.md`) |

The PAW3222 draws roughly half the tracking current of the PMW3610 the project used before. The
module's mechanical values (lens distance, lens body, board thickness) are nominal: PixArt
publishes no assembly drawing for the PAW3222 and its lens. The ball height does not depend on
them (section 3); they only decide whether the module fits its sleeve, which the test print
checks.

Why this module: tilted, one edge of a sensor board swings down and the other swings up, and the
upper edge has to stay under the cup rim. What limits the tilt is the board's width in the tilt
plane. The old PMW3610 board could not get narrower than about 13 mm there (the sensor sits in a
16.96 x 8.60 mm cutout), so its best legal angle was 38 degrees, worth 0.06 mm of ball height.
The 8 mm module allows 65 degrees.

## 2. Connector and cable

Right PCB connector J1: Hirose FH12-6S-0.5SH (or the pin-compatible LCSC part), bottom contact,
on the **key side** of the right PCB at (-20.6, +47). Its pin order follows the module, pin for
pin:

| Pin | 1 | 2 | 3 | 4 | 5 | 6 |
|-----|---|---|---|---|---|---|
| Right PCB (J1) | VCC 3.3 V | TB_NCS | TB_MOT | TB_SDIO | TB_SCLK | GND |
| Module | 3.3V | CS | MOTION | SDIO | SCLK | GND |

Cable: 6 conductors, 0.5 mm pitch, 30 to 40 mm, **opposite-side contacts (type B)**. J1 looks at
the cable from below (the cable lies on top of the board), the module's connector from the other
face, so a type B cable joins pin 1 to pin 1. A type A cable presents insulation to one connector
and connects nothing. `tests/test_ffc_pin_order.py` derives this; the first physical cable gets a
continuity check (`issues/hw-ffc-pin-order-verification.md`).

Cable route: the FFC leaves the sleeve below the PCB, climbs past the PCB plane in the 3.45 mm gap
between the cup (24.1 mm envelope) and the PCB notch (apothem 15.5 mm), runs round the cup above
the PCB and folds over the board edge into J1. The lock stays reachable with the keyboard
assembled, so the module can be unplugged and lifted out without touching the PCB.

## 3. Geometry and heights

The ball rests on three 2.0 mm ceramic balls in an open cup. The module sits in a sleeve beside
the cup, tilted 65 degrees from vertical (`sensor_angle`) and leaning away from the keys
(`sensor_az` = 270 in the layout frame); it looks at the ball through a 4 mm window 25 degrees
below the equator. Nominal lens distance 2.4 mm (window 2.2 to 2.6, aim for 2.3 to 2.5).

The cup floor sets the ball height (`drop_cup` 11.53 mm against `drop_board` 10.65 mm for the
module), so the unmeasured module values cannot raise the ball. `tests/test_cradle.py` asserts it.

Heights from `hardware/trackball-cradle/stack.json` and `hardware/case/stack.json`, z = 0 is the
main PCB top:

| | z | over the desk |
|---|---|---|
| desk (1 mm rubber feet in 0.8 mm recesses) | -9.8 | 0 |
| case underside | -9.6 | 0.2 |
| battery well floor | -7.6 | |
| pocket floor, cradle base | -7.1 | |
| ball bottom | -5.1 | |
| PCB | -1.6 to 0 | |
| cup rim (1 mm below the equator) | +3.4 | |
| ball centre | +4.4 | |
| keycap top | +11.0 | **20.8** |
| ball top | +13.95 | **23.75** (2.95 above the caps) |
| lid top, transport | +17.5 | **27.3** |

r2.3 for comparison: keycaps 25.6, ball 31.7, transport 31.7 mm over the desk.

Floor footprint (`dxf/floor-19mm-pocket.dxf`): the cup skirt plus the tilted sleeve where the floor
clips it, 24.05 x 26.84 mm including 0.5 mm clearance, extending further on the side away from
the keys. The case well around it is 25 x 30 mm. Two M2 x 10 countersunk self-tapping screws come
up through the case floor into the cup skirt, 20 mm apart on the y axis; the module itself has no
holes. Above the PCB plane nothing is wider than 24.1 mm, and the notch corner towards the keys is
square, so the whole module drops into the pocket and lifts out with the PCB fitted.

Retention: the cup has nothing above its rim, the ball lifts straight out. An optional clip-on
retainer keeps the ball in when the half is turned over (`issues/mech-ball-retainer-clip.md`);
otherwise the case lid covers it in transport.

## 4. Why 19.05 mm

19.05 mm (3/4 inch) is the smallest ball with a working keyboard precedent: torabo-tsuki LP ships
it, LiNEA40 tracks it, and 3/4 inch POM bearing balls cost a few euros per pack. Details in
`spec/00-feasibility.md`, section 4a. It is the only supported size; the 25 mm variant was dropped
in r2.4. The fingertip covers more of a small ball, so the same CPI feels faster: start at 600 CPI.

## 5. Assembly

The steps are in `spec/04-build-guide.md`, chapter 10, and `hardware/trackball-cradle/README.md`.
In short: bearings into the cup, module into the sleeve with the cable plugged in, cradle into the
pocket, two screws from below, cable into J1, ball in. For service reverse the order; keycaps and
PCB stay where they are.

## 6. Test

| Step | Expected |
|------|----------|
| VCC to GND resistance at J1 before power | more than 10 kOhm |
| module current, ball still | below 1 mA |
| ZMK log at boot | sensor found, no SPI errors |
| MOTION | high when idle, pulses low when the ball moves |
| cursor | moves in both axes; the 65 degree tilt scales X and Y differently, which the firmware corrects (`issues/fw-cpi-tuning-19mm.md`) |

## 7. Open points (tickets)

* First print of the 65 degree mount, lens distance with a feeler gauge, and the two tight
  values: sleeve top 0.11 mm under the cup rim, module 14.76 mm radial against the 15.5 mm notch
  (`issues/mech-ball-height-23mm.md`).
* Firmware: PAW3222 driver and the axis scaling for the tilt (`issues/hw-paw3222-variant.md`).
* FFC pin order on the first physical cable (`issues/hw-ffc-pin-order-verification.md`).
* Ball surface: test two or three balls before choosing one (`issues/hw-ball-colour-tracking-test.md`).
* Case pocket (`issues/mech-case-ball-pocket.md`).
