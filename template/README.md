# HyperPrior paper format

This is an independent class built from the measurements in
`layout-measurements.md`. It uses XCharter, the reference's open body typeface.
The house mark is Austin drawn as vector paths. No font substitution was needed.

Use the qualified Tectonic 0.17.0 binary and the CPU dependencies in
`../requirements-reproduce.txt`. The local binary is
`.research-run/tools/tectonic-0.17.0/tectonic`; the system installation is
unchanged. Pass its absolute path as `TECTONIC` and the prepared local resource
ZIP as `TECTONIC_BUNDLE`, then run:

```sh
make
make check
```

Ordinary builds pass `--only-cached --untrusted` to Tectonic and cannot fetch
missing TeX resources. The qualified ZIP is
`.research-run/figure-review/tectonic-bibliography-qualification/cached-resources.zip`,
SHA-256 `bd549861bece732bb330ffd858f635d4fac84099872aa227ab9c3c7e6098c790`.
It contains the verified resource subset already used by these papers, with a
distinct subset identity; it does not claim to be the complete upstream bundle.
The environment check verifies this exact ZIP. `BUILD_CACHE` selects the format
cache, defaulting to `.research-run/cache` in the papers repository. Tectonic
0.17 uses a different cache layout from 0.15, so the old default cache alone is
insufficient for an offline build.

Reconstruct the ZIP from the existing verified cache without network access:

```sh
python hyperprior/template/scripts/prepare_local_tex_bundle.py \
  --cache .research-run/cache/Tectonic \
  --manifest .research-run/cache/Tectonic/manifests/6ffe055852f8faf66c0acbe1a7fb27f87b869a90bad1204f3bf4d9683f597c7c.txt \
  --output .research-run/figure-review/tectonic-bibliography-qualification/cached-resources.zip
```

Run this command from the papers repository. It verifies every cached member,
orders names and fixes ZIP timestamps. Missing or changed resources fail
explicitly. Preserve the qualified bundle as a build dependency for a clean
checkout; no model weights or inference runtime are needed. See
`review/tectonic-bibliography-qualification.md` for the compiler comparison and
`../REPRODUCE.md` for the complete build. `make prepare-tex-cache` remains a
separate setup command that permits downloads; it is not part of reproduction.

The figure helper verifies the four bundled open XCharter outline fonts in
`fonts/manifest.json`; it makes no network calls. Their original licence notice
is preserved in `fonts/LICENCE.txt`. The wordmark's outlined PDF and SVG are
included, so rebuilding papers needs no proprietary font file. The optional
dependencies in this directory's `requirements.txt` support source-font
conversion and raster comparison, which are outside the ordinary PDF build.

Each paper directory contains a relative `hyperprior.cls` link to the shared
class. This keeps the ordinary restricted Tectonic build independent of extra
search paths, which `--untrusted` disables. For another paper directory, create
the equivalent relative link, then use:

```tex
\documentclass{hyperprior}
\wordmarkpath{../../template/wordmark.pdf}
\title{A concrete research title}
\date{2026-10-18}
\keywords{evaluation, resolution}
\begin{abstract}
The abstract is stored here before the document begins.
\end{abstract}
\begin{document}
\maketitle
\section{Introduction}
The main text begins here.
\end{document}
```

The authors and affiliation default to the requested byline. Use `\author` and
`\affiliation` only when that changes. Correspondence appears as a website link.
The first page carries the house mark and finishing date. Later pages carry the
title and page number.

Working papers enable version, prior-confidence and revisit metadata with:

```tex
\workingpaper{\PaperVersion}{\PriorConfidence}{\RevisitDate}
```

The manuscript supplies these macros; the class invents no values. Use generated
metadata macros where the prior is a registered numerical statement. The
finishing date already supplied to `\date` is repeated automatically, so version,
date, prior confidence and revisit date appear on every page. A compact block
sits beside the first-page correspondence note; later pages use a single footer
line with the page number at right. Omitting `\workingpaper` preserves the
original footer. The example uses explicitly non-empirical specimen values.

