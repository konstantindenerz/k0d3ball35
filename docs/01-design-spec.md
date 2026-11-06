# k0d3ball35 design specification

Revision: r2 (2026-11-06). This document is the contract every other part of the
repository (layout, schematic, PCB, firmware, cradle, tests, docs) must agree with.
If something here changes, the change must be propagated and a ticket filed in `issues/`.

What changed from r1: two separate PCBs instead of one reversible board, 35 keys (the right
half loses its inner thumb key), a stepped angular outline without rounding, and a 19.05 mm
ball in a case pocket beside the right PCB instead of a 25 mm ball through a PCB cutout. The
solder jumpers, the mirrored left-half pin map and the grounded D0 are gone with the reversible
board. Ticket `hw-two-pcbs-r2`.

## 1. Requirements

| # | Requirement | Value |
|---|-------------|-------|
| R1 | Keys | 35 total: left 15 finger + 3 thumb = 18, right 15 finger + 2 thumb = 17 |
| R2 | Switches | Kailh Choc V1 (PG1350) in hot-swap sockets (CPG135001S30); hot-swap only, like the Keyball |
| R3 | Key pitch | 18.0 mm (x) x 17.0 mm (y) |
| R4 | Column stagger | Keyball39 proportions scaled to 17 mm row pitch (see section 5) |
| R5 | Thumb cluster | Keyball39 three-key arc, 0 / 10 / 20 degree rotation; the right half uses the two outer keys (0 and 10 degrees) |
| R6 | Pointing | 19.05 mm (3/4 inch) POM trackball on the right half in a case pocket beside the PCB, PMW3610 sensor on a daughterboard on the case floor; 25 mm stays a cradle parameter |
| R7 | Wireless | nRF52840 Pro Micro form factor (nice!nano v2 or SuperMini), BLE split, ZMK |
| R8 | Power | 1S LiPo per half, on-board charger of the controller, slide power switch |
| R9 | PCB | two main PCBs (`k0d3ball35-left`, `k0d3ball35-right`) with identical controller wiring; one sensor PCB |
| R10 | Height | low profile: nothing taller than the Choc switch above the PCB except the ball; ball top about 17 mm above the PCB top |
| R11 | Indicators | none on the PCB; controller LED visible through a case window |
| R12 | Assembly | all parts hand-solderable (SOD-123, low-profile controller sockets, 0.5 mm FPC with care) |
| R13 | Outline | angular: 90 degree steps following the column stagger, no corner rounding, rectangular controller block at the inner edge |
| R14 | License | MIT for firmware/scripts/docs, CERN-OHL-P-2.0 for hardware |

Out of scope for r2: RGB, OLED/nice!view, rotary encoder, dongle (prepared in firmware only), case
(separate phase; the trackball cradle and the pocket geometry are specified now).

## 2. Controller pin map

Controller pins are named by their Pro Micro position (ZMK `&pro_micro N`). nRF52840 port pins
are given for the nice!nano v2; the SuperMini is pin compatible. **The same table is valid for
both halves**: since r2 each half is its own PCB and the controller footprint is wired the same
way on both. The left half simply leaves the four sensor pins unconnected (they end on test pads).

| Signal | Pro Micro | nRF52840 | Direction | Note |
|--------|-----------|----------|-----------|------|
| COL0 (pinky) | D4 | P0.22 | out | matrix column, outermost |
| COL1 (ring) | D5 | P0.24 | out | |
| COL2 (middle) | D6 | P1.00 | out | |
| COL3 (index) | D7 | P0.11 | out | |
| COL4 (inner) | D8 | P1.04 | out | innermost finger column |
| ROW0 (top) | D21 | P0.31 | in, pull-down | |
| ROW1 (home) | D20 | P0.29 | in, pull-down | |
| ROW2 (bottom) | D19 | P0.02 | in, pull-down | |
| ROW3 (thumbs) | D18 | P1.15 | in, pull-down | |
| TB_SCLK | D15 | P1.13 | out | PMW3610 SPI clock (right half; test pad on the left) |
| TB_SDIO | D16 | P0.10 | bidir | PMW3610 3-wire SPI data, MOSI and MISO tied (right; test pad on the left) |
| TB_NCS | D10 | P0.09 | out | PMW3610 chip select, active low (right; test pad on the left) |
| TB_MOT | D14 | P1.11 | in, pull-up | PMW3610 motion interrupt, active low (right; test pad on the left) |
| spare | D0, D1 | P0.08, P0.06 | | test pads on both halves (I2C capable) |
| spare | D2, D3, D9 | P0.17, P0.20, P1.06 | | test pads on both halves |
| B+ | RAW | | | battery positive, through the power switch |
| GND | GND | | | |
| RST | RST | | | reset button to GND |
| VCC | VCC | | | 3.3 V output of the controller, feeds the sensor board (right) |

