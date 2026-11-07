# Feasibility study

Status: complete (2026-11-05). Verdict: **GO.**

Every subsystem of k0d3ball35 has working, open-source prior art. The firmware stack needs no
third-party driver module any more. The two genuine risks are mechanical and logistical, not
electrical: a trackball small enough for a low-profile board that still tracks (resolved in r2 with
a 19.05 mm POM ball, see section 4a), and keeping the sensor stack under the ball low enough.

![Reference build on an oak desk](images/img-hero-desk.png)

## 1. The source build

The reference is the keyboard shown in the YouTube video
"[The endpoint of keyboard and mouse] I completed the ultimate keyboard, fully wireless, split, with
a trackball" (channel monograph, published 2024-08-07, Japanese). The author describes, in order:

- Base: **Keyball39** by Yowkees, the smallest Keyball model (39 keys).
- PCB: the **Keyball39ish-LP**, a low-profile re-layout of the Keyball39 made and sold by Kz
  (@kazu_dob). It is not published as source.
- Switches: Kailh Choc V2 Silent Linear (earlier Lofree Ghost). Keycaps and case: self-designed,
  3D printed, narrow pitch, dished caps, orange thumb caps for layer keys.
- Trackball: a **25 mm ceramic bearing ball from AliExpress** in a self-designed printed holder.
- Wireless conversion: a **BLE Micro Pro** replacing the Pro Micro, a conversion kit bought from
  @PinoCo998 (made for the standard Keyball, adapted to the LP board), a LiPo cell and regulator
  soldered in by hand, firmware flashed through the BLE Micro Pro web configurator.
- The author calls the software side "much harder than expected" and the information "scarce
  and scattered".

No repository, STL or BOM was published by the author. The Japanese community build logs for the
same conversion route agree on two points: battery life of the converted boards is poor (the
PMW3360 on the Keyball daughterboard is a 5 V, high-current part), and ZMK-native designs with
the PMW3610 sensor (roBa, moNa2, torabo-tsuki) are the better route today.

That is exactly what k0d3ball35 does: it is a from-scratch low-profile, wireless-first design that
keeps the Keyball39 hand geometry and replaces everything else.

## 2. What Keyball39 actually is, and how k0d3ball35 differs

Measured from the published design data of the Keyball repository (gerbers, KiCad 5 sources,
netlist). Nothing from that repository is included here; see section 7.

| Aspect | Keyball39 (Yowkees) | k0d3ball35 |
|--------|---------------------|------------|
| Keys | 39 (21 no-ball half, 18 ball half) | 35 (18 left, 17 ball half; two different PCBs since r2) |
| Switch standard | MX, 19.05 mm pitch, 5 thumb positions MX/Choc dual | Choc V1, 18 x 17 mm pitch, all positions hot-swap |
| Column stagger | 11.70 / 4.70 / 0 / 2.50 / 5.00 mm (pinky to inner) | same proportions scaled to 17 mm rows |
| Thumb cluster | 3-key arc, 21.63 mm pitch, 0 / 10 / 20 degrees | same arc, 20.4 mm pitch, same angles; the ball half uses the two inner keys and the ball takes the outer position, as on the Keyball |
| Controller | Pro Micro (ATmega32U4) or RP2040 Pro Micro, wired | nice!nano v2 / SuperMini (nRF52840), BLE |
| Half interconnect | TRRS cable, half-duplex serial | Bluetooth split (ZMK) |
| Sensor | PMW3360 on a 5 V daughterboard with 1.9 V LDO and two level shifters | PMW3610 on a 3.3 V daughterboard, 1.8 V LDO, no level shifting |
| Sensor interface | 7-pin press-fit connector with 8 solder jumpers | 6-pin 0.5 mm FPC |
| Ball | 34 mm, 3 glued 2 mm ceramic balls, injection-moulded holder (not published) | 19.05 mm POM, 3 x 2 mm ZrO2 balls, parametric printed cradle standing in a case pocket beside the PCB (published) |
| Power | USB | 1S LiPo per half, controller charger, slide switch |
| PCB | two different PCBs per half, top FR4 plate, acrylic layers | one flat PCB per half (no plate), one sensor PCB |
| Extras | OLED, SK6812MINI-E RGB, reset, handedness jumper | none (reset only) |
| Firmware | QMK 0.22.14 out-of-tree, Remap / Keyball Link | ZMK main, ZMK Studio |
| License | GPL-3.0 (blanket), firmware GPL-2.0-or-later | MIT (software, docs) + CERN-OHL-P-2.0 (hardware) |
| Published | PCB sources and gerbers yes; sensor board and ball holder no | everything |

![Top view of both halves with the key grid](images/img-layout-top.png)

## 3. Prior art

