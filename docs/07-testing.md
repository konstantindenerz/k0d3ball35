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
| `tests/test_kicad_gates.py` | `kicad-cli sch erc` and `kicad-cli pcb drc --schematic-parity` report zero errors for the main and sensor boards; reports are written to `build/*.json` |
| `tests/test_geometry.py` | 36 keys, 18 x 17 pitch, stagger values per spec, no footprint overlap, ball zone clearance, left equals mirrored right |
| `tests/test_netlist.py` | each switch has exactly one diode, 18 unique matrix cells, no shorted rows or columns, controller pins match the spec table, FPC connector nets match between main and sensor PCB |
| `tests/test_bom.py` | BOM quantities match placed footprints, every BOM line has a source |

The geometry, netlist and BOM tests are added together with the generators they verify.

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
| 1.6 FPC pins | Continuity from controller pads D15, D16, D10, D14, VCC, GND to connector contacts 3, 4, 5, 6, 1, 2 | one beep each, in that order |

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
| 3.1 Keys | Open a key tester page or ZMK Studio, press every key | every key registers once, correct position in the layout picture |
| 3.2 Rollover | Hold three keys in a row and press a fourth in another column | fourth key registers, no phantom key |
| 3.3 Split | Pair both halves, press keys on the peripheral | keys arrive through the central |

### 4. Sensor

| Step | How | Expected |
|------|-----|----------|
| 4.1 Product ID | Build the right half with `CONFIG_LOG=y`, `CONFIG_INPUT_LOG_LEVEL_DBG=y` and `CONFIG_ZMK_USB_LOGGING=y`, open the serial console | the pmw3610 driver logs a successful init (product id 0x3e) and no SPI errors |
| 4.2 Motion | Move the ball by hand | cursor moves, direction matches finger movement; if an axis is inverted set `invert-x` / `invert-y` |
| 4.3 Idle current | Leave the ball still for 10 s, then move it | first movement wakes the sensor within a few milliseconds, no visible lag |
| 4.4 CPI sanity | Roll the ball by one full turn along x (circumference 78.5 mm at 25 mm) | cursor travel in pixels roughly equals CPI x 3.09; adjust `res-cpi` to taste |

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
