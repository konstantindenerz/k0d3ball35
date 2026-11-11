#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Export fabrication files for one or both halves: gerbers + drill (JLCPCB naming), zip, STEP,
# renders, schematic PDF, BOM, position file.
#   scripts/export.sh [left|right]      (default: both)
set -euo pipefail
cd "$(dirname "$0")/.."
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
# check_routed.py needs only the standard library: the repo venv when there is one, else python3 (CI)
PY="${PY:-$([ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)}"
HALVES=("$@")
[ ${#HALVES[@]} -eq 0 ] && HALVES=(left right)
mkdir -p build
for half in "${HALVES[@]}"; do
  case "$half" in left|right) ;; *) echo "unknown half '$half' (left|right)" >&2; exit 2 ;; esac
  NAME="k0d3ball35-$half"
  DIR="hardware/$half-pcb"
  BOARD="$DIR/$NAME.kicad_pcb"
  SCH="$DIR/$NAME.kicad_sch"
  OUT="$DIR/gerbers"
  REN="$DIR/renders"
  # never export fab files from an unrouted board (r2.4 did once)
  "$KICAD_CLI" pcb drc --schematic-parity --format json -o "build/$NAME.export-drc.json" "$BOARD" >/dev/null 2>&1 || true
  "$PY" scripts/check_routed.py "$BOARD" "build/$NAME.export-drc.json"
  rm -rf "$OUT"; mkdir -p "$OUT" "$REN"
  "$KICAD_CLI" pcb export gerbers --layers "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" \
    --subtract-soldermask --no-protel-ext -o "$OUT/" "$BOARD" >/dev/null
  "$KICAD_CLI" pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 -o "$OUT/" "$BOARD" >/dev/null
  (cd "$OUT" && rm -f "../$NAME-gerbers.zip" && zip -q "../$NAME-gerbers.zip" ./*)
  "$KICAD_CLI" pcb export step --subst-models --no-dnp -o "$DIR/$NAME.step" "$BOARD" >/dev/null 2>&1 || echo "$half: STEP export skipped"
  "$KICAD_CLI" pcb render --side top --quality high --background opaque -w 2400 -h 1600 -o "$REN/$half-pcb-top.png" "$BOARD" >/dev/null
  "$KICAD_CLI" pcb render --side bottom --quality high --background opaque -w 2400 -h 1600 -o "$REN/$half-pcb-bottom.png" "$BOARD" >/dev/null
  "$KICAD_CLI" sch export pdf -o "$DIR/$NAME-schematic.pdf" "$SCH" >/dev/null
  "$KICAD_CLI" sch export bom --fields "Reference,Value,Footprint,\${QUANTITY},Description" --group-by Value,Footprint -o "$DIR/$NAME-bom.csv" "$SCH" >/dev/null
  "$KICAD_CLI" pcb export pos --format csv --units mm --side both -o "$DIR/$NAME-pos.csv" "$BOARD" >/dev/null
  echo "$half: exported $OUT, $DIR/$NAME-gerbers.zip, renders, schematic pdf, bom, pos"
done
