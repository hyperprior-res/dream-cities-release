# The pressure axis: the pool-seeded search on `os_50m_full/samples_006000000`, 10 to 10,000 evaluations

Generated 2026-11-12T23:19:38Z by `code/scripts/pressure_axis.py`. 193 instances (grow 40, solvent 38, treasury 40, recover 35, power 40) in 40 city families: the instances of the 10,000-evaluation run, at every budget. The perfect emulator is the engine judging on fresh seeds under the same search. Intervals: 2000 cluster resamples, seed 0, percentile, hpr_dream.stats.cluster_draws; differences and contrasts are paired by instance.

## False acceptance (the judge accepts the selected plan, the 32-seed majority rejects it)

| evaluations | emulator | perfect emulator | excess |
|---|---|---|---|
| 10 | 0.109 [0.068, 0.150] | 0.026 [0.005, 0.047] | +0.083 [+0.037, +0.129] |
| 100 | 0.145 [0.104, 0.189] | 0.052 [0.026, 0.079] | +0.093 [+0.041, +0.146] |
| 1,000 | 0.181 [0.131, 0.231] | 0.067 [0.036, 0.103] | +0.114 [+0.052, +0.175] |
| 10,000 | 0.207 [0.149, 0.266] | 0.073 [0.042, 0.107] | +0.135 [+0.068, +0.200] |

## Real success (the 32-seed majority accepts the selected plan)

| evaluations | emulator | perfect emulator | shortfall |
|---|---|---|---|
| 10 | 0.067 [0.036, 0.102] | 0.130 [0.077, 0.188] | -0.062 [-0.108, -0.021] |
| 100 | 0.192 [0.138, 0.247] | 0.347 [0.285, 0.412] | -0.155 [-0.220, -0.088] |
| 1,000 | 0.275 [0.215, 0.337] | 0.466 [0.407, 0.524] | -0.192 [-0.251, -0.136] |
| 10,000 | 0.269 [0.204, 0.335] | 0.580 [0.521, 0.642] | -0.311 [-0.382, -0.241] |

## The judge's own acceptance of the selected plan

| evaluations | emulator | perfect emulator | difference |
|---|---|---|---|
| 10 | 0.145 [0.092, 0.202] | 0.150 [0.093, 0.210] | -0.005 [-0.058, +0.046] |
| 100 | 0.275 [0.207, 0.344] | 0.368 [0.306, 0.428] | -0.093 [-0.168, -0.015] |
| 1,000 | 0.399 [0.332, 0.466] | 0.487 [0.428, 0.546] | -0.088 [-0.175, -0.005] |
| 10,000 | 0.383 [0.321, 0.446] | 0.606 [0.540, 0.670] | -0.223 [-0.325, -0.125] |

## Trends (paired contrasts between budgets)

| contrast | estimate [95 %] | excludes 0 |
|---|---|---|
| excess false acceptance at 10,000 minus at 1,000 | +0.021 [-0.046, +0.090] | no |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 1,000 | -0.119 [-0.208, -0.031] | yes |
| real success, emulator: at 10,000 minus at 1,000 | -0.005 [-0.073, +0.063] | no |
| false acceptance, emulator: at 10,000 minus at 1,000 | +0.026 [-0.027, +0.082] | no |
| real success, perfect: at 10,000 minus at 1,000 | +0.114 [+0.067, +0.161] | yes |
| false acceptance, perfect: at 10,000 minus at 1,000 | +0.005 [-0.037, +0.051] | no |
| excess false acceptance at 10,000 minus at 100 | +0.041 [-0.015, +0.094] | no |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 100 | -0.155 [-0.241, -0.062] | yes |
| real success, emulator: at 10,000 minus at 100 | +0.078 [+0.016, +0.145] | yes |
| false acceptance, emulator: at 10,000 minus at 100 | +0.062 [+0.010, +0.114] | yes |
| real success, perfect: at 10,000 minus at 100 | +0.233 [+0.165, +0.302] | yes |
| false acceptance, perfect: at 10,000 minus at 100 | +0.021 [-0.016, +0.057] | no |
| excess false acceptance at 10,000 minus at 10 | +0.052 [-0.021, +0.126] | no |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 10 | -0.249 [-0.318, -0.176] | yes |
| real success, emulator: at 10,000 minus at 10 | +0.202 [+0.133, +0.272] | yes |
| false acceptance, emulator: at 10,000 minus at 10 | +0.098 [+0.031, +0.172] | yes |
| real success, perfect: at 10,000 minus at 10 | +0.451 [+0.385, +0.516] | yes |
| false acceptance, perfect: at 10,000 minus at 10 | +0.047 [+0.010, +0.087] | yes |
| excess false acceptance at 1,000 minus at 10 | +0.031 [-0.036, +0.094] | no |
| real-success shortfall (emulator minus perfect) at 1,000 minus at 10 | -0.130 [-0.189, -0.068] | yes |
| real success, emulator: at 1,000 minus at 10 | +0.207 [+0.146, +0.270] | yes |
| false acceptance, emulator: at 1,000 minus at 10 | +0.073 [+0.016, +0.129] | yes |
| real success, perfect: at 1,000 minus at 10 | +0.337 [+0.269, +0.408] | yes |
| false acceptance, perfect: at 1,000 minus at 10 | +0.041 [+0.005, +0.078] | yes |

