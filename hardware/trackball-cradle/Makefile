# k0d3ball35 trackball cradle build
# Requires OpenSCAD 2025.x or newer with the Manifold backend (tested with 2026.10.11,
# `brew install --cask openscad@snapshot`). The 2021.01 release renders the same
# geometry but is roughly 100x slower and lacks --backend.
#
# One variant since r2.4: the 19.05 mm ball in the case pocket, sensor module tilted beside it.

OPENSCAD ?= $(shell command -v openscad 2>/dev/null || echo /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD)
OSC       = $(OPENSCAD) --backend manifold
PYTHON   ?= python3
# cameras look at the exported (print frame) scene: y and the turn about z are those of the
# layout-frame view mirrored in y (target y -> -y, rot_z -> 180 - rot_z)
CAM_SEC   = --camera=0,0,3,80,0,270,110 --imgsize=1200,900 --colorscheme=Tomorrow
CAM_ASM   = --camera=0,0,5,55,0,145,170 --imgsize=1200,900 --colorscheme=Tomorrow
CAM_BODY  = --camera=0,0,0,55,0,325,90 --imgsize=1200,900 --colorscheme=Tomorrow
POCKET19  = -D ball_d=19.05

STL = stl/cradle-19mm-pocket.stl
DXF = dxf/floor-19mm-pocket.dxf
PNG = preview/section-19mm-pocket.png preview/assembly-19mm-pocket.png preview/cradle-19mm-pocket.png

.PHONY: all stls dxfs previews stack clean
all: stls dxfs previews stack
stls: $(STL)
dxfs: $(DXF)
previews: $(PNG)

stl dxf preview:
	@mkdir -p $@

stl/cradle-19mm-pocket.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="cradle"'   $(POCKET19) -o $@ $<

dxf/floor-19mm-pocket.dxf: cradle.scad params.scad | dxf
	$(OSC) -D 'part="floor2d"'  $(POCKET19) -o $@ $<

preview/section-19mm-pocket.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="section"'  $(POCKET19) $(CAM_SEC) -o $@ $<
preview/assembly-19mm-pocket.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="assembly"' $(POCKET19) $(CAM_ASM) -o $@ $<

# the printed body alone, from the sleeve side: tab, open back, rim chamfer
preview/cradle-19mm-pocket.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="cradle"'   $(POCKET19) $(CAM_BODY) -o $@ $<

stack: stack.json
stack.json: cradle.scad params.scad stack.py
	$(PYTHON) stack.py $(OPENSCAD)

clean:
	rm -rf build stl dxf preview stack.json
