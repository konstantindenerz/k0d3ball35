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

Same as above except: 22 x 25 mm, 1.6 mm, ENIG strongly preferred (the 16-pin lead-frame sensor and
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
- [ ] Drill file: 2.2 mm NPTH x 9 (holes), 3.05 mm NPTH x 54 (socket bosses), 3.4 mm x 18 and 1.7 mm x 36
      (switch posts), 1.0 mm PTH x 24 (controller) plus the small diode and battery holes
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

Make targets, in order:

```
make layout    # points.json, outline.dxf, previews
make sch       # schematic + project file (ERC clean by construction)
make pcb       # unrouted board + footprint library
make route     # freerouting via Specctra DSN/SES, track widths normalised, zones refilled
make erc drc   # kicad-cli gates, JSON reports in build/
make gerbers   # scripts/export.sh
make test      # pytest
```

Everything is generated from `hardware/layout/k0d3ball36.yaml` and `scripts/k0d3/`. Do not edit the
KiCad files by hand; change the generator and re-run, otherwise the next run overwrites your work.

## CI gates

- `tests.yml`: pytest on every push (tests not needing KiCad), ticket index up to date.
- `hardware.yml`: KiCad 10 container runs ERC, DRC with schematic parity and `--exit-code-violations`,
  exports gerbers and uploads them as artifacts; a second job runs the KiCad-marked tests.
- `firmware.yml`: ZMK build of both halves and settings_reset, weekly schedule to catch upstream changes.
