---
title: Confirm the PMW3610 VCSEL and laser pins against the datasheet
type: question
priority: P0
status: open
area: hw
created: 2026-11-07
---

# Confirm the PMW3610 VCSEL and laser pins against the datasheet

## Context

`hardware/sensor-pcb/generate.py` wires the four laser-related pins of the PMW3610DM-SUDU like this:

| Pin | Schematic name | Net | External components on that net |
|-----|----------------|-----|---------------------------------|
| 1 | `+VCSEL` | `VCSEL_P` | C7, 10 nF to GND |
| 10 | `PASS_T` | `VCSEL_P` | none; tied to pin 1 |
| 15 | `XYLASER` | `VCSEL_N` | none |
| 16 | `-VCSEL` | `VCSEL_N` | none; tied to pin 15 only |

So `VCSEL_N` is a two-pad net (U1.15 to U1.16) carrying exactly one track segment, with no connection to
GND, to a current-setting resistor, or to anything else. `PASS_T` is shorted to `+VCSEL`.

Three things make this worth checking before the boards are ordered:

- ERC cannot catch it. A two-pad net counts as connected, so `kicad-cli sch erc` reports zero violations
  and `--schematic-parity` is satisfied. The gate is blind to it by construction.
- There is no second source of truth anywhere in the repo. `spec/08-trackball-module.md` section 2 lists a
  component for every other pin of the part and lists nothing for `VCSEL_N`, so the intended topology was
  never written down and cannot be recovered from the design.
- Nothing on the sensor board is covered by an electrical test. `tests/test_sensor_pcb_vs_cradle.py` checks
  geometry and component heights only. No test asserts the decoupling set, the 1.8 V rail, R1's NRESET
  pull-up, or the values of R2 and R3 -- even though `tests/test_ffc_pin_order.py` and three tickets rest
  on the claim that "R3 (1 k) and R2 keep a wrongly inserted cable non-destructive". That claim is asserted
  in prose and nowhere else.

If the laser pins are wrong the sensor does not track, and the fix is a board spin. Checking costs about
fifteen minutes with the datasheet.

## Acceptance criteria

- [ ] Pins 1, 10, 15 and 16 compared one by one against the PMS0039 application circuit and the result
      written into `spec/08-trackball-module.md` section 2, including what each pin is *supposed* to
      connect to, so the next reader does not have to re-derive it
- [ ] If a current-setting resistor or a GND reference on the cathode side is required, it is added to
      `PARTS` in `hardware/sensor-pcb/generate.py` and to the BOM before the order
- [ ] A test in `tests/` pins the agreed topology of `VCSEL_P` and `VCSEL_N` so a future edit is deliberate
- [ ] `issues/hw-jlcpcb-order-r1.md` references this ticket as a blocker for the sensor board

## Notes

Found during the r2.3 design review (2026-11-07). The rest of the sensor board's passive set looks right
for the part: C5 100 nF at VDDIO pin 6, C1 1 uF at the LDO input, C2 + C3 + C4 = 4.4 uF on the 1.8 V rail,
C6 100 nF across the charge pump at CP/CN, C8 + C9 on VCP, R1 and R2 as 10 k pull-ups on NRESET and NCS.
Only the laser pins are unexplained.
