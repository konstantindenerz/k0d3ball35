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


def test_repo_files_load_from_the_commit_not_the_branch():
    """raw.githubusercontent.com serves the old file under `main` for minutes after a push, and the
    browser then keeps those old bytes under the new ?v= URL. A commit URL cannot go stale, so the
    page resolves the branch to its sha before the first tab mounts and builds every raw URL from it."""
    assets = (DOCS / "js" / "assets.js").read_text()
    main = (DOCS / "js" / "main.js").read_text()
    assert re.search(r"raw\.githubusercontent\.com/\$\{REPO\}/\$\{pinned \|\|", assets), \
        "assetUrl no longer builds raw URLs from the pinned commit"
    assert "pinned = c.sha" in assets, "loadCommit no longer pins the commit"
    start = main.index("await Promise.all(")
    assert "loadCommit()" in main[start:main.index("\n", start)], "main.js mounts tabs before the commit is known"
    assert main.index("loadCommit()") < main.rindex("route();"), "the first tab mounts before the commit is known"


def test_shell_lists_every_tab(site):
    html = (DOCS / "index.html").read_text()
    for i, tab in enumerate(site["tabs"], 1):
        tid = tab["id"]
        assert f'href="#{tid}" data-tab="{tid}"><small>{i}</small>' in html, f"nav entry for {tid}"
        assert f'id="tab-{tid}"' in html, f"section for {tid}"
        assert (DOCS / "js" / "tabs" / f"{tid}.js").is_file(), f"module for {tid}"
        assert (DOCS / "css" / "tabs" / f"{tid}.css").is_file(), f"stylesheet for {tid}"
        assert re.search(rf'href="css/tabs/{tid}\.css\?v=[0-9a-f]{{10}}"', html), f"versioned stylesheet for {tid}"


def test_shell_stays_small_and_pins_three():
    html = (DOCS / "index.html").read_text()
    assert len(html) < 50_000, "nothing is inlined into the shell any more"
    assert not re.search(r"[A-Za-z0-9+/]{2000,}", html), "no base64 blobs"
    versions = set(re.findall(r"three@([\w.]+)/", html))
    assert versions and all(re.fullmatch(r"\d+\.\d+\.\d+", v) for v in versions) and len(versions) == 1


def test_every_url_the_page_loads_is_versioned():
    """Content hashes on every local module, stylesheet, data file and fetched repository file, so
    one page load never mixes two versions from different caches (the mirrored-tray report)."""
    html = (DOCS / "index.html").read_text()
    imports = json.loads(re.search(r'<script type="importmap">(.*?)</script>', html)[1])["imports"]
    for js in (DOCS / "js").rglob("*.js"):
        rel = js.relative_to(DOCS).as_posix()
        assert re.fullmatch(rf"\./{re.escape(rel)}\?v=[0-9a-f]{{10}}", imports[f"./{rel}"]), rel
    assert re.search(r'<script type="module" src="js/main\.js\?v=[0-9a-f]{10}"></script>', html)
    data = json.loads(re.search(r'<script type="application/json" id="dataVersions">(.*?)</script>', html)[1])
    assert set(data) == {p.stem for p in DATA.glob("*.json")} | {f"i18n/{p.stem}" for p in (DOCS / "i18n").glob("*.json")}
    versions = json.loads((DATA / "versions.json").read_text())
    for name in ("parts", "layout", "pcbs"):
        for s in _strings(json.loads((DATA / f"{name}.json").read_text())):
            if re.search(r"\.(stl|glb|svg|png)$", s) and (ROOT / s).is_file():
                assert s in versions, s
    # literals the page carries in its own code rather than in the data files
    for literal in ("spec/images/concept-render.png",):
        assert literal in versions


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def test_preview_server_disables_the_cache():
    assert "no-store" in (ROOT / "scripts/site_serve.py").read_text()
    assert "scripts/site_serve.py" in (ROOT / "Makefile").read_text()


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
        # "sensor" is the bought module's envelope (trackball-cradle/ref), placed like the cradle
        ball = {"cover", "cradle", "clip", "sensor"} if h["ball"] else set()
        assert set(h["case_files"]) == {"tray", "guard", "cap", "lid", "lid_folded"} | ball
        for k, path in h["case_files"].items():
            assert path in tracked and (k in ("cradle", "sensor") or half in path)


