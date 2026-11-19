# The pressure axis: the pool-seeded search on `os_50m_full/samples_006000000`, 10 to 10,000 evaluations

Generated 2026-11-12T23:20:41Z by `code/scripts/pressure_axis.py`. 100 instances (grow 20, solvent 20, treasury 20, recover 20, power 20) in 39 city families: the instances of the 10,000-evaluation run, at every budget. The perfect emulator is the engine judging on fresh seeds under the same search. Intervals: 2000 cluster resamples, seed 0, percentile, hpr_dream.stats.cluster_draws; differences and contrasts are paired by instance.

## False acceptance (the judge accepts the selected plan, the 32-seed majority rejects it)

| evaluations | emulator | perfect emulator | excess |
|---|---|---|---|
| 10 | 0.130 [0.071, 0.198] | 0.020 [0.000, 0.053] | +0.110 [+0.047, +0.180] |
| 100 | 0.170 [0.119, 0.221] | 0.090 [0.042, 0.143] | +0.080 [+0.010, +0.151] |
| 1,000 | 0.190 [0.121, 0.262] | 0.110 [0.057, 0.168] | +0.080 [+0.000, +0.165] |
| 10,000 | 0.250 [0.168, 0.344] | 0.070 [0.028, 0.127] | +0.180 [+0.089, +0.271] |

## Real success (the 32-seed majority accepts the selected plan)

| evaluations | emulator | perfect emulator | shortfall |
|---|---|---|---|
| 10 | 0.090 [0.044, 0.146] | 0.170 [0.091, 0.260] | -0.080 [-0.149, -0.013] |
| 100 | 0.190 [0.107, 0.284] | 0.370 [0.278, 0.477] | -0.180 [-0.268, -0.098] |
| 1,000 | 0.300 [0.211, 0.394] | 0.450 [0.357, 0.554] | -0.150 [-0.237, -0.065] |
| 10,000 | 0.290 [0.187, 0.398] | 0.630 [0.542, 0.728] | -0.340 [-0.444, -0.235] |

## The judge's own acceptance of the selected plan

| evaluations | emulator | perfect emulator | difference |
|---|---|---|---|
| 10 | 0.180 [0.107, 0.265] | 0.190 [0.112, 0.280] | -0.010 [-0.086, +0.063] |
| 100 | 0.300 [0.208, 0.392] | 0.430 [0.337, 0.530] | -0.130 [-0.219, -0.044] |
| 1,000 | 0.440 [0.354, 0.526] | 0.510 [0.423, 0.593] | -0.070 [-0.167, +0.024] |
| 10,000 | 0.440 [0.354, 0.526] | 0.640 [0.537, 0.744] | -0.200 [-0.326, -0.087] |

## Trends (paired contrasts between budgets)

| contrast | estimate [95 %] | excludes 0 |
|---|---|---|
| excess false acceptance at 10,000 minus at 1,000 | +0.100 [+0.011, +0.183] | yes |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 1,000 | -0.190 [-0.327, -0.042] | yes |
| real success, emulator: at 10,000 minus at 1,000 | -0.010 [-0.115, +0.101] | no |
| false acceptance, emulator: at 10,000 minus at 1,000 | +0.060 [-0.013, +0.134] | no |
| real success, perfect: at 10,000 minus at 1,000 | +0.180 [+0.105, +0.262] | yes |
| false acceptance, perfect: at 10,000 minus at 1,000 | -0.040 [-0.102, +0.029] | no |
| excess false acceptance at 10,000 minus at 100 | +0.100 [+0.010, +0.184] | yes |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 100 | -0.160 [-0.287, -0.027] | yes |
| real success, emulator: at 10,000 minus at 100 | +0.100 [-0.011, +0.217] | no |
| false acceptance, emulator: at 10,000 minus at 100 | +0.080 [-0.009, +0.175] | no |
| real success, perfect: at 10,000 minus at 100 | +0.260 [+0.170, +0.357] | yes |
| false acceptance, perfect: at 10,000 minus at 100 | -0.020 [-0.078, +0.038] | no |
| excess false acceptance at 10,000 minus at 10 | +0.070 [-0.041, +0.183] | no |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 10 | -0.260 [-0.352, -0.160] | yes |
| real success, emulator: at 10,000 minus at 10 | +0.200 [+0.092, +0.311] | yes |
| false acceptance, emulator: at 10,000 minus at 10 | +0.120 [+0.011, +0.233] | yes |
| real success, perfect: at 10,000 minus at 10 | +0.460 [+0.374, +0.544] | yes |
| false acceptance, perfect: at 10,000 minus at 10 | +0.050 [+0.000, +0.111] | no |
| excess false acceptance at 1,000 minus at 10 | -0.030 [-0.137, +0.080] | no |
| real-success shortfall (emulator minus perfect) at 1,000 minus at 10 | -0.070 [-0.170, +0.031] | no |
| real success, emulator: at 1,000 minus at 10 | +0.210 [+0.118, +0.305] | yes |
| false acceptance, emulator: at 1,000 minus at 10 | +0.060 [-0.034, +0.161] | no |
| real success, perfect: at 1,000 minus at 10 | +0.280 [+0.176, +0.387] | yes |
| false acceptance, perfect: at 1,000 minus at 10 | +0.090 [+0.030, +0.149] | yes |

