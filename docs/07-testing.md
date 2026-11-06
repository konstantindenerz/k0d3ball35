# Testing

Two kinds of checks exist: automated tests that run on every push, and a bench procedure a
builder follows on real hardware. Both are meant to catch the mistakes that are expensive in a
keyboard project: a wrong pin, a reversed diode, a mirrored connector, a dead sensor.

## Automated tests

Run everything with `make test` (equivalent to `.venv/bin/pytest -q`). Tests that need files
another step has not produced yet skip with a reason instead of failing.

| Test file | What it checks |
|-----------|----------------|
| `tests/test_issues.py` | every ticket in `issues/` has valid frontmatter (type, priority, status, area, date), the file name matches its area, and `issues/README.md` equals the rendered index |
| `tests/test_docs.py` | every relative markdown link resolves; every `docs/NN-*.md` named in the spec or README exists or is ticketed; no tool attribution strings; markdown is English (German marker heuristic); no image references without a file (pictures are prompt blocks) |
| `tests/test_license.py` | MIT and CERN-OHL-P-2.0 texts present; every script and test carries an SPDX header |
| `tests/test_kicad_gates.py` | `kicad-cli sch erc` and `kicad-cli pcb drc --schematic-parity` report zero errors for the left, right and sensor boards; reports are written to `build/*.json` |
| `tests/test_geometry.py` | 18 keys left / 17 right, 18 x 17 pitch, stagger values per spec, thumb arc, no keycap overlap, cradle circle clear of caps and of the outline outside the notch (right only), points files up to date |
| `tests/test_netlist.py` | each switch has exactly one diode, unique matrix cells per half (row 3 cols 2-4 left, 2-3 right), controller holes match the single spec pin table on both halves, FPC only on the right with the spec pin order, no jumpers, power path, unique references |
| `tests/test_footprints.py` | pad sets of the project footprints, no overlapping pads of different numbers, hole positions of the Choc footprint, controller 2x12 geometry, library files parse |
| `tests/test_firmware_pins.py` | devicetree pins of both overlays equal the single spec table, 35 bindings per layer, transform row 3 per half |
| `tests/test_cradle.py` | pocket cradle renders in OpenSCAD, STL watertight, stands on the floor and stays inside the 15 mm notch apothem, 19 mm default matches the layout, stack heights within the datasheet window |
| `tests/test_bom.py` | BOM quantities cover the parts placed on both PCBs (35 switches and diodes, one FPC connector), every BOM line has a source; section 6 carries every LCSC code of the sensor fab BOM with at least the exported quantity |
| `tests/test_pcb_review.py` | automated part of the board review: socket pads versus the kiswitch reference, FH12 on the right only, controller hole nets and labels, USB overhang, battery bay, mounting holes, power switch at the inner edge, diode orientation, silkscreen, test pads, edge clearance, octagonal notch, filled GND pours without slivers or islands |
| `tests/test_gerbers.py` | independent parse of the three gerber zips with gerbonara: file set and naming, two copper layers, extents, closed outlines, drill hit counts against the boards, the notch, battery bay silkscreen, no copper outside the outline; renders `build/gerber-check/*.png` for a visual pass |
| `tests/test_ffc_pin_order.py` | the sensor board's FPC pin order is the mirror of the right PCB's for a same-side-contact (type A) cable, both connectors bottom contact on the component side |
| `tests/test_sensor_pcb_vs_cradle.py` | sensor board against the cradle: outline, hole spacing, optical centre, sensor cutout and lens envelope (LM18-LSI datasheet) inside the cavity, parts on the floor side below the component gap, connector in front of the cable slot; OpenSCAD render when available |
| `tests/test_firmware_build_config.py` | firmware build configuration: the GitHub workflow against ZMK's reusable build-user-config, the build matrix against the shield files, the pinned ZMK revision, Kconfig symbols and the devicetree/keymap references a build would resolve |
| `tests/test_case.py` | case geometry, generated data, renders |

Current state: run `.venv/bin/pytest -q`; the KiCad gates run against the generated left, right and sensor PCBs and skip while a board file does not exist yet.

### Hardware pipeline checks

`scripts/build_board.sh <half>` runs the generators, ERC, the autorouter and DRC with schematic parity for one board and retries the route/DRC step until it is clean; a pre-route DRC catches collisions of the hand routes in the half's `manual_routes`. `scripts/export.sh <half>` refuses nothing by itself, so always run the DRC first. The exact commands are listed in [docs/06-fabrication.md](06-fabrication.md).

### Where the gates run

