# One-month errors per entry: noledger_50m_full_1step_samples_002400000_dec-b

Mean absolute error. Start states: the first month of the 500 held-out plans (K = 8 model samples).
Random transitions: the 2,000 held-out one-step transitions (engine floor re-seeded at month t).

| entry | start: model sample | start: mean of K | start: engine floor | start: copy | ratio sample/copy | random: T=1 | random: T=0 | random: engine floor | random: copy |
|---|---|---|---|---|---|---|---|---|---|
| res_valve | 59.78 | 27.14 | 2.02 | 55.45 | 1.078 | 60.79 | 21.96 | 1.76 | 56.63 |
| com_valve | 85.11 | 44.21 | 5.08 | 112.98 | 0.753 | 84.39 | 32.98 | 7.66 | 125.67 |
| ind_valve | 89.36 | 48.90 | 0.00 | 126.05 | 0.709 | 74.18 | 26.12 | 0.37 | 101.15 |
| score | 75.57 | 42.73 | 0.71 | 46.63 | 1.621 | 7.72 | 3.38 | 0.72 | 4.95 |