## By task family (emulator / perfect emulator; 20 instances each, no intervals)

| family | evaluations | false acceptance | real success | judge accepts |
|---|---|---|---|---|
| grow | 10 | 0.05 / 0.00 | 0.05 / 0.20 | 0.05 / 0.20 |
| grow | 100 | 0.05 / 0.15 | 0.10 / 0.20 | 0.05 / 0.35 |
| grow | 1,000 | 0.00 / 0.10 | 0.20 / 0.25 | 0.10 / 0.35 |
| grow | 10,000 | 0.05 / 0.05 | 0.15 / 0.40 | 0.05 / 0.45 |
| solvent | 10 | 0.00 / 0.05 | 0.05 / 0.05 | 0.00 / 0.10 |
| solvent | 100 | 0.00 / 0.00 | 0.05 / 0.15 | 0.00 / 0.10 |
| solvent | 1,000 | 0.05 / 0.05 | 0.10 / 0.25 | 0.10 / 0.20 |
| solvent | 10,000 | 0.05 / 0.00 | 0.20 / 0.55 | 0.05 / 0.40 |
| treasury | 10 | 0.25 / 0.05 | 0.05 / 0.15 | 0.30 / 0.20 |
| treasury | 100 | 0.40 / 0.15 | 0.20 / 0.50 | 0.60 / 0.55 |
| treasury | 1,000 | 0.30 / 0.15 | 0.20 / 0.50 | 0.50 / 0.55 |
| treasury | 10,000 | 0.30 / 0.10 | 0.30 / 0.55 | 0.45 / 0.65 |
| recover | 10 | 0.30 / 0.00 | 0.00 / 0.05 | 0.30 / 0.05 |
| recover | 100 | 0.25 / 0.15 | 0.15 / 0.10 | 0.40 / 0.25 |
| recover | 1,000 | 0.35 / 0.25 | 0.30 / 0.25 | 0.60 / 0.45 |
| recover | 10,000 | 0.45 / 0.20 | 0.30 / 0.65 | 0.75 / 0.70 |
| power | 10 | 0.05 / 0.00 | 0.30 / 0.40 | 0.25 / 0.40 |
| power | 100 | 0.15 / 0.00 | 0.45 / 0.90 | 0.45 / 0.90 |
| power | 1,000 | 0.25 / 0.00 | 0.70 / 1.00 | 0.90 / 1.00 |
| power | 10,000 | 0.40 / 0.00 | 0.50 / 1.00 | 0.90 / 1.00 |

# Added fields 

Coverage: 100 of the 193 instances are on the axis (emulator holds 100 at 10,000, perfect emulator 100; on one side only: 0 emulator, 0 perfect). 10,000-evaluation directories: emulator: `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded_1e4`; perfect: `results/audit/engine_reference/tasks_v2_H24/cem_seeded_1e4_i100`. Random search: `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24` beside `results/audit/engine_reference/tasks_v2_H24/B_economy`.

