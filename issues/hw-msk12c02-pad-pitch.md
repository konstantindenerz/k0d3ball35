---
title: Verify the MSK-12C02 pad pitch against a physical switch
type: question
priority: P1
status: open
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
turned off. The switches are already in hand (ordered from keycapsss), and
`docs/12-order-checklist.md` already calls for a 1:1 paper check -- this ticket is only here to make that
check blocking rather than optional, and to record the anomaly so it is not re-discovered later.

## Acceptance criteria

- [ ] `build/print/<half>-check-1to1.pdf` printed at 100 % and a physical MSK-12C02 laid on the PS1
      outline: all three terminals land on their pads, and the four mounting tabs land on theirs
- [ ] The pad coordinates either confirmed with a datasheet or drawing reference added as a comment in
      `scripts/k0d3/footprints.py`, or corrected and the boards regenerated
- [ ] `issues/hw-jlcpcb-order-r1.md` references this ticket as a blocker for the main boards

## Notes

Found during the r2.3 design review (2026-11-07). Also worth checking on the same plot: the terminal pads
are only 0.6 x 1.3 mm for a part that gets actuated by a fingernail through the case wall. The four
1.05 x 0.7 mm mounting tabs at (+-3.675, +-1.1) are what carry the mechanical load, which is the right
arrangement -- but they should be measured too while the part is on the paper.
