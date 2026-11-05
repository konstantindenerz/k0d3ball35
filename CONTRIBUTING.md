# Contributing

Thanks for your interest in k0d3ball36. This page explains how the repository is organised and
what a change needs before it is merged.

## Ground rules

- All code, comments, documentation and ticket text are written in English.
- `docs/01-design-spec.md` is the contract. If your change alters a pin, a dimension, the matrix or
  the FPC pinout, update the spec in the same change and file a ticket in `issues/`.
- Hardware files are licensed under CERN-OHL-P-2.0, everything else under MIT. Do not import
  material under incompatible licenses (GPL hardware files from other keyboard projects included).
- Images are not committed. Every picture is described as a generation prompt in a fenced
  ```prompt block so it can be produced later.

## Workflow

1. Pick or create a ticket in `issues/` (see the convention in the design spec, section 7).
2. Set its `status` to `in-progress`.
3. Make the change. Run `make test`. For hardware changes also run `make erc drc`.
4. Regenerate the ticket index with `make issues`.
5. Open a pull request. The CI runs the test suite and the KiCad ERC/DRC gates.

## Tooling

| Tool | Version | Install |
|------|---------|---------|
| KiCad | 10.x (pinned in CI) | `brew install --cask kicad` |
| Ergogen | 4.x | `npm i -g ergogen` |
| Python | 3.12+ | `uv venv .venv && uv pip install -e .` or `uv pip install pytest pyyaml kiutils numpy` |
| ZMK | pinned commit in `firmware/zmk-config/config/west.yml` | built in CI, or locally with docker |

## Commit messages

Imperative mood, one topic per commit, reference the ticket slug in the body when applicable.
Example:

```
Add M2 cradle holes to the ball zone

Refs: hw-main-pcb-r1
```

## Filing bugs

Create `issues/<area>-<slug>.md` with the frontmatter fields from the design spec, describe the
observed behaviour, the expected behaviour, and the steps to reproduce. Set a priority:

- P0: blocks the next prototype order or the firmware build
- P1: must be solved before r1 is called done
- P2: should be solved, workaround exists
- P3: nice to have
