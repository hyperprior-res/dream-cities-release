# One-month errors per entry: noledger_50m_full_1step_samples_001200000_dec-b

Mean absolute error. Start states: the first month of the 500 held-out plans (K = 8 model samples).
Random transitions: the 2,000 held-out one-step transitions (engine floor re-seeded at month t).

| entry | start: model sample | start: mean of K | start: engine floor | start: copy | ratio sample/copy | random: T=1 | random: T=0 | random: engine floor | random: copy |
|---|---|---|---|---|---|---|---|---|---|
| res_valve | 92.72 | 48.91 | 2.02 | 55.45 | 1.672 | 89.17 | 38.75 | 1.76 | 56.63 |
| com_valve | 129.61 | 77.74 | 5.08 | 112.98 | 1.147 | 132.30 | 63.24 | 7.66 | 125.67 |
| ind_valve | 133.75 | 85.23 | 0.00 | 126.05 | 1.061 | 109.44 | 53.94 | 0.37 | 101.15 |
| score | 90.41 | 51.08 | 0.71 | 46.63 | 1.939 | 9.03 | 3.51 | 0.72 | 4.95 |