| Project | What it contributes | Sensor / ball | MCU | License | Source |
|---------|---------------------|---------------|-----|---------|--------|
| torabo-tsuki-lp (sekigon-gonnoc) | low-profile wireless split shipped with a **25 or 19.05 mm POM** ball, FPC sensor module, full KiCad | PAW3222 class module, 25 / 19.05 mm | BMP Boost | MIT | https://github.com/sekigon-gonnoc/torabo-tsuki-lp |
| LiNEA40 (keyfreaks) | Choc split with a **19 mm** ball and the PMW3610 directly on the PCB: the tracking precedent for our ball size | PMW3610, 19 mm | nRF52840 | open hardware | https://github.com/keyfreaks/LiNEA40 |
| roBa (kumamuk-git) | wireless Keyball-style split on ZMK, published PMW3610 breakout | PMW3610, 34 mm | XIAO nRF52840 | GPL-3.0 | https://github.com/kumamuk-git/roBa |
| Kivipallur (dr3san) | 38-key Choc V1 split with a 25 mm ball, Ergogen built | PMW3360, 25 mm | 0xCB Helios | GPL-3.0 | https://github.com/dr3san/Kivipallur |
| Cocot46plus (aki27kbd) | 34 / 25 mm ball option, printed 25 mm case | ADNS-5050 | Pro Micro | MIT | https://github.com/aki27kbd/cocot46plus |
| zmk_kb39 (fengli-master) | documented wireless Keyball39 hardware plan, nice!nano + PMW3610, BOM | PMW3610, 34 mm | nice!nano v2 | GPL-3.0 | https://github.com/fengli-master/zmk_kb39 |
| zmk-config (kovalev-org) | mature Keyball39 ZMK tuning: CPI, per-axis scaling, auto mouse layer timings | PMW3610 | nice!nano v2 | MIT | https://github.com/kovalev-org/zmk-config |
| zmk-config-Keyball39 (tangbonze) | the de-facto Keyball39 ZMK shield and pin map we reuse | PMW3610 | nice!nano v2 | MIT | https://github.com/tangbonze/zmk-config-Keyball39 |
| Rollino (tompi) | low-profile ball mechanics, ceramic ball seats, OpenSCAD | 2x PMW3610 | XIAO nRF52840 | MIT | https://github.com/tompi/rollino |
| VIK (sadekbaroudi) | open pointing-module connector standard, PMW3610-XS module | PMW3610 | any | CERN-OHL-P-2.0 | https://github.com/sadekbaroudi/vik |
| pmw3610-pcb (bullwinkle3000) | reference breakout circuit for the PMW3610 | PMW3610 | any | CERN-OHL-P-2.0 | https://github.com/bullwinkle3000/pmw3610-pcb |
| Keyball (Yowkees) | geometry reference, build guide structure | PMW3360, 34 mm | Pro Micro | GPL-3.0 | https://github.com/Yowkees/keyball |

## 4. Subsystem feasibility

| Subsystem | Finding | Status |
|-----------|---------|--------|
| Controller pin budget | 18 keys as 4 x 5 matrix = 9 GPIO, PMW3610 3-wire SPI + motion = 4 GPIO, total 13. nice!nano v2 offers 21. The XIAO nRF52840 would offer exactly 13 with its NFC pads repurposed, zero headroom. | OK, nice!nano / SuperMini |
| Sensor voltage | PMW3610: VDD 1.7 to 2.1 V (on-board LDO), VDDIO 1.7 to 3.3 V. Direct 3.3 V SPI from the nRF52840, no level shifter. Lens LM18-LSI, 2.4 to 2.9 mm lens-to-surface. | OK |
| Sensor availability | PMW3610DM-SUDU is a JLCPCB extended part (C42442560), also sold as chip + lens kits on AliExpress and as assembled breakouts (Randware, beekeeb, skree). | OK |
| ZMK driver | ZMK main moved to Zephyr 4.1 in December 2025; Zephyr ships an upstream `pixart,pmw3610` input driver (`CONFIG_INPUT_PMW3610`, `res-cpi` 200 to 3200 in 200 steps, `smart-mode`, `force-awake`). No external module needed. badjeff's `pixart,pmw3610-alt` remains a fallback. | OK |
| Split pointing | Mouse support in ZMK core since v0.2 (March 2025); `zmk,input-split` lets a peripheral forward sensor events, so a left-ball or dongle build is configuration only. The ball lives on the central half for r1, as in every shipping design. | OK |
| ZMK Studio | GA since November 2024, proven together with split + pointing on roBa and torabo-tsuki-lp. RAM must be watched on nRF52840. | OK |
| Battery life | PMW3610 0.60 mA tracking, 36 uA rest, 3 uA shutdown. nRF52840 central with BLE host and peripheral link 0.5 to 1.5 mA average. 350 mAh plain half: two to three months. 350 mAh ball half: 4 to 7 weeks of mixed use, days if `force-awake` is enabled. | OK with 350 mAh on both halves |
| Battery placement | One PKCELL LP552035 (350 mAh, 5.7 x 20 x 37 mm) per half under the PCB, below the controller, in a 9 mm well of the case floor; the back of the PCB is free there on both boards. Controller on 2.5 mm sockets, nothing underneath. JST and solder pads exist on every PCB. | OK |
| Two PCBs instead of one reversible board | r1 tried a reversible board and paid for it with three solder jumpers, a sacrificed D0, a mirrored pin map on the left half and a dead 30 mm cutout on the left. r2 generates two boards from the same layout file; the controller wiring is identical, only the thumb row, the FPC connector and the pocket notch differ. Costs one more 5-piece PCB batch (about 15 EUR). | OK |
| Components in the EU | Everything except the sensor chip and the ceramic balls is stocked by 42keebs, keycapsss, splitkb, keeb.supply, Kamami or Mouser DE. Sensor, lens and ceramic balls come from AliExpress or LCSC. | OK |
| PCB fabrication | JLCPCB 2-layer, 1.6 mm, ENIG, 5 pcs main + 5 pcs sensor: roughly 60 to 90 EUR delivered including VAT. | OK |
| Tooling | KiCad 9 (`kicad-cli` for ERC, DRC, gerbers), Ergogen 4 for geometry, OpenSCAD for the cradle, pytest, GitHub Actions for ZMK builds. All free. | OK |

