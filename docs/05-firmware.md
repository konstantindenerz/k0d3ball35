# Firmware (ZMK)

k0d3ball36 runs [ZMK](https://zmk.dev) on two nice!nano v2 (or SuperMini nRF52840) controllers.
The right half is the split central and drives the PMW3610 trackball through the upstream Zephyr
`pixart,pmw3610` input driver; no third-party driver module is needed. Since r2 the two halves are
separate PCBs with identical controller wiring: one shared kscan pin set, 35 keys (18 left, 17 right). ZMK Studio is enabled, so the
keymap can be edited live from a browser.

Sources: `firmware/zmk-config/`. Shield files: `config/boards/shields/k0d3ball36/`.

## 1. Building

### GitHub Actions (default)

Every push that touches `firmware/zmk-config/` runs `.github/workflows/firmware.yml`, which calls
ZMK's reusable `build-user-config.yml`. Download the `k0d3ball36-firmware` artifact from the
workflow run; it contains:

| File | Flash to |
|------|----------|
| `k0d3ball36_right-nice_nano_v2-zmk.uf2` | right half (central, trackball) |
| `k0d3ball36_left-nice_nano_v2-zmk.uf2` | left half |
| `settings_reset-nice_nano_v2-zmk.uf2` | either half, to wipe pairing data |

The workflow also runs weekly against the pinned ZMK commit in `config/west.yml`, so a broken
toolchain container shows up before you need a build.

### Local build with Docker

```bash
cd firmware/zmk-config
docker run --rm -it -v "$PWD":/workspaces/zmk-config -v zmk-ws:/workspaces -w /workspaces \
  zmkfirmware/zmk-build-arm:stable bash
# inside the container
west init -l zmk-config/config && west update --fetch-opt=--filter=tree:0 && west zephyr-export
west build -p -s zmk/app -d build/right -b 'nice_nano//zmk' -S studio-rpc-usb-uart -- \
  -DSHIELD=k0d3ball36_right -DZMK_CONFIG=/workspaces/zmk-config/config
west build -p -s zmk/app -d build/left -b 'nice_nano//zmk' -- \
  -DSHIELD=k0d3ball36_left -DZMK_CONFIG=/workspaces/zmk-config/config
```

The UF2 files land in `build/<side>/zephyr/zmk.uf2`. A native toolchain works the same way after
following the ZMK "native setup" guide; the board name `nice_nano//zmk` is the Zephyr 4.1 hardware
model identifier of the nice!nano v2.

### Pinned ZMK revision

`config/west.yml` pins ZMK `main` to a commit. To update: change the revision, rebuild all three
targets, re-pair the halves if the split protocol changed (release notes say so), and flash both
halves in the same session.

## 2. Flashing

1. Flash `settings_reset` to **both** halves first (new build, or whenever the halves stop talking to
   each other). Double-tap reset, copy the UF2 to the `NICENANO` drive, wait for the drive to vanish.
2. Flash `k0d3ball36_left` to the left half and `k0d3ball36_right` to the right half the same way.
3. Power-cycle both halves. The halves pair with each other automatically within a few seconds.
4. Connect the right half to the host by USB or pair it over Bluetooth (profile 0 by default).

The reset button sits next to the controller on each half. If the controller is socketed and you
cannot reach the button, short the RST and GND pads on the PCB twice quickly.

## 3. Pairing and profiles

The right half manages up to five Bluetooth profiles. On the System layer (hold both outer thumb
keys, or `&lt SYS ESC` on the left outer thumb):

| Key | Action |
|-----|--------|
| left top row 1 to 5 | select BT profile 0 to 4 |
| left bottom row, inner key | clear the current profile (`BT_CLR`) |
| right top row 1 / 2 | force USB / force BLE output |
| right top row outer | bootloader |
| right bottom row outer | ZMK Studio unlock |
| right outer thumb | reset |

Switch the host device by selecting another profile; the first connection on a fresh profile starts
advertising and the host sees "k0d3ball36".

## 4. ZMK Studio

The right half is built with the `studio-rpc-usb-uart` snippet. Connect it by USB (or Bluetooth on
browsers that support Web Bluetooth), open <https://zmk.studio>, press the Studio unlock key on the
System layer, and edit layers and bindings live. Changes persist on the keyboard. Keymap changes in
`k0d3ball36.keymap` are ignored once Studio has saved a keymap, until you choose "Restore Stock
Settings" in Studio.

Studio shows the keyboard using the physical layout in `k0d3ball36-layouts.dtsi`, which is
generated from `hardware/layout/output/points-left.json` and `points-right.json` by
`scripts/gen_physical_layout.py`. Regenerate it whenever the hardware layout changes:

```bash
python3 firmware/zmk-config/scripts/gen_physical_layout.py > /tmp/pl.txt   # paste into the dtsi
python3 firmware/zmk-config/scripts/gen_physical_layout.py --json > firmware/zmk-config/config/k0d3ball36.json
```

## 5. Default keymap

Key positions in matrix transform order:

```
 0  1  2  3  4      5  6  7  8  9
10 11 12 13 14     15 16 17 18 19
20 21 22 23 24     25 26 27 28 29
      30 31 32     33 34
```

35 positions: the left half has three thumb keys (30 inner, 31 middle, 32 outer), the right half
only the two outer ones (33 middle, 34 outer); the place where a right inner thumb key would sit is
taken by the ball pocket. Matrix transform row 3 is `RC(3,2) RC(3,3) RC(3,4)` on the left and
`RC(3,8) RC(3,7)` on the right.

| Layer | Access | Content |
|-------|--------|---------|
| 0 Base | | QWERTY, home-row mods GACS on A S D F and J K L ; (hold = mod, tap = letter) |
| 1 Nav | hold left middle thumb (Space) | arrows, Home/End, PgUp/PgDn, media; left hand keeps the mods |
| 2 Num | hold left inner thumb (Tab) | numpad on the left hand, brackets and operators around it |
| 3 Sym | hold right middle thumb (Enter) | symbols on the left hand mirroring the Num layer |
| 4 Mouse | automatic, when the ball moves | right home row J K L = left / right / middle click, M , = back / forward, U = hold for scroll, I = hold for snipe, right thumbs = left / right click and scroll |
| 5 Scroll | hold U on the mouse layer, or right outer thumb (Backspace) | ball movement becomes scrolling, clicks stay available |
| 6 Snipe | hold I on the mouse layer | ball movement at one third speed |
| 7 System | hold left outer thumb (Esc), or both outer thumbs | Bluetooth profiles, output selection, F keys, bootloader, Studio unlock, reset |

Thumb keys: left outer `Esc / System`, left middle `Space / Nav`, left inner `Tab / Num`,
right middle `Enter / Sym`, right outer `Backspace / Scroll`. The r1 right inner thumb key is gone,
so its bindings moved one key outward and Delete is reached from the Nav layer.

Combos on the base layer: W+E = Esc, E+R = Tab, F+J = Caps Word, both outer thumbs = System layer.

Image prompt: *Top-down flat illustration of a 35-key split keyboard layout, 3x5 keys per hand plus three fanned thumb keys on the left and two on the right, legends showing a QWERTY base layer with small modifier labels (GUI ALT CTRL SHIFT) under the home-row keys, a 19 mm trackball drawn beside the right thumb keys, clean technical diagram style, white background.*

## 6. Trackball tuning

All trackball settings live in `k0d3ball36_right.overlay`.

| Setting | Where | Default | Notes |
|---------|-------|---------|-------|
| sensor resolution | `res-cpi` on the `trackball` node | 600 | 200 to 3200 in steps of 200. The sensor counts surface travel, so a 19 mm ball needs about 30 percent more CPI than the 25 mm ball of r1 (which started at 400) for the same cursor speed per thumb movement. 800 to 1000 suits fast cursor users. |
| global scaling | `input-processors` of `trackball_listener` | none | add `&zip_xy_scaler 1 2` before the temp layer processor for a finer global scale without touching the CPI |
| axis direction | `invert-x`, `invert-y` on the `trackball` node | off | enable if the cursor moves the wrong way; swap axes with `&zip_xy_swap_mapper` if the sensor board is mounted rotated by 90 degrees |
| auto mouse layer timeout | `&zip_temp_layer LAYER_MOUSE 700` | 700 ms | layer 4 is active while the ball moves and 700 ms after the last movement |
| keys that keep the mouse layer | `excluded-positions` of `&zip_temp_layer` | mouse buttons, scroll, snipe | pressing other keys ends the mouse layer immediately |
| typing guard | `require-prior-idle-ms` | 150 ms | the mouse layer does not open while you are typing |
| scroll speed | `&zip_scroll_scaler 1 6` in the `scroll` child | 1/6 | smaller divisor = faster scrolling; natural scrolling: add `&zip_scroll_transform (INPUT_TRANSFORM_Y_INVERT)` |
| snipe speed | `&zip_xy_scaler 1 3` in the `snipe` child | 1/3 | |
| smart mode | `smart-mode` | on | PixArt's surface quality algorithm, keep on for plastic balls |
| force awake | `force-awake` | off | keeps the sensor out of its rest modes; faster first movement at a high battery cost |

Known behaviour of small balls: the first few millimetres after a pause can feel jumpy because the
sensor wakes from rest mode. If that bothers you more than battery life, try `force-awake` and measure.
A 19 mm ball has little inertia, so there are no long flicks; the snipe layer matters less and the
CPI matters more than on a 34 mm Keyball.

## 7. Battery expectations

| Half | Battery | Estimate |
|------|---------|----------|
| left (peripheral) | 110 mAh | several weeks |
| right (central, sensor) | 300 mAh | three to six weeks of mixed use |

Numbers come from the PMW3610 datasheet (0.6 mA tracking, 36 uA rest) plus typical nRF52840 split
central consumption; measured values will replace them (see `issues/`). Deep sleep starts after
30 minutes of inactivity (`CONFIG_ZMK_IDLE_SLEEP_TIMEOUT`) and switches the controller's VCC rail off,
which also powers down the sensor. Only a key press wakes the keyboard; moving the ball does not.

Battery levels of both halves are reported to the host over BLE (the central proxies the peripheral's
level) and shown in ZMK Studio.

## 8. Troubleshooting

| Symptom | Check |
|---------|-------|
| halves do not talk to each other | flash `settings_reset` to both, then the real firmware; power both halves within a minute of each other |
| right half works over USB but the host sees no Bluetooth keyboard | `&out OUT_BLE` on the System layer; clear the profile and pair again |
| cursor does not move | sensor board power (3.3 V on pin 1 of the FPC), cable seated with contacts facing the connector, `NCS` and `MOT` continuity to the controller; build log must show `pixart,pmw3610` without warnings |
| cursor moves only on one axis or diagonally | lens not clipped on the sensor, ball too high (lens-to-ball distance must be 2.2 to 2.6 mm), dirty ball |
| cursor moves the wrong way | `invert-x` / `invert-y`; 90 degree rotation of the sensor board needs `&zip_xy_swap_mapper` |
| mouse layer opens while typing | increase `require-prior-idle-ms`; make sure `excluded-positions` does not include letter keys |
| scroll goes in the wrong direction | add `&zip_scroll_transform (INPUT_TRANSFORM_Y_INVERT)` after the scroll mapper |
| Studio cannot connect | right half must be the USB-connected half and built with the `studio-rpc-usb-uart` snippet; press the unlock key |
| short battery life on the right half | disable `force-awake`, lower the sleep timeout, check that the slide switch really cuts the battery (not just the controller enable) |

## 9. One pin set for both halves

Since r2 each half is its own PCB and the controller footprint is wired identically on both, so
there is one pin table (`docs/01-design-spec.md`, section 2) and one shared `kscan0` in
`k0d3ball36.dtsi`:

| Line | Both halves |
|------|-------------|
| COL0..COL4 (pinky to inner) | D4 D5 D6 D7 D8 |
| ROW0..ROW3 (top to thumbs) | D21 D20 D19 D18 |
| TB_SCLK / TB_SDIO / TB_NCS / TB_MOT | D15 / D16 / D10 / D14 (sensor populated on the right; test pads on the left) |

D0 to D3 and D9 are free and broken out as test pads on both halves. The r1 mirrored pin table,
the solder jumpers and the grounded D0 are gone (`issues/fw-left-half-pin-mirror.md`,
`issues/hw-d0-grounded.md`). The per-side overlays only differ in the matrix transform row for the
thumbs and in the sensor node.

## 10. Moving the ball to the left half

The left PCB has no pocket notch and no FPC connector, so a left-ball build needs a mirrored right
PCB (the layout generator can produce one by giving the left half the `trackball` and `fpc` blocks
and mirroring the pocket). The firmware side is a configuration change because the sensor pins are
the same on both halves:

1. In `k0d3ball36_left.overlay`, enable the prepared left-ball block (`&pinctrl`, `&spi1` with
   the `trackball` node on D15 / D16 / D10 / D14, and `&trackball_split { status = "okay"; device = <&trackball>; };`).
2. In `k0d3ball36_right.overlay`, remove `trackball_listener` and enable the shared
   `trackball_split_listener` and the `trackball_split` node (`status = "okay";` on both). Move the
   input processor settings to that listener.
3. Add `CONFIG_INPUT_PMW3610=y`, `CONFIG_SPI=y` and `CONFIG_INPUT=y` to `k0d3ball36_left.conf`.
4. Rebuild and flash both halves.

The peripheral forwards motion events to the central through ZMK's `zmk,input-split`; input
processors can run on either side. The same mechanism is the basis for a future dongle build in which
both halves are peripherals.

## 11. Checks

`firmware/zmk-config/scripts/check_pins.py` compares the devicetree pin usage of both overlays
(including the prepared left-ball set) against the single pin table in
`docs/01-design-spec.md` and is run by `tests/test_firmware_pins.py`. The firmware itself is
validated by building it (CI, or the Docker commands above).
