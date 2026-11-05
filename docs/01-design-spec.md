# k0d3ball36 design specification

Revision: r1 (draft, 2026-11-05). This document is the contract every other part of the
repository (layout, schematic, PCB, firmware, cradle, tests, docs) must agree with.
If something here changes, the change must be propagated and a ticket filed in `issues/`.

## 1. Requirements

| # | Requirement | Value |
|---|-------------|-------|
| R1 | Keys | 36 total, 18 per half: 3 rows x 5 columns + 3 thumb keys |
| R2 | Switches | Kailh Choc V1 (PG1350) in hot-swap sockets (CPG135001S30); hot-swap only, like the Keyball |
| R3 | Key pitch | 18.0 mm (x) x 17.0 mm (y) |
| R4 | Column stagger | Keyball39 proportions scaled to 17 mm row pitch (see section 5) |
| R5 | Thumb cluster | Keyball39 three-key arc, 0 / 10 / 20 degree rotation |
| R6 | Pointing | 25 mm trackball, right half by default, PMW3610 sensor on a daughterboard |
| R7 | Wireless | nRF52840 Pro Micro form factor (nice!nano v2 or SuperMini), BLE split, ZMK |
| R8 | Power | 1S LiPo per half, on-board charger of the controller, slide power switch |
| R9 | PCB | one reversible main PCB serves both halves; one sensor PCB |
| R10 | Height | low profile: nothing taller than the Choc switch above the PCB except the ball |
| R11 | Indicators | none on the PCB; controller LED visible through a case window |
| R12 | Assembly | all parts hand-solderable (SOD-123, 1.27 mm sockets, 0.5 mm FPC with care) |
| R13 | License | MIT for firmware/scripts/docs, CERN-OHL-P-2.0 for hardware |

Out of scope for r1: RGB, OLED/nice!view, rotary encoder, dongle (prepared in firmware only), case
(separate phase; only the trackball cradle module is designed now).

## 2. Controller pin map

Controller pins are named by their Pro Micro position (ZMK `&pro_micro N`). nRF52840 port pins
are given for the nice!nano v2; the SuperMini is pin compatible.

**Right half** (trackball half, split central):

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
| TB_SCLK | D15 | P1.13 | out | PMW3610 SPI clock |
| TB_SDIO | D16 | P0.10 | bidir | PMW3610 3-wire SPI data (MOSI and MISO tied) |
| TB_NCS | D10 | P0.09 | out | PMW3610 chip select, active low |
| TB_MOT | D14 | P1.11 | in, pull-up | PMW3610 motion interrupt, active low |
| spare | D0, D1 | P0.08, P0.06 | | broken out as test pads (I2C capable) |
| spare | D2, D3, D9 | P0.17, P0.20, P1.06 | | broken out as test pads |
| B+ | RAW | | | battery positive, through the power switch |
| GND | GND | | | |
| RST | RST | | | reset button to GND |
| VCC | VCC | | | 3.3 V output of the controller, feeds the sensor board |

P0.09 and P0.10 are the NFC pins; the ZMK nice!nano board definition already configures them as GPIO.
The same mapping is used by the existing community Keyball39 ZMK configs, so their tuning carries over.

**Left half** (same PCB flipped over): the controller footprint is a plain 2x12 through-hole pattern, so
flipping the board swaps the two Pro Micro pin columns. The copper is identical, the controller pins on each
matrix line are not:

| Signal | Pro Micro | nRF52840 | Direction | Note |
|--------|-----------|----------|-----------|------|
| COL0 (pinky) | D19 | P0.02 | out | |
| COL1 (ring) | D18 | P1.15 | out | |
| COL2 (middle) | D15 | P1.13 | out | |
| COL3 (index) | D14 | P1.11 | out | |
| COL4 (inner) | D16 | P0.10 | out | |
| ROW0 (top) | D2 | P0.17 | in, pull-down | |
| ROW1 (home) | D3 | P0.20 | in, pull-down | |
| ROW2 (bottom) | D4 | P0.22 | in, pull-down | |
| ROW3 (thumbs) | D5 | P0.24 | in, pull-down | |
| TB_SCLK | D6 | P1.00 | out | sensor not populated on the left in r1 |
| TB_SDIO | D8 | P1.04 | bidir | |
| TB_NCS | D9 | P1.06 | out | |
| TB_MOT | D7 | P0.11 | in, pull-up | |
| spare | D21, D20, D10 | P0.31, P0.29, P0.09 | | the test pads carry these pins on the left half |

