# Bill of materials

One complete keyboard: a left and a right half (two different PCBs since r2), one trackball on
the right half. Prices are EU retail including VAT as of late 2025 and will drift; links point to
the shop category or product page. LCSC part numbers are given where the part can be ordered
together with the PCBs.

Quantities marked "+n" include recommended spares.

![All parts laid out before assembly](images/img-parts-flatlay.png)

## 1. Printed circuit boards

| Qty | Part | Spec | Source | Price | Notes |
|-----|------|------|--------|-------|-------|
| 1 (min. order 5) | Left PCB `k0d3ball35-left` | 2 layer, 1.6 mm FR4, 1 oz, ENIG, 121 x 87 mm | JLCPCB, gerbers in `hardware/left-pcb/` | 15 to 25 EUR per 5 | 18 keys, no sensor connector |
| 1 (min. order 5) | Right PCB `k0d3ball35-right` | 2 layer, 1.6 mm FR4, 1 oz, ENIG, 121 x 87 mm | JLCPCB, gerbers in `hardware/right-pcb/` | 15 to 25 EUR per 5 | 17 keys, FPC connector on the key side, notch for the ball pocket |
| | Shipping and import VAT | | | 20 to 40 EUR | Order both boards in the same cart to share shipping |

## 2. Controllers and sockets

| Qty | Part | Spec | Source | Price | Alt source | Notes |
|-----|------|------|--------|-------|------------|-------|
| 2 | nice!nano v2 | nRF52840, Pro Micro pinout, LiPo charger, battery ADC | https://42keebs.eu/shop/parts/controllers/nice-nano-v2-wireless-controller/ | 20.70 EUR each | https://splitkb.com/products/nice-nano (25.94 EUR), https://keycapsss.com (Puchi-BLE, 27.90 EUR) | One per half, identical wiring on both PCBs |
| 2 | SuperMini nRF52840 (alternative) | nice!nano clone, same pinout | https://mechboards.co.uk/products/supermini-nrf52840-ble-pro-micro | about 10 EUR each | AliExpress | Cheaper, slightly higher sleep current reported by some users |
| 4 | Socket strip 1 x 12, low profile | Mill-Max 315-43-112 (2.1 to 2.8 mm above the board) or "conthrough" spring pins (2.5 mm), 2.54 mm pitch, 12 pins | https://42keebs.eu/shop/parts/components/controller-sockets-pins-mill-max-generic/ | 1 to 2 EUR each | https://keycapsss.com, AliExpress | Nothing sits under the controller any more (the cell is under the PCB), so the lowest socket wins. Mill-Max 310 (4.2 mm) still fits but adds height. |
| 48 | Socket pins | Mill-Max 3320-0-00-15-00-00-03-0 (0.52 mm, 6.3 mm) or diode-leg style | with the sockets | | | Only needed with machined sockets; conthrough needs none |

## 3. Switches and keycaps

| Qty | Part | Spec | Source | Price | Alt source | Notes |
|-----|------|------|--------|-------|------------|-------|
| 35 (+2) | Kailh Choc V1 switch | CPG1350, any stem; Silent Linear, Pro Red or Sunset recommended | https://keycapsss.com/Kailh-Low-Profile-Choc-Switches-V1/KC10034-SI | 6.90 to 7.90 EUR per 10 | https://42keebs.eu, https://splitkb.com | 18 left, 17 right. The video uses Choc V2 Silent Linear; V2 does not fit the V1 hot-swap socket |
| 35 (+4) | Hot-swap socket | Kailh CPG135001S30 | https://42keebs.eu/shop/parts/kailh-choc-hot-swap-sockets/ | 1.50 EUR per 10 | https://keeb.supply/products/kailh-hotswap-sockets (2.20 EUR per 10), AliExpress | 18 left, 17 right |
| 35 | Keycap | MBK blank 1u, Choc, PBT | https://42keebs.eu/shop/keycaps/mbk-blank-choc-keycaps/ | 0.40 to 0.70 EUR each | https://keycapsss.com (2.90 EUR per 10), Chosfox low profile | 5 in an accent colour for the thumb keys (3 left, 2 right), as in the reference build |

## 4. Per-half electronics (quantities for both halves)

