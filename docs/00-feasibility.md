# Feasibility study

Status: complete (2026-11-05). Verdict: **GO.**

Every subsystem of k0d3ball36 has working, open-source prior art. The firmware stack needs no
third-party driver module any more. The two genuine risks are mechanical and logistical, not
electrical: securing a repeatable supply of 25 mm balls, and keeping the sensor stack under the ball
low enough for a low-profile board.

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

That is exactly what k0d3ball36 does: it is a from-scratch low-profile, wireless-first design that
keeps the Keyball39 hand geometry and replaces everything else.

## 2. What Keyball39 actually is, and how k0d3ball36 differs

Measured from the published design data of the Keyball repository (gerbers, KiCad 5 sources,
netlist). Nothing from that repository is included here; see section 7.

| Aspect | Keyball39 (Yowkees) | k0d3ball36 |
|--------|---------------------|------------|
| Keys | 39 (21 no-ball half, 18 ball half) | 36 (18 + 18, identical halves) |
| Switch standard | MX, 19.05 mm pitch, 5 thumb positions MX/Choc dual | Choc V1, 18 x 17 mm pitch, all positions hot-swap |
| Column stagger | 11.70 / 4.70 / 0 / 2.50 / 5.00 mm (pinky to inner) | same proportions scaled to 17 mm rows |
| Thumb cluster | 3-key arc, 21.63 mm pitch, 0 / 10 / 20 degrees | same arc, 19.5 mm pitch, same angles |
| Controller | Pro Micro (ATmega32U4) or RP2040 Pro Micro, wired | nice!nano v2 / SuperMini (nRF52840), BLE |
| Half interconnect | TRRS cable, half-duplex serial | Bluetooth split (ZMK) |
| Sensor | PMW3360 on a 5 V daughterboard with 1.9 V LDO and two level shifters | PMW3610 on a 3.3 V daughterboard, 1.8 V LDO, no level shifting |
| Sensor interface | 7-pin press-fit connector with 8 solder jumpers | 6-pin 0.5 mm FPC |
| Ball | 34 mm, 3 glued 2 mm ceramic balls, injection-moulded holder (not published) | 25 mm, 3 x 2 mm ZrO2 balls, parametric printed cradle (published) |
| Power | USB | 1S LiPo per half, controller charger, slide switch |
| PCB | two different PCBs per half, top FR4 plate, acrylic layers | one reversible main PCB, one sensor PCB |
| Extras | OLED, SK6812MINI-E RGB, reset, handedness jumper | none (reset only) |
| Firmware | QMK 0.22.14 out-of-tree, Remap / Keyball Link | ZMK main, ZMK Studio |
| License | GPL-3.0 (blanket), firmware GPL-2.0-or-later | MIT (software, docs) + CERN-OHL-P-2.0 (hardware) |
| Published | PCB sources and gerbers yes; sensor board and ball holder no | everything |

![Top view of both halves with the key grid](images/img-layout-top.png)

## 3. Prior art

| Project | What it contributes | Sensor / ball | MCU | License | Source |
|---------|---------------------|---------------|-----|---------|--------|
| torabo-tsuki-lp (sekigon-gonnoc) | low-profile wireless split with a **25 mm** ball, FPC sensor module, full KiCad | PAW3222, 25 mm | BMP Boost | MIT | https://github.com/sekigon-gonnoc/torabo-tsuki-lp |
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
| Battery life | PMW3610 0.60 mA tracking, 36 uA rest, 3 uA shutdown. nRF52840 central with BLE host and peripheral link 0.5 to 1.5 mA average. 110 mAh plain half: weeks. 300 mAh ball half: 3 to 6 weeks of mixed use, days if `force-awake` is enabled. | OK with 300 mAh on the ball half |
| Battery placement | 301230 (3.3 mm thick) fits under a controller on 1.27 mm sockets; 702025 (6.7 mm) needs a case pocket. Both pads exist on every PCB. | OK |
| Reversible PCB | Standard for 36-key splits. The ball zone (cutout plus three flange holes) is present on both halves and simply unused on the left. The sensor sits on its own board, so no component breaks the mirror. | OK |
| Components in the EU | Everything except the sensor chip and the ceramic balls is stocked by 42keebs, keycapsss, splitkb, keeb.supply, Kamami or Mouser DE. Sensor, lens and ceramic balls come from AliExpress or LCSC. | OK |
| PCB fabrication | JLCPCB 2-layer, 1.6 mm, ENIG, 5 pcs main + 5 pcs sensor: roughly 60 to 90 EUR delivered including VAT. | OK |
| Tooling | KiCad 9 (`kicad-cli` for ERC, DRC, gerbers), Ergogen 4 for geometry, OpenSCAD for the cradle, pytest, GitHub Actions for ZMK builds. All free. | OK |

![Pinout diagram of the controller](images/img-pinout-controller.png)

## 5. Risk register

