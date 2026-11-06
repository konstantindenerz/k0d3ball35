# SPDX-License-Identifier: MIT
"""ERC and DRC gates. Skipped cleanly when the KiCad files or kicad-cli are missing."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

BOARDS = {
    "left": ("hardware/left-pcb/k0d3ball36-left.kicad_sch", "hardware/left-pcb/k0d3ball36-left.kicad_pcb"),
    "right": ("hardware/right-pcb/k0d3ball36-right.kicad_sch", "hardware/right-pcb/k0d3ball36-right.kicad_pcb"),
    "sensor": ("hardware/sensor-pcb/k0d3ball36-sensor.kicad_sch", "hardware/sensor-pcb/k0d3ball36-sensor.kicad_pcb"),
}


def _run(cmd: list[str], report: Path) -> tuple[int, dict]:
    report.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(report.read_text(encoding="utf-8")) if report.exists() else {}
    return proc.returncode, data


def _errors(data: dict, key: str) -> list[str]:
    out = []
    for sheet in data.get("sheets", [data]):
        for item in sheet.get(key, []):
            if item.get("severity") == "error":
                out.append(f"{item.get('type')}: {item.get('description')}")
    return out


@pytest.mark.kicad
@pytest.mark.parametrize("board", sorted(BOARDS))
def test_erc_clean(repo_root: Path, kicad_cli: str, board: str):
    sch = repo_root / BOARDS[board][0]
    if not sch.exists():
        pytest.skip(f"{sch.relative_to(repo_root)} not created yet")
    report = repo_root / "build" / f"{board}.erc.json"
    code, data = _run(
        [kicad_cli, "sch", "erc", "--exit-code-violations", "--severity-error", "--format", "json", "-o", str(report), str(sch)],
        report,
    )
    errors = _errors(data, "violations")
    assert code == 0 and not errors, f"ERC errors in {board}:\n" + "\n".join(errors)


@pytest.mark.kicad
@pytest.mark.parametrize("board", sorted(BOARDS))
def test_drc_clean(repo_root: Path, kicad_cli: str, board: str):
    pcb = repo_root / BOARDS[board][1]
    if not pcb.exists():
        pytest.skip(f"{pcb.relative_to(repo_root)} not created yet")
    report = repo_root / "build" / f"{board}.drc.json"
    code, data = _run(
        [
            kicad_cli, "pcb", "drc", "--exit-code-violations", "--severity-error", "--schematic-parity",
            "--format", "json", "-o", str(report), str(pcb),
        ],
        report,
    )
    errors = _errors(data, "violations") + _errors(data, "unconnected_items") + _errors(data, "schematic_parity")
    assert code == 0 and not errors, f"DRC errors in {board}:\n" + "\n".join(errors)
