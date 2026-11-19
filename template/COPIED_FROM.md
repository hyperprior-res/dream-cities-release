# Copied from the group template

This directory is a verbatim copy of the HyperPrior Research shared paper
template. Do not edit it here: the class, wordmark and figure style must stay
byte-identical across the group's papers. Record wishes for the template in
`../review/format/BUILD_NOTES.md` instead.

| Item | Value |
|---|---|
| Source repository | `<home>/development/papers` |
| Source path | `hyperprior/template/` |
| Source commit | `672f3c61265b6fd598e328e648c51d61f802c52a` |
| Commit date | 2026-10-18T17:52:04+01:00 |
| Commit subject | Complete scientific reviews, export verification and final handoff |
| Source tree object | `6bff271d0f4950b55595e397b0f9f334c068aab3` |
| Copied | 18 October 2026 |
| Files | 65 (every file tracked at that commit; this file is the only addition) |

The papers working tree was clean when copied. The files were extracted with

```sh
git -C <home>/development/papers archive --format=tar \
  672f3c61265b6fd598e328e648c51d61f802c52a:hyperprior/template | tar -x -C template
```

so build junk that the papers repository does not track was not copied
(`__pycache__/`, `scripts/__pycache__/`, `example.aux`, `example.log`,
`example.out`). Each copied file was then compared byte for byte with the
papers working tree, and file modes were compared; all matched.

Paths in `README.md` such as `.research-run/...`, `../REPRODUCE.md` and
`../requirements-reproduce.txt` are relative to the papers repository. In this
repository the build reads the qualified Tectonic binary and resource ZIP from
that repository's `.research-run/`; see `../build_common.mk` and
`../review/format/BUILD_NOTES.md`.

## SHA-256 manifest

Verify from this directory with:

```sh
sed -n '/^```sha256$/,/^```$/p' COPIED_FROM.md | sed '1d;$d' | sha256sum --check --quiet
```

