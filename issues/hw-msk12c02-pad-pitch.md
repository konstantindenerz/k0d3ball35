---
title: Verify the MSK-12C02 pad pitch against a physical switch
type: question
priority: P1
status: done
area: hw
created: 2026-11-07
---

# Verify the MSK-12C02 pad pitch against a physical switch

## Context

`scripts/k0d3/footprints.py::msk12c02_reversible` places the three terminal pads at

    x = -2.25 / +0.75 / +2.25, y = -1.95, each 0.6 x 1.3 mm

which is a gap of **3.00 mm** between pads 1 and 2 and **1.50 mm** between pads 2 and 3, and the set is not
centred on the 7.0 x 3.0 mm body outline. The two 0.85 mm locating holes in the same footprint *are*
symmetric, at x = -1.5 and +1.5.

A three-terminal slide switch on a 1.5 mm pitch would put its pads at -1.5 / 0 / +1.5. Either the part has
an asymmetric terminal layout, which is possible but then deserves a comment, or pad 1 is misplaced by
1.5 mm. Nothing in the repo records where these coordinates came from -- unlike the Choc socket pads, whose
geometry is credited to kiswitch in `NOTICE`.

PS1 is on both halves, so if the footprint is wrong both boards lose their power switch and neither can be
turned off.

## Resolution (2026-11-08): the part is asymmetric, the footprint is right

Compared against KiCad's own library, which ships with the installation this project builds with:

    /Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/
      Button_Switch_SMD.pretty/SW_SPDT_Shouhan_MSK12C02.kicad_mod

Every coordinate matches: terminals at -2.25 / +0.75 / +2.25, size 0.6 x 1.3; mounting tabs at
(+-3.675, +-1.1), size 1.05 x 0.7; two 0.85 mm NPTH at +-1.5. That footprint's `descr` cites the
SHOU-HAN MSK12C02 datasheet (LCSC C431540). So the 3.00 / 1.50 mm terminal spacing is the part, not a
transcription slip, and no board respin is needed.

Two deliberate deviations from upstream, recorded so the diff is not re-discovered: the fab rectangle here
is 7.0 x 3.0 rather than 6.7 x 2.8 (it serves as a clearance envelope, not a body drawing), and the four
mounting tabs stay unnamed where upstream names them `SH` (they carry no net).

## Acceptance criteria

- [x] The pad coordinates confirmed against a datasheet-derived reference and the citation added as a
      comment in `scripts/k0d3/footprints.py`, credited in `NOTICE`
- [x] `tests/test_footprints.py::test_msk12c02_terminals_match_the_datasheet_footprint` pins the three
      terminal positions, the four tabs and the two locating holes, so the comment is load-bearing
- [x] The physical confirmation handed to `issues/hw-main-pcb-review-r1.md` step 2b, where the parts and
      the 1:1 plot already meet

## Notes

Found during the r2.3 design review (2026-11-07), resolved 2026-11-08.

The original acceptance criterion asked for the check on `build/print/<half>-check-1to1.pdf`. That sheet
deliberately draws no footprints, so the criterion was unachievable as written; the part check belongs on
`build/print/<half>-bottom-1to1.pdf` from `make print-plots`.

Still worth measuring when the switches arrive, on that plot: the terminal pads are only 0.6 x 1.3 mm for
a part actuated by a fingernail through the case wall. The four 1.05 x 0.7 mm mounting tabs are what carry
the mechanical load, which is the right arrangement -- but they should be measured too while the part is
on the paper.
