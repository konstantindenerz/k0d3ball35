# k0d3ball36 trackball cradle build
# Requires OpenSCAD 2025.x or newer with the Manifold backend (tested with 2026.10.11,
# `brew install --cask openscad@snapshot`). The 2021.01 release renders the same
# geometry but is roughly 100x slower and lacks --backend.

OPENSCAD ?= $(shell command -v openscad 2>/dev/null || echo /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD)
OSC       = $(OPENSCAD) --backend manifold
PYTHON   ?= python3
CAM_SEC   = --camera=0,0,3,75,0,200,150 --imgsize=1200,900 --colorscheme=Tomorrow
CAM_ASM   = --camera=0,0,5,55,0,35,170 --imgsize=1200,900 --colorscheme=Tomorrow

STL = stl/cradle-25mm.stl stl/retainer-25mm.stl \
      stl/cradle-25mm-tilted.stl \
      stl/cradle-34mm.stl stl/retainer-34mm.stl
DXF = dxf/cutout-25mm.dxf dxf/cutout-25mm-tilted.dxf dxf/cutout-34mm.dxf
PNG = preview/section-25mm.png preview/assembly-25mm.png preview/section-25mm-tilted.png preview/assembly-34mm.png

.PHONY: all stls dxfs previews stack clean
all: stls dxfs previews stack
stls: $(STL)
dxfs: $(DXF)
previews: $(PNG)

stl dxf preview:
	@mkdir -p $@

stl/cradle-25mm.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="cradle"'   -o $@ $<
stl/retainer-25mm.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="retainer"' -o $@ $<
stl/cradle-25mm-tilted.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="cradle"' -D sensor_angle=60 -o $@ $<
stl/cradle-34mm.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="cradle"'   -D ball_d=34 -o $@ $<
stl/retainer-34mm.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="retainer"' -D ball_d=34 -o $@ $<

dxf/cutout-25mm.dxf: cradle.scad params.scad | dxf
	$(OSC) -D 'part="cutout2d"' -o $@ $<
dxf/cutout-25mm-tilted.dxf: cradle.scad params.scad | dxf
	$(OSC) -D 'part="cutout2d"' -D sensor_angle=60 -o $@ $<
dxf/cutout-34mm.dxf: cradle.scad params.scad | dxf
	$(OSC) -D 'part="cutout2d"' -D ball_d=34 -o $@ $<

preview/section-25mm.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="section"' $(CAM_SEC) -o $@ $<
preview/section-25mm-tilted.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="section"' -D sensor_angle=60 $(CAM_SEC) -o $@ $<
preview/assembly-25mm.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="assembly"' $(CAM_ASM) -o $@ $<
preview/assembly-34mm.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="assembly"' -D ball_d=34 $(CAM_ASM) -o $@ $<

stack: stack.json
stack.json: cradle.scad params.scad stack.py
	$(PYTHON) stack.py $(OPENSCAD)

clean:
	rm -rf build stl dxf preview stack.json
