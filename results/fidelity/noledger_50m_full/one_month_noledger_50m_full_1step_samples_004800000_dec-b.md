# One-month errors per entry: noledger_50m_full_1step_samples_004800000_dec-b

Mean absolute error. Start states: the first month of the 500 held-out plans (K = 8 model samples).
Random transitions: the 2,000 held-out one-step transitions (engine floor re-seeded at month t).

| entry | start: model sample | start: mean of K | start: engine floor | start: copy | ratio sample/copy | random: T=1 | random: T=0 | random: engine floor | random: copy |
|---|---|---|---|---|---|---|---|---|---|
| res_valve | 31.48 | 17.56 | 2.02 | 55.45 | 0.568 | 35.77 | 16.42 | 1.76 | 56.63 |
| com_valve | 45.51 | 28.40 | 5.08 | 112.98 | 0.403 | 47.13 | 23.50 | 7.66 | 125.67 |
| ind_valve | 44.66 | 27.98 | 0.00 | 126.05 | 0.354 | 40.59 | 20.42 | 0.37 | 101.15 |
| score | 45.70 | 30.86 | 0.71 | 46.63 | 0.980 | 4.04 | 2.05 | 0.72 | 4.95 |
