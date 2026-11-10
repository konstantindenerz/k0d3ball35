#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the data files of the published page (docs/data/*.json) and stamp the versions.

The page itself (index.html, css/, js/) is hand-written and static. It reads these JSON files
and fetches the real 3D files (STL, GLB) from the repository: raw.githubusercontent.com on the
published site, the working tree when served from localhost (`make site-serve`).

Every URL the page loads carries a content hash (`?v=`), so one page load never mixes files of
two versions from different caches (GitHub Pages caches 10 minutes, raw.githubusercontent 5):
- data/versions.json: a hash per repository file the page fetches (named in the data files or
  as a string literal in js/);
- the block between `<!-- versions -->` and `<!-- /versions -->` in index.html: the stylesheets,
  an importmap that maps every local module to its hashed URL (so the relative imports between
  the modules resolve to the same build), the hashes of the data files and the main module.

Usage: build.py [--check] [--out DIR]
  --check  regenerate in memory and fail if a committed file differs (what the tests run)
  --out    write somewhere else than docs/data
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
INDEX = HERE / "index.html"
ASSET = re.compile(r"\.(stl|glb|svg|png|jpg|zip|step)$")
THREE = "0.160.0"

# one module per data file in docs/gen/, in the order they are written
GENERATORS = ("site", "layout", "parts", "pcbs", "keymap")


def render(data: dict) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False) + "\n"


def short_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:10]


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def asset_paths(files: dict[str, str]) -> list[str]:
    """Repository files the page fetches: paths in the data, path literals in the modules."""
    found = {s for text in files.values() for s in _strings(json.loads(text)) if ASSET.search(s)}
    for js in (HERE / "js").rglob("*.js"):
        found |= {m for m in re.findall(r"'([\w./-]+)'", js.read_text()) if ASSET.search(m)}
    return sorted(p for p in found if (REPO / p).is_file())


def versions(files: dict[str, str]) -> str:
    return render({p: short_hash((REPO / p).read_bytes()) for p in asset_paths(files)})


def stamp(html: str, files: dict[str, str], tab_ids: list[str]) -> str:
    """index.html with the versions block rewritten from the current css/, js/ and data."""
    def v(rel: str) -> str:
        return f"{rel}?v={short_hash((HERE / rel).read_bytes())}"

    css = ["css/site.css"] + [f"css/tabs/{t}.css" for t in tab_ids]
    modules = sorted(str(p.relative_to(HERE)) for p in (HERE / "js").rglob("*.js"))
    imports = {"three": f"https://cdn.jsdelivr.net/npm/three@{THREE}/build/three.module.min.js",
               "three/addons/": f"https://cdn.jsdelivr.net/npm/three@{THREE}/examples/jsm/"}
    imports |= {f"./{m}": f"./{v(m)}" for m in modules}
    data = {name[:-5]: short_hash(text.encode()) for name, text in sorted(files.items())}
    block = "\n".join(
        [f'<link rel="stylesheet" href="{v(c)}">' for c in css]
        + [f'<script type="importmap">{json.dumps({"imports": imports}, separators=(",", ":"))}</script>',
           f'<script type="application/json" id="dataVersions">{json.dumps(data, separators=(",", ":"))}</script>',
           f'<script type="module" src="{v("js/main.js")}"></script>'])
    out, n = re.subn(r"<!-- versions -->.*?<!-- /versions -->",
                     lambda _: f"<!-- versions -->\n{block}\n<!-- /versions -->", html, flags=re.S)
    assert n == 1, "index.html needs one <!-- versions --> ... <!-- /versions --> block"
    return out


def generate() -> dict[str, str]:
    out = {}
    for name in GENERATORS:
        data = importlib.import_module(f"gen.{name}").build()
        if data is not None:
            out[f"{name}.json"] = render(data)
    out["versions.json"] = versions(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE / "data")
    args = ap.parse_args()
    files = generate()
    tabs = [t["id"] for t in json.loads(files["site.json"])["tabs"]]
    html = stamp(INDEX.read_text(), files, tabs)
    if args.check:
        stale = [n for n, text in files.items() if not (args.out / n).exists() or (args.out / n).read_text() != text]
        if html != INDEX.read_text():
            stale.append("index.html (versions)")
        if stale:
            print("stale, run `make site`: " + ", ".join(stale))
            return 1
        print(f"{len(files)} data files and the index.html versions current")
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (args.out / name).write_text(text)
        print(f"wrote {args.out.name}/{name} ({len(text) // 1024} KiB)")
    INDEX.write_text(html)
    print("stamped index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