def test_explorer_loads_every_case_part():
    """The Explorer fetches each half's case STLs by the case_files keys; a key the module does not
    name would silently leave a part out of the exploded view."""
    layout = json.loads((DATA / "layout.json").read_text())
    js = (DOCS / "js" / "tabs" / "explorer.js").read_text()
    names = re.search(r"CASE_KEYS\s*=\s*\[([^\]]*)\]", js)
    assert names, "explorer.js lists the case parts it loads in CASE_KEYS"
    keys = set(re.findall(r"'(\w+)'", names.group(1)))
    assert keys == set().union(*(h["case_files"] for h in layout["halves"].values())), keys
    for k in keys:
        assert f"caseMesh('{k}'" in js, f"explorer.js never places the {k} mesh"


def test_explorer_draws_the_real_cradle():
    """r2.4 shipped an Explorer whose cradle was a box and a disc drawn from stack numbers, long
    after the real part had changed shape. The cradle and the pocket cover are the STLs now."""
    js = (DOCS / "js" / "tabs" / "explorer.js").read_text()
    assert "caseMesh('cradle'" in js and "caseMesh('cover'" in js
    assert "BoxGeometry(S.housing_x" not in js and "cup skirt" not in js, "primitive cradle still drawn"


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




def test_site_facts_match_their_sources(site):
    facts = {f["id"]: f for f in site["facts"]}
    right = json.loads((ROOT / "hardware/layout/output/points-right.json").read_text())
    left = json.loads((ROOT / "hardware/layout/output/points-left.json").read_text())
    assert facts["keys"]["value"] == len(left["keys"]) + len(right["keys"]) == 35
    assert facts["keys"]["pitch"] == [right["pitch"]["x"], right["pitch"]["y"]]
    assert facts["ball"]["value"] == right["trackball"]["ball_diameter"] == 19.05
    overlay = (ROOT / "firmware/zmk-config/config/boards/shields/k0d3ball35/k0d3ball35_right.overlay").read_text()
    assert f'"pixart,{facts["ball"]["sensor"].lower()}"' in overlay
    assert facts["battery"]["cell"] == right["battery"]["cell"]
    assert facts["battery"]["value"] == right["battery"]["capacity_mah"]
    assert "nice!nano v2" in facts["controller"]["text"]
    assert "Choc V1" in facts["switch"]["text"]
    st = site["status"]
    assert st["pcbs_ordered"] == ("status: done" in (ROOT / st["order_ticket"]).read_text())
    assert f"**{st['cost']}**" in (ROOT / "spec/03-bom.md").read_text()
    for d in site["docs"]:
        assert (ROOT / d["path"]).is_file(), d["path"]
    for f in site["facts"]:
        assert (ROOT / f["source"]).is_file(), f["source"]
    footer = (ROOT / "docs/index.html").read_text()
    assert "MIT" in footer and "CERN-OHL-P-2.0" in footer
    assert (ROOT / "LICENSE").read_text().startswith("MIT License")


# ---------------------------------------------------------------- PCBs tab (make pcb-3d)
def _glb(path: Path) -> tuple[dict, bytes]:
    """Minimal GLB reader: header, JSON chunk, BIN chunk."""
    import struct

    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF" and version == 2, f"{path.name}: not a glTF 2 binary"
    assert length == len(data), f"{path.name}: header length {length} != file size {len(data)}"
    off, js, bin_ = 12, None, b""
    while off < length:
        clen, ctype = struct.unpack_from("<II", data, off)
        if ctype == 0x4E4F534A:
            js = json.loads(data[off + 8: off + 8 + clen])
        elif ctype == 0x004E4942:
            bin_ = data[off + 8: off + 8 + clen]
        off += 8 + clen
    assert js is not None
    return js, bin_


@pytest.fixture(scope="module")
def pcbs() -> dict:
    return json.loads((DATA / "pcbs.json").read_text())


def test_pcbs_names_both_boards_with_existing_files(pcbs, tracked):
    # r2.4: the bought PAW3222 module replaced our sensor daughterboard, so the PCBs tab shows
    # the two halves only (issues/hw-paw3222-variant.md).
    assert [b["id"] for b in pcbs["boards"]] == ["left", "right"]
    for b in pcbs["boards"]:
        paths = [*b["files"].values(), *(l["path"] for l in b["layers"])]
        for p in paths:
            assert (ROOT / p).is_file(), f"{b['id']}: {p} missing"
            assert p in tracked, f"{b['id']}: {p} not committed"
        assert {l["id"] for l in b["layers"]} == {"F.Cu", "B.Cu", "F.Silkscreen", "B.Silkscreen", "F.Mask", "B.Mask", "Edge.Cuts"}


