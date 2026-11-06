# Roadmap

Tickets referenced here live in `issues/`. Priorities: P0 blocker, P1 must, P2 should, P3 nice.

## r2 verification before ordering

Do these before paying for anything:

1. Finish the r2 pipeline: both halves generated, routed, ERC/DRC clean, gerbers exported, renders
   in the README. Ticket `hw-two-pcbs-r2`.
2. Independent gerber check: upload `hardware/left-pcb/k0d3ball36-left-gerbers.zip`,
   `hardware/right-pcb/k0d3ball36-right-gerbers.zip` and the sensor zip to the JLCPCB preview or
   open them in gerbv; layers, drills, outlines, the octagonal notch on the right board, no copper
   in the notch. Ticket `test-fab-gerber-viewer`.
3. Manual review in the KiCad GUI with 3D models: socket orientation against a real socket, FH12
   orientation on the right board, MSK12C02 actuator at the inner edge, USB overhang, mounting
   holes, pours and auto-placed GND vias, hand routes of the thumb cluster on both boards. Tickets
   `hw-main-pcb-review-r1`, `hw-gnd-stitching-review`.
4. Cradle test print and sensor fit: print `hardware/trackball-cradle/stl/cradle-19mm-pocket.stl`
   plus the retainer, fit a sensor board (or a 26 x 25 mm dummy) and check the lens gap with a
   feeler gauge; check the cup against a printed copy of the right outline's notch. Tickets
   `hw-sensor-stack-height`, `mech-lm18-lens-outline-measurement`.
5. Ball sourcing and tracking: order a pack of 3/4 inch POM balls (and a PandaKB TB19) and a bag of
   2 mm ZrO2 balls now, test them on the sensor board as soon as it exists. Tickets
   `hw-19mm-ball-sourcing`, `hw-ball-colour-tracking-test`.
6. FFC pin order with a physical cable and both connectors. Ticket `hw-ffc-pin-order-verification`.
7. Then order: `hw-jlcpcb-order-r1`.

## r2 (current revision)

Scope: two main PCBs (left 18 keys, right 17 keys with the FPC connector and the pocket notch),
PMW3610 sensor PCB, parametric cradle for a 19.05 mm ball standing in a case pocket (25 mm as a
parameter), ZMK shield with 35 keys and Studio, documentation, automated checks. Everything a
person needs to order parts, build the two halves and flash them.

| Item | State | Ticket |
|------|-------|--------|
| Feasibility, design spec r2, BOM | done | |
| Layout generator per half, coordinate tables, stepped outline, pocket notch | done | `hw-two-pcbs-r2` |
| Left and right PCB schematic, routing, DRC, gerbers | in progress | `hw-two-pcbs-r2`, `hw-main-pcb-review-r1` |
| Sensor PCB | done (r1, unchanged) | `hw-sensor-pcb-r1` |
| Cradle 19 mm pocket mount (25 mm pocket and r1 cutout as variants) | done, test print pending | `mech-trackball-cradle` |
| ZMK shield with 35 keys, keymap, CI build | in progress | `fw-zmk-shield`, `infra-ci-firmware` |
| Build guide, firmware guide, fabrication guide | written for r2, to be verified on the first build | `doc-build-guide` |
| Case pocket geometry handed to the case phase | specified | `mech-case-ball-pocket` |
| Verify FFC pin order with a physical cable | open | `hw-ffc-pin-order-verification` |
| Secure 19 mm ball supply | open | `hw-19mm-ball-sourcing` |
| Print cradle, confirm sensor stack height | open | `hw-sensor-stack-height` |
| Tune CPI and scaling for 19 mm | open after first build | `fw-cpi-tuning-19mm` |

## r2.1 - case

Boxy, angular printed case in the style of the reference build: flat tray following the stepped
PCB outline, walls flush with the keycap skirts, a raised rectangular controller box at the inner
edge with the LED window, USB-C opening, power switch slot and reset hole, a 32 mm pocket beside
the right PCB for the ball with the sensor board on its floor, room for the 702025 cell in the
controller box of the right half, bumper recesses. Optional tenting feet. Depends on the final PCB
outlines (`outline-left.dxf`, `outline-right.dxf`) and the cradle floor footprint
(`hardware/trackball-cradle/dxf/floor-19mm-pocket.dxf`).
Tickets: `mech-case`, `mech-case-ball-pocket`, `mech-case-ball-dome`.

## r2.2 - firmware polish

- ZMK Studio layout polish: physical layout from the generator, sensible default keymap for
  German and US layouts, documented layer scheme. `fw-physical-layout-exact-coords`
- Keyball-style scroll behaviour: scroll snap (vertical, horizontal, free) via input processors,
  runtime CPI and auto mouse layer timeout keys. `fw-scroll-axis-lock`, `fw-runtime-pointer-settings`,
  `fw-one-handed-scroll-toggle`
- Battery reporting of the peripheral on the central, sleep timeouts tuned from measured drain.
  `fw-battery-drain-measurement`, `fw-split-sleep-wake-check`

## r3 candidates

| Item | Why | Ticket |
|------|-----|--------|
| Rename to k0d3ball35 | the board has 35 keys since r2; folder, shield and library names still say 36 | (lead decision, last step of the r2 plan) |
| Dongle variant | both halves as peripherals with `zmk,input-split`, lower latency on the host, better battery; needs a third nRF52840 board | `fw-input-split-dongle` |
| Left-ball build | mirror build for left-handed pointing; needs a mirrored right PCB with the pocket on the left side, firmware swaps central and sensor overlays | `fw-input-split-dongle` (same mechanism) |
| 25 mm cradle fallback | if 19 mm balls do not track well or feel too light; cradle is parametric, needs a right PCB with a 16.5 mm notch apothem and a 35 mm pocket | `hw-25mm-cradle-fallback` |
| PAW3222 sensor variant | about half the tracking current of the PMW3610 and a thinner module; needs a second sensor PCB and the sekigon ZMK driver | `hw-paw3222-variant` |
| PCBA order option | JLCPCB assembly of diodes, sockets, connectors and the PMW3610 (C42442560) for people who do not want to solder; adds a position file and BOM export | `infra-pcba-export` |
| Keycap set | 3D printed dished Choc caps with smoothed thumb caps as in the video, printable in two colours | `mech-keycaps` |
| Encoder or display pads | spare pins D0 to D3 and D9 are broken out as test pads on both halves; a later PCB revision could add footprints | `hw-spare-pin-features` |
| Solder-only PCB variant | thinner build without hot-swap sockets for people who want the lowest possible height | `hw-solder-only-variant` |

## Not planned

RGB lighting (battery), OLED on the halves (battery, height), MX switch support (height), balls
smaller than 19 mm (no keyboard precedent, no bearings, no tracking data).
