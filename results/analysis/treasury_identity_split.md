# Treasury identity: accepted trajectories split by the oracle

Generated 2026-11-12T13:06:38Z by `code/scripts/treasury_split.py` on `results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24`, per-trajectory data from `<cache>/audit/work/ladder/os_50m_full/samples_006000000/patching/v1-248fd2187b/identity`. Breach: created money above 5% of the starting treasury over 24 months (form B, dc.patching.created_share), per emulator trajectory. Cells: breached / trajectories, rate, 95 % BCa cluster bootstrap over held-out cities, 2,000 resamples, seed 0 (run_patching._est, as treasury_identity.md); percentile beside it. Check: emulator accepts / rejects groups recomputed and equal to patching_costs.json identity.material (trajectories and the >5 % rate) for every search and budget.

| search | evaluations | wrongly accepted | rightly accepted | rejected | wrongly minus rightly |
|---|---|---|---|---|---|
| best_of_n | 1 | 2/56 0.036 [0.00, 0.09] (7 records) | 1/64 0.016 [0.00, 0.12] (8 records) | 36/672 0.054 [0.02, 0.11] (84 records) | +0.020 [-0.083, +0.083] |
| best_of_n | 10 | 9/112 0.080 [0.02, 0.15] (14 records) | 9/224 0.040 [0.01, 0.08] (28 records) | 19/456 0.042 [0.02, 0.09] (57 records) | +0.040 [-0.024, +0.121] |
| best_of_n | 100 | 3/120 0.025 [0.00, 0.05] (15 records) | 12/248 0.048 [0.02, 0.10] (31 records) | 15/424 0.035 [0.02, 0.06] (53 records) | -0.023 [-0.069, +0.018] |
| best_of_n | 1,000 | 10/80 0.125 [0.03, 0.38] (10 records) | 14/240 0.058 [0.03, 0.11] (30 records) | 20/472 0.042 [0.02, 0.08] (59 records) | +0.067 [-0.046, +0.328] |
| best_of_n | all budgets | 24/368 0.065 [0.03, 0.12] (46 records) | 36/776 0.046 [0.02, 0.08] (97 records) | 90/2024 0.044 [0.02, 0.07] (253 records) | +0.019 [-0.032, +0.083] |
| cem | 1 | 1/32 0.031 [0.00, 0.09] (4 records) | 0/0 - | 80/1512 0.053 [0.03, 0.10] (189 records) | - |
| cem | 10 | 1/32 0.031 [0.00, 0.09] (4 records) | 0/0 - | 151/1512 0.100 [0.06, 0.16] (189 records) | - |
| cem | 100 | 6/40 0.150 [0.00, 0.60] (5 records) | 0/0 - | 188/1504 0.125 [0.08, 0.19] (188 records) | - |
| cem | 1,000 | 8/80 0.100 [0.03, 0.21] (10 records) | 1/8 0.125 [0.12, 0.12] (1 records) | 188/1456 0.129 [0.08, 0.20] (182 records) | -0.025 [-0.100, +0.087] |
| cem | all budgets | 16/184 0.087 [0.02, 0.27] (23 records) | 1/8 0.125 [0.12, 0.12] (1 records) | 607/5984 0.101 [0.07, 0.15] (748 records) | -0.038 [-0.101, +0.138] |
| random | 1 | 0/128 0.000 [0, 0.19 one-sided] (16 records) | 0/24 0.000 [0, 0.63 one-sided] (3 records) | 71/1392 0.051 [0.02, 0.11] (174 records) | +0.000 [+0.000, +0.000] |
| random | 10 | 1/192 0.005 [0.00, 0.03] (24 records) | 10/144 0.069 [0.02, 0.17] (18 records) | 118/1208 0.098 [0.06, 0.16] (151 records) | -0.064 [-0.161, -0.014] |
| random | 100 | 13/200 0.065 [0.03, 0.16] (25 records) | 29/288 0.101 [0.05, 0.20] (36 records) | 111/1056 0.105 [0.06, 0.17] (132 records) | -0.036 [-0.140, +0.049] |
| random | 1,000 | 37/232 0.159 [0.08, 0.27] (29 records) | 27/328 0.082 [0.04, 0.17] (41 records) | 124/984 0.126 [0.07, 0.21] (123 records) | +0.077 [-0.010, +0.171] |
| random | all budgets | 51/752 0.068 [0.03, 0.12] (94 records) | 66/784 0.084 [0.04, 0.14] (98 records) | 424/4640 0.091 [0.06, 0.15] (580 records) | -0.016 [-0.068, +0.022] |
| random_verdict | 1 | 0/128 0.000 [0, 0.19 one-sided] (16 records) | 0/16 0.000 [0, 0.78 one-sided] (2 records) | 71/1400 0.051 [0.02, 0.11] (175 records) | +0.000 [+0.000, +0.000] |
| random_verdict | 10 | 20/288 0.069 [0.03, 0.14] (36 records) | 14/176 0.080 [0.03, 0.17] (22 records) | 73/1080 0.068 [0.04, 0.13] (135 records) | -0.010 [-0.067, +0.047] |
| random_verdict | 100 | 33/456 0.072 [0.04, 0.12] (57 records) | 41/392 0.105 [0.06, 0.18] (49 records) | 55/696 0.079 [0.04, 0.14] (87 records) | -0.032 [-0.107, +0.016] |
| random_verdict | 1,000 | 13/104 0.125 [0.01, 0.35] (13 records) | 6/96 0.062 [0.01, 0.21] (12 records) | 14/120 0.117 [0.04, 0.27] (15 records) | +0.062 [-0.076, +0.278] |
| random_verdict | all budgets | 66/976 0.068 [0.04, 0.11] (122 records) | 61/680 0.090 [0.05, 0.15] (85 records) | 213/3296 0.065 [0.04, 0.12] (412 records) | -0.022 [-0.071, +0.015] |
