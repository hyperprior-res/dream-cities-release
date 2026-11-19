# Start-state families

Built by `python code/scripts/build_families.py --workers 16` in 9 s. Protocol `dc-replay-1`. 100 families, 268 start files.

## Bundled cities screened

Rule: population at load at least 2,000 and the start bar met; first 20 by file name.

| file | pop | zones | powered | no-op min/start | bar | taken |
|---|---|---|---|---|---|---|
| about.cty | 0 | 0 | 1.00 | 0.00 | fails: pop,zones,noop_collapse |  |
| badnews.cty | 156,060 | 566 | 0.35 | 0.73 | fails: powered |  |
| bluebird.cty | 0 | 0 | 1.00 | 0.00 | fails: pop,zones,noop_collapse |  |
| bruce.cty | 14,400 | 58 | 1.00 | 1.02 | met | yes |
| deadwood.cty | 6,840 | 506 | 1.00 | 1.03 | met | yes |
| finnigan.cty | 0 | 0 | 1.00 | 0.00 | fails: pop,zones,noop_collapse |  |
| freds.cty | 63,120 | 146 | 1.00 | 0.92 | met | yes |
| haight.cty | 213,540 | 615 | 1.00 | 0.81 | met | yes |
| happisle.cty | 105,540 | 277 | 1.00 | 0.96 | met | yes |
| joffburg.cty | 178,680 | 351 | 1.00 | 1.00 | met | yes |
| kamakura.cty | 90,320 | 263 | 1.00 | 0.75 | met | yes |
| kobe.cty | 152,640 | 396 | 1.00 | 0.92 | met | yes |
| kowloon.cty | 136,620 | 420 | 1.00 | 0.87 | met | yes |
| kyoto.cty | 108,560 | 431 | 1.00 | 0.69 | met | yes |
| linecity.cty | 12,780 | 41 | 1.00 | 1.04 | met | yes |
| med_isle.cty | 24,880 | 81 | 1.00 | 1.01 | met | yes |
| ndulls.cty | 35,040 | 77 | 1.00 | 0.95 | met | yes |
| neatmap.cty | 0 | 0 | 1.00 | 0.00 | fails: pop,zones,noop_collapse |  |
| radial.cty | 38,200 | 219 | 1.00 | 0.64 | met | yes |
| scenario_bern.cty | 95,300 | 244 | 1.00 | 0.89 | met | yes |
| scenario_boston.cty | 79,080 | 331 | 1.00 | 0.82 | met | yes |
| scenario_detroit.cty | 75,940 | 305 | 0.99 | 0.84 | met | yes |
| scenario_dullsville.cty | 18,080 | 31 | 1.00 | 0.92 | met | yes |
| scenario_hamburg.cty | 109,600 | 309 | 0.99 | 0.98 | met | yes |
| scenario_rio_de_janeiro.cty | 152,260 | 429 | 0.99 | 0.94 | met | yes |
| scenario_san_francisco.cty | 107,540 | 295 | 1.00 | 0.95 | met |  |
| scenario_tokyo.cty | 113,000 | 335 | 1.00 | 0.84 | met |  |
| senri.cty | 20,700 | 68 | 1.00 | 1.00 | met |  |
| southpac.cty | 15,180 | 47 | 1.00 | 0.93 | met |  |
| splats.cty | 0 | 0 | 1.00 | 0.00 | fails: pop,zones,noop_collapse |  |
| wetcity.cty | 19,960 | 70 | 1.00 | 1.00 | met |  |
| yokohama.cty | 80,860 | 476 | 1.00 | 0.68 | met |  |

## Families

Population, funds, zones and powered fraction are of the family's reference start at load: the full warm-up for a generated family, the bundled file itself for a bundled one. funds0: treasury of the generated terrain during the warm-up. W: warm-up months. F: funds set before saving (bundled: variants 1.. only; variant 0 is the file as distributed). style: the warm-up builder (bundled: the builder that made variants 1..). Attempts: builder re-rolls until the bar was met.

