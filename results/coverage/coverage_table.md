# B20 coverage table (counts from the files; no engine, no model)

Share of *building* months (at least one macro) at each tax setting, per source. Last rows: summaries over all months.

| tax | train_full, all months | train_full, builder trajectories | train_cov, all months | train_cov2, all months | union train_full + train_cov + train_cov2 | selected plans, all methods | selected plans, random B=1000 | frontier plans |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.018 | 0.002 | 0.066 | 0.256 | 0.070 | 0.012 | 0.063 | 0.310 |
| 1 | 0.013 | 0.002 | 0.064 | 0.140 | 0.044 | 0.014 | 0.022 | 0.131 |
| 2 | 0.013 | 0.002 | 0.060 | 0.092 | 0.035 | 0.017 | 0.018 | 0.078 |
| 3 | 0.013 | 0.002 | 0.062 | 0.072 | 0.031 | 0.025 | 0.006 | 0.058 |
| 4 | 0.011 | 0.000 | 0.060 | 0.043 | 0.024 | 0.037 | 0.001 | 0.067 |
| 5 | 0.039 | 0.052 | 0.059 | 0.039 | 0.042 | 0.120 | 0.250 | 0.082 |
| 6 | 0.208 | 0.291 | 0.056 | 0.090 | 0.165 | 0.258 | 0.371 | 0.110 |
| 7 | 0.254 | 0.327 | 0.060 | 0.139 | 0.205 | 0.199 | 0.124 | 0.083 |
| 8 | 0.265 | 0.278 | 0.055 | 0.099 | 0.204 | 0.166 | 0.128 | 0.074 |
| 9 | 0.037 | 0.036 | 0.058 | 0.024 | 0.038 | 0.062 | 0.002 | 0.004 |
| 10 | 0.010 | 0.000 | 0.047 | 0.001 | 0.014 | 0.035 | 0.000 | 0.000 |
| 11 | 0.011 | 0.000 | 0.044 | 0.003 | 0.014 | 0.022 | 0.000 | 0.000 |
| 12 | 0.011 | 0.000 | 0.039 | 0.000 | 0.013 | 0.013 | 0.000 | 0.000 |
| 13 | 0.011 | 0.000 | 0.039 | 0.000 | 0.013 | 0.007 | 0.000 | 0.000 |
| 14 | 0.011 | 0.000 | 0.035 | 0.000 | 0.012 | 0.004 | 0.000 | 0.000 |
| 15 | 0.012 | 0.001 | 0.035 | 0.000 | 0.013 | 0.002 | 0.000 | 0.000 |
| 16 | 0.012 | 0.001 | 0.034 | 0.000 | 0.013 | 0.002 | 0.001 | 0.000 |
| 17 | 0.012 | 0.001 | 0.032 | 0.000 | 0.013 | 0.001 | 0.002 | 0.003 |
| 18 | 0.012 | 0.001 | 0.033 | 0.002 | 0.013 | 0.002 | 0.002 | 0.000 |
| 19 | 0.012 | 0.001 | 0.032 | 0.000 | 0.013 | 0.002 | 0.001 | 0.000 |
| 20 | 0.013 | 0.001 | 0.031 | 0.000 | 0.013 | 0.001 | 0.005 | 0.000 |
| **building months** | 731,820 | 258,262 | 154,367 | 204,582 | 1,090,769 | 32,139 | 2,033 | 3,059 |
| **all months** | 3,000,000 | 1,633,560 | 600,000 | 600,000 | 4,200,000 | 61,416 | 4,632 | 4,632 |
| share of months that build | 0.244 | 0.158 | 0.257 | 0.341 | 0.260 | 0.523 | 0.439 | 0.660 |
| building months at tax <= 4 (share of building months) | 0.069 | 0.009 | 0.311 | 0.603 | 0.204 | 0.105 | 0.111 | 0.644 |
| building months at tax <= 4 with a funding cut (share of building months) | 0.057 | 0.000 | 0.308 | 0.603 | 0.195 | 0.087 | 0.086 | 0.638 |
| building months with any funding line below 100 % | 0.251 | 0.025 | 0.992 | 1.000 | 0.496 | 0.453 | 0.126 | 0.851 |
| building months with all funding at 0 | 0.002 | 0.000 | 0.009 | 0.336 | 0.066 | 0.000 | 0.000 | 0.441 |
| building months at tax <= 4 with all funding at 0 (count) | 314 | 0 | 420 | 41,519 | 42,253 | 0 | 0 | 1,126 |
| the same, share of building months | 0.000 | 0.000 | 0.003 | 0.203 | 0.039 | 0.000 | 0.000 | 0.368 |
| all months at tax <= 4 | 0.063 | 0.010 | 0.242 | 0.614 | 0.167 | 0.102 | 0.212 | 0.666 |

Forced earthquakes (transitions at or after a forced earthquake in their trajectory, event month included):

- train_full: 72,864 of 3,000,000 transitions; 1,858 trajectories with one (35 in month 0)
- train_cov: 0 of 600,000 transitions; 0 trajectories with one (0 in month 0)
- train_cov2: 120,000 of 600,000 transitions; 5,000 trajectories with one (5,000 in month 0)
- union train_full + train_cov + train_cov2: 192,864 of 4,200,000 transitions

Share of *non-building* months at each tax setting is in the JSON (`tax_counts_not_building`).

By method and budget (selected plans): building months at tax <= 4 / share of months that build

- best_of_n|B1 (99 plans): 0.000 / 0.344
- best_of_n|B10 (99 plans): 0.000 / 0.448
- best_of_n|B100 (99 plans): 0.000 / 0.462
- best_of_n|B1000 (99 plans): 0.000 / 0.458
- cem|B1 (193 plans): 0.161 / 0.742
- cem|B10 (193 plans): 0.134 / 0.814
- cem|B100 (193 plans): 0.159 / 0.880
- cem|B1000 (193 plans): 0.229 / 0.894
- random_verdict|B1 (193 plans): 0.091 / 0.255
- random_verdict|B10 (193 plans): 0.027 / 0.387
- random_verdict|B100 (193 plans): 0.031 / 0.408
- random_verdict|B1000 (40 plans): 0.033 / 0.436
- random|B1 (193 plans): 0.091 / 0.255
- random|B10 (193 plans): 0.034 / 0.440
- random|B100 (193 plans): 0.044 / 0.456
- random|B1000 (193 plans): 0.111 / 0.439

By task (frontier plans): building months at tax <= 4 / share of months that build

- grow (40 plans): 0.899 / 0.639
- solvent (38 plans): 0.892 / 0.589
- treasury (40 plans): 0.203 / 0.760
- recover (35 plans): 0.847 / 0.662
- power (40 plans): 0.514 / 0.649
