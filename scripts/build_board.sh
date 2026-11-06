#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Regenerate, autoroute and verify the main PCB of one or both halves:
#   scripts/build_board.sh [left|right]      (default: both)
# Freerouting is not deterministic, so the route/DRC step is retried a few times until
# DRC (with schematic parity) is clean.
set -euo pipefail
cd "$(dirname "$0")/.."
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
KPY="${KPY:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3}"
PY="${PY:-.venv/bin/python}"
export FREEROUTING_JAR="${FREEROUTING_JAR:-build/freerouting.jar}"
export JAVA="${JAVA:-java}"
export FREEROUTING_PASSES="${FREEROUTING_PASSES:-60}"
ATTEMPTS="${ATTEMPTS:-3}"
HALVES=("$@")
[ ${#HALVES[@]} -eq 0 ] && HALVES=(left right)

$PY scripts/gen_layout.py >/dev/null
mkdir -p build
for half in "${HALVES[@]}"; do
  case "$half" in left|right) ;; *) echo "unknown half '$half' (left|right)" >&2; exit 2 ;; esac
  NAME="k0d3ball36-$half"
  DIR="hardware/$half-pcb"
  BOARD="$DIR/$NAME.kicad_pcb"
  $PY scripts/gen_schematic.py "$half"
  $PY scripts/gen_pcb.py "$half"
  "$KICAD_CLI" sch erc --exit-code-violations --severity-error --format json -o "build/$NAME.erc.json" "$DIR/$NAME.kicad_sch" >/dev/null 2>&1
  ok=0
  for attempt in $(seq 1 "$ATTEMPTS"); do
    "$KPY" scripts/route.py all "$BOARD" 2>&1 | grep -E "Auto-routing stage completed|widened" || true
    if "$KICAD_CLI" pcb drc --schematic-parity --severity-error --exit-code-violations --format json -o "build/$NAME.drc.json" "$BOARD" >/dev/null 2>&1; then
      echo "$half: DRC clean after attempt $attempt"
      ok=1
      break
    fi
    echo "$half: DRC not clean (attempt $attempt), rerouting"
    $PY scripts/gen_pcb.py "$half" >/dev/null
  done
  if [ "$ok" -ne 1 ]; then
    echo "$half: routing failed $ATTEMPTS times, see build/$NAME.drc.json" >&2
    exit 1
  fi
done
