Fidelity on the development selection (decoding a, K = 8, 2000 transitions, 500 plans), pilot6_censored at 600,064 samples, model code ladder-v2. tag and fast: GPU 1, eval seed 3; plans per rollout batch: tag 32, tagc 32 (equal: the same random stream; different: another batch layout, so other draws). B3: results/fidelity/pilot6_censored (GPU 0, seeds 0 and 1); evaluation noise = |B3 seed 0 - B3 seed 1|.

| metric | tag (GPU 1) | fast (GPU 1) | abs(fast - tag) | B3 seed 0 | B3 seed 1 | evaluation noise | fast - tag within noise |
|---|---|---|---|---|---|---|---|
| tile structural F1, one month | 0.1465 | 0.1472 | 0.0008 | 0.1466 | 0.1462 | 0.0005 | NO |
| tile structural F1 since start, 12 months | 0.3430 | 0.3424 | 0.0006 | 0.3433 | 0.3431 | 0.0002 | NO |
| tile structural F1 since start, 24 months | 0.3165 | 0.3159 | 0.0007 | 0.3165 | 0.3165 | 0.0000 | NO |
| funds median rel. error, 12 months | 0.0391 | 0.0416 | 0.0026 | 0.0403 | 0.0402 | 0.0001 | NO |
| funds median rel. error, 24 months | 0.0571 | 0.0585 | 0.0014 | 0.0598 | 0.0576 | 0.0022 | yes |
| population median rel. error, 12 months | 0.0314 | 0.0301 | 0.0013 | 0.0309 | 0.0313 | 0.0004 | NO |
| population median rel. error, 24 months | 0.0572 | 0.0582 | 0.0010 | 0.0578 | 0.0570 | 0.0007 | NO |
| res_valve, one month from start (x copy) | 0.0959 | 0.0949 | 0.0010 | 0.0955 | 0.0961 | 0.0006 | NO |
| com_valve, one month from start (x copy) | 0.0935 | 0.0955 | 0.0020 | 0.0893 | 0.0919 | 0.0027 | yes |
| ind_valve, one month from start (x copy) | 0.0598 | 0.0585 | 0.0013 | 0.0582 | 0.0584 | 0.0002 | NO |
| score, one month from start (x copy) | 0.2273 | 0.2287 | 0.0014 | 0.2274 | 0.2263 | 0.0011 | NO |
| res_valve, 12 months (x copy) | 0.2778 | 0.2800 | 0.0022 | 0.2771 | 0.2792 | 0.0021 | NO |
| com_valve, 12 months (x copy) | 0.4038 | 0.4084 | 0.0046 | 0.4045 | 0.4057 | 0.0012 | NO |
| ind_valve, 12 months (x copy) | 0.3322 | 0.3318 | 0.0004 | 0.3260 | 0.3287 | 0.0028 | yes |
| res_valve, 24 months (x copy) | 0.3263 | 0.3136 | 0.0127 | 0.3264 | 0.3187 | 0.0077 | NO |
| com_valve, 24 months (x copy) | 0.5788 | 0.5829 | 0.0041 | 0.5827 | 0.5719 | 0.0108 | yes |
| ind_valve, 24 months (x copy) | 0.5864 | 0.5854 | 0.0009 | 0.5904 | 0.5732 | 0.0172 | yes |
| funds, one month on random transitions (MAE) | 53.8140 | 51.4955 | 2.3185 | 55.9535 | 58.9625 | 3.0090 | yes |
| mean ratio over scalars, 24 months | 0.4050 | 0.4091 | 0.0041 | 0.4080 | 0.4089 | 0.0009 | NO |

6 of 19 rows: abs(tagc - tag) <= evaluation noise. Seconds: tag 161.5, tagc 121.4 (one-step evaluation + rollouts).
