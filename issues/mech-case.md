---
title: Boxy angular 3D printed case with raised controller box and ball pocket
type: feature
priority: P2
status: in-progress
area: mech
created: 2026-11-05
---

# Boxy angular 3D printed case with raised controller box and ball pocket

## Context

Separate phase after the r2 hardware is frozen. Two-part printed case per half in the style of the
reference build (Keyball39ish-LP in a self-designed case): a flat, boxy tray whose walls follow the
stepped PCB outline from `hardware/layout/output/outline-left.dxf` and `outline-right.dxf` (90 degree
steps, no rounding), walls flush with the keycap skirts, a raised rectangular box over the
controller block at the inner edge (room for the controller on 2.5 mm sockets, the power switch
slot, the reset hole, the USB-C opening and a window for the controller LED; raising the box is
now a styling choice, the controller top is only +5.7 mm), a 9 mm deep battery well under the
controller block on both halves (`battery` block in `points-left.json` / `points-right.json`:
bay 21 x 41 mm centred (-53.9, 17.5), floor at -10.6 mm or the pocket level -11.6 mm, J3 at
(-56, 44) and RB1 at (-66, 41) below the bay inside the same well), a 32 mm pocket beside the right PCB for the trackball module
(`mech-case-ball-pocket`), five M2 standoffs per half on the PCB holes, rubber feet.

## Acceptance criteria

- [x] Parametric CAD in `hardware/case/` using the per-half layout (`scripts/gen_case.py` writes `data.scad` from `k0d3.geometry`, both halves from one set of sources, left mirrored)
- [x] Both halves printable without supports in CAD (`tests/test_case.py` sums the downward faces: only the USB, switch and LED openings, the magnet pockets and the boss chamfers remain); the test print is open
- [x] Controller block: separate cap plate at +6.7 under / +8.7 top clears the controller top (+5.7) by 1 mm, LED window on the inner wall (position to verify on the controller)
- [x] Battery well under the controller block on both halves: 10.0 mm below the PCB underside (-11.6, shared with the pocket floor) over the bay rectangle plus the J3 and RB1 courtyards
- [x] Image prompts for renders in `spec/images/PROMPTS.md` (`img-case-exploded`, `img-case-tray-top`, `img-case-controller-box-section`)

## Notes

Blocked by hw-two-pcbs-r2 (final outlines) and mech-case-ball-pocket. Each half also gets a
removable lid that covers keys and ball for transport and attaches under the half as a foot
(`mech-case-lid`); the cradle cup is open, so the lid (or the optional clip-on retainer,
`mech-ball-retainer-clip`) is what keeps the ball in a bag.
The lid holds on top by an inner lip; the tray only provides the four magnet pockets in the
floor for the foot position.

2026-11-06: CAD done in `hardware/case/` (tray, box cap, dummies, previews, `stack.json`). Key
numbers: wall 3.0, rim +5.0, key floor -4.6, well and pocket floor -11.6, underside -14.1 flat,
standoffs 6.0 mm with M2 heat-set inserts (3.2 mm holes, 4 mm deep; `-D pcb_screws="pilot"` for
self-tapping), controller box walls to +8.7 with a separate cap on two M2 screws in corner
bosses, USB 11 x 5.8, switch slot 7 x 3, reset pin hole 3 mm, LED window 3 x 3. Open: test
print and fit of both trays. See `spec/11-case.md`.
