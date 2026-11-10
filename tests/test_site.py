# SPDX-License-Identifier: MIT
"""The published page in docs/: data files current, every file it loads exists in the repo,
the shell lists every tab."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = DOCS / "data"
REPO_PATH = re.compile(r"^(hardware|spec|firmware|issues|scripts)/[\w./+-]+\.\w+$")


def _strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)
    elif isinstance(obj, str):
        yield obj


@pytest.fixture(scope="module")
def site() -> dict:
    return json.loads((DATA / "site.json").read_text())


@pytest.fixture(scope="module")
def tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return set(out.split())


def test_data_files_are_current():
    """docs/data is generated; `make site` after a layout, case or board change keeps it current."""
    r = subprocess.run([sys.executable, str(DOCS / "build.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_every_file_the_page_loads_is_in_the_repo(tracked):
    """The page fetches repo paths from raw.githubusercontent.com, so each one has to be committed."""
    paths = {s for f in DATA.glob("*.json") for s in _strings(json.loads(f.read_text())) if REPO_PATH.match(s)}
    assert paths, "the data names no repo files at all"
    missing = sorted(p for p in paths if not (ROOT / p).is_file())
    untracked = sorted(p for p in paths if p not in tracked and p not in missing)
    assert not missing, f"named in docs/data but not on disk: {missing}"
    assert not untracked, f"named in docs/data but not committed: {untracked}"


def test_shell_lists_every_tab(site):
    html = (DOCS / "index.html").read_text()
    for i, tab in enumerate(site["tabs"], 1):
        tid = tab["id"]
        assert f'href="#{tid}" data-tab="{tid}"><small>{i}</small>' in html, f"nav entry for {tid}"
        assert f'id="tab-{tid}"' in html, f"section for {tid}"
        assert (DOCS / "js" / "tabs" / f"{tid}.js").is_file(), f"module for {tid}"
        assert (DOCS / "css" / "tabs" / f"{tid}.css").is_file(), f"stylesheet for {tid}"
        assert f'href="css/tabs/{tid}.css"' in html


def test_shell_stays_small_and_pins_three():
    html = (DOCS / "index.html").read_text()
    assert len(html) < 50_000, "nothing is inlined into the shell any more"
    assert not re.search(r"[A-Za-z0-9+/]{2000,}", html), "no base64 blobs"
    versions = set(re.findall(r"three@([\w.]+)/", html))
    assert versions and all(re.fullmatch(r"\d+\.\d+\.\d+", v) for v in versions) and len(versions) == 1


def test_modules_import_only_pinned_or_local_code():
    """ES modules may import 'three', 'three/addons/...' (both pinned in the importmap) or relative files."""
    for js in (DOCS / "js").rglob("*.js"):
        for spec in re.findall(r"""(?:from\s+|import\s*\(\s*)['"`]([^'"`]+)['"`]""", js.read_text()):
            ok = spec == "three" or spec.startswith("three/addons/") or spec.startswith(".")
            assert ok, f"{js.relative_to(ROOT)} imports {spec}"
            if spec.startswith(".") and "${" not in spec:
                assert (js.parent / spec).resolve().is_file(), f"{js.relative_to(ROOT)}: {spec} missing"


def test_layout_names_the_case_stls(tracked):
    layout = json.loads((DATA / "layout.json").read_text())
    for half, h in layout["halves"].items():
        assert set(h["case_files"]) == {"tray", "cap", "lid", "lid_folded"}
        for path in h["case_files"].values():
            assert path in tracked and half in path


def test_explorer_loads_every_case_part():
    """The Explorer fetches each half's case STLs by the case_files keys; a key the module does not
    name would silently leave a part out of the exploded view."""
    layout = json.loads((DATA / "layout.json").read_text())
    js = (DOCS / "js" / "tabs" / "explorer.js").read_text()
    names = re.search(r"CASE_KEYS\s*=\s*\[([^\]]*)\]", js)
    assert names, "explorer.js lists the case parts it loads in CASE_KEYS"
    keys = set(re.findall(r"'(\w+)'", names.group(1)))
    for half, h in layout["halves"].items():
        assert keys == set(h["case_files"]), f"{half}: explorer loads {sorted(keys)}, layout has {sorted(h['case_files'])}"
    for k in keys:
        assert f"caseMesh('{k}'" in js, f"explorer.js never places the {k} mesh"


# ---------------------------------------------------------------- keymap, build and overview tabs

KEYMAP_FILE = ROOT / "firmware/zmk-config/config/k0d3ball35.keymap"


def _keymap_source_layers() -> list[tuple[str, int]]:
    """(display-name, binding count) per layer, read straight from the keymap file."""
    text = re.sub(r"/\*.*?\*/", " ", KEYMAP_FILE.read_text(), flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    out = []
    for name, body in re.findall(r'display-name\s*=\s*"([^"]+)";\s*bindings\s*=\s*<(.*?)>;', text, flags=re.S):
        out.append((name, sum(1 for tok in body.split() if tok.startswith("&"))))
    return out


@pytest.fixture(scope="module")
def keymap() -> dict:
    return json.loads((DATA / "keymap.json").read_text())


def test_keymap_layers_match_the_keymap_file(keymap):
    src = _keymap_source_layers()
    assert [l["name"] for l in keymap["layers"]] == [n for n, _ in src]
    layout = json.loads((DATA / "layout.json").read_text())
    n_keys = sum(len(h["keys"]) for h in layout["halves"].values())
    assert n_keys == 35
    for (name, count), layer in zip(src, keymap["layers"]):
        assert count == n_keys, f"{name}: the keymap file has {count} bindings"
        assert len(layer["bindings"]) == n_keys, f"{name}: keymap.json has {len(layer['bindings'])} bindings"
        assert [b["pos"] for b in layer["bindings"]] == list(range(n_keys))


def test_every_physical_key_gets_one_binding_per_layer(keymap):
    """The matrix transform maps the 35 binding positions onto the 35 switches, one to one."""
    layout = json.loads((DATA / "layout.json").read_text())
    physical = {(half, k["ref"]) for half, h in layout["halves"].items() for k in h["keys"]}
    mapped = [(k["half"], k["ref"]) for k in keymap["keys"]]
    assert len(mapped) == len(set(mapped)), "two binding positions land on the same switch"
    assert set(mapped) == physical


def test_keymap_follows_the_shield_transform(keymap):
    dtsi = (ROOT / "firmware/zmk-config/config/boards/shields/k0d3ball35/k0d3ball35.dtsi").read_text()
    cells = [(int(r), int(c)) for r, c in re.findall(r"RC\((\d+),\s*(\d+)\)", dtsi)]
    assert [(k["row"], k["matrix_col"]) for k in keymap["keys"]] == cells
    # the ball half keeps the inner thumbs: position 33 is its 20 degree key, 34 the 10 degree key
    assert (keymap["keys"][33]["half"], keymap["keys"][33]["ref"]) == ("right", "SW34")
    assert keymap["layers"][0]["bindings"][31]["tap"] == "Space"


def test_keymap_labels_and_combos(keymap):
    base = keymap["layers"][0]["bindings"]
    assert (base[10]["tap"], base[10]["hold"], base[10]["kind"]) == ("A", "Gui", "mod-tap")
    assert (base[31]["hold"], base[31]["layer"]) == ("Nav", "Nav")
    num = next(l for l in keymap["layers"] if l["name"] == "Num")["bindings"]
    assert (num[0]["tap"], num[1]["tap"]) == ("[", "7")
    text = KEYMAP_FILE.read_text()
    assert len(keymap["combos"]) == len(re.findall(r"^\s*key-positions\s*=", text, flags=re.M))
    assert keymap["pointer"]["auto_layer"] == "Mouse"
    assert {m["layer"] for m in keymap["pointer"]["modes"]} == {"Scroll", "Snipe"}


def _md_table_rows_per_section(md: str) -> dict[str, int]:
    out: dict[str, int] = {}
    section = None
    lines = md.splitlines()
    for i, line in enumerate(lines):
        h = re.match(r"^##\s+(?:\d+\.\s+)?(.+)$", line)
        if h:
            section = h[1].strip()
            out[section] = 0
        elif section and line.startswith("|") and not re.match(r"^\|[\s:|-]+\|\s*$", line):
            is_header = i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1])
            if not is_header:
                out[section] += 1
    return out


def test_bom_rows_equal_the_markdown_tables():
    bom = json.loads((DATA / "bom.json").read_text())
    want = _md_table_rows_per_section((ROOT / "spec/03-bom.md").read_text())
    got = {s["title"]: sum(len(b["table"]["rows"]) for b in s["blocks"] if "table" in b) for s in bom["sections"]}
    assert got == want
    for s in bom["sections"]:
        for b in s["blocks"]:
            if "table" in b:
                assert all(len(r) == len(b["table"]["header"]) for r in b["table"]["rows"]), s["title"]


def test_status_tickets_equal_the_tracker():
    sys.path.insert(0, str(ROOT / "scripts"))
    import issues  # noqa: E402

    tickets, problems = issues.load_tickets()
    assert not problems
    status = json.loads((DATA / "status.json").read_text())
    want = {(t.slug, t.priority) for t in tickets if t.status in ("open", "in-progress")}
    got = {(t["slug"], p) for p, g in status["tickets"].items() for t in g}
    assert got == want
    steps = status["before_ordering"]["steps"]
    roadmap = (ROOT / "spec/09-roadmap.md").read_text()
    section = roadmap.split("## r2 verification before ordering", 1)[1].split("\n## ", 1)[0]
    assert [s["number"] for s in steps] == [int(n) for n in re.findall(r"^(\d+)\.\s", section, flags=re.M)]
    assert all(s["state"] in ("done", "partly", "open") for s in steps)


def test_site_facts_match_their_sources(site):
    facts = {f["id"]: f for f in site["facts"]}
    right = json.loads((ROOT / "hardware/layout/output/points-right.json").read_text())
    left = json.loads((ROOT / "hardware/layout/output/points-left.json").read_text())
    assert facts["keys"]["value"] == len(left["keys"]) + len(right["keys"]) == 35
    assert (facts["pitch"]["x"], facts["pitch"]["y"]) == (right["pitch"]["x"], right["pitch"]["y"])
    assert facts["ball"]["value"] == right["trackball"]["ball_diameter"] == 19.05
    overlay = (ROOT / "firmware/zmk-config/config/boards/shields/k0d3ball35/k0d3ball35_right.overlay").read_text()
    assert f'"pixart,{facts["ball"]["sensor"].lower()}"' in overlay
    assert f'res-cpi = <{facts["ball"]["cpi"]}>' in overlay
    stack = json.loads((ROOT / "hardware/trackball-cradle/stack.json").read_text())["variants"]["19mm-pocket"]
    assert facts["ball_top"]["value"] == stack["ball_top_above_pcb_top"]
    assert facts["battery"]["cell"] == right["battery"]["cell"]
    assert facts["battery"]["value"] == right["battery"]["capacity_mah"]
    assert "nice!nano v2" in facts["controller"]["text"]
    assert "Choc V1" in facts["switch"]["text"]
    assert facts["firmware"]["revision"] in (ROOT / "firmware/zmk-config/config/west.yml").read_text()
    for f in site["facts"]:
        assert (ROOT / f["source"]).is_file(), f["source"]
    lic = {l["id"]: l["path"] for l in site["licences"]}
    assert lic == {"MIT": "LICENSE", "CERN-OHL-P-2.0": "LICENSE-HARDWARE"}
    assert (ROOT / "LICENSE").read_text().startswith("MIT License")
    assert "CERN Open Hardware Licence Version 2 - Permissive" in (ROOT / "LICENSE-HARDWARE").read_text()[:200]
