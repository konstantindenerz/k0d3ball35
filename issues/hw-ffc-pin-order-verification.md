---
title: Verify the 6-pin FFC pin order between main PCB and sensor PCB
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Verify the 6-pin FFC pin order between main PCB and sensor PCB

## Context

Both FPC connectors are bottom-contact parts, but since r2.2 they look at the cable from opposite
faces: J1 sits on the key side of the right PCB with the cable on top of the board, the sensor
connector hangs under the sensor board. The cable must therefore be a **type B** FFC (contacts on
opposite faces at its two ends) and the pin order runs straight through, 1 to 1. The main PCB
order is fixed in the design spec (3V3, GND, SCLK, SDIO, NCS, MOT); the sensor PCB matches it.
A wrong cable type connects nothing at one end, a wrong order would swap 3V3 and MOT.

## Acceptance criteria

- [x] Pin order on both boards drawn in one diagram with the cable in between, in `docs/08-trackball-module.md`
- [ ] Physical check with a cable and two connectors on breakout boards, or a continuity test on the first PCBs before the sensor is connected
- [x] `tests/test_ffc_pin_order.py` cross-checks main PCB connector nets against the sensor PCB connector nets
  (reads the pads of both boards, models the type B cable, pairs the pads and compares the nets)
- [ ] The first cable must be type B: check the two ends against the light before plugging anything in

## Notes

torabo-tsuki-lp uses a 6-pin FFC between main board and sensor module; its schematics are a cross-check.

Both boards use the same footprint, Hirose FH12-6S-0.5SH (0.5 mm, 6 contacts, bottom contact, ZIF slider),
copied into `hardware/lib/k0d3ball35.pretty`. Main PCB pin order (fixed): 1 VCC 3.3 V, 2 GND, 3 TB_SCLK,
4 TB_SDIO, 5 TB_NCS, 6 TB_MOT. The sensor PCB adapts its order to the cable.

Resolved on paper (2026-11-05): the sensor-board order is mirrored, 1 MOT, 2 NCS, 3 SDIO, 4 SCLK, 5 GND, 6 VCC, because
both connectors are bottom contact on the component sides and a type A cable reverses the order. R3 (1 k in
series with MOTION) and R2 (NCS pull-up) keep a wrongly inserted cable non-destructive. Still to do: the physical
check with the first cable and connectors before ordering main PCBs in quantity.

### Desk check 2026-11-06 (r2, superseded by r2.2 below)

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

Mounting in the pocket (docs/08 sections 2.2 and 3.2) in one world frame, X/Y = right PCB board axes, Z up:

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
`FPC_0.5mm_6P_FH12-6S_top`, placed on F.Cu at (117.4, 105.5) in the board frame, rotation 0, pad
set on F.Cu and **not** mirrored, so pad 1 is at -x (board x 116.15) and the cable mouth faces +y,
towards the notch. The sensor board is unchanged.

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
