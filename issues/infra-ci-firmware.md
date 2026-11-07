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
  `k0d3ball35-firmware`.
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

## What you must do

1. Push the repository to GitHub and enable Actions (Settings > Actions > "Allow all actions and
   reusable workflows"; the build calls a reusable workflow from `zmkfirmware/zmk`).
2. Check the first run of `firmware` and download `k0d3ball35-firmware`. Tick the first criterion.
3. Push a tag (`git tag v0.1.0 && git push --tags`) once and verify the UF2 files appear on the
   release. The `release` job needs `contents: write`, which the default `GITHUB_TOKEN` grants
   unless the repository restricts workflow permissions to read-only.
4. Fix the `url:` in `k0d3ball35.zmk.yml` to the real repository (`issues/doc-zmk-yml-repo-url.md`).

## Remaining risks

- The workflow references `build-user-config.yml@main`; upstream can change its inputs or the
  container. The weekly run surfaces this, `tests/test_firmware_build_config.py` only checks the
  inputs known today.
- Expected warnings in the build log that are not ours: `Deprecated symbol KSCAN is enabled`
  (ZMK on Zephyr 4.1), `ZMK_USB ... unsatisfied dependencies` on the left half (set by the board
  defconfig, the peripheral has no USB HID), an unused variable in
  `input_processor_temp_layer.c`, and array-bounds warnings in `settings_reset`.
- The release job has not run on GitHub yet.

## Notes

The local build command and the Docker image are in `spec/05-firmware.md`, section 1.
