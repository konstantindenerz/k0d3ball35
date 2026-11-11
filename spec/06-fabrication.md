# Fabrication

Two boards go to the fab house: the left PCB (18 keys) and the right PCB (17 keys, FPC connector,
notch for the ball pocket). Both are plain two-layer boards. Since r2 they are different designs;
order each as its own 5-piece batch. Since r2.4 the trackball sensor is a bought PAW3222 module,
so there is no third board (`issues/hw-paw3222-variant.md`).

## Main PCB order settings (JLCPCB, left and right)

| Setting | Value |
|---------|-------|
| Layers | 2 |
| Dimensions | about 121.0 x 86.7 mm per half (from the gerbers) |
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

On the two main boards the Edge.Cuts layer carries only the outer outline; there is no internal
cutout. The **sensor** board does have one: a 16.96 x 8.60 mm slot for the PMW3610 body, drawn on
Edge.Cuts by the U1 footprint itself. JLCPCB mills it without a note, but do not be surprised by it
in the preview.

The outline is angular with 90 degree inside corners (`corner_radius: 0` in the layout). There are
13 concave corners per half, and a router cannot cut into a concave corner: a 2 mm end mill leaves
an uncut fillet reaching (sqrt(2) - 1) * 1 mm = **0.41 mm** diagonally into the corner, 0.50 mm with
a 2.4 mm bit. That is accepted for the look, but it eats into two clearances that are worth knowing
about before the first fit:

- the trackball module's insertion path. The squared notch corner at layout (-28, 51) sits 0.707 mm
  diagonally from the cradle housing corner, i.e. the documented 0.5 mm per axis. Subtract the
  fillet and roughly 0.29 mm is left (0.21 mm with a 2.4 mm bit), before the printed housing's own
  elephant-foot adds material on the other side. If the module will not drop into its pocket, this
  corner is why, and a file on the printed housing is the fix.
- the case tray cavity, which offsets the outline by `pcb_clear` = 0.2 mm with mitred corners, i.e.
  0.283 mm diagonally at a concave corner. The real FR4 protrudes further, so expect to break the
  corners of the tray cavity or the board with a file on the first assembly.

The right board's notch is a regular octagon with 15 mm apothem, with the corner towards the keys
squared off; JLCPCB mills it without a note.

## Sensor

Nothing to order from the fab house. Since r2.4 the sensor is the ready-made 14 x 8 mm PixArt
PAW3222 module (sekigon-gonnoc / nogikes-ya), bought as a part and listed in `spec/03-bom.md`
with the other bought parts.

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
      printed on the sheet (`scripts/gen_print_check.py`, A4 per half). This needs no parts, and
      it carries the thumb reach to the ball surface that `mech-thumb-arc-tuning` asks for
- [ ] `make print-plots`, the four part-check sheets printed at 100 %: the real hot-swap socket,
      the MSK-12C02 and the FH12-6S laid on their pads (`scripts/gen_print_plots.py`, A4 per half
      and face, step 2b of `hw-main-pcb-review-r1`). Needs the parts in hand
- [ ] The two sheet families cross-checked against each other: held against a window the outlines
      coincide and the key grid falls on the switch holes
- [ ] Ticket `hw-main-pcb-review-r1` closed (manual review of both boards in the KiCad GUI)
- [ ] Ticket `hw-ffc-pin-order-verification` resolved against the bought sensor module: J1 carries
      the module's own pin order, which only a continuity test on the physical cable can confirm
- [ ] Quantity 5 for both boards, 1.6 mm, ENIG or HASL as decided

## Cost and lead time

| Item | Approximate cost |
|------|------------------|
| Left or right PCB, 5 pcs, HASL | 10 to 15 EUR each design |
| Left or right PCB, 5 pcs, ENIG | 30 to 40 EUR each design |
| Shipping to Germany | 15 to 35 EUR depending on service |
| Import VAT | 19 percent on goods plus shipping |

Expect about 80 to 120 EUR for one prototype spin with both boards in one order. Production
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
copper, and then removes any unlocked GND via whose hole still crowds another hole
(`drop_crowded_ground_vias`).

Hole spacing needs that second pass because nothing else enforces it. The board's
`min_hole_to_hole` is **0.5 mm**, which is JLCPCB's figure rather than KiCad's default, and a grid
point is skipped when its drill would land closer than that to an existing hole. But KiCad's own
`hole_to_hole` rule skips pairs on the *same* net, and the pour ties every stitching via to the
controller's ground pads -- so a via beside a GND pad or another GND via is invisible to DRC. That
is how a 0.3 mm via once ended up 0.498 mm inside a 1.0 mm pad hole
(`issues/hw-main-pcb-review-r1.md`). Freerouting is not told about hole spacing either: `prepare`
only inflates copper clearance for the router copy, so the router's own vias can land too close and
`stitch_ground` cannot move a via it did not place. The removal pass is what closes that gap, and
`tests/test_pcb_review.py::test_drills_keep_the_board_minimum_hole_to_hole` checks the result
net-agnostically. If a violation survives -- a locked via from the layout file against a pad, say --
`finish` refuses to save and names the pair, because that needs a layout change.

Design rules: clearance 0.2 mm, tracks 0.25 mm everywhere except RAW and the battery at 0.4 mm.
The sensor bus is 0.25 mm too since r2.3: a track centred on an FH12 contact still clears the
neighbour by 0.5 - 0.125 - 0.15 = 0.225 mm, so the 0.15 mm of r2.2 only added resistance, vias 0.6 / 0.3 mm, copper to edge 0.3 mm enforced with a 0.35 mm
keep-out ring; the hot-swap socket pads reach 9.8 mm out and `socket_margin` 1.1 keeps them
0.3 mm inside the outline. The thumb cluster and the COL2,
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
