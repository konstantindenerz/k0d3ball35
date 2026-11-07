# Order checklist

Everything to buy for one keyboard (left and right half, one trackball), grouped by shop so each
cart is placed once. Part numbers, specs and prices are those of the [bill of
materials](03-bom.md); this page only sequences the carts. Tick a line when the order is placed
and write the order number next to it. "You do" names the step that needs a person.

Why the PCBs no longer wait for the cradle print: the sensor height is set by
`hardware/trackball-cradle/params.scad`, not by any PCB; the right board's notch is fixed by the
layout and its tests; and the only outcome that would change a PCB (a 25 mm ball instead of 19 mm)
cannot be tested without the sensor PCB in hand. The exposure is one right-hand batch, about
30 to 40 EUR. Details in `issues/hw-jlcpcb-order-r1.md`.

## 1. Already ordered

| Done | Qty | Part | Exact number | Shop | Status | You do |
|------|-----|------|--------------|------|--------|--------|
| [x] | 35 (+4) | Choc hot-swap socket | Kailh CPG135001S30 | https://keycapsss.com | ordered | 1:1 paper check of one socket on the printed PCB plot (`issues/hw-main-pcb-review-r1.md`) |
| [x] | 2 | Power switch | MSK-12C02 | https://keycapsss.com | ordered | 1:1 paper check: pins on the three pads, actuator past the edge line |
| [x] | 4 | Controller socket strip 1 x 12 | Mill-Max 315-43-112 | https://keycapsss.com | ordered | |
| [x] | 48 | Socket pins | Mill-Max 3320-0-00-15-00-00-03-0 | https://keycapsss.com | ordered | |
| [x] | 35 (+10) | Diode | 1N4148W SOD-123 | https://keycapsss.com | ordered | |
| [x] | 2 | Controller | nice!nano v2 | https://42keebs.eu/shop/parts/controllers/nice-nano-v2-wireless-controller/ | ordered | |
| [ ] | 35 (+2) | Choc V1 switch | CPG1350 (Silent Linear, Pro Red or Sunset) | https://keycapsss.com/Kailh-Low-Profile-Choc-Switches-V1/KC10034-SI | **confirm**: not in the ordered list | check the keycapsss order; add to the next cart if missing |
| [ ] | 35 | Keycap | MBK blank 1u Choc, 5 in an accent colour | https://42keebs.eu/shop/keycaps/mbk-blank-choc-keycaps/ or https://keycapsss.com | **confirm**: not in the ordered list | same |

## 2. Mouser DE (open)

One cart; everything ships from the same warehouse.

| Done | Qty | Part | Mouser number | Status | You do |
|------|-----|------|---------------|--------|--------|
| [ ] | 2 | FPC connector, 6 pin 0.5 mm, bottom contact | 798-FH12-6S-0.5SH55 | open | one for the right PCB (J1, key side), one for the sensor PCB |
| [ ] | 2 | Battery connector JST PH 2.0 side entry | 306-S2B-PH-SM4-TB | open | |
| [ ] | 2 | Reset button, side actuated | 667-EVQ-P7A01P | open | |
| [ ] | 1 (+1), optional | FFC cable 6 pos 0.5 mm, **type B** (opposite-side contacts), 30 to 40 mm | Molex 15166 series, 6 circuits, type B | open | type B is mandatory, a type A cable does not connect (`spec/08-trackball-module.md` 2.2); or take the AliExpress cable below |
| [ ] | 2, optional | LDO 1.8 V SOT-23 | Torex XC6206P182MR | open | only if the LCSC lines are not ordered with the PCBs |

## 3. EU shops (open)

| Done | Qty | Part | Exact number | Shop | Status | You do |
|------|-----|------|--------------|------|--------|--------|
| [ ] | 2 | LiPo 350 mAh with PH 2.0 plug | PKCELL LP552035 | https://eckstein-shop.de/LiPo-Akku-Lithium-Ion-Polymer-Batterie-37V-350mAh-mit-JST-PHR-2-Stecker-LP552035 | open | |
| [ ] | 1 | Trackball 19 mm phenolic (premium option) | PandaKB TB19 | https://pandakb.com/shop/parts/pandakb-tb19-19mm-split-keyboard-trackball/ | open | optional next to the POM pack |

