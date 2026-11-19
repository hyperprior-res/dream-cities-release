Fidelity on the development selection, decoding a, pilot6_censored at 600,064 samples (model code ladder-v2).
Columns 'tag' = variant tag, columns 'fast' = variant tagc (tag: the eager trunk, as eval_fidelity.py runs it; tagc: the tag's compiled trunk; fast: dc.fast).

Evaluations, tag: fidelity_dev/tag_seed0.json (batch 32); fidelity_dev/tag_seed1.json (batch 32); fidelity_dev/tag_seed2.json (batch 32); fidelity_dev/tag_seed3.json (batch 32)

Evaluations, fast: fidelity_dev/tagc_seed0.json (batch 32); fidelity_dev/tagc_seed1.json (batch 32); fidelity_dev/tagc_seed2.json (batch 32); fidelity_dev/tagc_seed3.json (batch 32)

| metric | tag mean | tag sd | n | fast mean | fast sd | n | fast - tag | 2 x SE | within |
|---|---|---|---|---|---|---|---|---|---|
| tile structural F1, one month | 0.1463 | 0.0007 | 4 | 0.1467 | 0.0006 | 4 | +0.0004 | 0.0010 | yes |
| tile structural F1 since start, 12 months | 0.3428 | 0.0002 | 4 | 0.3428 | 0.0003 | 4 | -0.0000 | 0.0004 | yes |
| tile structural F1 since start, 24 months | 0.3162 | 0.0004 | 4 | 0.3161 | 0.0002 | 4 | -0.0001 | 0.0004 | yes |
| funds median rel. error, 12 months | 0.0386 | 0.0003 | 4 | 0.0403 | 0.0012 | 4 | +0.0017 | 0.0012 | NO |
| funds median rel. error, 24 months | 0.0582 | 0.0012 | 4 | 0.0583 | 0.0023 | 4 | +0.0001 | 0.0025 | yes |
| population median rel. error, 12 months | 0.0318 | 0.0005 | 4 | 0.0318 | 0.0013 | 4 | +0.0001 | 0.0014 | yes |
| population median rel. error, 24 months | 0.0578 | 0.0005 | 4 | 0.0570 | 0.0012 | 4 | -0.0008 | 0.0013 | yes |
| res_valve, one month from start (x copy) | 0.0950 | 0.0018 | 4 | 0.0956 | 0.0008 | 4 | +0.0007 | 0.0020 | yes |
| com_valve, one month from start (x copy) | 0.0910 | 0.0023 | 4 | 0.0890 | 0.0045 | 4 | -0.0021 | 0.0050 | yes |
| ind_valve, one month from start (x copy) | 0.0591 | 0.0008 | 4 | 0.0581 | 0.0003 | 4 | -0.0010 | 0.0008 | NO |
| score, one month from start (x copy) | 0.2285 | 0.0012 | 4 | 0.2293 | 0.0019 | 4 | +0.0007 | 0.0022 | yes |
| res_valve, 12 months (x copy) | 0.2820 | 0.0043 | 4 | 0.2799 | 0.0057 | 4 | -0.0021 | 0.0072 | yes |
| com_valve, 12 months (x copy) | 0.4054 | 0.0056 | 4 | 0.4052 | 0.0027 | 4 | -0.0002 | 0.0062 | yes |
| ind_valve, 12 months (x copy) | 0.3313 | 0.0057 | 4 | 0.3345 | 0.0047 | 4 | +0.0033 | 0.0074 | yes |
| res_valve, 24 months (x copy) | 0.3275 | 0.0026 | 4 | 0.3238 | 0.0092 | 4 | -0.0037 | 0.0096 | yes |
| com_valve, 24 months (x copy) | 0.5786 | 0.0063 | 4 | 0.5755 | 0.0112 | 4 | -0.0032 | 0.0128 | yes |
| ind_valve, 24 months (x copy) | 0.5885 | 0.0051 | 4 | 0.5892 | 0.0103 | 4 | +0.0007 | 0.0115 | yes |
| funds, one month on random transitions (MAE) | 56.6229 | 4.2337 | 4 | 56.5514 | 4.9292 | 4 | -0.0715 | 6.4978 | yes |
| mean ratio over scalars, 24 months | 0.4097 | 0.0044 | 4 | 0.4084 | 0.0009 | 4 | -0.0013 | 0.0044 | yes |

17 of 19 rows within 2 standard errors (at 95 per cent per row about 1 of 19 falls outside by chance when the two are the same model).
