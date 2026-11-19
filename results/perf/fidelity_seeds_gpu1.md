Fidelity on the development selection, decoding a, pilot6_censored at 600,064 samples (model code ladder-v2).
Columns 'tag' = variant tag, columns 'fast' = variant fast (tag: the eager trunk, as eval_fidelity.py runs it; tagc: the tag's compiled trunk; fast: dc.fast).

Evaluations, tag: fidelity_dev/tag_seed0.json (batch 32); fidelity_dev/tag_seed1.json (batch 32); fidelity_dev/tag_seed2.json (batch 32); fidelity_dev/tag_seed3.json (batch 32)

Evaluations, fast: fidelity_dev/fast_seed0.json (batch 32); fidelity_dev/fast_seed1.json (batch 32); fidelity_dev/fast_seed2.json (batch 32); fidelity_dev/fast_seed3.json (batch 32); fidelity_dev_b64/fast_seed0.json (batch 64)

| metric | tag mean | tag sd | n | fast mean | fast sd | n | fast - tag | 2 x SE | within |
|---|---|---|---|---|---|---|---|---|---|
| tile structural F1, one month | 0.1463 | 0.0007 | 4 | 0.1465 | 0.0005 | 5 | +0.0002 | 0.0009 | yes |
| tile structural F1 since start, 12 months | 0.3428 | 0.0002 | 4 | 0.3431 | 0.0005 | 5 | +0.0002 | 0.0005 | yes |
| tile structural F1 since start, 24 months | 0.3162 | 0.0004 | 4 | 0.3164 | 0.0004 | 5 | +0.0002 | 0.0005 | yes |
| funds median rel. error, 12 months | 0.0386 | 0.0003 | 4 | 0.0397 | 0.0011 | 5 | +0.0010 | 0.0010 | yes |
| funds median rel. error, 24 months | 0.0582 | 0.0012 | 4 | 0.0573 | 0.0015 | 5 | -0.0009 | 0.0018 | yes |
| population median rel. error, 12 months | 0.0318 | 0.0005 | 4 | 0.0317 | 0.0007 | 5 | -0.0001 | 0.0008 | yes |
| population median rel. error, 24 months | 0.0578 | 0.0005 | 4 | 0.0573 | 0.0010 | 5 | -0.0005 | 0.0010 | yes |
| res_valve, one month from start (x copy) | 0.0950 | 0.0018 | 4 | 0.0953 | 0.0022 | 5 | +0.0003 | 0.0027 | yes |
| com_valve, one month from start (x copy) | 0.0910 | 0.0023 | 4 | 0.0902 | 0.0039 | 5 | -0.0009 | 0.0042 | yes |
| ind_valve, one month from start (x copy) | 0.0591 | 0.0008 | 4 | 0.0579 | 0.0005 | 5 | -0.0012 | 0.0009 | NO |
| score, one month from start (x copy) | 0.2285 | 0.0012 | 4 | 0.2295 | 0.0013 | 5 | +0.0009 | 0.0017 | yes |
| res_valve, 12 months (x copy) | 0.2820 | 0.0043 | 4 | 0.2795 | 0.0030 | 5 | -0.0025 | 0.0051 | yes |
| com_valve, 12 months (x copy) | 0.4054 | 0.0056 | 4 | 0.4015 | 0.0036 | 5 | -0.0038 | 0.0065 | yes |
| ind_valve, 12 months (x copy) | 0.3313 | 0.0057 | 4 | 0.3268 | 0.0050 | 5 | -0.0044 | 0.0073 | yes |
| res_valve, 24 months (x copy) | 0.3275 | 0.0026 | 4 | 0.3238 | 0.0048 | 5 | -0.0037 | 0.0050 | yes |
| com_valve, 24 months (x copy) | 0.5786 | 0.0063 | 4 | 0.5739 | 0.0063 | 5 | -0.0048 | 0.0084 | yes |
| ind_valve, 24 months (x copy) | 0.5885 | 0.0051 | 4 | 0.5869 | 0.0043 | 5 | -0.0016 | 0.0064 | yes |
| funds, one month on random transitions (MAE) | 56.6229 | 4.2337 | 4 | 57.8300 | 4.6083 | 5 | +1.2071 | 5.9088 | yes |
| mean ratio over scalars, 24 months | 0.4097 | 0.0044 | 4 | 0.4092 | 0.0022 | 5 | -0.0005 | 0.0048 | yes |

18 of 19 rows within 2 standard errors (at 95 per cent per row about 1 of 19 falls outside by chance when the two are the same model).
