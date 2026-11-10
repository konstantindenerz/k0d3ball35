# SPDX-License-Identifier: MIT
"""The texts the page translates, and how complete docs/i18n/<lang>.json is.

The English text is the key (docs/js/i18n.js). Keys come from three places:
- `t('…')` literals in docs/js (the first argument must be one single-quoted literal);
- `data-i18n` elements and `data-i18n-aria|title|content` attributes of docs/index.html;
- the data fields the tabs pass through t() (DATA_FIELDS below), read from docs/data/*.json.

A text with no word in it ("1.6 mm", "121 x 87 mm") needs no translation and is not a key.
Not a data generator: build.py's GENERATORS does not list it.
"""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1]
LANGS = ("ja", "zh-CN", "ru")
CATALOGS = DOCS / "i18n"

T_LITERAL = re.compile(r"(?<![\w.$])t\(\s*'((?:[^'\\\n]|\\.)*)'")
# a template/double-quoted literal or a ternary as the key: invisible to T_LITERAL
T_BAD = re.compile(r"(?<![\w.$])t\(\s*([`\"]|[^'`)]+ \?)")
PLACEHOLDER = re.compile(r"\{(\w+)\}")
UNITS = re.compile(r"\b(mm|oz|deg|mAh|CPI|x|V|N)\b")


def needs_translation(s: str) -> bool:
    return bool(re.search(r"[A-Za-z]{2,}", UNITS.sub("", s)))


def _unescape(s: str) -> str:
    return re.sub(r"\\(.)", r"\1", s)


def js_keys() -> set[str]:
    out = set()
    for js in sorted((DOCS / "js").rglob("*.js")):
        out |= {_unescape(m) for m in T_LITERAL.findall(js.read_text())}
    return out


def js_violations() -> list[str]:
    """t(`…`), t("…") or t(cond ? 'a' : 'b'): the extractor would not see the key."""
    out = []
    for js in sorted((DOCS / "js").rglob("*.js")):
        for i, line in enumerate(js.read_text().splitlines(), 1):
            if T_BAD.search(line):
                out.append(f"{js.relative_to(DOCS)}:{i}")
    return out


class _Static(HTMLParser):
    ATTRS = {"data-i18n-aria": "aria-label", "data-i18n-title": "title", "data-i18n-content": "content"}

    def __init__(self):
        super().__init__()
        self.keys: set[str] = set()
        self._text: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for marker, attr in self.ATTRS.items():
            if marker in a:
                self.keys.add(a[marker] or a.get(attr, ""))
        if "data-i18n" in a:
            if a["data-i18n"]:
                self.keys.add(a["data-i18n"])
            else:
                self._text = []
        # the tabs' sheet titles: main.js passes data-title through t()
        if "data-title" in a:
            self.keys.add(a["data-title"])

    def handle_data(self, data):
        if self._text is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if self._text is not None:
            self.keys.add("".join(self._text).strip())
            self._text = None


def html_keys() -> set[str]:
    p = _Static()
    p.feed((DOCS / "index.html").read_text())
    return {k for k in p.keys if k}


def _data(name: str) -> dict:
    return json.loads((DOCS / "data" / f"{name}.json").read_text())


def data_keys() -> set[str]:
    """The data texts the tabs show through t(); keep in step with docs/js/tabs/*.js."""
    out: set[str] = set()
    site = _data("site")
    for f in site["facts"]:
        out |= {f["label"], f["tpl"]}
    for d in site["docs"]:
        out |= {d["title"], d["text"]}

    parts = _data("parts")
    out |= {g["label"] for g in parts["groups"]}
    for p in parts["parts"]:
        # case.js lists the parts of a half without the ", left|right" suffix
        out |= {p["name"], re.sub(r", (left|right)$", "", p["name"]), p["role"]}
    out |= {pv["caption"] for pv in parts["previews"] if pv.get("caption")}
    out |= {v["label"] for v in parts["trackball"]["variants"]}

    for b in _data("pcbs")["boards"]:
        out.add(b["name"])
        if b.get("notes"):
            out.add(b["notes"])
        for k, v in b["facts"]:
            out |= {str(k), str(v)}
        for p in b["parts"]:
            out |= {p["role"], p["side"]}
        out |= {l["label"] for l in b["layers"]}

    km = _data("keymap")
    for k in km["keys"]:
        out |= {k["half"], k["name"]}
    for L in km["layers"]:
        out |= {L["access"], L["content"]}
    for m in km["pointer"]["modes"]:
        out |= set(m["effect"])
    return out


def keys() -> set[str]:
    return {k for k in js_keys() | html_keys() | data_keys() if k and needs_translation(k)}


def catalog(lang: str) -> dict[str, str]:
    path = CATALOGS / f"{lang}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def report(lang: str, wanted: set[str] | None = None) -> dict[str, list[str]]:
    """missing: keys without a translation; stale: catalog entries no key uses;
    placeholders: translations whose {names} differ from the English."""
    wanted = keys() if wanted is None else wanted
    cat = catalog(lang)
    return {
        "missing": sorted(wanted - cat.keys()),
        "stale": sorted(cat.keys() - wanted),
        "placeholders": sorted(k for k, v in cat.items()
                               if k in wanted and sorted(PLACEHOLDER.findall(k)) != sorted(PLACEHOLDER.findall(v))),
    }
