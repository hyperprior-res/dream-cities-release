HPR_ROOT := $(abspath ..)
include $(HPR_ROOT)/build_common.mk

.PHONY: all check clean prepare-tex-cache
all: example.pdf

figure-example.pdf: scripts/make_example_figure.py figure_style.py hyperprior.mplstyle
	$(PYTHON) scripts/make_example_figure.py

example.pdf: example.tex hyperprior.cls wordmark.pdf figure-example.pdf
	$(TECTONIC) -X compile $(TEX_OPTIONS) example.tex

# Explicit setup target. It may download TeX resources; ordinary builds cannot.
prepare-tex-cache: figure-example.pdf
	$(TECTONIC) -X compile --keep-logs --untrusted example.tex

check: example.pdf
	$(PYTHON) scripts/check_pdf.py example.pdf --output review/format/example-check.json

clean:
	rm -f example.aux example.log example.out example.bbl example.blg
