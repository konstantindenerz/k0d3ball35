#!/usr/bin/env bash
# Export fabrication and documentation outputs for the sensor board (KiCad 10 kicad-cli).
set -euo pipefail
cd "$(dirname "$0")"
K="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
B=k0d3ball36-sensor.kicad_pcb
S=k0d3ball36-sensor.kicad_sch
REV=r1
rm -rf gerbers renders fab build/erc.rpt build/drc.rpt
mkdir -p gerbers renders fab build
"$K" sch erc --exit-code-violations --severity-error --format report -o build/erc.rpt "$S"
"$K" pcb drc --schematic-parity --exit-code-violations --severity-error --format report -o build/drc.rpt "$B"
"$K" pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --no-x2 --no-netlist --use-drill-file-origin -o gerbers/ "$B"
"$K" pcb export drill --format excellon --excellon-units mm --excellon-zeros-format decimal \
  --excellon-separate-th --generate-map --map-format gerberx2 -o gerbers/ "$B"
(cd gerbers && zip -q -r "../fab/k0d3ball36-sensor-${REV}-gerbers.zip" .)
"$K" pcb export pos --format csv --units mm --side front --use-drill-file-origin --exclude-dnp \
  -o "fab/k0d3ball36-sensor-${REV}-cpl-top.csv" "$B"
"$K" pcb export pos --format csv --units mm --side back --use-drill-file-origin \
  -o "fab/k0d3ball36-sensor-${REV}-cpl-bottom.csv" "$B"
"$K" sch export bom --fields 'Reference,Value,Footprint,LCSC,Note,${QUANTITY}' \
  --labels 'Designator,Value,Footprint,LCSC,Description,Quantity' --group-by 'Value,Footprint,LCSC' \
  --exclude-dnp -o "fab/k0d3ball36-sensor-${REV}-bom.csv" "$S"
"$K" sch export pdf -o renders/k0d3ball36-sensor-schematic.pdf "$S"
"$K" sch export svg -o renders/ "$S"
"$K" pcb render --side top --quality high --background opaque --width 1600 --height 1600 \
  -o renders/k0d3ball36-sensor-top.png "$B"
"$K" pcb render --side bottom --quality high --background opaque --width 1600 --height 1600 \
  -o renders/k0d3ball36-sensor-bottom.png "$B"
"$K" pcb export step --subst-models --include-tracks --include-zones -o renders/k0d3ball36-sensor.step "$B"
"$K" pcb export svg --layers F.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts --page-size-mode 2 \
  --exclude-drawing-sheet -o renders/k0d3ball36-sensor-layers.svg "$B"
echo "sensor board exports complete"
