#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Pack the printed parts into one zip for a GitHub release.

    release_zip.py <version> [--out DIR]

What goes in is what docs/data/parts.json lists as printed (docs/gen/parts.py), one folder per
group, plus a README.txt with the part list. The files are the committed ones, nothing is
rendered here; the standard library is enough, so the release workflow needs no environment.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PARTS = REPO / "docs" / "data" / "parts.json"
URL = "https://github.com/konstantindenerz/k0d3ball35"
FOLDERS = {"right": "right-half", "left": "left-half", "test": "test-prints", "cradle": "trackball-cradle",
           "retainer": "ball-retainer"}
EPOCH = (2026, 1, 1, 0, 0, 0)     # fixed time stamps: the same commit gives the same zip


def entries() -> list[tuple[str, dict]]:
    """(path inside the zip, part) for every printed part, in the order of the part list."""
    data = json.loads(PARTS.read_text())
    return [(f"{FOLDERS[p['group']]}/{Path(p['path']).name}", p) for p in data["parts"] if p["printed"]]


def readme(version: str) -> str:
    data = json.loads(PARTS.read_text())
    lines = [f"k0d3ball35 printed parts, {version}", "",
             "Status: untested. Nothing in here has been printed or fit-checked yet; this archive is",
             "for test prints. Start with the folder test-prints.", "",
             f"Print settings and what to check: {URL}/blob/{version}/hardware/case/README.md",
             f"Cradle:                           {URL}/blob/{version}/hardware/trackball-cradle/README.md",
             "", "The files are in the print frame: seen from above as they lie on the bed, z up, in mm.", ""]
    for g in data["groups"]:
        rows = [(name, p) for name, p in entries() if p["group"] == g["id"]]
        if not rows:
            continue
        lines += [g["label"], "-" * len(g["label"])]
        for name, p in rows:
            x, y, z = p["size"]
            lines += [f"{name}", f"    {p['name']}, {x:.1f} x {y:.1f} x {z:.1f} mm. {p['role']}"]
        lines.append("")
    return "\n".join(lines)


def build(version: str, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    root = f"k0d3ball35-print-{version}"
    path = out / f"{root}.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        def add(name: str, data: bytes) -> None:
            z.writestr(zipfile.ZipInfo(f"{root}/{name}", EPOCH), data, zipfile.ZIP_DEFLATED)

        add("README.txt", readme(version).encode())
        add("LICENSE", (REPO / "LICENSE").read_bytes())
        for name, p in entries():
            add(name, (REPO / p["path"]).read_bytes())
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("version", help="the tag, e.g. test-print-1")
    ap.add_argument("--out", type=Path, default=REPO / "build")
    a = ap.parse_args()
    made = build(a.version, a.out)
    print(f"wrote {made.relative_to(REPO) if made.is_relative_to(REPO) else made} ({made.stat().st_size // 1024} KiB)")
