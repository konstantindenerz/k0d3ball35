#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Export fabrication files for the main PCB: gerbers + drill (JLCPCB naming), zip, STEP, renders, BOM, position file.
set -euo pipefail
cd "$(dirname "$0")/.."
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
BOARD=hardware/main-pcb/k0d3ball36.kicad_pcb
SCH=hardware/main-pcb/k0d3ball36.kicad_sch
OUT=hardware/main-pcb/gerbers
REN=hardware/main-pcb/renders
rm -rf "$OUT"; mkdir -p "$OUT" "$REN" build
"$KICAD_CLI" pcb export gerbers --layers "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" \
  --subtract-soldermask --no-protel-ext -o "$OUT/" "$BOARD" >/dev/null
"$KICAD_CLI" pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 -o "$OUT/" "$BOARD" >/dev/null
(cd "$OUT" && rm -f ../k0d3ball36-gerbers.zip && zip -q ../k0d3ball36-gerbers.zip ./*)
"$KICAD_CLI" pcb export step --subst-models --no-dnp -o hardware/main-pcb/k0d3ball36.step "$BOARD" >/dev/null 2>&1 || echo "STEP export skipped"
"$KICAD_CLI" pcb render --side top --quality high --background opaque -w 2400 -h 1600 -o "$REN/main-pcb-top.png" "$BOARD" >/dev/null
"$KICAD_CLI" pcb render --side bottom --quality high --background opaque -w 2400 -h 1600 -o "$REN/main-pcb-bottom.png" "$BOARD" >/dev/null
"$KICAD_CLI" sch export pdf -o hardware/main-pcb/k0d3ball36-schematic.pdf "$SCH" >/dev/null
"$KICAD_CLI" sch export bom --fields "Reference,Value,Footprint,\${QUANTITY},Description" --group-by Value,Footprint -o hardware/main-pcb/k0d3ball36-bom.csv "$SCH" >/dev/null
"$KICAD_CLI" pcb export pos --format csv --units mm --side both -o hardware/main-pcb/k0d3ball36-pos.csv "$BOARD" >/dev/null
echo "exported: $OUT, hardware/main-pcb/k0d3ball36-gerbers.zip, renders, schematic pdf, bom, pos"