def test_pcb_layer_svgs_share_one_viewbox(pcbs):
    """The layer plot stacks the SVGs of a board, so they must have one coordinate frame."""
    for b in pcbs["boards"]:
        files = [b["files"]["outline"], *(l["path"] for l in b["layers"])]
        boxes = {p: re.search(r'viewBox="([^"]+)"', (ROOT / p).read_text()).group(1) for p in files}
        assert len(set(boxes.values())) == 1, f"{b['id']}: {boxes}"
        assert [float(v) for v in next(iter(boxes.values())).split()] == b["viewbox"]
        for p in files:
            text = (ROOT / p).read_text()
            assert not re.search(r"20\d\d-\d\d-\d\dT\d\d:", text), f"{p}: plot date left in, re-runs would churn git"


def test_pcb_glbs_are_gltf2_and_match_the_outline(pcbs):
    import numpy as np

    for b in pcbs["boards"]:
        js, bin_ = _glb(ROOT / b["files"]["glb"])
        assert "generated_at" not in js["asset"].get("extras", {}), "export timestamp left in"
        # world bounds of every POSITION accessor, with the node translations KiCad writes (no rotations or scales)
        lo, hi = np.full(3, np.inf), np.full(3, -np.inf)

        def walk(i, t):
            nonlocal lo, hi
            n = js["nodes"][i]
            # the sensor board used to be exempt here; with only the two halves left, every
            # GLB node must be a plain translation the way KiCad writes it (r2.4).
            assert "matrix" not in n and "rotation" not in n and "scale" not in n
            t = t + np.array(n.get("translation", [0, 0, 0]))
            if "mesh" in n and js["meshes"][n["mesh"]].get("name", "").startswith(b["stem"]):
                for p in js["meshes"][n["mesh"]]["primitives"]:
                    a = js["accessors"][p["attributes"]["POSITION"]]
                    lo = np.minimum(lo, t + a["min"])
                    hi = np.maximum(hi, t + a["max"])
            for c in n.get("children", []):
                walk(c, t)

        for r in js["scenes"][js.get("scene", 0)]["nodes"]:
            walk(r, np.zeros(3))
        size = (hi - lo) * 1000   # metres -> mm; glTF Y up, so the board plane is x/z
        w, h = b["size_mm"]
        assert abs(size[0] - w) < 0.3 and abs(size[2] - h) < 0.3, f"{b['id']}: GLB {size[0]:.2f} x {size[2]:.2f} vs outline {w} x {h}"
        assert abs(size[1] - b["thickness_mm"]) < 0.2, f"{b['id']}: GLB board stack {size[1]:.2f} mm"
        assert len(bin_) >= sum(v["byteLength"] for v in js["bufferViews"])


def test_makefile_has_pcb_3d():
    mk = (ROOT / "Makefile").read_text()
    assert re.search(r"^pcb-3d:.*## ", mk, re.M), "pcb-3d target with help text"
    assert re.search(r"^\.PHONY:.*\bpcb-3d\b", mk, re.M)
    assert "scripts/export_site_pcbs.py" in mk


# ---------------------------------------------------------------- parts.json (Case and Trackball tabs)
PART_DIRS = ("hardware/case/stl", "hardware/trackball-cradle/stl")


@pytest.fixture(scope="module")
def parts() -> dict:
    return json.loads((DATA / "parts.json").read_text())


def test_parts_lists_every_stl(parts):
    """Every STL of the case and the cradle is on the page or excluded with a reason."""
    on_disk = {str(p.relative_to(ROOT)) for d in PART_DIRS for p in (ROOT / d).glob("*.stl")}
    listed = {p["path"] for p in parts["parts"]}
    excluded = parts["excluded"]
    assert all(isinstance(r, str) and r.strip() for r in excluded.values()), "every exclusion needs a reason"
    excluded_paths = {p for p in on_disk if p.rsplit("/", 1)[1][:-4] in excluded}
    assert on_disk == listed | excluded_paths, (sorted(on_disk - listed - excluded_paths), sorted(listed - on_disk))
    assert not listed & excluded_paths
    groups = {g["id"] for g in parts["groups"]}
    for p in parts["parts"]:
        assert p["group"] in groups and p["name"] and p["role"] and (ROOT / p["doc"]).is_file()
        assert p["id"] == p["path"].rsplit("/", 1)[1][:-4]
    # the closed and folded lid pairs are display meshes, everything else is printed
    for p in parts["parts"]:
        assert p["printed"] == (not re.fullmatch(r"lid-(folded-)?(left|right)", p["id"])), p["id"]


