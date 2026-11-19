# One-month errors per entry: noledger_50m_full_1step_samples_003600000_dec-b

Mean absolute error. Start states: the first month of the 500 held-out plans (K = 8 model samples).
Random transitions: the 2,000 held-out one-step transitions (engine floor re-seeded at month t).

| entry | start: model sample | start: mean of K | start: engine floor | start: copy | ratio sample/copy | random: T=1 | random: T=0 | random: engine floor | random: copy |
|---|---|---|---|---|---|---|---|---|---|
| res_valve | 45.38 | 24.53 | 2.02 | 55.45 | 0.818 | 45.50 | 18.25 | 1.76 | 56.63 |
| com_valve | 62.08 | 34.18 | 5.08 | 112.98 | 0.549 | 61.97 | 26.36 | 7.66 | 125.67 |
| ind_valve | 61.46 | 35.33 | 0.00 | 126.05 | 0.488 | 53.03 | 22.15 | 0.37 | 101.15 |
| score | 61.03 | 38.02 | 0.71 | 46.63 | 1.309 | 5.31 | 2.41 | 0.72 | 4.95 |
