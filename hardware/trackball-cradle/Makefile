# k0d3ball36 trackball cradle build
# Requires OpenSCAD 2025.x or newer with the Manifold backend (tested with 2026.10.11,
# `brew install --cask openscad@snapshot`). The 2021.01 release renders the same
# geometry but is roughly 100x slower and lacks --backend.
#
# Variants: 19.05 mm ball in the case pocket (r2 default), 25 mm ball in a wider pocket
# (fallback, needs a PCB with a 16.5 mm notch apothem), 25 mm ball through a PCB cutout (r1).

OPENSCAD ?= $(shell command -v openscad 2>/dev/null || echo /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD)
OSC       = $(OPENSCAD) --backend manifold
PYTHON   ?= python3
CAM_SEC   = --camera=0,0,3,75,0,200,150 --imgsize=1200,900 --colorscheme=Tomorrow
CAM_ASM   = --camera=0,0,5,55,0,35,170 --imgsize=1200,900 --colorscheme=Tomorrow
POCKET19  = -D 'mount="pocket"' -D ball_d=19.05
POCKET25  = -D 'mount="pocket"' -D ball_d=25 -D notch_apothem=16.5
CUTOUT25  = -D 'mount="cutout"' -D ball_d=25

STL = stl/cradle-19mm-pocket.stl stl/retainer-19mm.stl \
      stl/cradle-25mm-pocket.stl stl/retainer-25mm.stl \
      stl/cradle-25mm-cutout.stl
DXF = dxf/floor-19mm-pocket.dxf dxf/floor-25mm-pocket.dxf dxf/cutout-25mm.dxf
PNG = preview/section-19mm-pocket.png preview/assembly-19mm-pocket.png \
      preview/assembly-25mm-pocket.png preview/section-25mm-cutout.png

.PHONY: all stls dxfs previews stack clean
all: stls dxfs previews stack
stls: $(STL)
dxfs: $(DXF)
previews: $(PNG)

stl dxf preview:
	@mkdir -p $@

stl/cradle-19mm-pocket.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="cradle"'   $(POCKET19) -o $@ $<
stl/retainer-19mm.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="retainer"' $(POCKET19) -o $@ $<
stl/cradle-25mm-pocket.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="cradle"'   $(POCKET25) -o $@ $<
stl/retainer-25mm.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="retainer"' $(POCKET25) -o $@ $<
stl/cradle-25mm-cutout.stl: cradle.scad params.scad | stl
	$(OSC) -D 'part="cradle"'   $(CUTOUT25) -o $@ $<

dxf/floor-19mm-pocket.dxf: cradle.scad params.scad | dxf
	$(OSC) -D 'part="floor2d"'  $(POCKET19) -o $@ $<
dxf/floor-25mm-pocket.dxf: cradle.scad params.scad | dxf
	$(OSC) -D 'part="floor2d"'  $(POCKET25) -o $@ $<
dxf/cutout-25mm.dxf: cradle.scad params.scad | dxf
	$(OSC) -D 'part="cutout2d"' $(CUTOUT25) -o $@ $<

preview/section-19mm-pocket.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="section"'  $(POCKET19) $(CAM_SEC) -o $@ $<
preview/assembly-19mm-pocket.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="assembly"' $(POCKET19) $(CAM_ASM) -o $@ $<
preview/assembly-25mm-pocket.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="assembly"' $(POCKET25) $(CAM_ASM) -o $@ $<
preview/section-25mm-cutout.png: cradle.scad params.scad | preview
	$(OSC) --render -D 'part="section"'  $(CUTOUT25) $(CAM_SEC) -o $@ $<

stack: stack.json
stack.json: cradle.scad params.scad stack.py
	$(PYTHON) stack.py $(OPENSCAD)

clean:
	rm -rf build stl dxf preview stack.json
