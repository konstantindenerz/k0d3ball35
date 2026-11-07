---
title: CI build of both halves with ZMK
type: task
priority: P1
status: open
area: infra
created: 2026-11-05
---

# CI build of both halves with ZMK

## Context

GitHub Actions workflow building `k0d3ball35_left`, `k0d3ball35_right` and `settings_reset`
for `nice_nano//zmk` from `firmware/zmk-config`, uploading UF2 artifacts, plus a scheduled build so
breakage from ZMK main surfaces early.

## Acceptance criteria

- [ ] `.github/workflows/firmware.yml` green (needs the repo on GitHub; the same build passes
      locally in the ZMK container, see below)
- [x] Weekly scheduled run (`cron: 17 5 * * 1`, on the pinned ZMK commit)
- [x] UF2 files attached to GitHub releases on tags (`release` job in `firmware.yml`; untested on
      GitHub until the first tag is pushed)

## Verified (2026-11-06)

- Local build of all three targets with `zmkfirmware/zmk-build-arm:stable` on the pinned ZMK
  commit `4dd95d78` (2026-10-09, Zephyr `v4.1.0+zmk-fixes`), identical to the commands in
  `spec/05-firmware.md`: `right` 276 kB flash / 73 kB RAM, `left` 191 kB / 38 kB, `settings_reset`
  52 kB / 13 kB; `zmk.uf2` written for each. No devicetree or Kconfig errors.
- Right half `.config` has `INPUT_PMW3610`, `SPI`, `ZMK_SPLIT_ROLE_CENTRAL`, `ZMK_STUDIO`,
  `ZMK_POINTING`; the final devicetree contains the `pixart,pmw3610` node and the
  `trackball_listener` with `zip_temp_layer 4 700`.
- Workflow inputs (`config_path`, `build_matrix_path`, `archive_name`) and the `build.yaml` keys
  (`board`, `shield`, `snippet`, `artifact-name`) match the current upstream
  `zmkfirmware/zmk/.github/workflows/build-user-config.yml`; the merged artifact is named
  `k0d3ball35-firmware`. (Superseded: the reusable workflow is no longer called, see the CI fix
  below. The inputs were valid; the nesting of `config_path` was not.)
- `config/west.yml` pins ZMK to a commit and imports `app/west.yml`; the PMW3610 driver is
  Zephyr's upstream `pixart,pmw3610` (`drivers/input/input_pmw3610.c`, `CONFIG_INPUT_PMW3610`),
  so no third-party module is needed. All properties on the sensor node exist in the Zephyr
  binding; the input processors (`zip_temp_layer`, `zip_xy_to_scroll_mapper`,
  `zip_scroll_scaler`, `zip_xy_scaler`) and the `zmk,input-listener` / `zmk,input-split`
  bindings exist at the pinned commit. All `CONFIG_` symbols in the `.conf` files exist there.
- Pin check `scripts/check_pins.py` passes against `spec/01-design-spec.md`;
  `tests/test_firmware_pins.py` and the new `tests/test_firmware_build_config.py` pass.

Fixed on the way:

- `Kconfig.shield` / `Kconfig.defconfig` used `SHIELD_K0D3BALL36_*` (old project name); renamed
  to `SHIELD_K0D3BALL35_*`. The build worked anyway because both files used the same wrong name,
  but it was a trap for anyone adding per-side Kconfig.
- `build.yaml` artifact names now carry the `-zmk` suffix so the files in the artifact match
  the table in `spec/05-firmware.md`.
- Central-only symbols (`ZMK_POINTING_SMOOTH_SCROLLING`, `ZMK_SPLIT_BLE_CENTRAL_BATTERY_LEVEL_*`)
  moved from the shared `k0d3ball35.conf` to `k0d3ball35_right.conf`; they produced
  "unsatisfied dependencies" warnings in the left-half build.
- `firmware.yml`: added the `release` job (downloads the merged artifact, creates the release if
  it does not exist, uploads `*.uf2`).

## CI fix (2026-11-07)

The first runs on GitHub failed in every matrix target with
`FATAL ERROR: no west workspace found from "/__w/k0d3ball35/k0d3ball35"`. ZMK's reusable
`build-user-config.yml` runs `west init -l "$GITHUB_WORKSPACE/<config_path>"` and then `west update`
with `working-directory: $GITHUB_WORKSPACE`. West puts the workspace topdir at the *parent* of the
manifest directory, so with `config_path: firmware/zmk-config/config` the topdir landed in
`firmware/zmk-config` while west ran one level above it. The reusable workflow only supports a
config directory that is a direct child of the repository root; nesting cannot be expressed through
its inputs.

`firmware.yml` now carries the build itself (matrix, build, merge, release), modelled on upstream's
steps but with `working-directory: firmware/zmk-config` — the same workspace the local build in
`spec/05-firmware.md` uses. `tests/test_firmware_build_config.py` checks that every west command
stays in that workspace.

Replayed in `zmkfirmware/zmk-build-arm:stable` with the repository mounted at the CI path
(`/__w/k0d3ball35/k0d3ball35`) and the workflow's own commands: `west init -l config` reports
`topdir=/__w/k0d3ball35/k0d3ball35/firmware/zmk-config`, `west update` resolves the pinned
`4dd95d78`, and all three targets build and write `zmk.uf2` (right 276052 B flash / 73470 B RAM,
left 190628 B / 37824 B, settings_reset 52508 B / 12840 B).

Behind the west failure sat a second one: `k0d3ball35-layouts.dtsi` did not parse, so no target
could have built even with the workspace fixed. See `issues/fw-physical-layout-exact-coords.md`.

## What you must do

1. Push the repository to GitHub and enable Actions.
2. Check the first run of `firmware` and download `k0d3ball35-firmware`. Tick the first criterion.
3. Push a tag (`git tag v0.1.0 && git push --tags`) once and verify the UF2 files appear on the
   release. The `release` job needs `contents: write`, which the default `GITHUB_TOKEN` grants
   unless the repository restricts workflow permissions to read-only.
4. Fix the `url:` in `k0d3ball35.zmk.yml` to the real repository (`issues/doc-zmk-yml-repo-url.md`).

## Remaining risks

- The build job is a copy of upstream's `build-user-config.yml` steps and has to be kept in step
  with it by hand. The weekly run surfaces container drift, not workflow drift.
- Expected warnings in the build log that are not ours: `Deprecated symbol KSCAN is enabled`
  (ZMK on Zephyr 4.1), `ZMK_USB ... unsatisfied dependencies` on the left half (set by the board
  defconfig, the peripheral has no USB HID), an unused variable in
  `input_processor_temp_layer.c`, and array-bounds warnings in `settings_reset`.
- The release job has not run on GitHub yet.

## Notes

The local build command and the Docker image are in `spec/05-firmware.md`, section 1.
