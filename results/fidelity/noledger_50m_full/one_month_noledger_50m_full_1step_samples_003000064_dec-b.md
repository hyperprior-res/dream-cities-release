# One-month errors per entry: noledger_50m_full_1step_samples_003000064_dec-b

Mean absolute error. Start states: the first month of the 500 held-out plans (K = 8 model samples).
Random transitions: the 2,000 held-out one-step transitions (engine floor re-seeded at month t).

| entry | start: model sample | start: mean of K | start: engine floor | start: copy | ratio sample/copy | random: T=1 | random: T=0 | random: engine floor | random: copy |
|---|---|---|---|---|---|---|---|---|---|
| res_valve | 52.69 | 26.61 | 2.02 | 55.45 | 0.950 | 50.45 | 19.41 | 1.76 | 56.63 |
| com_valve | 69.42 | 38.72 | 5.08 | 112.98 | 0.614 | 70.83 | 27.89 | 7.66 | 125.67 |
| ind_valve | 69.42 | 37.78 | 0.00 | 126.05 | 0.551 | 59.83 | 23.84 | 0.37 | 101.15 |
| score | 69.44 | 40.71 | 0.71 | 46.63 | 1.489 | 6.12 | 3.03 | 0.72 | 4.95 |
