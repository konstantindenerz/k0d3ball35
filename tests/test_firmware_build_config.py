# SPDX-License-Identifier: MIT
"""The firmware build configuration must be consistent before CI can build it.

Checks the GitHub workflow against ZMK's reusable build-user-config.yml, the
build matrix against the shield files, the pinned ZMK revision, the Kconfig
symbols of the shield and the devicetree/keymap references that a build would
resolve. No Zephyr toolchain needed.
"""
import pathlib
import re

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "zmk-config"
CONFIG = FW / "config"
SHIELD = CONFIG / "boards" / "shields" / "k0d3ball35"
WORKFLOW = ROOT / ".github" / "workflows" / "firmware.yml"
DOCS = ROOT / "spec" / "05-firmware.md"

# inputs of zmkfirmware/zmk/.github/workflows/build-user-config.yml
UPSTREAM_INPUTS = {"build_matrix_path", "config_path", "fallback_binary", "archive_name"}
# keys of a build.yaml entry the upstream workflow reads
UPSTREAM_MATRIX_KEYS = {"board", "shield", "snippet", "cmake-args", "artifact-name"}
# features allowed by zmk/schema/hardware-metadata.schema.json
ZMK_FEATURES = {"keys", "display", "encoder", "underglow", "backlight", "pointer", "studio"}


def _yaml(path: pathlib.Path):
    return yaml.safe_load(path.read_text())