| Qty | Part | Spec | Source | Price | LCSC | Notes |
|-----|------|------|--------|-------|------|-------|
| 35 (+10) | Diode | 1N4148W, SOD-123 | https://www.reichelt.de, Mouser DE | about 3 EUR per 100 | C81598 | One per key (18 left, 17 right), cathode towards the row |
| 2 | Power switch | MSK-12C02, SMD SPDT slide, 7 x 3 x 1.5 mm | https://kamami.pl/en/switches-and-buttons/584809-msk-12c02-2-position-smd-slide-switch-horizontal-5906623474981.html | about 0.60 EUR each | C431540 | Alps SSSS811101 is the premium alternative, different footprint, not used here |
| 2 | Reset button | Panasonic EVQ-P7A01P, side actuated SMD tact, 3.5 x 2.9 mm | Mouser DE 667-EVQ-P7A01P | about 0.40 EUR each | C122222 | Alps SKRPACE010 (C139797) is the drop-in alternative |
| 2 | Battery connector | JST S2B-PH-SM4-TB, PH 2.0 mm, 2 pin, SMD side entry | Mouser DE 306-S2B-PH-SM4-TB | about 0.50 EUR each | C295747 | Default on both halves (the LP552035 comes with a PH 2.0 plug); 6 mm tall, sits inside the battery well. Bare leads can go to the pads J2 instead |
| 2 | Test pad set | printed on PCB | | | | No part to buy; no solder jumpers exist in r2 |

## 5. Batteries

| Qty | Part | Spec | Source | Price | Notes |
|-----|------|------|--------|-------|-------|
| 2 | LiPo PKCELL LP552035 | 350 mAh, 5.7 x 20 x 37 mm max. incl. protection circuit (S-8261), JST-PH 2.0 plug, 10 cm leads | https://eckstein-shop.de/LiPo-Akku-Lithium-Ion-Polymer-Batterie-37V-350mAh-mit-JST-PHR-2-Stecker-LP552035 | 4.97 EUR each | One per half, in the battery bay under the PCB below the controller; plugs into J3. Same cell at tinytronics.nl |
| | Alternatives | 502030 (250 mAh, 20 x 30 x 5 mm), 402025 (150 mAh, Eckstein LP402025) | 42keebs, Eckstein, Amazon | | Any cell up to 20.5 x 37.5 x 5.7 mm with a PH 2.0 plug fits: the case well is 6.0 mm deep. 6 and 7 mm cells (602025, 702025, 602030) do not. Mouser does not ship lithium cells to Germany |

Both halves use the same cell and the same bay, so there is one battery part to buy and one case
well to print. The ball half still drains faster because of the sensor.

## 6. Sensor module and cable (one per keyboard)

| Qty | Part | Spec | Source | Price | LCSC | Notes |
|-----|------|------|--------|-------|------|-------|
| 1 | Trackball sensor module | PixArt PAW3222 with lens on a 14 x 8 mm board, 6-pin 0.5 mm FPC connector (pinout 3.3V, CS, MOTION, SDIO, SCLK, GND) | beekeeb, https://shop.beekeeb.com (ships worldwide, free shipping from 80 USD), or BOOTH, https://booth.pm | see shop | | The module torabo-tsuki LP uses. Shipping to the EU is fine. Sits tilted in the cradle sleeve (`spec/08-trackball-module.md`) |
| 2 | FPC connector J1 | Hirose FH12-6S-0.5SH(55), 6 pin, 0.5 mm, bottom contact, ZIF slider | Mouser DE 798-FH12-6S-0.5SH55 | about 1 EUR each | C2764370 | One on the right PCB (key side), one spare for rework; the left PCB has none. The LCSC code is a pin-compatible equivalent for a JLCPCB assembly run |
| 1 (+1) | FFC cable | 6 conductor, 0.5 mm pitch, 30 to 40 mm, **opposite-side contacts (type B)** | AliExpress, Mouser DE (Molex 15166 series) | about 0.50 EUR | | Type B is mandatory: J1 and the module look at the cable from opposite faces, a type A cable connects nothing |

## 7. Trackball and bearings

