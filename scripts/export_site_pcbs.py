#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Export the board files the page shows on its PCBs tab (`make pcb-3d`).

Per board (left, right, sensor):
  hardware/<board>/renders/k0d3ball35-<board>.glb   binary glTF from `kicad-cli pcb export glb`
      with tracks, pads, zones, silkscreen and soldermask, then compacted: the primitives of each
      mesh are merged per material, identical vertices are welded and the board's own flat meshes
      lose their normals (viewers shade them flat, which is exact for extruded copper and mask). KiCad writes one primitive
      per copper shape (11 000 on a main board), which makes the file 12 MB and slow to parse;
      merged it is a few MB with the same triangles. The export timestamp is dropped so a re-run
      leaves git clean. Frame as KiCad writes it: glTF Y up, metres.
  hardware/<board>/renders/layers/<layer>.svg   one plot per layer (F.Cu, B.Cu, F.Silkscreen,
      B.Silkscreen, F.Mask, B.Mask, Edge.Cuts) from `kicad-cli pcb export svg --page-size-mode 2`,
      plus outline.svg (the board shape filled, holes and slots cut out). Every file of a board
      gets the same viewBox: the board outline plus 1 mm, so the plots stack. Colours are reduced
      to currentColor (the plot) and var(--hole) (drill holes on copper), so the page colours
      each layer itself. The plot date in <title> is replaced by the board and layer name.

Needs kicad-cli and KiCad's own Python (pcbnew, for the board outline):
  KICAD_CLI=... KPY=... scripts/export_site_pcbs.py [left|right|sensor ...]