## Both searches on these instances, one interval method (BCa)

Intervals: BCa cluster bootstrap over held-out cities (city families), 2000 resamples, seed 0, hpr_dream.stats.conditional_mean; percentile bounds of the same resamples beside it (pct_*). * = no event (or every unit an event): the exact one-sided binomial bound on clusters is given (`interval` in the json).

| search | evaluations | false acceptance: emulator | perfect | excess | real success: emulator | perfect | shortfall |
|---|---|---|---|---|---|---|---|
| random | 1 | 0.100 [0.050, 0.171] | 0.030 [0.009, 0.079] | +0.070 [+0.020, +0.126] | 0.040 [0.011, 0.093] | 0.040 [0.011, 0.093] | +0.000 [+0.000, +0.000] |
| random | 10 | 0.150 [0.096, 0.218] | 0.040 [0.011, 0.101] | +0.110 [+0.053, +0.180] | 0.150 [0.096, 0.220] | 0.260 [0.176, 0.400] | -0.110 [-0.250, -0.049] |
| random | 100 | 0.130 [0.079, 0.196] | 0.090 [0.043, 0.159] | +0.040 [-0.060, +0.133] | 0.270 [0.200, 0.354] | 0.450 [0.363, 0.561] | -0.180 [-0.274, -0.110] |
| random | 1,000 | 0.150 [0.091, 0.225] | 0.080 [0.033, 0.168] | +0.070 [-0.030, +0.167] | 0.370 [0.295, 0.457] | 0.510 [0.403, 0.627] | -0.140 [-0.242, -0.048] |
| pool-seeded | 10 | 0.130 [0.077, 0.201] | 0.020 [0.000, 0.066] | +0.110 [+0.051, +0.189] | 0.090 [0.045, 0.148] | 0.170 [0.100, 0.270] | -0.080 [-0.165, -0.021] |
| pool-seeded | 100 | 0.170 [0.121, 0.223] | 0.090 [0.046, 0.149] | +0.080 [+0.000, +0.149] | 0.190 [0.119, 0.302] | 0.370 [0.291, 0.495] | -0.180 [-0.269, -0.100] |
| pool-seeded | 1,000 | 0.190 [0.123, 0.264] | 0.110 [0.060, 0.172] | +0.080 [-0.008, +0.163] | 0.300 [0.218, 0.406] | 0.450 [0.366, 0.563] | -0.150 [-0.237, -0.065] |
| pool-seeded | 10,000 | 0.250 [0.170, 0.348] | 0.070 [0.030, 0.133] | +0.180 [+0.092, +0.280] | 0.290 [0.198, 0.406] | 0.630 [0.543, 0.729] | -0.340 [-0.440, -0.232] |

## Contrasts at 10,000 (pool-seeded search), per comparison and corrected for three

| contrast | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |
|---|---|---|---|---|
| excess false acceptance: at 10,000 minus at 10 | +0.070 [-0.039, +0.186] | no | +0.070 [-0.058, +0.218] | no |
| excess false acceptance: at 10,000 minus at 100 | +0.100 [+0.011, +0.184] | yes | +0.100 [-0.011, +0.208] | no |
| excess false acceptance: at 10,000 minus at 1,000 | +0.100 [+0.021, +0.189] | yes | +0.100 [+0.000, +0.205] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 10 | -0.260 [-0.347, -0.155] | yes | -0.260 [-0.360, -0.132] | yes |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 100 | -0.160 [-0.283, -0.020] | yes | -0.160 [-0.304, +0.012] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000 | -0.190 [-0.315, -0.026] | yes | -0.190 [-0.338, +0.014] | no |
| real success, emulator: at 10,000 minus at 10 | +0.200 [+0.102, +0.321] | yes | +0.200 [+0.077, +0.344] | yes |
| real success, emulator: at 10,000 minus at 100 | +0.100 [-0.007, +0.227] | no | +0.100 [-0.028, +0.252] | no |
| real success, emulator: at 10,000 minus at 1,000 | -0.010 [-0.101, +0.121] | no | -0.010 [-0.121, +0.151] | no |
| real success, perfect: at 10,000 minus at 10 | +0.460 [+0.374, +0.544] | yes | +0.460 [+0.355, +0.566] | yes |
| real success, perfect: at 10,000 minus at 100 | +0.260 [+0.173, +0.362] | yes | +0.260 [+0.152, +0.383] | yes |
| real success, perfect: at 10,000 minus at 1,000 | +0.180 [+0.110, +0.267] | yes | +0.180 [+0.095, +0.284] | yes |

