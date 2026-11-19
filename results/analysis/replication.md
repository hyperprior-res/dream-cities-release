# The main checkpoint's headline on three city sets (COMPLETE)

Checkpoint `os_50m_full-samples_006000000`. Random search and the pool-seeded search at each budget, on the 40 cities, the 80 new cities and all 120 cities, each beside the same search in a perfect emulator (the engine judging itself on fresh seeds) on the same instances. Cluster bootstrap over start-state families, 2000 resamples, seed 0, BCa 95 per cent intervals (`hpr_dream.stats`, as the audit's reference tables); `*` the percentile interval where BCa is undefined; `†` no event, the exact one-sided bound on clusters. Generated 2026-11-14T15:54:19Z by `PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/analyse_ladder.py`.

**Statement (complete).** Pool-seeded search at 1,000, 80 new cities: the difference from the perfect emulator's BCa interval [+0.032, +0.138] excludes 0. The 40-city point estimate +0.114 lies inside the 80-city interval.

## Random search

| B | cities | n | false acceptance, emulator | false acceptance, perfect | difference | real success, emulator | real success, perfect | false rejection, emulator | false rejection, perfect |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 120 | 574 | 0.092 [0.071, 0.121] | 0.016 [0.007, 0.032] | +0.077 [+0.052, +0.105] | 0.052 [0.033, 0.084] | 0.052 [0.033, 0.084] | 0.533 [0.333, 0.731] | 0.100 [0.025, 0.259] |
| 1 | 40 | 193 | 0.083 [0.051, 0.123] | 0.021 [0.005, 0.046] | +0.062 [+0.026, +0.103] | 0.031 [0.010, 0.078] | 0.031 [0.010, 0.078] | 0.500 [0.000, 1.000] | 0.167 [0.000, 0.600] |
| 1 | 80 | 381 | 0.097 [0.069, 0.133] | 0.013 [0.005, 0.034] | +0.084 [+0.053, +0.120] | 0.063 [0.037, 0.108] | 0.063 [0.037, 0.108] | 0.542 [0.333, 0.772] | 0.083 [0.000, 0.292] |
| 10 | 120 | 574 | 0.138 [0.114, 0.163] | 0.040 [0.025, 0.058] | +0.098 [+0.069, +0.129] | 0.200 [0.167, 0.243] | 0.275 [0.238, 0.322] | 0.383 [0.301, 0.470] | 0.044 [0.019, 0.081] |
| 10 | 40 | 193 | 0.124 [0.089, 0.167] | 0.031 [0.010, 0.059] | +0.093 [+0.048, +0.138] | 0.140 [0.102, 0.194] | 0.223 [0.171, 0.307] | 0.333 [0.172, 0.544] | 0.023 [0.000, 0.123] |
| 10 | 80 | 381 | 0.144 [0.113, 0.178] | 0.045 [0.027, 0.072] | +0.100 [+0.060, +0.140] | 0.231 [0.184, 0.285] | 0.302 [0.247, 0.358] | 0.398 [0.300, 0.494] | 0.052 [0.019, 0.097] |
| 100 | 120 | 574 | 0.138 [0.113, 0.166] | 0.052 [0.037, 0.072] | +0.085 [+0.056, +0.120] | 0.314 [0.274, 0.359] | 0.460 [0.420, 0.505] | 0.311 [0.247, 0.375] | 0.053 [0.029, 0.088] |
| 100 | 40 | 193 | 0.130 [0.085, 0.173] | 0.057 [0.031, 0.103] | +0.073 [+0.005, +0.128] | 0.269 [0.219, 0.337] | 0.435 [0.378, 0.513] | 0.308 [0.196, 0.429] | 0.048 [0.012, 0.141] |
| 100 | 80 | 381 | 0.142 [0.111, 0.178] | 0.050 [0.031, 0.072] | +0.092 [+0.057, +0.132] | 0.336 [0.285, 0.394] | 0.472 [0.422, 0.531] | 0.312 [0.237, 0.396] | 0.056 [0.028, 0.102] |
| 1000 | 120 | 574 | 0.162 [0.134, 0.194] | 0.070 [0.052, 0.093] | +0.092 [+0.059, +0.128] | 0.336 [0.298, 0.378] | 0.516 [0.475, 0.563] | 0.306 [0.240, 0.371] | 0.061 [0.039, 0.091] |
| 1000 | 40 | 193 | 0.150 [0.104, 0.195] | 0.083 [0.051, 0.126] | +0.067 [+0.010, +0.125] | 0.311 [0.255, 0.380] | 0.492 [0.426, 0.574] | 0.317 [0.208, 0.446] | 0.053 [0.021, 0.112] |
| 1000 | 80 | 381 | 0.168 [0.132, 0.214] | 0.063 [0.042, 0.086] | +0.105 [+0.067, +0.155] | 0.349 [0.302, 0.404] | 0.528 [0.474, 0.583] | 0.301 [0.225, 0.385] | 0.065 [0.036, 0.105] |

## Pool-seeded search

| B | cities | n | false acceptance, emulator | false acceptance, perfect | difference | real success, emulator | real success, perfect | false rejection, emulator | false rejection, perfect |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 120 | 574 | 0.091 [0.070, 0.118] | n/a | the perfect emulator was not run at this budget | 0.052 [0.033, 0.084] | n/a | 0.533 [0.348, 0.727] | n/a |
| 1 | 40 | 193 | 0.083 [0.051, 0.123] | n/a | the perfect emulator was not run at this budget | 0.031 [0.010, 0.078] | n/a | 0.500 [0.000, 1.000] | n/a |
| 1 | 80 | 381 | 0.094 [0.068, 0.129] | n/a | the perfect emulator was not run at this budget | 0.063 [0.037, 0.108] | n/a | 0.542 [0.350, 0.762] | n/a |
| 10 | 120 | 574 | 0.125 [0.101, 0.151] | 0.037 [0.023, 0.056] | +0.089 [+0.058, +0.116] | 0.118 [0.091, 0.156] | 0.176 [0.139, 0.219] | 0.368 [0.258, 0.500] | 0.050 [0.020, 0.097] |
| 10 | 40 | 193 | 0.109 [0.072, 0.153] | 0.026 [0.010, 0.052] | +0.083 [+0.037, +0.130] | 0.067 [0.041, 0.109] | 0.130 [0.082, 0.199] | 0.462 [0.167, 0.755] | 0.040 [0.000, 0.171] |
| 10 | 80 | 381 | 0.134 [0.106, 0.163] | 0.042 [0.023, 0.069] | +0.092 [+0.054, +0.128] | 0.144 [0.103, 0.191] | 0.199 [0.153, 0.254] | 0.345 [0.229, 0.482] | 0.053 [0.014, 0.118] |
| 100 | 120 | 574 | 0.157 [0.132, 0.184] | 0.057 [0.042, 0.077] | +0.099 [+0.065, +0.134] | 0.221 [0.188, 0.261] | 0.385 [0.347, 0.428] | 0.339 [0.258, 0.425] | 0.086 [0.053, 0.123] |
| 100 | 40 | 193 | 0.145 [0.104, 0.189] | 0.052 [0.026, 0.083] | +0.093 [+0.037, +0.144] | 0.192 [0.147, 0.258] | 0.347 [0.294, 0.424] | 0.324 [0.181, 0.500] | 0.090 [0.033, 0.176] |
| 100 | 80 | 381 | 0.163 [0.131, 0.194] | 0.060 [0.038, 0.088] | +0.102 [+0.059, +0.144] | 0.236 [0.194, 0.295] | 0.404 [0.354, 0.459] | 0.344 [0.245, 0.451] | 0.084 [0.050, 0.124] |
| 1000 | 120 | 574 | 0.176 [0.144, 0.208] | 0.082 [0.060, 0.110] | +0.094 [+0.051, +0.133] | 0.287 [0.252, 0.328] | 0.495 [0.456, 0.539] | 0.248 [0.182, 0.320] | 0.085 [0.059, 0.118] |
| 1000 | 40 | 193 | 0.181 [0.130, 0.229] | 0.067 [0.037, 0.105] | +0.114 [+0.052, +0.173] | 0.275 [0.220, 0.344] | 0.466 [0.413, 0.530] | 0.208 [0.120, 0.339] | 0.100 [0.052, 0.165] |
| 1000 | 80 | 381 | 0.173 [0.137, 0.216] | 0.089 [0.058, 0.128] | +0.084 [+0.032, +0.138] | 0.294 [0.249, 0.345] | 0.509 [0.457, 0.561] | 0.268 [0.192, 0.372] | 0.077 [0.046, 0.118] |

## Checks

- random, 40 cities: equals the run's reference.json in 60 values.
- cem_seeded, 40 cities: equals the run's reference.json in 45 values.

## The analysis plan's replication statement , at 1,000 evaluations

"Replicates" if the interval of the excess over the perfect emulator on the 80 new cities excludes zero; "consistent in size" if the interval of the 80-minus-40 difference includes zero. Excess intervals as the tables above (BCa; `*` percentile where BCa is undefined); the difference: independent cluster bootstraps over the two sets of cities, percentile interval of the replicate differences.

| search | excess, 40 cities (n) | excess, 80 cities (n) | 80 minus 40 [95 %] | 80-city interval excludes 0 | difference's interval includes 0 | reading |
|---|---|---|---|---|---|---|
| Random search | +0.067 [+0.010, +0.125] (193) | +0.105 [+0.067, +0.155] (381) | +0.038 [-0.037, +0.107] | yes | yes | replicates; consistent in size |
| Pool-seeded search | +0.114 [+0.052, +0.173] (193) | +0.084 [+0.032, +0.138] (381) | -0.030 [-0.109, +0.048] | yes | yes | replicates; consistent in size |

- Difference interval: independent cluster bootstraps over the two sets of cities (start-state families), 2000 resamples each, seeds 0 (40 cities) and 1 (80 cities), percentile 95 per cent interval of the replicate differences.

- The analysis plan: random search's excess over the perfect emulator at 1,000 minus at budget 1 (one logged plan), paired by instance: all 120 cities +0.016 [-0.019, +0.050] (574 instances); the 40 cities +0.005 [-0.056, +0.065] (193 instances) (BCa; `*` percentile where BCa is undefined).