For figures, import `apply`, `save`, `COLUMN_IN` and `TEXT_IN` from
`figure_style.py`. Call `apply()` before drawing. Draw at the final size and use
7–9 pt labels. `save(fig, path)` writes vector PDF with embedded outline fonts.
Use the dark red as the principal accent, blue only for a meaningful second
condition, and greys for context. Use direct labels where they remain legible.

Regenerate the mark only when the source font is available locally:

```sh
python scripts/make_wordmark.py --font /path/to/austin-regular.woff2
```

Compare a paper with the source PDF without retaining its contact details:

```sh
python scripts/compare_pages.py --reference /path/to/reference.pdf \
  --paper example.pdf --output review/format/example-comparison.png
```

The script redacts the source contact block and margin identifier before
rasterising. It retains no source text or PDF. `check_pdf.py` checks embedded
fonts, bitmap fonts, cross-references and significant text-box warnings.

For Matplotlib PDF embedding, the helper converts the open font’s cubic outlines
to quadratic outlines with a tolerance of half a font unit. This changes the font
container, not the chosen typeface; it avoids a PDF font-type mismatch. These
converted fonts are bundled with their source-archive checksum and their own
checksums in `fonts/manifest.json`.

The question-anatomy renderer reads one actual filtered record and writes a
vector PDF plus a provenance sidecar. It requires quote timestamps and source
hashes; it does not fill missing fields with illustrative values:

```sh
python scripts/render_question_card.py /path/to/questions.jsonl \
  --question-id SOURCE:IDENTIFIER --output /path/to/question-anatomy.pdf
```

The renderer displays metadata only. Outcomes are not shown in the card, and
the displayed crowd quotes are not model inputs. Select the record after the
eligibility ledger has been applied, and include the generated provenance file
in the figure build.

The study schematics are generated with:

```sh
python scripts/make_overviews.py
python scripts/make_boundary_diagram.py
```

The second study's overview follows the ordinary-task-solving amendment. Its
sampler and training policy are separate, and the adversarial arm is explicitly
absent. `trust-boundary.pdf` shows the location of expected values and the two
decision-error types. It contains no executable examples and makes no claim
about observed tampering or resistance to adaptive attacks. Update the overview
if the realised training matrix changes before the experiment freeze.

Render a dated live batch and a recorded grader card with:

```sh
python scripts/render_live_calendar.py /path/to/live/questions.jsonl \
  --output /path/to/live-calendar.pdf
python scripts/render_grader_card.py /path/to/cards/visible_gated.json \
  --output /path/to/grader-card.pdf
```

The calendar uses `scheduled_event_date` and groups by `superfamily_id`.
It never substitutes that date for an unavailable platform settlement date.
It writes a caption and provenance sidecar containing the source hash, date
counts and shared-event counts. Its labels do not expose question text.

The card renderer accepts the JSON emitted by `hpr-audit`. Under `metrics`,
`budget_curve` is a list of records with `budget`, `estimate`, `lower` and
`upper`. `false_rejection_rate` has `estimate`, optional interval bounds and
`denominator`, the number of oracle-passing programs. A separate
`canonical_reference_false_rejection_rate` field reports the corresponding
reference-program check. `failure_classes` maps names to records containing
`count` and `denominator` or an estimated rate and interval. Optional
`budget_description` supplies the precise sampler budget. Missing observations
remain unavailable. The renderer preserves the supplied measurements in its
provenance sidecar, labels the curve as ordinary sampling, and treats the
revisit date as administrative. It does not estimate shelf life from one audit.

`interval_description` and `rejection_interval_description` print the respective
interval method and resampling unit; the renderer does not infer them from
bounds. Nested `ast_label_counts` and `token_label_counts` retain separate syntax
counts, with `failure_classes.accepted_wrong_count` printed as their denominator.
The chart starts at zero and labels its observed upper scale. Missing-data
bounds have separate dashed marks, missing estimates remain gaps, and all type
is at least 7 pt at the intended full-page size. Explicitly synthetic display
checks and their previews are described in `review/grader-card-redesign.md`.