## 10,000 minus 1,000, leaving out one task family

| contrast | n | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |
|---|---|---|---|---|---|
| excess false acceptance: at 10,000 minus at 1,000, without grow | 80 | +0.100 [-0.019, +0.222] | no | +0.100 [-0.043, +0.247] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without grow | 80 | -0.188 [-0.324, +0.000] | no | -0.188 [-0.354, +0.032] | no |
| real success, emulator: at 10,000 minus at 1,000, without grow | 80 | +0.000 [-0.101, +0.147] | no | +0.000 [-0.121, +0.184] | no |
| real success, perfect: at 10,000 minus at 1,000, without grow | 80 | +0.188 [+0.110, +0.295] | yes | +0.188 [+0.095, +0.325] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without solvent | 80 | +0.113 [+0.013, +0.228] | yes | +0.113 [-0.012, +0.259] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without solvent | 80 | -0.188 [-0.326, +0.019] | no | -0.188 [-0.353, +0.075] | no |
| real success, emulator: at 10,000 minus at 1,000, without solvent | 80 | -0.037 [-0.136, +0.139] | no | -0.037 [-0.154, +0.174] | no |
| real success, perfect: at 10,000 minus at 1,000, without solvent | 80 | +0.150 [+0.081, +0.238] | yes | +0.150 [+0.069, +0.255] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without treasury | 80 | +0.113 [+0.021, +0.229] | yes | +0.113 [+0.000, +0.262] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without treasury | 80 | -0.250 [-0.386, -0.065] | yes | -0.250 [-0.407, -0.011] | yes |
| real success, emulator: at 10,000 minus at 1,000, without treasury | 80 | -0.037 [-0.141, +0.101] | no | -0.037 [-0.162, +0.148] | no |
| real success, perfect: at 10,000 minus at 1,000, without treasury | 80 | +0.212 [+0.130, +0.308] | yes | +0.212 [+0.112, +0.329] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without recover | 80 | +0.087 [+0.037, +0.150] | yes | +0.087 [+0.027, +0.167] | yes |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without recover | 80 | -0.138 [-0.274, +0.013] | no | -0.138 [-0.291, +0.042] | no |
| real success, emulator: at 10,000 minus at 1,000, without recover | 80 | -0.013 [-0.101, +0.111] | no | -0.013 [-0.121, +0.143] | no |
| real success, perfect: at 10,000 minus at 1,000, without recover | 80 | +0.125 [+0.064, +0.209] | yes | +0.125 [+0.049, +0.239] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without power | 80 | +0.087 [+0.013, +0.194] | yes | +0.087 [+0.000, +0.221] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without power | 80 | -0.188 [-0.344, -0.023] | yes | -0.188 [-0.375, +0.034] | no |
| real success, emulator: at 10,000 minus at 1,000, without power | 80 | +0.037 [-0.069, +0.169] | no | +0.037 [-0.091, +0.218] | no |
| real success, perfect: at 10,000 minus at 1,000, without power | 80 | +0.225 [+0.138, +0.338] | yes | +0.225 [+0.123, +0.363] | yes |

## The analysis plan

not applied: 100 of 193 instances on the axis.

# The same on the well-posed instances