"""
from __future__ import annotations

import json
import os
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
KICAD_CLI = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
KPY = os.environ.get("KPY", "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3")

BOARDS = {
    "left": "hardware/left-pcb/k0d3ball35-left.kicad_pcb",
    "right": "hardware/right-pcb/k0d3ball35-right.kicad_pcb",
    "sensor": "hardware/sensor-pcb/k0d3ball35-sensor.kicad_pcb",
}
# file name in renders/layers/ -> KiCad layer name
LAYERS = {
    "F.Cu": "F.Cu", "B.Cu": "B.Cu",
    "F.Silkscreen": "F.SilkS", "B.Silkscreen": "B.SilkS",
    "F.Mask": "F.Mask", "B.Mask": "B.Mask",
    "Edge.Cuts": "Edge.Cuts",
}
MARGIN = 1.0  # mm around the outline in every viewBox
GLB_FLAGS = ["--include-tracks", "--include-pads", "--include-zones", "--include-silkscreen",
             "--include-soldermask", "--subst-models"]


def run(cmd: list[str]) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"failed: {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r.stdout


# ---------------------------------------------------------------- GLB
def read_glb(data: bytes) -> tuple[dict, bytes]:
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF" and version == 2 and length == len(data), "not a glTF 2 binary"
    off, js, bin_ = 12, None, b""
    while off < length:
        clen, ctype = struct.unpack_from("<II", data, off)
        chunk = data[off + 8: off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(chunk)
        elif ctype == 0x004E4942:
            bin_ = chunk
        off += 8 + clen
    return js, bin_


def write_glb(js: dict, bin_: bytes) -> bytes:
    j = json.dumps(js, separators=(",", ":"), sort_keys=True).encode()
    j += b" " * (-len(j) % 4)
    bin_ += b"\0" * (-len(bin_) % 4)
    total = 12 + 8 + len(j) + 8 + len(bin_)
    return (struct.pack("<4sII", b"glTF", 2, total) + struct.pack("<II", len(j), 0x4E4F534A) + j
            + struct.pack("<II", len(bin_), 0x004E4942) + bin_)


BOARD_MESH = re.compile(r"^k0d3ball35-\w+_(copper|pad|via|silkscreen|soldermask|PCB)$")
_CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}
_NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def _accessor(js: dict, bin_: bytes, i: int) -> np.ndarray:
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    dt = np.dtype(_CT[a["componentType"]])
    n = _NC[a["type"]]
    start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", dt.itemsize * n)
    raw = np.frombuffer(bin_, dtype=np.uint8, count=stride * (a["count"] - 1) + dt.itemsize * n, offset=start)
    rows = np.lib.stride_tricks.as_strided(raw, shape=(a["count"], dt.itemsize * n), strides=(stride, 1))
    return np.ascontiguousarray(rows).view(dt).reshape(a["count"], n) if n > 1 else np.ascontiguousarray(rows).view(dt).ravel()


def compact_glb(data: bytes, board: str) -> bytes:
    """Merge the primitives of each mesh per material, weld identical vertices, drop the timestamp."""
    js, bin_ = read_glb(data)
    out_bin = bytearray()
    views, accs = [], []

    def put(arr: np.ndarray, target: int, kind: str, minmax: bool = False) -> int:
        while len(out_bin) % 4:
            out_bin.append(0)
        views.append({"buffer": 0, "byteOffset": len(out_bin), "byteLength": arr.nbytes, "target": target})
        out_bin.extend(arr.tobytes())
        ct = {np.dtype(np.float32): 5126, np.dtype(np.uint32): 5125, np.dtype(np.uint16): 5123}[arr.dtype]
        acc = {"bufferView": len(views) - 1, "componentType": ct, "count": len(arr), "type": kind}
        if minmax:
            acc["min"] = [float(v) for v in arr.min(axis=0)]
            acc["max"] = [float(v) for v in arr.max(axis=0)]
        accs.append(acc)
        return len(accs) - 1

    meshes = []
    for mesh in js["meshes"]:
        # the board's own meshes (copper, pads, vias, silkscreen, soldermask, body) are flat extrusions:
        # without normals glTF viewers shade them flat, which is exact, and their vertices weld by position
        flat = bool(BOARD_MESH.search(mesh.get("name", "")))
        groups: dict = {}
        for p in mesh["primitives"]:
            assert p.get("mode", 4) == 4 and set(p["attributes"]) <= {"POSITION", "NORMAL"}, p
            pos = _accessor(js, bin_, p["attributes"]["POSITION"])
            nor = _accessor(js, bin_, p["attributes"]["NORMAL"]) if "NORMAL" in p["attributes"] else np.zeros_like(pos)
            idx = _accessor(js, bin_, p["indices"]).astype(np.int64) if "indices" in p else np.arange(len(pos))
            groups.setdefault(p.get("material"), []).append((pos, nor, idx))
        prims = []
        for mat in sorted(groups, key=lambda m: -1 if m is None else m):
            parts = groups[mat]
            pos = np.concatenate([g[0] for g in parts])
            nor = np.concatenate([g[1] for g in parts])
            base = np.cumsum([0] + [len(g[0]) for g in parts[:-1]])
            idx = np.concatenate([g[2] + b for g, b in zip(parts, base)])
            # weld: identical position (and normal, where kept) -> one vertex, first occurrence keeps its order
            key = (pos if flat else np.concatenate([pos, nor], axis=1)).astype(np.float32)
            key = np.ascontiguousarray(key)
            _, first, inv = np.unique(key.view(np.dtype((np.void, key.dtype.itemsize * key.shape[1]))).ravel(),
                                      return_index=True, return_inverse=True)
            order = np.argsort(first)
            rank = np.empty_like(order)
            rank[order] = np.arange(len(order))
            keep = first[order]
            idx = rank[inv.ravel()][idx]
            pos, nor = pos[keep].astype(np.float32), nor[keep].astype(np.float32)
            ityp = np.uint16 if len(pos) < 65535 else np.uint32
            attrs = {"POSITION": put(pos, 34962, "VEC3", True)}
            if not flat:
                attrs["NORMAL"] = put(nor, 34962, "VEC3")
            prim = {"attributes": attrs, "indices": put(idx.astype(ityp), 34963, "SCALAR"), "mode": 4}
            if mat is not None:
                prim["material"] = mat
            prims.append(prim)
        m = {"primitives": prims}
        if "name" in mesh:
            m["name"] = mesh["name"]
        meshes.append(m)

    asset = js["asset"]
    extras = dict(asset.get("extras", {}))
    extras.pop("generated_at", None)
    extras["source_pcb_file"] = f"k0d3ball35-{board}.kicad_pcb"
    out = {k: v for k, v in js.items() if k not in ("accessors", "bufferViews", "buffers", "meshes")}
    out["asset"] = {**asset, "extras": extras}
    out.update(accessors=accs, bufferViews=views, buffers=[{"byteLength": len(out_bin)}], meshes=meshes)
    return write_glb(out, bytes(out_bin))


# ---------------------------------------------------------------- outline (KiCad's Python)
OUTLINE_PY = r"""
import json, sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
ps = pcbnew.SHAPE_POLY_SET()
assert b.GetBoardPolygonOutlines(ps, False), "board outline is not closed"
mm = pcbnew.ToMM
def ring(c): return [[round(mm(c.CPoint(i).x), 4), round(mm(c.CPoint(i).y), 4)] for i in range(c.PointCount())]
polys = [{"outline": ring(ps.Outline(i)), "holes": [ring(ps.Hole(i, h)) for h in range(ps.HoleCount(i))]} for i in range(ps.OutlineCount())]
print("OUTLINE" + json.dumps(polys))
"""


def board_outline(pcb: Path) -> list[dict]:
    out = run([KPY, "-c", OUTLINE_PY, str(pcb)])
    return json.loads(out.split("OUTLINE", 1)[1].strip())


# ---------------------------------------------------------------- SVG
def _num(v: float) -> str:
    return f"{v:.4f}"


def clean_svg(text: str, view: tuple[float, float, float, float], title: str) -> str:
    """Common viewBox, colours to currentColor / var(--hole), no plot date."""
    x, y, w, h = view
    text = re.sub(r'width="[^"]*mm" height="[^"]*mm" viewBox="[^"]*"',
                  f'width="{_num(w)}mm" height="{_num(h)}mm" viewBox="{_num(x)} {_num(y)} {_num(w)} {_num(h)}"', text, count=1)
    text = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", text, count=1, flags=re.S)
    text = re.sub(r"#000000\b", "currentColor", text)
    text = re.sub(r"#FFFFFF\b", "var(--hole, #FFFFFF)", text)
    assert not re.search(r"(?<!--hole, )#[0-9A-Fa-f]{6}\b", text), f"{title}: unexpected colour left"
    assert not re.search(r"20\d\d-\d\d-\d\dT", text), f"{title}: timestamp left"
    return text


def outline_svg(polys: list[dict], origin: tuple[float, float], view, title: str) -> str:
    ox, oy = origin
    d = []
    for p in polys:
        for r in [p["outline"], *p["holes"]]:
            pts = " ".join(f"{_num(px - ox)},{_num(py - oy)}" for px, py in r)
            d.append(f"M {pts} Z")
    x, y, w, h = view
    return ('<?xml version="1.0" standalone="no"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            f'width="{_num(w)}mm" height="{_num(h)}mm" viewBox="{_num(x)} {_num(y)} {_num(w)} {_num(h)}">\n'
            f"<title>{title}</title>\n"
            f'<path style="fill:currentColor; fill-rule:evenodd; stroke:none;" d="{" ".join(d)}" />\n</svg>\n')


def first_point(svg: str) -> tuple[float, float]:
    m = re.search(r'd="M\s*([-\d.]+)[ ,]([-\d.]+)', svg)
    return float(m.group(1)), float(m.group(2))


def export_board(board: str, tmp: Path) -> None:
    pcb = ROOT / BOARDS[board]
    name = pcb.stem
    ren = pcb.parent / "renders"
    lay = ren / "layers"
    lay.mkdir(parents=True, exist_ok=True)

    raw = tmp / f"{name}.glb"
    run([KICAD_CLI, "pcb", "export", "glb", *GLB_FLAGS, "-f", "-o", str(raw), str(pcb)])
    glb = compact_glb(raw.read_bytes(), board)
    (ren / f"{name}.glb").write_bytes(glb)

    polys = board_outline(pcb)
    pts = np.array([pt for p in polys for pt in p["outline"]])
    (minx, miny), (maxx, maxy) = pts.min(axis=0), pts.max(axis=0)
    view = (-MARGIN, -MARGIN, maxx - minx + 2 * MARGIN, maxy - miny + 2 * MARGIN)

    for fname, klayer in LAYERS.items():
        out = tmp / f"{fname}.svg"
        drill = "2" if klayer.endswith(".Cu") else "0"
        run([KICAD_CLI, "pcb", "export", "svg", "--mode-single", "--layers", klayer, "--page-size-mode", "2",
             "--exclude-drawing-sheet", "--black-and-white", "--drill-shape-opt", drill, "-o", str(out), str(pcb)])
        text = out.read_text()
        if klayer == "Edge.Cuts":
            # the plot frame starts at the outline's lower-left corner; check that before relying on it
            fx, fy = first_point(text)
            near = np.hypot(pts[:, 0] - minx - fx, pts[:, 1] - miny - fy).min()
            assert near < 0.05, f"{board}: Edge.Cuts plot is offset from the outline by {near:.3f} mm"
        (lay / f"{fname}.svg").write_text(clean_svg(text, view, f"{name} {fname}"))
    (lay / "outline.svg").write_text(outline_svg(polys, (minx, miny), view, f"{name} outline"))
    sizes = ", ".join(f"{p.name} {p.stat().st_size // 1024} KiB" for p in [ren / f"{name}.glb", *sorted(lay.glob("*.svg"))])
    print(f"{board}: {sizes}")


def main(argv: list[str]) -> int:
    boards = argv or list(BOARDS)
    for b in boards:
        if b not in BOARDS:
            print(f"unknown board '{b}' ({'|'.join(BOARDS)})", file=sys.stderr)
            return 2
    with tempfile.TemporaryDirectory() as t:
        for b in boards:
            export_board(b, Path(t))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