def test_parts_facts_match_the_meshes(parts):
    trimesh = pytest.importorskip("trimesh")
    for p in parts["parts"]:
        m = trimesh.load(ROOT / p["path"], force="mesh")
        lo, hi = m.bounds
        # the page rounds to 0.01, so compare with the raw bounds (rounding both sides can differ by 0.01)
        assert p["bbox_min"] == pytest.approx(list(lo), abs=0.006), p["id"]
        assert p["bbox_max"] == pytest.approx(list(hi), abs=0.006), p["id"]
        assert p["triangles"] == len(m.faces), p["id"]
        assert p["watertight"] == bool(m.is_watertight), p["id"]


def test_parts_previews_exist(parts, tracked):
    paths = {pv["path"] for pv in parts["previews"]}
    paths |= {x for p in parts["parts"] for x in p["previews"]}
    paths |= {x for v in parts["trackball"]["variants"] for x in v["previews"]}
    assert paths
    for path in sorted(paths):
        assert (ROOT / path).is_file() and path.endswith(".png"), path
        assert path in tracked, f"{path} is not committed"
    known = {pv["path"] for pv in parts["previews"]}
    assert paths == known, "every preview a part names has a caption"


def test_trackball_numbers_equal_stack_json(parts):
    stack = json.loads((ROOT / "hardware/trackball-cradle/stack.json").read_text())["variants"]
    retention = json.loads((ROOT / "hardware/case/retention.json").read_text())["variants"]
    tb = parts["trackball"]
    ids = [v["id"] for v in tb["variants"]]
    assert set(ids) == set(stack) and tb["default"] == "19mm-pocket"
    by_id = {p["id"]: p for p in parts["parts"]}
    for v in tb["variants"]:
        s = stack[v["id"]]
        for key in ("ball_d", "ball_centre_z", "rim_z", "lens_reference_plane_dist", "ball_top_above_pcb_top",
                    "bearing_contact_z", "sensor_pcb_plane_z"):
            assert v["stack"][key] == pytest.approx(s[key], abs=0.0006), (v["id"], key)
        for key, val in v["retention"].items():
            ref = retention[v["id"]][key]
            assert val == (pytest.approx(ref, abs=0.0006) if isinstance(ref, float) else ref), (v["id"], key)
        assert v["cradle"] in by_id and by_id[v["cradle"]]["group"] == "cradle"
        assert v["retainer"] in by_id and by_id[v["retainer"]]["group"] == "retainer"
        # the cradle STL is in the stack frame: its rim is at rim_z and the ball centre on the z axis
        # (symmetric across the lean only: the tilted sensor sleeve sits on one side, +x since r2.4b)
        c = by_id[v["cradle"]]
        assert c["bbox_max"][2] == pytest.approx(s["rim_z"], abs=0.01)
        assert c["bbox_min"][2] == pytest.approx(s["lowest_plastic_z"], abs=0.01)
        assert s["window_az"] == 0
        assert abs(c["bbox_min"][1] + c["bbox_max"][1]) < 0.02


def test_every_sheet_says_the_design_is_untested():
    """Like the README's notice: a release stamp in the title block on every sheet, a short
    explanation behind it, and an 'untested' line next to every download."""
    html = (DOCS / "index.html").read_text()
    assert 'popovertarget="wip"' in html and 'id="wip" popover' in html
    assert "<span data-i18n>Preliminary</span> · </span><span data-i18n>untested</span>" in html
    assert "fabricated, printed or tested" in html and "README" in html
    for tab in ("case", "trackball", "pcbs"):
        assert 'class="untested"' in (DOCS / "js" / "tabs" / f"{tab}.js").read_text(), tab
    assert "Work in progress" in (ROOT / "README.md").read_text()


def test_wordmark_uses_kode_mono():
    """The name in the title block is set in Kode Mono (OFL, slashed zero, so k0d3 never reads as kOd3);
    headings keep Archivo and the font is actually requested from Google Fonts."""
    html = (DOCS / "index.html").read_text()
    css = (DOCS / "css/site.css").read_text()
    assert "family=Kode+Mono:wght@700" in html
    assert re.search(r'--wordmark:\s*"Kode Mono"', css)
    assert re.search(r"\.tb-name span \{[^}]*var\(--wordmark\)", css)
    assert re.search(r"\.display \{[^}]*var\(--display\)", css)
    # every place that shows the name, not just the title block
    assert re.search(r"\.ov-name \{[^}]*var\(--wordmark\)", (DOCS / "css/tabs/overview.css").read_text())
    assert re.search(r"\.xp-title \{[^}]*var\(--wordmark\)", (DOCS / "css/tabs/explorer.css").read_text())


# ---------------------------------------------------------------- translations (docs/i18n)
def _i18n():
    sys.path.insert(0, str(DOCS))
    from gen import i18n
    return i18n


