---
title: Manual review of both main PCBs (r2) before ordering
type: task
priority: P0
status: open
area: hw
created: 2026-11-05
---

# Manual review of both main PCBs (r2) before ordering

## Context

Both r2 boards (`hardware/left-pcb/k0d3ball35-left.kicad_pcb`, `hardware/right-pcb/k0d3ball35-right.kicad_pcb`)
are generated and autorouted; a human pass in the KiCad GUI with 3D models is still required before money is spent.

Everything that can be checked from the board files is automated in `tests/test_pcb_review.py`
(run `.venv/bin/python -m pytest -q tests/test_pcb_review.py`; the silkscreen check needs
`kicad-cli`). Items marked "(automated)" below are green on the current boards; the two defects found
in the first pass are fixed and their regression tests run as plain tests (no `xfail` left).

## Acceptance criteria

- [x] Socket pad orientation matches a real CPG135001S30 (both boards) (automated: pad set equals the kiswitch reference, see notes; a 1:1 paper check with a real socket remains below)
- [x] FH12-6S orientation on the right board: contacts towards the keys, cable exits towards the pocket (+y) (automated; the cable pin order itself is ticket `hw-ffc-pin-order-verification`)
- [x] MSK12C02 actuator reaches the inner board edge and can be moved from outside the case (**defect 1**, fixed 2026-11-06: rotation 270, `test_power_switch_actuator_points_through_the_inner_edge` passes)
- [x] Silkscreen: `LEFT half` / `RIGHT half`, revision r2, pin names at the controller (automated)
- [x] Controller USB-C overhang at the top edge (**defect 2**, fixed 2026-11-06: shell overhangs by 1.5 mm, `test_controller_usb_overhang_per_spec` passes); battery bay outline on the back silkscreen under U1 free of parts (automated, only U1's socket tails inside), socket tails cut flush there (hand, after assembly)
- [x] Five mounting holes per board clear switch bodies and sockets (automated; see the clearance table, H1 is tight to the SW11 socket)
- [x] Right board: octagonal notch (apothem 15 mm) present, no copper, pour or via inside the notch or within 0.3 mm of its edge; no cradle holes anywhere (automated)
- [x] Left board: three thumb positions, no FPC footprint, nine test pads (D0, D1, D2, D3, D9, D10, D14, D15, D16); right board: two thumb positions, five test pads (automated)
- [x] Routed tracks reviewed for ugly detours near the controller and the thumb cluster on both boards
      (scripted pass 2026-11-07, see below; two drill defects found and fixed, the eyeball pass in the
      GUI stays with the remaining hand checks)

Additional items verified by the tests: every controller hole carries the net the pin table in
`spec/01-design-spec.md` section 2 demands (RAW, GND, RST, VCC on holes 13 to 16 of the
right-hand row, sensor pins on `TB_*` on the right and on `TP_*` on the left), the pin labels
next to the holes read the right names, the diodes all point cathode (pad 1) to the row net with
the silkscreen bar on the cathode side and follow the switch rotation, both back-face socket pads
of every switch are reached by copper, all copper keeps exactly 0.300 mm from the board edge, the
GND pours are filled on both faces, RAW and BAT+ tracks are 0.4 mm wide, and silkscreen over
copper is limited to the cosmetic list in the notes.

## Notes

### Defect 1: power switch PS1 is rotated the wrong way (both boards)

`power_switch: { center: { x: -68.5, y: 30.0 }, rotation: 90 }` in `hardware/layout/k0d3ball35.yaml`
was meant to put the actuator through the inner edge. The footprint `SW_SPDT_MSK12C02_reversible`
has its three solder pins at local -y and the actuator at local +y (0 to 2.9 mm past the body). KiCad
rotates counter-clockwise on screen, so 90 degrees maps local +y to +x: on both boards the actuator
points **into** the board (frame x -67.0 to -65.6, under the controller's courtyard) and the
solder pins face the inner edge (pads at x -70.45, edge at x -71.5, 0.4 mm copper clearance).
Consequences visible in DRC warnings: `courtyards_overlap PS1 / U1`, the `ON` label of PS1 lies
on controller hole 12, the U1 silkscreen box crosses a PS1 tab pad.

Fix (not applied here, the boards are not re-run in this ticket): rotation 270 (or -90) in the yaml,
then `make layout`, `make pcb route drc gerbers` with `JAVA=/opt/homebrew/opt/openjdk/bin/java`.
With 270 degrees the pads move to x -66.55 (clear of the edge by 4.6 mm) and the actuator tip
reaches x -71.4, 0.1 mm inside the edge line at x -71.5, which is what the case slot needs; if more
protrusion is wanted move the centre to x -69.0 (pads then at x -67.05, actuator tip at -71.9,
i.e. 0.4 mm past the edge; the edge keep-out does not care about the actuator). Re-check
`geometry.back_parts` afterwards: the battery bay clearance of 0.8 mm to the PS1 courtyard was
computed with the courtyard offset on the wrong side and becomes 0.8 mm to the pin side instead.
`test_power_switch_actuator_points_through_the_inner_edge` is the regression test.

**Fixed 2026-11-06:** `rotation: 270` in the yaml, both boards regenerated and re-routed, DRC clean.
The battery bay now keeps 0.8 mm to the PS1 pin side; `check_layout` still passes.

### Defect 2: no USB-C overhang

The spec and the yaml (`controller.usb_overhang: 1.5`) promise a 1.5 mm USB-C overhang, but
`usb_overhang` is not used anywhere in `scripts/k0d3/geometry.py`. The controller block top edge is
`center.y - size.y / 2 - controller_margin` = -4.75, the footprint's body outline ends at
y -3.35 (the yaml size box at -2.75). The nice!nano PCB therefore ends 1.4 mm **inside** the board
edge and the USB-C shell (about 1.3 mm past the nice!nano PCB) sits roughly flush with the edge.
A plug still fits if the case wall has a window right at the edge, but the geometry does not match
the spec. Decide: either drop the overhang from the spec and the yaml, or make `build_outline` use
`usb_overhang` (controller block top = body top + 1.3 - usb_overhang) and re-run the pipeline.
The U1 reference text on F.SilkS at y -4.6 is clipped by the edge for the same reason
(`silk_edge_clearance` warning). `test_controller_usb_overhang_per_spec` is the regression test.

**Fixed 2026-11-06:** `build_outline` derives the block's top edge from the controller board top
(`pcb_offset_y` -0.6), the shell protrusion past the controller board (`usb_shell` 0.6 mm, 34.1 mm
overall length vs the 33.5 mm board) and `usb_overhang` 1.5 mm. The controller hole-pattern centre
moved from (-58, 14) to (-58, 11.7) so the PCB outline is unchanged: the controller board now
overhangs the top edge by 0.9 mm and the shell by 1.5 mm. `check_layout` verifies the overhang.

### Minor: two GND vias almost touching (right board) - fixed 2026-11-07

DRC `hole_to_hole` warning: the stitching via at frame (9.0, 6.0) and an autorouter via at
(9.475, 6.225) were 0.2256 mm hole to hole (board minimum 0.25 mm, same net). Not fatal (both GND,
JLCPCB only enforces hole spacing between different nets), but the second via is useless and a
drill that close to another may break.

**Fixed 2026-11-07** in `scripts/route.py`: `stitch_ground` now collects every existing hole
(router vias and all pad drills) before it places the grid and skips a grid point whose drill
would come closer than the board's `min_hole_to_hole`. The grid point at (9.0, 6.0) is simply
left out; the right board goes from 41 to 39 stitching vias (87 to 85 vias in total), the left
board is unchanged at 100. The pour-contains test the placement already did only guarantees
*copper* clearance, and copper says nothing about two holes that belong to the same net.

### Defect 3: a stitching via inside a controller pad hole (right board)

Found by the same pass and worse than the one above: a 0.3 mm GND stitching via sat 0.152 mm
from the centre of U1 pad 14 (GND, 1.0 mm hole) at frame (-50.53, 0.23), i.e. **inside** the
controller socket hole, -0.4982 mm hole to hole. KiCad never reported it: its `hole_to_hole`
rule skips pairs on the same net, and the GND pour connects to that pad, so the grid point
passed the "inside both fills" test. The fab would have drilled a 0.3 mm hole into a 1.0 mm
one. Same fix as above (pad drills are part of the hole list);
`test_drills_keep_the_board_minimum_hole_to_hole` is the regression test and fails on the
2026-11-06 board for both defects.

### Hot-swap socket geometry (verified)

Back-face pad set of `SW_Choc_V1_HS_reversible` versus kiswitch `SW_Hotswap_Kailh_Choc_V1_1.00u`
(socket on the back, seen from the front):

| Item | kiswitch | this project |
|------|----------|--------------|
| boss holes | (0, -5.9) and (5, -3.8), 3.05 mm | identical (plus a third hole at (-5, -3.8) for the mirrored set) |
| pad 1 | (-3.5, -6.0), 2.55 x 2.5 | (-3.5, -6.45), 2.55 x 2.0 pill, 0.45 mm further north to clear the mirrored boss hole |
| pad 2 | (8.5, -3.8), 2.55 x 2.5 | identical |

So pad 1 lies west of its boss hole and pad 2 east of its boss hole on both references; the ticket
wording "pads at the right side of the boss holes" holds for pad 2 only, which is correct for the
real socket (its two solder legs point away from each other). The socket body envelope used in the
layout checks (15 x 6.9 mm, local x -4.8 to 10.2, y -8.9 to -2.0) touches the top edge line at the
pinky top key (0.15 mm over, the envelope includes the legs); the pads keep 0.3 mm. The unused front
pad copies have mask openings; the title text crosses the front pad 2 of SW24 (cosmetic).

### Mounting holes (verified, distances from the hole centre, same on both boards)

| Hole | frame (x, y) | nearest switch body | nearest socket body | nearest copper | edge |
|------|--------------|---------------------|---------------------|----------------|------|
| H1 | (27.0, 10.8) | 2.10 (SW00) | **1.49 (SW11)** | 2.43 | 9.2 |
| H2 | (27.0, 44.5) | 2.10 (SW20) | 4.68 (SW20) | 1.63 | 2.8 |
| H3 | (-9.0, 40.0) | 2.10 (SW22) | 5.77 (SW23) | 1.63 to 1.77 | 3.1 / 11.9 |
| H4 | (-27.0, 8.0) | 2.10 (SW03) | 4.56 (SW14) | 1.63 to 3.31 | 12.4 |
| H5 | (-32.0, 61.0) | 3.13 (SW33) | 3.50 (SW33) | 2.17 | 7.4 |

Hole radius is 1.1 mm. For the case: a standoff or washer on the back at H1 must stay below 3.0 mm
in diameter (the SW11 socket body starts 1.49 mm from the hole centre); screw heads on the front
up to 4.0 mm clear the 13.8 mm switch housings by 0.1 mm at H1 to H4, so prefer M2 heads of 3.5 mm
or countersunk screws from the back.

### Silkscreen over copper (DRC warnings reviewed, all cosmetic)

| Board | Item | Verdict |
|-------|------|---------|
| both | `TPn` reference labels touch the neighbouring test pad (2.5 mm pitch, label 2.2 mm right of the pad) | clipped by the mask, pads are bare copper anyway; tidy by moving the label below the pad |
| both | title text crosses the unused front pad 2 and the boss hole of SW24 | under the keycap, invisible |
| both | dashed battery bay outline crosses U1 holes 11 and 23 on the back | the bay ends at y 25 inside the hole rows (holes 11/23 are at y 25.43) |
| both | `ON` label of PS1 on U1 hole 12, U1 silk box on a PS1 tab pad | disappears with defect 1 |
| both | `U1` reference clipped by the top edge | disappears with defect 2 or by moving the label |
| right | `J1` reference on B.Fab not mirrored | fab layer only, no silkscreen |

`test_silk_over_copper_only_known_cosmetic` fails on anything beyond this list.

### Other findings

* Edge clearance: the pours and all tracks reach exactly 0.300 mm from the edge, nothing closer;
  no copper or via inside the notch octagon or within 0.3 mm of it; the ball circle clears the PCB.
* The only 2.2 mm holes are H1 to H5 (no cradle holes); every switch has the 3.40 / 1.70 / 3.05 holes.
* The battery bay rectangle (frame x -64.4 to -43.4, y -3 to 38 since r2.1b) contains nothing on the back but
  the 24 controller socket tails; the JST J3 (6 mm tall) sits below the bay at y 42, inside the
  case well as specified. No back courtyard of PS1, RB1, J3, J2, any socket or diode intersects it.
* J1 (right only): back face only, pin 1 (VCC) at +x seen from the front, i.e. on the pinky side,
  with the `1` silk mark; contacts at y 43.65 towards the keys, hold-down pads at y 46.9 towards the
  pocket; the body ends 1.0 mm above the cradle housing (y 49.5).
* Diodes: pads on both faces tied by the 0.4 mm joiners; the build guide mounts them on the bottom
  face. The cathode bar sits on the pad 1 (row net) side on both silkscreen faces.

## Remaining hand checks (KiCad GUI, in this order)

1. Open `hardware/right-pcb/k0d3ball35-right.kicad_pro`, PCB editor, `View > 3D Viewer` (Alt+3).
   Toggle `View > Flip board` (or press F) for the back. The generated footprints carry no 3D
   models, so judge against the fab outlines: `Preferences > Display options > Fab layers` on,
   `Silkscreen` on, `Solder mask` off.
2. **Without the parts yet:** `make print-check` writes `build/print/<half>-check-1to1.pdf`, an A4
   sheet per half with the board at 1:1, the key grid, the controller hole pattern, the battery bay
   and (right) the notch and ball circle dimensioned in colour, plus a 100 mm and a 50 mm
   calibration bar. It settles two things a ruler can settle - that the print is really 1:1 and that
   the geometry carries the layout's numbers - and the hand check: thumb to ball circle. It does not
   check a single footprint; that is the paper check below. It does print the thumb's reach to the
   ball surface and the height to stack on the ball circle, which is what `mech-thumb-arc-tuning`
   needs. `tests/test_print_check.py` keeps the printed numbers tied to the layout and the PDF
   page box at A4.
2b. **Parts on paper, 1:1 (needs the parts):** `make print-plots` writes
   `build/print/<half>-bottom-1to1.pdf` and `<half>-top-1to1.pdf`, A4 per face, the board at 1:1
   with the pads as outlines carrying their numbers, a 100 mm calibration bar and a red ring round
   each part this step names. Print at 100 %, measure the bar, then place a real CPG135001S30 with
   its two bosses in the 3.05 mm circles of SW22 on the **bottom** sheet: both solder legs must
   land on the two pads and the body must stay inside the dashed 15 x 6.9 outline. Repeat for a
   thumb key (SW33, rotated 10 degrees) and for SW00 at the top edge. The MSK12C02 goes on the
   same sheet: pins on the three 0.6 x 1.3 pads, tabs on the 1.05 x 0.7 pads, actuator past the
   edge line. That last one also closes `hw-msk12c02-pad-pitch`, whose terminal spacing is
   deliberately asymmetric.
3. **FH12-6S:** J1 sits on the key side since r2.2, so it is on the **top** sheet, not the bottom
   one. Put the connector on it with the contact side (the long side with the leads) towards the
   keys and the cable mouth towards the notch. The `1` mark must sit at the pinky-side contact.
   Confirm the mirrored pin order on the sensor board per `hw-ffc-pin-order-verification` before
   soldering anything.
4. **Controller:** in the 3D viewer look at the top edge above U1 from a low angle: the controller
   outline ends at y -3.35 versus the edge at -4.75 (both in the layout frame); after the decision
   on defect 2 the USB-C shell must either overhang or the case gets a window flush with the edge.
   Check that the `USB` marker and the `U1` label are readable.
5. **Battery bay:** back view, confirm the dashed rectangle, the three text lines, and that only
   the controller socket tails are inside it. After assembly, cut the tails flush (the 9 mm well
   budget assumes 1.0 mm of tail).
6. **Routing review:** PCB editor, press the backtick key and click a net to highlight it, in this
   order: `ROW3`, `COL4`, `COL3`, `RAW`, `BAT+`, `TB_SCLK`, `TB_SDIO`, `TB_NCS`, `TB_MOT`, `VCC`.
   Look for detours around the controller block, loops around the thumb keys and long parallel runs
   of the SPI nets. `Inspect > Board Statistics` shows the via count (85 on the right board since
   2026-11-07); anything with more than four vias on one signal net deserves a look. The scripted
   pass below already did the counting, so this step is only the eyeball check.
7. **Mounting holes:** back view, look at H1: the SW11 socket starts 0.4 mm from the hole edge;
   note the standoff limit in the case ticket (`issues/mech-case.md`).
8. Repeat steps 1, 2, 4, 5, 6 and 7 on `hardware/left-pcb/k0d3ball35-left.kicad_pro` (18 keys,
   nine test pads, no J1, the inner thumb key SW34 at 20 degrees is hand-routed).
9. Close with the gerber viewer pass of `test-fab-gerber-viewer` and the drill counts in
    `spec/06-fabrication.md`.

### Routing review, scripted pass (2026-11-07)

Every signal net of both boards measured against the minimum spanning tree over its own pads (the
shortest a router could do with straight lines and no obstacles), plus via counts, dangling track
ends, hole-to-hole distances and parallel runs of the SPI nets:

| Finding | Verdict |
|---|---|
| Worst detour left: `SW33` 53.3 mm of track for a 26.1 mm MST (ratio 2.04) with 5 vias and 26 segments | accepted. A matrix net of a 10 degree thumb key whose front and back socket pad copies sit on opposite sides of D33; about 25 milliohm, no signal integrity meaning. It is the only net on either board above 4 vias, `test_no_signal_net_piles_up_vias` holds the line at 5 |
| Worst detour right: `TB_SCLK` 82.3 mm for 54.0 mm (1.52), `BAT+` 40.6 for 27.1 (1.50), `VCC` 82.2 for 60.3 (1.36) | accepted. The SPI nets run from U1 at the inner edge to J1 at the notch and have to pass the thumb cluster; `BAT+` and `VCC` are 0.4 mm class and go round the battery well |
| Everything else is below 1.4, 29 of 39 nets below 1.2 | no detours worth a hand route |
| Dangling track ends | none on either board (every end sits in a pad or a via) |
| Holes closer than 0.25 mm | two on the right board, both fixed, see defects above |
| `TB_SCLK` and `TB_MOT` run 27.1 mm, `TB_SDIO` and `TB_MOT` 33.1 mm side by side on B.Cu, 0.252 mm edge to edge (0.15 mm tracks) | accepted, see below |

On the parallel SPI runs: the gap is 1.7 track widths over about 30 mm with no GND between the
two (the pour cannot fit into 0.25 mm), and the reference pour is 1.5 mm away on the other face.
That is as tight as it looks, but the same six conductors then run **0.5 mm apart over the whole
length of the FFC**, which is the dominant coupling path and cannot be designed away; the
aggressor is SCLK at 2 MHz, the victim MOT is a level signal that carries a 1 k series resistor
(R3) on the sensor board, and a false edge on it costs a pointer poll, not data. Widening the
gap means hand routes for three nets through the thumb cluster. Revisit only if the first board
shows spurious motion interrupts (`fw-cursor-axis-verification`).

Reproduce: `PYTHONPATH=scripts:tests .venv/bin/python` on the snippet in the ticket history, or
just run `tests/test_pcb_review.py`, which now carries the two assertions that matter.

Use `kicad-cli pcb render` outputs in `hardware/left-pcb/renders/` and `hardware/right-pcb/renders/`
for a first look, then the GUI. Title kept for history; it covers both r2 boards.

Both sheet families are produced into `build/print/` (gitignored, so regenerate after a
checkout). `make print` runs both; `make print-check` is the measuring sheet of step 2 and
`make print-plots` the part-check plots of step 2b.

This ticket used to carry a `kicad-cli pcb export pdf` snippet here. It did not work and is
deliberately not coming back: the generated boards set `(paper "A3")`, so every exported PDF was
420 x 297 mm and an A4 printer either scaled it - destroying the one property the sheet needs - or
clipped it, and the `B.Cu` layer flooded the page with the GND pour over the very pads the sheet
is for. `scripts/gen_print_plots.py` plots the fab layers through the SVG exporter, whose
`--page-size-mode 2` crops to the board, and re-pages the result onto A4 at 1:1.

Print at 100 % (no "fit to page"), measure the calibration bar first, and cross-check the two
sheets against each other: held against a window the outlines must coincide and the measuring
sheet's key grid must fall on the plot's switch holes.

## r2.3 rework (2026-11-07)

The ball moved inboard and the right half swapped its thumb pair
(`hw-ball-inboard-r2-3`), so the right board was regenerated and rerouted from scratch and the
left one got its hand routes re-laid on the 45 degree grid. Everything automated in this ticket
was rerun and is green; the hand checks below are due again on the new boards, with two items
that have moved:

* the socket paper check now applies to SW33 and SW34 on the right (10 and 20 degrees), not SW32
  and SW33,
* J1 sits at (-20.6, 47.4) with the notch edge at y 51, so step 3 looks at a different place.

New since the rework, and worth a look in the GUI: the seven hand routes of the right board and
the nine of the left. They were placed by a grid search over the free copper of each layer and
are checked by `tests/test_generated_tracks.py` against drills, foreign pads, the board edge,
each other and the 45 degree grid - but a human should still look at them once.
