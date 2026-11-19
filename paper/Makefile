# Dream cities: build the paper from the result files on CPU.
#
#   make            numbers, tables, figures, then the PDF (the build stops if any macro's source is missing)
#   make numbers    paper/numbers.tex, the macro ledger and the generated tables from results/ (always rerun,
#                   so results that land between builds reach the text)
#   make figures    every figure script under ../figures/ (Figure 1's data step is separate: make fig1-data);
#                   fig_pressure.py draws the main figure (section 3); fig_across.py draws section 5's figure only
#                   when results/analysis/main_claim.json is complete (a labelled stub until then)
#   make fig1-data  replays the Figure 1 plan on the engine and draws 8 emulator samples on the CPU
#   make check      fonts, ??, overfull boxes (template check), the numbers gate and the slot list
#   make format     page 1 beside the reference at 150 dpi, into review/format/
#
# The TeX engine is the group's qualified Tectonic 0.17.0, offline, with the cache in ../.build-cache.
REPO := $(abspath ..)
PYTHON ?= $(REPO)/.venv/bin/python
TECTONIC ?= $(or $(firstword $(wildcard $(REPO)/ext/tools/tectonic-0.17.0/tectonic $(REPO)/scratch/tools/tectonic-0.17.0/tectonic)),tectonic)
export XDG_CACHE_HOME ?= $(REPO)/.build-cache
export MPLCONFIGDIR ?= $(REPO)/.build-cache/matplotlib
export MPLBACKEND := Agg
export CUDA_VISIBLE_DEVICES :=
export OMP_NUM_THREADS := 4
export PYTHONPATH := $(REPO)/code:$(REPO)/hpr-dream
TEX_OPTIONS = $(if $(TEX_FETCH),,$(if $(wildcard $(XDG_CACHE_HOME)/Tectonic),--only-cached,)) --keep-logs --untrusted
FIGS := $(REPO)/figures
SECTIONS := $(wildcard sections/*.tex)

.PHONY: all numbers figures fig1-data check format clean FORCE
FORCE:
.DEFAULT_GOAL := all

all: main.pdf

numbers numbers.tex: scripts/make_numbers.py figures FORCE
	$(PYTHON) scripts/make_numbers.py

figures/fig1_environment.json figures/fig1_environment.pdf: $(FIGS)/fig1_environment.py $(FIGS)/hpr_fig.py $(FIGS)/data/fig1_case.npz \
		$(REPO)/results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24/patching.jsonl.gz
	$(PYTHON) $(FIGS)/fig1_environment.py

fig1-data:
	$(PYTHON) $(FIGS)/fig1_data.py

figures: figures/fig1_environment.pdf
	$(PYTHON) $(FIGS)/fig_anatomy.py
	$(PYTHON) $(FIGS)/fig_pressure.py
	$(PYTHON) $(FIGS)/fig_main_results.py
	$(PYTHON) $(FIGS)/fig_gallery.py
	$(PYTHON) $(FIGS)/fig_mechanism.py
	$(PYTHON) $(FIGS)/fig_defences.py
	$(PYTHON) $(FIGS)/fig_coverage.py
	$(PYTHON) $(FIGS)/fig_across.py
	$(PYTHON) $(FIGS)/fig_heatmaps.py
	$(PYTHON) $(FIGS)/fig_spatial_decomp.py
	$(PYTHON) $(FIGS)/fig_slots.py

refs_tex.bib: refs.bib scripts/bib_for_tex.py
	$(PYTHON) scripts/bib_for_tex.py

main.pdf: main.tex numbers.tex refs_tex.bib $(SECTIONS) hyperprior.cls figures
	@test -x "$(TECTONIC)" || { echo "No Tectonic 0.17.0 binary found" >&2; exit 1; }
	$(TECTONIC) -X compile $(TEX_OPTIONS) main.tex
	@grep -c "Overfull" main.log | xargs -I{} echo "overfull boxes: {}"

check: main.pdf
	$(PYTHON) $(REPO)/template/scripts/check_pdf.py main.pdf --output review/main-pdf-check.json || true
	$(PYTHON) scripts/check_numbers.py
	$(PYTHON) scripts/check_slots.py

format: main.pdf
	$(PYTHON) scripts/compare_format.py

clean:
	rm -f main.aux main.log main.out main.bbl main.blg
