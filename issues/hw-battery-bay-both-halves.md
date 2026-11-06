---
title: Battery bay under the controller on both halves, controller on low-profile sockets
type: feature
priority: P1
status: done
area: hw
created: 2026-11-06
---

# Battery bay under the controller on both halves, controller on low-profile sockets

## Context

Until now the two halves mounted their cells differently: the left half carried a 301230 (110 mAh,
3.3 mm) between the PCB and the controller, which forced 3.5 to 4.2 mm sockets and a raised
controller box, while the right half's 702025 (300 mAh, 7 mm) was described as lying "in the case
pocket next to the controller" without any geometry behind it. Two concepts meant two case designs,
two battery parts and a taller controller stack on the left for no reason.

Decision (2026-11-06): one concept for both halves. The cell lies **under the PCB**, directly below
the controller, in a well of the case floor. The back of the PCB carries nothing there except the
socket tails, so the "battery bay" is the same rectangle on both boards. With nothing between the
controller and the PCB any more, both controllers sit on the lowest sockets available.

Numbers (layout frame, z = 0 PCB top; `battery` block in `hardware/layout/k0d3ball35.yaml` and
`points-left.json` / `points-right.json`):

| Item | Value |
|------|-------|
| Cell | PKCELL LP552035, 350 mAh, 5.7 x 20 x 37 mm max. incl. PCM, JST-PH plug, one per half (r2.1b; the first draft used a 702025) |
| Bay (back of the PCB) | centre (-53.9, +17.5), 21 x 41 mm: x -64.4 to -43.4, y -3 to +38, lead end towards +y (r2.1b; was 21 x 28 under the controller centre) |
| Clearances | 1.75 mm to the inner and top PCB edges, 0.8 mm to the PS1 courtyard, no other back-side part within 3 mm (checked by `check_layout`) |
| Well | 9.0 mm below the PCB underside (tails 1.0 + pad 0.5 + cell 7.2 + 0.3), floor at -10.6 mm; the case may use the pocket level -11.6 mm instead |
| J3 | (-56, +44) and RB1 (-66, +41), below the bay in the same well; J3 is the default connection on both halves |
| Sockets | Mill-Max 315 with 3320 pins or conthrough, 2.5 mm design value (was 3.5 to 4.2 mm) |
| Controller top | +5.7 mm (2.5 + 1.6 nice!nano PCB + 1.6 USB-C shell above it), was about +8.4 mm; keycap tops are at about +11 mm, so a raised controller box is optional |
| Alternatives | 602025 / 502025 / 402025 fit the same bay; the 301230 (32 mm long) does not |

Research behind the numbers: Mill-Max 315 "LoPro" 2.1 to 2.8 mm above the board depending on the
source, 310 "HiPro" 4.19 mm; conthrough 2.5 mm; nice!nano v2 PCB 1.6 mm with a mid-mount USB-C
(3.2 mm overall) and no parts on the underside; S2B-PH-SM4-TB 5.5 mm tall.

## Acceptance criteria

- [x] `battery` block in the layout yaml (cell, size, bay, depth, edge clearance, lead direction); `controller.socket_height`
- [x] `Layout.battery_bay()` and `Layout.back_parts()`; `check_layout` refuses a bay outside the outline, too close to the edge, smaller than the cell or touching a back-side part; bay exported to `points-*.json` (`battery`, `bay_polygon`, `well_floor_z`), drawn in the previews and on the `BATTERY_BAY` layer of the outline DXFs
- [x] Dashed bay outline and label on the back silkscreen of both PCBs; both boards re-routed, ERC and DRC clean with schematic parity, gerbers, renders, STEP, BOM and position files re-exported
- [x] Exploded view: same battery layer on both halves (cell in the bay under the PCB), controller on 2.5 mm sockets, dims table with battery and well floor
- [x] Docs: design spec section 4 and 5, layout, BOM (2 x 702025, J3 default, 315 sockets + 3320 pins), build guide chapters 5 and 7, feasibility, firmware battery table, roadmap, lessons, README, image prompts
- [x] Tickets: `hw-battery-under-controller-fit` wontfix, `hw-jst-connector-height` done, `mech-case`, `mech-case-lid`, `doc-exploded-view-3d`, `hw-main-pcb-review-r1` updated
- [x] Tests: bay identical on both halves, clear of back-side parts, in the points JSON, bay marker in both PCBs, BOM lists two 702025 and no 301230 default

## Notes

r2.1b (2026-11-06): no German or EU shop outside Amazon stocks a 20 x 25 mm cell with 250 to
300 mAh and a JST-PH plug, and Mouser does not ship lithium cells to Germany. The bay was moved
4 mm outward (its left edge now runs between the two controller hole rows, 0.37 mm from the left
pads) and lengthened to 41 mm; the reset button moved from y 38 to 41 and the JST from y 42 to
44 to make room. That fits the PKCELL LP552035 (350 mAh, Eckstein, in stock) with 3.5 mm length
margin and still takes every 20 x 25 and 20 x 30 cell. The outline, the controller position and
the well depth did not change; both boards were re-routed, DRC clean.