![Pinout diagram of the controller](images/img-pinout-controller.png)

## 4a. Ball size: why 19.05 mm

r1 specified a 25 mm ball through a cutout of the PCB; with the PMW3610 straight below the ball
the ball top ended 23 mm above the PCB, 12 mm above the keycaps, which defeated the low-profile
goal (`issues/mech-ball-height-23mm.md`). Smaller balls were researched on 2026-11-06:

| Finding | Source |
|---------|--------|
| torabo-tsuki LP ships with 25 mm or 19.05 mm POM balls on the same sensor module; the 19.05 mm option is a shipping product, not an experiment | https://github.com/sekigon-gonnoc/torabo-tsuki-lp |
| LiNEA40 uses a 19 mm ball with a PMW3610 directly on the PCB | https://github.com/keyfreaks/LiNEA40 |
| A seven-month review of the 19 mm torabo-tsuki LP reports no tracking problems and keycaps and ball at about the same height | https://www.naenote.net/entry/torabo-tsuki-lp-xs-review |
| PandaKB sells a 19 mm phenolic ball made for split keyboards (TB19, 11.90 USD) | https://pandakb.com/shop/parts/pandakb-tb19-19mm-split-keyboard-trackball/ |
| 3/4 inch (19.05 mm) POM bearing balls cost a few euros per pack of 20 | Amazon, AliExpress ("3/4 inch POM ball", "Delrin ball 19.05") |
| Nothing smaller than 19 mm exists as a keyboard trackball: no bearings, no holders, no tracking reports | search of GitHub, kbd.news, note.com build logs |

Consequences: ball top drops from about 23 to about 17 mm above the PCB top (6 mm above Choc
caps), the cradle shrinks from 34 to about 24 mm above the PCB plane, the sensor stack stays the
same (lens to surface 2.4 mm). Trade-off: less inertia, no long flicks, and about 30 percent more
CPI for the same cursor speed per thumb movement (ZMK `res-cpi` starts at 600 instead of 400).
Two mounting options were compared: the cradle on top of the PCB would have been about 12 mm
taller; a pocket in the case beside the PCB keeps the sensor board on the case floor exactly as
the r1 cutout did, so the pocket won. The 25 mm cradle remains a parameter for a fallback PCB with
a wider notch (`issues/hw-25mm-cradle-fallback.md`).

## 5. Risk register

