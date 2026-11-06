# Build guide

Assembly instructions for one k0d3ball35: a left PCB with 18 keys and a right PCB with 17 keys
and the trackball. The structure follows the Keyball39 build guide: every chapter lists what you
need, numbered steps, and a checkpoint before you move on. Plan two evenings for the electronics
and one for the trackball module and firmware.

Reference documents: [design spec](01-design-spec.md), [BOM](03-bom.md), [firmware](05-firmware.md),
[trackball module](08-trackball-module.md), [cradle README](../hardware/trackball-cradle/README.md),
[testing](07-testing.md). If something here contradicts the design spec, the spec wins and a ticket
belongs in `issues/`.

## Contents

0. Read first
1. Parts and tools check
2. Identify the halves
3. Diodes
4. Hot-swap sockets
5. Controller sockets and header pins
6. Power switch, reset button, FPC connector
7. Battery
8. Flash the firmware
9. Smoke test before closing
10. Sensor board and lens
11. Trackball cradle
12. Switches and keycaps
13. Pairing and trackball tuning
14. Troubleshooting
15. Maintenance
16. Printable checklist

---

## 0. Read first

* **LiPo cells.** Never short B+ to GND, never solder on a cell, never puncture or bend one. Keep
  the power switch off while soldering anything on a half that already has its battery attached;
  better, attach the battery last (chapter 7). Charge only through the controller's USB port.
  Store spare cells at about 50 percent charge in a fireproof container.
* **Two different PCBs.** Since r2 the left and the right half are separate boards. Each has one
  component face (the bottom, with sockets, diodes, switch, button, connector) and one switch face
  (the top, with the controller). There are no mirrored pad sets, no solder jumpers and no
  per-half pin tables: the controller is wired identically on both boards.
* **Hot-swap only.** The switch holes are unplated 3.05 mm holes for the socket bosses; switches
  cannot be soldered directly.
* **ESD.** The nRF52840 and the PMW3610 are CMOS parts. Work on a grounded mat or at least touch
  a grounded metal object before handling the controller and the sensor.
* **Soldering.** 300 to 320 C for leaded, 330 to 350 C for lead-free solder, a chisel tip of 1.5 to
  2 mm for sockets and a 0.8 mm conical tip for the FPC connector and SOD-123 diodes. Use flux on
  every SMD joint. Keep each joint under 3 seconds on the sensor and the controller.
* **Order of operations matters.** Diodes and sockets before the controller, firmware before the
  case, trackball module last.

## 1. Parts and tools check

Lay everything out and tick the list. Quantities are for one keyboard (two halves).

![All parts before assembly](images/img-parts-flatlay.png)