def test_i18n_keys_are_extractable():
    """t() takes one single-quoted literal (or a data field), so the key list sees every text."""
    i18n = _i18n()
    assert not i18n.js_violations(), "t() with a template or double-quoted literal: " + ", ".join(i18n.js_violations())
    assert len(i18n.keys()) > 300


@pytest.mark.parametrize("lang", ["ja", "zh-CN", "ru"])
def test_i18n_catalog_complete(lang):
    """Every page text has a translation, none is left over, the {placeholders} match.
    `python docs/build.py --i18n` lists what to add or drop."""
    i18n = _i18n()
    r = i18n.report(lang)
    assert not r["missing"], f"{lang}: {len(r['missing'])} texts without a translation, e.g. {r['missing'][:5]}"
    assert not r["stale"], f"{lang}: {len(r['stale'])} unused entries, e.g. {r['stale'][:5]}"
    assert not r["placeholders"], f"{lang}: placeholders differ in {r['placeholders'][:5]}"
    assert not [k for k, v in i18n.catalog(lang).items() if not v.strip()], f"{lang}: empty translations"


def test_i18n_shell_offers_every_language():
    js = (DOCS / "js/i18n.js").read_text()
    for lang in ["en", "ja", "zh-CN", "ru"]:
        assert f"'{lang}'" in js or f"  {lang}: [" in js
    html = (DOCS / "index.html").read_text()
    assert 'id="langBtn"' in html and 'id="langMenu"' in html
    for lang in ["ja", "zh-CN", "ru"]:
        assert f'"i18n/{lang}":' in html, f"index.html versions block lacks i18n/{lang}; run `make site`"


# ---------------------------------------------------------------- attribution and link previews
@pytest.fixture(scope="module")
def index() -> str:
    return (DOCS / "index.html").read_text()


@pytest.fixture(scope="module")
def site_data() -> dict:
    return json.loads((DATA / "site.json").read_text())


def _meta(html: str, attr: str, value: str) -> str | None:
    m = re.search(rf'<meta {attr}="{re.escape(value)}" content="([^"]*)">', html)
    return m.group(1) if m else None


def test_the_footer_names_the_maker(index, site_data):
    """A visitor who reaches the bottom of the page should know whose project this is."""
    author = site_data["author"]
    footer = index[index.index('<footer class="foot">'):index.index("</footer>")]
    assert author["name"] in footer, "the footer does not name the author"
    assert f'href="{author["url"]}"' in footer, "the author's name is not linked"
    assert "Designed and built by" in footer
    assert "MIT" in footer and "CERN-OHL-P-2.0" in footer, "the licence line must survive"


def test_the_page_declares_its_author_and_canonical_url(index, site_data):
    assert _meta(index, "name", "author") == site_data["author"]["name"]
    canonical = re.search(r'<link rel="canonical" href="([^"]*)">', index)
    assert canonical and canonical.group(1) == site_data["site"]


def test_link_previews_are_absolute_and_agree_with_the_generator(index, site_data):
    """A scraper runs no JavaScript and resolves no relative path, so these must be absolute.

    The base URL lives once, in docs/gen/site.py, and reaches site.json from there; this holds
    the hand-written head to it so the domain cannot drift between the two.
    """
    site = site_data["site"]
    og = {m.group(1): m.group(2)
          for m in re.finditer(r'<meta property="og:([\w:]+)" content="([^"]*)">', index)}
    assert og["type"] == "website" and og["site_name"]
    assert og["url"] == site
    for key in ("title", "description", "image:alt"):
        assert og[key].strip(), f"og:{key} is empty"
    assert site_data["author"]["name"] in og["description"], "the preview text drops the author"
    assert og["image"].startswith(site), "og:image must be absolute and on the published site"
    assert _meta(index, "name", "twitter:card") == "summary_large_image"


def test_the_share_card_is_the_image_the_page_promises(index, site_data):
    """The card is committed, not rebuilt here: type rendering depends on the fonts installed.

    What must hold is that the file exists where og:image points and really has the dimensions
    the head declares - a scraper that is lied to about the size crops or rejects the image.
    """
    Image = pytest.importorskip("PIL.Image")
    og = {m.group(1): m.group(2)
          for m in re.finditer(r'<meta property="og:([\w:]+)" content="([^"]*)">', index)}
    card = DOCS / og["image"][len(site_data["site"]):]
    assert card.is_file(), f"og:image points at {card}, which is not in docs/"
    with Image.open(card) as im:
        assert (im.width, im.height) == (int(og["image:width"]), int(og["image:height"]))
        assert im.format == "JPEG" and og["image:type"] == "image/jpeg"
    assert card.stat().st_size < 1_000_000, "a preview image over 1 MB is refused by some scrapers"
