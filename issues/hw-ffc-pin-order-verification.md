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

Both FPC connectors are bottom-contact and sit on the top side of their boards. With a same-side
(type A) 0.5 mm cable the pin order either maps 1 to 1 or mirrored depending on how the two connectors
face each other. The main PCB pin order is fixed in the design spec (3V3, GND, SCLK, SDIO, NCS, MOT).
The sensor PCB chooses its order to match. A mistake here swaps 3V3 and MOT and may kill the sensor.

## Acceptance criteria

- [x] Pin order on both boards drawn in one diagram with the cable in between, in `docs/08-trackball-module.md`
- [ ] Physical check with a cable and two connectors on breakout boards, or a continuity test on the first PCBs before the sensor is connected
- [x] `tests/test_ffc_pin_order.py` cross-checks main PCB connector nets against the sensor PCB connector nets
  (reads the pads of both boards, models the type A cable, pairs the pads and compares the nets)

## Notes

torabo-tsuki-lp uses a 6-pin FFC between main board and sensor module; its schematics are a cross-check.

Both boards use the same footprint, Hirose FH12-6S-0.5SH (0.5 mm, 6 contacts, bottom contact, ZIF slider),
copied into `hardware/lib/k0d3ball35.pretty`. Main PCB pin order (fixed): 1 VCC 3.3 V, 2 GND, 3 TB_SCLK,
4 TB_SDIO, 5 TB_NCS, 6 TB_MOT. The sensor PCB adapts its order to the cable.

Resolved on paper (2026-11-05): the sensor-board order is mirrored, 1 MOT, 2 NCS, 3 SDIO, 4 SCLK, 5 GND, 6 VCC, because
both connectors are bottom contact on the component sides and a type A cable reverses the order. R3 (1 k in
series with MOTION) and R2 (NCS pull-up) keep a wrongly inserted cable non-destructive. Still to do: the physical
check with the first cable and connectors before ordering main PCBs in quantity.

### Desk check 2026-11-06

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

### Bench procedure (open item)

1. Solder J1 on one right PCB and J1 on one sensor PCB; do not fit U1 (PMW3610) or the regulator U2 yet, or lift them if already fitted.
2. Plug a 0.5 mm, 6-way, type A FFC (contacts on the same face at both ends) into both connectors exactly as in the pocket: contact face towards each PCB, no twist, sensor board component side down with its cable edge towards the right PCB.
3. Set the multimeter to continuity and probe TP1 (VCC) on the sensor board against the right PCB's VCC net (controller 3V3 socket pin or the J1 pad 1 fillet); expect a beep.
4. Repeat for GND (there is no GND test point: probe a metal-fitting pad of the sensor J1, which is on GND, against the right PCB GND), then TP3 SCLK, TP4 SDIO, TP5 NCS and TP6 MOT against the controller holes D15, D16, D10 and D14 of the right PCB; each must beep only against its own net and stay open against the other five.
5. If any pair is swapped, stop and open a defect ticket before fitting the sensor; only after six clean passes fit U1 and U2 and power the board.
