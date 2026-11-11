---
title: Verify the 6-pin FFC pin order between main PCB and sensor PCB
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Verify the 6-pin FFC pin order between main PCB and sensor module

## Context

Both FPC connectors are bottom-contact parts, but since r2.2 they look at the cable from opposite
faces: J1 sits on the key side of the right PCB with the cable on top of the board, the sensor
connector sits on the back of the sensor. The cable must therefore be a **type B** FFC (contacts
on opposite faces at its two ends) and the pin order runs straight through, 1 to 1. Since r2.4 the
far end is the bought PAW3222 module, whose pinout is the vendor's, so J1 follows it instead of
the other way round. A wrong cable type connects nothing at one end; a wrong order now shorts 3V3
to GND, because the module puts those two on the outer pins.

## Acceptance criteria

- [x] Pin order on both boards drawn in one diagram with the cable in between, in `spec/08-trackball-module.md`
- [ ] Physical check with a cable and two connectors on breakout boards, or a continuity test on the first PCBs before the sensor is connected
- [x] `tests/test_ffc_pin_order.py` checks J1 against the module's declared pinout (derives the
  type B pairing from the two mounting faces, cross-checks the sign against torabo-tsuki LP's
  published type A wiring of the same module, compares J1's copper with the generator model)
- [ ] `make pcb` / `make route` re-run on the right board after the r2.4 pin reorder, so the
  copper carries the new nets (`tests/test_ffc_pin_order.py::test_right_j1_copper_matches_the_model`
  and `tests/test_pcb_review.py` fail until then)
- [ ] The first cable must be type B: check the two ends against the light before plugging anything in

## Notes

torabo-tsuki-lp uses a 6-pin FFC between main board and sensor module; its schematics are a cross-check.

Both boards use the same connector, Hirose FH12-6S-0.5SH (0.5 mm, 6 contacts, bottom contact, ZIF slider),
in two single-face footprint variants. Main PCB pin order (fixed): 1 VCC 3.3 V, 2 GND, 3 TB_SCLK,
4 TB_SDIO, 5 TB_NCS, 6 TB_MOT.

**Current answer (r2.4, see the desk check at the bottom): the cable is type B and the pin order is
straight through, 1 to 1, and J1 now carries the module's own order:
1 VCC, 2 TB_NCS, 3 TB_MOT, 4 TB_SDIO, 5 TB_SCLK, 6 GND.** R3 and R2 went with the sensor
daughterboard, so a mis-made cable is no longer current-limited by anything of ours. Still to do:
the physical check with the first cable and connectors before ordering main PCBs in quantity.

An earlier paragraph here said the sensor order was mirrored (1 MOT ... 6 VCC) for a **type A** cable. That
was the r2 answer and it was removed on 2026-11-07, because it was not merely superseded: it described a
board that does not exist. `hardware/sensor-pcb/k0d3ball35-sensor.kicad_pcb` has had the straight order
since r2.2, and reading the mirrored one top-down leads to ordering the wrong cable -- whose failure mode,
nothing connecting at one end, looks exactly like a dead sensor.

### Desk check 2026-11-06 (r2) -- SUPERSEDED, DO NOT ACT ON THIS SECTION

> Kept for the reasoning only. It concludes that a **type A** cable and a mirrored sensor-side pin order
> are correct. Both were true while J1 sat on the **back** of the right PCB; since r2.2 J1 is on the key
> side (`hw-j1-top-side`) and the current answer is **type B, straight through**. The live answer is in
> "Desk check 2026-11-06, r2.2 (current)" further down and in the Notes above.

Pads read from `hardware/right-pcb/k0d3ball35-right.kicad_pcb` and `hardware/sensor-pcb/k0d3ball35-sensor.kicad_pcb`
(board frames, KiCad y points down, i.e. towards the user on the right PCB):

| | Right PCB J1 | Sensor PCB J1 |
|---|---|---|
| Footprint | `FPC_0.5mm_6P_FH12-6S_bottom`, placed on F.Cu at (120.0, 105.5), rot 0, pad set on B.Cu | `FPC_0.5mm_6P_FH12-6S`, placed on F.Cu at (117.6, 102.45), rot 180, pad set on F.Cu |
| Face of the part | bottom face (key side is the top) | component side (top of the board file) |
| Contact row | y = 103.65, pads 1..6 at x = 121.25, 120.75, ... 118.75 | y = 104.3, pads 1..6 at x = 118.85, 118.35, ... 116.35 |
| Metal-fitting pads | y = 106.9 | y = 101.05 |
| Cable entry (fittings side) | +y, towards the user and the pocket | -y, the edge that faces the keys in the pocket |
| Pad 1 in the board frame | +x side | +x side |
| Nets 1..6 | VCC, GND, TB_SCLK, TB_SDIO, TB_NCS, TB_MOT | MOT_J, NCS, SDIO, SCLK, GND, VCC |

Mounting in the pocket (spec/08 sections 2.2 and 3.2) in one world frame, X/Y = right PCB board axes, Z up:

