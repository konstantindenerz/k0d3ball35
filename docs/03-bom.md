# Bill of materials

One complete keyboard: two halves, one trackball on the right half. Prices are EU retail including
VAT as of late 2025 and will drift; links point to the shop category or product page. LCSC part
numbers are given where the part can be ordered together with the PCBs.

Quantities marked "+n" include recommended spares. Sensor-board passives are 0603.

![All parts laid out before assembly](images/img-parts-flatlay.png)

## 1. Printed circuit boards

| Qty | Part | Spec | Source | Price | Notes |
|-----|------|------|--------|-------|-------|
| 2 (min. order 5) | Main PCB `k0d3ball36-main` | 2 layer, 1.6 mm FR4, 1 oz, ENIG, about 118 x 92 mm | JLCPCB, gerbers in `hardware/main-pcb/gerbers/` | 15 to 25 EUR per 5 | Reversible: the same board is the left and the right half |
| 1 (min. order 5) | Sensor PCB `k0d3ball36-sensor` | 2 layer, 1.6 mm, ENIG, 22 x 25 mm | JLCPCB, gerbers in `hardware/sensor-pcb/gerbers/` | 2 to 5 EUR per 5 | Order in the same cart to share shipping |
| | Shipping and import VAT | | | 20 to 40 EUR | |

## 2. Controllers and sockets

| Qty | Part | Spec | Source | Price | Alt source | Notes |
|-----|------|------|--------|-------|------------|-------|
| 2 | nice!nano v2 | nRF52840, Pro Micro pinout, LiPo charger, battery ADC | https://42keebs.eu/shop/parts/controllers/nice-nano-v2-wireless-controller/ | 20.70 EUR each | https://splitkb.com/products/nice-nano (25.94 EUR), https://keycapsss.com (Puchi-BLE, 27.90 EUR) | |
| 2 | SuperMini nRF52840 (alternative) | nice!nano clone, same pinout | https://mechboards.co.uk/products/supermini-nrf52840-ble-pro-micro | about 10 EUR each | AliExpress | Cheaper, slightly higher sleep current reported by some users |
| 4 | Socket strip 1 x 12, 1.27 mm... see note | Mill-Max 310-style or "conthrough" press-fit 2.54 mm, 12 pins | https://42keebs.eu/shop/parts/ (headers and sockets) | 1 to 2 EUR each | https://keycapsss.com, AliExpress | Standard 2.54 mm pitch along the row; the socket height must leave 3.5 mm under the controller for the 301230 cell. Low-profile Mill-Max 315 sockets plus 7305 pins or conthrough pins both work. |
| 48 | Socket pins | Mill-Max 3320 or diode-leg style | with the sockets | | | Only needed with machined sockets |

## 3. Switches and keycaps

| Qty | Part | Spec | Source | Price | Alt source | Notes |
|-----|------|------|--------|-------|------------|-------|
| 36 (+2) | Kailh Choc V1 switch | CPG1350, any stem; Silent Linear, Pro Red or Sunset recommended | https://keycapsss.com/Kailh-Low-Profile-Choc-Switches-V1/KC10034-SI | 6.90 to 7.90 EUR per 10 | https://42keebs.eu, https://splitkb.com | The video uses Choc V2 Silent Linear; V2 does not fit the V1 hot-swap socket |
| 36 (+4) | Hot-swap socket | Kailh CPG135001S30 | https://42keebs.eu/shop/parts/kailh-choc-hot-swap-sockets/ | 1.50 EUR per 10 | https://keeb.supply/products/kailh-hotswap-sockets (2.20 EUR per 10), AliExpress | |
| 36 | Keycap | MBK blank 1u, Choc, PBT | https://42keebs.eu/shop/keycaps/mbk-blank-choc-keycaps/ | 0.40 to 0.70 EUR each | https://keycapsss.com (2.90 EUR per 10), Chosfox low profile | 6 in an accent colour for the thumb keys, as in the reference build |

## 4. Per-half electronics (quantities already doubled)

| Qty | Part | Spec | Source | Price | LCSC | Notes |
|-----|------|------|--------|-------|------|-------|
| 36 (+10) | Diode | 1N4148W, SOD-123 | https://www.reichelt.de, Mouser DE | about 3 EUR per 100 | C81598 | One per key, cathode towards the row |
| 2 | Power switch | MSK-12C02, SMD SPDT slide, 7 x 3 x 1.5 mm | https://kamami.pl/en/switches-and-buttons/584809-msk-12c02-2-position-smd-slide-switch-horizontal-5906623474981.html | about 0.60 EUR each | C431540 | Alps SSSS811101 is the premium alternative, different footprint, not used here |
| 2 | Reset button | Panasonic EVQ-P7A01P, side actuated SMD tact, 3.5 x 2.9 mm | Mouser DE 667-EVQ-P7A01P | about 0.40 EUR each | C122222 | Alps SKRPACE010 (C139797) is the drop-in alternative |
| 2 | Battery connector | JST S2B-PH-SM4-TB, PH 2.0 mm, 2 pin, SMD side entry | Mouser DE 306-S2B-PH-SM4-TB | about 0.50 EUR each | C295747 | Solder pads for bare leads are on the PCB as well |
| 2 | Test pad set | printed on PCB | | | | No part to buy |

## 5. Batteries

