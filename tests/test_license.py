# SPDX-License-Identifier: MIT
"""License files exist and scripts carry SPDX headers."""
from __future__ import annotations

from pathlib import Path

SPDX = "SPDX-License-Identifier:"


def test_license_files_present(repo_root: Path):
    mit = (repo_root / "LICENSE").read_text(encoding="utf-8")
    ohl = (repo_root / "LICENSE-HARDWARE").read_text(encoding="utf-8")
    assert "MIT License" in mit and "Konstantin Denerz" in mit
    assert "CERN Open Hardware Licence Version 2 - Permissive" in ohl


def test_scripts_have_spdx_headers(repo_root: Path, tracked_files: list[Path]):
    missing = []
    for path in tracked_files:
        if path.suffix not in (".py", ".sh") or "scripts" not in path.parts and "tests" not in path.parts:
            continue
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:5])
        if SPDX not in head:
            missing.append(str(path.relative_to(repo_root)))
    assert not missing, "scripts without SPDX header in the first 5 lines:\n" + "\n".join(missing)