P0.09 and P0.10 are the NFC pins; the ZMK nice!nano board definition already configures them as GPIO.
The same mapping is used by the existing community Keyball39 ZMK configs, so their tuning carries over.

Test pads: a row of 1.5 mm pads at the bottom of the controller block (start (-66, +57.5),
2.5 mm pitch along x). Right half: D0, D1, D2, D3, D9. Left half: the same five plus D10, D14,
D15 and D16 (the sensor pins that have no connector on the left). All are bare copper; no
jumpers exist on either board.

Matrix: 4 rows x 5 columns, diode direction COL2ROW (diode cathode towards the row line).
Row 3 holds the thumb keys: left `(3,2)` outer, `(3,3)` middle, `(3,4)` inner; right `(3,2)`
outer and `(3,3)` middle. Cells `(3,0)` and `(3,1)` do not exist on either half, `(3,4)` does
not exist on the right. Firmware keeps one overlay per half for the matrix transform and the
sensor; the kscan pin set is shared.

## 3. Sensor daughterboard interface (6-pin, 0.5 mm FPC, right half only)

Right PCB connector J1 pin order (fixed):

| Pin | Signal |
|-----|--------|
| 1 | VCC 3.3 V |
| 2 | GND |
| 3 | TB_SCLK |
| 4 | TB_SDIO |
| 5 | TB_NCS |
| 6 | TB_MOT |

J1 sits on the bottom side of the right PCB at (0.0, +45.5) under the middle column's bottom key,
1 mm above the cradle housing; the cable exits towards +y (towards the user) and drops straight
into the slot of the cradle housing.
The left PCB has no J1 and no sensor nets.

Connector family: Hirose FH12-6S-0.5SH (0.5 mm pitch, 6 contacts, bottom contact, ZIF slider) or a
pin-compatible LCSC equivalent; the same footprint is used on both boards. Cable: 0.5 mm pitch, 6 conductor, same-side contacts
(type A), 30 to 50 mm long. The sensor board's connector pin order is chosen so that this cable
works when both connectors sit on the component side of their boards.

Sensor board (`hardware/sensor-pcb/`): PMW3610DM-SUDU, LM18-LSI lens, VDD 1.8 V generated on the board from
3.3 V, VDDIO 3.3 V, 100 nF plus 1 uF decoupling, no level shifting. Outline 26 x 25 mm (17 mm sensor body cutout
plus a routing channel on each side), two M2 holes 20 mm apart on the vertical 25 mm axis with the optical centre
exactly between them at the board centre; the lens runs along the 26 mm side. Component side is the top (FPC
connector, passives); the back carries the "BALL SIDE" silkscreen, the sensor body (protrudes 0.7 mm) and the lens.
In the pocket mount the board lies on the case floor with the component side down and the lens looking up.

Sensor-board connector pin order is MIRRORED relative to the main board: 1 TB_MOT, 2 TB_NCS, 3 TB_SDIO, 4 TB_SCLK,
5 GND, 6 VCC. Both FH12-6S connectors are bottom contact on the component sides of their boards and a type A
same-side FFC reverses the order between them. R3 (1 k in series with MOTION) and R2 (NCS pull-up) make a
wrongly inserted cable non-destructive.

Optical stack (datasheet lens-to-surface 2.2 to 2.6 mm, 2.4 mm typical):

| From the ball surface to | Distance |
|--------------------------|----------|
| lens flange | 2.40 mm |
| PCB face on the lens side | 5.80 mm |
| PCB face on the component side | 7.40 mm |
| top of the tallest component (FPC connector) | 9.05 mm |

## 4. Power

| Half | Battery | Position | Expected runtime |
|------|---------|----------|------------------|
| left (peripheral) | PKCELL LP552035, 350 mAh, protected, JST-PH | battery bay under the PCB, below the controller | two to three months |
| right (central, trackball) | PKCELL LP552035, 350 mAh, protected, JST-PH | battery bay under the PCB, below the controller | 4 to 7 weeks mixed use |

