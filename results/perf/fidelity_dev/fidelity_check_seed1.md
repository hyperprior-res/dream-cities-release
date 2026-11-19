Fidelity on the development selection (decoding a, K = 8, 2000 transitions, 500 plans), pilot6_censored at 600,064 samples, model code ladder-v2. tag and fast: GPU 1, eval seed 1; plans per rollout batch: tag 32, tagc 32 (equal: the same random stream; different: another batch layout, so other draws). B3: results/fidelity/pilot6_censored (GPU 0, seeds 0 and 1); evaluation noise = |B3 seed 0 - B3 seed 1|.

| metric | tag (GPU 1) | fast (GPU 1) | abs(fast - tag) | B3 seed 0 | B3 seed 1 | evaluation noise | fast - tag within noise |
|---|---|---|---|---|---|---|---|
| tile structural F1, one month | 0.1472 | 0.1470 | 0.0002 | 0.1466 | 0.1462 | 0.0005 | yes |
| tile structural F1 since start, 12 months | 0.3426 | 0.3430 | 0.0004 | 0.3433 | 0.3431 | 0.0002 | NO |
| tile structural F1 since start, 24 months | 0.3157 | 0.3162 | 0.0005 | 0.3165 | 0.3165 | 0.0000 | NO |
| funds median rel. error, 12 months | 0.0384 | 0.0410 | 0.0026 | 0.0403 | 0.0402 | 0.0001 | NO |
| funds median rel. error, 24 months | 0.0578 | 0.0612 | 0.0034 | 0.0598 | 0.0576 | 0.0022 | NO |
| population median rel. error, 12 months | 0.0315 | 0.0319 | 0.0004 | 0.0309 | 0.0313 | 0.0004 | NO |
| population median rel. error, 24 months | 0.0582 | 0.0578 | 0.0004 | 0.0578 | 0.0570 | 0.0007 | yes |
| res_valve, one month from start (x copy) | 0.0971 | 0.0957 | 0.0014 | 0.0955 | 0.0961 | 0.0006 | NO |
| com_valve, one month from start (x copy) | 0.0880 | 0.0854 | 0.0027 | 0.0893 | 0.0919 | 0.0027 | NO |
| ind_valve, one month from start (x copy) | 0.0585 | 0.0577 | 0.0008 | 0.0582 | 0.0584 | 0.0002 | NO |
| score, one month from start (x copy) | 0.2300 | 0.2306 | 0.0006 | 0.2274 | 0.2263 | 0.0011 | yes |
| res_valve, 12 months (x copy) | 0.2832 | 0.2761 | 0.0072 | 0.2771 | 0.2792 | 0.0021 | NO |
| com_valve, 12 months (x copy) | 0.4023 | 0.4058 | 0.0036 | 0.4045 | 0.4057 | 0.0012 | NO |
| ind_valve, 12 months (x copy) | 0.3317 | 0.3306 | 0.0011 | 0.3260 | 0.3287 | 0.0028 | yes |
| res_valve, 24 months (x copy) | 0.3298 | 0.3204 | 0.0094 | 0.3264 | 0.3187 | 0.0077 | NO |
| com_valve, 24 months (x copy) | 0.5868 | 0.5639 | 0.0229 | 0.5827 | 0.5719 | 0.0108 | NO |
| ind_valve, 24 months (x copy) | 0.5959 | 0.6025 | 0.0066 | 0.5904 | 0.5732 | 0.0172 | yes |
| funds, one month on random transitions (MAE) | 55.4870 | 55.8210 | 0.3340 | 55.9535 | 58.9625 | 3.0090 | yes |
| mean ratio over scalars, 24 months | 0.4150 | 0.4074 | 0.0077 | 0.4080 | 0.4089 | 0.0009 | NO |

6 of 19 rows: abs(tagc - tag) <= evaluation noise. Seconds: tag 162.6, tagc 121.9 (one-step evaluation + rollouts).