def _strip(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


@pytest.fixture(scope="module")
def workflow():
    return _yaml(WORKFLOW)


@pytest.fixture(scope="module")
def matrix():
    return _yaml(FW / "build.yaml")["include"]


def test_workflow_calls_upstream_build_with_valid_inputs(workflow):
    build = workflow["jobs"]["build"]
    assert build["uses"].startswith("zmkfirmware/zmk/.github/workflows/build-user-config.yml@")
    inputs = build["with"]
    assert set(inputs) <= UPSTREAM_INPUTS, f"unknown inputs: {set(inputs) - UPSTREAM_INPUTS}"
    assert (ROOT / inputs["config_path"]).is_dir()
    assert (ROOT / inputs["config_path"] / "west.yml").is_file()
    assert (ROOT / inputs["build_matrix_path"]).is_file()
    assert inputs["build_matrix_path"] == "firmware/zmk-config/build.yaml"


def test_workflow_triggers_cover_push_schedule_and_tags(workflow):
    on = workflow[True] if True in workflow else workflow["on"]  # yaml parses `on` as True
    assert "schedule" in on and on["schedule"], "weekly scheduled run missing"
    assert "workflow_dispatch" in on
    for event in ("push", "pull_request"):
        assert "firmware/zmk-config/**" in on[event]["paths"]
    release = workflow["jobs"]["release"]
    assert "refs/tags/" in release["if"]
    assert release["needs"] == "build"
    assert release["permissions"]["contents"] == "write"
    steps = release["steps"]
    download = next(s for s in steps if str(s.get("uses", "")).startswith("actions/download-artifact@"))
    assert download["with"]["name"] == workflow["jobs"]["build"]["with"]["archive_name"]
    assert any("gh release upload" in str(s.get("run", "")) for s in steps)


def test_build_matrix_targets(matrix):
    shields = [e["shield"] for e in matrix]
    assert shields == ["k0d3ball35_right", "k0d3ball35_left", "settings_reset"]
    for entry in matrix:
        assert set(entry) <= UPSTREAM_MATRIX_KEYS, f"unknown matrix key in {entry}"
        assert entry["board"] == "nice_nano//zmk", "Zephyr 4.1 hardware model name of the nice!nano v2"
        if entry["shield"] != "settings_reset":
            assert (SHIELD / f"{entry['shield']}.overlay").is_file()
    right = next(e for e in matrix if e["shield"] == "k0d3ball35_right")
    assert right["snippet"] == "studio-rpc-usb-uart", "ZMK Studio needs the RPC snippet on the central"


def test_artifact_names_match_docs(matrix):
    """spec/05-firmware.md lists the files of the k0d3ball35-firmware artifact."""
    docs = DOCS.read_text()
    for entry in matrix:
        name = entry["artifact-name"]
        assert re.fullmatch(r"[a-z0-9_]+-nice_nano_v2-zmk", name), name
        assert f"`{name}.uf2`" in docs, f"{name}.uf2 not documented in spec/05-firmware.md"


def test_west_manifest_pins_zmk_commit():
    manifest = _yaml(CONFIG / "west.yml")["manifest"]
    zmk = next(p for p in manifest["projects"] if p["name"] == "zmk")
    assert re.fullmatch(r"[0-9a-f]{40}", zmk["revision"]), "ZMK must be pinned to a commit, not a branch"
    assert zmk["import"] == "app/west.yml"
    assert manifest["self"]["path"] == "config"
    # the PMW3610 driver is Zephyr's own (pixart,pmw3610); no extra module must be needed
    assert [p["name"] for p in manifest["projects"]] == ["zmk"]


def test_shield_kconfig_symbols_match_shield_names():
    kshield = (SHIELD / "Kconfig.shield").read_text()
    symbols = dict(re.findall(r"config (SHIELD_\w+)\n\s+def_bool \$\(shields_list_contains,(\w+)\)", kshield))
    assert symbols == {"SHIELD_K0D3BALL35_LEFT": "k0d3ball35_left", "SHIELD_K0D3BALL35_RIGHT": "k0d3ball35_right"}
    defconfig = (SHIELD / "Kconfig.defconfig").read_text()
    used = set(re.findall(r"SHIELD_\w+", defconfig))
    assert used == set(symbols), f"Kconfig.defconfig uses undefined symbols {used - set(symbols)}"
    assert re.search(r"if SHIELD_K0D3BALL35_RIGHT\n.*?config ZMK_SPLIT_ROLE_CENTRAL\n\s+default y", defconfig, re.S)
    assert "config ZMK_SPLIT\n    default y" in defconfig


def test_shield_metadata():
    meta = _yaml(SHIELD / "k0d3ball35.zmk.yml")
    assert meta["type"] == "shield" and meta["id"] == "k0d3ball35"
    assert meta["requires"] == ["pro_micro"]
    assert set(meta["features"]) <= ZMK_FEATURES
    assert set(meta["siblings"]) == {"k0d3ball35_left", "k0d3ball35_right"}
    for sibling in meta["siblings"]:
        assert (SHIELD / f"{sibling}.overlay").is_file()


def test_right_overlay_matches_zephyr_pmw3610_binding():
    """Properties used on the sensor node exist in Zephyr's pixart,pmw3610 binding."""
    right = _strip((SHIELD / "k0d3ball35_right.overlay").read_text())
    node = re.search(r"trackball: trackball@0 \{(.*?)\n    \};", right, re.S).group(1)
    assert 'compatible = "pixart,pmw3610"' in node
    for required in ("reg =", "spi-max-frequency =", "motion-gpios =", "zephyr,axis-x =", "zephyr,axis-y ="):
        assert required in node, f"{required} missing on the trackball node"
    props = set(re.findall(r"^\s*([a-z][a-z0-9,-]*)\s*[;=]", node, re.M))
    allowed = {"compatible", "status", "reg", "spi-max-frequency", "motion-gpios", "reset-gpios",
               "zephyr,axis-x", "zephyr,axis-y", "res-cpi", "invert-x", "invert-y", "force-awake", "smart-mode"}
    assert props <= allowed, f"unknown PMW3610 properties {props - allowed}"
    cpi = int(re.search(r"res-cpi = <(\d+)>", node).group(1))
    assert 200 <= cpi <= 3200 and cpi % 200 == 0
    assert "#include <input/processors.dtsi>" in right
    assert "#include <dt-bindings/input/input-event-codes.h>" in right
    assert "CONFIG_INPUT_PMW3610=y" in (SHIELD / "k0d3ball35_right.conf").read_text()


def test_input_listener_uses_known_processors():
    right = _strip((SHIELD / "k0d3ball35_right.overlay").read_text())
    listener = re.search(r"trackball_listener: trackball_listener \{(.*)\n    \};", right, re.S).group(1)
    assert 'compatible = "zmk,input-listener"' in listener
    assert "device = <&trackball>" in listener
    processors = set(re.findall(r"&(zip_\w+)", listener))
    known = {"zip_temp_layer", "zip_xy_to_scroll_mapper", "zip_scroll_scaler", "zip_xy_scaler",
             "zip_xy_swap_mapper", "zip_xy_transform", "zip_scroll_transform", "zip_x_scaler", "zip_y_scaler"}
    assert processors <= known, f"unknown input processors {processors - known}"
    # the layer numbers passed to the temp-layer processor must be keymap layers
    keymap = (CONFIG / "k0d3ball35.keymap").read_text()
    layer_count = len(re.findall(r"^\s{8}\w+_layer \{", keymap, re.M))
    for name, value in re.findall(r"#define (LAYER_\w+)\s+(\d+)", right):
        assert int(value) < layer_count, f"{name} = {value} but the keymap has {layer_count} layers"
    overrides = re.search(r"&zip_temp_layer \{(.*?)\};", right, re.S).group(1)
    assert set(re.findall(r"^\s*([a-z-]+) =", overrides, re.M)) <= {"require-prior-idle-ms", "excluded-positions"}


def test_keymap_includes_and_behaviors_exist_in_zmk():
    keymap = (CONFIG / "k0d3ball35.keymap").read_text()
    includes = set(re.findall(r"#include <([^>]+)>", keymap))
    assert includes == {"behaviors.dtsi", "dt-bindings/zmk/bt.h", "dt-bindings/zmk/keys.h",
                        "dt-bindings/zmk/outputs.h", "dt-bindings/zmk/pointing.h"}
    local = set(re.findall(r"^\s{8}(\w+): \w+ \{", keymap, re.M))
    used = set(re.findall(r"&(\w+)", keymap)) - local
    zmk_behaviors = {"kp", "mt", "lt", "mo", "trans", "none", "bt", "out", "bootloader", "sys_reset",
                     "studio_unlock", "caps_word", "mkp", "msc", "mmv", "to", "tog", "sk", "sl", "key_repeat"}
    assert used <= zmk_behaviors, f"behaviors not provided by ZMK: {used - zmk_behaviors}"


def test_shared_conf_symbols_exist_in_pinned_zmk():
    """Symbols set in the .conf files exist in ZMK main / Zephyr (checked against the pinned commit)."""
    conf = "".join((p.read_text() for p in (CONFIG / "k0d3ball35.conf", SHIELD / "k0d3ball35_right.conf", SHIELD / "k0d3ball35_left.conf")))
    symbols = set(re.findall(r"^CONFIG_(\w+)=", conf, re.M))
    known = {"ZMK_POINTING", "ZMK_POINTING_SMOOTH_SCROLLING", "ZMK_STUDIO", "ZMK_BATTERY_REPORTING",
             "ZMK_SPLIT_BLE_CENTRAL_BATTERY_LEVEL_PROXY", "ZMK_SPLIT_BLE_CENTRAL_BATTERY_LEVEL_FETCHING",
             "ZMK_SLEEP", "ZMK_IDLE_SLEEP_TIMEOUT", "ZMK_EXT_POWER", "BT_CTLR_TX_PWR_PLUS_8",
             "ZMK_KSCAN_DEBOUNCE_PRESS_MS", "ZMK_KSCAN_DEBOUNCE_RELEASE_MS", "INPUT_PMW3610", "SPI", "INPUT"}
    assert symbols <= known, f"symbols not verified against the pinned ZMK: {symbols - known}"