81 of the 100 instances are well posed (grow 19, solvent 13, treasury 19, recover 10, power 20) in 34 city families (flag `in_band`, as in the 193-instance tables). Percentile intervals: 2000 resamples of the subset's own city families, seed 0, percentile, hpr_dream.stats.cluster_draws (the procedure of the top-level fields, run on the subset). Not well posed: `ho-g-00-v0|recover|H24`, `ho-g-05-v0|grow|H24`, `ho-g-06-v0|solvent|H24`, `ho-g-07-v0|recover|H24`, `ho-g-07-v0|solvent|H24`, `ho-g-08-v0|recover|H24`, `ho-g-08-v0|solvent|H24`, `ho-g-11-v0|recover|H24`, `ho-g-11-v0|solvent|H24`, `ho-g-12-v0|recover|H24`, `ho-g-12-v0|solvent|H24`, `ho-g-12-v0|treasury|H24`, `ho-g-13-v0|recover|H24`, `ho-g-13-v0|solvent|H24`, `ho-g-18-v0|recover|H24`, `ho-g-23-v0|recover|H24`, `ho-g-33-v0|recover|H24`, `ho-g-36-v0|solvent|H24`, `ho-g-38-v0|recover|H24`.

## False acceptance (the judge accepts the selected plan, the 32-seed majority rejects it)

| evaluations | emulator | perfect emulator | excess |
|---|---|---|---|
| 10 | 0.099 [0.033, 0.165] | 0.000 [0.000, 0.000] | +0.099 [+0.033, +0.165] |
| 100 | 0.185 [0.122, 0.254] | 0.086 [0.035, 0.141] | +0.099 [+0.013, +0.193] |
| 1,000 | 0.160 [0.088, 0.236] | 0.086 [0.029, 0.144] | +0.074 [-0.010, +0.162] |
| 10,000 | 0.222 [0.138, 0.312] | 0.049 [0.012, 0.093] | +0.173 [+0.080, +0.281] |

## Real success (the 32-seed majority accepts the selected plan)

| evaluations | emulator | perfect emulator | shortfall |
|---|---|---|---|
| 10 | 0.111 [0.057, 0.177] | 0.210 [0.125, 0.311] | -0.099 [-0.183, -0.023] |
| 100 | 0.210 [0.116, 0.323] | 0.444 [0.337, 0.581] | -0.235 [-0.342, -0.137] |
| 1,000 | 0.346 [0.244, 0.452] | 0.543 [0.430, 0.662] | -0.198 [-0.295, -0.103] |
| 10,000 | 0.321 [0.197, 0.451] | 0.679 [0.580, 0.783] | -0.358 [-0.483, -0.232] |

## The judge's own acceptance of the selected plan

| evaluations | emulator | perfect emulator | difference |
|---|---|---|---|
| 10 | 0.160 [0.071, 0.253] | 0.210 [0.125, 0.311] | -0.049 [-0.134, +0.024] |
| 100 | 0.321 [0.225, 0.425] | 0.494 [0.390, 0.608] | -0.173 [-0.269, -0.084] |
| 1,000 | 0.444 [0.356, 0.531] | 0.568 [0.483, 0.655] | -0.123 [-0.219, -0.025] |
| 10,000 | 0.432 [0.349, 0.524] | 0.679 [0.562, 0.800] | -0.247 [-0.370, -0.128] |

## Trends (paired contrasts between budgets)

