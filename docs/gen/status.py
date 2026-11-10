# SPDX-License-Identifier: MIT
"""docs/data/status.json: where the project stands before the first order.

- tickets: the open and in-progress tickets of issues/ (parsed by scripts/issues.py), grouped by
  priority
- before_ordering: the numbered steps of "r2 verification before ordering" in spec/09-roadmap.md.
  The state comes from how each step starts ("Done:" -> done; "Done (...)", "Mostly done" or a
  "Done ... Open:" pair -> partly; anything else -> open); tickets named in the step are linked
- order: rows ticked [x] versus [ ] per section of spec/12-order-checklist.md
"""
from __future__ import annotations

import importlib.util
import re

from . import REPO

ROADMAP = "spec/09-roadmap.md"
CHECKLIST = "spec/12-order-checklist.md"
ORDER_TICKET = "hw-jlcpcb-order-r1"
SHOWN = ("open", "in-progress")


def _issues():
    spec = importlib.util.spec_from_file_location("issues", REPO / "scripts/issues.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tickets() -> tuple[dict, dict]:
    mod = _issues()
    found, problems = mod.load_tickets()
    assert not problems, problems
    groups: dict[str, list] = {p: [] for p in mod.PRIORITIES}
    for t in found:
        if t.status in SHOWN:
            groups[t.priority].append({"slug": t.slug, "title": t.title, "type": t.type, "area": t.area,
                                       "status": t.status, "created": t.created,
                                       "path": f"issues/{t.path.name}"})
    for g in groups.values():
        g.sort(key=lambda t: (t["status"] != "in-progress", t["area"], t["slug"]))
    every = {t.slug: t.status for t in found}
    return groups, every


def _plain(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("`", "")).strip()


def _first_sentence(s: str) -> str:
    m = re.match(r"(.+?[.;])(\s|$)", s)
    out = (m[1] if m else s).rstrip(".;")
    return out


def roadmap_steps(statuses: dict[str, str]) -> dict:
    text = (REPO / ROADMAP).read_text()
    sec = re.search(r"^## (r2 verification before ordering)\n(.*?)(?=^## )", text, flags=re.M | re.S)
    title, body = sec[1], sec[2]
    intro = _plain(body.split("\n1.")[0])
    items = re.findall(r"^(\d+)\.\s+(.*?)(?=^\d+\.\s|\Z)", body, flags=re.M | re.S)
    steps = []
    for num, raw in items:
        raw = " ".join(raw.split())
        head, sep, rest = raw.partition(":")
        h = head.strip().lower()
        if not sep or len(head) > 60:
            head, rest = "", raw
        if h == "done" and "Open" not in rest:
            state = "done"
        elif h.startswith("done") or h.startswith("mostly done"):
            state = "partly"
        else:
            state = "open"
        summary = re.sub(r"\s*\((?:`[a-z0-9-]+`(?:,\s*)?)+\)", "", rest)
        open_part = None
        m = re.search(r"\bOpen(?: for the user)?:\s*(.*)$", raw)
        if m and state != "open":
            open_part = _plain(_first_sentence(m[1]))
        slugs = [s for s in dict.fromkeys(re.findall(r"`([a-z]+-[a-z0-9-]+)`", raw)) if s in statuses]
        steps.append({"number": int(num), "state": state, "label": _plain(head) or None,
                      "summary": _plain(_first_sentence(summary.strip())), "open": open_part,
                      "text": _plain(raw),
                      "tickets": [{"slug": s, "status": statuses[s], "path": f"issues/{s}.md"} for s in slugs]})
    return {"source": ROADMAP, "title": title, "intro": intro, "steps": steps}


def order_checklist() -> dict:
    text = (REPO / CHECKLIST).read_text()
    sections = []
    for m in re.finditer(r"^## (\d+)\.\s+(.+?)\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S):
        done = len(re.findall(r"^\| \[x\] \|", m[3], flags=re.M))
        todo = len(re.findall(r"^\| \[ \] \|", m[3], flags=re.M))
        if done or todo:
            sections.append({"number": int(m[1]), "title": re.sub(r"\s*\((open)\)$", "", m[2].strip()),
                             "done": done, "total": done + todo})
    return {"source": CHECKLIST, "sections": sections,
            "done": sum(s["done"] for s in sections), "total": sum(s["total"] for s in sections)}


def build() -> dict:
    groups, statuses = tickets()
    return {
        "tickets": groups,
        "ticket_counts": {p: len(g) for p, g in groups.items()},
        "before_ordering": roadmap_steps(statuses),
        "order": {**order_checklist(), "pcb_ticket": {"slug": ORDER_TICKET, "status": statuses.get(ORDER_TICKET),
                                                      "path": f"issues/{ORDER_TICKET}.md"}},
    }
