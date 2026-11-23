# Printed keycaps

Parametric OpenSCAD model of a low profile 1u keycap for Kailh Choc V1 (PG1350) at 18 x 17 mm
spacing, made for FDM printing with a 0.4 mm nozzle. It is the printed alternative to the MBK caps
in the BOM (`spec/03-bom.md`). There is one body with three tops:

- finger keys: a shallow cylindrical dish across the key;
- the two index home keys (F and J, `index_1` on both halves): the same dish with a rounded bar;
- thumb keys: no dish, a flat top with a 1.5 mm round-over for the side of the thumb.

Ticket: `issues/mech-keycaps.md`.

**Status: untested.** No cap has been printed or put on a switch yet. Print the fit test first.

Files

| File | Purpose |
|------|---------|
| `keycaps.scad` | the model, `part` selects what is rendered |
| `params.scad` | every dimension, documented; `stem_fit` is the one to tune |
| `Makefile` | `make` builds the STLs and the preview (`make keycaps` at the top level) |
| `stl/` | `keycap-1u.stl`, `keycap-1u-homing.stl`, `keycap-thumb.stl`; `keycap-fit-test.stl`, six stem tabs |
| `preview/` | `keycaps.png`: finger, homing and thumb cap |

Requires OpenSCAD 2025 or newer with the Manifold backend (tested with 2026.10.11).

## Geometry

Cap frame: x across the key, y away from the user, z up, z = 0 the flat underside of the top that
rests on the switch slider. Heights over the PCB top use the Choc V1 drawing (CPG135001D01): the
slider top stands at +8.0 at rest, the housing top at +5.0, the 15 x 15 mm flange reaches +3.0,
travel 3.0 mm.

| | cap frame | over the PCB top |
|---|---|---|
| top edge | +2.6 | +10.6 |
| homing bar top | +2.5 | +10.5 |
| dish bottom (0.6 mm deep) | +2.0 | +10.0 |
| underside of the top, on the slider | 0 | +8.0 |
| skirt bottom at rest | -1.3 | +6.7 |
| skirt bottom pressed | | +3.7, 0.7 over the flange |
| leg tips | -3.0 | +5.0 |

- **Footprint** 17.4 x 16.4 mm, corner radius 1.0. That is 0.1 under the 17.5 x 16.5 mm
  envelope every case check uses (`cap_size`, `cap_skirt_z` 5.0, `cap_top_z` 11.0 in
  `hardware/case/params.scad`), so neighbouring caps keep 0.6 mm instead of 0.5.
  `tests/test_keycaps.py` keeps all three caps inside that envelope. The lid, the box
  clearance and the interference test then hold for the printed caps as they are.
- **Wall** 1.0 mm. The 15.4 x 14.4 mm cavity clears the 13.8 mm housing by 0.3 mm a side.
- **Top** 2.0 mm thick at the dish bottom.
- **Stem legs** nominal 1.20 x 3.00 mm (the slider sockets), 5.70 mm apart, 3.0 mm long, with a
  0.2 mm chamfer at the tip. `stem_fit` (default 0.10) comes off both width and length.

## Printing

Each STL is already oriented: the cap stands on its back face, the side away from the user. In
that orientation the layers run along the legs, so the legs do not snap off at the root, and the
dish and the homing bar print as clean vertical walls.

- Material: PETG or ASA. PLA legs are brittle and crack after a few pulls.
- Layer height 0.08 to 0.12 mm, 3 walls, 100 % infill (the caps are almost all wall anyway).
- Support only under the legs: tree supports, or normal supports painted on the legs only. Nothing
  else on the cap overhangs.
- Slow outer walls (20 mm/s or less), seam at the back. Print a batch as "one object at a time"
  if the slicer strings between caps.
- Elephant's foot compensation on, the face on the bed is the back face of the cap.

How many, for the grey/white/orange set:

| STL | Colour | Left | Right | Total |
|---|---|---|---|---|
| `keycap-1u.stl` | grey, pinky column (`pinky_0` to `pinky_2`) | 3 | 3 | 6 |
| `keycap-1u.stl` | white, the other finger keys | 11 | 11 | 22 |
| `keycap-1u-homing.stl` | white, `index_1` (F left, J right) | 1 | 1 | 2 |
| `keycap-thumb.stl` | orange, thumb keys | 3 | 2 | 5 |
| | | 18 | 17 | 35 |

## Fit test

`keycap-fit-test.stl` holds six tabs on snap-off bridges. Each tab is a 12 x 7 mm plate with
the two legs. Tab n has n notches in its top edge and `stem_fit` 0.00, 0.05, 0.10, 0.15, 0.20,
0.25 (tab 1 to 6, the tightest first). Print it with the same printer, filament and settings as
the caps, and with support under the legs.

1. Snap the tabs off and clean the leg tips.
2. Push each tab onto a bare Choc V1 switch, starting with tab 6 (the loosest).
3. Pick the loosest tab that stays on when the switch is turned over and shaken, and that comes
   off without cracking. Push it on and pull it off five times; it should not get loose.
4. Set `stem_fit` in `params.scad` to that tab's value and run `make keycaps`.

If tab 1 is still loose, the printer prints the legs thin: lower the flow or the line width
instead of going below 0.00. If tab 6 is still too tight, check the leg tips for an elephant's
foot or blobs before you go further.
