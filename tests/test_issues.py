# SPDX-License-Identifier: MIT
"""The ticket folder is valid and its index is current."""
from __future__ import annotations

import issues


def test_frontmatter_valid():
    tickets, problems = issues.load_tickets()
    assert not problems, "\n".join(problems)
    assert tickets, "no tickets found in issues/"


def test_index_up_to_date():
    tickets, _ = issues.load_tickets()
    rendered = issues.render_index(tickets)
    assert issues.INDEX.exists(), "issues/README.md missing, run scripts/issues.py"
    assert issues.INDEX.read_text(encoding="utf-8") == rendered, "issues/README.md is stale, run scripts/issues.py"


def test_every_ticket_has_sections():
    tickets, _ = issues.load_tickets()
    for t in tickets:
        text = t.path.read_text(encoding="utf-8")
        for heading in ("## Context", "## Acceptance criteria"):
            assert heading in text, f"{t.path.name}: missing '{heading}'"
