# SPDX-License-Identifier: MIT
"""The release archive holds exactly the printed parts, and the workflow that attaches it exists."""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import release_zip  # noqa: E402


def test_zip_holds_every_printed_part(tmp_path):
    path = release_zip.build("test-print-1", tmp_path)
    assert path.name == "k0d3ball35-print-test-print-1.zip"
    parts = json.loads((ROOT / "docs" / "data" / "parts.json").read_text())["parts"]
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        names = z.namelist()
        assert all(n.startswith("k0d3ball35-print-test-print-1/") for n in names)
        stls = {n.rsplit("/", 1)[1] for n in names if n.endswith(".stl")}
        assert stls == {Path(p["path"]).name for p in parts if p["printed"]}
        assert not [n for n in stls if n.startswith(("lid-left", "lid-right", "lid-folded"))], "display pairs are not printed"
        for p in parts:
            if p["printed"]:
                inside = next(n for n in names if n.endswith("/" + Path(p["path"]).name))
                assert z.read(inside) == (ROOT / p["path"]).read_bytes()
        text = z.read("k0d3ball35-print-test-print-1/README.txt").decode()
    assert "untested" in text and "blob/test-print-1/hardware/case/README.md" in text
    for n in stls:
        assert n in text
    assert release_zip.build("test-print-1", tmp_path / "again").read_bytes() == path.read_bytes(), "not reproducible"


def test_a_tag_attaches_the_zip():
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "release.yml").read_text())
    assert wf[True]["push"]["tags"] == ["*"]          # yaml reads the key `on` as True
    job = wf["jobs"]["print-files"]
    assert job["permissions"] == {"contents": "write"}
    runs = " ".join(str(s.get("run", "")) for s in job["steps"])
    assert "scripts/release_zip.py" in runs and "gh release upload" in runs and "--prerelease" in runs