| contrast | estimate [95 %] | excludes 0 |
|---|---|---|
| excess false acceptance at 10,000 minus at 1,000 | +0.099 [+0.014, +0.178] | yes |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 1,000 | -0.160 [-0.328, +0.015] | no |
| real success, emulator: at 10,000 minus at 1,000 | -0.025 [-0.143, +0.114] | no |
| false acceptance, emulator: at 10,000 minus at 1,000 | +0.062 [-0.023, +0.133] | no |
| real success, perfect: at 10,000 minus at 1,000 | +0.136 [+0.055, +0.227] | yes |
| false acceptance, perfect: at 10,000 minus at 1,000 | -0.037 [-0.098, +0.026] | no |
| excess false acceptance at 10,000 minus at 100 | +0.074 [-0.012, +0.162] | no |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 100 | -0.123 [-0.273, +0.039] | no |
| real success, emulator: at 10,000 minus at 100 | +0.111 [-0.026, +0.253] | no |
| false acceptance, emulator: at 10,000 minus at 100 | +0.037 [-0.040, +0.118] | no |
| real success, perfect: at 10,000 minus at 100 | +0.235 [+0.130, +0.337] | yes |
| false acceptance, perfect: at 10,000 minus at 100 | -0.037 [-0.094, +0.013] | no |
| excess false acceptance at 10,000 minus at 10 | +0.074 [-0.037, +0.202] | no |
| real-success shortfall (emulator minus perfect) at 10,000 minus at 10 | -0.259 [-0.375, -0.140] | yes |
| real success, emulator: at 10,000 minus at 10 | +0.210 [+0.076, +0.356] | yes |
| false acceptance, emulator: at 10,000 minus at 10 | +0.123 [+0.012, +0.239] | yes |
| real success, perfect: at 10,000 minus at 10 | +0.469 [+0.373, +0.571] | yes |
| false acceptance, perfect: at 10,000 minus at 10 | +0.049 [+0.012, +0.093] | yes |
| excess false acceptance at 1,000 minus at 10 | -0.025 [-0.137, +0.092] | no |
| real-success shortfall (emulator minus perfect) at 1,000 minus at 10 | -0.099 [-0.221, +0.020] | no |
| real success, emulator: at 1,000 minus at 10 | +0.235 [+0.123, +0.341] | yes |
| false acceptance, emulator: at 1,000 minus at 10 | +0.062 [-0.040, +0.164] | no |
| real success, perfect: at 1,000 minus at 10 | +0.333 [+0.207, +0.464] | yes |
| false acceptance, perfect: at 1,000 minus at 10 | +0.086 [+0.029, +0.144] | yes |

## By task family (emulator / perfect emulator; n per family above, no intervals)

| family | evaluations | false acceptance | real success | judge accepts |
|---|---|---|---|---|
| grow | 10 | 0.05 / 0.00 | 0.05 / 0.21 | 0.05 / 0.21 |
| grow | 100 | 0.05 / 0.16 | 0.11 / 0.21 | 0.05 / 0.37 |
| grow | 1,000 | 0.00 / 0.11 | 0.21 / 0.26 | 0.11 / 0.37 |
| grow | 10,000 | 0.05 / 0.05 | 0.16 / 0.42 | 0.05 / 0.47 |
| solvent | 10 | 0.00 / 0.00 | 0.08 / 0.08 | 0.00 / 0.08 |
| solvent | 100 | 0.00 / 0.00 | 0.08 / 0.23 | 0.00 / 0.15 |
| solvent | 1,000 | 0.00 / 0.00 | 0.15 / 0.38 | 0.08 / 0.23 |
| solvent | 10,000 | 0.00 / 0.00 | 0.23 / 0.69 | 0.00 / 0.54 |
| treasury | 10 | 0.21 / 0.00 | 0.05 / 0.16 | 0.26 / 0.16 |
| treasury | 100 | 0.37 / 0.16 | 0.21 / 0.47 | 0.58 / 0.53 |
| treasury | 1,000 | 0.32 / 0.16 | 0.21 / 0.53 | 0.53 / 0.58 |
| treasury | 10,000 | 0.32 / 0.11 | 0.32 / 0.58 | 0.47 / 0.68 |
| recover | 10 | 0.20 / 0.00 | 0.00 / 0.10 | 0.20 / 0.10 |
| recover | 100 | 0.40 / 0.10 | 0.10 / 0.20 | 0.50 / 0.30 |
| recover | 1,000 | 0.20 / 0.20 | 0.40 / 0.40 | 0.50 / 0.50 |
| recover | 10,000 | 0.30 / 0.10 | 0.40 / 0.70 | 0.70 / 0.60 |
| power | 10 | 0.05 / 0.00 | 0.30 / 0.40 | 0.25 / 0.40 |
| power | 100 | 0.15 / 0.00 | 0.45 / 0.90 | 0.45 / 0.90 |
| power | 1,000 | 0.25 / 0.00 | 0.70 / 1.00 | 0.90 / 1.00 |
| power | 10,000 | 0.40 / 0.00 | 0.50 / 1.00 | 0.90 / 1.00 |

## Both searches on these instances, one interval method (BCa)

