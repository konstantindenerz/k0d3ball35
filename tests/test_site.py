# SPDX-License-Identifier: MIT
"""The published page in docs/: data files current, every file it loads exists in the repo,
the shell lists every tab."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = DOCS / "data"
REPO_PATH = re.compile(r"^(hardware|spec|firmware|issues|scripts)/[\w./+-]+\.\w+$")


def _strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)
    elif isinstance(obj, str):
        yield obj


@pytest.fixture(scope="module")
def site() -> dict:
    return json.loads((DATA / "site.json").read_text())


@pytest.fixture(scope="module")
def tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return set(out.split())


def test_data_files_are_current():
    """docs/data is generated; `make site` after a layout, case or board change keeps it current."""
    r = subprocess.run([sys.executable, str(DOCS / "build.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_every_file_the_page_loads_is_in_the_repo(tracked):
    """The page fetches repo paths from raw.githubusercontent.com, so each one has to be committed."""
    paths = {s for f in DATA.glob("*.json") for s in _strings(json.loads(f.read_text())) if REPO_PATH.match(s)}
    assert paths, "the data names no repo files at all"
    missing = sorted(p for p in paths if not (ROOT / p).is_file())
    untracked = sorted(p for p in paths if p not in tracked and p not in missing)
    assert not missing, f"named in docs/data but not on disk: {missing}"
    assert not untracked, f"named in docs/data but not committed: {untracked}"


def test_shell_lists_every_tab(site):
    html = (DOCS / "index.html").read_text()
    for i, tab in enumerate(site["tabs"], 1):
        tid = tab["id"]
        assert f'href="#{tid}" data-tab="{tid}"><small>{i}</small>' in html, f"nav entry for {tid}"
        assert f'id="tab-{tid}"' in html, f"section for {tid}"
        assert (DOCS / "js" / "tabs" / f"{tid}.js").is_file(), f"module for {tid}"
        assert (DOCS / "css" / "tabs" / f"{tid}.css").is_file(), f"stylesheet for {tid}"
        assert f'href="css/tabs/{tid}.css"' in html


def test_shell_stays_small_and_pins_three():
    html = (DOCS / "index.html").read_text()
    assert len(html) < 50_000, "nothing is inlined into the shell any more"
    assert not re.search(r"[A-Za-z0-9+/]{2000,}", html), "no base64 blobs"
    versions = set(re.findall(r"three@([\w.]+)/", html))
    assert versions and all(re.fullmatch(r"\d+\.\d+\.\d+", v) for v in versions) and len(versions) == 1


def test_modules_import_only_pinned_or_local_code():
    """ES modules may import 'three', 'three/addons/...' (both pinned in the importmap) or relative files."""
    for js in (DOCS / "js").rglob("*.js"):
        for spec in re.findall(r"""(?:from\s+|import\s*\(\s*)['"`]([^'"`]+)['"`]""", js.read_text()):
            ok = spec == "three" or spec.startswith("three/addons/") or spec.startswith(".")
            assert ok, f"{js.relative_to(ROOT)} imports {spec}"
            if spec.startswith(".") and "${" not in spec:
                assert (js.parent / spec).resolve().is_file(), f"{js.relative_to(ROOT)}: {spec} missing"


def test_layout_names_the_case_stls(tracked):
    layout = json.loads((DATA / "layout.json").read_text())
    for half, h in layout["halves"].items():
        assert set(h["case_files"]) == {"tray", "cap", "lid", "lid_folded"}
        for path in h["case_files"].values():
            assert path in tracked and half in path