| Qty | Part | Where it goes | Chapter |
|-----|------|---------------|---------|
| 1 | Left PCB `k0d3ball35-left` | left half, 18 keys | 2 |
| 1 | Right PCB `k0d3ball35-right` | right half, 17 keys, trackball | 2 |
| 1 | Sensor PCB `k0d3ball35-sensor` | right half, in the ball pocket | 10 |
| 35 (+ spares) | 1N4148W SOD-123 diode | bottom face, one per key (18 + 17) | 3 |
| 35 (+ spares) | Kailh CPG135001S30 hot-swap socket | bottom face, one per key (18 + 17) | 4 |
| 2 | nice!nano v2 or SuperMini nRF52840 | top face, inner edge | 5 |
| 4 | 1 x 12 socket strip, 2.54 mm pitch, low profile (Mill-Max 315 style) or 2 x 24 conthrough pins | controller | 5 |
| 48 | matching header pins (only with machined sockets) | controller | 5 |
| 2 | MSK-12C02 slide switch | bottom face, inner edge | 6 |
| 2 | EVQ-P7A01P tact switch | bottom face, below the controller | 6 |
| 2 | Hirose FH12-6S-0.5SH (or LCSC clone) 6-pin 0.5 mm FPC connector | one on the right PCB (bottom face), one on the sensor board | 6, 10 |
| 1 (+1) | 6-conductor 0.5 mm FFC, type A (contacts on the same face at both ends), 30 to 50 mm | right half | 11 |
| 2 | JST S2B-PH-SM4-TB battery connector | bottom face, below the controller, inside the battery well | 7 |
| 2 | LiPo 702025, 300 mAh, protected, JST-PH plug | one per half, battery bay on the bottom face under the controller | 7 |
| 2 | foam or Kapton pad, about 20 x 27 x 0.5 mm, plus double-sided tape | between PCB underside and cell | 7 |
| 1 (+1) | PixArt PMW3610DM-SUDU + LM18-LSI lens | sensor board | 10 |
| 1 set | sensor-board passives: XC6206P182MR, 0603 capacitors and resistors as listed in the BOM | sensor board | 10 |
| 1 (+1) | 19.05 mm (3/4 inch) POM trackball, or the PandaKB TB19 phenolic ball | right half | 11 |
| 3 (+3) | 2.0 mm ZrO2 ceramic bearing balls | cradle | 11 |
| 1 | printed cradle (`hardware/trackball-cradle/stl/cradle-19mm-pocket.stl`) | right half, case pocket; no retainer, the case lid keeps the ball in for transport | 11 |
| 2 | M2 x 10 self-tapping screws (or M2 x 10 machine screws + heat-set inserts) | case screws: from below through the case floor and the sensor board into the cradle posts | 11 |
| 2 (optional) | M2 x 5 self-tapping screws | bench test: sensor board in the cradle posts before the case exists | 11 |
| 35 (+2) | Kailh Choc V1 switch (PG1350) | | 12 |
| 35 | Choc 1u keycaps (MBK), 5 in an accent colour for the thumbs | | 12 |
| 8 | bumpers (GLIPLUS pads or 3M SJ5302) | underside | 15 |

Tools:

* temperature-controlled soldering iron, chisel tip 1.5 to 2 mm and a fine conical tip
* 0.5 mm solder (leaded 63/37 is the easiest), flux pen or gel flux, solder wick, isopropyl alcohol
* fine tweezers (ESD safe), small side cutters, a toothpick
* multimeter with diode mode and continuity beep
* M2 screwdriver (PH00 or a 1.5 mm hex, depending on the screws), 1.9 to 2.0 mm drill bit for reaming the bearing seats
* 2.0 mm feeler gauge, or a stack of paper measured with calipers (for the lens distance check)
* 3D printer (0.12 mm layers, PETG or PLA) or a print service for the cradle
* a USB-C data cable, a computer with a file manager and a browser

Checkpoint: every row ticked, the two main PCBs are different (the right one has the octagonal
notch at its lower outer corner and the FPC footprint), the sensor kit has both the chip and the lens.

## 2. Identify the halves

Each PCB has its name and revision in silkscreen on the top face below the controller outline:
`k0d3ball35 r2  LEFT half` or `RIGHT half`. The right PCB is the one with the octagonal notch
beside the thumb keys and the FPC connector footprint J1 between the index/middle bottom keys and
the thumb keys; it has two thumb positions. The left PCB has three thumb positions and no notch.

![Both PCBs with their silkscreen labels facing up](images/img-build-identify-halves.png)

1. Lay both boards down with the silkscreen readable. This is the **top face** of each half:
   switches and the controller go here.
2. The other face is the **bottom face**: sockets, diodes, the slide switch, the reset button and
   (right half only) the FPC connector go here. There is only one pad set per part; nothing is
   mirrored.
3. The controller outline on the top face carries the pin names; they are the same on both halves.

Checkpoint: two different PCBs, each identified, labels readable on the top face.

## 3. Diodes

