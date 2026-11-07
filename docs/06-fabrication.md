# Fabrication

Three boards go to the fab house: the left PCB (18 keys), the right PCB (17 keys, FPC connector,
notch for the ball pocket) and the small PMW3610 sensor PCB. All are plain two-layer
boards. Since r2 the two main boards are different designs; order each as its own 5-piece batch.

## Main PCB order settings (JLCPCB, left and right)

| Setting | Value |
|---------|-------|
| Layers | 2 |
| Dimensions | left about 121.0 x 86.7 mm, right about 117.8 x 80.4 mm (from the gerbers) |
| Quantity | 5 (minimum) of each = 5 keyboards' worth of one side plus spares |
| Material | FR-4, TG 135 or higher |
| Thickness | 1.6 mm (stiffness for the hot-swap sockets; do not go thinner) |
| Copper weight | 1 oz |
| Surface finish | ENIG recommended (flat pads for the 0.5 mm FPC connector and the sockets); lead-free HASL is acceptable |
| Solder mask | green or black, any |
| Silkscreen | white |
| Via covering | tented |
| Remove order number | "specify a location" (the JLCJLCJLCJLC text is not on the board, so choose "yes" if you do not want it) |
| Castellated holes | no |
| Impedance control | no |
| Gold fingers | no |
| Confirm production file | no |

The Edge.Cuts layer carries only the outer outline; there is no internal cutout any more. The
outline is angular with 90 degree inside corners, which the fab's 1 mm router leaves slightly
rounded; that is accepted (`corner_radius: 0` in the layout). The right board's notch is a regular
octagon with 15 mm apothem; JLCPCB mills it without a note.

## Sensor PCB order settings

Same as above except: 26 x 25 mm, 1.6 mm, ENIG strongly preferred (the 16-pin lead-frame sensor and
the 0.5 mm connector), quantity 5. Upload the zip `hardware/sensor-pcb/fab/k0d3ball35-sensor-r1-gerbers.zip` (the loose
files are in `hardware/sensor-pcb/gerbers/`).

Optional assembly: the PMW3610DM-SUDU is JLCPCB part C42442560 (extended part), so economic PCBA can
place the sensor, LDO and capacitors. The lens is clipped on by hand afterwards. For five boards the
extended-part fees roughly double the price; hand assembly is fine for a first spin.

## What the export produces

`scripts/export.sh <half>` (`make gerbers`, both halves; `HALVES=right` for one) writes per half:

| File | Content |
|------|---------|
| `hardware/<half>-pcb/gerbers/*.gbr`, `*.drl`, map files | gerbers (F/B copper, paste, silk, mask, Edge.Cuts), Excellon drill files (PTH and NPTH separate), drill map |
| `hardware/<half>-pcb/k0d3ball35-<half>-gerbers.zip` | the zip to upload |
| `hardware/<half>-pcb/k0d3ball35-<half>.step` | STEP model for the case design |
| `hardware/<half>-pcb/renders/<half>-pcb-top.png`, `-bottom.png` | rendered views |
| `hardware/<half>-pcb/k0d3ball35-<half>-schematic.pdf` | schematic |
| `hardware/<half>-pcb/k0d3ball35-<half>-bom.csv`, `-pos.csv` | BOM and placement file (for PCBA, not needed for a bare board) |

The sensor board has its own `hardware/sensor-pcb/export.sh` with the same outputs.

## Checklist before ordering

