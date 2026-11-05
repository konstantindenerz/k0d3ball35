# SPDX-License-Identifier: MIT
"""Shared fixtures: repository root, tracked files, kicad-cli discovery."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

KICAD_CANDIDATES = (
    os.environ.get("KICAD_CLI", ""),
    "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    shutil.which("kicad-cli") or "",
)


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def tracked_files(repo_root: Path) -> list[Path]:
    """Files git considers part of the repository (tracked or untracked but not ignored)."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=repo_root,
            check=True,
            capture_output=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [p for p in repo_root.rglob("*") if p.is_file() and ".venv" not in p.parts and ".git" not in p.parts]
    return [repo_root / name for name in out.decode().split("\0") if name]


@pytest.fixture(scope="session")
def kicad_cli() -> str:
    for candidate in KICAD_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    pytest.skip("kicad-cli not found (set KICAD_CLI or install KiCad)")