Intervals: BCa cluster bootstrap over held-out cities (city families), 2000 resamples, seed 0, hpr_dream.stats.conditional_mean; percentile bounds of the same resamples beside it (pct_*). * = no event (or every unit an event): the exact one-sided binomial bound on clusters is given (`interval` in the json).

| search | evaluations | false acceptance: emulator | perfect | excess | real success: emulator | perfect | shortfall |
|---|---|---|---|---|---|---|---|
| random | 1 | 0.086 [0.034, 0.163] | 0.025 [0.000, 0.074] | +0.062 [+0.010, +0.126] | 0.037 [0.011, 0.093] | 0.037 [0.011, 0.093] | +0.000 [+0.000, +0.000] |
| random | 10 | 0.136 [0.078, 0.204] | 0.025 [0.000, 0.072] | +0.111 [+0.039, +0.184] | 0.185 [0.117, 0.274] | 0.321 [0.218, 0.480] | -0.136 [-0.288, -0.060] |
| random | 100 | 0.148 [0.085, 0.231] | 0.049 [0.013, 0.099] | +0.099 [+0.012, +0.192] | 0.309 [0.227, 0.397] | 0.506 [0.405, 0.635] | -0.198 [-0.315, -0.115] |
| random | 1,000 | 0.148 [0.082, 0.250] | 0.074 [0.021, 0.167] | +0.074 [-0.034, +0.192] | 0.432 [0.347, 0.526] | 0.543 [0.436, 0.675] | -0.111 [-0.231, -0.013] |
| pool-seeded | 10 | 0.099 [0.043, 0.180] | 0.000 [0.000, 0.084]* | +0.099 [+0.043, +0.180] | 0.111 [0.060, 0.182] | 0.210 [0.130, 0.324] | -0.099 [-0.194, -0.027] |
| pool-seeded | 100 | 0.185 [0.127, 0.259] | 0.086 [0.040, 0.149] | +0.099 [+0.013, +0.197] | 0.210 [0.127, 0.346] | 0.444 [0.344, 0.594] | -0.235 [-0.337, -0.133] |
| pool-seeded | 1,000 | 0.160 [0.093, 0.241] | 0.086 [0.040, 0.157] | +0.074 [-0.012, +0.156] | 0.346 [0.250, 0.457] | 0.543 [0.437, 0.667] | -0.198 [-0.297, -0.105] |
| pool-seeded | 10,000 | 0.222 [0.139, 0.314] | 0.049 [0.014, 0.100] | +0.173 [+0.083, +0.284] | 0.321 [0.206, 0.456] | 0.679 [0.581, 0.785] | -0.358 [-0.476, -0.228] |

## Contrasts at 10,000 (pool-seeded search), per comparison and corrected for three

| contrast | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |
|---|---|---|---|---|
| excess false acceptance: at 10,000 minus at 10 | +0.074 [-0.038, +0.200] | no | +0.074 [-0.063, +0.218] | no |
| excess false acceptance: at 10,000 minus at 100 | +0.074 [-0.012, +0.162] | no | +0.074 [-0.030, +0.179] | no |
| excess false acceptance: at 10,000 minus at 1,000 | +0.099 [+0.013, +0.176] | yes | +0.099 [-0.011, +0.190] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 10 | -0.259 [-0.369, -0.135] | yes | -0.259 [-0.390, -0.105] | yes |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 100 | -0.123 [-0.274, +0.038] | no | -0.123 [-0.307, +0.067] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000 | -0.160 [-0.321, +0.027] | no | -0.160 [-0.347, +0.076] | no |
| real success, emulator: at 10,000 minus at 10 | +0.210 [+0.082, +0.365] | yes | +0.210 [+0.060, +0.391] | yes |
| real success, emulator: at 10,000 minus at 100 | +0.111 [-0.013, +0.279] | no | +0.111 [-0.037, +0.313] | no |
| real success, emulator: at 10,000 minus at 1,000 | -0.025 [-0.133, +0.131] | no | -0.025 [-0.151, +0.165] | no |
| real success, perfect: at 10,000 minus at 10 | +0.469 [+0.375, +0.574] | yes | +0.469 [+0.357, +0.599] | yes |
| real success, perfect: at 10,000 minus at 100 | +0.235 [+0.139, +0.354] | yes | +0.235 [+0.125, +0.380] | yes |
| real success, perfect: at 10,000 minus at 1,000 | +0.136 [+0.066, +0.250] | yes | +0.136 [+0.051, +0.278] | yes |

