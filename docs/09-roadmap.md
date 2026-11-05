# Roadmap

Tickets referenced here live in `issues/`. Priorities: P0 blocker, P1 must, P2 should, P3 nice.

## r1 (current revision)

Scope: reversible main PCB, PMW3610 sensor PCB, parametric 25 mm cradle, ZMK shield with Studio,
documentation, automated checks. Everything a person needs to order parts, build the two halves and
flash them.

| Item | State | Ticket |
|------|-------|--------|
| Feasibility, design spec, BOM | done | |
| Layout generator and coordinate table | in progress | `hw-layout-generator` |
| Main PCB schematic, routing, DRC, gerbers | in progress | `hw-main-pcb` |
| Sensor PCB | in progress | `hw-sensor-pcb` |
| Cradle 25 mm (34 mm as parameter) | in progress | `mech-cradle` |
| ZMK shield, keymap, CI build | in progress | `fw-zmk-shield`, `infra-ci-firmware` |
| Build guide, firmware guide, fabrication guide | in progress | `doc-build-guide` |
| Verify FFC pin order with a physical cable | open | `hw-ffc-pin-order-verification` |
| Secure 25 mm ball supply | open | `hw-25mm-ball-sourcing` |
| Print cradle, confirm sensor stack height | open | `hw-sensor-stack-height` |
| Tune CPI and scaling for 25 mm | open after first build | `fw-cpi-tuning-25mm` |

## r1.1 - case

Low-profile printed case in the style of the reference build: beige or grey body, flat top,
window for the controller LED, pocket for the 702025 cell on the ball half, cable-free exterior,
room for the cradle flange, bumper recesses. Optional tenting feet. Depends on the final PCB
outline (DXF from the layout generator) and the cradle height.
Tickets: `mech-case-lowprofile`, `mech-case-led-window`, `mech-case-battery-pocket`, `mech-case-tenting`.

## r1.2 - firmware polish

- ZMK Studio layout polish: physical layout from the generator, sensible default keymap for
  German and US layouts, documented layer scheme. `fw-studio-layout`
- Keyball-style scroll behaviour: scroll divider, scroll snap (vertical, horizontal, free) via
  input processors, auto mouse layer timeout tuning. `fw-scroll-snap`
- Battery reporting of the peripheral on the central, sleep timeouts tuned from measured drain.
  `fw-power-tuning`

## r2 candidates

| Item | Why | Ticket |
|------|-----|--------|
| Dongle variant | both halves as peripherals with `zmk,input-split`, lower latency on the host, better battery; needs a third nRF52840 board | `fw-dongle-variant` |
| Left-ball build | mirror build for left-handed pointing; the PCB already has the ball zone on both halves, firmware swaps central and sensor overlays | `fw-left-ball` |
| 34 mm cradle option | if 25 mm balls stay hard to source or the feel is too sensitive; cradle is parametric, PCB cutout stays 30 mm | `mech-cradle-34mm` |
| PAW3222 sensor variant | about half the tracking current of the PMW3610 and a thinner module; needs a second sensor PCB and the sekigon ZMK driver | `hw-paw3222-variant` |
| PCBA order option | JLCPCB assembly of diodes, sockets, connectors and the PMW3610 (C42442560) for people who do not want to solder; adds a position file and BOM export | `infra-pcba-export` |
| Keycap set | 3D printed dished Choc caps with smoothed thumb caps as in the video, printable in two colours | `mech-keycaps` |
| Encoder or display pads | spare pins D0 to D3 and D9 are broken out; a later PCB revision could add footprints | `hw-spare-pin-features` |
| Solder-only PCB variant | thinner build without hot-swap sockets for people who want the lowest possible height | `hw-solder-only-variant` |

## Not planned

RGB lighting (battery), OLED on the halves (battery, height), MX switch support (height).
