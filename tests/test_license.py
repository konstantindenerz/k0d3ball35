# SPDX-License-Identifier: MIT
"""License files exist and scripts carry SPDX headers."""
from __future__ import annotations

from pathlib import Path

SPDX = "SPDX-License-Identifier:"


HOLDER = "Konstantin Denerz"


def test_license_files_present(repo_root: Path):
    """Both licences, and both naming the holder.

    CERN-OHL-P section 3 asks for the copyright notice to travel with the design files, and the
    hardware is the part most likely to be copied out of this repository on its own - so the
    notice has to be in LICENSE-HARDWARE itself, not only in the MIT file next to it.
    """
    mit = (repo_root / "LICENSE").read_text(encoding="utf-8")
    ohl = (repo_root / "LICENSE-HARDWARE").read_text(encoding="utf-8")
    assert "MIT License" in mit and HOLDER in mit
    assert "CERN Open Hardware Licence Version 2 - Permissive" in ohl
    assert HOLDER in ohl, "LICENSE-HARDWARE carries the licence text but names no copyright holder"
    for name, text in (("LICENSE", mit), ("LICENSE-HARDWARE", ohl)):
        assert f"Copyright (c) 2026 {HOLDER}" in text, f"{name}: no copyright line"


def test_the_notice_names_the_owner(repo_root: Path):
    """NOTICE states that the wordmark is excluded from both licences; that claim needs an owner."""
    notice = (repo_root / "NOTICE").read_text(encoding="utf-8")
    assert HOLDER in notice
    assert "Owner wordmark" in notice


def test_scripts_have_spdx_headers(repo_root: Path, tracked_files: list[Path]):
    missing = []
    for path in tracked_files:
        if path.suffix not in (".py", ".sh") or "scripts" not in path.parts and "tests" not in path.parts:
            continue
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:5])
        if SPDX not in head:
            missing.append(str(path.relative_to(repo_root)))
    assert not missing, "scripts without SPDX header in the first 5 lines:\n" + "\n".join(missing)
