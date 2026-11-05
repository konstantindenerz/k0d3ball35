#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Regenerate, autoroute and verify the main PCB. Freerouting is not deterministic, so the
# route/DRC step is retried a few times until DRC (with schematic parity) is clean.
set -euo pipefail
cd "$(dirname "$0")/.."
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
KPY="${KPY:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3}"
PY="${PY:-.venv/bin/python}"
export FREEROUTING_JAR="${FREEROUTING_JAR:-build/freerouting.jar}"
export JAVA="${JAVA:-java}"
export FREEROUTING_PASSES="${FREEROUTING_PASSES:-60}"
BOARD=hardware/main-pcb/k0d3ball36.kicad_pcb
$PY scripts/gen_layout.py >/dev/null
$PY scripts/gen_schematic.py
$PY scripts/gen_pcb.py
mkdir -p build
"$KICAD_CLI" sch erc --exit-code-violations --severity-error --format json -o build/erc.json hardware/main-pcb/k0d3ball36.kicad_sch >/dev/null 2>&1
for attempt in 1 2 3; do
  "$KPY" scripts/route.py 2>&1 | grep -E "Auto-routing stage completed|widened" || true
  if "$KICAD_CLI" pcb drc --schematic-parity --severity-error --exit-code-violations --format json -o build/drc.json "$BOARD" >/dev/null 2>&1; then
    echo "DRC clean after attempt $attempt"
    exit 0
  fi
  echo "DRC not clean (attempt $attempt), rerouting"
  $PY scripts/gen_pcb.py >/dev/null
done
echo "routing failed three times, see build/drc.json" >&2
exit 1