| family | split | kind | style | funds0 | W | F | pop | funds | zones | powered | variants | attempts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tr-b-bruce | train | bundled | satellite | - | 0 | 10000 | 14,400 | 281 | 58 | 1.00 | 4 | 1 |
| tr-b-deadwood | train | bundled | corridor | - | 0 | 10000 | 6,840 | 15,651 | 506 | 1.00 | 4 | 1 |
| tr-b-freds | train | bundled | satellite | - | 0 | 5000 | 63,120 | 1,510 | 146 | 1.00 | 4 | 1 |
| tr-b-haight | train | bundled | satellite | - | 0 | 40000 | 213,540 | 1,000,000 | 615 | 1.00 | 4 | 1 |
| tr-b-happisle | train | bundled | frugal | - | 0 | 5000 | 105,540 | 6,865 | 277 | 1.00 | 4 | 1 |
| tr-b-joffburg | train | bundled | grid | - | 0 | 10000 | 178,680 | 187,223 | 351 | 1.00 | 4 | 1 |
| tr-b-kamakura | train | bundled | satellite | - | 0 | 5000 | 90,320 | 58,550 | 263 | 1.00 | 4 | 1 |
| tr-b-kobe | train | bundled | frugal | - | 0 | 5000 | 152,640 | 84,383 | 396 | 1.00 | 4 | 1 |
| tr-b-kowloon | train | bundled | corridor | - | 0 | 40000 | 136,620 | 19,623 | 420 | 1.00 | 4 | 1 |
| tr-b-kyoto | train | bundled | transit | - | 0 | 5000 | 108,560 | 35,133 | 431 | 1.00 | 4 | 1 |
| tr-b-linecity | train | bundled | transit | - | 0 | 20000 | 12,780 | 10,544 | 41 | 1.00 | 4 | 1 |
| tr-b-med_isle | train | bundled | grid | - | 0 | 40000 | 24,880 | 2,236 | 81 | 1.00 | 4 | 1 |
| tr-b-ndulls | train | bundled | industry | - | 0 | 5000 | 35,040 | 3,859 | 77 | 1.00 | 4 | 1 |
| tr-b-radial | train | bundled | grid | - | 0 | 20000 | 38,200 | 17,485 | 219 | 1.00 | 4 | 1 |
| tr-b-scenario_bern | train | bundled | transit | - | 0 | 40000 | 95,300 | 20,000 | 244 | 1.00 | 4 | 1 |
| tr-b-scenario_boston | train | bundled | boom | - | 0 | 20000 | 79,080 | 20,000 | 331 | 1.00 | 4 | 1 |
| tr-b-scenario_detroit | train | bundled | industry | - | 0 | 20000 | 75,940 | 20,000 | 305 | 0.99 | 4 | 1 |
| tr-b-scenario_dullsville | train | bundled | industry | - | 0 | 5000 | 18,080 | 5,000 | 31 | 1.00 | 4 | 1 |
| tr-b-scenario_hamburg | train | bundled | boom | - | 0 | 5000 | 109,600 | 20,000 | 309 | 0.99 | 4 | 1 |
| tr-b-scenario_rio_de_janeiro | train | bundled | transit | - | 0 | 20000 | 152,260 | 20,000 | 429 | 0.99 | 4 | 1 |
| tr-g-00 | train | generated | satellite | 20000 | 270 | 40000 | 2,220 | 40,000 | 45 | 1.00 | 3 | 1 |
| tr-g-01 | train | generated | corridor | 20000 | 65 | 5000 | 9,480 | 5,000 | 68 | 1.00 | 3 | 1 |
| tr-g-02 | train | generated | frugal | 20000 | 88 | 5000 | 9,160 | 5,000 | 68 | 1.00 | 3 | 1 |
| tr-g-03 | train | generated | frugal | 20000 | 88 | 40000 | 8,220 | 40,000 | 56 | 1.00 | 3 | 1 |
| tr-g-04 | train | generated | industry | 20000 | 268 | 20000 | 9,940 | 20,000 | 68 | 1.00 | 4 | 2 |
| tr-g-05 | train | generated | satellite | 20000 | 162 | 5000 | 9,120 | 5,000 | 57 | 1.00 | 4 | 2 |
| tr-g-06 | train | generated | frugal | 20000 | 66 | 20000 | 9,720 | 20,000 | 68 | 1.00 | 3 | 4 |
| tr-g-07 | train | generated | satellite | 20000 | 152 | 20000 | 6,100 | 20,000 | 51 | 1.00 | 4 | 3 |
| tr-g-08 | train | generated | frugal | 20000 | 68 | 5000 | 9,860 | 5,000 | 56 | 1.00 | 2 | 8 |
| tr-g-09 | train | generated | frugal | 20000 | 61 | 20000 | 8,740 | 20,000 | 64 | 0.97 | 3 | 1 |
| tr-g-10 | train | generated | frugal | 20000 | 62 | 20000 | 9,080 | 20,000 | 62 | 1.00 | 3 | 1 |
| tr-g-11 | train | generated | corridor | 20000 | 214 | 20000 | 8,720 | 20,000 | 65 | 0.95 | 4 | 1 |
| tr-g-12 | train | generated | industry | 20000 | 68 | 5000 | 9,920 | 5,000 | 68 | 1.00 | 3 | 4 |
| tr-g-13 | train | generated | satellite | 20000 | 92 | 5000 | 4,580 | 5,000 | 54 | 0.94 | 3 | 1 |
| tr-g-14 | train | generated | transit | 20000 | 310 | 5000 | 24,380 | 5,000 | 73 | 1.00 | 4 | 1 |
| tr-g-15 | train | generated | industry | 20000 | 150 | 5000 | 13,160 | 5,000 | 68 | 1.00 | 4 | 4 |
| tr-g-16 | train | generated | industry | 50000 | 170 | 10000 | 20,980 | 10,000 | 126 | 1.00 | 4 | 1 |
| tr-g-17 | train | generated | industry | 20000 | 118 | 20000 | 19,080 | 20,000 | 68 | 1.00 | 4 | 1 |
| tr-g-18 | train | generated | industry | 50000 | 305 | 20000 | 29,300 | 20,000 | 134 | 0.99 | 4 | 1 |
| tr-g-19 | train | generated | corridor | 50000 | 126 | 20000 | 27,880 | 20,000 | 131 | 1.00 | 4 | 1 |
| tr-g-20 | train | generated | frugal | 50000 | 240 | 5000 | 17,140 | 5,000 | 88 | 1.00 | 4 | 1 |
| tr-g-21 | train | generated | corridor | 50000 | 203 | 20000 | 21,040 | 20,000 | 118 | 1.00 | 4 | 1 |
| tr-g-22 | train | generated | satellite | 20000 | 344 | 40000 | 14,320 | 40,000 | 57 | 1.00 | 4 | 1 |
| tr-g-23 | train | generated | grid | 20000 | 148 | 40000 | 20,960 | 40,000 | 86 | 0.97 | 4 | 2 |
| tr-g-24 | train | generated | satellite | 20000 | 198 | 20000 | 10,940 | 20,000 | 45 | 1.00 | 4 | 1 |
| tr-g-25 | train | generated | industry | 50000 | 179 | 40000 | 45,740 | 40,000 | 152 | 0.99 | 4 | 1 |
| tr-g-26 | train | generated | boom | 50000 | 229 | 20000 | 75,760 | 20,000 | 158 | 1.00 | 4 | 1 |
| tr-g-27 | train | generated | corridor | 100000 | 138 | 40000 | 30,420 | 40,000 | 131 | 1.00 | 4 | 2 |
| tr-g-28 | train | generated | corridor | 100000 | 289 | 5000 | 30,160 | 5,000 | 124 | 1.00 | 4 | 1 |
| tr-g-29 | train | generated | corridor | 100000 | 92 | 10000 | 33,520 | 10,000 | 131 | 1.00 | 4 | 1 |
| tr-g-30 | train | generated | grid | 50000 | 301 | 5000 | 31,800 | 5,000 | 148 | 1.00 | 4 | 1 |
| tr-g-31 | train | generated | boom | 50000 | 100 | 20000 | 38,500 | 20,000 | 148 | 1.00 | 4 | 1 |
| tr-g-32 | train | generated | boom | 50000 | 191 | 10000 | 65,680 | 10,000 | 151 | 1.00 | 4 | 1 |
| tr-g-33 | train | generated | transit | 100000 | 77 | 5000 | 41,920 | 5,000 | 190 | 1.00 | 4 | 1 |
| tr-g-34 | train | generated | boom | 100000 | 76 | 10000 | 55,880 | 10,000 | 195 | 0.98 | 3 | 1 |
| tr-g-35 | train | generated | transit | 100000 | 161 | 5000 | 135,240 | 5,000 | 298 | 1.00 | 4 | 1 |
| tr-g-36 | train | generated | transit | 150000 | 270 | 10000 | 158,820 | 10,000 | 440 | 1.00 | 4 | 1 |
| tr-g-37 | train | generated | transit | 150000 | 305 | 40000 | 161,780 | 40,000 | 431 | 1.00 | 4 | 1 |
| tr-g-38 | train | generated | boom | 100000 | 317 | 10000 | 81,160 | 10,000 | 256 | 0.99 | 4 | 1 |
| tr-g-39 | train | generated | transit | 150000 | 247 | 5000 | 151,340 | 5,000 | 300 | 1.00 | 4 | 1 |
| ho-g-00 | heldout | generated | grid | 20000 | 63 | 5000 | 9,320 | 5,000 | 81 | 0.96 | 1 | 10 |
| ho-g-01 | heldout | generated | industry | 20000 | 61 | 20000 | 9,800 | 20,000 | 68 | 1.00 | 1 | 7 |
| ho-g-02 | heldout | generated | satellite | 20000 | 131 | 40000 | 9,840 | 40,000 | 51 | 1.00 | 1 | 1 |
| ho-g-03 | heldout | generated | satellite | 20000 | 221 | 10000 | 8,420 | 10,000 | 53 | 0.96 | 1 | 1 |
| ho-g-04 | heldout | generated | satellite | 20000 | 60 | 40000 | 9,580 | 40,000 | 57 | 1.00 | 1 | 4 |
| ho-g-05 | heldout | generated | satellite | 20000 | 359 | 5000 | 4,540 | 5,000 | 51 | 1.00 | 1 | 1 |
| ho-g-06 | heldout | generated | satellite | 20000 | 277 | 10000 | 3,500 | 10,000 | 51 | 1.00 | 1 | 2 |
| ho-g-07 | heldout | generated | satellite | 20000 | 230 | 5000 | 5,280 | 5,000 | 45 | 1.00 | 1 | 10 |
| ho-g-08 | heldout | generated | satellite | 20000 | 106 | 5000 | 9,920 | 5,000 | 57 | 1.00 | 1 | 1 |
| ho-g-09 | heldout | generated | industry | 20000 | 64 | 40000 | 9,520 | 40,000 | 68 | 1.00 | 1 | 5 |
| ho-g-10 | heldout | generated | boom | 20000 | 79 | 20000 | 27,660 | 20,000 | 70 | 0.96 | 1 | 1 |
| ho-g-11 | heldout | generated | corridor | 50000 | 228 | 20000 | 27,680 | 20,000 | 149 | 1.00 | 1 | 1 |
| ho-g-12 | heldout | generated | grid | 50000 | 211 | 10000 | 27,840 | 10,000 | 141 | 1.00 | 1 | 1 |
| ho-g-13 | heldout | generated | boom | 20000 | 158 | 20000 | 21,980 | 20,000 | 69 | 0.96 | 1 | 1 |
| ho-g-14 | heldout | generated | frugal | 20000 | 327 | 10000 | 13,560 | 10,000 | 68 | 1.00 | 1 | 2 |
| ho-g-15 | heldout | generated | satellite | 20000 | 334 | 20000 | 18,680 | 20,000 | 57 | 1.00 | 1 | 1 |
| ho-g-16 | heldout | generated | frugal | 20000 | 249 | 40000 | 13,840 | 40,000 | 68 | 1.00 | 1 | 1 |
| ho-g-17 | heldout | generated | grid | 50000 | 215 | 10000 | 29,740 | 10,000 | 136 | 1.00 | 1 | 1 |
| ho-g-18 | heldout | generated | corridor | 50000 | 64 | 5000 | 18,800 | 5,000 | 105 | 1.00 | 1 | 1 |
| ho-g-19 | heldout | generated | transit | 20000 | 85 | 10000 | 27,840 | 10,000 | 72 | 1.00 | 1 | 1 |
| ho-g-20 | heldout | generated | corridor | 100000 | 231 | 5000 | 34,340 | 5,000 | 161 | 1.00 | 1 | 1 |
| ho-g-21 | heldout | generated | corridor | 50000 | 297 | 10000 | 32,460 | 10,000 | 131 | 1.00 | 1 | 1 |
| ho-g-22 | heldout | generated | transit | 50000 | 68 | 40000 | 31,920 | 40,000 | 148 | 0.98 | 1 | 1 |
| ho-g-23 | heldout | generated | transit | 100000 | 136 | 20000 | 70,960 | 20,000 | 285 | 1.00 | 1 | 1 |
| ho-g-24 | heldout | generated | transit | 100000 | 87 | 10000 | 53,220 | 10,000 | 210 | 1.00 | 1 | 1 |
| ho-g-25 | heldout | generated | transit | 50000 | 289 | 20000 | 77,340 | 20,000 | 179 | 0.99 | 1 | 1 |
| ho-g-26 | heldout | generated | grid | 100000 | 125 | 10000 | 35,760 | 10,000 | 135 | 0.99 | 1 | 1 |
| ho-g-27 | heldout | generated | corridor | 100000 | 309 | 20000 | 35,140 | 20,000 | 149 | 0.96 | 1 | 1 |
| ho-g-28 | heldout | generated | corridor | 50000 | 252 | 20000 | 30,000 | 20,000 | 132 | 1.00 | 1 | 1 |
| ho-g-29 | heldout | generated | grid | 100000 | 283 | 10000 | 33,080 | 10,000 | 147 | 1.00 | 1 | 2 |
| ho-g-30 | heldout | generated | boom | 100000 | 289 | 10000 | 158,920 | 10,000 | 311 | 1.00 | 1 | 1 |
| ho-g-31 | heldout | generated | boom | 150000 | 310 | 40000 | 129,940 | 40,000 | 285 | 1.00 | 1 | 1 |
| ho-g-32 | heldout | generated | boom | 150000 | 199 | 10000 | 124,560 | 10,000 | 397 | 1.00 | 1 | 1 |
| ho-g-33 | heldout | generated | boom | 100000 | 310 | 20000 | 111,340 | 20,000 | 282 | 1.00 | 1 | 1 |
| ho-g-34 | heldout | generated | boom | 150000 | 205 | 20000 | 136,680 | 20,000 | 418 | 1.00 | 1 | 1 |
| ho-g-35 | heldout | generated | transit | 100000 | 275 | 10000 | 152,480 | 10,000 | 308 | 0.99 | 1 | 1 |
| ho-g-36 | heldout | generated | transit | 150000 | 210 | 20000 | 168,060 | 20,000 | 397 | 1.00 | 1 | 1 |
| ho-g-37 | heldout | generated | boom | 100000 | 193 | 5000 | 132,720 | 5,000 | 283 | 1.00 | 1 | 1 |
| ho-g-38 | heldout | generated | transit | 100000 | 205 | 20000 | 125,620 | 20,000 | 292 | 1.00 | 1 | 1 |
| ho-g-39 | heldout | generated | boom | 100000 | 108 | 40000 | 87,560 | 40,000 | 275 | 1.00 | 1 | 1 |

## Population histogram by split (families; reference variant)

| split | 2k-10k | 10k-30k | 30k-80k | >80k |
|---|---|---|---|---|
| train | 15 | 15 | 15 | 15 |
| heldout | 10 | 10 | 10 | 10 |

## Population histogram by split (all start variants)

| split | 2k-10k | 10k-30k | 30k-80k | >80k |
|---|---|---|---|---|
| train | 52 | 78 | 54 | 44 |
| heldout | 10 | 10 | 10 | 10 |

Contact sheet: `results/families/contact_sheet.png`.
