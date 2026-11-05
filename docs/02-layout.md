# Key layout

The whole geometry of k0d3ball36 lives in one file, `hardware/layout/k0d3ball36.yaml`. The
generator `scripts/gen_layout.py` turns it into `hardware/layout/output/points.json` (consumed by the
schematic and PCB generators, the tests and the firmware physical layout), `outline.dxf` (for the case)
and the two previews below. Nothing in the PCB is placed by hand.

![right half](../hardware/layout/output/preview-right.png)

![left half](../hardware/layout/output/preview-left.png)

![layout diagram](images/img-layout-top.png)

## Coordinate system

Right half, millimetres. x grows outward towards the pinky, y grows downward towards the user. The
origin is the centre of the middle-column top key. This is KiCad's screen orientation, so the PCB
generator adds only a page offset. The left half is the mirror image (x to -x) and is built from the
same PCB flipped over.

## Derivation from the Keyball39

The Keyball39 is an MX board on a 19.05 mm grid. Its column stagger and thumb arc were measured from
the published gerbers (switch centre coordinates) and scaled to the Choc 18 x 17 mm pitch. Keyball
files are not reused; only these ratios are.

| Column | Keyball39 stagger (mm) | in key units | k0d3ball36 stagger (x 17 / 19.05) |
|--------|------------------------|--------------|------------------------------------|
| pinky | 11.70 | 0.614 | 10.44 |
| ring | 4.70 | 0.247 | 4.19 |
| middle | 0 | 0 | 0 |
| index | 2.50 | 0.131 | 2.23 |
| inner | 5.00 | 0.262 | 4.46 |

Stagger is the y offset of a column's top key relative to the middle column; positive means lower.
Column x positions are simply 0, +-18 and +-36.

Thumb keys are placed relative to the inner column's bottom key. The Keyball39 offsets (+15.05/+23.75,
-6.50/+25.55 and -27.42/+31.07 mm) are scaled by 18 / 19.05 in x and 17 / 19.05 in y; the 0 / 10 / 20
degree rotations are kept. The resulting pitch between neighbouring thumb centres is 20.4 mm, which leaves a few millimetres
between rotated 1u Choc caps.

## Key table (right half)

| Ref | Name | Row | Col | x | y | Rotation |
|-----|------|-----|-----|---|---|----------|
| SW00 | pinky_0 | 0 | 0 | 36.00 | 10.44 | 0 |
| SW01 | ring_0 | 0 | 1 | 18.00 | 4.19 | 0 |
| SW02 | middle_0 | 0 | 2 | 0.00 | 0.00 | 0 |
| SW03 | index_0 | 0 | 3 | -18.00 | 2.23 | 0 |
| SW04 | inner_0 | 0 | 4 | -36.00 | 4.46 | 0 |
| SW10 | pinky_1 | 1 | 0 | 36.00 | 27.44 | 0 |
| SW11 | ring_1 | 1 | 1 | 18.00 | 21.19 | 0 |
| SW12 | middle_1 | 1 | 2 | 0.00 | 17.00 | 0 |
| SW13 | index_1 | 1 | 3 | -18.00 | 19.23 | 0 |
| SW14 | inner_1 | 1 | 4 | -36.00 | 21.46 | 0 |
| SW20 | pinky_2 | 2 | 0 | 36.00 | 44.44 | 0 |
| SW21 | ring_2 | 2 | 1 | 18.00 | 38.19 | 0 |
| SW22 | middle_2 | 2 | 2 | 0.00 | 34.00 | 0 |
| SW23 | index_2 | 2 | 3 | -18.00 | 36.23 | 0 |
| SW24 | inner_2 | 2 | 4 | -36.00 | 38.46 | 0 |
| SW32 | thumb_outer | 3 | 2 | -21.78 | 59.65 | 0 |
| SW33 | thumb_middle | 3 | 3 | -42.14 | 61.26 | 10 |
| SW34 | thumb_inner | 3 | 4 | -61.91 | 66.19 | 20 |

