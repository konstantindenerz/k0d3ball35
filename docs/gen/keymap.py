# SPDX-License-Identifier: MIT
"""docs/data/keymap.json: the ZMK keymap as the keymap tab draws it.

Reads firmware/zmk-config/config/k0d3ball35.keymap (layers, combos, behaviours), the shield's
matrix transform in k0d3ball35.dtsi plus the right overlay's col-offset (binding index -> matrix
row/column -> half and switch reference SW<row><col>), the trackball listener of the right overlay
(auto mouse layer, scroll and snipe processors) and the layer table of spec/05-firmware.md.
Labels are a lookup table; a code that is not in it is shown as written in the keymap.
"""
from __future__ import annotations

import re

import yaml

from . import REPO

KEYMAP = REPO / "firmware/zmk-config/config/k0d3ball35.keymap"
SHIELD = REPO / "firmware/zmk-config/config/boards/shields/k0d3ball35"
LAYOUT_YAML = REPO / "hardware/layout/k0d3ball35.yaml"
FIRMWARE_MD = REPO / "spec/05-firmware.md"

# key codes -> legend. ZMK names from dt-bindings/zmk/keys.h; aliases share one entry.
KEYS = {
    **{c: c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
    **{f"N{i}": str(i) for i in range(10)}, **{f"NUMBER_{i}": str(i) for i in range(10)},
    **{f"F{i}": f"F{i}" for i in range(1, 25)},
    "SPACE": "Space", "SPC": "Space", "RET": "Enter", "ENTER": "Enter", "RETURN": "Enter",
    "BSPC": "Bksp", "BACKSPACE": "Bksp", "DEL": "Del", "DELETE": "Del", "TAB": "Tab", "ESC": "Esc", "ESCAPE": "Esc",
    "INS": "Ins", "INSERT": "Ins", "CAPS": "Caps", "CAPSLOCK": "Caps", "PSCRN": "PrtSc", "PRINTSCREEN": "PrtSc",
    "HOME": "Home", "END": "End", "PG_UP": "PgUp", "PAGE_UP": "PgUp", "PG_DN": "PgDn", "PAGE_DOWN": "PgDn",
    "UP": "↑", "DOWN": "↓", "LEFT": "←", "RIGHT": "→",
    "LBKT": "[", "RBKT": "]", "LBRC": "{", "RBRC": "}", "LPAR": "(", "RPAR": ")", "LT": "<", "GT": ">",
    "SEMI": ";", "SEMICOLON": ";", "COLON": ":", "SQT": "'", "APOS": "'", "DQT": '"', "COMMA": ",", "DOT": ".",
    "PERIOD": ".", "FSLH": "/", "SLASH": "/", "BSLH": "\\", "BACKSLASH": "\\", "PIPE": "|", "GRAVE": "`",
    "TILDE": "~", "EXCL": "!", "AT": "@", "HASH": "#", "POUND": "#", "DLLR": "$", "DOLLAR": "$", "PRCNT": "%",
    "PERCENT": "%", "CARET": "^", "AMPS": "&", "STAR": "*", "ASTRK": "*", "MINUS": "-", "UNDER": "_",
    "UNDERSCORE": "_", "EQUAL": "=", "PLUS": "+", "QMARK": "?", "QUESTION": "?",
    "C_PP": "Play", "C_PLAY_PAUSE": "Play", "C_NEXT": "Next", "C_PREV": "Prev", "C_VOL_UP": "Vol+",
    "C_VOL_DN": "Vol−", "C_MUTE": "Mute", "C_BRI_UP": "Bri+", "C_BRI_DN": "Bri−",
}
MODS = {"LGUI": "Gui", "RGUI": "Gui", "LCMD": "Gui", "RCMD": "Gui", "LWIN": "Gui", "RWIN": "Gui",
        "LALT": "Alt", "RALT": "Alt", "LCTRL": "Ctrl", "RCTRL": "Ctrl", "LCTL": "Ctrl", "RCTL": "Ctrl",
        "LSHFT": "Shift", "RSHFT": "Shift", "LSHIFT": "Shift", "RSHIFT": "Shift"}
MOUSE = {"LCLK": "Left click", "RCLK": "Right click", "MCLK": "Middle click", "MB1": "Left click",
         "MB2": "Right click", "MB3": "Middle click", "MB4": "Back", "MB5": "Forward"}
SYSTEM = {"bootloader": "Boot­loader", "sys_reset": "Reset", "studio_unlock": "Studio unlock",
          "caps_word": "Caps Word", "soft_off": "Off"}
# hold-tap behaviours whose hold is a modifier (custom &hml/&hmr are found in the keymap itself)
MOD_TAPS = {"mt"}


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", " ", text)


def key_label(code: str) -> str:
    return KEYS.get(code) or MODS.get(code) or code


def split_bindings(text: str) -> list[list[str]]:
    """'&kp Q &hml LGUI A' -> [['kp', 'Q'], ['hml', 'LGUI', 'A']]."""
    out: list[list[str]] = []
    for tok in text.split():
        if tok.startswith("&"):
            out.append([tok[1:]])
        elif out:
            out[-1].append(tok)
    return out


def parse_binding(parts: list[str], layers: dict[str, str], mod_taps: set[str]) -> dict:
    """{raw, tap, hold, kind, layer?}. kind: key, mod, mod-tap, layer-tap, layer, mouse, bt, output,
    system, trans, none."""
    beh, args = parts[0], parts[1:]
    raw = "&" + " ".join(parts)
    b = {"raw": raw, "tap": None, "hold": None, "kind": "key"}
    if beh == "trans":
        b.update(kind="trans")
    elif beh == "none":
        b.update(kind="none")
    elif beh == "kp":
        code = args[0]
        b.update(tap=key_label(code), kind="mod" if code in MODS else "key")
    elif beh in mod_taps and len(args) == 2:
        b.update(tap=key_label(args[1]), hold=MODS.get(args[0], key_label(args[0])), kind="mod-tap")
    elif beh == "lt":
        name = layers.get(args[0], args[0])
        b.update(tap=key_label(args[1]), hold=name, kind="layer-tap", layer=name)
    elif beh in ("mo", "tog", "to", "sl"):
        name = layers.get(args[0], args[0])
        verb = {"mo": "", "tog": "Toggle ", "to": "To ", "sl": "Sticky "}[beh]
        b.update(tap=f"{verb}{name}", hold=None, kind="layer", layer=name)
    elif beh == "mkp":
        b.update(tap=MOUSE.get(args[0], args[0]), kind="mouse")
    elif beh == "bt":
        cmd = args[0]
        if cmd == "BT_SEL":
            b.update(tap=f"BT {args[1]}", kind="bt")
        else:
            b.update(tap={"BT_CLR": "BT clear", "BT_CLR_ALL": "BT clear all", "BT_NXT": "BT next",
                          "BT_PRV": "BT prev"}.get(cmd, cmd), kind="bt")
    elif beh == "out":
        b.update(tap={"OUT_USB": "USB", "OUT_BLE": "BLE", "OUT_TOG": "USB/BLE"}.get(args[0], args[0]), kind="output")
    elif beh in SYSTEM:
        b.update(tap=SYSTEM[beh], kind="system")
    else:
        b.update(tap=" ".join(parts), kind="key")
    return b


def node_body(text: str, name: str) -> str:
    """Body of the devicetree node `name { ... }`, braces matched."""
    m = re.search(rf"\b{name}\s*\{{", text)
    i, depth = m.end(), 1
    for j in range(i, len(text)):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return text[i:j]
    raise ValueError(f"unbalanced node {name}")


def defines(text: str) -> dict[str, str]:
    return {m[1]: m[2].strip() for m in re.finditer(r"^#define\s+(\w+)\s+(.+)$", text, flags=re.M)}


def matrix_transform() -> list[dict]:
    """binding index -> {half, row, col, ref} from the shield's default transform. The right half
    adds its col-offset to the matrix column; the switch reference on the board is SW<row><col>
    with the column of that half."""
    dtsi = strip_comments((SHIELD / "k0d3ball35.dtsi").read_text())
    tr = re.search(r"default_transform\s*:.*?\{(.*?)\};", dtsi, flags=re.S)[1]
    columns = int(re.search(r"columns\s*=\s*<(\d+)>", tr)[1])
    cells = [(int(r), int(c)) for r, c in re.findall(r"RC\((\d+),\s*(\d+)\)", re.search(r"map\s*=\s*<(.*?)>", tr, flags=re.S)[1])]
    right = strip_comments((SHIELD / "k0d3ball35_right.overlay").read_text())
    offset = int(re.search(r"col-offset\s*=\s*<(\d+)>", right)[1])
    left = strip_comments((SHIELD / "k0d3ball35_left.overlay").read_text())
    assert "col-offset" not in left, "left overlay offsets its columns; the mapping below assumes it does not"
    assert offset * 2 == columns
    out = []
    for r, c in cells:
        half, col = ("right", c - offset) if c >= offset else ("left", c)
        out.append({"half": half, "row": r, "col": col, "matrix_col": c, "ref": f"SW{r}{col}"})
    return out


def key_names() -> dict[tuple[int, int], str]:
    """(row, col) -> finger / thumb name from the layout yaml."""
    cfg = yaml.safe_load(LAYOUT_YAML.read_text())
    rows = ("top", "home", "bottom")
    names = {(r, c["col"]): f"{c['name']} {rows[r]}" for c in cfg["columns"] for r in range(cfg["rows"])}
    for t in cfg["thumbs"]:
        names[(t["row"], t["col"])] = t["name"].replace("_", " ")
    return names


def firmware_layer_table() -> dict[str, dict]:
    """spec/05-firmware.md: | Layer | Access | Content | -> {display name: {access, content}}."""
    text = FIRMWARE_MD.read_text()
    m = re.search(r"^\| Layer \| Access \| Content \|\n\|[-| ]+\|\n((?:\|.*\|\n)+)", text, flags=re.M)
    out = {}
    if m:
        for line in m[1].strip().splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            num, _, name = cells[0].partition(" ")
            out[name] = {"index": int(num), "access": cells[1], "content": cells[2]}
    return out


def pointer() -> dict:
    """The trackball listener of the right overlay: which layer opens automatically, and what the
    scroll and snipe layers do to the ball movement."""
    text = strip_comments((SHIELD / "k0d3ball35_right.overlay").read_text())
    d = defines((SHIELD / "k0d3ball35_right.overlay").read_text())
    layer_of = {v: k for k, v in d.items() if k.startswith("LAYER_")}
    cpi = int(re.search(r"res-cpi\s*=\s*<(\d+)>", text)[1])
    temp = re.search(r"trackball_listener\s*\{.*?input-processors\s*=\s*<&zip_temp_layer\s+(\w+)\s+(\d+)>", text, flags=re.S)
    zip_tl = re.search(r"&zip_temp_layer\s*\{(.*?)\};", text, flags=re.S)[1]
    idle = int(re.search(r"require-prior-idle-ms\s*=\s*<(\d+)>", zip_tl)[1])
    keep = [int(x) for x in re.search(r"excluded-positions\s*=\s*<([^>]*)>", zip_tl)[1].split()]
    modes = []
    for name, body in re.findall(r"\n\s*(\w+)\s*\{\s*(layers\s*=.*?)\};", text, flags=re.S):
        layer_macro = re.search(r"layers\s*=\s*<(\w+)>", body)[1]
        procs = re.findall(r"<&(\w+)([^>]*)>", re.search(r"input-processors\s*=\s*(.*?);", body, flags=re.S)[1])
        effect = []
        for proc, args in procs:
            a = args.split()
            if proc == "zip_xy_to_scroll_mapper":
                effect.append("ball movement scrolls instead of moving the cursor")
            elif proc == "zip_scroll_scaler":
                effect.append(f"scroll speed {a[0]}/{a[1]}")
            elif proc == "zip_xy_scaler":
                effect.append(f"cursor speed {a[0]}/{a[1]}")
            else:
                effect.append(proc + (" " + " ".join(a) if a else ""))
        modes.append({"node": name, "layer_index": int(d[layer_macro]), "processors": [f"&{p}{a}".strip() for p, a in procs],
                      "effect": effect})
    return {"sensor": "PMW3610", "cpi": cpi,
            "auto_layer_index": int(d[temp[1]]), "auto_timeout_ms": int(temp[2]),
            "require_prior_idle_ms": idle, "keep_positions": keep, "modes": modes,
            "_macros": layer_of}


def build() -> dict:
    raw = KEYMAP.read_text()
    text = strip_comments(raw)
    d = defines(raw)
    mod_taps = set(MOD_TAPS)
    for name, body in re.findall(r"(\w+)\s*:\s*\w+\s*\{([^{}]*compatible\s*=\s*\"zmk,behavior-hold-tap\"[^{}]*)\}", text):
        if re.search(r"bindings\s*=\s*<&kp>\s*,\s*<&kp>", body):
            mod_taps.add(name)

    km = node_body(text, "keymap")
    nodes = re.findall(r"(\w+)\s*\{\s*display-name\s*=\s*\"([^\"]+)\";\s*bindings\s*=\s*<(.*?)>;\s*\};", km, flags=re.S)
    index_of = {int(v): k for k, v in d.items() if v.isdigit() and k.isupper() and not k.startswith("KEYS")}
    names = [disp for _, disp, _ in nodes]
    layer_names = {macro: names[i] for i, macro in index_of.items() if i < len(names)}
    for i, n in enumerate(names):
        layer_names[str(i)] = n

    transform = matrix_transform()
    kname = key_names()
    keys = [{"pos": i, **t, "name": kname.get((t["row"], t["col"]), "")} for i, t in enumerate(transform)]

    table = firmware_layer_table()
    layers = []
    for i, (node, disp, body) in enumerate(nodes):
        parts = split_bindings(body)
        assert len(parts) == len(keys), f"{disp}: {len(parts)} bindings for {len(keys)} keys"
        bindings = [{"pos": p, **parse_binding(b, layer_names, mod_taps)} for p, b in enumerate(parts)]
        info = table.get(disp, {})
        layers.append({"index": i, "id": disp.lower(), "name": disp, "node": node,
                       "macro": index_of.get(i), "access": info.get("access", ""), "content": info.get("content", ""),
                       "bindings": bindings})

    combos = []
    for name, body in re.findall(r"(\w+)\s*\{([^{}]*)\}", node_body(text, "combos")):
        pos = [int(x) for x in re.search(r"key-positions\s*=\s*<([^>]*)>", body)[1].split()]
        binding = parse_binding(split_bindings(re.search(r"bindings\s*=\s*<([^>]*)>", body)[1])[0], layer_names, mod_taps)
        lay = re.search(r"layers\s*=\s*<([^>]*)>", body)
        timeout = re.search(r"timeout-ms\s*=\s*<(\d+)>", body)
        combos.append({"name": name, "positions": pos, "binding": binding,
                       "layers": [layer_names[x] for x in lay[1].split()] if lay else [],
                       "timeout_ms": int(timeout[1]) if timeout else None})

    p = pointer()
    p.pop("_macros")
    p["auto_layer"] = names[p.pop("auto_layer_index")]
    for m in p["modes"]:
        m["layer"] = names[m.pop("layer_index")]

    return {
        "source": "firmware/zmk-config/config/k0d3ball35.keymap",
        "transform": "firmware/zmk-config/config/boards/shields/k0d3ball35/k0d3ball35.dtsi",
        "keys": keys,
        "layers": layers,
        "combos": combos,
        "pointer": p,
    }