| Qty | Part | Spec | Source | Price | Alt source | Notes |
|-----|------|------|--------|-------|------------|-------|
| 1 (+1) | Ball 19.05 mm | POM (Delrin) bearing ball, 3/4 inch, grade G1 or G2, matte | Amazon DE or AliExpress "3/4 inch POM ball" (packs of 10 to 20) | 3 to 8 EUR per pack | https://www.kugel-winnie.de (precision ball supplier), eBay | What torabo-tsuki LP ships as its 19.05 mm option; buy a pack, the surface varies slightly between balls |
| | Ball premium option | PandaKB TB19, 19 mm phenolic resin trackball | https://pandakb.com/shop/parts/pandakb-tb19-19mm-split-keyboard-trackball/ | 11.90 USD | | Sold specifically for split keyboards; phenolic tracks very well on PixArt sensors |
| 3 (+3) | Bearing ball | 2.0 mm ZrO2 (zirconia) precision ball, G10 | AliExpress "2mm zirconia ceramic ball" | cents each | EU precision ball suppliers | Static seats in the cradle; 2.5 mm also fits the parametric cradle |
| 2 | Screw | M2 x 8 mm countersunk (90 degree flat head), self-tapping, steel | hardware store, Mouser DE | | | Case screws: from below through the case floor into the cradle's cup skirt, 20 mm apart |
| 2 | Screw | M2 x 6 mm countersunk (90 degree flat head, DIN 7991 or self-tapping) | hardware store, Amazon DE | | | Pocket cover, right half: from the top into 1.6 mm pilots in the tray ledge |
| 14 (pack of 50) | Heat-set threaded insert | brass, M2, 3 mm long, about 3.5 mm OD, for a 3.2 mm hole | Amazon DE, AliExpress | 5 to 8 EUR per pack | | Default of the case (`hardware/case/params.scad`): five PCB standoffs and two controller-cap bosses per half, 7 per half |
| 14 (pack) | Screw | M2 x 5 (or x 6) machine screw, pan or button head, head max 3.5 mm dia | Amazon DE, hardware store | 3 to 5 EUR per pack | | 7 per half into the inserts. Alternative: self-tapping into a 1.6 mm pilot with `-D pcb_screws="pilot"` in `hardware/case/params.scad` |

## 8. Finishing

| Qty | Part | Spec | Source | Price | Notes |
|-----|------|------|--------|-------|-------|
| 14 | Bumper | 10 mm round rubber feet, 1 mm thick | Amazon, 3M distributors | 3 to 8 EUR | Seven 10.5 mm recesses per half, 0.8 mm deep: the feet stand 0.2 mm proud and grip (`hardware/case/README.md`) |
| about 220 g | Filament | PLA or PETG, matte | | 5 EUR | about 110 g per half for tray, cap and the two lid plates (`spec/11-case.md`) |
| 16 (pack of 20) | Magnet | 6 x 2 mm neodymium disc, N35 or better | Amazon DE | 5 to 8 EUR per pack | 8 per half for the lid as a foot (`issues/mech-case-lid.md`): 4 in the tray floor, 4 in the roof of the outer lid plate |
| 2 | Hinge pin | 2 mm steel rod, about 80 mm long: 2 mm round bar ("Rundstahl 2 mm") or a 2 x 80 mm dowel pin, cut to length | hardware store, Amazon DE | 1 to 3 EUR | One per lid hinge (`hardware/case/README.md`); a piece of 1.75 mm filament works as a fallback with `-D hinge_pin_d=1.75` |
| 1 | Flux pen, solder wick, 0.5 mm solder | | | | Needed for the FPC connectors |
| 1 | Kapton tape | 10 mm wide | Amazon DE | 3 to 6 EUR | A strip over the back of the sensor sleeve holds the module (`spec/04-build-guide.md`, chapter 10) |

## 9. Totals

| Group | EUR |
|-------|-----|
| PCBs delivered (two designs, 5 each) | 85 |
| Controllers (nice!nano) and sockets | 48 |
| Switches, sockets, keycaps | 53 |
| Per-half electronics | 8 |
| Batteries | 10 |
| Sensor module | see shop |
| FPC connectors, cable | 3 |
| Ball, ceramic balls, hardware | 10 |
| Finishing | 5 |
| **Total** | **about 225 EUR plus the sensor module** |

With SuperMini controllers: about 20 EUR less. The spare PCB sets reduce a second build to roughly
150 EUR. Two separate main PCBs cost one more 5-piece batch than the r1 reversible board did; in
exchange the boards lost the jumpers, the dead D0 and the empty ball cutout on the left.

## 10. Order plan

The shop-by-shop checklist with quantities, part numbers and what is already ordered lives in
[spec/12-order-checklist.md](12-order-checklist.md). Sequencing: the PCBs do not wait for the
cradle test print, since nothing the print can show changes a PCB. Order the PCBs, the sensor
module and the small parts in the same week, print the cradle in parallel, and follow the
[build guide](04-build-guide.md) when the boards arrive.
