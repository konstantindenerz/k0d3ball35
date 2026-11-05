# Roadmap

Tickets referenced here live in `issues/`. Priorities: P0 blocker, P1 must, P2 should, P3 nice.

## r1 verification before ordering

Do these before paying for anything:

1. Independent gerber check: upload `hardware/main-pcb/k0d3ball36-gerbers.zip` and the sensor zip to
   the JLCPCB preview or open them in gerbv; layers, drills, outline and the 30 mm cutout. Ticket
   `test-fab-gerber-viewer`.
2. Manual review in the KiCad GUI with 3D models: socket orientation against a real socket, FH12
   orientation, MSK12C02 actuator at the inner edge, jumper silkscreen, USB overhang, mounting and
   cradle holes, pours and auto-placed GND vias. Tickets `hw-main-pcb-review-r1`,
   `hw-gnd-stitching-review`.
3. Cradle test print and sensor fit: print `hardware/trackball-cradle/stl/cradle-25mm.stl` plus the
   retainer, fit a sensor board (or a 26 x 25 mm dummy) and check the lens gap with a feeler gauge.
   Tickets `hw-sensor-stack-height`, `mech-lm18-lens-outline-measurement`.
4. Ball sourcing and tracking: order two 25 mm balls and a bag of 2 mm ZrO2 balls now, test the balls
   on the sensor board as soon as it exists. Tickets `hw-25mm-ball-sourcing`, `hw-ball-colour-tracking-test`.
5. FFC pin order with a physical cable and both connectors. Ticket `hw-ffc-pin-order-verification`.
6. Then order: `hw-jlcpcb-order-r1`.

## r1 (current revision)

Scope: reversible main PCB, PMW3610 sensor PCB, parametric 25 mm cradle, ZMK shield with Studio,
documentation, automated checks. Everything a person needs to order parts, build the two halves and
flash them.

| Item | State | Ticket |
|------|-------|--------|
| Feasibility, design spec, BOM | done | |
| Layout generator and coordinate table | done | `hw-main-pcb-r1` |
| Main PCB schematic, routing, DRC, gerbers | done, review pending | `hw-main-pcb-r1`, `hw-main-pcb-review-r1` |
| Sensor PCB | done | `hw-sensor-pcb-r1` |
| Cradle 25 mm (34 mm as parameter) | done, test print pending | `mech-trackball-cradle` |
| ZMK shield, keymap, CI build | builds | `fw-zmk-shield`, `infra-ci-firmware` |
| Build guide, firmware guide, fabrication guide | written, to be verified on the first build | `doc-build-guide` |
| Verify FFC pin order with a physical cable | open | `hw-ffc-pin-order-verification` |
| Secure 25 mm ball supply | open | `hw-25mm-ball-sourcing` |
| Print cradle, confirm sensor stack height | open | `hw-sensor-stack-height` |
| Tune CPI and scaling for 25 mm | open after first build | `fw-cpi-tuning-25mm` |

## r1.1 - case

Low-profile printed case in the style of the reference build: beige or grey body, flat top,
window for the controller LED, pocket for the 702025 cell on the ball half, cable-free exterior,
room for the cradle flange, bumper recesses. Optional tenting feet. Depends on the final PCB
outline (DXF from the layout generator) and the cradle height.
Tickets: `mech-case`, `mech-case-ball-dome`.

## r1.2 - firmware polish

- ZMK Studio layout polish: physical layout from the generator, sensible default keymap for
  German and US layouts, documented layer scheme. `fw-physical-layout-exact-coords`
- Keyball-style scroll behaviour: scroll snap (vertical, horizontal, free) via input processors,
  runtime CPI and auto mouse layer timeout keys. `fw-scroll-axis-lock`, `fw-runtime-pointer-settings`,
  `fw-one-handed-scroll-toggle`
- Battery reporting of the peripheral on the central, sleep timeouts tuned from measured drain.
  `fw-battery-drain-measurement`, `fw-split-sleep-wake-check`

## r2 candidates

| Item | Why | Ticket |
|------|-----|--------|
| Dongle variant | both halves as peripherals with `zmk,input-split`, lower latency on the host, better battery; needs a third nRF52840 board | `fw-input-split-dongle` |
| Left-ball build | mirror build for left-handed pointing; the PCB already has the ball zone on both halves, firmware swaps central and sensor overlays | `fw-left-half-pin-mirror` (pin set prepared) |
| 34 mm cradle option | if 25 mm balls stay hard to source or the feel is too sensitive; cradle is parametric, PCB cutout stays 30 mm | `hw-34mm-cradle-option` |
| PAW3222 sensor variant | about half the tracking current of the PMW3610 and a thinner module; needs a second sensor PCB and the sekigon ZMK driver | `hw-paw3222-variant` |
| PCBA order option | JLCPCB assembly of diodes, sockets, connectors and the PMW3610 (C42442560) for people who do not want to solder; adds a position file and BOM export | `infra-pcba-export` |
| Keycap set | 3D printed dished Choc caps with smoothed thumb caps as in the video, printable in two colours | `mech-keycaps` |
| Encoder or display pads | spare pins D0 to D3 and D9 are broken out; a later PCB revision could add footprints | `hw-spare-pin-features` |
| Solder-only PCB variant | thinner build without hot-swap sockets for people who want the lowest possible height | `hw-solder-only-variant` |

## Not planned

RGB lighting (battery), OLED on the halves (battery, height), MX switch support (height).
