# Project libraries

Footprints (`k0d3ball35.pretty/`) are shared by every KiCad project in this repository; both
project folders reference them through their local `fp-lib-table` with
`${KIPRJMOD}/../lib/k0d3ball35.pretty`, so the repository is self-contained and needs no global
library configuration. The symbols the two main PCBs use live in `k0d3ball35-main.kicad_sym`,
which `scripts/gen_schematic.py` writes and the project `sym-lib-table` files point at.

`k0d3ball35.kicad_sym` is the older hand-drawn symbol library. It belonged to the PMW3610 sensor
daughterboard, which r2.4 dropped in favour of a bought PAW3222 module
(`issues/hw-paw3222-variant.md`), so no project references it any more; its remaining symbols are
kept for reference until the follow-up decides whether to delete the file.

| Item | Origin | Notes |
|------|--------|-------|
| `FPC_0.5mm_6P_FH12-6S` | KiCad official library `Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal` | renamed copy; the `_top` and `_bottom` variants are the single-face versions, the right PCB uses `_top` for J1 on the key side |
| `C_0603`, `R_0603`, `TestPoint_D1.0mm` | KiCad official footprint libraries | renamed copies; only the retired sensor daughterboard used them, so no board references them now |
| `MountingHole_M2` | this project | 2.2 mm plain hole, 2.0 mm courtyard radius |
| `FPC_6P`, `C`, `R`, `TestPoint`, `MountingHole`, power symbols in `k0d3ball35.kicad_sym` | this project | drawn by hand for the retired sensor daughterboard project |

Footprints copied from the KiCad libraries are licensed under CC-BY-SA 4.0 with the KiCad library
exception (https://www.kicad.org/libraries/license/). Everything authored here is CERN-OHL-P-2.0.

Do not edit generated files by hand; change the generator and re-run it. `k0d3ball35-main.kicad_sym`
is written by `scripts/gen_schematic.py`; the pad geometry of the main-PCB footprints is described
in `scripts/k0d3/footprints.py`, which `scripts/gen_pcb.py` places on the boards.