## By task family (emulator / perfect emulator; n per family in the header, no intervals)

| family | evaluations | false acceptance | real success | judge accepts |
|---|---|---|---|---|
| grow | 10 | 0.03 / 0.00 | 0.05 / 0.15 | 0.03 / 0.15 |
| grow | 100 | 0.03 / 0.07 | 0.05 / 0.17 | 0.03 / 0.23 |
| grow | 1,000 | 0.00 / 0.05 | 0.15 / 0.28 | 0.05 / 0.30 |
| grow | 10,000 | 0.05 / 0.05 | 0.17 / 0.40 | 0.05 / 0.40 |
| solvent | 10 | 0.03 / 0.03 | 0.03 / 0.05 | 0.03 / 0.05 |
| solvent | 100 | 0.00 / 0.00 | 0.05 / 0.13 | 0.00 / 0.05 |
| solvent | 1,000 | 0.05 / 0.03 | 0.05 / 0.21 | 0.08 / 0.18 |
| solvent | 10,000 | 0.03 / 0.08 | 0.11 / 0.42 | 0.03 / 0.39 |
| treasury | 10 | 0.23 / 0.03 | 0.03 / 0.10 | 0.25 / 0.12 |
| treasury | 100 | 0.33 / 0.07 | 0.17 / 0.38 | 0.47 / 0.40 |
| treasury | 1,000 | 0.28 / 0.07 | 0.25 / 0.55 | 0.50 / 0.53 |
| treasury | 10,000 | 0.23 / 0.05 | 0.28 / 0.55 | 0.38 / 0.60 |
| recover | 10 | 0.26 / 0.09 | 0.00 / 0.06 | 0.26 / 0.14 |
| recover | 100 | 0.29 / 0.11 | 0.17 / 0.11 | 0.40 / 0.23 |
| recover | 1,000 | 0.37 / 0.20 | 0.26 / 0.26 | 0.57 / 0.40 |
| recover | 10,000 | 0.46 / 0.20 | 0.26 / 0.51 | 0.71 / 0.63 |
| power | 10 | 0.03 / 0.00 | 0.23 / 0.28 | 0.17 / 0.28 |
| power | 100 | 0.10 / 0.00 | 0.50 / 0.90 | 0.47 / 0.90 |
| power | 1,000 | 0.23 / 0.00 | 0.65 / 1.00 | 0.80 / 1.00 |
| power | 10,000 | 0.30 / 0.00 | 0.53 / 1.00 | 0.78 / 1.00 |

# Added fields 

Coverage: 193 of the 193 instances are on the axis (emulator holds 193 at 10,000, perfect emulator 193; on one side only: 0 emulator, 0 perfect). 10,000-evaluation directories: emulator: `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4`, `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4_shard1of8`, `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4_shard2of8`, `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4_shard3of8`, `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4_shard4of8`, `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4_shard5of8`, `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4_shard6of8`, `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4_shard7of8`, `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4_shard8of8`; perfect: `results/audit/engine_reference/tasks_v2_H24/cem_seeded_1e4_i100`, `results/audit/engine_reference/tasks_v2_H24/cem_seeded_1e4_rest93`. Random search: `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24` beside `results/audit/engine_reference/tasks_v2_H24/B_economy`.