```sha256
5b1bab4087ede16b410384dbb1f1feac2a7d8dbf940062f6ebcda55a8908fed4  .gitignore
dae67e57bc66a400dd62528e708bd580be325861be4e631866f6547e7aea8c8a  Makefile
d94727156a79d7de6a9ba1fda95d0df563e493290a32067bbed53c2a2f7a74f1  README.md
b294b1f71f77d44366dd9021f1f35ea6cb30dd6e8d3fa1bef2af2687b3fbc871  diagram_style.py
8d18981795cf8b44b33a6cae5705d4c24c2aff5aac207121e8b38ad8baf08d39  example.pdf
a037ff2474956101f0baf14ea6f32eacbf27c0a511eb267824710ef7c4338412  example.tex
5aef6bf3099310bc1d6826ef59e8043d63576800a7b8eeddf3b8a9b72a0f338c  figure-example.pdf
d30757ab56028c8c354291575e1fe4eb8647310db688ee62d08374bb5c9ac10f  figure_style.py
2ecd309de8dfc6517ab08e230498537f54e071e27c2f87236f56afc6e40c3530  fonts/LICENCE.txt
3030fbc563d7c2174311770682b3d4d412c5598e646a33df9326b562e95d5331  fonts/XCharter-Bold.ttf
de546339aed4edbbe08935aeb8d2c3b131cfec7b3d336b1a8c963d2d1f59e4c4  fonts/XCharter-BoldItalic.ttf
e091ca7280efc6205c5139b31341b7eb345db1babfd6af59f22ab868a98b4fdf  fonts/XCharter-Italic.ttf
c437dccaac12b4feef1745b2eaddfeabcfe75ffaf9c95781ec6b34e8057c2a95  fonts/XCharter-Roman.ttf
4f753c3719c058265a1b2378613b414696044b5dfd178a31854b6352029bc22d  fonts/manifest.json
bba754241658ff09db52e24a4b9fb170bb9e0576f06b58533271cdca3d940889  hyperprior.cls
cdac92e863abffde838833fdc17669269a0d90b464a89b8ed23453052b52c0db  hyperprior.mplstyle
b738cea2e23f6dda8f363c93a19254cad9582a951a257a79c2dfc9e56d9847ba  layout-measurements.md
1d941c7d3ed9b1570893b145f81b9ed2fd890781cfa475fdba4f8a9e672d2807  requirements.txt
43129ac66a4d268e4402bd4a6968b67d4732dfed432a36049e9f464a60683508  review/check_execution_overview_binding.py
f81bc55fb6a8c127138f0f127256a8b649239a2b393ffa543efcf77239206bbd  review/check_grader_card_conditions.py
dac676760ffa621d64dc1b3df1d4ccdc8b853d2bae839e300b4e659cb8d0e620  review/check_grader_card_conditions_pdf.py
f60f5c0918c21c812a88dd2dba06406d67d5ae4b9d7e25175ce5e151ffb183de  review/check_grader_card_redesign.py
2ce7d1039927048f2b1cf54418d60195c5bbbc58f3214396419a640370488771  review/check_tectonic_bibliography.py
7677936b732c6b8c15874bfaa1ea631d6dbffb835025377d0d7460e1da8bea5d  review/design-redesign-20261018.json
024a82568aee245f87a0dcd38c239e730bbdec32864de019487a73e09edb2b04  review/design-redesign-20261018.md
743acf463d86c0b688c1afa6a8b0759f79a95d71a1211edf70197df1bb142c9b  review/execution-overview-binding-check.json
62b86cad3720e91988c05d74a23fd6603504ae8a7b61e6bdec496419e3bd4c4f  review/execution-overview-candidate-check.json
9624b285529ea6629dffef4461d7e30ca123897cca1cfe65898fad2408bccc2b  review/execution-overview-candidate.md
228faba01699041e1b9bbfb11c41cd4433b120ace1e1f9e9d118f5e2b1fc1f67  review/format/example-check.json
42393ff34c9a8fc71bed1f7a1514cbc6d87601b89064f29e621a1852afb3f995  review/format/example-comparison.png
e69cf1b9b46b174701dc7d850bc38155e6dba3f0a3ac41d8c47ef0819a0ac26b  review/format/metadata-review.json
8d8b4b3288a19b077135a3ecc2fcc6945a78c19459d42be3bc55930898be0230  review/format/metadata-review.md
4b587d743a52acbbac01bcb43a768667382ec32931ac2390cdb9904030ad986d  review/format/overview-label-review.json
e1cfe44317f7d374a4d948e9a4b2e7c1fe07b77d86d9ba934e794bde375240e5  review/format/template-compliance.json
aad5652a0218e7e9ef86ef5bf6ec753f1e6c3f1fa75fa89f5995b08688ce48aa  review/format/template-compliance.md
caf118401b194b6b12b3c65ef3801c538f3d78f3b6e201cefc1f410dcf6cf43f  review/grader-card-conditions-check.json
080e8526198d5865c261dd32cc61395cd5a540e8e992426ff7eeceec6f8bd053  review/grader-card-conditions-pdf.json
ca32812fe648f387e94986c4565ffa27810150499fb5c09260746040a54e0d36  review/grader-card-conditions.md
9fedef4e1cccb7ed1dbf7c1a4782bb44e82e8f6e264fa68a871195e40203d085  review/grader-card-footer-7pt.json
d86773e1a4fc792cf17864ac9a1fc3ad7c47677bd417648ab8c3a65d433c16cd  review/grader-card-footer-7pt.md
f6677c2171066ce78f1058466f1156afbce0a898b06d375fc2249059dee0e178  review/grader-card-layout.json
4150a79130baccf8721fc8501b706332fd8663df2c1da5c6057f9d33752e1151  review/grader-card-layout.md
4df80379bd33e95b617c492ea6b92250d3a2bbb9d9b51b7ec2a08c0c8747cc7d  review/grader-card-redesign-bounds.json
013cfd00cbabbf138ab7be559fcf1dcfe3d83163688d153bddbfe1aa6654bf06  review/grader-card-redesign-check.json
ee23cbe2518ff9ddc1c0303add52ffcca42de01885134905a14d0525054db6de  review/grader-card-redesign.md
f55a80ef8f10f3a9b365b6f1806ededdd72694a92ee49c10676baa8e4172782c  review/tectonic-0.17.0-download.json
54d2bb2e5f63fff64c63f44c021b5cb0185f898cde971076d4a281802e9183b6  review/tectonic-bibliography-qualification.json
65350a37254eb90cc781db6445886328be199daa83d89b1da85cac9634e9fc50  review/tectonic-bibliography-qualification.md
903773b5a30b833162ee0ba1de35879b34fef1f1d22f227e5b76276617e7b9cb  review/tectonic-qualified-environment.json
e2be98c1da34c870b2a8ae4589d43283fc742d40213a24ff8f49c787f2d96bce  review/terminology-layout.json
c4c0c471f39ee8e30b4f40c0c15dc8166e388404da34183267310ffd47ec9194  review/terminology-layout.md
9fe7ad5d254c7c9d199f55e3683725f6d02d06af709a943bc55df60faddfce48  scripts/check_pdf.py
4ea1053230ad0680cc51a5c558c567cd01be49847378ecb0f572bacbf6f993ad  scripts/compare_pages.py
cd867ab2543bd2f2c78cfe1a57958857532ee2a78a8825658210bb744339c90c  scripts/make_boundary_diagram.py
2a60d6e26f1085a856c46e1889eb3e7ebaa83591615ee1ef3861a3420fde3dd6  scripts/make_example_figure.py
4ed23dbf6444d54cddc7f46279e3afb9a1c66c9d9044fc4dbc148c9e8b02d97a  scripts/make_execution_overview.py
587ebbcdee5172e1a7b43a1ffbdfa2011cc87de9794940b1a6b536369b767e88  scripts/make_overviews.py
701315fa201c43e0081a0898458c6124aa00e1afa2c814bfb49a0d2a52e319f7  scripts/make_wordmark.py
f04a912e49cb7d11c81989ffdd1f1f72e442d13ed380474d651adf03ca683694  scripts/prepare_local_tex_bundle.py
763fa26ce6d02e2299c8c3d131205a166080deb4b8d65328a790a95abce5c0d8  scripts/render_grader_card.py
63216548d1a86671737bf0a93ae54b9f685c404cef09c52baef2d4c43717c5b2  scripts/render_live_calendar.py
12b975fd6ae7cdefaaabb94618c8735b2ce41cf6959bd6e90c1baedfc38f0524  scripts/render_question_card.py
7e851c72cdbe92c88e63be2e365512927b178759f5f5250baa52c40cc2a16f3a  wordmark-provenance.json
98b5c7e91881daf036386cf30628aa3bdfc7c41b1c50b327334393541d0450c7  wordmark.pdf
2a84ff712f8416c9351c02325a06b96e79e4c2d70965dd254699b242231ac185  wordmark.svg
```
