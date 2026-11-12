# Order checklist

Everything to buy for one keyboard (left and right half, one trackball), grouped by shop so each
cart is placed once. Part numbers, specs and prices are those of the [bill of
materials](03-bom.md); this page only sequences the carts. Tick a line when the order is placed
and write the order number next to it. "You do" names the step that needs a person.

Why the PCBs do not wait for the cradle print: the sensor height is set by
`hardware/trackball-cradle/params.scad`, not by any PCB, and the right board's notch is fixed by
the layout and its tests. Details in `issues/hw-jlcpcb-order-r1.md`.

## 1. Already ordered

| Done | Qty | Part | Exact number | Shop | Status | You do |
|------|-----|------|--------------|------|--------|--------|
| [x] | 35 (+4) | Choc hot-swap socket | Kailh CPG135001S30 | https://keycapsss.com | ordered | 1:1 paper check of one socket on `make print-plots` (`issues/hw-main-pcb-review-r1.md` step 2b) |
| [x] | 2 | Power switch | MSK-12C02 | https://keycapsss.com | ordered | 1:1 paper check on `make print-plots`: pins on the three pads (spacing 3.00 then 1.50 mm, asymmetric by design), actuator past the edge line |
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
| [ ] | 1 (+1) | FPC connector, 6 pin 0.5 mm, bottom contact | 798-FH12-6S-0.5SH55 | open | for the right PCB (J1, key side); since r2.4 the sensor module brings its own connector |
| [ ] | 2 | Battery connector JST PH 2.0 side entry | 306-S2B-PH-SM4-TB | open | |
| [ ] | 2 | Reset button, side actuated | 667-EVQ-P7A01P | open | |
| [ ] | 1 (+1) | FFC cable 6 pos 0.5 mm, **type B** (opposite-side contacts), 50 mm | GCT 05-06-D-0050-A-4-06-4-G (Digi-Key DE, about 1.80 EUR), or JUSHUO JS05B-06P-050-3-4 (LCSC C5151973); Molex 15020-0054 (50.8 mm, "Type D") also fits | open | type B is mandatory: a type A cable can make contact and then reverses the pin order, 3.3 V onto GND |

## 3. EU shops (open)

| Done | Qty | Part | Exact number | Shop | Status | You do |
|------|-----|------|--------------|------|--------|--------|
| [ ] | 1 | LiPo 150 mAh, 4 mm thick, with PH 2.0 plug (LEFT half) | LP402025 | Eckstein, 42keebs or Amazon DE | open | the 5.7 mm cell does not fit under the left board's sockets |
| [ ] | 1 | LiPo 350 mAh with PH 2.0 plug (RIGHT half) | PKCELL LP552035 | https://eckstein-shop.de/LiPo-Akku-Lithium-Ion-Polymer-Batterie-37V-350mAh-mit-JST-PHR-2-Stecker-LP552035 | open | |
| [ ] | 1 | Trackball 19 mm phenolic (premium option) | PandaKB TB19 | https://pandakb.com/shop/parts/pandakb-tb19-19mm-split-keyboard-trackball/ | open | optional next to the POM pack |

## 4. Amazon DE (open)

| Done | Qty | Part | Spec | Status | You do |
|------|-----|------|------|--------|--------|
| [ ] | 1 pack | Ball 19.05 mm | 3/4 inch POM (Delrin) bearing balls, pack of 10 to 20 | open | test two or three balls on the sensor (`issues/hw-ball-colour-tracking-test.md`) |
| [ ] | 3 (+3) | Bearing ball | 2.0 mm ZrO2 (zirconia) precision balls | open | AliExpress is the usual source, Amazon if in stock |
| [ ] | 2 | Cradle screw | M2 x 8 self-tapping countersunk (90 degree flat head) | open | up through the case floor into the cup skirt; since r2.4 the module has no screw holes of its own (`hardware/trackball-cradle/params.scad`) |
| [ ] | 1 pack (50) | Heat-set threaded insert | brass, M2, 3 mm long, about 3.5 mm OD, for a 3.2 mm hole | open | 14 used: 5 PCB standoffs + 2 controller-cap bosses per half; Amazon DE or AliExpress |
| [ ] | 4 | Box cap screw | M2 x 5 countersunk machine screw (90 degree flat head), head max 3.8 mm dia | open | 2 per half, flush in the controller box cap; M2 x 6 bottoms out in the boss |
| [ ] | 1 pack (10 used) | PCB screw | M2 x 5 machine screw, pan or button head, head max 3.5 mm dia | open | 5 per half; the alternative is self-tapping into a 1.6 mm pilot (`-D pcb_screws="pilot"` in `hardware/case/params.scad`) |
| [ ] | 14 | Bumper | 10 mm round rubber feet, 1 mm thick | open | seven 10.5 mm recesses per half, 0.8 mm deep; taller dome bumpers do not fit them |
| [ ] | 2 | Pocket cover screw | M2 x 6 countersunk (90 degree flat head), self-tapping | open | right half, from the top into the tray |
| [ ] | 1 roll | Kapton tape, 10 mm | | open | over the back of the sensor sleeve and over the controller socket joints in the battery bay |
| [ ] | 1 pack (20) | Magnet | 6 x 2 mm neodymium disc | open | 16 used: 4 in the tray floor and 4 in the outer lid plate's roof per half (`issues/mech-case-lid.md`) |
| [ ] | 2 | Hinge pin | 2 mm steel rod, about 80 mm (2 mm round bar or a 2 x 80 mm dowel pin, cut to length) | open | one per lid hinge; a piece of 1.75 mm filament is the fallback (`hardware/case/README.md`) |

