# k0d3ball36 build entry points.
# Override tool paths on the command line, e.g. `make drc KICAD_CLI=kicad-cli`.

KICAD_CLI ?= /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY        ?= .venv/bin/python
ERGOGEN   ?= ergogen

LAYOUT     := hardware/layout/k0d3ball36.yaml
LAYOUT_OUT := hardware/layout/output
MAIN_DIR   := hardware/main-pcb
MAIN_SCH   := $(MAIN_DIR)/k0d3ball36.kicad_sch
MAIN_PCB   := $(MAIN_DIR)/k0d3ball36.kicad_pcb
SENSOR_DIR := hardware/sensor-pcb
SENSOR_SCH := $(SENSOR_DIR)/k0d3ball36-sensor.kicad_sch
SENSOR_PCB := $(SENSOR_DIR)/k0d3ball36-sensor.kicad_pcb
BUILD      := build

SCHS := $(wildcard $(MAIN_SCH) $(SENSOR_SCH))
PCBS := $(wildcard $(MAIN_PCB) $(SENSOR_PCB))

.PHONY: all layout sch pcb route erc drc gerbers firmware test issues docs-check clean help

all: layout sch pcb route erc drc gerbers

help:
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

layout: ## Run Ergogen: points, outlines, unrouted PCB
	$(ERGOGEN) $(LAYOUT) -o $(LAYOUT_OUT)

sch: ## Generate the main PCB schematic from the layout and the design spec
	$(PY) scripts/gen_schematic.py

pcb: ## Place footprints and assign nets on the main PCB
	$(PY) scripts/gen_pcb.py

route: ## Autoroute the main PCB and import the result
	scripts/route.sh

erc: ## Electrical rules check on every schematic
	@mkdir -p $(BUILD)
	@for s in $(SCHS); do \
	  echo "ERC $$s"; \
	  $(KICAD_CLI) sch erc --exit-code-violations --severity-error --format json \
	    -o $(BUILD)/$$(basename $$s .kicad_sch).erc.json $$s || exit 1; \
	done

drc: ## Design rules check with schematic parity on every PCB
	@mkdir -p $(BUILD)
	@for p in $(PCBS); do \
	  echo "DRC $$p"; \
	  $(KICAD_CLI) pcb drc --exit-code-violations --severity-error --schematic-parity --format json \
	    -o $(BUILD)/$$(basename $$p .kicad_pcb).drc.json $$p || exit 1; \
	done

gerbers: ## Export gerbers, drill files, STEP and renders
	scripts/export.sh

firmware: ## Build ZMK firmware locally with docker (CI is the reference build)
	@if command -v docker >/dev/null 2>&1; then \
	  scripts/build_firmware.sh; \
	else \
	  echo "docker not found. Firmware is built by .github/workflows/firmware.yml;"; \
	  echo "see docs/05-firmware.md for a local west setup."; \
	fi

test: ## Run the test suite
	$(PY) -m pytest -q

issues: ## Regenerate issues/README.md from the ticket frontmatter
	$(PY) scripts/issues.py

docs-check: ## Run only the documentation and ticket checks
	$(PY) -m pytest -q tests/test_docs.py tests/test_issues.py tests/test_license.py

clean:
	rm -rf $(BUILD) .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
