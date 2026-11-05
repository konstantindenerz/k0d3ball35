# Fabrication

Two boards go to the fab house: the reversible main PCB (order 2 per keyboard, the same design serves
both halves) and the small PMW3610 sensor PCB (1 per keyboard). Both are plain two-layer boards.

## Main PCB order settings (JLCPCB)

| Setting | Value |
|---------|-------|
| Layers | 2 |
| Dimensions | about 120.4 x 93.5 mm (from the gerbers) |
| Quantity | 5 (minimum) = 2 keyboards plus spares |
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

The gerber zip contains an Edge.Cuts layer with the outer outline and the 30 mm trackball cutout. JLCPCB
mills both; no extra note is needed.

## Sensor PCB order settings

Same as above except: 26 x 25 mm, 1.6 mm, ENIG strongly preferred (the 16-pin lead-frame sensor and
the 0.5 mm connector), quantity 5. Files in `hardware/sensor-pcb/gerbers/`.

Optional assembly: the PMW3610DM-SUDU is JLCPCB part C42442560 (extended part), so economic PCBA can
place the sensor, LDO and capacitors. The lens is clipped on by hand afterwards. For five boards the
extended-part fees roughly double the price; hand assembly is fine for a first spin.

## What the export produces

`scripts/export.sh` (`make gerbers`) writes:

| File | Content |
|------|---------|
| `hardware/main-pcb/gerbers/*.gbr`, `*.drl`, map files | gerbers (F/B copper, paste, silk, mask, Edge.Cuts), Excellon drill files (PTH and NPTH separate), drill map |
| `hardware/main-pcb/k0d3ball36-gerbers.zip` | the zip to upload |
| `hardware/main-pcb/k0d3ball36.step` | STEP model for the case design |
| `hardware/main-pcb/renders/main-pcb-top.png`, `-bottom.png` | rendered views |
| `hardware/main-pcb/k0d3ball36-schematic.pdf` | schematic |
| `hardware/main-pcb/k0d3ball36-bom.csv`, `-pos.csv` | BOM and placement file (for PCBA, not needed for a bare board) |

The sensor board has its own `hardware/sensor-pcb/export.sh` with the same outputs.

## Checklist before ordering

- [ ] `make erc` and `make drc` report zero errors (DRC runs with schematic parity)
- [ ] `make test` green (geometry, netlist, KiCad gates)
- [ ] Open the zip in a gerber viewer (JLCPCB's upload preview is enough): outline closed, 30 mm cutout
      present, three cradle holes, six mounting holes, no missing layers
- [ ] Drill files (counted from `hardware/main-pcb/gerbers/*.drl` of the current export): NPTH 3.40 mm x 18
      and 1.70 mm x 36 (switch posts), 3.05 mm x 54 (socket bosses), 2.20 mm x 8 (5 case holes + 3 cradle
      holes), 0.85 mm x 2 (power switch); PTH 1.00 mm x 26 (controller and battery pads), 0.40 mm x 54
      (diode and pin-1 joiner pads), 0.30 mm x 132 (vias)
- [ ] Ticket `test-fab-gerber-viewer` closed (independent viewer check)
- [ ] Ticket `hw-gnd-stitching-review` closed (pours and auto-placed vias looked at in KiCad)
- [ ] Ticket `hw-main-pcb-review-r1` closed (manual review in the KiCad GUI)
- [ ] Ticket `hw-ffc-pin-order-verification` resolved for the sensor board
- [ ] Quantity 5 for both boards, 1.6 mm, ENIG or HASL as decided

## Cost and lead time

| Item | Approximate cost |
|------|------------------|
| Main PCB, 5 pcs, HASL | 10 to 15 EUR |
| Main PCB, 5 pcs, ENIG | 30 to 40 EUR |
| Sensor PCB, 5 pcs | 2 to 5 EUR |
| Shipping to Germany | 15 to 35 EUR depending on service |
| Import VAT | 19 percent on goods plus shipping |

Expect about 60 to 90 EUR for one prototype spin with both boards in one order. Production takes 2 to 4
days, shipping 1 to 3 weeks depending on the service.

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
make layout                 # scripts/gen_layout.py: points.json, outline.dxf, previews, layout checks
scripts/build_board.sh      # gen_schematic.py + ERC, gen_pcb.py, scripts/route.py, DRC with parity;
                            # the route/DRC pair is retried up to three times (freerouting is not deterministic)
scripts/export.sh           # gerbers, drill, zip, STEP, renders, schematic PDF, BOM, position file
make erc drc                # the KiCad gates on their own
make test                   # pytest
```

`scripts/route.py` runs in four processes (KiCad's Python wrapper misbehaves after a Specctra import):
`prepare` removes unlocked tracks and writes a router copy with 0.05 mm larger clearances,
`dsn` gives duplicate pad numbers unique names, bakes footprint rotations into the pads, drops the
pours (GND is routed as a normal net) and exports the DSN, `route` runs freerouting, `import` strips the
placement block from the SES and imports the tracks, `finish` widens undersized tracks to their net
class, fills the pours, adds GND vias on a 6 mm grid wherever both pours have copper (56 on the current
board) and removes vias that would only anchor islands.

Design rules: clearance 0.2 mm, tracks 0.25 mm (0.4 mm for RAW and battery, 0.15 mm for the FPC
nets at the 0.5 mm connector), vias 0.6 / 0.3 mm, copper to edge 0.3 mm enforced with a 0.35 mm
keep-out ring, 0.45 mm socket pad bands kept inside the outline. The thumb cluster and the COL3, COL4
and ROW3 legs to the controller are hand routes in `manual_routes` of the layout file because the
autorouter does not reach footprints rotated by 10 or 20 degrees (ticket
`hw-freerouting-rotated-footprints`).

Verification commands:

```
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --exit-code-violations --severity-error \
  --format json -o build/erc.json hardware/main-pcb/k0d3ball36.kicad_sch
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc --schematic-parity --exit-code-violations \
  --severity-error --format json -o build/drc.json hardware/main-pcb/k0d3ball36.kicad_pcb
.venv/bin/pytest -q
```

Remaining DRC warnings are expected: the diode courtyard lies inside the switch courtyard, the
diode joiner holes sit inside the switch courtyard (`pth_inside_courtyard`), and a few silkscreen
labels touch copper under the keycaps.

Everything is generated from `hardware/layout/k0d3ball36.yaml` and `scripts/k0d3/`. Do not edit the
KiCad files by hand; change the generator and re-run, otherwise the next run overwrites your work.

## CI gates

- `tests.yml`: pytest on every push (tests not needing KiCad), ticket index up to date.
- `hardware.yml`: KiCad 10 container runs ERC, DRC with schematic parity and `--exit-code-violations`,
  exports gerbers and uploads them as artifacts; a second job runs the KiCad-marked tests.
- `firmware.yml`: ZMK build of both halves and settings_reset, weekly schedule to catch upstream changes.