| Qty | Part | Spec | Source | Price | Notes |
|-----|------|------|--------|-------|-------|
| 1 | LiPo 301230 | 110 mAh, 32 x 11.5 x 3.3 mm, protected, bare leads | https://42keebs.eu/shop/parts/lithium-polymer-battery/ | about 4 EUR | Plain half, fits under the controller |
| 1 | LiPo 702025 | 300 mAh, 27 x 19.7 x 6.7 mm, protected, JST-PH | https://42keebs.eu/shop/parts/lithium-polymer-battery/ | about 7 EUR | Trackball half, sits in the case pocket |
| | Alternatives | Typeractive 110 mAh, splitkb Halcyon LiPo board | https://typeractive.xyz/products/lithium-battery-110mah, https://splitkb.com/products/halcyon-lipo-battery-board | | Batteries ship within the EU only from 42keebs |

Both halves can take either cell; the ball half needs the larger one because the sensor adds about
0.6 mA while tracking.

## 6. Sensor board (one per keyboard)

| Qty | Part | Spec | Source | Price | LCSC | Notes |
|-----|------|------|--------|-------|------|-------|
| 1 (+1) | Optical sensor | PixArt PMW3610DM-SUDU, 16-pin DIP lead frame | https://www.aliexpress.com/item/1005006208592770.html (chip + lens kit) | about 8 EUR per kit | C42442560 | JLCPCB extended part, can be placed by JLCPCB for a production run |
| 1 (+1) | Lens | PixArt LM18-LSI | with the chip kit | | | Peel both protective films before fitting |
| 1 | LDO 1.8 V | Torex XC6206P182MR, SOT-23 | LCSC, Mouser DE | 0.10 EUR | C5446 | Generates VDD from 3.3 V |
| 2 | Capacitor | 1 uF 0603 X7R 10 V | LCSC | | C15849 | Input and output of the LDO |
| 3 | Capacitor | 100 nF 0603 X7R 16 V | LCSC | | C14663 | VDD, VDDIO, sensor pin decoupling |
| 1 | Resistor | 10 k 0603 | LCSC | | C25804 | NCS pull-up |
| 2 | FPC connector | Hirose FH19SC-6S-0.5SH(05), 6 pin, 0.5 mm, bottom contact, flip lock | Mouser DE 798-FH19SC6S05SH05 | about 1 EUR each | C2764371 (compatible) | One on the main PCB, one on the sensor PCB |
| 1 (+1) | FFC cable | 6 conductor, 0.5 mm pitch, 40 mm, same-side contacts (type A) | AliExpress, Mouser DE (Molex 15166 series) | about 0.50 EUR | | 30 to 50 mm works |

## 7. Trackball and bearings

| Qty | Part | Spec | Source | Price | Alt source | Notes |
|-----|------|------|--------|-------|------------|-------|
| 1 | Ball 25 mm | Perixx PERIPRO-305, 25 mm, polished | https://eu.perixx.com/collections/all | 11.99 EUR | https://perixx.com/products/peripro-305, Amazon DE | German company, EU store often out of stock, check early |
| | Ball alternative | Elecom M-B25SV / M-B25RD, 25 mm | eBay DE, Amazon JP | 12 to 20 EUR | | Released 2024 for the Elecom Relacon |
| | Ball alternative | 25 mm ceramic bearing ball (ZrO2 or Si3N4) | AliExpress "25mm ceramic ball" | 5 to 15 EUR | | What the reference build uses; heavy, very smooth, check it is matte enough for the sensor |
| 3 (+3) | Bearing ball | 2.0 mm ZrO2 (zirconia) precision ball, G10 | AliExpress "2mm zirconia ceramic ball" | cents each | EU precision ball suppliers | Static seats in the cradle; 2.5 mm also fits the parametric cradle |
| 3 | Screw | M2 x 6 mm pan head, steel or nylon | hardware store, Mouser DE | | | Cradle flange to main PCB |
| 3 | Standoff or spacer | M2, 2 mm | | | | Only if the cradle model needs a gap (see trackball module doc) |
| 2 | Screw | M2 x 4 mm | | | | Sensor PCB to cradle |

## 8. Finishing

| Qty | Part | Spec | Source | Price | Notes |
|-----|------|------|--------|-------|-------|
| 8 | Bumper | GLIPLUS anti-slip pads or 3M SJ5302 clear bumpers | Amazon, 3M distributors | 3 to 8 EUR | The reference build uses GLIPLUS pads; they stop the halves from sliding completely |
| 1 | Flux pen, solder wick, 0.5 mm solder | | | | Needed for the FPC connectors |

## 9. Totals

| Group | EUR |
|-------|-----|
| PCBs delivered | 75 |
| Controllers (nice!nano) and sockets | 48 |
| Switches, sockets, keycaps | 54 |
| Per-half electronics | 8 |
| Batteries | 12 |
| Sensor board parts, connectors, cable | 12 |
| Ball, ceramic balls, hardware | 18 |
| Finishing | 5 |
| **Total** | **about 230 EUR** |

With SuperMini controllers: about 210 EUR. The three spare PCB sets reduce a second build to
roughly 150 EUR.

## 10. Order plan

Order in this sequence so the mechanical risk is retired before money goes into PCBs:

1. **Week 0:** 25 mm ball (two if possible), 2 mm ceramic balls, PMW3610 + LM18-LSI kit, FPC
   connectors and cable. Print the cradle from `hardware/trackball-cradle/` and check the
   lens-to-ball distance with the bare sensor board outline.
2. **Week 0, same day:** controllers, batteries, sockets, switches, keycaps from the EU shops.
3. **After the cradle test fit:** PCBs from JLCPCB (main and sensor in one cart, ENIG), LDO and
   passives from LCSC in the same order.
4. **When the PCBs arrive:** follow the [build guide](04-build-guide.md).
