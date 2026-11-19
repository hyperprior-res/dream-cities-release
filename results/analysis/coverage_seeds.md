# The coverage model against three training seeds of the main configuration 

Generated 2026-11-12T22:05:39Z by `PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/coverage_seeds.py`. Tasks `tasks_v2_H24` (the 40 original cities), budget 1,000; models: `os_50m_full-samples_006000000` (seed 0 (main checkpoint)); `os_50m_full_s1-samples_006000000` (seed 1); `os_50m_full_s2-samples_006000000` (seed 2); `os_50m_cov-samples_006000000` (coverage model). Intervals: cluster bootstrap over start-state families, 2000 resamples, seed 0, BCa 95 per cent (percentile where BCa is undefined; the exact one-sided bound where no unit is falsely accepted), hpr_dream.stats, as analyse_ladder.py's decision_fidelity and coverage arm. Paired difference: coverage model minus the mean of the three seeds on the same instances and the same cluster resamples: per instance for (i) and (ii) (the reference is common, so (i)'s difference is the difference in false acceptance); for (iii) the coverage model's ratio minus the mean of the seeds' ratios. Reading: the analysis plan: the coverage model's value below the lowest of the three seeds (below_all), above the highest (above_all), otherwise within (a tie with a seed is within); compared on exact counts; the wording is fixed for (i) and (ii), and (iii) carries the position only. Status: COMPLETE.

## random search (193 instances, 40 start-state families)

Perfect emulator: false acceptance 0.083 [0.051, 0.126], real success 0.492 [0.426, 0.574].

| model | false acceptance | excess over perfect | real success | false rejection | emulator accepts | falsely accepted / perfect / oracle accepts / falsely rejected |
|---|---|---|---|---|---|---|
| seed 0 (main checkpoint) | 0.150 [0.104, 0.195] | +0.067 [+0.010, +0.125] | 0.311 [0.255, 0.380] | 0.317 [0.208, 0.446] | 0.363 [0.302, 0.420] | 29 / 16 / 60 / 19 |
| seed 1 | 0.181 [0.149, 0.214] | +0.098 [+0.051, +0.148] | 0.332 [0.280, 0.402] | 0.281 [0.185, 0.391] | 0.420 [0.370, 0.470] | 35 / 16 / 64 / 18 |
| seed 2 | 0.140 [0.094, 0.198] | +0.057 [+0.005, +0.118] | 0.326 [0.266, 0.402] | 0.365 [0.239, 0.516] | 0.347 [0.285, 0.421] | 27 / 16 / 63 / 23 |
| coverage model | 0.098 [0.062, 0.149] | +0.016 [-0.031, +0.065] | 0.332 [0.285, 0.402] | 0.344 [0.233, 0.459] | 0.316 [0.267, 0.363] | 19 / 16 / 64 / 22 |

| quantity | coverage | seeds 0, 1, 2 | seeds' min / max / mean | coverage minus seed mean | position  | wording |
|---|---|---|---|---|---|---|
| (i) excess false acceptance over the perfect emulator | 0.016 | 0.067, 0.098, 0.057 | 0.057 / 0.098 / 0.074 | -0.059 [-0.098, -0.016] | below_all | lies below all three training seeds of the original configuration |
| (ii) real success of the selected plans | 0.332 | 0.311, 0.332, 0.326 | 0.311 / 0.332 / 0.323 | +0.009 [-0.040, +0.054] | within | lies within the spread of three training seeds of the original configuration, so its difference from the main checkpoint cannot be told from seed-to-seed variation |
| (iii) false rejection of the selected plans | 0.344 | 0.317, 0.281, 0.365 | 0.281 / 0.365 / 0.321 | +0.023 [-0.076, +0.116] | within | (no wording fixed: printed side by side) |

Beside it, coverage minus the main checkpoint (as `coverage.json`): excess -0.052 [-0.107, +0.000], real success +0.021 [-0.051, +0.077], false rejection +0.027 [-0.118, +0.138].

## pool-seeded (adaptive) search (193 instances, 40 start-state families)

Perfect emulator: false acceptance 0.067 [0.037, 0.105], real success 0.466 [0.413, 0.530].

| model | false acceptance | excess over perfect | real success | false rejection | emulator accepts | falsely accepted / perfect / oracle accepts / falsely rejected |
|---|---|---|---|---|---|---|
| seed 0 (main checkpoint) | 0.181 [0.130, 0.229] | +0.114 [+0.052, +0.173] | 0.275 [0.220, 0.344] | 0.208 [0.120, 0.339] | 0.399 [0.328, 0.464] | 35 / 13 / 53 / 11 |
| seed 1 | 0.197 [0.147, 0.256] | +0.130 [+0.073, +0.193] | 0.249 [0.200, 0.313] | 0.208 [0.111, 0.340] | 0.394 [0.340, 0.462] | 38 / 13 / 48 / 10 |
| seed 2 | 0.145 [0.097, 0.205] | +0.078 [+0.021, +0.141] | 0.301 [0.256, 0.365] | 0.362 [0.226, 0.500] | 0.337 [0.267, 0.409] | 28 / 13 / 58 / 21 |
| coverage model | 0.098 [0.066, 0.141] | +0.031 [-0.010, +0.073] | 0.275 [0.224, 0.340] | 0.340 [0.245, 0.444] | 0.280 [0.230, 0.338] | 19 / 13 / 53 / 18 |

| quantity | coverage | seeds 0, 1, 2 | seeds' min / max / mean | coverage minus seed mean | position  | wording |
|---|---|---|---|---|---|---|
| (i) excess false acceptance over the perfect emulator | 0.031 | 0.114, 0.130, 0.078 | 0.078 / 0.130 / 0.107 | -0.076 [-0.125, -0.025] | below_all | lies below all three training seeds of the original configuration |
| (ii) real success of the selected plans | 0.275 | 0.275, 0.249, 0.301 | 0.249 / 0.301 / 0.275 | +0.000 [-0.043, +0.046] | within | lies within the spread of three training seeds of the original configuration, so its difference from the main checkpoint cannot be told from seed-to-seed variation |
| (iii) false rejection of the selected plans | 0.340 | 0.208, 0.208, 0.362 | 0.208 / 0.362 / 0.259 | +0.080 [-0.014, +0.189] | within | (no wording fixed: printed side by side) |

Beside it, coverage minus the main checkpoint (as `coverage.json`): excess -0.083 [-0.138, -0.031], real success +0.000 [-0.053, +0.062], false rejection +0.132 [+0.026, +0.247].

## Checks

- every audit reads ok with analyse_ladder.read_audit, paired with the perfect emulator on all 193 instances of the tasks file; the four models hold the same instances, start-state families and reference verdicts; each card names its own run's checkpoint
- each audit's all-instance false acceptance, perfect-emulator false acceptance and excess equal its reference.json (values; any interval limit that differs is listed in notes)
- random: the main checkpoint's and the coverage model's statistics and their paired difference equal results/analysis/coverage.json
- random: the main checkpoint's statistics equal results/analysis/replication.json (40 cities)
- cem_seeded: the main checkpoint's and the coverage model's statistics and their paired difference equal results/analysis/coverage.json
- cem_seeded: the main checkpoint's statistics equal results/analysis/replication.json (40 cities)

The sentence always says that three seeds bound the spread loosely.
