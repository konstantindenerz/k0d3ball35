---
title: Eight DRC rules are downgraded to warning, six without a substitute test
type: task
priority: P3
status: open
area: hw
created: 2026-11-07
---

# Eight DRC rules are downgraded to warning, six without a substitute test

## Context

`scripts/k0d3/pcb.py` writes `rule_severities` into both main-board projects, and among the 63 entries
these are downgraded from KiCad's default of `error` to `warning`:

| Rule | Substitute test in `tests/` |
|------|------------------------------|
| `hole_to_hole` | yes, `test_drills_keep_the_board_minimum_hole_to_hole` |
| `isolated_copper` | yes, `test_gnd_zones_have_no_slivers` |
| `copper_sliver` | no |
| `connection_width` | no |
| `track_dangling` | no |
| `via_dangling` | no |
| `holes_co_located` | no |
| `padstack` | no |
| `net_conflict` | no, and two of these are outstanding per board (PS1 pad 3) |

Plus six set to `ignore`: `footprint_type_mismatch`, `lib_footprint_issues`, `footprints_on_back`,
`missing_courtyard`, `track_not_centered_on_via`, `footprint_filters_mismatch`.

The gate in `tests/test_kicad_gates.py` runs `--severity-error`, so none of these can fail a build. "DRC
clean" on this project therefore means "clean at error severity, on a rule set where eight normally-fatal
rules were downgraded". Two of the overrides are well justified -- `courtyards_overlap` and
`pth_inside_courtyard` are inherent to the reversible footprints, where the switch body courtyard contains
the socket boss holes -- but nothing in the file distinguishes those from the six that have no stated
reason.

This is not theoretical. `issues/hw-main-pcb-review-r1.md` records a 0.3 mm GND stitching via that sat
0.152 mm from the centre of U1 pad 14, a 1.0 mm hole, i.e. -0.4982 mm hole to hole: a 0.3 mm drill inside a
1.0 mm one. KiCad never reported it, because its `hole_to_hole` rule skips pairs on the same net. The
review of 2026-11-07 found two more same-net pairs on the left board at 0.346 and 0.383 mm, which is the
same defect class a little further out.

## Decision (2026-11-07)

Deliberately **not** restoring the severities for r2.3. For a two-layer board with 93 vias the work of
re-opening the table and fixing whatever falls out is out of proportion to the risk, and the two
hole-spacing offenders were fixed on their own terms instead (numeric rule raised to 0.5 mm, post-route
cleanup in `scripts/route.py`). This ticket exists so the choice is deliberate and visible rather than
accidental.

## Acceptance criteria

- [ ] Each override in `scripts/k0d3/pcb.py` carries a one-line reason, so a justified one is
      distinguishable from an inherited one
- [ ] `copper_sliver`, `connection_width`, `track_dangling`, `via_dangling` and `holes_co_located`
      restored to `error`, or each given a substitute test, or each given a written reason
- [ ] `net_conflict` restored to `error` once PS1 pad 3 has an explicit no-connect net, so a *new* parity
      conflict is visible instead of hiding behind two permanent ones

## Notes

Found during the r2.3 design review (2026-11-07). The sensor board has no severity overrides at all and
runs on KiCad defaults.
