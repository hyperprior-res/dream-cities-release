Fidelity on the development selection (decoding a, K = 8, 2000 transitions, 500 plans), pilot6_censored at 600,064 samples, model code ladder-v2. tag and fast: GPU 1, eval seed 2; plans per rollout batch: tag 32, tagc 32 (equal: the same random stream; different: another batch layout, so other draws). B3: results/fidelity/pilot6_censored (GPU 0, seeds 0 and 1); evaluation noise = |B3 seed 0 - B3 seed 1|.

| metric | tag (GPU 1) | fast (GPU 1) | abs(fast - tag) | B3 seed 0 | B3 seed 1 | evaluation noise | fast - tag within noise |
|---|---|---|---|---|---|---|---|
| tile structural F1, one month | 0.1461 | 0.1458 | 0.0004 | 0.1466 | 0.1462 | 0.0005 | yes |
| tile structural F1 since start, 12 months | 0.3428 | 0.3432 | 0.0004 | 0.3433 | 0.3431 | 0.0002 | NO |
| tile structural F1 since start, 24 months | 0.3163 | 0.3164 | 0.0001 | 0.3165 | 0.3165 | 0.0000 | NO |
| funds median rel. error, 12 months | 0.0385 | 0.0395 | 0.0010 | 0.0403 | 0.0402 | 0.0001 | NO |
| funds median rel. error, 24 months | 0.0598 | 0.0580 | 0.0019 | 0.0598 | 0.0576 | 0.0022 | yes |
| population median rel. error, 12 months | 0.0317 | 0.0323 | 0.0007 | 0.0309 | 0.0313 | 0.0004 | NO |
| population median rel. error, 24 months | 0.0582 | 0.0559 | 0.0023 | 0.0578 | 0.0570 | 0.0007 | NO |
| res_valve, one month from start (x copy) | 0.0935 | 0.0952 | 0.0017 | 0.0955 | 0.0961 | 0.0006 | NO |
| com_valve, one month from start (x copy) | 0.0919 | 0.0875 | 0.0044 | 0.0893 | 0.0919 | 0.0027 | NO |
| ind_valve, one month from start (x copy) | 0.0584 | 0.0581 | 0.0003 | 0.0582 | 0.0584 | 0.0002 | NO |
| score, one month from start (x copy) | 0.2288 | 0.2310 | 0.0022 | 0.2274 | 0.2263 | 0.0011 | NO |
| res_valve, 12 months (x copy) | 0.2796 | 0.2880 | 0.0084 | 0.2771 | 0.2792 | 0.0021 | NO |
| com_valve, 12 months (x copy) | 0.4018 | 0.4048 | 0.0030 | 0.4045 | 0.4057 | 0.0012 | NO |
| ind_valve, 12 months (x copy) | 0.3376 | 0.3411 | 0.0036 | 0.3260 | 0.3287 | 0.0028 | NO |
| res_valve, 24 months (x copy) | 0.3294 | 0.3356 | 0.0062 | 0.3264 | 0.3187 | 0.0077 | yes |
| com_valve, 24 months (x copy) | 0.5714 | 0.5681 | 0.0033 | 0.5827 | 0.5719 | 0.0108 | yes |
| ind_valve, 24 months (x copy) | 0.5874 | 0.5908 | 0.0035 | 0.5904 | 0.5732 | 0.0172 | yes |
| funds, one month on random transitions (MAE) | 54.3050 | 55.5680 | 1.2630 | 55.9535 | 58.9625 | 3.0090 | yes |
| mean ratio over scalars, 24 months | 0.4077 | 0.4080 | 0.0004 | 0.4080 | 0.4089 | 0.0009 | yes |

7 of 19 rows: abs(tagc - tag) <= evaluation noise. Seconds: tag 162.0, tagc 121.0 (one-step evaluation + rollouts).
