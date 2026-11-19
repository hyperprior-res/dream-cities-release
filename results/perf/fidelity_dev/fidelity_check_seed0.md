Fidelity on the development selection (decoding a, K = 8, 2000 transitions, 500 plans), pilot6_censored at 600,064 samples, model code ladder-v2. tag and fast: GPU 1, eval seed 0; plans per rollout batch: tag 32, tagc 32 (equal: the same random stream; different: another batch layout, so other draws). B3: results/fidelity/pilot6_censored (GPU 0, seeds 0 and 1); evaluation noise = |B3 seed 0 - B3 seed 1|.

| metric | tag (GPU 1) | fast (GPU 1) | abs(fast - tag) | B3 seed 0 | B3 seed 1 | evaluation noise | fast - tag within noise |
|---|---|---|---|---|---|---|---|
| tile structural F1, one month | 0.1454 | 0.1466 | 0.0012 | 0.1466 | 0.1462 | 0.0005 | NO |
| tile structural F1 since start, 12 months | 0.3431 | 0.3428 | 0.0003 | 0.3433 | 0.3431 | 0.0002 | NO |
| tile structural F1 since start, 24 months | 0.3164 | 0.3162 | 0.0002 | 0.3165 | 0.3165 | 0.0000 | NO |
| funds median rel. error, 12 months | 0.0387 | 0.0391 | 0.0005 | 0.0403 | 0.0402 | 0.0001 | NO |
| funds median rel. error, 24 months | 0.0581 | 0.0557 | 0.0024 | 0.0598 | 0.0576 | 0.0022 | NO |
| population median rel. error, 12 months | 0.0325 | 0.0331 | 0.0005 | 0.0309 | 0.0313 | 0.0004 | NO |
| population median rel. error, 24 months | 0.0574 | 0.0561 | 0.0013 | 0.0578 | 0.0570 | 0.0007 | NO |
| res_valve, one month from start (x copy) | 0.0934 | 0.0967 | 0.0033 | 0.0955 | 0.0961 | 0.0006 | NO |
| com_valve, one month from start (x copy) | 0.0908 | 0.0876 | 0.0032 | 0.0893 | 0.0919 | 0.0027 | NO |
| ind_valve, one month from start (x copy) | 0.0598 | 0.0580 | 0.0017 | 0.0582 | 0.0584 | 0.0002 | NO |
| score, one month from start (x copy) | 0.2280 | 0.2268 | 0.0012 | 0.2274 | 0.2263 | 0.0011 | NO |
| res_valve, 12 months (x copy) | 0.2875 | 0.2756 | 0.0118 | 0.2771 | 0.2792 | 0.0021 | NO |
| com_valve, 12 months (x copy) | 0.4137 | 0.4018 | 0.0118 | 0.4045 | 0.4057 | 0.0012 | NO |
| ind_valve, 12 months (x copy) | 0.3236 | 0.3346 | 0.0110 | 0.3260 | 0.3287 | 0.0028 | NO |
| res_valve, 24 months (x copy) | 0.3244 | 0.3255 | 0.0011 | 0.3264 | 0.3187 | 0.0077 | yes |
| com_valve, 24 months (x copy) | 0.5775 | 0.5869 | 0.0094 | 0.5827 | 0.5719 | 0.0108 | yes |
| ind_valve, 24 months (x copy) | 0.5844 | 0.5779 | 0.0065 | 0.5904 | 0.5732 | 0.0172 | yes |
| funds, one month on random transitions (MAE) | 62.8855 | 63.3210 | 0.4355 | 55.9535 | 58.9625 | 3.0090 | yes |
| mean ratio over scalars, 24 months | 0.4111 | 0.4093 | 0.0018 | 0.4080 | 0.4089 | 0.0009 | NO |

4 of 19 rows: abs(tagc - tag) <= evaluation noise. Seconds: tag 165.7, tagc 133.3 (one-step evaluation + rollouts).