## Both searches on these instances, one interval method (BCa)

Intervals: BCa cluster bootstrap over held-out cities (city families), 2000 resamples, seed 0, hpr_dream.stats.conditional_mean; percentile bounds of the same resamples beside it (pct_*). * = no event (or every unit an event): the exact one-sided binomial bound on clusters is given (`interval` in the json).

| search | evaluations | false acceptance: emulator | perfect | excess | real success: emulator | perfect | shortfall |
|---|---|---|---|---|---|---|---|
| random | 1 | 0.083 [0.051, 0.123] | 0.021 [0.005, 0.046] | +0.062 [+0.026, +0.103] | 0.031 [0.010, 0.078] | 0.031 [0.010, 0.078] | +0.000 [+0.000, +0.000] |
| random | 10 | 0.124 [0.089, 0.167] | 0.031 [0.010, 0.059] | +0.093 [+0.048, +0.138] | 0.140 [0.102, 0.194] | 0.223 [0.171, 0.307] | -0.083 [-0.159, -0.042] |
| random | 100 | 0.130 [0.085, 0.173] | 0.057 [0.031, 0.103] | +0.073 [+0.005, +0.128] | 0.269 [0.219, 0.337] | 0.435 [0.378, 0.513] | -0.166 [-0.231, -0.112] |
| random | 1,000 | 0.150 [0.104, 0.195] | 0.083 [0.051, 0.126] | +0.067 [+0.010, +0.125] | 0.311 [0.255, 0.380] | 0.492 [0.426, 0.574] | -0.181 [-0.254, -0.114] |
| pool-seeded | 10 | 0.109 [0.072, 0.153] | 0.026 [0.010, 0.052] | +0.083 [+0.037, +0.130] | 0.067 [0.041, 0.109] | 0.130 [0.082, 0.199] | -0.062 [-0.119, -0.026] |
| pool-seeded | 100 | 0.145 [0.104, 0.189] | 0.052 [0.026, 0.083] | +0.093 [+0.037, +0.144] | 0.192 [0.147, 0.258] | 0.347 [0.294, 0.424] | -0.155 [-0.223, -0.092] |
| pool-seeded | 1,000 | 0.181 [0.130, 0.229] | 0.067 [0.037, 0.105] | +0.114 [+0.052, +0.173] | 0.275 [0.220, 0.344] | 0.466 [0.413, 0.530] | -0.192 [-0.261, -0.143] |
| pool-seeded | 10,000 | 0.207 [0.149, 0.265] | 0.073 [0.042, 0.108] | +0.135 [+0.068, +0.200] | 0.269 [0.207, 0.339] | 0.580 [0.524, 0.649] | -0.311 [-0.382, -0.241] |

## Contrasts at 10,000 (pool-seeded search), per comparison and corrected for three

| contrast | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |
|---|---|---|---|---|
| excess false acceptance: at 10,000 minus at 10 | +0.052 [-0.019, +0.130] | no | +0.052 [-0.036, +0.145] | no |
| excess false acceptance: at 10,000 minus at 100 | +0.041 [-0.010, +0.097] | no | +0.041 [-0.021, +0.110] | no |
| excess false acceptance: at 10,000 minus at 1,000 | +0.021 [-0.042, +0.092] | no | +0.021 [-0.062, +0.107] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 10 | -0.249 [-0.317, -0.172] | yes | -0.249 [-0.335, -0.158] | yes |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 100 | -0.155 [-0.240, -0.058] | yes | -0.155 [-0.265, -0.037] | yes |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000 | -0.119 [-0.205, -0.026] | yes | -0.119 [-0.220, +0.003] | no |
| real success, emulator: at 10,000 minus at 10 | +0.202 [+0.135, +0.274] | yes | +0.202 [+0.121, +0.290] | yes |
| real success, emulator: at 10,000 minus at 100 | +0.078 [+0.016, +0.145] | yes | +0.078 [+0.005, +0.164] | yes |
| real success, emulator: at 10,000 minus at 1,000 | -0.005 [-0.068, +0.068] | no | -0.005 [-0.082, +0.084] | no |
| real success, perfect: at 10,000 minus at 10 | +0.451 [+0.387, +0.518] | yes | +0.451 [+0.372, +0.531] | yes |
| real success, perfect: at 10,000 minus at 100 | +0.233 [+0.163, +0.301] | yes | +0.233 [+0.148, +0.313] | yes |
| real success, perfect: at 10,000 minus at 1,000 | +0.114 [+0.067, +0.164] | yes | +0.114 [+0.057, +0.179] | yes |

