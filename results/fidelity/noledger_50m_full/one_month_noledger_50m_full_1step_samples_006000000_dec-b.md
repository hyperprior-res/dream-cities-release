# One-month errors per entry: noledger_50m_full_1step_samples_006000000_dec-b

Mean absolute error. Start states: the first month of the 500 held-out plans (K = 8 model samples).
Random transitions: the 2,000 held-out one-step transitions (engine floor re-seeded at month t).

| entry | start: model sample | start: mean of K | start: engine floor | start: copy | ratio sample/copy | random: T=1 | random: T=0 | random: engine floor | random: copy |
|---|---|---|---|---|---|---|---|---|---|
| res_valve | 25.16 | 15.11 | 2.02 | 55.45 | 0.454 | 32.02 | 17.22 | 1.76 | 56.63 |
| com_valve | 37.80 | 25.13 | 5.08 | 112.98 | 0.335 | 43.57 | 23.02 | 7.66 | 125.67 |
| ind_valve | 39.06 | 25.50 | 0.00 | 126.05 | 0.310 | 36.19 | 20.13 | 0.37 | 101.15 |
| score | 40.09 | 29.23 | 0.71 | 46.63 | 0.860 | 3.29 | 1.84 | 0.72 | 4.95 |
