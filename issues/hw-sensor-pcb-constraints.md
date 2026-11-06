---
title: Sensor PCB must match the cradle geometry
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Sensor PCB must match the cradle geometry

## Context

The cradle (`hardware/trackball-cradle/cradle.scad`) fixes how the sensor board mounts: optical centre of the
PMW3610 at the board centre, two M2 holes 20 mm apart along the 25 mm axis, the lens along the 26 mm side
(the board came out 26 x 25 mm, see mech-cradle-sensor-26mm), FPC connector and anything taller than 3.4 mm on the pin side only. The main PCB underside must stay
free within a 40 mm circle around the ball centre for the flange.

## Acceptance criteria

- [x] hardware/sensor-pcb outline, holes and lens orientation match the cradle parameters
- [ ] Main PCB has no bottom-side parts within 20 mm of the ball centre (only the socket of SW32 is close; check)
- [ ] tests/test_geometry.py checks the 40 mm flange circle against bottom-side parts

## Notes

Cradle preview and stack numbers in `hardware/trackball-cradle/`.

### Comparison sensor PCB vs cradle (2026-11-06, `tests/test_sensor_pcb_vs_cradle.py`)

All numbers are read programmatically from `hardware/sensor-pcb/k0d3ball35-sensor.kicad_pcb`,
`hardware/trackball-cradle/params.scad` and `stack.json` (19mm-pocket). Board coordinates: optical
centre at (110, 110), cradle local x = lens / pin-row axis (26 mm side), local y = hole axis (25 mm).

| Item | Sensor PCB | Cradle | Result |
|------|-----------|--------|--------|
| Board outline | 26.00 x 25.00 mm (x 97..123, y 97.5..122.5), 2 mm corner radii, 1.6 mm | `sensor_pcb_w` 26, `sensor_pcb_l` 25, `sensor_pcb_t` 1.6; board cavity 26.4 x 25.4 (`sensor_pcb_gap` 0.2 per side) | match |
| M2 holes | H1 (110, 100), H2 (110, 120), 2.2 mm NPTH, 20.00 mm apart on the 25 mm axis, midpoint (110, 110) = board centre | `sensor_hole_sp` 20 on local y, 5 mm post columns, 1.6 mm pilot, `case_screw_d` 2.0; `case_screw_sp` 20 | match |
| Optical centre | U1 origin (110, 110), on B.Cu (ball side); pin 1 at (113.18, 115.35): 3.18 mm from the centre along the row, rows at +-5.35, lower row shifted 0.89 | ball axis through the midpoint of the two posts | match. Datasheet figure 5: optical centre 3.18 from the pin 1 column, 5.35 between the rows (10.70 row spacing); bullwinkle3000/pmw3610-pcb shows the same 3.18 offset |
| Sensor body cutout | 16.96 x 8.60 mm, x -11.00..+5.96 and y +-4.30 from the optical centre (datasheet figure 5: 14.18 / 2.78 / 1.05 / 9.65 from pin 1) | lens cavity 24 x 23 x 3.8 mm (`sensor_pcb_w - 2`, `sensor_pcb_l - 2`, `lens_h + 0.4`) | fits: 1.0 mm margin on the far side, 6.04 on the pin 1 side, 7.2 in y; 0.7 mm body protrusion vs 3.8 mm depth |
| Lens LM18-LSI | datasheet PMS0039 R1.03 figure 1: base flange 12.90 x 8.25 (reference surface), upper body 10.29 x 6.55, 5.95 mm tall incl. two 0.90 mm guide posts, base 2.12 | post columns leave 15.0 mm between them (inner edges at y +-7.5); `lens_l` 21.5 x `lens_w` 11.5 are over-estimates; lens reference plane 3.4 above the board plane (`lens_h`), cavity ceiling at 3.8, so the lens hangs on the sensor with 0.4 mm air above the ceiling-equivalent "base plate" | fits with 3.4 mm to each post column. The cradle lens parameters only size the assembly dummy and can shrink to 12.9 x 8.25 |
| Lens placeholder on `Dwgs.User` | 16.96 x 17.0 mm (y +-8.5) in the footprint, marked approximate | post columns at y +-7.5 | mismatch of the placeholder only: it overlaps each post column by 1.0 mm; the real lens (+-4.125) clears them by 3.4 mm. Replace the placeholder by 12.9 x 8.25 in `generate.py` (mech-lm18-lens-outline-measurement) |
| Component gap | tallest parts on the component side: J1 FH12 2.0 mm (Hirose: standard flip-lock height 2.0), U1 package on the pin side 1.65 (9.05 - 7.40), U2 SOT-23 max 1.45, 0603 max 0.95, test points 0 | floor -11.6, board underside -9.35 (`sensor_pcb_plane_z` -7.75 - 1.6): 2.25 mm; `sensor_pins_h` 2.25 | holds, 0.25 mm left under J1 |
| Sides | U1 is the only footprint on B.Cu; the other 24 footprints are on F.Cu | lens side up against the housing face, component side towards the floor | match |
| FPC connector | J1 at (117.6, 102.45) rot 180 on F.Cu; body 7.1 mm (FH12-06S C) spans 4.05..11.15 mm from the centre line; cable mouth at y 98.05, 0.55 mm from the top edge (y 97.5, one end of the hole axis); courtyard 113.05..122.15 x 97.55..105.45 inside the board | cable slot in the -y wall 24 mm wide (`housing_x - 2 * corner_post`, x +-12), from the floor to the board plane (3.85 mm) | inside the slot with 0.85 mm to the slot edge; the mouth faces the slotted wall, so the FFC runs out through the slot in the 2.25 mm gap |
| Housing | - | 30 x 29 mm outer, walls 2.0 (1.8 beside the board cavity) | STL cross-sections of `build/cradle-19mm-pocket.stl`: board cavity walls at x +-13.2 / y +-12.7, slot edges x +-12, lens cavity x +-12 / y +-11.5, ceiling at board plane + 3.8, post columns r 2.5 at (0, +-10) |

Z stack cross-check against the datasheets: `lens_z` 2.4 is the typical of 2.2..2.6, `lens_h` 3.4 equals
"gap between PCB and base plate" (figure 4), and `sensor_pcb_plane_dist` 15.325 = 19.05 / 2 + 2.4 + 3.4.

Sources: PMW3610DM-SUDU datasheet PMS0003 R2.4
(https://trackballs.eu/media/Nakabayashi/Digio2/PMW3610DM-SUDU.pdf, mirror
https://www.epsglobal.com/Media-Library/EPSGlobal/Products/files/pixart/PMW3610DM-SUDU.pdf); LM18-LSI
datasheet PMS0039 R1.03 (https://github.com/ufan/pmw3610_breakout/blob/master/datasheet/lens-LM18-LSI.pdf);
Hirose FH12 catalogue (https://media.digikey.com/pdf/Data%20Sheets/Hirose%20PDFs/FH12.pdf);
reference footprints https://github.com/bullwinkle3000/pmw3610-pcb and https://github.com/ufan/pmw3610_breakout.

The second and third criteria describe the r1 cutout mount (flange under the main PCB). In the r2 pocket
mount the module stands beside the right PCB and there is no flange; they stay open until the ticket is
rewritten for the pocket geometry (`issues/mech-case-ball-pocket.md`).