D0 (P0.08) is tied to GND on both halves (its hole pairs with a GND pin on the other column). The RAW, RST and
VCC rows are selected with the solder jumpers described in section 4. Firmware keeps one overlay per half.

Matrix: 4 rows x 5 columns, diode direction COL2ROW (diode cathode towards the row line).
Row 3 holds the three thumb keys in columns 2, 3 and 4 (middle, index, inner).
Cells (3,0) and (3,1) are unused.

## 3. Sensor daughterboard interface (6-pin, 0.5 mm FPC)

Main PCB connector pin order (fixed):

| Pin | Signal |
|-----|--------|
| 1 | VCC 3.3 V |
| 2 | GND |
| 3 | TB_SCLK |
| 4 | TB_SDIO |
| 5 | TB_NCS |
| 6 | TB_MOT |

Connector family: Hirose FH12-6S-0.5SH (0.5 mm pitch, 6 contacts, bottom contact, ZIF slider) or a
pin-compatible LCSC equivalent; the same footprint is used on both boards. Cable: 0.5 mm pitch, 6 conductor, same-side contacts
(type A), 30 to 50 mm long. The sensor board's connector pin order is chosen so that this cable
works when both connectors sit on the top side of their boards; the sensor PCB documentation
records whether that is pin 1 to 1 or mirrored.

Sensor board (`hardware/sensor-pcb/`): PMW3610DM-SUDU, LM18-LSI lens, VDD 1.8 V generated on the board from
3.3 V, VDDIO 3.3 V, 100 nF plus 1 uF decoupling, no level shifting. Outline 26 x 25 mm (17 mm sensor body cutout
plus a routing channel on each side), two M2 holes 20 mm apart on the vertical 25 mm axis with the optical centre
exactly between them at the board centre; the lens runs along the 26 mm side. Component side is the top (FPC
connector, passives); the back carries the "BALL SIDE" silkscreen, the sensor body (protrudes 0.7 mm) and the lens.

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
| plain | 301230, 110 mAh, protected | under the socketed controller | weeks |
| trackball (central) | 702025, 300 mAh, protected | case pocket next to controller | 3 to 6 weeks mixed use |

Both halves have the same PCB: solder pads J2 for bare battery leads (2.54 mm pitch, B+ is the square pad)
as the default, an optional JST-PH 2.0 connector J3 (S2B-PH-SM4-TB, 6 mm tall, only if the case allows it),
MSK-12C02 slide switch PS1 in the B+ line, reset button RB1 on RST, controller on 1.27 mm mill-max or
"conthrough" sockets so that a 3.3 mm cell fits underneath.

Controller power rows on a flipped board: the first four Pro Micro rows pair D1/RAW, D0/GND, GND/RST and
GND/VCC. Three 3-pad solder jumpers next to the controller select the right hole per half:

| Jumper | Net on pad 2 | Right half | Left half |
|--------|--------------|------------|-----------|
| JP1 | RAW (battery via switch) | bridge 2-3 | bridge 1-2 |
| JP2 | RST (reset button) | bridge 2-3 | bridge 1-2 |
| JP3 | VCC (3.3 V to the sensor) | bridge 2-3 | bridge 1-2 |

The D0/GND row needs no jumper: both holes are tied to GND, which sacrifices D0 on both halves.
Sensor supply is the controller's VCC (3.3 V, up to 500 mA available); the PMW3610 draws 0.6 mA when
tracking and 36 uA in rest.

## 5. Geometry (single source: `hardware/layout/k0d3ball36.yaml`)