35 diodes, 18 on the left and 17 on the right, all on the **bottom face**, in the free band south
of each switch (between the switch's centre post hole and the next row).

![Soldering a row of diodes](images/img-build-step-diodes.png)

1. Find the cathode band of a 1N4148W: the thin printed line at one end of the black body.
2. Find the silkscreen bar at one end of each diode outline on the bottom face. The band on the
   diode goes to the **bar end** (this is pad 1, the row line).
3. Tin one pad of the first footprint, hold the diode with tweezers, reflow the tinned pad while
   sliding the diode in, then solder the other pad. Add flux and touch up the first pad.
4. Repeat for all positions. Keep every band pointing the same way within a row; the thumb keys
   are rotated, follow their silkscreen bar, not the neighbours.
5. Do the second half.
6. Test: multimeter in diode mode, red probe on the row pad (band end), black probe on the other
   pad: no reading. Reverse the probes: 0.5 to 0.7 V. Do this for every diode; a wrong one means a
   dead key or a ghosting row.

Checkpoint: 35 diodes, all bands at the bar end, 35 forward readings between 0.5 and 0.7 V.

## 4. Hot-swap sockets

35 sockets on the **bottom face**. Every switch position has the big centre hole, two small post
holes and two 3.05 mm holes for the socket bosses, all on one side: the socket fits one way round,
with its two leaf contacts on the two copper pads.

![Soldering hot-swap sockets](images/img-build-step-sockets.png)

1. Hold a socket against the bottom face with its two bosses in the boss holes; the two metal
   leaf contacts must land on the two copper pads.
2. Tin both pads lightly. Press the socket down with a fingertip or a wooden stick, reflow the
   first pad until the solder flows under the contact, then do the second pad. Reheat the first pad
   with a little fresh solder so both joints have a smooth fillet.
3. The socket must sit flat; a tilted socket will not take a switch. Reheat and press down if
   needed.
4. After each row, push a spare switch into two or three sockets from the top face as a fit test
   and pull it out again.
5. Continuity test: beep between the socket contact near the diode and the diode's anode pad
   (the non-bar end), and between the other socket contact and the column line (any other socket
   in the same column, same contact side).

Checkpoint: 35 sockets flat, every switch position accepts a test switch, no solder bridge between
a socket pad and the neighbouring diode.

## 5. Controller sockets and header pins

The controller sits on the **top face** at the inner edge in the rectangular controller block,
component side up, USB-C connector towards the top edge, on the lowest sockets you can get
(Mill-Max 315 with 3320 pins, or conthrough spring pins; about 2.5 mm). Nothing goes between the
controller and the PCB: the cell lies on the other face, in the battery bay printed on the bottom
silkscreen right under the controller. Same on both halves.

![Controller on low-profile sockets](images/img-build-step-controller.png)

1. Push two 1 x 12 socket strips into the two rows of holes from the top face. Flip the board
   onto a flat surface so the sockets are pressed flat against the PCB, solder one pin of each
   strip, check that both strips stand square, then solder the rest. Conthrough pins instead:
   press them into the controller only, as their instructions say; they are never soldered to the
   PCB.
2. Header pins into the controller: put the pins into the sockets first, set the controller on
   top with the **USB connector at the top edge and the chip facing up**, check that the hole marked
   with a square pad (hole 1, D1) is at the top-left of the footprint, then solder the pins to the
   controller. Do not solder the controller directly to the PCB; the socket makes it replaceable.
3. Pull the controller off again. It goes back on in chapter 8.
4. Cut the socket tails flush on the **bottom face** inside the dashed battery bay and file off
   any sharp solder spike: the cell will lie against this area with only a 0.5 mm pad in between.
   Nothing may protrude more than 1 mm there.

Checkpoint: two socket rows soldered flat, controller plugs in and out, USB connector at the top
edge, square pad at top-left, bottom face inside the battery bay smooth.

## 6. Power switch, reset button, FPC connector

All on the **bottom face**. The FPC connector exists only on the right PCB.

![Power switch, reset button and FPC connector on the bottom face](images/img-build-step-power-switch.png)

Power switch MSK-12C02 (PS1, inner edge of the controller block):

1. Place the switch so that its actuator points to the inner board edge and the three pins land
   on the three signal pads; the four wider pads take the metal shell tabs. The pins fit only one
   way round.
2. Solder one shell tab, align, solder the other tabs, then the three pins (small, fast joints).
3. The `ON` marking on the silkscreen shows the actuator position for "on" (actuator towards the
   `ON` text). Leave it **off** for now.

Reset button EVQ-P7A01P (RB1, below the power switch near the inner corner):

4. Place it on its four pads; it is symmetric. Solder diagonally opposite pads first.

FPC connector FH12-6S-0.5SH (J1, right PCB only, between the index/middle bottom keys and the
thumb keys):

5. Open the flip lock. The connector goes on with the lock (cable entry) facing the ball pocket,
   i.e. towards the user; the six contacts point towards the keys. The silkscreen `1` marks pin 1.
6. Use the fine tip. Tin one anchor tab, place the connector, reflow the tab, check that all six
   leads sit exactly on their pads under magnification, solder the second tab, then drag-solder the
   six leads with flux. Remove any bridge with wick; check again with the loupe.
7. Multimeter: continuity from pin 1 to the controller hole for VCC, pin 2 to GND, and no short
   between neighbouring pins.

Test pads in a row at the bottom of the controller block carry D0, D1, D2, D3 and D9 on both halves
(plus D10, D14, D15 and D16 on the left, where the sensor pins have no connector); nothing to solder.

Checkpoint: switch clicks between two positions, button clicks, FPC lock opens and closes, no
shorts between FPC pins.

## 7. Battery

Both halves are identical here: one 702025 cell (300 mAh) lies on the **bottom face** in the
dashed battery bay printed right under the controller, lead end towards the JST connector J3, and
plugs into J3. The case provides a 9 mm deep well under the controller block for it. The solder
pads J2 remain for cells with bare leads.

![Battery in the bay under the controller](images/img-build-step-battery.png)

1. Power switch **off**. Controller removed.
2. Measure the cell: 3.6 to 4.2 V between its red (+) and black (-) lead. Note which lead is
   which; some cells have swapped colours on the connector.
3. JST connector J3 (default): solder the connector like the FPC connector (tabs first). Pin 1 (the
   pad marked `1`) is B+. Check the cell's plug polarity against that before plugging in; swap the
   pins in the plug housing if needed.
4. Solder pads J2 instead (bare leads): the **square** pad is B+, the round pad is B-. Trim the
   leads so the cell reaches the bay with 5 mm of slack, strip 2 mm, tin, solder red to the square
   pad, black to the round pad. Do not let the two bare leads touch each other while you work.
5. Multimeter: cell voltage between the controller's RAW hole and GND must be **0 V** with the
   switch off and the cell voltage with the switch on. If it is reversed in polarity, stop and fix
   it before the controller goes on.
6. Switch off again. Stick the 0.5 mm foam or Kapton pad onto the PCB inside the dashed bay (it
   covers the socket tails), then the cell onto the pad with double-sided tape, lead end towards
   J3. Nothing but the pad may lie between the cell and the PCB; the leads must not run under
   the cell.

Checkpoint: correct polarity at RAW/GND, switch really cuts the supply, cell fixed inside the bay
on both halves, leads not under strain.

## 8. Flash the firmware

Firmware files come from the GitHub Actions run or the local Docker build (see
[firmware](05-firmware.md), section 1). You need `settings_reset`, `k0d3ball35_left` and
`k0d3ball35_right` as UF2 files.

![Dragging the UF2 onto the controller drive](images/img-build-step-flash.png)

1. Plug the controller onto its sockets (USB at the top edge, chip up). Power switch off (USB
   powers the controller for flashing).
2. Connect USB-C to the computer. Double-tap the reset button within half a second: a drive
   named `NICENANO` appears.
3. Copy `settings_reset-nice_nano_v2-zmk.uf2` onto the drive. The drive disappears when done.
4. Double-tap reset again and copy `k0d3ball35_right-...uf2` (right half) or
   `k0d3ball35_left-...uf2` (left half).
5. Repeat for the other half. Both halves must get `settings_reset` first on a fresh build or
   whenever they stop talking to each other.
6. Unplug USB. Switch both halves on within a minute of each other; they pair automatically.

Checkpoint: both halves flashed, the right half shows up as a USB keyboard when connected.

## 9. Smoke test before closing

Do this with the controllers on, switches not yet installed.

![Matrix test with a wire bridging a socket](images/img-build-step-smoke-test.png)

1. Right half on USB, open a text editor. Short the two contacts of a socket with a piece of
   wire or a test switch: a character must appear. Try every position on both halves (the left
   half sends its keys through the right half over Bluetooth, so pair them first by switching both
   on).
2. A key that prints the wrong character: wrong socket position in the keymap, check in ZMK
   Studio. A key that prints nothing: diode direction (chapter 3) or a cold socket joint (chapter 4).
   A key that triggers two characters: a bridge between a diode pad and a socket pad.
3. Hold a key and press another in the same column, then in the same row: no ghost characters.
4. Battery check: with USB disconnected and the switch on, the half must keep working; with USB
   connected the controller's charge LED comes on for a cell below 4.2 V.
5. ZMK Studio (<https://zmk.studio>, right half on USB, press the Studio unlock key on the System
   layer) shows both halves' battery levels. Below 3.5 V means the cell was not charged.

Checkpoint: 35 positions register (18 left, 17 right), no ghosting, both halves run from battery,
both battery levels visible in Studio.

## 10. Sensor board and lens

Right half only. Details and the test table are in [trackball module](08-trackball-module.md).
The board has a BALL SIDE (lens) and a component side (passives, FPC connector).

![Inserting the sensor through the board and clipping the lens](images/img-build-step-sensor-lens.png)

1. Solder the SMD parts on the component side: XC6206 regulator, the 0603 capacitors and
   resistors, the FPC connector (same technique as chapter 6, step 6). Flip lock away from the
   board edge, cable enters from the edge.
2. Push the PMW3610 from the **ball side** through the rectangular cutout until it seats; the
   square pad marks pin 1. Solder the 16 leads on the component side, each joint under 3 seconds.
   Do not let flux reach the optical window.
3. Clean with isopropyl alcohol, let it dry.
4. Multimeter before power: VCC to GND more than 10 kOhm, 1V8 to GND no short.
5. Peel the two protective films off the sensor window. Clip the LM18-LSI lens onto the sensor
   body, holding it only by its flange. Never touch the optical surfaces; if you do, clean with a
   lens cloth, not a paper towel.
6. Power test through the FFC (chapter 11, step 3): 1V8 test pad reads 1.75 to 1.85 V, idle current
   below 1 mA.

Checkpoint: no shorts, 1.8 V present, lens clipped on straight with the aperture centred.

## 11. Trackball cradle

Print `cradle-19mm-pocket.stl` upright (housing down), 0.12 mm layers, 3 perimeters, 30 percent
infill, no supports, PETG or PLA. There is no retainer to print: the cup rim ends 1 mm below the
ball equator and the ball is held by gravity; the removable case lid (`issues/mech-case-lid.md`)
covers it for transport. Deburr the rim, it is the only printed edge near the ball. Full details
and the test-fit list are in the
[cradle README](../hardware/trackball-cradle/README.md). The module stands on the case floor in
the pocket beside the right PCB. Its 30 x 29 mm housing has no screw ears: the two case screws go
up through the floor and the sensor board into the cradle's sensor posts, 20 mm apart. Until the
case exists, a scrap of 2 mm material with two 2.2 mm holes 20 mm apart works as a test floor.

![Pressing the ceramic bearings into the cup](images/img-build-step-cradle.png)

1. Clean the three bearing seats inside the cup with a 1.9 to 2.0 mm bit. Press one 2.0 mm ZrO2
   ball into each seat from inside the cup with a toothpick until it bottoms out. Put a dot of
   cyanoacrylate at the rim of each seat (never under the ball). Let it cure 10 minutes.
2. Roll the trackball in the cup: it must spin without a click or scrape. A scraping ball means a
   bearing is not fully seated.
3. Plug the FFC into the sensor board connector **now**, contacts facing the connector's contacts
   (the exposed metal of the cable towards the PCB on a bottom-contact connector), stiffener up,
   close the flip lock. The connector is unreachable once the board is in the housing. The pin
   order between the two boards is intentionally mirrored, see
   [trackball module, section 2.2](08-trackball-module.md).
4. Slide the sensor board **lens first** into the housing from below, aperture in the 9 mm hole,
   cable out through the slot in the key-facing wall. For the bench test hold it with two M2 x 5
   self-tapping screws from below; they come out again in step 6. Tighten until snug, then stop:
   the plastic threads strip easily.
5. Lens distance check (ball out): a 2.0 mm feeler gauge laid on the lens aperture through the
   9 mm hole must be flush with the cup surface at the bottom. The ball rests 0.4 mm above the cup
   surface, which gives the 2.4 mm the datasheet asks for; 2.2 to 2.6 mm is acceptable. Too high
   or too low: check the lens is seated flat and the screws are not pulling the board askew.

![Checking the lens-to-ball distance with a feeler gauge](images/img-build-step-lens-gauge.png)

6. Stand the module in the case pocket (screw holes on the user-facing axis, cable slot towards
   the keys), take the short bench-test screws out and fasten it with two M2 x 10 self-tapping
   screws from underneath the case floor: each screw passes the 2 mm floor, the 2.25 mm gap and
   the sensor board and bites about 4 mm into the post (or M2 x 10 machine screws into heat-set
   inserts). Snug, not tight: the same screws clamp the board, it must not bow. The cup must sit
   centred in the PCB's octagonal notch with a visible gap all round.
7. Route the FFC under the PCB to connector J1 on the right PCB's bottom face, insert with the
   contacts towards the PCB, close the lock.
8. Right half on USB: the cursor must move when you roll a finger on the cup's bearings. Then
   drop the ball in. Nothing holds it: it must spin freely in every direction and a strip of
   paper must pass between the ball and the rim all the way round.
9. Lift the ball out with two fingers and put it back. For transport the case lid goes on
   (`issues/mech-case-lid.md`); until the case exists, carry the half without the ball.

![Trackball module mounted beside the right half](images/img-build-step-ball.png)

Checkpoint: ball spins freely, lens distance within 2.2 to 2.6 mm, cup clear of the notch, cursor
moves, ball retained.

## 12. Switches and keycaps

![Switches and keycaps going in](images/img-build-step-switches.png)

1. Check the two pins of each Choc V1 switch are straight. Bent pins will fold inside the socket
   and not contact.
2. Press each switch straight down into its socket from the top face, supporting the PCB from
   below with a finger right under the socket so the solder joints do not take the load. The
   centre post and the two side posts locate the switch; the pins engage with a soft click.
3. Thumb keys: the rotated positions take the switch in the same orientation as the silkscreen
   outline shows; the stem's flat side follows the rotation.
4. Keycaps: 1u Choc caps on all 35 positions; accent colour on the five thumb keys if you follow
   the reference build.
5. Press every key once in a text editor.

Checkpoint: 35 keys register, no switch sits high or tilted.

## 13. Pairing and trackball tuning

1. Both halves on. The halves find each other within seconds. Connect the right half to the host
   by USB or by Bluetooth: on the System layer (hold both outer thumb keys), select profile 0 with
   the top-left key and pair "k0d3ball35" from the host.
2. Cursor direction: roll the ball away from you, the cursor must move up. If an axis is reversed,
   set `invert-x` / `invert-y` in `k0d3ball35_right.overlay`; if the axes are swapped, add
   `&zip_xy_swap_mapper` (sensor board rotated 90 degrees). Rebuild and reflash the right half.
3. Speed: the default is 600 CPI. A half turn of the 19 mm ball should move the cursor about one
   screen width. Adjust `res-cpi` in steps of 200, or add a scaler in the input processors (see
   [firmware, section 6](05-firmware.md)).
4. Mouse layer: moving the ball activates layer 4 for 700 ms; the right-hand thumb and home-row
   keys become mouse buttons. Hold the scroll key to scroll, the snipe key for slow precision moves.
5. Save keymap changes in ZMK Studio if you prefer not to rebuild; Studio settings persist on the
   keyboard.

Checkpoint: cursor direction and speed feel right, clicks work on the mouse layer, both halves
reconnect after a power cycle.

## 14. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `NICENANO` drive never appears | reset button not reaching the controller's RST | reflow the button; double-tap faster; try the reset pads on the controller directly |
| one key dead | diode reversed or cold socket joint | diode mode test (chapter 3); reflow both socket pads |
| whole row or column dead | row/col hole on the controller not soldered, or a socket pad bridged to the diode | check continuity from the controller hole to the farthest socket in that line |
| two keys fire together | solder bridge between a socket pad and a diode or a neighbouring pad | wick the bridge, re-check under magnification |
| halves do not talk | pairing data stale | `settings_reset` on both, then the real firmware, power both on within a minute |
| half dies when USB is unplugged | battery not connected or reversed, slide switch not in the B+ line | chapter 7 step 5 |
| controller gets warm, battery reads reversed | cell polarity reversed | disconnect immediately, swap the leads, replace the controller if the charger IC died |
| cursor does not move | no 3.3 V on FPC pin 1, cable in backwards or not latched, lens films still on | check VCC at the sensor board, reseat the cable with contacts towards the connector, peel the films |
| cursor jitters at rest or tracks on one axis only | lens not seated, lens distance out of range, dirty ball | reseat the lens, feeler gauge check (chapter 11), clean the ball |
| cursor moves the wrong way | axis config | `invert-x` / `invert-y`, `&zip_xy_swap_mapper` |
| mouse layer opens while typing | timing | raise `require-prior-idle-ms`, check `excluded-positions` |
| short battery life on the right half | `force-awake` on, slide switch not in the battery line, sensor always tracking | disable `force-awake`, confirm 0 V at RAW with the switch off, make sure nothing (lid, pocket wall) presses the ball onto the bearings |
| ball falls out when the half is carried | by design, there is no retainer | put the case lid on for transport (`issues/mech-case-lid.md`) or carry the half without the ball; a bayonet ring is the fallback described in the cradle README |
| ball rubs on the PCB notch | cradle not centred in the pocket | loosen the two floor screws, centre the cup in the notch, retighten |
| switch will not go in | socket tilted, bent switch pin | reflow the socket flat, straighten the pin |

Measurements that settle most arguments: cell 3.6 to 4.2 V; RAW equals cell voltage with the
switch on, 0 V off; VCC 3.3 V with the controller running; sensor 1V8 pad 1.75 to 1.85 V; diode
forward 0.5 to 0.7 V.

## 15. Maintenance

* **Ball.** Lift the ball out (nothing holds it), wipe it with a lint-free cloth and a little
  isopropyl alcohol, brush the three bearings with a dry brush. Every few weeks, more with dry skin.
  POM balls pick up skin oil faster than phenolic ones.
* **Bearings.** If the ball starts scraping, a bearing has shifted. Reseat it and re-glue at the
  seat rim. Keep three spares.
* **Lens.** Blow dust off with a bulb blower only. Never spray cleaner into the cup.
* **Battery.** Charge through USB; the controller's LED goes out when full. Do not store the
  keyboard fully discharged for months; the protection circuit cuts at about 3.0 V and the cell
  then needs a USB charge before the half switches on again. Replace a cell that swells.
* **Bumpers.** Stick the anti-slip pads on the case underside at the four corners of each half.
* **Firmware.** Before updating to a newer ZMK revision, read the release notes; if the split
  protocol changed, flash `settings_reset` on both halves and pair again.

## 16. Printable checklist

```
k0d3ball35 build checklist                       half: [ ] right (17 keys)  [ ] left (18 keys)

[ ] 1  parts complete, tools ready, cell measured 3.6-4.2 V
[ ] 2  PCB identified: "<SIDE> half" silkscreen readable from above
[ ] 3  diodes (18 L / 17 R), bands at the silkscreen bar, 0.5-0.7 V forward each
[ ] 4  sockets (18 L / 17 R) flat on the bottom face, test switch fits everywhere
[ ] 5  controller sockets soldered, pins on the controller, USB at the top edge
[ ] 6  power switch (actuator to the inner edge), reset button, FPC connector (right only)
[ ] 7  battery: J3 pin 1 = B+ (square pad on J2), 0 V at RAW with switch off, cell on its pad in the bay
[ ] 8  settings_reset flashed, then left / right firmware
[ ] 9  35 positions register, no ghosting, battery level visible in Studio
[ ] 10 sensor board: no shorts, 1.8 V present, lens clipped on
[ ] 11 cradle: bearings glued, FFC plugged before the board goes in, lens gauge 2.2-2.6 mm,
       module screwed to the floor, cup centred in the notch, ball retained
[ ] 12 switches and keycaps in, every key tested
[ ] 13 cursor direction and speed set, halves reconnect after power cycle
[ ] 15 bumpers on, ball cleaning routine noted
```