| Workflow | Runner | Runs |
|----------|--------|------|
| `.github/workflows/tests.yml` | ubuntu, uv | everything except KiCad gates, plus `scripts/issues.py --diff` |
| `.github/workflows/hardware.yml` | `ghcr.io/kicad/kicad:10.0` container | ERC, DRC, gerber export, KiCad gate tests, artifacts |
| `.github/workflows/firmware.yml` | ZMK build container | left, right and settings_reset firmware for `nice_nano//zmk` |

KiCad is pinned to major version 10 in CI. Locally the Makefile uses the app bundle path
`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`; override with `KICAD_CLI=`.

## Bench procedure

Do these steps in order after soldering a half. Expected results are in the right column.
A multimeter with continuity beep and diode mode is enough; a USB-C cable and a computer with a
serial terminal help for the sensor step.

### 1. Before the controller is socketed

| Step | How | Expected |
|------|-----|----------|
| 1.1 Shorts | Continuity between every pair of controller pads RAW, VCC, GND | no beep between any pair |
| 1.2 Battery switch | Continuity from battery + pad to RAW with the slide switch in both positions | beep in ON only |
| 1.3 Columns | Continuity from the column pad (D4 .. D8) to the socket pin of each key in that column (the pin not connected to a diode) | beep for every key of the column, no beep to other columns |
| 1.4 Diodes | Diode mode, red probe on the row pad (D21 .. D18), black probe on the socket's diode-side pin | 0.5 to 0.7 V forward drop for every key in the row; open the other way round |
| 1.5 Reset | Continuity RST to GND while pressing the button | beep only while pressed |
| 1.6 FPC pins (right half) | Continuity from controller pads D15, D16, D10, D14, VCC, GND to connector contacts 3, 4, 5, 6, 1, 2 | one beep each, in that order |
| 1.7 Test pads (left half) | Continuity from controller pads D15, D16, D10, D14 to the four extra test pads | one beep each; these pins go nowhere else on the left |

A reversed diode shows an open circuit in 1.4 in both directions on one key, or a forward drop in
the wrong direction. Fix it before continuing; in a matrix one reversed diode makes two keys
misbehave.

### 2. Controller and power

| Step | How | Expected |
|------|-----|----------|
| 2.1 Flash | Double tap reset, copy the UF2 for this half | drive ejects, blue LED blinks once |
| 2.2 Charging | Connect the battery, switch ON, plug USB | controller charge LED on, off when full (typical cell charges in about 1 h at 100 mA) |
| 2.3 Battery level | Pair the right half over Bluetooth, read the battery level in the host's device info or ZMK Studio | plausible percentage, not 0 or 100 for a half-full cell |

### 3. Matrix

| Step | How | Expected |
|------|-----|----------|
| 3.1 Keys | Open a key tester page or ZMK Studio, press every key (18 left, 17 right) | every key registers once, correct position in the layout picture |
| 3.2 Rollover | Hold three keys in a row and press a fourth in another column | fourth key registers, no phantom key |
| 3.3 Split | Pair both halves, press keys on the peripheral | keys arrive through the central |

### 4. Sensor

| Step | How | Expected |
|------|-----|----------|
| 4.1 Product ID | Build the right half with `CONFIG_LOG=y`, `CONFIG_INPUT_LOG_LEVEL_DBG=y` and `CONFIG_ZMK_USB_LOGGING=y`, open the serial console | the pmw3610 driver logs a successful init (product id 0x3e) and no SPI errors |
| 4.2 Motion | Move the ball by hand | cursor moves, direction matches finger movement; if an axis is inverted set `invert-x` / `invert-y` |
| 4.3 Idle current | Leave the ball still for 10 s, then move it | first movement wakes the sensor within a few milliseconds, no visible lag |
| 4.4 CPI sanity | Roll the ball by one full turn along x (circumference 59.8 mm at 19.05 mm) | cursor travel in pixels roughly equals CPI x 2.36; adjust `res-cpi` to taste |

If 4.1 shows a product id of 0x00 or 0xff, check the FPC cable orientation (ticket
`hw-ffc-pin-order-verification`) and the 1.8 V rail on the sensor board.

### 5. Bluetooth and sleep

| Step | How | Expected |
|------|-----|----------|
| 5.1 Profiles | Pair with a second host, switch profiles with the system layer | both hosts work, switching takes under 2 s |
| 5.2 Sleep | Leave the board idle past the deep sleep timeout, press a key | wakes within a second; trackball does not wake it (expected, wake is on keys) |
| 5.3 Current | Optional: USB current meter on the trackball half in idle and while tracking | idle below 1 mA, tracking a few mA |

## Reporting

A failed bench step becomes a ticket in `issues/` (type `bug`, area `hw` or `fw`) with the step
number, the measured value and the serial of the PCB. See the convention in
[docs/01-design-spec.md](01-design-spec.md), section 7.
