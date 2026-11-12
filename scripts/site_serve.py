#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Serve the repository root for the project page preview (`make site-serve`).

Like `python -m http.server`, but every response says `Cache-Control: no-store`: the preview
shows the working tree, which changes under it, and a browser that caches by heuristic would
mix old modules with new STLs.

Usage: scripts/site_serve.py [port] [bind]     (defaults 8000, 127.0.0.1)
"""
from __future__ import annotations

import functools
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class NoStoreHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main(argv: list[str]) -> None:
    if len(argv) > 1 and argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return
    port = int(argv[1]) if len(argv) > 1 else 8000
    bind = argv[2] if len(argv) > 2 else "127.0.0.1"
    handler = functools.partial(NoStoreHandler, directory=str(REPO))
    with ThreadingHTTPServer((bind, port), handler) as httpd:
        print(f"serving {REPO} on http://{bind}:{port}/docs/ (no-store)", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main(sys.argv)