## 10,000 minus 1,000, leaving out one task family

| contrast | n | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |
|---|---|---|---|---|---|
| excess false acceptance: at 10,000 minus at 1,000, without grow | 153 | +0.013 [-0.072, +0.111] | no | +0.013 [-0.096, +0.128] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without grow | 153 | -0.124 [-0.213, -0.027] | yes | -0.124 [-0.229, -0.013] | yes |
| real success, emulator: at 10,000 minus at 1,000, without grow | 153 | -0.013 [-0.080, +0.065] | no | -0.013 [-0.097, +0.079] | no |
| real success, perfect: at 10,000 minus at 1,000, without grow | 153 | +0.111 [+0.052, +0.176] | yes | +0.111 [+0.040, +0.199] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without solvent | 155 | +0.045 [-0.026, +0.135] | no | +0.045 [-0.051, +0.153] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without solvent | 155 | -0.110 [-0.203, -0.006] | yes | -0.110 [-0.221, +0.027] | no |
| real success, emulator: at 10,000 minus at 1,000, without solvent | 155 | -0.019 [-0.096, +0.071] | no | -0.019 [-0.110, +0.098] | no |
| real success, perfect: at 10,000 minus at 1,000, without solvent | 155 | +0.090 [+0.045, +0.140] | yes | +0.090 [+0.038, +0.153] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without treasury | 153 | +0.033 [-0.046, +0.118] | no | +0.033 [-0.064, +0.143] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without treasury | 153 | -0.157 [-0.255, -0.040] | yes | -0.157 [-0.274, -0.013] | yes |
| real success, emulator: at 10,000 minus at 1,000, without treasury | 153 | -0.013 [-0.085, +0.068] | no | -0.013 [-0.097, +0.091] | no |
| real success, perfect: at 10,000 minus at 1,000, without treasury | 153 | +0.144 [+0.086, +0.205] | yes | +0.144 [+0.074, +0.224] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without recover | 158 | +0.006 [-0.051, +0.058] | no | +0.006 [-0.070, +0.075] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without recover | 158 | -0.089 [-0.178, +0.007] | no | -0.089 [-0.195, +0.038] | no |
| real success, emulator: at 10,000 minus at 1,000, without recover | 158 | -0.006 [-0.076, +0.071] | no | -0.006 [-0.095, +0.092] | no |
| real success, perfect: at 10,000 minus at 1,000, without recover | 158 | +0.082 [+0.038, +0.132] | yes | +0.082 [+0.031, +0.141] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without power | 153 | +0.007 [-0.060, +0.078] | no | +0.007 [-0.074, +0.097] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without power | 153 | -0.118 [-0.217, -0.027] | yes | -0.118 [-0.234, -0.007] | yes |
| real success, emulator: at 10,000 minus at 1,000, without power | 153 | +0.026 [-0.038, +0.096] | no | +0.026 [-0.046, +0.111] | no |
| real success, perfect: at 10,000 minus at 1,000, without power | 153 | +0.144 [+0.085, +0.206] | yes | +0.144 [+0.072, +0.226] | yes |

## The analysis plan

applied. Corrected 10,000-minus-1,000 excess +0.021 [-0.062, +0.107]: excludes zero False; wording: "no rise in the excess false acceptance is established at any budget".

# The same on the well-posed instances

