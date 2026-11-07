# Sensor board (PMW3610 daughterboard)

26 x 25 mm, two layer, 1.6 mm FR4. Carries the PixArt PMW3610DM-SUDU laser sensor with its
LM18-LSI lens, a 1.8 V regulator and a 6-pin 0.5 mm FPC connector to the main PCB.
Design notes, stack-up and the FFC orientation rule are in `spec/08-trackball-module.md`.

## Files

| Path | Content |
|------|---------|
| `generate.py` | single source of truth: parts, nets, placement; writes schematic, PCB and libraries |
| `export.sh` | ERC/DRC gates, gerbers, drill, pick-and-place, BOM, renders, STEP |
| `k0d3ball35-sensor.kicad_pro/.kicad_sch/.kicad_pcb` | generated KiCad 10 project (committed so it can be opened directly) |
| `gerbers/`, `fab/` | JLCPCB-ready outputs (`fab/*-gerbers.zip`, `*-bom.csv`, `*-cpl-*.csv`) |
| `renders/` | schematic PDF/SVG, PCB renders, STEP model for the cradle design |
| `build/` | scratch (DSN/SES, reports), ignored by git |

## Regenerate

```sh
# Python bundled with KiCad 10 (provides pcbnew); freerouting jar in build/ or $FREEROUTING_JAR
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 generate.py all
./export.sh
```

`generate.py all` writes libraries, schematic and an unrouted PCB, autoroutes it with freerouting,
adds the ground pours and re-runs ERC and DRC (with schematic parity) until the result is clean.
`export.sh` refuses to export when ERC or DRC report errors.

## Ordering

JLCPCB: 2 layer, 1.6 mm, any colour, ENIG recommended (flat pads under the 0.5 mm connector),
"remove order number: specify location" not needed. Upload `fab/k0d3ball35-sensor-r1-gerbers.zip`.
For assembly use the BOM and the top-side CPL; the sensor (U1) is a through-hole part on the
bottom side and is soldered by hand together with the lens.
