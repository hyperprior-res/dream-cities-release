Fidelity on the development selection, decoding a, pilot6_censored at 600,064 samples (model code ladder-v2).
Columns 'tag' = variant tagc, columns 'fast' = variant fast (tag: the eager trunk, as eval_fidelity.py runs it; tagc: the tag's compiled trunk; fast: dc.fast).

Evaluations, tag: fidelity_dev/tagc_seed0.json (batch 32); fidelity_dev/tagc_seed1.json (batch 32); fidelity_dev/tagc_seed2.json (batch 32); fidelity_dev/tagc_seed3.json (batch 32)

Evaluations, fast: fidelity_dev/fast_seed0.json (batch 32); fidelity_dev/fast_seed1.json (batch 32); fidelity_dev/fast_seed2.json (batch 32); fidelity_dev/fast_seed3.json (batch 32); fidelity_dev_b64/fast_seed0.json (batch 64)

| metric | tag mean | tag sd | n | fast mean | fast sd | n | fast - tag | 2 x SE | within |
|---|---|---|---|---|---|---|---|---|---|
| tile structural F1, one month | 0.1467 | 0.0006 | 4 | 0.1465 | 0.0005 | 5 | -0.0002 | 0.0008 | yes |
| tile structural F1 since start, 12 months | 0.3428 | 0.0003 | 4 | 0.3431 | 0.0005 | 5 | +0.0002 | 0.0006 | yes |
| tile structural F1 since start, 24 months | 0.3161 | 0.0002 | 4 | 0.3164 | 0.0004 | 5 | +0.0003 | 0.0004 | yes |
| funds median rel. error, 12 months | 0.0403 | 0.0012 | 4 | 0.0397 | 0.0011 | 5 | -0.0006 | 0.0015 | yes |
| funds median rel. error, 24 months | 0.0583 | 0.0023 | 4 | 0.0573 | 0.0015 | 5 | -0.0011 | 0.0026 | yes |
| population median rel. error, 12 months | 0.0318 | 0.0013 | 4 | 0.0317 | 0.0007 | 5 | -0.0002 | 0.0014 | yes |
| population median rel. error, 24 months | 0.0570 | 0.0012 | 4 | 0.0573 | 0.0010 | 5 | +0.0003 | 0.0015 | yes |
| res_valve, one month from start (x copy) | 0.0956 | 0.0008 | 4 | 0.0953 | 0.0022 | 5 | -0.0004 | 0.0021 | yes |
| com_valve, one month from start (x copy) | 0.0890 | 0.0045 | 4 | 0.0902 | 0.0039 | 5 | +0.0012 | 0.0057 | yes |
| ind_valve, one month from start (x copy) | 0.0581 | 0.0003 | 4 | 0.0579 | 0.0005 | 5 | -0.0002 | 0.0006 | yes |
| score, one month from start (x copy) | 0.2293 | 0.0019 | 4 | 0.2295 | 0.0013 | 5 | +0.0002 | 0.0023 | yes |
| res_valve, 12 months (x copy) | 0.2799 | 0.0057 | 4 | 0.2795 | 0.0030 | 5 | -0.0004 | 0.0064 | yes |
| com_valve, 12 months (x copy) | 0.4052 | 0.0027 | 4 | 0.4015 | 0.0036 | 5 | -0.0037 | 0.0042 | yes |
| ind_valve, 12 months (x copy) | 0.3345 | 0.0047 | 4 | 0.3268 | 0.0050 | 5 | -0.0077 | 0.0065 | NO |
| res_valve, 24 months (x copy) | 0.3238 | 0.0092 | 4 | 0.3238 | 0.0048 | 5 | +0.0000 | 0.0102 | yes |
| com_valve, 24 months (x copy) | 0.5755 | 0.0112 | 4 | 0.5739 | 0.0063 | 5 | -0.0016 | 0.0125 | yes |
| ind_valve, 24 months (x copy) | 0.5892 | 0.0103 | 4 | 0.5869 | 0.0043 | 5 | -0.0023 | 0.0110 | yes |
| funds, one month on random transitions (MAE) | 56.5514 | 4.9292 | 4 | 57.8300 | 4.6083 | 5 | +1.2786 | 6.4254 | yes |
| mean ratio over scalars, 24 months | 0.4084 | 0.0009 | 4 | 0.4092 | 0.0022 | 5 | +0.0007 | 0.0022 | yes |

18 of 19 rows within 2 standard errors (at 95 per cent per row about 1 of 19 falls outside by chance when the two are the same model).
