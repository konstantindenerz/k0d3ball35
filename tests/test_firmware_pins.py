# SPDX-License-Identifier: MIT
"""The ZMK shield must use the pins from the design spec (one set for both halves)."""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "zmk-config"
SHIELD = FW / "config" / "boards" / "shields" / "k0d3ball35"
KEYS = 35

COLS = [4, 5, 6, 7, 8]
ROWS = [21, 20, 19, 18]


def _strip(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def _pins(text: str, prop: str) -> list[int]:
    block = re.search(prop + r"\s*=\s*(.*?);", text, re.S)
    return [int(n) for n in re.findall(r"&pro_micro\s+(\d+)", block.group(1))] if block else []


def test_shield_pins_match_design_spec():
    script = FW / "scripts" / "check_pins.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_keymap_has_35_bindings_per_layer():
    keymap = (FW / "config" / "k0d3ball35.keymap").read_text()
    layers = re.findall(r"bindings = <(.*?)>;", keymap, re.S)
    # combos also use `bindings = <...>`; keep only the keymap layers (long blocks)
    layer_blocks = [b for b in layers if b.count("&") >= 30]
    assert len(layer_blocks) == 8, f"expected 8 layers, found {len(layer_blocks)}"
    for block in layer_blocks:
        tokens = [t for t in block.split() if t.startswith("&")]
        assert len(tokens) == KEYS, f"layer has {len(tokens)} bindings:\n{block}"


def test_keymap_positions_stay_below_key_count():
    """Combos, hold-trigger lists and the auto mouse layer may only name existing positions."""
    keymap = (FW / "config" / "k0d3ball35.keymap").read_text()
    right = (SHIELD / "k0d3ball35_right.overlay").read_text()
    lists = re.findall(r"\bkey-positions = <([0-9 ]+)>", keymap)
    lists += re.findall(r"#define (?:KEYS_L|KEYS_R|THUMBS)\s+([0-9 ]+)", keymap)
    lists += re.findall(r"excluded-positions = <([^>]*)>", right)
    assert lists
    for lst in lists:
        for pos in map(int, lst.split()):
            assert pos < KEYS, f"position {pos} does not exist on a {KEYS}-key board"


def test_matrix_pins_are_shared_and_identical():
    """Two separate PCBs with the same controller wiring: one kscan pin set in the dtsi."""
    dtsi = _strip((SHIELD / "k0d3ball35.dtsi").read_text())
    assert _pins(dtsi, "col-gpios") == COLS
    assert _pins(dtsi, "row-gpios") == ROWS
    for name in ("k0d3ball35_left.overlay", "k0d3ball35_right.overlay"):
        text = _strip((SHIELD / name).read_text())
        assert _pins(text, "col-gpios") == [], f"{name} must not redefine col-gpios"
        assert _pins(text, "row-gpios") == [], f"{name} must not redefine row-gpios"


def test_matrix_transform_has_35_cells_with_two_right_thumbs():
    dtsi = _strip((SHIELD / "k0d3ball35.dtsi").read_text())
    cells = re.findall(r"RC\((\d),(\d)\)", dtsi)
    assert len(cells) == KEYS
    thumbs = [c for c in cells if c[0] == "3"]
    assert thumbs == [("3", "2"), ("3", "3"), ("3", "4"), ("3", "8"), ("3", "7")]
    right = (SHIELD / "k0d3ball35_right.overlay").read_text()
    assert "col-offset = <5>" in right


def test_physical_layout_matches_generator():
    """Both generated layout files are current and list 35 keys."""
    script = FW / "scripts" / "gen_physical_layout.py"
    dts = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, check=True).stdout
    layouts = (SHIELD / "k0d3ball35-layouts.dtsi").read_text()
    assert dts.strip() in layouts, "k0d3ball35-layouts.dtsi is stale; rerun gen_physical_layout.py"
    assert layouts.count("&key_physical_attrs") == KEYS

    js = subprocess.run([sys.executable, str(script), "--json"], capture_output=True, text=True, check=True).stdout
    current = json.loads((FW / "config" / "k0d3ball35.json").read_text())
    assert json.loads(js) == current, "k0d3ball35.json is stale; rerun gen_physical_layout.py --json"
    assert len(current["layouts"]["default_layout"]["layout"]) == KEYS