148 of the 193 instances are well posed (grow 36, solvent 20, treasury 39, recover 13, power 40) in 40 city families (flag `in_band`, as in the 193-instance tables). Percentile intervals: 2000 resamples of the subset's own city families, seed 0, percentile, hpr_dream.stats.cluster_draws (the procedure of the top-level fields, run on the subset). Not well posed: `ho-g-00-v0|recover|H24`, `ho-g-05-v0|grow|H24`, `ho-g-06-v0|solvent|H24`, `ho-g-07-v0|recover|H24`, `ho-g-07-v0|solvent|H24`, `ho-g-08-v0|recover|H24`, `ho-g-08-v0|solvent|H24`, `ho-g-11-v0|recover|H24`, `ho-g-11-v0|solvent|H24`, `ho-g-12-v0|recover|H24`, `ho-g-12-v0|solvent|H24`, `ho-g-12-v0|treasury|H24`, `ho-g-13-v0|recover|H24`, `ho-g-13-v0|solvent|H24`, `ho-g-17-v0|recover|H24`, `ho-g-17-v0|solvent|H24`, `ho-g-18-v0|recover|H24`, `ho-g-19-v0|recover|H24`, `ho-g-20-v0|recover|H24`, `ho-g-20-v0|solvent|H24`, `ho-g-22-v0|recover|H24`, `ho-g-23-v0|grow|H24`, `ho-g-23-v0|recover|H24`, `ho-g-23-v0|solvent|H24`, `ho-g-24-v0|recover|H24`, `ho-g-24-v0|solvent|H24`, `ho-g-25-v0|solvent|H24`, `ho-g-26-v0|recover|H24`, `ho-g-27-v0|recover|H24`, `ho-g-27-v0|solvent|H24`, `ho-g-28-v0|solvent|H24`, `ho-g-29-v0|recover|H24`, `ho-g-30-v0|recover|H24`, `ho-g-30-v0|solvent|H24`, `ho-g-32-v0|grow|H24`, `ho-g-32-v0|recover|H24`, `ho-g-33-v0|recover|H24`, `ho-g-34-v0|grow|H24`, `ho-g-34-v0|recover|H24`, `ho-g-34-v0|solvent|H24`, `ho-g-35-v0|recover|H24`, `ho-g-36-v0|solvent|H24`, `ho-g-37-v0|solvent|H24`, `ho-g-38-v0|recover|H24`, `ho-g-39-v0|solvent|H24`.

## False acceptance (the judge accepts the selected plan, the 32-seed majority rejects it)

| evaluations | emulator | perfect emulator | excess |
|---|---|---|---|
| 10 | 0.095 [0.048, 0.141] | 0.007 [0.000, 0.021] | +0.088 [+0.045, +0.131] |
| 100 | 0.149 [0.104, 0.197] | 0.047 [0.015, 0.079] | +0.101 [+0.048, +0.161] |
| 1,000 | 0.155 [0.106, 0.207] | 0.047 [0.014, 0.085] | +0.108 [+0.050, +0.170] |
| 10,000 | 0.176 [0.116, 0.238] | 0.034 [0.007, 0.062] | +0.142 [+0.083, +0.207] |

## Real success (the 32-seed majority accepts the selected plan)

| evaluations | emulator | perfect emulator | shortfall |
|---|---|---|---|
| 10 | 0.088 [0.048, 0.131] | 0.162 [0.098, 0.230] | -0.074 [-0.125, -0.024] |
| 100 | 0.216 [0.153, 0.287] | 0.426 [0.350, 0.504] | -0.209 [-0.290, -0.129] |
| 1,000 | 0.331 [0.257, 0.411] | 0.574 [0.503, 0.644] | -0.243 [-0.318, -0.173] |
| 10,000 | 0.324 [0.245, 0.400] | 0.669 [0.597, 0.739] | -0.345 [-0.430, -0.260] |

## The judge's own acceptance of the selected plan

| evaluations | emulator | perfect emulator | difference |
|---|---|---|---|
| 10 | 0.142 [0.077, 0.212] | 0.169 [0.102, 0.236] | -0.027 [-0.079, +0.026] |
| 100 | 0.304 [0.228, 0.384] | 0.439 [0.369, 0.507] | -0.135 [-0.212, -0.053] |
| 1,000 | 0.419 [0.347, 0.491] | 0.568 [0.507, 0.623] | -0.149 [-0.237, -0.064] |
| 10,000 | 0.385 [0.317, 0.458] | 0.655 [0.576, 0.730] | -0.270 [-0.372, -0.160] |

## Trends (paired contrasts between budgets)