## 4. Amazon DE (open)

| Done | Qty | Part | Spec | Status | You do |
|------|-----|------|------|--------|--------|
| [ ] | 1 pack | Ball 19.05 mm | 3/4 inch POM (Delrin) bearing balls, pack of 10 to 20 | open | test two or three balls on the sensor (`issues/hw-ball-colour-tracking-test.md`) |
| [ ] | 3 (+3) | Bearing ball | 2.0 mm ZrO2 (zirconia) precision balls | open | AliExpress is the usual source, Amazon if in stock |
| [ ] | 2 | Cradle screw | M2 x 10 self-tapping countersunk (90 degree flat head) | open | plus 2 x M2 x 5 self-tapping for the bench test of the sensor board in the cradle posts |
| [ ] | 1 pack (50) | Heat-set threaded insert | brass, M2, 3 mm long, about 3.5 mm OD, for a 3.2 mm hole | open | 14 used: 5 PCB standoffs + 2 controller-cap bosses per half; Amazon DE or AliExpress |
| [ ] | 1 pack (14 used) | PCB and cap screw | M2 x 5 (or x 6) machine screw, pan or button head, head max 3.5 mm dia | open | 7 per half; the alternative is self-tapping into a 1.6 mm pilot (`-D pcb_screws="pilot"` in `hardware/case/params.scad`) |
| [ ] | 8 | Bumper | GLIPLUS pads or 3M SJ5302 | open | |
| [ ] | 1 pack (20) | Magnet | 6 x 2 mm neodymium disc | open | 16 used: 4 in the tray floor and 4 in the outer lid plate's roof per half (`issues/mech-case-lid.md`) |
| [ ] | 2 | Hinge pin | 2 mm steel rod, about 80 mm (2 mm round bar or a 2 x 80 mm dowel pin, cut to length) | open | one per lid hinge; a piece of 1.75 mm filament is the fallback (`hardware/case/README.md`) |

## 5. AliExpress (open)

| Done | Qty | Part | Spec | Status | You do |
|------|-----|------|------|--------|--------|
| [ ] | 1 (+1) | Sensor and lens kit | PMW3610DM-SUDU + LM18-LSI, https://www.aliexpress.com/item/1005006208592770.html | open | measure the lens flange and clips on arrival (`issues/mech-lm18-lens-outline-measurement.md`) |
| [ ] | 2 | FFC cable (alternative to Mouser) | 6 pin 0.5 mm, 30 to 40 mm, **type B** opposite-side contacts | open | only one of the two cable lines is needed; check the two ends against the light before ordering a batch |

## 6. JLCPCB and LCSC (open)

Upload the three zips, one order each, in the same cart:

- `hardware/left-pcb/k0d3ball35-left-gerbers.zip`
- `hardware/right-pcb/k0d3ball35-right-gerbers.zip`
- `hardware/sensor-pcb/fab/k0d3ball35-sensor-r1-gerbers.zip`

Parameters from [spec/06](06-fabrication.md): 2 layers, quantity 5 per design, FR-4 TG 135 or
higher, 1.6 mm, 1 oz, ENIG (lead-free HASL is acceptable for the two main boards, ENIG for the
sensor board), tented vias, remove order number ("specify a location" or "yes"), white silkscreen.

| Done | Step | Status | You do |
|------|------|--------|--------|
| [ ] | Upload preview: 2 layers detected, about 121 x 87, 121 x 87 and 26 x 25 mm, no DFM complaint about the notch or the sensor window | open | `issues/test-fab-gerber-viewer.md` |
| [ ] | Order the three batches | open | record order number, cost and the tag `v0.2.0-r2-order` in `issues/hw-jlcpcb-order-r1.md` |

LCSC lines for the sensor board, in the same cart (quantities for one board plus spares; codes
from `hardware/sensor-pcb/fab/k0d3ball35-sensor-r1-bom.csv`):