| | Right PCB | Sensor PCB |
|---|---|---|
| Board orientation | key side up, not turned over | turned over, component side on the case floor |
| Connector contacts | between cable and PCB, so the cable's contact face points up | between cable and PCB, so the cable's contact face points up |
| Board x to world X | X = x | X = -x (turned over about the cable axis Y so that its cable edge faces J1) |
| Pad i world offset from the connector centre | +1.25 - 0.5 (i - 1), pad 1 at +1.25 | -1.25 + 0.5 (i - 1), pad 1 at -1.25 |

Both contact faces point up, so the straight cable needs no twist and a type A (same-side) FFC is the right cable.
A conductor keeps its lateral offset along the cable, so right pad i meets sensor pad j with
1.25 - 0.5 (i - 1) = -1.25 + 0.5 (j - 1), i.e. i + j = 7:

| Right J1 pin | Right net | Sensor J1 pin | Sensor net | Match |
|---|---|---|---|---|
| 1 | VCC | 6 | VCC | yes |
| 2 | GND | 5 | GND | yes |
| 3 | TB_SCLK | 4 | SCLK | yes |
| 4 | TB_SDIO | 3 | SDIO | yes |
| 5 | TB_NCS | 2 | NCS | yes |
| 6 | TB_MOT | 1 | MOT_J (R3 1 k to MOTION) | yes |

Conclusion: the boards are consistent with each other; the mirrored sensor-side order is correct for a type A cable in
the pocket mount. VCC and MOT sit at opposite cable edges on both boards, so a cable inserted the wrong way round
puts VCC on R3/MOT_J and MOT on VCC, both limited by R3 and R2 as intended.

Footprint versus datasheet: the Hirose FH12 catalog (2019 edition, pages 4 and 10) gives land dimensions for the
0.5 mm bottom-contact type but does not print contact numbers on the horizontal drawing; it only shows the
"polarizing mark indicator" at one end of the body (the end opposite the "number of contacts indicator"), at the
left end when the part is viewed from above with the leads at the rear. The KiCad library footprint
`Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal` numbers that end as pad 1 (pad 1 at x = -1.25, contact row at
y = -1.85, metal fittings at x = +-3.15, y = +1.4, cable entry towards +y); the project footprint
`FPC_0.5mm_6P_FH12-6S` is pad for pad identical, and the `_bottom` variant is its x-mirror on B.Cu with the "1"
mark moved along, which is exactly what KiCad's own flip produces. The cross-connection result does not depend on
which end Hirose calls contact 1: both boards use the same pad geometry, so a relabelling would renumber both ends
together and the net pairing above would be unchanged.

### Desk check 2026-11-06, r2.2 (current)

J1 moved to the key side of the right PCB (`hw-j1-top-side`): footprint
`FPC_0.5mm_6P_FH12-6S_top`, placed on F.Cu at (99.4, 107.4) in the board frame, rotation 0, pad
set on F.Cu and **not** mirrored, so pad 1 is at -x (board x 98.15) and the cable mouth faces +y,
towards the notch. (Layout frame (-20.6, +47.4); the connector moved with the ball in r2.3.) The sensor
board is unchanged: 1 VCC, 2 GND, 3 SCLK, 4 SDIO, 5 NCS, 6 MOT_J.

| | Right PCB J1 | Sensor PCB J1 |
|---|---|---|
| Face of the part | key side (top) | component side, facing the case floor |
| Cable contact face there | down, towards the PCB | up, towards the PCB |
| Pad 1 offset from the connector centre | -1.25 mm | +1.25 mm in its own frame |
| Board x to world X | X = x | X = -x (board turned over) |
| Pad 1 in world X | -1.25 mm | -1.25 mm |

The two contact faces are opposite, so the cable needs its contact windows on opposite faces:
type B. No twist and no fold back on itself, so each conductor keeps its lateral offset and
right pad i meets sensor pad i:

| Right J1 pin | Right net | Sensor J1 pin | Sensor net | Match |
|---|---|---|---|---|
| 1 | VCC | 1 | VCC | yes |
| 2 | GND | 2 | GND | yes |
| 3 | TB_SCLK | 3 | SCLK | yes |
| 4 | TB_SDIO | 4 | SDIO | yes |
| 5 | TB_NCS | 5 | NCS | yes |
| 6 | TB_MOT | 6 | MOT_J (R3 1 k to MOTION) | yes |

A type A cable, a cable swapped end for end or one put in upside down all present insulation to
the contacts at one end: nothing connects, nothing is powered the wrong way round. VCC and MOT
still sit at opposite cable edges on both boards, so even a mis-made cable stays non-destructive
thanks to R3 and R2.

### Bench procedure (open item)

