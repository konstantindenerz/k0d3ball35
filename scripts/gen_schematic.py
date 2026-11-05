#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the main PCB schematic (hardware/main-pcb/k0d3ball36.kicad_sch) and project file."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from k0d3.geometry import REPO, load_layout  # noqa: E402
from k0d3.netlist import build_components  # noqa: E402
from k0d3.pcb import project_json  # noqa: E402
from k0d3.schematic import build_schematic, symbols  # noqa: E402

OUT = REPO / "hardware" / "main-pcb"


def main() -> int:
    layout = load_layout()
    comps = build_components(layout)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "k0d3ball36.kicad_sch").write_text(build_schematic(comps, "k0d3ball36 main PCB", layout.cfg["revision"]))
    (OUT / "k0d3ball36.kicad_pro").write_text(project_json("k0d3ball36", comps))
    lib = REPO / "hardware" / "lib" / "k0d3ball36-main.kicad_sym"
    lib.write_text("(kicad_symbol_lib (version 20231120) (generator \"k0d3ball36\") (generator_version \"1.0\")\n"
                   + "\n".join(sym.sexpr().replace(f'(symbol "k0d3ball36:{sym.name}"', f'(symbol "{sym.name}"', 1) for sym in symbols().values()) + "\n)\n")
    (OUT / "sym-lib-table").write_text('(sym_lib_table\n  (version 7)\n  (lib (name "k0d3ball36")(type "KiCad")(uri "${KIPRJMOD}/../lib/k0d3ball36-main.kicad_sym")(options "")(descr "k0d3ball36 main PCB symbols"))\n)\n')
    (OUT / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n  (lib (name "k0d3ball36")(type "KiCad")(uri "${KIPRJMOD}/../lib/k0d3ball36.pretty")(options "")(descr "k0d3ball36 project footprints"))\n)\n')
    print(f"wrote {OUT / 'k0d3ball36.kicad_sch'} with {len(comps)} components")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