| Done | Qty | Part | LCSC |
|------|-----|------|------|
| [ ] | 2 | XC6206P182MR LDO 1.8 V, SOT-23 | C5446 |
| [ ] | 2 | 1 uF 0603 X5R 10 V (C1, C2) | C15849 |
| [ ] | 1 | 3.3 uF 0603 X7R 16 V (C3) | C1678 |
| [ ] | 3 | 100 nF 0603 X7R 16 V (C4, C5, C6) | C14663 |
| [ ] | 2 | 10 nF 0603 X7R 16 V (C7, C9) | C57112 |
| [ ] | 1 | 10 uF 0603 X7R 16 V (C8) | C19702 |
| [ ] | 2 | 10 k 0603 (R1, R2) | C25804 |
| [ ] | 1 | 1 k 0603 (R3) | C21190 |
| [ ] | 2, optional | FPC connector 6 pin 0.5 mm, FH12 equivalent (if not from Mouser) | C2764370 |

0603 parts come in minimum lots of 10 to 20 at LCSC; the cost is cents either way, so order the
minimum lot of each and keep the rest as spares. The sensor itself (C42442560) comes with the lens
in the AliExpress kit; LCSC only matters for a later assembly run.

## 7. Printed parts

| Done | Part | File | Status | You do |
|------|------|------|--------|--------|
| [ ] | Cradle, 19 mm pocket mount | `hardware/trackball-cradle/stl/cradle-19mm-pocket.stl` | orderable now | print in parallel with the PCB order |
| [ ] | Cradle, 25 mm fallback | `hardware/trackball-cradle/stl/cradle-25mm-pocket.stl` | orderable now | only if the 19 mm ball disappoints (`issues/hw-25mm-cradle-fallback.md`) |
| [ ] | Case trays | `hardware/case/stl/tray-left.stl`, `hardware/case/stl/tray-right.stl` | being generated in `hardware/case/` | wait for the case ticket (`issues/mech-case.md`) |
| [ ] | Controller caps | `hardware/case/stl/box-cap-left.stl`, `hardware/case/stl/box-cap-right.stl` | being generated | same |
| [ ] | Lid plates | `hardware/case/stl/lid-outer-left.stl`, `lid-inner-left.stl`, `lid-outer-right.stl`, `lid-inner-right.stl` | being generated | same (`issues/mech-case-lid.md`); `lid-left.stl` / `lid-right.stl` are the closed pairs for the exploded view, not for printing |
| [ ] | Pocket test piece | `hardware/case/stl/pocket-test-right.stl` | being generated | print first, test the cradle and the right PCB notch in it |

Print service or own printer: a service (JLC3DP or Craftcloud, SLA resin or MJF nylon) gives the
cleanest bearing seats and the flattest floor; for the cradle pick SLA. On an own FDM printer use
0.12 mm layers, 3 perimeters, no supports (the parts are designed to print flat), and ream the
three 2 mm bearing seats with a drill bit by hand before pressing the ceramic balls in.

## 8. What waits for hardware

These cannot be done from the files and are the remaining steps before, during and after the
order:

- JLCPCB upload preview of the three zips, then the order (`issues/hw-jlcpcb-order-r1.md`)
- 1:1 paper check of a socket and the MSK12C02 on the printed plot (`issues/hw-main-pcb-review-r1.md`)
- KiCad 3D viewer pass of both main boards (same ticket)
- GitHub push so CI builds the firmware and runs the suite (`issues/infra-ci-firmware.md`, `issues/infra-ci-hardware.md`)
- Cradle and pocket test prints, lens gap with a feeler gauge (`issues/hw-sensor-stack-height.md`)
- FFC continuity with a physical cable and both connectors (`issues/hw-ffc-pin-order-verification.md`)
- LM18-LSI flange and clip measurement (`issues/mech-lm18-lens-outline-measurement.md`)
- Ball tracking test, POM versus phenolic (`issues/hw-ball-colour-tracking-test.md`)
