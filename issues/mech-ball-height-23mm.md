---
title: Ball top 23.75 mm over the desk - verify the r2.4 flat stack on a print
type: task
priority: P1
status: open
area: mech
created: 2026-11-05
---

# Ball top 23.75 mm over the desk - verify the r2.4 flat stack on a print

## Context

r2.4 lowered the keyboard with the same 350 mAh cell. The PAW3222 module sits tilted 65 degrees
beside the ball instead of straight under it, the ball pocket is decoupled from the battery well
(floors -7.1 and -7.6 mm), `floor_t` is 2.0 mm and the 1 mm feet sit in 0.8 mm recesses.
Numbers from `hardware/case/stack.json` and `hardware/trackball-cradle/stack.json`, over the desk:

| | r2.3 | r2.4 |
|---|---|---|
| keycap top | 25.6 | **20.8** |
| ball top | 31.7 | **23.75** |
| ball over the caps | +6.1 | +2.95 |
| transport with lid | 31.7 | 27.3 |
| case underside (`base_z`, from the PCB top) | -14.1 | -9.6 |

The cup floor sets the ball height (`drop_cup` 11.53 mm against `drop_board` 10.78 mm), so the
nominal, unmeasured PAW3222 lens values cannot raise the ball; they only decide whether the
module fits. The 65 degree mount has not been printed yet.

## Acceptance criteria

- [ ] Print `hardware/case/stl/pocket-test-right.stl` and the cradle at 0.12 mm, module in the sleeve
- [ ] Lens distance with the 2.0 mm feeler gauge within 2.3 to 2.5 mm; otherwise set `lens_shim` and reprint
- [ ] Measure the tight value: module rear corner 16.4 mm radial (towards +x, no PCB there), 0.3 mm in front of the rib on the pocket wall
- [ ] Ball top measured on the assembled right half, within 0.3 mm of 23.75 mm over the desk
- [ ] Module slides into the sleeve from the open back and seats with its lens face on the cavity floor; Kapton tape holds it
- [ ] Lens gauge fits the 4 mm window: a feeler blade may be too wide, use a 2.0 mm pin or drill shank
- [ ] Two 0.3 mm first-layer slivers beside the FFC exit and a 0.7 mm wedge on the pocket wall top
  print or drop out cleanly and do not snag the cable
- [ ] Cursor tracks in both axes on the printed mount

## Notes

Until 2026-11-06 this ticket tracked the r1 question (25 mm ball, sensor straight below, ball top
about 23 mm over the PCB); r2 answered it with the 19.05 mm ball, r2.4 with the tilted module.
Related: `hw-paw3222-variant`, `mech-case-ball-pocket`, `mech-trackball-cradle`.