| Risk | Impact | Likelihood | Mitigation | Ticket |
|------|--------|------------|-----------|--------|
| 19 mm ball surface quality. POM bearing balls are industrial parts; surface finish varies between suppliers and some plastics track badly on optical sensors. | Erratic cursor | Medium | Buy a pack of 3/4 inch POM balls plus the PandaKB TB19 phenolic ball before ordering PCBs and test them on the sensor board. Keep the 25 mm pocket cradle as a fallback. | `issues/hw-19mm-ball-sourcing.md`, `issues/hw-ball-colour-tracking-test.md` |
| Sensor stack height. A Keyball 34-to-25 mm conversion report names the sensor PCB height under the ball, not the ball diameter, as the ergonomic bottleneck; the author went back to 34 mm. | Ball sits too high for a low-profile board | Low since r2 | The sensor board lies on the case floor in a pocket beside the PCB, the ball is 19 mm: ball top 17 mm above the PCB. The cradle is parametric and printed first. Stack math is documented in the trackball module doc. | `issues/hw-sensor-stack-height.md` |
| ZMK main is a moving target (v0.4 not tagged, board names changed to `nice_nano//zmk`). | Firmware stops building | High over time | Pin the ZMK revision in `west.yml`, build on a schedule in CI so breakage shows up early, keep the badjeff driver as a documented fallback. | `issues/infra-ci-firmware.md` |
| FFC pin order between main PCB and sensor PCB (same-side cable, both connectors bottom contact). | Sensor dead or reversed supply | Medium | Pin order on the main PCB is fixed in the design spec; the sensor PCB mirrors or keeps it based on the connector orientation, verified with a physical cable before the order. | `issues/hw-ffc-pin-order-verification.md` |
| Hot-swap socket stiffness on a thin board. | Keys pop out, flex | Low | 1.6 mm FR4, ENIG, kiswitch footprint with both solder and hot-swap pads, case support under the thumb cluster. | `issues/hw-sensor-stack-height.md` (case phase) |
| 19 mm ball sensitivity and inertia. A smaller ball turns more per millimetre of thumb travel and has no flick, so Keyball-style CPI values feel wrong in both directions. | Poor pointer control | High | Default `res-cpi` 600, snipe layer, scroll via input processors, per-axis scaling like the kovalev-org config if the geometry needs it; tune on hardware. | `issues/fw-cpi-tuning-19mm.md` |
| 0.5 mm FPC connectors are the hardest hand-solder step. | Assembly failure | Low | Flip-lock connectors with wide solder tabs, build-guide step with flux and drag soldering, continuity test in the test procedure. | `issues/hw-ffc-pin-order-verification.md` |

## 6. Cost estimate for one keyboard (both halves)

Prices are EU retail including VAT, late 2025. Details and links in [the BOM](03-bom.md).

| Group | EUR |
|-------|-----|
| PCBs (5 left + 5 right + 5 sensor, JLCPCB, ENIG, shipping, import VAT) | 90 |
| 2 x nice!nano v2 (SuperMini: about 20 EUR for two) | 42 |
| Controller sockets, pins | 6 |
| 35 Choc V1 switches | 27 |
| 35 hot-swap sockets | 6 |
| 35 MBK keycaps | 20 |
| Diodes, slide switches, reset buttons, battery connectors, passives | 8 |
| 2 batteries (350 mAh each) | 10 |
| PMW3610 + lens, LDO, FPC connectors, cable | 12 |
| 19.05 mm POM balls (pack) | 5 |
| Ceramic balls, M2 hardware, bumpers | 8 |
| **Total** | **about 240 EUR** (about 220 EUR with SuperMini controllers) |

The spare PCBs allow a second build for roughly 150 EUR.

## 7. License analysis

Keyball's repository carries a blanket GPL-3.0 with no hardware-specific wording; the firmware
files say GPL-2.0-or-later. GPL applied to CAD data is an awkward fit, and deriving PCB files from
it would bind this project to GPL-3.0.

k0d3ball35 therefore takes **no file, footprint, symbol, schematic fragment or copper from Keyball**.
What it takes is the hand geometry: the column stagger ratios and the thumb arc angles, measured
from the published gerbers and re-expressed as parameters in `hardware/layout/k0d3ball35.yaml`.
A key layout is functional information, not a copyrightable expression, and it is reproduced with
different pitch, different switches, different outline and different electronics. Keyball is
credited in `NOTICE` and in the README as the inspiration.

Component libraries and reference circuits were chosen for compatible licenses: kiswitch (MIT and
CC-BY-SA 4.0), marbastlib (CERN-OHL-P-2.0), the bullwinkle3000 PMW3610 breakout (CERN-OHL-P-2.0),
torabo-tsuki-lp (MIT) for the low-profile 25 / 19.05 mm ball mechanics. roBa and Kivipallur (GPL-3.0) were
studied for numbers only.

Resulting licenses:

| Part of the repository | License |
|------------------------|---------|
| `firmware/`, `scripts/`, `tests/`, `docs/`, `README.md` | MIT |
| `hardware/` (KiCad projects, Ergogen source, cradle CAD, gerbers) | CERN-OHL-P-2.0 |

Commercial use is permitted under both. If kits are ever sold, the name should avoid implying an
official Keyball product.

## 8. Decision

Proceed with the design as specified in [the design specification](01-design-spec.md). First
physical step after the design files exist: print the 19 mm pocket cradle, buy the balls and the
sensor, confirm the lens distance, then order PCBs.