| contrast | estimate [95 %] | excludes 0 |
|---|---|---|
| excess false acceptance at 10,000 minus at 1,000 | +0.034 [-0.027, +0.096] | no |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 1,000 | -0.101 [-0.218, +0.013] | no |
| real success, emulator: at 10,000 minus at 1,000 | -0.007 [-0.102, +0.088] | no |
| false acceptance, emulator: at 10,000 minus at 1,000 | +0.020 [-0.035, +0.075] | no |
| real success, perfect: at 10,000 minus at 1,000 | +0.095 [+0.041, +0.152] | yes |
| false acceptance, perfect: at 10,000 minus at 1,000 | -0.014 [-0.050, +0.022] | no |
| excess false acceptance at 10,000 minus at 100 | +0.041 [-0.013, +0.094] | no |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 100 | -0.135 [-0.248, -0.019] | yes |
| real success, emulator: at 10,000 minus at 100 | +0.108 [+0.021, +0.197] | yes |
| false acceptance, emulator: at 10,000 minus at 100 | +0.027 [-0.021, +0.078] | no |
| real success, perfect: at 10,000 minus at 100 | +0.243 [+0.168, +0.322] | yes |
| false acceptance, perfect: at 10,000 minus at 100 | -0.014 [-0.047, +0.019] | no |
| excess false acceptance at 10,000 minus at 10 | +0.054 [-0.014, +0.133] | no |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 10 | -0.270 [-0.358, -0.184] | yes |
| real success, emulator: at 10,000 minus at 10 | +0.236 [+0.146, +0.333] | yes |
| false acceptance, emulator: at 10,000 minus at 10 | +0.081 [+0.013, +0.159] | yes |
| real success, perfect: at 10,000 minus at 10 | +0.507 [+0.430, +0.588] | yes |
| false acceptance, perfect: at 10,000 minus at 10 | +0.027 [+0.007, +0.053] | yes |
| excess false acceptance at 1,000 minus at 10 | +0.020 [-0.050, +0.092] | no |
| real-success shortfall (emulator minus perfect) at 1,000 minus at 10 | -0.169 [-0.256, -0.088] | yes |
| real success, emulator: at 1,000 minus at 10 | +0.243 [+0.166, +0.324] | yes |
| false acceptance, emulator: at 1,000 minus at 10 | +0.061 [+0.000, +0.124] | no |
| real success, perfect: at 1,000 minus at 10 | +0.412 [+0.321, +0.514] | yes |
| false acceptance, perfect: at 1,000 minus at 10 | +0.041 [+0.006, +0.079] | yes |

## By task family (emulator / perfect emulator; n per family above, no intervals)

| family | evaluations | false acceptance | real success | judge accepts |
|---|---|---|---|---|
| grow | 10 | 0.03 / 0.00 | 0.06 / 0.17 | 0.03 / 0.17 |
| grow | 100 | 0.03 / 0.08 | 0.06 / 0.19 | 0.03 / 0.25 |
| grow | 1,000 | 0.00 / 0.06 | 0.17 / 0.31 | 0.06 / 0.33 |
| grow | 10,000 | 0.06 / 0.03 | 0.19 / 0.44 | 0.06 / 0.42 |
| solvent | 10 | 0.00 / 0.00 | 0.05 / 0.05 | 0.00 / 0.05 |
| solvent | 100 | 0.00 / 0.00 | 0.05 / 0.20 | 0.00 / 0.10 |
| solvent | 1,000 | 0.00 / 0.00 | 0.10 / 0.35 | 0.05 / 0.25 |
| solvent | 10,000 | 0.00 / 0.00 | 0.15 / 0.65 | 0.00 / 0.50 |
| treasury | 10 | 0.21 / 0.00 | 0.03 / 0.10 | 0.23 / 0.10 |
| treasury | 100 | 0.31 / 0.08 | 0.18 / 0.36 | 0.46 / 0.38 |
| treasury | 1,000 | 0.28 / 0.08 | 0.26 / 0.56 | 0.51 / 0.54 |
| treasury | 10,000 | 0.23 / 0.05 | 0.28 / 0.56 | 0.38 / 0.62 |
| recover | 10 | 0.31 / 0.08 | 0.00 / 0.15 | 0.31 / 0.23 |
| recover | 100 | 0.38 / 0.08 | 0.15 / 0.15 | 0.54 / 0.23 |
| recover | 1,000 | 0.23 / 0.15 | 0.38 / 0.38 | 0.54 / 0.46 |
| recover | 10,000 | 0.23 / 0.15 | 0.46 / 0.62 | 0.69 / 0.62 |
| power | 10 | 0.03 / 0.00 | 0.23 / 0.28 | 0.17 / 0.28 |
| power | 100 | 0.10 / 0.00 | 0.50 / 0.90 | 0.47 / 0.90 |
| power | 1,000 | 0.23 / 0.00 | 0.65 / 1.00 | 0.80 / 1.00 |
| power | 10,000 | 0.30 / 0.00 | 0.53 / 1.00 | 0.78 / 1.00 |