Both halves mount the cell the same way (decided 2026-11-06, `issues/hw-battery-bay-both-halves.md`):
the cell lies **under the PCB**, directly below the controller, in a well of the case floor. The
back of the PCB carries nothing there except the socket tails, so the "battery bay" is the same
rectangle on both boards and is printed on the back silkscreen:

| Item | Value |
|------|-------|
| Bay (back of the PCB, layout frame) | centre (-53.9, +17.5), 21 x 41 mm, i.e. x -64.4 to -43.4, y -3 to +38 (`battery.bay` in the layout yaml); it starts between the two controller hole rows and ends above the reset button |
| Cell | PKCELL LP552035, 350 mAh, 5.7 x 20 x 37 mm maximum including the protection circuit, JST-PH plug (Eckstein, Germany); lead end towards +y |
| Well depth | 9.0 mm below the PCB underside (socket tails 1.0 + 0.5 mm foam pad + up to 7.2 mm cell + 0.3 mm), floor at z = -10.6 mm; the case may use -11.6 mm to share the ball pocket's floor level |
| Clearances | bay 1.75 mm from the top PCB edge, 0.37 mm from the left controller hole pads, 1.25 mm from the reset button, 2.6 mm from the inner column's hot-swap sockets; checked by the layout generator against every back-side part |
| Alternatives | any cell up to 20.5 x 37.5 x 7.2 mm: 702025 / 602025 (20 x 25), 502030 / 602030 (20 x 30), 552035; the old 301230 (12 x 32 mm) would fit too but is not stocked with a plug |

Because nothing lies between the controller and the PCB any more, the controller sits on the
lowest sockets available (Mill-Max 315 with 3320 pins or conthrough, 2.5 mm design value): the
controller top is at about +5.7 mm above the PCB (2.5 mm socket + 1.6 mm nice!nano PCB + 1.6 mm
USB-C shell above it), 3.5 mm below the keycap tops. A raised controller box on the case is now
a styling choice, not a necessity.

Both PCBs carry the same power parts in the controller block: JST-PH 2.0 connector J3
(S2B-PH-SM4-TB, 6 mm tall, at (-56, +44), below the bay in the same well) as the default connection for
the cell's plug, solder pads J2 for bare battery leads (2.54 mm pitch, B+ is the square pad, at
(-57, +50.5)) as the alternative, MSK-12C02 slide switch PS1 in the B+ line at (-68.5, +30) with
the actuator through the inner edge, reset button RB1 on RST at (-66, +41) below the bay.

RAW, GND, RST and VCC connect straight to their controller holes on both boards. There are no
solder jumpers and no sacrificed pins: D0 is a free test pad. Sensor supply on the right half is
the controller's VCC (3.3 V, up to 500 mA available); the PMW3610 draws 0.6 mA when tracking and
36 uA in rest.

## 5. Geometry (single source: `hardware/layout/k0d3ball35.yaml`)

Coordinates are in mm in a half's own frame: x grows outward (towards the pinky), y grows downward
(towards the user). Origin is the centre of the middle-column top key. Pitch 18 x 17. Both halves
share the frame, which is handedness-neutral: it describes the right half seen from the top and the
left half seen through the board. Every physical artefact of the left half (PCB, case, lid) is the
mirror image of the frame (x -> -x, `Layout.to_board` in `scripts/k0d3/geometry.py`): on the left
BOARD seen from the top the controller block, the power switch and the test pads sit at +x, the
right-hand edge, and the pinky column at the left. Footprints are not mirrored (the parts are
chiral), only their rotation changes sign. The yaml, `points-*.json`, `outline-*.dxf` and the tables
below stay in frame coordinates. Everything that is not listed under `halves:` in the yaml is
identical on both boards.

Column stagger (y offset of a column relative to the middle column; Keyball39 values 11.70 / 4.70 /
0 / 2.50 / 5.00 mm at 19.05 pitch, scaled by 17 / 19.05):

| Column | Matrix col | x | y offset |
|--------|------------|---|----------|
| pinky | 0 | +36 | +10.44 |
| ring | 1 | +18 | +4.19 |
| middle | 2 | 0 | 0 |
| index | 3 | -18 | +2.23 |
| inner | 4 | -36 | +4.46 |

Thumb arc (Keyball39 positions scaled by 18 / 19.05 in x and 17 / 19.05 in y, 20.4 mm between
neighbouring thumb centres, rotations kept). The keys sit at the same positions on both halves;
the right half omits the inner one:

| Key | Matrix cell | x | y | rotation | left | right |
|-----|-------------|---|---|----------|------|-------|
| thumb outer | (3,2) | -21.78 | +59.65 | 0 deg | yes | yes |
| thumb middle | (3,3) | -42.14 | +61.26 | 10 deg | yes | yes |
| thumb inner | (3,4) | -61.91 | +66.19 | 20 deg | yes | no |

Exact values come out of the layout generator and are tabulated in `docs/02-layout.md`.

Ball pocket (right half only): ball centre (+5.0, +64.0), outboard of the outer thumb key and
below the middle/ring columns. The ball does not pass through the PCB. The PCB edge has a regular
octagonal notch with apothem 15.0 mm around the ball centre (cradle clearance radius 14 mm plus
1.0 mm), the case pocket around the cradle is a 32 mm circle (28 mm cradle clearance plus a 2 mm
wall), and the 26 x 25 mm sensor board lies centred under the ball on the case floor, 11.6 mm below
the PCB top. The cradle is screwed to the case floor, not to the PCB; there are no cradle holes on
the PCB. Minimum clearance between the 28 mm cradle circle and any keycap: 1.0 mm (checked by the
generator). Ball top about 17.1 mm above the PCB top (`hardware/trackball-cradle/stack.json`).

Controller block: a rectangle at the inner edge from above the controller down to the thumb
cluster. Controller hole-pattern centre (-58, +11.7), USB connector towards the top edge, component side up, long
axis parallel to the columns, the USB-C shell 1.5 mm past the PCB edge (the controller board
overhangs the edge by 0.9 mm, the block's top edge is derived from that). Power switch, reset button, battery pads, JST
and the test-pad row live in this block; the battery bay (21 x 41 mm, section 4) sits on the back
under the controller. A "thumb bridge" fills the slot between the index/inner bottom keys and the
thumb keys.

Outline: the union of the keycap rectangles (0.5 mm margin plus 1.1 mm per side for the hot-swap
socket pads), 90 degree steps between neighbouring columns, the controller block and the thumb
bridge, closed with mitre joins (corner radius 0; the fab's 1 mm router radius is accepted). The
right half additionally subtracts the pocket notch. Sizes: left 121.0 x 86.7 mm, right 117.8 x 80.4 mm.

Mounting holes: five M2 (2.2 mm) non-plated holes per half for the case, placed in the gaps between
switch bodies and outside the hot-swap socket pad bands, identical on both boards:

| Hole | x | y | Location |
|------|---|---|----------|
| H1 | +27.0 | +10.8 | ring / pinky, top |
| H2 | +27.0 | +44.5 | ring / pinky, bottom |
| H3 | -9.0 | +40.0 | middle / index, bottom |
| H4 | -27.0 | +8.0 | index / inner, top |
| H5 | -32.0 | +61.0 | between outer and middle thumb key |

Ten GND stitching vias per half (nine shared positions plus one per half) tie the two ground pours
together, and a 0.45 mm wide track/via keep-out ring runs along the board edge so the autorouter
keeps the 0.3 mm copper-to-edge clearance.

## 6. Firmware contract

ZMK `main` (Zephyr 4.1 based), shield name `k0d3ball35`, builds `k0d3ball35_left` and
`k0d3ball35_right` for `nice_nano//zmk` plus `settings_reset`. One shared kscan with the pin set
of section 2; the matrix transform is 4 rows x 10 columns with 35 positions, row 3 mapping
`RC(3,2) RC(3,3) RC(3,4)` on the left and `RC(3,8) RC(3,7)` on the right (right thumb middle is
matrix column 3, thumb outer column 2). The right half is the split central and carries the sensor
(`pixart,pmw3610`, `res-cpi` 600 default for the 19 mm ball). `zmk,input-split` is scaffolded so
that a left-ball or dongle build is a configuration change. ZMK Studio enabled; the physical layout
is generated from `points-left.json` and `points-right.json`.

Layers: 0 base, 1 nav, 2 num, 3 sym, 4 mouse (auto mouse layer), 5 scroll, 6 snipe, 7 system (BT, reset, Studio unlock).

## 7. Ticket convention

Features, bugs and open questions live in `issues/` as one markdown file each,
named `<area>-<slug>.md` (areas: hw, fw, mech, doc, test, infra). Frontmatter fields:
`title`, `type` (feature | bug | question | task), `priority` (P0 blocker, P1 must, P2 should, P3 nice),
`status` (open | in-progress | done | wontfix), `area`, `created`. `scripts/issues.py` renders `issues/README.md`.
