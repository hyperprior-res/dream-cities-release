Fidelity on the development selection, decoding a, pilot6_censored at 600,064 samples (model code ladder-v2).
Columns 'tag' = variant tag and B3, columns 'fast' = variant fast (tag: the eager trunk, as eval_fidelity.py runs it; tagc: the tag's compiled trunk; fast: dc.fast).

Evaluations, tag: fidelity_dev/tag_seed0.json (batch 32); fidelity_dev/tag_seed1.json (batch 32); fidelity_dev/tag_seed2.json (batch 32); fidelity_dev/tag_seed3.json (batch 32); B3 dev; B3 dev_noise_seed1

Evaluations, fast: fidelity_dev/fast_seed0.json (batch 32); fidelity_dev/fast_seed1.json (batch 32); fidelity_dev/fast_seed2.json (batch 32); fidelity_dev/fast_seed3.json (batch 32); fidelity_dev_b64/fast_seed0.json (batch 64)

| metric | tag mean | tag sd | n | fast mean | fast sd | n | fast - tag | 2 x SE | within |
|---|---|---|---|---|---|---|---|---|---|
| tile structural F1, one month | 0.1463 | 0.0006 | 6 | 0.1465 | 0.0005 | 5 | +0.0002 | 0.0007 | yes |
| tile structural F1 since start, 12 months | 0.3430 | 0.0002 | 6 | 0.3431 | 0.0005 | 5 | +0.0001 | 0.0005 | yes |
| tile structural F1 since start, 24 months | 0.3163 | 0.0003 | 6 | 0.3164 | 0.0004 | 5 | +0.0001 | 0.0004 | yes |
| funds median rel. error, 12 months | 0.0392 | 0.0008 | 6 | 0.0397 | 0.0011 | 5 | +0.0005 | 0.0012 | yes |
| funds median rel. error, 24 months | 0.0584 | 0.0012 | 6 | 0.0573 | 0.0015 | 5 | -0.0011 | 0.0017 | yes |
| population median rel. error, 12 months | 0.0315 | 0.0005 | 6 | 0.0317 | 0.0007 | 5 | +0.0001 | 0.0008 | yes |
| population median rel. error, 24 months | 0.0576 | 0.0005 | 6 | 0.0573 | 0.0010 | 5 | -0.0004 | 0.0010 | yes |
| res_valve, one month from start (x copy) | 0.0952 | 0.0015 | 6 | 0.0953 | 0.0022 | 5 | +0.0000 | 0.0023 | yes |
| com_valve, one month from start (x copy) | 0.0909 | 0.0020 | 6 | 0.0902 | 0.0039 | 5 | -0.0007 | 0.0039 | yes |
| ind_valve, one month from start (x copy) | 0.0589 | 0.0007 | 6 | 0.0579 | 0.0005 | 5 | -0.0010 | 0.0008 | NO |
| score, one month from start (x copy) | 0.2280 | 0.0013 | 6 | 0.2295 | 0.0013 | 5 | +0.0015 | 0.0016 | yes |
| res_valve, 12 months (x copy) | 0.2807 | 0.0039 | 6 | 0.2795 | 0.0030 | 5 | -0.0012 | 0.0042 | yes |
| com_valve, 12 months (x copy) | 0.4053 | 0.0043 | 6 | 0.4015 | 0.0036 | 5 | -0.0037 | 0.0048 | yes |
| ind_valve, 12 months (x copy) | 0.3300 | 0.0050 | 6 | 0.3268 | 0.0050 | 5 | -0.0031 | 0.0060 | yes |
| res_valve, 24 months (x copy) | 0.3258 | 0.0040 | 6 | 0.3238 | 0.0048 | 5 | -0.0020 | 0.0055 | yes |
| com_valve, 24 months (x copy) | 0.5782 | 0.0060 | 6 | 0.5739 | 0.0063 | 5 | -0.0043 | 0.0074 | yes |
| ind_valve, 24 months (x copy) | 0.5863 | 0.0076 | 6 | 0.5869 | 0.0043 | 5 | +0.0006 | 0.0073 | yes |
| funds, one month on random transitions (MAE) | 56.9012 | 3.4418 | 6 | 57.8300 | 4.6083 | 5 | +0.9288 | 4.9886 | yes |
| mean ratio over scalars, 24 months | 0.4093 | 0.0034 | 6 | 0.4092 | 0.0022 | 5 | -0.0001 | 0.0034 | yes |

18 of 19 rows within 2 standard errors (at 95 per cent per row about 1 of 19 falls outside by chance when the two are the same model).
