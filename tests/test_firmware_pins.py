# SPDX-License-Identifier: MIT
"""The ZMK shield must use the pins from the design spec."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_shield_pins_match_design_spec():
    script = ROOT / "firmware" / "zmk-config" / "scripts" / "check_pins.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_keymap_has_36_bindings_per_layer():
    keymap = (ROOT / "firmware" / "zmk-config" / "config" / "k0d3ball36.keymap").read_text()
    import re
    layers = re.findall(r"bindings = <(.*?)>;", keymap, re.S)
    # combos also use `bindings = <...>`; keep only the keymap layers (long blocks)
    layer_blocks = [b for b in layers if b.count("&") >= 30]
    assert len(layer_blocks) == 8, f"expected 8 layers, found {len(layer_blocks)}"
    for block in layer_blocks:
        tokens = [t for t in block.split() if t.startswith("&")]
        assert len(tokens) == 36, f"layer has {len(tokens)} bindings:\n{block}"


def test_left_and_right_overlays_use_different_pins():
    """Reversible PCB: the flipped left half must not reuse the right half's pins."""
    import re
    shield = ROOT / "firmware" / "zmk-config" / "config" / "boards" / "shields" / "k0d3ball36"

    def pins(name, prop):
        text = re.sub(r"/\*.*?\*/", "", (shield / name).read_text(), flags=re.S)
        block = re.search(prop + r"\s*=\s*(.*?);", text, re.S).group(1)
        return [int(n) for n in re.findall(r"&pro_micro\s+(\d+)", block)]

    assert pins("k0d3ball36_right.overlay", "col-gpios") == [4, 5, 6, 7, 8]
    assert pins("k0d3ball36_left.overlay", "col-gpios") == [19, 18, 15, 14, 16]
    assert pins("k0d3ball36_right.overlay", "row-gpios") == [21, 20, 19, 18]
    assert pins("k0d3ball36_left.overlay", "row-gpios") == [2, 3, 4, 5]
