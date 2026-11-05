# SPDX-License-Identifier: MIT
"""Minimal helpers for writing KiCad s-expression files deterministically."""
from __future__ import annotations

import uuid

NAMESPACE = uuid.UUID("6f1b2a9e-3c4d-4e5f-8a9b-0c1d2e3f4a5b")


def uid(*parts: object) -> str:
    """Deterministic UUID so that regenerating the files produces no spurious diffs."""
    return str(uuid.uuid5(NAMESPACE, "/".join(str(p) for p in parts)))


def num(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s


def quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def at(x: float, y: float, rot: float | None = None) -> str:
    if rot is None or abs(rot) < 1e-9:
        return f"(at {num(x)} {num(y)})"
    return f"(at {num(x)} {num(y)} {num(rot)})"


def font(size: float = 1.0, thickness: float = 0.15) -> str:
    return f"(effects (font (size {num(size)} {num(size)}) (thickness {num(thickness)})))"