Coordinates are in mm, right half, x grows outward (towards the pinky), y grows downward
(towards the user). Origin is the centre of the middle-column top key. Pitch 18 x 17.

Column stagger (y offset of a column relative to the middle column; Keyball39 values 11.70 / 4.70 /
0 / 2.50 / 5.00 mm at 19.05 pitch, scaled by 17 / 19.05):

| Column | Matrix col | x | y offset |
|--------|------------|---|----------|
| pinky | 0 | +36 | +10.44 |
| ring | 1 | +18 | +4.19 |
| middle | 2 | 0 | 0 |
| index | 3 | -18 | +2.23 |
| inner | 4 | -36 | +4.46 |

Thumb arc (Keyball39 positions scaled by 18 / 19.05 in x and 17 / 19.05 in y, 20.4 mm between neighbouring thumb centres, rotations kept):

| Key | Matrix cell | approx. x | approx. y | rotation |
|-----|-------------|-----------|-----------|----------|
| thumb outer | (3,2) | -22 | +58.5 | 0 deg |
| thumb middle | (3,3) | -41 | +60.5 | 10 deg |
| thumb inner | (3,4) | -59.5 | +65.5 | 20 deg |

Exact values come out of the layout generator and are tabulated in `docs/02-layout.md`.

Ball zone: centre near (+12, +64), i.e. below the middle/ring columns, outboard of the outer thumb.
PCB cutout diameter 30 mm for the cradle, three M2 holes on a 36 mm circle for the cradle flange.
The cutout and holes exist on both halves (reversible PCB); the left half leaves them unused.
Minimum clearance between the cradle outline (diameter 34 mm) and any keycap: 1.0 mm. The PCB outline
ring around the ball zone is cradle radius 17 mm plus a 3.5 mm margin, so the three flange holes on the 36 mm
circle keep 0.3 mm of material to the edge.

Controller: at the inner edge, USB connector towards the top edge, component side up, long axis
parallel to the columns. FPC connector between controller and ball zone.

Mounting holes: six M2 (2.2 mm) non-plated holes per half for the later case, placed in the gaps between
switch bodies and outside the hot-swap socket pad bands (from `hardware/layout/k0d3ball36.yaml`):

| Hole | x | y | Location |
|------|---|---|----------|
| H1 | +27.0 | +10.8 | ring / pinky, top |
| H2 | +27.0 | +44.5 | ring / pinky, bottom |
| H3 | -9.0 | +40.0 | middle / index, bottom |
| H4 | -27.0 | +8.0 | index / inner, top |
| H5 | -32.0 | +61.0 | between outer and middle thumb key |
| H6 | -67.0 | +45.0 | controller block, bottom inner corner |

Plus the three cradle flange holes HB1..HB3 on the 36 mm circle. Twelve GND stitching vias tie the two
ground pours together, and a 0.45 mm wide track/via keep-out ring runs along the board edge and the cutout
so the autorouter keeps the 0.3 mm copper-to-edge clearance.

## 6. Firmware contract

ZMK `main` (Zephyr 4.1 based), shield name `k0d3ball36`, builds `k0d3ball36_left` and
`k0d3ball36_right` for `nice_nano//zmk` plus `settings_reset`. The right half is the split central and
carries the sensor (`pixart,pmw3610`, `res-cpi` 400 default). `zmk,input-split` is scaffolded so that a
left-ball or dongle build is a configuration change. ZMK Studio enabled.

Layers: 0 base, 1 nav, 2 num, 3 sym, 4 mouse (auto mouse layer), 5 scroll, 6 snipe, 7 system (BT, reset, Studio unlock).

## 7. Ticket convention

Features, bugs and open questions live in `issues/` as one markdown file each,
named `<area>-<slug>.md` (areas: hw, fw, mech, doc, test, infra). Frontmatter fields:
`title`, `type` (feature | bug | question | task), `priority` (P0 blocker, P1 must, P2 should, P3 nice),
`status` (open | in-progress | done | wontfix), `area`, `created`. `scripts/issues.py` renders `issues/README.md`.
