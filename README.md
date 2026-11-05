# k0d3ball36

A wireless, low profile, 36-key split keyboard with an integrated 25 mm trackball.
Keyball-inspired column stagger and thumb arc, Kailh Choc V1 hot-swap switches, a nice!nano v2
on each half, ZMK firmware, and one reversible PCB that serves both halves.

```prompt
Photorealistic product photo, 35 mm lens, soft window light. Two halves of a low profile split
keyboard on a light oak desk next to a closed silver MacBook. Each half has 15 finger keys in a
column-staggered 3x5 grid and three thumb keys fanned in an arc. Keycaps are matte white and light
grey low profile caps, the two inner thumb keys are burnt orange. Cases are warm beige-grey 3D
printed trays, about 12 mm tall, with a slightly taller rounded housing on the right half holding
a glossy white 25 mm trackball at the thumb position. No cables anywhere. Shallow depth of field,
the right half in focus.
```

## Status

| Subsystem | State | Where |
|-----------|-------|-------|
| Design specification | draft r1 | [docs/01-design-spec.md](docs/01-design-spec.md) |
| Layout (Ergogen) | in progress | [hardware/layout](hardware/layout) |
| Main PCB (KiCad) | in progress | [hardware/main-pcb](hardware/main-pcb) |
| Sensor PCB (KiCad) | in progress | [hardware/sensor-pcb](hardware/sensor-pcb) |
| Trackball cradle | in progress | [hardware/trackball-cradle](hardware/trackball-cradle) |
| Firmware (ZMK) | in progress | [firmware/zmk-config](firmware/zmk-config) |
| Case | later phase | [issues/mech-case.md](issues/mech-case.md) |
| Tests and CI | in progress | [tests](tests), [.github/workflows](.github/workflows) |

Open work is tracked as markdown tickets in [issues/](issues/README.md).

## Features

- 36 keys: 3 rows x 5 columns plus 3 thumb keys per half, 18 x 17 mm pitch
- Column stagger and thumb arc derived from the Keyball39 geometry, scaled to Choc spacing
- Kailh Choc V1 switches in hot-swap sockets (the footprint can also be soldered directly)
- 25 mm trackball on the right half, resting on three 2 mm ceramic balls, PMW3610 sensor on a small
  daughterboard connected with a 6-pin flat cable
- Fully wireless: nice!nano v2 (or SuperMini nRF52840) per half, Bluetooth split, LiPo cell with
  the controller's charger, slide power switch, reset button
- One reversible main PCB: the same board is flipped for the left half; the ball zone on the left
  half simply stays empty
- No LEDs, display or encoder on the PCB, to keep the height and the power draw down
- ZMK firmware on a pinned `main` revision with the upstream PMW3610 driver, automatic mouse layer,
  scroll and snipe modes, ZMK Studio
- All geometry generated from one Ergogen file, schematic and tests generated from the same data

## Repository map

```
docs/                 specification, layout, BOM, build guide, firmware, fabrication, testing
hardware/layout/      Ergogen source, generated points and outlines
hardware/main-pcb/    KiCad project of the reversible main PCB, gerbers and renders
hardware/sensor-pcb/  KiCad project of the PMW3610 daughterboard
hardware/lib/         project symbol and footprint libraries
hardware/trackball-cradle/  parametric cradle, STL exports
firmware/zmk-config/  ZMK shield, keymap, build matrix
scripts/              generators and checks (schematic, routing, export, tickets)
tests/                pytest suite incl. KiCad ERC/DRC gates
issues/               markdown tickets and the generated index
```

## Documentation

| Document | Content |
|----------|---------|
| [00 Feasibility](docs/00-feasibility.md) | prior art, risks, licensing, why this design |
| [01 Design specification](docs/01-design-spec.md) | requirements, pin map, matrix, FPC interface, geometry contract |
| [02 Layout](docs/02-layout.md) | key coordinates, stagger derivation, ball zone |
| [03 Bill of materials](docs/03-bom.md) | parts, quantities, sources |
| [04 Build guide](docs/04-build-guide.md) | step by step assembly |
| [05 Firmware](docs/05-firmware.md) | flashing, pairing, tuning, battery |
| [06 Fabrication](docs/06-fabrication.md) | PCB order settings, gerber checklist |
| [07 Testing](docs/07-testing.md) | automated checks and bench procedure |
| [08 Trackball module](docs/08-trackball-module.md) | sensor board, lens distance, cradle |
| [09 Roadmap](docs/09-roadmap.md) | case, dongle, sensor variants |
| [Image prompts](docs/images/PROMPTS.md) | every picture as a generation prompt |

## Quick start

```sh
brew install --cask kicad          # KiCad 10, provides kicad-cli
npm i -g ergogen                   # layout generator
uv venv .venv && uv pip install --python .venv/bin/python pytest pyyaml kiutils numpy
make layout                        # regenerate points, outlines and the unrouted PCB
make erc drc                       # KiCad gates
make test                          # full test suite
```

Firmware is built by GitHub Actions from `firmware/zmk-config`; see
[docs/05-firmware.md](docs/05-firmware.md) for local builds and flashing.

```prompt
Top-down studio render of the right half of a low profile split keyboard, white background, soft
shadows. Bare black PCB with 18 Kailh Choc hot-swap sockets, small SOD-123 diodes next to each key,
a nice!nano controller on low profile sockets at the inner edge with a thin silver LiPo cell visible
underneath, a round 30 mm cutout below the middle columns with a beige printed cradle holding a white
25 mm ball, a tiny flat flex cable running from the cradle to a connector on the PCB. Clean,
technical, product photography style.
```

## Credits

- [Keyball](https://github.com/Yowkees/keyball) by Yowkees: the column stagger, thumb arc and the
  idea of a trackball at the thumb are the design inspiration. No Keyball files are used.
- [torabo-tsuki-lp](https://github.com/sekigon-gonnoc/torabo-tsuki-lp) by sekigon-gonnoc: reference
  for a low profile 25 mm trackball and a sensor module on a flat cable.
- [roBa](https://github.com/kumamuk-git/roBa) by kumamuk: reference for a ZMK trackball split with
  PMW3610.
- [kiswitch](https://github.com/kiswitch/kiswitch) and [marbastlib](https://github.com/ebastler/marbastlib):
  switch, socket and controller footprints.
- [ZMK](https://zmk.dev) and the Zephyr PMW3610 driver.

```prompt
Three quarter view close-up of the trackball housing on the right half: a glossy white 25 mm ball
sitting low in a beige 3D printed cradle, three tiny ceramic balls just visible at the rim, burnt
orange thumb keycap directly in front of it, light grey Choc keycaps behind. Oak desk, soft daylight,
macro lens, shallow depth of field.
```

## License

Firmware, scripts and documentation: [MIT](LICENSE).
Hardware (everything under `hardware/`): [CERN-OHL-P-2.0](LICENSE-HARDWARE).
