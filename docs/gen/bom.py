# SPDX-License-Identifier: MIT
"""docs/data/bom.json: the bill of materials of spec/03-bom.md as sections of tables.

Each `## N. Title` heading starts a section; its markdown tables keep their header and rows, its
paragraphs are kept as text. A cell is a list of runs: a plain string, or {"text", "href"} for a
markdown link or a bare URL (shown as the host name). Emphasis markers are dropped, code spans
keep their text. Nothing is added: no prices or parts that are not in the file.

Two summaries ride along for the top of the Build tab:
- cost: the "Totals" table of the BOM as numbers per group, its total row and the notes below it
- guide: from spec/04-build-guide.md the time estimate of the intro, the tools list of chapter 1 and
  the chapter list (with the anchors GitHub gives the headings)
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import REPO

SOURCE = "spec/03-bom.md"
GUIDE = "spec/04-build-guide.md"
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


def cost(sections: list) -> dict:
    """The Totals section: [{label, eur}] per group, the total row's text, the notes."""
    sec = next(s for s in sections if s["title"].lower() == "totals")
    table = next(b["table"] for b in sec["blocks"] if "table" in b)
    groups, total = [], None
    for label, eur in ((run_text(r[0]).strip(), run_text(r[1]).strip()) for r in table["rows"]):
        if label.lower() == "total":
            total = eur
        else:
            groups.append({"label": label, "eur": float(eur)})
    amount = re.search(r"(\d+)\s*EUR", total)
    notes = [b["text"] for b in sec["blocks"] if "text" in b]
    return {"section": sec["number"], "groups": groups, "total_text": total,
            "total": int(amount[1]), "notes": notes}


def github_anchor(heading: str) -> str:
    """The id GitHub gives a markdown heading: lower case, punctuation dropped, spaces to dashes."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def guide() -> dict:
    md = (REPO / GUIDE).read_text()
    intro = md.split("\n## ", 1)[0]
    time = re.search(r"(Plan [^.]+)\.", " ".join(intro.split()))
    tools_block = re.search(r"^Tools:\n\n(.*?)(?:\n\n|\Z)", md, flags=re.M | re.S)[1]
    tools = [_plain(" ".join(t.split())) for t in re.split(r"^\* ", tools_block, flags=re.M) if t.strip()]
    chapters = [{"number": int(m[1]), "title": _plain(m[2].strip()), "anchor": github_anchor(f"{m[1]}. {m[2]}")}
                for m in re.finditer(r"^## (\d+)\.\s+(.+)$", md, flags=re.M)]
    return {"source": GUIDE, "time": time[1] if time else None, "tools": tools, "chapters": chapters}


def build() -> dict:
    md = (REPO / SOURCE).read_text()
    title = re.search(r"^#\s+(.+)$", md, flags=re.M)[1].strip()
    intro, sections = parse_sections(md)
    return {"source": SOURCE, "title": title, "intro": intro, "sections": sections,
            "cost": cost(sections), "guide": guide()}
