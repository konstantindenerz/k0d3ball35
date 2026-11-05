# SPDX-License-Identifier: MIT
"""Reversible footprint checks and library consistency."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from k0d3.footprints import Pad, all_footprints
from k0d3.geometry import REPO
from k0d3.netlist import HOLE_PIN_LEFT, HOLE_PIN_RIGHT

LIB_DIR = REPO / "hardware" / "lib" / "k0d3ball36.pretty"
HANDED = {"SW_Choc_V1_HS_reversible", "FPC_0.5mm_6P_FH12-6S_reversible", "SW_SPDT_MSK12C02_reversible", "JST_PH_S2B-PH-SM4-TB_reversible"}
SYMMETRIC = {"D_SOD-123_reversible", "SolderJumper_3_bridged_both_sides", "TestPad_1.5mm", "SW_SPST_EVQP7A_reversible"}


@pytest.fixture(scope="module")
def fps():
    return all_footprints(HOLE_PIN_RIGHT, HOLE_PIN_LEFT)


def _on(pad: Pad, layer: str) -> bool:
    return layer in pad.layers or "*.Cu" in pad.layers


def _copper(pad: Pad, layer: str) -> bool:
    return pad.kind != "np_thru_hole" and _on(pad, layer)


def test_pad_numbers_on_both_faces(fps):
    for name, fp in fps.items():
        f = {p.number for p in fp.pads if p.number and _copper(p, "F.Cu")}
        b = {p.number for p in fp.pads if p.number and _copper(p, "B.Cu")}
        assert f == b, f"{name}: F {f} vs B {b}"


def _match(fp, mirror: bool):
    for p in fp.pads:
        if not p.number or p.kind != "smd" or "F.Cu" not in p.layers:
            continue
        want = (-p.x if mirror else p.x, p.y)
        ok = any(q.number == p.number and q.kind == "smd" and "B.Cu" in q.layers
                 and math.isclose(q.x, want[0], abs_tol=1e-6) and math.isclose(q.y, want[1], abs_tol=1e-6)
                 and (q.w, q.h) == (p.w, p.h) for q in fp.pads)
        assert ok, f"{fp.name}: no B counterpart for pad {p.number} at ({p.x}, {p.y})"


def test_handed_parts_are_mirrored(fps):
    for name in HANDED:
        _match(fps[name], mirror=True)


def test_symmetric_parts_same_positions(fps):
    for name in SYMMETRIC:
        _match(fps[name], mirror=False)


def _bbox(p: Pad):
    if p.shape == "circle":
        r = p.w / 2
        return (p.x - r, p.y - r, p.x + r, p.y + r)
    return (p.x - p.w / 2, p.y - p.h / 2, p.x + p.w / 2, p.y + p.h / 2)


def _overlap(a, b, margin=0.1):
    return not (a[2] + margin <= b[0] or b[2] + margin <= a[0] or a[3] + margin <= b[1] or b[3] + margin <= a[1])


def test_no_overlap_between_different_pads(fps):
    for name, fp in fps.items():
        for layer in ("F.Cu", "B.Cu"):
            pads = [p for p in fp.pads if p.number and _copper(p, layer)]
            for i, a in enumerate(pads):
                for b in pads[i + 1:]:
                    if a.number == b.number:
                        continue
                    assert not _overlap(_bbox(a), _bbox(b)), f"{name}: pads {a.number} and {b.number} overlap on {layer}"


def test_copper_clears_npth_holes(fps):
    """Copper pads keep 0.2 mm from the non-plated holes (socket bosses, posts, screws)."""
    for name, fp in fps.items():
        holes = [p for p in fp.pads if p.kind == "np_thru_hole"]
        for h in holes:
            for p in fp.pads:
                if p.kind == "np_thru_hole" or not p.number:
                    continue
                if p.shape == "circle":
                    d = math.dist((p.x, p.y), (h.x, h.y)) - p.w / 2 - h.drill / 2
                else:
                    # distance from hole centre to the pad rectangle, corners rounded by rratio
                    rr = (p.rratio or 0) * min(p.w, p.h)
                    cx = min(max(h.x, p.x - p.w / 2 + rr), p.x + p.w / 2 - rr)
                    cy = min(max(h.y, p.y - p.h / 2 + rr), p.y + p.h / 2 - rr)
                    d = math.dist((cx, cy), (h.x, h.y)) - rr - h.drill / 2
                assert d >= 0.2, f"{name}: pad {p.number} is {d:.2f} mm from hole at ({h.x}, {h.y})"


def test_choc_holes(fps):
    fp = fps["SW_Choc_V1_HS_reversible"]
    holes = {(p.x, p.y): p.drill for p in fp.pads if p.kind == "np_thru_hole"}
    assert holes == {(0, 0): 3.4, (-5.5, 0): 1.7, (5.5, 0): 1.7, (0, -5.9): 3.05, (5.0, -3.8): 3.05, (-5.0, -3.8): 3.05}
    assert not any(p.kind == "thru_hole" for p in fp.pads), "hot-swap only: no plated switch pin holes"


def test_controller_footprint(fps):
    fp = fps["nice_nano_v2_THT"]
    tht = [p for p in fp.pads if p.kind == "thru_hole"]
    assert len(tht) == 24
    assert {p.number for p in tht} == {str(i) for i in range(1, 25)}
    left = sorted((p for p in tht if p.x < 0), key=lambda p: p.y)
    right = sorted((p for p in tht if p.x > 0), key=lambda p: p.y)
    assert [p.number for p in left] == [str(i) for i in range(1, 13)]
    assert [p.number for p in right] == [str(i) for i in range(13, 25)]
    assert all(math.isclose(b.y - a.y, 2.54, abs_tol=1e-6) for a, b in zip(left, left[1:]))
    assert math.isclose(right[0].x - left[0].x, 15.24, abs_tol=1e-6)


# ----- library files ------------------------------------------------------------------
def _tokenize(text: str):
    tok, i, n = "", 0, len(text)
    while i < n:
        ch = text[i]
        if ch == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            yield text[i:j + 1]
            i = j + 1
        elif ch in "()":
            if tok:
                yield tok
                tok = ""
            yield ch
            i += 1
        elif ch.isspace():
            if tok:
                yield tok
                tok = ""
            i += 1
        else:
            tok += ch
            i += 1
    if tok:
        yield tok


def _parse(text: str):
    stack = [[]]
    for t in _tokenize(text):
        if t == "(":
            stack.append([])
        elif t == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t)
    return stack[0][0]


def test_library_files_match(fps):
    assert LIB_DIR.is_dir()
    for name, fp in fps.items():
        path = LIB_DIR / f"{name}.kicad_mod"
        assert path.exists(), path
        tree = _parse(path.read_text())
        assert tree[0] == "footprint" and tree[1] == f'"{name}"'
        pads = [n for n in tree if isinstance(n, list) and n and n[0] == "pad"]
        assert len(pads) == len(fp.pads), name
        numbers = sorted(p[1].strip('"') for p in pads)
        assert numbers == sorted(p.number for p in fp.pads)