## 10,000 minus 1,000, leaving out one task family

| contrast | n | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |
|---|---|---|---|---|---|
| excess false acceptance: at 10,000 minus at 1,000, without grow | 62 | +0.097 [-0.030, +0.192] | no | +0.097 [-0.053, +0.208] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without grow | 62 | -0.145 [-0.316, +0.060] | no | -0.145 [-0.345, +0.103] | no |
| real success, emulator: at 10,000 minus at 1,000, without grow | 62 | -0.016 [-0.140, +0.164] | no | -0.016 [-0.161, +0.205] | no |
| real success, perfect: at 10,000 minus at 1,000, without grow | 62 | +0.129 [+0.049, +0.268] | yes | +0.129 [+0.036, +0.302] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without solvent | 68 | +0.118 [+0.016, +0.206] | yes | +0.118 [+0.000, +0.230] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without solvent | 68 | -0.147 [-0.313, +0.057] | no | -0.147 [-0.351, +0.101] | no |
| real success, emulator: at 10,000 minus at 1,000, without solvent | 68 | -0.044 [-0.163, +0.130] | no | -0.044 [-0.178, +0.170] | no |
| real success, perfect: at 10,000 minus at 1,000, without solvent | 68 | +0.103 [+0.027, +0.213] | yes | +0.103 [+0.000, +0.236] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without treasury | 62 | +0.113 [+0.001, +0.218] | yes | +0.113 [-0.018, +0.241] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without treasury | 62 | -0.226 [-0.400, +0.012] | no | -0.226 [-0.441, +0.053] | no |
| real success, emulator: at 10,000 minus at 1,000, without treasury | 62 | -0.065 [-0.191, +0.121] | no | -0.065 [-0.218, +0.157] | no |
| real success, perfect: at 10,000 minus at 1,000, without treasury | 62 | +0.161 [+0.077, +0.266] | yes | +0.161 [+0.056, +0.288] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without recover | 71 | +0.085 [+0.015, +0.160] | yes | +0.085 [+0.000, +0.177] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without recover | 71 | -0.141 [-0.292, +0.019] | no | -0.141 [-0.324, +0.059] | no |
| real success, emulator: at 10,000 minus at 1,000, without recover | 71 | -0.028 [-0.137, +0.104] | no | -0.028 [-0.160, +0.142] | no |
| real success, perfect: at 10,000 minus at 1,000, without recover | 71 | +0.113 [+0.048, +0.206] | yes | +0.113 [+0.039, +0.228] | yes |
| excess false acceptance: at 10,000 minus at 1,000, without power | 61 | +0.082 [+0.000, +0.186] | no | +0.082 [-0.016, +0.211] | no |
| real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000, without power | 61 | -0.148 [-0.357, +0.073] | no | -0.148 [-0.404, +0.114] | no |
| real success, emulator: at 10,000 minus at 1,000, without power | 61 | +0.033 [-0.091, +0.189] | no | +0.033 [-0.107, +0.226] | no |
| real success, perfect: at 10,000 minus at 1,000, without power | 61 | +0.180 [+0.078, +0.333] | yes | +0.180 [+0.058, +0.367] | yes |

# Zero-event rates (R1 m16)

R1 m16: every rate in this file whose value is 0 or 1 and the interval given for it. Percentile fields (lo/hi) are two-sided 95 per cent percentile intervals and are degenerate at 0 or 1; the BCa fields (bca_lo/bca_hi) give the exact one-sided binomial bound on clusters there (field interval).

44 such fields; outside the family rows (which carry no interval): `well_posed.rows[budget=10].false_acceptance.perfect` (two-sided 95 % percentile interval: every resample gives the), `well_posed.bca.pool_seeded.rows[budget=10].false_acceptance.perfect` (no event: [0, one-sided 95.00% exact binomial upper bound on).