Rotation follows the KiCad convention (positive is counter-clockwise on screen). Each key's diode
sits 6 mm below the switch centre, rotated with it. The reference designators double as matrix
positions: `SWrc` is row r, column c; column 0 is the pinky, column 4 the inner index column, row 3
the thumb row. Cells (3,0) and (3,1) do not exist.

## Trackball zone

| Item | Value |
|------|-------|
| Ball centre | (+12.0, +65.0), below the middle/ring columns, outboard of the outer thumb key |
| Ball diameter | 25 mm (cradle also available for 34 mm, needs a different cutout) |
| PCB cutout | 30 mm diameter, the cradle cup passes through it |
| Cradle flange | 34 mm diameter used for clearance checks; three M2 holes on a 36 mm circle at 90, 210 and 330 degrees; the outline ring is cradle radius plus 3.5 mm so the holes keep 0.3 mm to the edge |
| Keycap clearance | at least 1.0 mm between the flange outline and any keycap (checked by the generator) |

The ball centre was moved down until the ring-column bottom key cleared the flange; moving it outward
instead collides with the pinky column. The cutout and the flange holes exist on both halves because
the PCB is reversible; the left half simply leaves them empty.

## Controller block and connectors

| Part | Position | Notes |
|------|----------|-------|
| Controller U1 | centre (-58, 14), USB at the top edge | nice!nano v2 / SuperMini, component side up, on 1.27 mm sockets, battery underneath |
| Solder jumpers JP1..JP3 | (-58, -6.5), 3 mm pitch, above the controller | RAW / RST / VCC row selection per half |
| Test pads TP1..TP3 | (-47, 5), 2.54 mm pitch | spare controller pins |
| Power switch PS1 | (-68.5, 30), rotated 90 | MSK12C02, actuator through the inner edge |
| Reset button RB1 | (-66, 38) | EVQ-P7A, bottom side |
| Battery pads J2 | (-48, 40) | 2.54 mm pitch, B+ is the square pad |
| JST J3 | (-56, 42) | optional, 6 mm tall |
| FPC J1 | (-4, 48.2) | FH12-6S, bottom side, cable exits towards the ball zone |

## Mounting holes

Six M2 holes per half. They sit in the 4.2 mm gaps between switch bodies and outside the bands the
hot-swap socket pads occupy on either face:

| Hole | x | y |
|------|---|---|
| H1 | 27.0 | 10.8 |
| H2 | 27.0 | 44.5 |
| H3 | -9.0 | 40.0 |
| H4 | -27.0 | 8.0 |
| H5 | -32.0 | 61.0 |
| H6 | -67.0 | 45.0 |

The three cradle holes HB1..HB3 can carry case standoffs as well.

## Outline

The outline is the union of all keycap rectangles (plus 0.5 mm margin and 1.1 mm extra per side for
the socket pads), the stepped bridges between neighbouring columns, the controller block, the ball
zone and two bridges that tie the ball zone to the key block and to the outer thumb key. Corners are
rounded with 2 mm. Size of one half: about 120.4 x 93.5 mm (bounding box).

## Changing the layout

1. Edit `hardware/layout/k0d3ball36.yaml` (stagger, thumb offsets, ball centre, part positions, holes).
2. Run `make layout`. The generator prints every key and refuses to write if keycaps overlap, the
   cradle touches a cap, a hole collides with a switch body or sits too close to the edge.
3. Look at `hardware/layout/output/preview-right.png`.
4. Run `make sch pcb route drc` to regenerate and re-route the board, then `make test`.
5. Regenerate the firmware physical layout from `points.json` (ticket `fw-physical-layout-exact-coords`).

```prompt
Clean technical top-view diagram of a 36-key split keyboard right half on white background:
five columns of three keys in a column-staggered grid (middle column highest, pinky column lowest),
three thumb keys fanning out at 0, 10 and 20 degrees below the inner column, a 25 mm trackball circle
at the lower right below the middle and ring columns, a Pro Micro sized controller rectangle at the
left edge, six small mounting hole circles, dimension lines showing 18 mm column pitch and 17 mm row
pitch, thin grey lines, labels in a sans-serif font, 16:10.
```
