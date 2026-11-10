# SPDX-License-Identifier: MIT
"""docs/data/bom.json: the bill of materials of spec/03-bom.md as sections of tables.

Each `## N. Title` heading starts a section; its markdown tables keep their header and rows, its
paragraphs are kept as text. A cell is a list of runs: a plain string, or {"text", "href"} for a
markdown link or a bare URL (shown as the host name). Emphasis markers are dropped, code spans
keep their text. Nothing is added: no prices or parts that are not in the file.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import REPO

SOURCE = "spec/03-bom.md"
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)|(https?://[^\s,;)]+[^\s,;).])")


def _plain(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_\s][^_]*)_(?!\w)", r"\1", text)
    return text


def runs(text: str, base: str = "spec/") -> list:
    """Markdown cell -> runs. Relative links (to other spec files) become repo paths."""
    out: list = []
    pos = 0
    text = text.strip()
    for m in LINK.finditer(text):
        if m.start() > pos:
            out.append(_plain(text[pos:m.start()]))
        if m[1] is not None:
            href = m[2]
            if not re.match(r"https?://", href):
                href = {"repo": (base + href).replace("spec/../", "")}
            out.append({"text": _plain(m[1]), "href": href})
        else:
            url = m[3]
            host = urlparse(url).netloc.removeprefix("www.")
            out.append({"text": host, "href": url})
        pos = m.end()
    if pos < len(text):
        out.append(_plain(text[pos:]))
    merged: list = []
    for r in out:
        if isinstance(r, str) and merged and isinstance(merged[-1], str):
            merged[-1] += r
        elif r != "":
            merged.append(r)
    return merged


def run_text(cell: list) -> str:
    return "".join(r if isinstance(r, str) else r["text"] for r in cell)


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_sections(md: str, base: str = "spec/") -> tuple[list, list]:
    """-> (intro paragraphs, sections). A section: {number, title, blocks}, a block is
    {"table": {"header", "rows"}} or {"text": runs}."""
    intro: list = []
    sections: list = []
    blocks = intro
    lines = md.splitlines()
    i = 0
    para: list[str] = []

    def flush():
        if para:
            blocks.append({"text": runs(" ".join(para), base)})
            para.clear()

    while i < len(lines):
        line = lines[i]
        h = re.match(r"^##\s+(?:(\d+)\.\s+)?(.+)$", line)
        if h:
            flush()
            sections.append({"number": int(h[1]) if h[1] else None, "title": h[2].strip(), "blocks": []})
            blocks = sections[-1]["blocks"]
        elif line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            flush()
            header = [_plain(c) for c in split_row(line)]
            rows = []
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                cells = split_row(lines[i])
                cells += [""] * (len(header) - len(cells))
                rows.append([runs(c, base) for c in cells[:len(header)]])
                i += 1
            blocks.append({"table": {"header": header, "rows": rows}})
            continue
        elif line.startswith("#") or line.startswith("!["):
            flush()
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
        i += 1
    flush()
    return intro, sections


def build() -> dict:
    md = (REPO / SOURCE).read_text()
    title = re.search(r"^#\s+(.+)$", md, flags=re.M)[1].strip()
    intro, sections = parse_sections(md)
    return {"source": SOURCE, "title": title, "intro": intro, "sections": sections}