## 5. Sensor module and AliExpress (open)

| Done | Qty | Part | Spec | Status | You do |
|------|-----|------|------|--------|--------|
| [ ] | 1 | PAW3222 trackball sensor module, 13.4 x 7.4 mm | beekeeb (https://shop.beekeeb.com, worldwide, free shipping from 80 USD) or BOOTH (https://booth.pm); price: see shop | open | EU shipping is fine; check the pinout on arrival (1 3.3V, 2 CS, 3 MOTION, 4 SDIO, 5 SCLK, 6 GND) |
| [ ] | 2 | FFC cable (alternative to Digi-Key) | 6 pin 0.5 mm, 50 mm, **type B** opposite-side contacts (LCSC JUSHUO JS05B-06P-050-3-4, C5151973) | open | only one of the two cable lines is needed; check the two ends against the light before ordering a batch |

## 6. JLCPCB and LCSC (open)

Upload the two zips, one order each, in the same cart:

- `hardware/left-pcb/k0d3ball35-left-gerbers.zip`
- `hardware/right-pcb/k0d3ball35-right-gerbers.zip`

Parameters from [spec/06](06-fabrication.md): 2 layers, quantity 5 per design, FR-4 TG 135 or
higher, 1.6 mm, 1 oz, ENIG (lead-free HASL is acceptable), tented vias, remove order number
("specify a location" or "yes"), white silkscreen.

| Done | Step | Status | You do |
|------|------|--------|--------|
| [ ] | Upload preview: 2 layers detected, about 121 x 87 mm each, no DFM complaint about the notch | open | `issues/test-fab-gerber-viewer.md` |
| [ ] | Order the two batches | open | record order number, cost and the tag `v0.2.0-r2-order` in `issues/hw-jlcpcb-order-r1.md` |

No LCSC lines: the sensor is a bought module (`issues/hw-paw3222-variant.md`).

## 7. Printed parts

| Done | Part | File | Status | You do |
|------|------|------|--------|--------|
| [ ] | Cradle, 19 mm pocket mount | `hardware/trackball-cradle/stl/cradle-19mm-pocket.stl` | orderable now | print in parallel with the PCB order |
| [ ] | Case trays | `hardware/case/stl/tray-left.stl`, `hardware/case/stl/tray-right.stl` | being generated in `hardware/case/` | wait for the case ticket (`issues/mech-case.md`) |
| [ ] | Controller caps | `hardware/case/stl/box-cap-left.stl`, `hardware/case/stl/box-cap-right.stl` | being generated | same |
| [ ] | Lid plates | `hardware/case/stl/lid-outer-left.stl`, `lid-inner-left.stl`, `lid-outer-right.stl`, `lid-inner-right.stl` | being generated | same (`issues/mech-case-lid.md`); `lid-left.stl` / `lid-right.stl` are the closed pairs for the exploded view, not for printing |
| [ ] | Pocket test piece | `hardware/case/stl/pocket-test-right.stl` | being generated | print first, test the cradle and the right PCB notch in it |

Print service or own printer: a service (JLC3DP or Craftcloud, SLA resin or MJF nylon) gives the
cleanest bearing seats and the flattest floor; for the cradle pick SLA. On an own FDM printer use
0.12 mm layers, 3 perimeters, no supports (the optional retainer clip needs them under its ring), and ream the
three 2 mm bearing seats with a drill bit by hand before pressing the ceramic balls in.

## 8. What waits for hardware

These cannot be done from the files and are the remaining steps before, during and after the
order:

- JLCPCB upload preview of the two zips, then the order (`issues/hw-jlcpcb-order-r1.md`)
- 1:1 paper check of a socket and the MSK12C02 on `make print-plots` (`issues/hw-main-pcb-review-r1.md` step 2b)
- KiCad 3D viewer pass of both main boards (same ticket)
- GitHub push so CI builds the firmware and runs the suite (`issues/infra-ci-firmware.md`, `issues/infra-ci-hardware.md`)
- Cradle and pocket test prints, lens gap with a feeler gauge (`issues/mech-ball-height-23mm.md`)
- FFC continuity with a physical cable and both connectors (`issues/hw-ffc-pin-order-verification.md`)
- Ball tracking test, POM versus phenolic (`issues/hw-ball-colour-tracking-test.md`)