1. Solder J1 on one right PCB and J1 on one sensor PCB; do not fit U1 (PMW3610) or the regulator U2 yet, or lift them if already fitted.
2. Plug a 0.5 mm, 6-way, **type B** FFC (contacts on opposite faces at its two ends) into both connectors exactly as in the pocket: on the right PCB the cable lies on the key side with its contacts down, on the sensor board it runs under the board with its contacts up, no twist.
3. Set the multimeter to continuity and probe TP1 (VCC) on the sensor board against the right PCB's VCC net (controller 3V3 socket pin or the J1 pad 1 fillet); expect a beep.
4. Repeat for GND (there is no GND test point: probe a metal-fitting pad of the sensor J1, which is on GND, against the right PCB GND), then TP3 SCLK, TP4 SDIO, TP5 NCS and TP6 MOT against the controller holes D15, D16, D10 and D14 of the right PCB; each must beep only against its own net and stay open against the other five. With a type B cable the pairing is pin for pin, so pad 1 meets pad 1.
5. If any pair is swapped, stop and open a defect ticket before fitting the sensor; only after six clean passes fit U1 and U2 and power the board.

### Desk check 2026-11-11, r2.4 (current)

The sensor daughterboard is gone (`hw-paw3222-variant`): r2.4 buys the 14 x 8 mm PixArt PAW3222
module (sekigon-gonnoc / nogikes-ya, as in torabo-tsuki LP) and tilts it beside the ball, so
`hardware/sensor-pcb/` and `tests/test_sensor_pcb_vs_cradle.py` were deleted. There is no second
`.kicad_pcb` to read the far end from, so the module's pinout is a declared constant in
`tests/test_ffc_pin_order.py` and the pairing is derived instead of measured.

Module pinout (vendor's, the same one `spec/08-trackball-module.md` section 2.2 already quoted as
torabo-tsuki's module side): **1 3.3V, 2 CS, 3 MOTION, 4 SDIO, 5 SCLK, 6 GND**.

Faces are unchanged from r2.2 on our side and equivalent on the module side: J1 is on the key side
with the cable on top of the board, so its contact window points DOWN; the module's connector is on
its back face, away from the ball, so the cable lies against that face and its contact window points
UP and inwards. Opposite faces, so the cable stays **type B**.

Why type B pairs pin i with pin i, without needing either board's coordinates. For one cable end
write `m` for the direction the cable leaves the mouth and `c` for the normal from the contacts
towards the cable; the direction from pin 1 to pin 6 has a fixed handedness for a given connector
family, `p = m x c`. In the cable's own frame (`u` from the keyboard end to the module end, `n`
normal to the cable):

| | keyboard end | module end |
|---|---|---|
| cable leaves the mouth along | `m = +u` | `m = -u` |
| its board lies on the | `-n` side | `+n` side (type B: the other face) |
| contacts point at the cable along | `c = +n` | `c = -n` |
| pin 1 -> pin 6 runs along | `p = u x n` | `p = (-u) x (-n) = u x n` |

Both ends number their pins in the same lateral direction, and an untwisted cable keeps every
conductor on its own side, so pin i meets pin i. A type A cable would keep `c = +n` at the module
end, flip `p` and reverse the mapping to `i + j = 7` -- which is exactly how torabo-tsuki LP, with
both connectors under its boards and a type A cable, ends up wiring its keyboard side as
1 GND, 2 SCLK, 3 SDIO, 4 MOTION, 5 CS, 6 3.3V against this same module. That published pair is the
independent check on the sign and the test asserts it.

J1 therefore becomes the module's order in our net names. The main PCBs were not ordered yet, so
this cost a pad relabelling in `scripts/k0d3/netlist.py` and nothing else:

| J1 pin | J1 net (r2.3) | J1 net (r2.4) | Module pin | Module signal |
|---|---|---|---|---|
| 1 | VCC | VCC | 1 | 3.3V |
| 2 | GND | TB_NCS | 2 | CS |
| 3 | TB_SCLK | TB_MOT | 3 | MOTION |
| 4 | TB_SDIO | TB_SDIO | 4 | SDIO |
| 5 | TB_NCS | TB_SCLK | 5 | SCLK |
| 6 | TB_MOT | GND | 6 | GND |

What got worse, and it is worth saying out loud. Until r2.3 VCC faced MOT across the cable and a
laterally reversed cable was current-limited by R3 (1 k in series with MOTION) on our own sensor
board. The module's fixed order puts 3.3V on pin 1 and GND on pin 6, so the two supply pins now sit
at opposite cable edges, and R3 went with the board. The common mistakes are still harmless, because
a type A cable, a cable swapped end for end and a cable inserted upside down all present insulation
to the contacts at one end and connect nothing. But a cable whose contact window is on the wrong
face at one end would short 3.3V to GND. Hence: continuity test before power, every time, and the
palindromic-pinout idea stays parked in `spec/08-trackball-module.md` section 6.

Open assumption. `p = m x c` needs the same sign at both ends, i.e. the module has to call the same
end of its contact row "1" as the Hirose part does. Two identical footprints made that free in
r2.2; a bought module does not. This is the one thing in the chain that no file in this repository
can settle, and it is a continuity test on the first physical cable.
