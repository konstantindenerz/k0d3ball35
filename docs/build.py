#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the data files of the published page (docs/data/*.json).

The page itself (index.html, css/, js/) is hand-written and static. It reads these JSON files
and fetches the real 3D files (STL, GLB) from the repository: raw.githubusercontent.com on the
published site, the working tree when served from localhost (`make site-serve`).

Usage: build.py [--check] [--out DIR]
  --check  regenerate in memory and fail if a committed file differs (what the tests run)
  --out    write somewhere else than docs/data
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# one module per data file in docs/gen/, in the order they are written
GENERATORS = ("site", "layout", "parts", "pcbs", "keymap")


def render(data: dict) -> str:
    return json.dumps(data, indent=1, ensure_ascii=False) + "\n"


def generate() -> dict[str, str]:
    out = {}
    for name in GENERATORS:
        data = importlib.import_module(f"gen.{name}").build()
        if data is not None:
            out[f"{name}.json"] = render(data)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", type=Path, default=HERE / "data")
    args = ap.parse_args()
    files = generate()
    if args.check:
        stale = [n for n, text in files.items() if not (args.out / n).exists() or (args.out / n).read_text() != text]
        if stale:
            print("stale, run `make site`: " + ", ".join(stale))
            return 1
        print(f"{len(files)} data files current")
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (args.out / name).write_text(text)
        print(f"wrote {args.out.name}/{name} ({len(text) // 1024} KiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