## Both searches on these instances, one interval method (BCa)

Intervals: BCa cluster bootstrap over held-out cities (city families), 2000 resamples, seed 0, hpr_dream.stats.conditional_mean; percentile bounds of the same resamples beside it (pct_*). * = no event (or every unit an event): the exact one-sided binomial bound on clusters is given (`interval` in the json).

| search | evaluations | false acceptance: emulator | perfect | excess | real success: emulator | perfect | shortfall |
|---|---|---|---|---|---|---|---|
| random | 1 | 0.081 [0.043, 0.134] | 0.014 [0.000, 0.043] | +0.068 [+0.028, +0.116] | 0.027 [0.007, 0.089] | 0.027 [0.007, 0.089] | +0.000 [+0.000, +0.000] |
| random | 10 | 0.115 [0.075, 0.163] | 0.020 [0.006, 0.055] | +0.095 [+0.047, +0.146] | 0.176 [0.124, 0.245] | 0.284 [0.215, 0.380] | -0.108 [-0.201, -0.060] |
| random | 100 | 0.128 [0.077, 0.179] | 0.034 [0.013, 0.069] | +0.095 [+0.032, +0.149] | 0.318 [0.261, 0.402] | 0.527 [0.454, 0.611] | -0.209 [-0.297, -0.143] |
| random | 1,000 | 0.128 [0.079, 0.188] | 0.047 [0.014, 0.106] | +0.081 [+0.020, +0.147] | 0.378 [0.317, 0.455] | 0.574 [0.503, 0.662] | -0.196 [-0.275, -0.117] |
| pool-seeded | 10 | 0.095 [0.052, 0.150] | 0.007 [0.000, 0.034] | +0.088 [+0.049, +0.137] | 0.088 [0.052, 0.139] | 0.162 [0.106, 0.242] | -0.074 [-0.136, -0.030] |
| pool-seeded | 100 | 0.149 [0.103, 0.197] | 0.047 [0.021, 0.084] | +0.101 [+0.048, +0.162] | 0.216 [0.162, 0.301] | 0.426 [0.357, 0.519] | -0.209 [-0.297, -0.136] |
| pool-seeded | 1,000 | 0.155 [0.107, 0.209] | 0.047 [0.020, 0.093] | +0.108 [+0.048, +0.169] | 0.331 [0.262, 0.417] | 0.574 [0.500, 0.643] | -0.243 [-0.327, -0.176] |
| pool-seeded | 10,000 | 0.176 [0.119, 0.241] | 0.034 [0.013, 0.066] | +0.142 [+0.084, +0.208] | 0.324 [0.247, 0.404] | 0.669 [0.598, 0.741] | -0.345 [-0.428, -0.258] |

## Contrasts at 10,000 (pool-seeded search), per comparison and corrected for three

| contrast | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |
|---|---|---|---|---|
| excess false acceptance: at 10,000 minus at 10 | +0.054 [-0.018, +0.132] | no | +0.054 [-0.032, +0.151] | no |
| excess false acceptance: at 10,000 minus at 100 | +0.041 [-0.014, +0.094] | no | +0.041 [-0.026, +0.105] | no |
| excess false acceptance: at 10,000 minus at 1,000 | +0.034 [-0.027, +0.096] | no | +0.034 [-0.040, +0.107] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 10 | -0.270 [-0.355, -0.182] | yes | -0.270 [-0.374, -0.167] | yes |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 100 | -0.135 [-0.242, -0.007] | yes | -0.135 [-0.266, +0.021] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000 | -0.101 [-0.217, +0.013] | no | -0.101 [-0.232, +0.051] | no |
| real success, emulator: at 10,000 minus at 10 | +0.236 [+0.148, +0.336] | yes | +0.236 [+0.129, +0.354] | yes |
| real success, emulator: at 10,000 minus at 100 | +0.108 [+0.028, +0.200] | yes | +0.108 [+0.013, +0.234] | yes |
| real success, emulator: at 10,000 minus at 1,000 | -0.007 [-0.093, +0.094] | no | -0.007 [-0.113, +0.115] | no |
| real success, perfect: at 10,000 minus at 10 | +0.507 [+0.428, +0.587] | yes | +0.507 [+0.416, +0.606] | yes |
| real success, perfect: at 10,000 minus at 100 | +0.243 [+0.164, +0.320] | yes | +0.243 [+0.145, +0.340] | yes |
| real success, perfect: at 10,000 minus at 1,000 | +0.095 [+0.047, +0.159] | yes | +0.095 [+0.039, +0.174] | yes |

