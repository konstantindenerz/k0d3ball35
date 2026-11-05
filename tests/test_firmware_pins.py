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