| Risk | Impact | Likelihood | Mitigation | Ticket |
|------|--------|------------|-----------|--------|
| 25 mm ball supply. Perixx PERIPRO-305 (German company, about 12 EUR) is often sold out in the EU store; Elecom M-B25 is a Japanese import; AliExpress 25 mm balls vary in surface quality. | Build cannot be finished | Medium | Order two balls before ordering PCBs. Publish the cradle in 25 mm and 34 mm so a 34 mm ball is a drop-in. Document the AliExpress ceramic bearing ball option used in the video. | `issues/hw-25mm-ball-sourcing.md` |
| Sensor stack height. A Keyball 34-to-25 mm conversion report names the sensor PCB height under the ball, not the ball diameter, as the ergonomic bottleneck; the author went back to 34 mm. | Ball sits too high for a low-profile board | Medium | The cradle is parametric and printed first; the main PCB has a 30 mm cutout so the sensor board can sit below PCB level. Stack math is documented in the trackball module doc. | `issues/hw-sensor-stack-height.md` |
| ZMK main is a moving target (v0.4 not tagged, board names changed to `nice_nano//zmk`). | Firmware stops building | High over time | Pin the ZMK revision in `west.yml`, build on a schedule in CI so breakage shows up early, keep the badjeff driver as a documented fallback. | `issues/infra-ci-firmware.md` |
| FFC pin order between main PCB and sensor PCB (same-side cable, both connectors bottom contact). | Sensor dead or reversed supply | Medium | Pin order on the main PCB is fixed in the design spec; the sensor PCB mirrors or keeps it based on the connector orientation, verified with a physical cable before the order. | `issues/hw-ffc-pin-order-verification.md` |
| Hot-swap socket stiffness on a thin board. | Keys pop out, flex | Low | 1.6 mm FR4, ENIG, kiswitch footprint with both solder and hot-swap pads, case support under the thumb cluster. | `issues/hw-sensor-stack-height.md` (case phase) |
| 25 mm ball sensitivity. A smaller ball turns more per millimetre of thumb travel, so Keyball-style CPI values feel twitchy. | Poor pointer control | High | Default `res-cpi` 400, snipe layer at 200, scroll via input processors, per-axis scaling like the kovalev-org config if the geometry needs it. | `issues/fw-cpi-tuning-25mm.md` |
| 0.5 mm FPC connectors are the hardest hand-solder step. | Assembly failure | Low | Flip-lock connectors with wide solder tabs, build-guide step with flux and drag soldering, continuity test in the test procedure. | `issues/hw-ffc-pin-order-verification.md` |

## 6. Cost estimate for one keyboard (both halves)

Prices are EU retail including VAT, late 2025. Details and links in [the BOM](03-bom.md).

| Group | EUR |
|-------|-----|
| PCBs (5 main + 5 sensor, JLCPCB, ENIG, shipping, import VAT) | 75 |
| 2 x nice!nano v2 (SuperMini: about 20 EUR for two) | 42 |
| Controller sockets, pins | 6 |
| 36 Choc V1 switches | 28 |
| 36 hot-swap sockets | 6 |
| 36 MBK keycaps | 20 |
| Diodes, slide switches, reset buttons, battery connectors, passives | 8 |
| 2 batteries (110 + 300 mAh) | 12 |
| PMW3610 + lens, LDO, FPC connectors, cable | 12 |
| 25 mm ball | 12 |
| Ceramic balls, M2 hardware, bumpers | 8 |
| **Total** | **about 230 EUR** (about 210 EUR with SuperMini controllers) |

The spare PCBs allow a second build for roughly 150 EUR.

## 7. License analysis

Keyball's repository carries a blanket GPL-3.0 with no hardware-specific wording; the firmware
files say GPL-2.0-or-later. GPL applied to CAD data is an awkward fit, and deriving PCB files from
it would bind this project to GPL-3.0.

k0d3ball36 therefore takes **no file, footprint, symbol, schematic fragment or copper from Keyball**.
What it takes is the hand geometry: the column stagger ratios and the thumb arc angles, measured
from the published gerbers and re-expressed as parameters in `hardware/layout/k0d3ball36.yaml`.
A key layout is functional information, not a copyrightable expression, and it is reproduced with
different pitch, different switches, different outline and different electronics. Keyball is
credited in `NOTICE` and in the README as the inspiration.

Component libraries and reference circuits were chosen for compatible licenses: kiswitch (MIT and
CC-BY-SA 4.0), marbastlib (CERN-OHL-P-2.0), the bullwinkle3000 PMW3610 breakout (CERN-OHL-P-2.0),
torabo-tsuki-lp (MIT) for the low-profile 25 mm mechanics. roBa and Kivipallur (GPL-3.0) were
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
physical step after the design files exist: print the 25 mm cradle, buy the balls and the sensor,
confirm the lens distance, then order PCBs.