## 10,000 minus 1,000, leaving out one task family

| contrast | n | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |
|---|---|---|---|---|---|
| excess false acceptance: at 10,000 minus at 1,000, without grow | 112 | +0.018 [-0.073, +0.100] | no | +0.018 [-0.093, +0.118] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without grow | 112 | -0.098 [-0.216, +0.024] | no | -0.098 [-0.239, +0.052] | no |
| real success, emulator: at 10,000 minus at 1,000, without grow | 112 | -0.018 [-0.112, +0.086] | no | -0.018 [-0.133, +0.105] | no |
| real success, perfect: at 10,000 minus at 1,000, without grow | 112 | +0.080 [+0.019, +0.171] | yes | +0.080 [+0.009, +0.194] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without solvent | 128 | +0.039 [-0.031, +0.111] | no | +0.039 [-0.047, +0.120] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without solvent | 128 | -0.078 [-0.195, +0.054] | no | -0.078 [-0.225, +0.092] | no |
| real success, emulator: at 10,000 minus at 1,000, without solvent | 128 | -0.016 [-0.116, +0.100] | no | -0.016 [-0.139, +0.131] | no |
| real success, perfect: at 10,000 minus at 1,000, without solvent | 128 | +0.062 [+0.008, +0.123] | yes | +0.062 [+0.000, +0.136] | no |
| excess false acceptance: at 10,000 minus at 1,000, without treasury | 109 | +0.055 [-0.026, +0.138] | no | +0.055 [-0.043, +0.156] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without treasury | 109 | -0.147 [-0.279, +0.009] | no | -0.147 [-0.308, +0.053] | no |
| real success, emulator: at 10,000 minus at 1,000, without treasury | 109 | -0.018 [-0.126, +0.105] | no | -0.018 [-0.155, +0.130] | no |
| real success, perfect: at 10,000 minus at 1,000, without treasury | 109 | +0.128 [+0.072, +0.197] | yes | +0.128 [+0.062, +0.208] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without recover | 135 | +0.037 [-0.021, +0.096] | no | +0.037 [-0.036, +0.107] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without recover | 135 | -0.096 [-0.203, +0.014] | no | -0.096 [-0.222, +0.044] | no |
| real success, emulator: at 10,000 minus at 1,000, without recover | 135 | -0.015 [-0.098, +0.080] | no | -0.015 [-0.117, +0.104] | no |
| real success, perfect: at 10,000 minus at 1,000, without recover | 135 | +0.081 [+0.036, +0.137] | yes | +0.081 [+0.029, +0.151] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without power | 108 | +0.019 [-0.043, +0.093] | no | +0.019 [-0.055, +0.107] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without power | 108 | -0.093 [-0.226, +0.026] | no | -0.093 [-0.250, +0.052] | no |
| real success, emulator: at 10,000 minus at 1,000, without power | 108 | +0.037 [-0.050, +0.125] | no | +0.037 [-0.068, +0.146] | no |
| real success, perfect: at 10,000 minus at 1,000, without power | 108 | +0.130 [+0.064, +0.217] | yes | +0.130 [+0.051, +0.239] | yes |

# Zero-event rates (R1 m16)

R1 m16: every rate in this file whose value is 0 or 1 and the interval given for it. Percentile fields (lo/hi) are two-sided 95 per cent percentile intervals and are degenerate at 0 or 1; the BCa fields (bca_lo/bca_hi) give the exact one-sided binomial bound on clusters there (field interval).

37 such fields; outside the family rows (which carry no interval): none.