- [ ] `make erc` and `make drc` report zero errors for both halves (DRC runs with schematic parity)
- [ ] `make test` green (geometry, netlist, KiCad gates)
- [ ] Open both zips in a gerber viewer (JLCPCB's upload preview is enough): outline closed, no
      internal cutout, the pocket notch on the right board only, five mounting holes per board,
      J1 only on the right board, no missing layers
- [ ] The left board outline is the mirror image of the right one: seen from the top the controller
      block sits at the right-hand edge on the left board and at the left-hand edge on the right
      board; the thumb arcs lean in opposite directions. The two boards are not interchangeable
      (`tests/test_pcb_review.py::test_left_board_is_mirror_of_layout`)
- [ ] Drill files (count them in `hardware/<half>-pcb/gerbers/*.drl` of the current export): per
      key one 3.40 mm and two 1.70 mm NPTH (switch posts) and three 3.05 mm NPTH (socket bosses,
      the reversible footprint has the mirrored third hole), so 18 / 36 / 54 on the left and
      17 / 34 / 51 on the right; 2.20 mm x 5 (case holes); 0.85 mm x 2 (power switch); PTH 1.00 mm
      x 26 (controller and battery pads); 0.40 mm x 3 per key for the diode joiner pads; 0.30 mm
      vias. `tests/test_gerbers.py` counts all of this against the boards. Nothing of 2.20 mm beyond the five case holes: there are no cradle holes
- [ ] Ticket `test-fab-gerber-viewer` closed (independent viewer check)
- [ ] Ticket `hw-gnd-stitching-review` closed (pours and auto-placed vias looked at in KiCad)
- [ ] `make print-check`, both sheets printed at 100 %: the 100 mm and 50 mm calibration bars
      measure exactly, then the board, key grid, controller, battery bay and pocket dimensions
      printed on the sheet (`scripts/gen_print_check.py`, A4 per half). This needs no parts; the
      footprint check against real sockets is step 2b of `hw-main-pcb-review-r1`
- [ ] Ticket `hw-main-pcb-review-r1` closed (manual review of both boards in the KiCad GUI)
- [ ] Ticket `hw-ffc-pin-order-verification` resolved for the sensor board
- [ ] Quantity 5 for all three boards, 1.6 mm, ENIG or HASL as decided

## Cost and lead time

| Item | Approximate cost |
|------|------------------|
| Left or right PCB, 5 pcs, HASL | 10 to 15 EUR each design |
| Left or right PCB, 5 pcs, ENIG | 30 to 40 EUR each design |
| Sensor PCB, 5 pcs | 2 to 5 EUR |
| Shipping to Germany | 15 to 35 EUR depending on service |
| Import VAT | 19 percent on goods plus shipping |

Expect about 80 to 120 EUR for one prototype spin with all three boards in one order. Production
takes 2 to 4 days, shipping 1 to 3 weeks depending on the service.

## Local toolchain

| Tool | Version | Install |
|------|---------|---------|
| KiCad | 10.0.7 | `brew install --cask kicad` (copy the app from the DMG if the cask needs admin rights for the demo files) |
| kicad-cli | bundled | `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` |
| pcbnew Python | bundled | `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3` (used by `scripts/route.py`) |
| freerouting | 2.5.0 jar | from the GitHub releases, path in `FREEROUTING_JAR` |
| Java | OpenJDK 21 or newer | `brew install openjdk`, binary in `JAVA` |
| Python venv | 3.12+ | `uv venv .venv && uv pip install pytest pyyaml shapely ezdxf matplotlib kiutils numpy` |

The pipeline, in order:

```
make layout                   # scripts/gen_layout.py: points-*.json, outline-*.dxf, previews, layout checks (both halves)
scripts/build_board.sh left   # gen_schematic.py + ERC, gen_pcb.py, scripts/route.py, DRC with parity for one half;
scripts/build_board.sh right  # the route/DRC pair is retried up to three times (freerouting is not deterministic)
scripts/export.sh left        # gerbers, drill, zip, STEP, renders, schematic PDF, BOM, position file
scripts/export.sh right
make sch pcb route gerbers    # the same for both halves in one go (HALVES=right for one)
make erc drc                  # the KiCad gates on their own (all schematics and boards)
make test                     # pytest
```

`scripts/route.py --half <half>` runs in four processes (KiCad's Python wrapper misbehaves after a
Specctra import): `prepare` removes unlocked tracks and writes a router copy with 0.05 mm larger
clearances, `dsn` gives duplicate pad numbers unique names, bakes footprint rotations into the pads,
drops the pours (GND is routed as a normal net) and exports the DSN, `route` runs freerouting,
`import` strips the placement block from the SES and imports the tracks, `finish` widens undersized
tracks to their net class, fills the pours, adds GND vias on a 6 mm grid wherever both pours have
copper and removes vias that would only anchor islands. A grid point is skipped when its drill
would come closer to an existing hole than the board's `min_hole_to_hole` (0.25 mm): copper
clearance says nothing about two holes on the same net, and the router does put vias next to GND
pads and on top of grid points (`tests/test_pcb_review.py::test_drills_keep_the_board_minimum_hole_to_hole`).

Design rules: clearance 0.2 mm, tracks 0.25 mm (0.4 mm for RAW and battery, 0.15 mm for the FPC
nets at the 0.5 mm connector), vias 0.6 / 0.3 mm, copper to edge 0.3 mm enforced with a 0.35 mm
keep-out ring, 0.45 mm socket pad bands kept inside the outline. The thumb cluster and the COL2,
COL3, COL4 and ROW3 legs are hand routes in the per-half `manual_routes` of the layout file because
the autorouter does not reach footprints rotated by 10 or 20 degrees (ticket
`hw-freerouting-rotated-footprints`).

Verification commands (replace `left` with `right` for the other board):

```
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --exit-code-violations --severity-error \
  --format json -o build/erc-left.json hardware/left-pcb/k0d3ball35-left.kicad_sch
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc --schematic-parity --exit-code-violations \
  --severity-error --format json -o build/drc-left.json hardware/left-pcb/k0d3ball35-left.kicad_pcb
.venv/bin/pytest -q
```

Remaining DRC warnings are expected: the diode courtyard lies inside the switch courtyard, the
diode joiner holes sit inside the switch courtyard (`pth_inside_courtyard`), and a few silkscreen
labels touch copper under the keycaps.

Everything is generated from `hardware/layout/k0d3ball35.yaml` and `scripts/k0d3/`. Do not edit the
KiCad files by hand; change the generator and re-run, otherwise the next run overwrites your work.

## CI gates

- `tests.yml`: pytest on every push (tests not needing KiCad), ticket index up to date.
- `hardware.yml`: KiCad 10 container runs ERC, DRC with schematic parity and `--exit-code-violations`
  for every schematic and board, exports gerbers and uploads them as artifacts; a second job runs
  the KiCad-marked tests.
- `firmware.yml`: ZMK build of both halves and settings_reset, weekly schedule to catch upstream changes.
