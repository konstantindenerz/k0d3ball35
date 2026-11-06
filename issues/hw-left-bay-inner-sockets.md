---
title: Left board: inner column hot-swap sockets reach into the battery bay
type: bug
priority: P1
status: open
area: hw
created: 2026-11-06
---

# Left board: inner column hot-swap sockets reach into the battery bay

## Context

Found while mirroring the left PCB (`hw-left-pcb-mirror`). The Choc hot-swap socket footprint is
chiral: the socket body spans local x -4.8 to +10.2 and pad 2 sits at +8.5. The key positions are
mirrored on the left board, the footprint is not, so the sockets of the inner column (SW04, SW14,
SW24) point towards the controller there. The battery bay rectangle (frame x -64.4 to -43.4, board
x 163.4 to 184.4 on the left page) therefore contains 2.8 mm of the socket body and 2.4 mm of pad 2
of these three switches (DRC reports the dashed bay outline on B.SilkS over the pads). On the right
board the same sockets point away from the bay and nothing but the U1 socket tails lies inside it.

The cell lies 9.0 mm below the PCB underside (tails 1.0 + pad 0.5 + cell up to 7.2 + 0.3); a socket
is about 1.8 mm tall, so the specified LP552035 (5.7 mm) still has about 0.7 mm of air under the
sockets, but the 7.2 mm maximum cell of the spec does not fit any more.

Shifting the bay by 3 mm towards the inner edge collides with the power switch (PS1 at frame x
-68.5, y 30 lies in the bay's y range), so this needs a layout decision:

- move PS1 (and possibly RB1) up or down so the left bay can move 3 mm inboard, or
- shrink the maximum cell height in the spec to 6 mm for the left half, or
- deepen the well locally under the inner column on the left case.

`tests/test_pcb_review.py::test_battery_bay_holds_nothing_but_u1` bounds the intrusion to 2.85 mm
on the left (`LEFT_BAY_SOCKET_INTRUSION`) and `SILK_OVER_COPPER_ACCEPTED` lists the three pads
until this is resolved.

## Acceptance criteria

- [ ] Decision taken and recorded in docs/01-design-spec.md (battery section)
- [ ] Left board regenerated if the layout changes, DRC clean, gerbers refreshed
- [ ] `LEFT_BAY_SOCKET_INTRUSION` and the silk acceptance entry removed from the review test
