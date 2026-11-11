# Trackball cradle

Parametric OpenSCAD model of the trackball holder: an open cup with three static ceramic
bearings for a 19.05 mm ball, and beside it a sleeve that holds the bought PAW3222 sensor module
tilted 65 degrees. The cradle stands on the case floor in a pocket beside the right PCB. The cup
rim stays below the ball equator, so the ball rests by gravity and lifts straight out for
cleaning. Keeping it in when the half is turned over is the job of the optional clip on the
case's pocket cover (`hardware/case/README.md`), or of the case lid in transport.

Files

| File | Purpose |
|------|---------|
| `cradle.scad` | the model, `part` selects what is rendered |
| `params.scad` | every dimension, documented |
| `Makefile` | builds STL, DXF (floor footprint), PNG previews and `stack.json` |
| `stack.py` | collects the computed stack heights into `stack.json` |
| `stl/` | `cradle-19mm-pocket.stl` |
| `dxf/` | `floor-19mm-pocket.dxf`, the footprint on the case floor with the two screw holes |
| `preview/` | cradle, section and assembly views |

Requires OpenSCAD 2025 or newer with the Manifold backend (tested with 2026.10.11,
`brew install --cask openscad@snapshot`). Build everything with `make`.

## Geometry

Frame: z up, z = 0 is the top surface of the main PCB, the ball centre on the z axis (at layout
(-13.0, +66.0) of the right half), +x outward
(towards the pinky), +y towards the user. That layout frame is left-handed, so `cradle.scad`
flips y once at export: STL and DXF are in the print frame (y away from the user), `stack.json`
stays in the layout frame.

| | z (from `stack.json`) |
|---|---|
| case floor, cradle base | -7.1 |
| ball bottom | -5.1 |
| PCB | -1.6 to 0 |
| cup rim (1 mm below the equator) | +3.425 |
| ball centre | +4.425 |
| ball top | +13.95 (23.75 mm over the desk) |

- **Sensor.** The 14 x 8 mm module sits in a sleeve beside the cup, tilted 65 degrees from
  vertical (`sensor_angle`) and leaning away from the keys (`sensor_az` = 270). It looks at the
  ball through a 4 mm window 25 degrees below the equator; lens distance 2.4 mm nominal.
- **Why 65 degrees works.** Tilted, the upper board edge must stay under the cup rim, so the
  board's width in the tilt plane decides: the old PMW3610 board (at least 13 mm there) allowed
  38 degrees for a 0.06 mm gain, the 8 mm module allows 65 (`spec/08-trackball-module.md`).
- **What sets the ball height.** The cup floor (`cup_floor_t` 2.0 mm), not the module, so the
  module's nominal lens values cannot raise the ball. `tests/test_cradle.py` asserts it.
- **Body.** One piece with vertical walls from the floor to the rim: the cup and, towards the
  sensor, a tab as wide as the sleeve (18 mm) that ends 0.3 mm inside the PCB notch octagon,
  with its 45 degree corners. One 0.8 mm 45 degree chamfer runs along the whole top edge. The tilted module slot is cut into the tab and open at the back.
- **Floor footprint.** The body's plan: 24.05 x 27.73 mm with 0.5 mm clearance
  (`dxf/floor-19mm-pocket.dxf`), extending further on the side away from the keys. The case well (the 24 x 29 mm housing box, offset 2.55 mm in y, plus
  0.5 mm) contains it.
- **Case screws.** Two M2 x 8 countersunk self-tapping screws come up through the case floor
  into the cup skirt, 20 mm apart on the x axis through the ball (`case_screw_sp`). The module has no holes.
- **Above the PCB** the cup is 23.05 mm wide and the tab stays 0.3 mm inside the PCB notch
  (apothem 15.5 mm); nothing of the cradle rises above the cup rim. The notch corner towards the keys is square, so the module drops into the
  pocket and lifts out with the PCB fitted (`issues/mech-cradle-notch-relief.md`).
- **Cable.** The FFC leaves the sleeve below the PCB, climbs past the PCB plane in the gap
  between cup and notch, runs round the cup above the PCB and folds over the board edge into J1
  on the key side.
- **Bearings.** Three 2.0 mm ZrO2 balls at 30, 150 and 270 degrees, 35 degrees below the equator,
  clear of the sensor window. Seats are 1.9 mm holes drilled radially into the solid cup skirt; printed holes come out
  undersize, ream with a 1.9 to 2.0 mm bit.

## Ball retention

The cup has nothing above its rim. The optional retainer clip sits on the case's pocket cover,
not on the cradle (`hardware/case/README.md`, `issues/mech-ball-retainer-clip.md`); its proof
`hardware/case/retention.py` uses this cradle's STL.

## Printing

- PETG or PLA, 0.12 mm layers, 3 perimeters, 30 percent infill.
- Cradle: upright as exported, no supports.
- Deburr the cup rim: a stray strand there makes the ball scrape.

## Assembly

1. Press the three ceramic balls into their seats from inside the cup, a dot of cyanoacrylate at
   each seat rim. Roll the trackball: no click, no scrape.
2. Plug the type B FFC into the module. Seat the module in the sleeve, lens towards the ball.
3. Check the lens distance (test-fit list below).
4. Stand the cradle in the case pocket, two M2 x 8 countersunk screws from below. Snug, not tight.
5. Route the cable round the cup and over the board edge into J1, contacts down, close the lock.
6. Pocket cover on, drop the ball in (case README). Optional: the retainer clip on the cover.

Service: open the lock, pull the cable, undo the two screws, lift the module out. Keycaps and PCB
stay in place.

## Test-fit checklist

- Ball spins freely and touches only the three bearings: a strip of paper passes between ball and
  rim all round.
- Lens distance: ball out, a 2.0 mm feeler gauge on the lens through the window sits flush with
  the cup's inner surface (2.0 + 0.4 mm ball gap = 2.4 mm). Aim for 2.3 to 2.5 mm (datasheet
  window 2.2 to 2.6). Otherwise set `lens_shim` to the difference (positive moves the module
  away from the ball) and reprint; the shim does not move the ball. Suspect the bearing seats
  first: a radial seat error d moves the ball centre by 1.43 d.
- Tight value to measure: module 14.76 mm radial against the 15.5 mm notch apothem.
- With a scrap PCB at the PCB plane, the module goes into the pocket and out again vertically.
- The FFC reaches J1 without a crease.
- Firmware: at 600 CPI a half turn of the ball moves the cursor about one screen width.

## Open points

- The 65 degree mount is unprinted; the print decides (`issues/mech-ball-height-23mm.md`).
- Bearing seat size is tuned for FDM; resin prints need `bearing_fit` set to 0.

## Image prompts

```prompt
Technical cross-section illustration of a 3D printed trackball module standing in a case pocket
beside a keyboard PCB: a 19 mm white ball in a thin blue cup on three small ceramic bearings, the
cup rim just below the ball's equator with nothing above it, beside the cup a small green sensor
board tilted 65 degrees in a printed sleeve looking at the ball's lower flank through a small
window, two screws coming up through the case floor into the cup, dimension line for the 2.4 mm
lens distance, clean CAD line-art style, white background.
```

