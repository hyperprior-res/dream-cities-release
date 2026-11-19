# Across emulators: does the cheap audit predict what reinforcement learning overstates? (COMPLETE)

**COMPLETE.** All 120 pairs have both variables of the main test.

Generated 2026-11-14T15:54:19Z by `PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/analyse_ladder.py`. Statistics fixed in the specification (and its round 2), the study protocol (section 1; amendments 3, 4, 7) and the analysis plan. Cluster bootstrap, 2000 resamples, seed 0, 95 per cent percentile intervals (`hpr_dream.stats`). Per-pair values: `pairs.csv`; figure data: `fig5_*.csv`; the main checkpoint on three city sets: `replication.md`; the coverage model: `coverage.md`.

City sets: the 40 cities (`tasks_v2_H24.json`, 193 instances), the 80 new cities (`tasks_v2x_H24.json`, 381 instances) and all 120 cities (both pooled: a pair's rate is events over the instances of both, its excess paired by instance against each file's perfect emulator). The main claim's audit variable is the 120-city value ; the 40 and the 80 are reported beside it.

## 1. Inputs

Ladder checkpoints found: 24 (protocol: 24); task families: grow, solvent, treasury, recover, power (40 cities: 40, 38, 40, 35, 40 instances; 80 cities: 77, 75, 80, 70, 79).

| checkpoint | objective | size | data (transitions) | stage | lineage | random, 40 | random, 80 | seeded, 40 | seeded, 80 | RL runs with all 3 snapshots (of 15) | fidelity dev | fidelity test | pairs with both main variables |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| os_100m_full-samples_003000064 | onestep | 100m | train_full (3,000,000) | half | os_100m_full | ok | ok | ok | absent | 15 | ok | absent | 5 |
| os_100m_full-samples_006000000 | onestep | 100m | train_full (3,000,000) | final | os_100m_full | ok | ok | ok | absent | 15 | ok | ok | 5 |
| os_100m_small-samples_003000064 | onestep | 100m | train_small (300,000) | half | os_100m_small | ok | ok | ok | absent | 15 | ok | absent | 5 |
| os_100m_small-samples_006000000 | onestep | 100m | train_small (300,000) | final | os_100m_small | ok | ok | ok | absent | 15 | ok | ok | 5 |
| os_15m_full-samples_003000064 | onestep | 15m | train_full (3,000,000) | half | os_15m_full | ok | ok | ok | absent | 15 | ok | absent | 5 |
| os_15m_full-samples_006000000 | onestep | 15m | train_full (3,000,000) | final | os_15m_full | ok | ok | ok | absent | 15 | ok | ok | 5 |
| os_15m_small-samples_003000064 | onestep | 15m | train_small (300,000) | half | os_15m_small | ok | ok | ok | absent | 15 | ok | absent | 5 |
| os_15m_small-samples_006000000 | onestep | 15m | train_small (300,000) | final | os_15m_small | ok | ok | ok | absent | 15 | ok | ok | 5 |
| os_50m_full-samples_003000064 | onestep | 50m | train_full (3,000,000) | half | os_50m_full | ok | ok | ok | absent | 15 | ok | absent | 5 |
| os_50m_full-samples_006000000 | onestep | 50m | train_full (3,000,000) | final | os_50m_full | ok | ok | ok | ok | 15 | ok | ok | 5 |
| os_50m_small-samples_003000064 | onestep | 50m | train_small (300,000) | half | os_50m_small | ok | ok | ok | absent | 15 | ok | absent | 5 |
| os_50m_small-samples_006000000 | onestep | 50m | train_small (300,000) | final | os_50m_small | ok | ok | ok | absent | 15 | ok | ok | 5 |
| sf_100m_full-samples_000750080 | selfforce | 100m | train_full (3,000,000) | half | os_100m_full | ok | ok | ok | absent | 15 | ok | absent | 5 |
| sf_100m_full-samples_001500032 | selfforce | 100m | train_full (3,000,000) | final | os_100m_full | ok | ok | ok | absent | 15 | ok | ok | 5 |
| sf_100m_small-samples_000750080 | selfforce | 100m | train_small (300,000) | half | os_100m_small | ok | ok | ok | absent | 15 | ok | absent | 5 |
| sf_100m_small-samples_001500032 | selfforce | 100m | train_small (300,000) | final | os_100m_small | ok | ok | ok | absent | 15 | ok | ok | 5 |
| sf_15m_full-samples_000750080 | selfforce | 15m | train_full (3,000,000) | half | os_15m_full | ok | ok | ok | absent | 15 | ok | absent | 5 |
| sf_15m_full-samples_001500032 | selfforce | 15m | train_full (3,000,000) | final | os_15m_full | ok | ok | ok | absent | 15 | ok | ok | 5 |
| sf_15m_small-samples_000750080 | selfforce | 15m | train_small (300,000) | half | os_15m_small | ok | ok | ok | absent | 15 | ok | absent | 5 |
| sf_15m_small-samples_001500032 | selfforce | 15m | train_small (300,000) | final | os_15m_small | ok | ok | ok | absent | 15 | ok | ok | 5 |
| sf_50m_full-samples_000750080 | selfforce | 50m | train_full (3,000,000) | half | os_50m_full | ok | ok | ok | absent | 15 | ok | absent | 5 |
| sf_50m_full-samples_001500032 | selfforce | 50m | train_full (3,000,000) | final | os_50m_full | ok | ok | ok | absent | 15 | ok | ok | 5 |
| sf_50m_small-samples_000750080 | selfforce | 50m | train_small (300,000) | half | os_50m_small | ok | ok | ok | absent | 15 | ok | absent | 5 |
| sf_50m_small-samples_001500032 | selfforce | 50m | train_small (300,000) | final | os_50m_small | ok | ok | ok | absent | 15 | ok | ok | 5 |

## 2. The protocol test, as amended

x: random search's false acceptance at 1,000 on the pair's instances. y: the RL variable, mean of three RL seeds of the frozen learner. Spearman over all pairs; cluster bootstrap by checkpoint. Decision rule (protocol): supported if the estimate is at least 0.4 and the interval excludes 0; falsified if the interval lies below 0.4; otherwise undecided at this power. It is applied to one row: all 120 cities against the margin inflation .

| x: cities | y | pairs | clusters (checkpoints) | Spearman [95 %] | Kendall [95 %] | lineages | Spearman, lineage clusters [95 %] | decision |
|---|---|---|---|---|---|---|---|---|
| all 120 cities | `rl_inflation_1000000` | 120 | 24 | +0.843 [+0.765, +0.904] | +0.682 [+0.612, +0.749] | 6 | +0.843 [+0.799, +0.894] | decision: supported |
| all 120 cities | `rl_gap_1000000` | 120 | 24 | +0.865 [+0.802, +0.914] | +0.691 [+0.620, +0.761] | 6 | +0.865 [+0.837, +0.895] | reported beside (no decision) |
| the 40 cities | `rl_inflation_1000000` | 120 | 24 | +0.829 [+0.759, +0.884] | +0.667 [+0.607, +0.729] | 6 | +0.829 [+0.791, +0.867] | reported beside (no decision) |
| the 40 cities | `rl_gap_1000000` | 120 | 24 | +0.826 [+0.764, +0.878] | +0.649 [+0.585, +0.715] | 6 | +0.826 [+0.793, +0.849] | reported beside (no decision) |
| the 80 new cities | `rl_inflation_1000000` | 120 | 24 | +0.839 [+0.756, +0.901] | +0.670 [+0.599, +0.742] | 6 | +0.839 [+0.787, +0.885] | reported beside (no decision) |
| the 80 new cities | `rl_gap_1000000` | 120 | 24 | +0.865 [+0.804, +0.913] | +0.690 [+0.624, +0.758] | 6 | +0.865 [+0.835, +0.891] | reported beside (no decision) |

Achieved, for the deciding row: 120 pairs in 24 clusters (5.00 pairs per cluster). Independent pairs needed for 80 per cent power at Spearman 0.4 (two-sided, 5 per cent, Fisher z): 47.
- At intra-checkpoint correlation 0.3 (the protocol's design effect 1 + (m - 1) rho): design effect 2.20, effective pairs 54.5, power to detect 0.4: 0.86.
- At intra-checkpoint correlation 0.5 (the protocol's design effect 1 + (m - 1) rho): design effect 3.00, effective pairs 40.0, power to detect 0.4: 0.73.
- Measured ICC(1) by checkpoint on these pairs: `random_c120_hack_1000` -0.088; `rl_inflation_1000000` -0.115; `rl_gap_1000000` -0.127.

## 3. Within task family

Spearman inside each family, one point per checkpoint (bootstrap over checkpoints); the mean of the family values (families with at least 3 pairs; bootstrap over checkpoints, every family recomputed on each resample); the pooled Spearman of within-family percentile ranks, (rank - 0.5) / n, recomputed on each resample. Columns: the three city sets of the audit variable.

### y: `rl_inflation_1000000`

| scope | pairs (120 / 40 / 80) | Spearman, 120 | Kendall, 120 | Spearman, 40 | Kendall, 40 | Spearman, 80 | Kendall, 80 |
|---|---|---|---|---|---|---|---|
| pooled | 120 / 120 / 120 | +0.843 [+0.765, +0.904] | +0.682 [+0.612, +0.749] | +0.829 [+0.759, +0.884] | +0.667 [+0.607, +0.729] | +0.839 [+0.756, +0.901] | +0.670 [+0.599, +0.742] |
| grow | 24 / 24 / 24 | +0.464 [+0.014, +0.779] | +0.352 [+0.000, +0.657] | +0.373 [-0.081, +0.740] | +0.290 [-0.074, +0.620] | +0.573 [+0.177, +0.841] | +0.453 [+0.147, +0.717] |
| solvent | 24 / 24 / 24 | +0.818 [+0.562, +0.944] | +0.667 [+0.431, +0.852] | +0.759 [+0.483, +0.930] | +0.648 [+0.402, +0.848] | +0.753 [+0.446, +0.911] | +0.592 [+0.334, +0.793] |
| treasury | 24 / 24 / 24 | +0.680 [+0.258, +0.926] | +0.552 [+0.229, +0.803] | +0.448 [+0.031, +0.767] | +0.334 [+0.036, +0.596] | +0.669 [+0.256, +0.912] | +0.537 [+0.203, +0.806] |
| recover | 24 / 24 / 24 | +0.734 [+0.468, +0.875] | +0.534 [+0.309, +0.733] | +0.669 [+0.327, +0.877] | +0.522 [+0.275, +0.732] | +0.726 [+0.434, +0.874] | +0.540 [+0.285, +0.742] |
| power | 24 / 24 / 24 | +0.068 [-0.398, +0.514] | +0.079 [-0.275, +0.398] | +0.071 [-0.369, +0.479] | +0.071 [-0.253, +0.386] | +0.086 [-0.395, +0.531] | +0.087 [-0.279, +0.413] |
| mean of families | 120 / 120 / 120 | +0.553 [+0.309, +0.726] | +0.437 [+0.248, +0.599] | +0.464 [+0.264, +0.617] | +0.373 [+0.218, +0.517] | +0.562 [+0.317, +0.738] | +0.442 [+0.251, +0.602] |
| pooled, ranked within family | 120 / 120 / 120 | +0.554 [+0.310, +0.724] | n/a | +0.478 [+0.260, +0.616] | n/a | +0.559 [+0.316, +0.732] | n/a |

- all 120 cities (complete): Spearman intervals that exclude 0: pooled, grow, solvent, treasury, recover, mean of families, pooled after ranking within family. Intervals that include 0: power.
- the 40 cities (complete): Spearman intervals that exclude 0: pooled, solvent, treasury, recover, mean of families, pooled after ranking within family. Intervals that include 0: grow, power.
- the 80 new cities (complete): Spearman intervals that exclude 0: pooled, grow, solvent, treasury, recover, mean of families, pooled after ranking within family. Intervals that include 0: power.

### y: `rl_gap_1000000`

| scope | pairs (120 / 40 / 80) | Spearman, 120 | Kendall, 120 | Spearman, 40 | Kendall, 40 | Spearman, 80 | Kendall, 80 |
|---|---|---|---|---|---|---|---|
| pooled | 120 / 120 / 120 | +0.865 [+0.802, +0.914] | +0.691 [+0.620, +0.761] | +0.826 [+0.764, +0.878] | +0.649 [+0.585, +0.715] | +0.865 [+0.804, +0.913] | +0.690 [+0.624, +0.758] |
| grow | 24 / 24 / 24 | +0.726 [+0.364, +0.921] | +0.589 [+0.281, +0.816] | +0.612 [+0.212, +0.846] | +0.491 [+0.173, +0.729] | +0.742 [+0.465, +0.889] | +0.593 [+0.353, +0.776] |
| solvent | 24 / 24 / 24 | +0.846 [+0.575, +0.976] | +0.740 [+0.486, +0.921] | +0.778 [+0.504, +0.917] | +0.624 [+0.395, +0.805] | +0.797 [+0.453, +0.962] | +0.674 [+0.377, +0.883] |
| treasury | 24 / 24 / 24 | +0.771 [+0.468, +0.908] | +0.588 [+0.339, +0.765] | +0.575 [+0.268, +0.769] | +0.424 [+0.210, +0.615] | +0.766 [+0.433, +0.922] | +0.603 [+0.326, +0.801] |
| recover | 24 / 24 / 24 | +0.665 [+0.377, +0.847] | +0.505 [+0.281, +0.714] | +0.584 [+0.246, +0.826] | +0.462 [+0.217, +0.694] | +0.676 [+0.369, +0.852] | +0.517 [+0.293, +0.715] |
| power | 24 / 24 / 24 | -0.252 [-0.624, +0.169] | -0.174 [-0.473, +0.146] | -0.341 [-0.657, +0.052] | -0.242 [-0.516, +0.059] | -0.214 [-0.618, +0.237] | -0.164 [-0.489, +0.188] |
| mean of families | 120 / 120 / 120 | +0.551 [+0.369, +0.682] | +0.450 [+0.303, +0.584] | +0.441 [+0.267, +0.582] | +0.352 [+0.216, +0.483] | +0.553 [+0.372, +0.690] | +0.445 [+0.297, +0.577] |
| pooled, ranked within family | 120 / 120 / 120 | +0.554 [+0.369, +0.685] | n/a | +0.460 [+0.264, +0.583] | n/a | +0.552 [+0.370, +0.689] | n/a |

- all 120 cities (complete): Spearman intervals that exclude 0: pooled, grow, solvent, treasury, recover, mean of families, pooled after ranking within family. Intervals that include 0: power.
- the 40 cities (complete): Spearman intervals that exclude 0: pooled, grow, solvent, treasury, recover, mean of families, pooled after ranking within family. Intervals that include 0: power.
- the 80 new cities (complete): Spearman intervals that exclude 0: pooled, grow, solvent, treasury, recover, mean of families, pooled after ranking within family. Intervals that include 0: power.

## 4. Reliability

Per family, over the pairs of the main test (each city set's own pairs). Audit: the binomial standard error of each pair's false acceptance, sqrt(p (1 - p) / n) with n the pair's instances, against the standard deviation of the pair values across checkpoints. RL: the standard error of each pair's three-seed mean, (seed standard deviation) / sqrt(3), against the standard deviation of the means across checkpoints. Reliability lambda = 1 - mean(SE^2) / variance across checkpoints. Attenuation (classical formula, for a linear correlation): r_observed = r_true x sqrt(lambda_audit x lambda_RL), a lambda at or below 0 entering as 0.

### y: `rl_inflation_1000000`

| family | cities | pairs | audit RMS SE | audit SD across checkpoints | lambda audit | RL seed SD (RMS) | RL SE of the mean (RMS) | RL SD across checkpoints | lambda RL | attenuation factor | observed value of a true 0.4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| grow | 120 | 24 | 0.022 | 0.070 | 0.90 | 0.034 | 0.020 | 0.254 | 0.99 | 0.95 | 0.38 |
| grow | 40 | 24 | 0.036 | 0.058 | 0.63 | 0.034 | 0.020 | 0.254 | 0.99 | 0.79 | 0.32 |
| grow | 80 | 24 | 0.028 | 0.079 | 0.88 | 0.034 | 0.020 | 0.254 | 0.99 | 0.93 | 0.37 |
| solvent | 120 | 24 | 0.024 | 0.070 | 0.88 | 0.033 | 0.019 | 0.202 | 0.99 | 0.93 | 0.37 |
| solvent | 40 | 24 | 0.044 | 0.070 | 0.61 | 0.033 | 0.019 | 0.202 | 0.99 | 0.78 | 0.31 |
| solvent | 80 | 24 | 0.029 | 0.073 | 0.84 | 0.033 | 0.019 | 0.202 | 0.99 | 0.91 | 0.36 |
| treasury | 120 | 24 | 0.040 | 0.078 | 0.73 | 0.029 | 0.017 | 0.078 | 0.95 | 0.84 | 0.33 |
| treasury | 40 | 24 | 0.070 | 0.077 | 0.17 | 0.029 | 0.017 | 0.078 | 0.95 | 0.40 | 0.16 |
| treasury | 80 | 24 | 0.049 | 0.089 | 0.70 | 0.029 | 0.017 | 0.078 | 0.95 | 0.82 | 0.33 |
| recover | 120 | 24 | 0.047 | 0.072 | 0.58 | 0.037 | 0.021 | 0.281 | 0.99 | 0.76 | 0.30 |
| recover | 40 | 24 | 0.082 | 0.087 | 0.13 | 0.037 | 0.021 | 0.281 | 0.99 | 0.36 | 0.14 |
| recover | 80 | 24 | 0.056 | 0.069 | 0.34 | 0.037 | 0.021 | 0.281 | 0.99 | 0.58 | 0.23 |
| power | 120 | 24 | 0.025 | 0.048 | 0.72 | 0.075 | 0.043 | 0.288 | 0.98 | 0.84 | 0.34 |
| power | 40 | 24 | 0.043 | 0.062 | 0.50 | 0.075 | 0.043 | 0.288 | 0.98 | 0.70 | 0.28 |
| power | 80 | 24 | 0.031 | 0.048 | 0.58 | 0.075 | 0.043 | 0.288 | 0.98 | 0.75 | 0.30 |

### y: `rl_gap_1000000`

| family | cities | pairs | audit RMS SE | audit SD across checkpoints | lambda audit | RL seed SD (RMS) | RL SE of the mean (RMS) | RL SD across checkpoints | lambda RL | attenuation factor | observed value of a true 0.4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| grow | 120 | 24 | 0.022 | 0.070 | 0.90 | 0.018 | 0.010 | 0.095 | 0.99 | 0.94 | 0.38 |
| grow | 40 | 24 | 0.036 | 0.058 | 0.63 | 0.018 | 0.010 | 0.095 | 0.99 | 0.79 | 0.31 |
| grow | 80 | 24 | 0.028 | 0.079 | 0.88 | 0.018 | 0.010 | 0.095 | 0.99 | 0.93 | 0.37 |
| solvent | 120 | 24 | 0.024 | 0.070 | 0.88 | 0.017 | 0.010 | 0.076 | 0.98 | 0.93 | 0.37 |
| solvent | 40 | 24 | 0.044 | 0.070 | 0.61 | 0.017 | 0.010 | 0.076 | 0.98 | 0.78 | 0.31 |
| solvent | 80 | 24 | 0.029 | 0.073 | 0.84 | 0.017 | 0.010 | 0.076 | 0.98 | 0.91 | 0.36 |
| treasury | 120 | 24 | 0.040 | 0.078 | 0.73 | 0.038 | 0.022 | 0.098 | 0.95 | 0.83 | 0.33 |
| treasury | 40 | 24 | 0.070 | 0.077 | 0.17 | 0.038 | 0.022 | 0.098 | 0.95 | 0.40 | 0.16 |
| treasury | 80 | 24 | 0.049 | 0.089 | 0.70 | 0.038 | 0.022 | 0.098 | 0.95 | 0.81 | 0.33 |
| recover | 120 | 24 | 0.047 | 0.072 | 0.58 | 0.023 | 0.013 | 0.119 | 0.99 | 0.76 | 0.30 |
| recover | 40 | 24 | 0.082 | 0.087 | 0.13 | 0.023 | 0.013 | 0.119 | 0.99 | 0.36 | 0.14 |
| recover | 80 | 24 | 0.056 | 0.069 | 0.34 | 0.023 | 0.013 | 0.119 | 0.99 | 0.58 | 0.23 |
| power | 120 | 24 | 0.025 | 0.048 | 0.72 | 0.016 | 0.009 | 0.017 | 0.72 | 0.72 | 0.29 |
| power | 40 | 24 | 0.043 | 0.062 | 0.50 | 0.016 | 0.009 | 0.017 | 0.72 | 0.60 | 0.24 |
| power | 80 | 24 | 0.031 | 0.048 | 0.58 | 0.016 | 0.009 | 0.017 | 0.72 | 0.64 | 0.26 |

### Split-sample reliability of the audit variable

Per family, across every checkpoint audited on both city files (no RL variable needed): Spearman and Pearson between a pair's 40-city and 80-city false acceptance at 1,000 (random search). Spearman-Brown for forms of unequal length: with k1 and k2 the instance counts, r = sqrt(rho(k1) rho(k2)) and rho(k) = k rho_1 / (1 + (k - 1) rho_1); solved for the per-instance rho_1 from Pearson's r, it gives the reliability of the 40, the 80 and the pooled 120. Beside it, the binomial-formula reliability of each on the same checkpoints.

| family | checkpoints with both | Spearman 40 vs 80 | Pearson 40 vs 80 | Spearman-Brown: 40 | 80 | pooled 120 | binomial: 40 | 80 | pooled 120 |
|---|---|---|---|---|---|---|---|---|---|
| grow | 24 | 0.580 | 0.843 | 0.80 | 0.89 | 0.92 | 0.63 | 0.88 | 0.90 |
| solvent | 24 | 0.709 | 0.858 | 0.82 | 0.90 | 0.93 | 0.61 | 0.84 | 0.88 |
| treasury | 24 | 0.585 | 0.621 | 0.55 | 0.71 | 0.78 | 0.17 | 0.70 | 0.73 |
| recover | 24 | 0.824 | 0.794 | 0.74 | 0.85 | 0.90 | 0.13 | 0.34 | 0.58 |
| power | 24 | 0.594 | 0.663 | 0.59 | 0.74 | 0.81 | 0.50 | 0.58 | 0.72 |

## 5. Alternatives (a fixed table, not a search)

The same pooled and within-family statistics with the audit variable replaced. Fidelity numbers are per checkpoint (constant across its five families); the test selection holds finals only. For fidelity rows, the secondary claim's question: is |pooled Spearman| below 0.3?

### y: `rl_inflation_1000000`

| x | pairs | checkpoints | lineages | pooled Spearman | pooled Kendall | pooled Spearman, lineage clusters | within-family mean Spearman | within-family mean Kendall | ranked within family | abs < 0.3 |
|---|---|---|---|---|---|---|---|---|---|---|
| random search: false acceptance at 1,000, all 120 cities | 120 | 24 | 6 | +0.843 [+0.765, +0.904] | +0.682 [+0.612, +0.749] | +0.843 [+0.799, +0.894] | +0.553 [+0.309, +0.726] | +0.437 [+0.248, +0.599] | +0.554 [+0.310, +0.724] |  |
| random search: false acceptance at 1,000, the 40 cities | 120 | 24 | 6 | +0.829 [+0.759, +0.884] | +0.667 [+0.607, +0.729] | +0.829 [+0.791, +0.867] | +0.464 [+0.264, +0.617] | +0.373 [+0.218, +0.517] | +0.478 [+0.260, +0.616] |  |
| random search: false acceptance at 1,000, the 80 new cities | 120 | 24 | 6 | +0.839 [+0.756, +0.901] | +0.670 [+0.599, +0.742] | +0.839 [+0.787, +0.885] | +0.562 [+0.317, +0.738] | +0.442 [+0.251, +0.602] | +0.559 [+0.316, +0.732] |  |
| pool-seeded search: false acceptance at 1,000, all 120 cities | 5 | 1 | 1 | +1.000 [1 cluster: no interval] | +1.000 [1 cluster: no interval] | +1.000 [1 cluster: no interval] | n/a | n/a | n/a |  |
| pool-seeded search: false acceptance at 1,000, the 40 cities | 120 | 24 | 6 | +0.839 [+0.803, +0.870] | +0.650 [+0.614, +0.691] | +0.839 [+0.816, +0.876] | +0.507 [+0.306, +0.651] | +0.381 [+0.236, +0.515] | +0.505 [+0.307, +0.652] |  |
| pool-seeded search: false acceptance at 1,000, the 80 new cities | 5 | 1 | 1 | +1.000 [1 cluster: no interval] | +1.000 [1 cluster: no interval] | +1.000 [1 cluster: no interval] | n/a | n/a | n/a |  |
| random search: excess over the perfect emulator at 1,000 (paired), all 120 cities | 120 | 24 | 6 | +0.790 [+0.755, +0.821] | +0.585 [+0.548, +0.624] | +0.790 [+0.754, +0.810] | +0.553 [+0.309, +0.726] | +0.437 [+0.248, +0.599] | +0.554 [+0.310, +0.724] |  |
| random search: excess over the perfect emulator at 1,000 (paired), the 40 cities | 120 | 24 | 6 | +0.796 [+0.761, +0.826] | +0.596 [+0.555, +0.636] | +0.796 [+0.754, +0.820] | +0.464 [+0.264, +0.617] | +0.373 [+0.218, +0.517] | +0.478 [+0.260, +0.616] |  |
| random search: excess over the perfect emulator at 1,000 (paired), the 80 new cities | 120 | 24 | 6 | +0.762 [+0.709, +0.811] | +0.557 [+0.504, +0.609] | +0.762 [+0.721, +0.785] | +0.562 [+0.317, +0.738] | +0.442 [+0.251, +0.602] | +0.559 [+0.316, +0.732] |  |
| pool-seeded search: excess over the perfect emulator at 1,000 (paired), all 120 cities | 5 | 1 | 1 | +0.900 [1 cluster: no interval] | +0.800 [1 cluster: no interval] | +0.900 [1 cluster: no interval] | n/a | n/a | n/a |  |
| pool-seeded search: excess over the perfect emulator at 1,000 (paired), the 40 cities | 120 | 24 | 6 | +0.734 [+0.678, +0.788] | +0.537 [+0.483, +0.600] | +0.734 [+0.702, +0.763] | +0.507 [+0.306, +0.651] | +0.381 [+0.236, +0.515] | +0.505 [+0.307, +0.652] |  |
| pool-seeded search: excess over the perfect emulator at 1,000 (paired), the 80 new cities | 5 | 1 | 1 | +0.900 [1 cluster: no interval] | +0.800 [1 cluster: no interval] | +0.900 [1 cluster: no interval] | n/a | n/a | n/a |  |
| fidelity, development selection: structural changed-tile F1, one month | 120 | 24 | 6 | +0.098 [-0.073, +0.221] | +0.047 [-0.069, +0.136] | +0.098 [-0.113, +0.225] | +0.142 [-0.208, +0.432] | +0.052 [-0.202, +0.269] | +0.142 [-0.209, +0.432] | yes |
| fidelity, development selection: structural changed-since-start tile F1, 12 months | 120 | 24 | 6 | +0.144 [-0.035, +0.283] | +0.101 [-0.023, +0.204] | +0.144 [-0.086, +0.311] | +0.186 [-0.205, +0.514] | +0.138 [-0.147, +0.385] | +0.186 [-0.202, +0.513] | yes |
| fidelity, development selection: funds, median relative error, 12 months | 120 | 24 | 6 | +0.001 [-0.146, +0.141] | +0.001 [-0.102, +0.100] | +0.001 [-0.146, +0.178] | -0.030 [-0.364, +0.303] | -0.020 [-0.261, +0.221] | -0.030 [-0.362, +0.298] | yes |
| fidelity, development selection: population, median relative error, 12 months | 120 | 24 | 6 | -0.205 [-0.301, -0.068] | -0.146 [-0.228, -0.049] | -0.205 [-0.318, -0.033] | -0.414 [-0.630, -0.113] | -0.297 [-0.495, -0.079] | -0.414 [-0.630, -0.112] | yes |
| fidelity, test selection (finals only): structural changed-tile F1, one month | 60 | 12 | 6 | +0.063 [-0.193, +0.218] | +0.025 [-0.138, +0.134] | +0.063 [-0.149, +0.208] | +0.085 [-0.509, +0.484] | +0.006 [-0.416, +0.303] | +0.085 [-0.509, +0.478] | yes |
| fidelity, test selection (finals only): structural changed-since-start tile F1, 12 months | 60 | 12 | 6 | +0.109 [-0.166, +0.292] | +0.063 [-0.136, +0.220] | +0.109 [-0.187, +0.278] | +0.162 [-0.467, +0.617] | +0.085 [-0.413, +0.493] | +0.162 [-0.446, +0.608] | yes |
| fidelity, test selection (finals only): funds, median relative error, 12 months | 60 | 12 | 6 | -0.101 [-0.262, +0.096] | -0.068 [-0.195, +0.073] | -0.101 [-0.271, +0.055] | -0.203 [-0.618, +0.304] | -0.158 [-0.507, +0.222] | -0.203 [-0.614, +0.303] | yes |
| fidelity, test selection (finals only): population, median relative error, 12 months | 60 | 12 | 6 | -0.188 [-0.311, +0.008] | -0.133 [-0.244, +0.006] | -0.188 [-0.320, +0.016] | -0.387 [-0.708, +0.104] | -0.279 [-0.574, +0.071] | -0.387 [-0.705, +0.101] | yes |

### y: `rl_gap_1000000`

| x | pairs | checkpoints | lineages | pooled Spearman | pooled Kendall | pooled Spearman, lineage clusters | within-family mean Spearman | within-family mean Kendall | ranked within family | abs < 0.3 |
|---|---|---|---|---|---|---|---|---|---|---|
| random search: false acceptance at 1,000, all 120 cities | 120 | 24 | 6 | +0.865 [+0.802, +0.914] | +0.691 [+0.620, +0.761] | +0.865 [+0.837, +0.895] | +0.551 [+0.369, +0.682] | +0.450 [+0.303, +0.584] | +0.554 [+0.369, +0.685] |  |
| random search: false acceptance at 1,000, the 40 cities | 120 | 24 | 6 | +0.826 [+0.764, +0.878] | +0.649 [+0.585, +0.715] | +0.826 [+0.793, +0.849] | +0.441 [+0.267, +0.582] | +0.352 [+0.216, +0.483] | +0.460 [+0.264, +0.583] |  |
| random search: false acceptance at 1,000, the 80 new cities | 120 | 24 | 6 | +0.865 [+0.804, +0.913] | +0.690 [+0.624, +0.758] | +0.865 [+0.835, +0.891] | +0.553 [+0.372, +0.690] | +0.445 [+0.297, +0.577] | +0.552 [+0.370, +0.689] |  |
| pool-seeded search: false acceptance at 1,000, all 120 cities | 5 | 1 | 1 | +0.900 [1 cluster: no interval] | +0.800 [1 cluster: no interval] | +0.900 [1 cluster: no interval] | n/a | n/a | n/a |  |
| pool-seeded search: false acceptance at 1,000, the 40 cities | 120 | 24 | 6 | +0.794 [+0.733, +0.850] | +0.617 [+0.557, +0.681] | +0.794 [+0.760, +0.824] | +0.534 [+0.355, +0.656] | +0.403 [+0.265, +0.523] | +0.530 [+0.353, +0.656] |  |
| pool-seeded search: false acceptance at 1,000, the 80 new cities | 5 | 1 | 1 | +0.900 [1 cluster: no interval] | +0.800 [1 cluster: no interval] | +0.900 [1 cluster: no interval] | n/a | n/a | n/a |  |
| random search: excess over the perfect emulator at 1,000 (paired), all 120 cities | 120 | 24 | 6 | +0.780 [+0.729, +0.821] | +0.572 [+0.520, +0.621] | +0.780 [+0.736, +0.805] | +0.551 [+0.369, +0.682] | +0.450 [+0.303, +0.584] | +0.554 [+0.369, +0.685] |  |
| random search: excess over the perfect emulator at 1,000 (paired), the 40 cities | 120 | 24 | 6 | +0.760 [+0.707, +0.809] | +0.557 [+0.504, +0.610] | +0.760 [+0.730, +0.790] | +0.441 [+0.267, +0.582] | +0.352 [+0.216, +0.483] | +0.460 [+0.264, +0.583] |  |
| random search: excess over the perfect emulator at 1,000 (paired), the 80 new cities | 120 | 24 | 6 | +0.768 [+0.709, +0.813] | +0.563 [+0.513, +0.611] | +0.768 [+0.723, +0.796] | +0.553 [+0.372, +0.690] | +0.445 [+0.297, +0.577] | +0.552 [+0.370, +0.689] |  |
| pool-seeded search: excess over the perfect emulator at 1,000 (paired), all 120 cities | 5 | 1 | 1 | +0.800 [1 cluster: no interval] | +0.600 [1 cluster: no interval] | +0.800 [1 cluster: no interval] | n/a | n/a | n/a |  |
| pool-seeded search: excess over the perfect emulator at 1,000 (paired), the 40 cities | 120 | 24 | 6 | +0.665 [+0.568, +0.754] | +0.490 [+0.408, +0.574] | +0.665 [+0.621, +0.707] | +0.534 [+0.355, +0.656] | +0.403 [+0.265, +0.523] | +0.530 [+0.353, +0.656] |  |
| pool-seeded search: excess over the perfect emulator at 1,000 (paired), the 80 new cities | 5 | 1 | 1 | +0.700 [1 cluster: no interval] | +0.600 [1 cluster: no interval] | +0.700 [1 cluster: no interval] | n/a | n/a | n/a |  |
| fidelity, development selection: structural changed-tile F1, one month | 120 | 24 | 6 | -0.094 [-0.232, +0.055] | -0.070 [-0.169, +0.032] | -0.094 [-0.254, +0.052] | -0.162 [-0.435, +0.129] | -0.127 [-0.333, +0.076] | -0.162 [-0.434, +0.132] | yes |
| fidelity, development selection: structural changed-since-start tile F1, 12 months | 120 | 24 | 6 | -0.063 [-0.215, +0.095] | -0.045 [-0.153, +0.061] | -0.063 [-0.288, +0.137] | -0.111 [-0.403, +0.186] | -0.076 [-0.297, +0.146] | -0.111 [-0.405, +0.187] | yes |
| fidelity, development selection: funds, median relative error, 12 months | 120 | 24 | 6 | +0.026 [-0.138, +0.192] | +0.018 [-0.099, +0.138] | +0.026 [-0.076, +0.166] | +0.067 [-0.274, +0.382] | +0.046 [-0.190, +0.288] | +0.067 [-0.271, +0.381] | yes |
| fidelity, development selection: population, median relative error, 12 months | 120 | 24 | 6 | -0.117 [-0.249, +0.048] | -0.082 [-0.179, +0.032] | -0.117 [-0.241, +0.104] | -0.287 [-0.528, +0.000] | -0.212 [-0.400, -0.007] | -0.288 [-0.527, +0.001] | yes |
| fidelity, test selection (finals only): structural changed-tile F1, one month | 60 | 12 | 6 | -0.145 [-0.314, +0.052] | -0.108 [-0.237, +0.029] | -0.145 [-0.319, +0.063] | -0.268 [-0.596, +0.127] | -0.209 [-0.485, +0.072] | -0.271 [-0.595, +0.125] | yes |
| fidelity, test selection (finals only): structural changed-since-start tile F1, 12 months | 60 | 12 | 6 | -0.085 [-0.299, +0.152] | -0.058 [-0.221, +0.109] | -0.085 [-0.343, +0.166] | -0.196 [-0.618, +0.303] | -0.142 [-0.510, +0.234] | -0.199 [-0.618, +0.296] | yes |
| fidelity, test selection (finals only): funds, median relative error, 12 months | 60 | 12 | 6 | -0.017 [-0.241, +0.217] | -0.016 [-0.179, +0.154] | -0.017 [-0.202, +0.145] | -0.051 [-0.552, +0.412] | -0.058 [-0.433, +0.310] | -0.049 [-0.547, +0.401] | yes |
| fidelity, test selection (finals only): population, median relative error, 12 months | 60 | 12 | 6 | -0.177 [-0.321, +0.071] | -0.128 [-0.246, +0.048] | -0.177 [-0.334, +0.028] | -0.351 [-0.680, +0.142] | -0.277 [-0.555, +0.069] | -0.351 [-0.676, +0.136] | yes |

## 6. The secondary claim as protocol (fidelity against random search's false acceptance at 1,000)

protocol: static fidelity correlates with false acceptance at 1,000 across the ladder at |Spearman| under 0.3; falsified if the interval on |Spearman| lies above 0.3 (here: the interval lies wholly above 0.3 or wholly below -0.3). Pairs with the audit variable; no RL variable needed. The 120-city audit variable first, the 40 and the 80 beside it.

| x | cities | pairs | checkpoints | pooled Spearman | within-family mean Spearman | abs < 0.3 | interval on abs above 0.3 |
|---|---|---|---|---|---|---|---|
| fidelity, development selection: structural changed-tile F1, one month | 120 | 120 | 24 | -0.076 [-0.226, +0.070] | -0.130 [-0.393, +0.151] | yes | no |
| fidelity, development selection: structural changed-since-start tile F1, 12 months | 120 | 120 | 24 | -0.068 [-0.229, +0.098] | -0.121 [-0.405, +0.198] | yes | no |
| fidelity, development selection: funds, median relative error, 12 months | 120 | 120 | 24 | -0.041 [-0.194, +0.131] | -0.143 [-0.439, +0.162] | yes | no |
| fidelity, development selection: population, median relative error, 12 months | 120 | 120 | 24 | -0.029 [-0.167, +0.116] | -0.089 [-0.351, +0.183] | yes | no |
| fidelity, test selection (finals only): structural changed-tile F1, one month | 120 | 60 | 12 | -0.056 [-0.268, +0.137] | -0.119 [-0.558, +0.307] | yes | no |
| fidelity, test selection (finals only): structural changed-since-start tile F1, 12 months | 120 | 60 | 12 | +0.012 [-0.225, +0.232] | +0.023 [-0.478, +0.503] | yes | no |
| fidelity, test selection (finals only): funds, median relative error, 12 months | 120 | 60 | 12 | -0.013 [-0.224, +0.223] | -0.064 [-0.532, +0.404] | yes | no |
| fidelity, test selection (finals only): population, median relative error, 12 months | 120 | 60 | 12 | -0.114 [-0.276, +0.113] | -0.256 [-0.644, +0.260] | yes | no |
| fidelity, development selection: structural changed-tile F1, one month | 40 | 120 | 24 | -0.056 [-0.197, +0.066] | -0.146 [-0.386, +0.088] | yes | no |
| fidelity, development selection: structural changed-since-start tile F1, 12 months | 40 | 120 | 24 | -0.033 [-0.166, +0.087] | -0.090 [-0.325, +0.145] | yes | no |
| fidelity, development selection: funds, median relative error, 12 months | 40 | 120 | 24 | -0.024 [-0.152, +0.113] | -0.076 [-0.325, +0.181] | yes | no |
| fidelity, development selection: population, median relative error, 12 months | 40 | 120 | 24 | -0.011 [-0.104, +0.097] | -0.032 [-0.229, +0.182] | yes | no |
| fidelity, test selection (finals only): structural changed-tile F1, one month | 40 | 60 | 12 | -0.024 [-0.209, +0.147] | -0.152 [-0.524, +0.209] | yes | no |
| fidelity, test selection (finals only): structural changed-since-start tile F1, 12 months | 40 | 60 | 12 | +0.019 [-0.179, +0.197] | -0.054 [-0.436, +0.310] | yes | no |
| fidelity, test selection (finals only): funds, median relative error, 12 months | 40 | 60 | 12 | -0.018 [-0.176, +0.165] | -0.012 [-0.351, +0.373] | yes | no |
| fidelity, test selection (finals only): population, median relative error, 12 months | 40 | 60 | 12 | -0.065 [-0.204, +0.100] | -0.128 [-0.480, +0.223] | yes | no |
| fidelity, development selection: structural changed-tile F1, one month | 80 | 120 | 24 | -0.081 [-0.240, +0.074] | -0.101 [-0.366, +0.183] | yes | no |
| fidelity, development selection: structural changed-since-start tile F1, 12 months | 80 | 120 | 24 | -0.085 [-0.255, +0.086] | -0.115 [-0.415, +0.215] | yes | no |
| fidelity, development selection: funds, median relative error, 12 months | 80 | 120 | 24 | -0.040 [-0.207, +0.149] | -0.143 [-0.455, +0.177] | yes | no |
| fidelity, development selection: population, median relative error, 12 months | 80 | 120 | 24 | -0.030 [-0.182, +0.130] | -0.115 [-0.394, +0.166] | yes | no |
| fidelity, test selection (finals only): structural changed-tile F1, one month | 80 | 60 | 12 | -0.055 [-0.287, +0.159] | -0.057 [-0.505, +0.384] | yes | no |
| fidelity, test selection (finals only): structural changed-since-start tile F1, 12 months | 80 | 60 | 12 | +0.017 [-0.249, +0.262] | +0.096 [-0.427, +0.609] | yes | no |
| fidelity, test selection (finals only): funds, median relative error, 12 months | 80 | 60 | 12 | -0.008 [-0.249, +0.267] | -0.090 [-0.605, +0.388] | yes | no |
| fidelity, test selection (finals only): population, median relative error, 12 months | 80 | 60 | 12 | -0.118 [-0.302, +0.139] | -0.301 [-0.696, +0.223] | yes | no |

### The two further protocol measures: held-out likelihood, fixed-candidate decision fidelity

Definitions fixed in the analysis plan before any of these correlations was computed; the same pairs, statistics and rule as the rows above. Held-out likelihood: the total bound (ELBO) in nats per transition of the test-selection file (`onestep.loglik_nats_per_transition.elbo`), components not tested separately. Fixed-candidate decision fidelity (the study brief, K = 2): per instance, Spearman's rho between the emulator's mean margin over its two search samples and the engine's margin (the majority oracle's) on the instance's first 100 logged behaviour plans; the mean over instances, leaving out those where either side is constant. Both on the final checkpoints. Random search selects on the same emulator scores, so this measure's verdict is read on disjoint cities: the measure on the 40 cities against false acceptance on the 80 new ones (the row marked **verdict**); the reverse and the same-city rows beside it.

| x | x: cities | false acceptance at 1,000: cities | pairs | checkpoints | pooled Spearman | within-family mean Spearman | abs < 0.3 | interval on abs above 0.3 | row |
|---|---|---|---|---|---|---|---|---|---|
| fidelity, test selection (finals only): held-out likelihood, the total bound (ELBO), nats per transition | test selection | 120 | 60 | 12 of 12 finals | -0.031 [-0.223, +0.168] | -0.084 [-0.530, +0.372] | yes | no |  |
| fidelity, test selection (finals only): held-out likelihood, the total bound (ELBO), nats per transition | test selection | 40 | 60 | 12 of 12 finals | -0.101 [-0.235, +0.050] | -0.265 [-0.536, +0.038] | yes | no |  |
| fidelity, test selection (finals only): held-out likelihood, the total bound (ELBO), nats per transition | test selection | 80 | 60 | 12 of 12 finals | +0.013 [-0.195, +0.226] | +0.040 [-0.422, +0.498] | yes | no |  |
| fixed-candidate decision fidelity on the 40 cities (finals only): mean over instances of the Spearman correlation between the emulator's two-sample mean margin and the engine's margin, first 100 behaviour plans | 40 | 80 | 60 | 12 of 12 finals | +0.114 [-0.119, +0.283] | +0.325 [-0.122, +0.660] | yes | no | **verdict** |
| fixed-candidate decision fidelity on the 80 new cities (finals only): mean over instances of the Spearman correlation between the emulator's two-sample mean margin and the engine's margin, first 100 behaviour plans | 80 | 40 | 0 | 0 of 12 finals | not computed | | | | beside |
| fixed-candidate decision fidelity on all 120 cities (finals only): mean over instances of the Spearman correlation between the emulator's two-sample mean margin and the engine's margin, first 100 behaviour plans | 120 | 120 | 0 | 0 of 12 finals | not computed | | | | beside |
| fixed-candidate decision fidelity on the 40 cities (finals only): mean over instances of the Spearman correlation between the emulator's two-sample mean margin and the engine's margin, first 100 behaviour plans | 40 | 40 | 60 | 12 of 12 finals | +0.104 [-0.041, +0.239] | +0.104 [-0.204, +0.434] | yes | no | beside |
| fixed-candidate decision fidelity on the 80 new cities (finals only): mean over instances of the Spearman correlation between the emulator's two-sample mean margin and the engine's margin, first 100 behaviour plans | 80 | 80 | 0 | 0 of 12 finals | not computed | | | | beside |

- `fid_decision_c80|c40` not computed: 12 of 12 finals: not computable: no run under <repo>/results/audit/engine_reference/tasks_v2x_H24 stores the truth-seed pool mean (truth_pool_mean_behaviour) of every instance, from which the engine's nine-seed mean follows: the emulator's two-sample margins cannot be recovered from the audits' residuals.
- `fid_decision_c120|c120` not computed: 12 of 12 finals: tasks_v2x_H24: not computable: no run under <repo>/results/audit/engine_reference/tasks_v2x_H24 stores the truth-seed pool mean (truth_pool_mean_behaviour) of every instance, from which the engine's nine-seed mean follows: the emulator's two-sample margins cannot be recovered from the audits' residuals.
- `fid_decision_c80|c80` not computed: 12 of 12 finals: not computable: no run under <repo>/results/audit/engine_reference/tasks_v2x_H24 stores the truth-seed pool mean (truth_pool_mean_behaviour) of every instance, from which the engine's nine-seed mean follows: the emulator's two-sample margins cannot be recovered from the audits' residuals.

Per final checkpoint. Decision fidelity: the mean over instances [instances with a rank correlation; left out: emulator constant / engine constant / both]; the recovery check (random-search records whose selected row's recovered margin equals the record's `grader_score`, and the largest error); the second reading (where the audit stores the 8-sample pass share of the first 100 plans: the mean, over instances with both, of the probability that a plan the emulator accepts has the higher recovered margin than one it rejects).

| checkpoint | held-out likelihood (nats / transition) | decision fidelity, 40 | recovery check, 40 | second reading, 40 | decision fidelity, 80 |
|---|---|---|---|---|---|
| os_100m_full-samples_006000000 | -2525.35 | 0.680 [193; 0 / 0 / 0] | 772 records, max error 4.4e-16 | not stored | not computable (below) |
| os_100m_small-samples_006000000 | -3613.74 | 0.681 [193; 0 / 0 / 0] | 772 records, max error 1.3e-15 | not stored | not computable (below) |
| os_15m_full-samples_006000000 | -2723.70 | 0.721 [193; 0 / 0 / 0] | 772 records, max error 1.3e-15 | 0.899 (100 instances) | not computable (below) |
| os_15m_small-samples_006000000 | -3013.26 | 0.680 [193; 0 / 0 / 0] | 772 records, max error 4.4e-16 | 0.881 (101 instances) | not computable (below) |
| os_50m_full-samples_006000000 | -2610.38 | 0.669 [193; 0 / 0 / 0] | 772 records, max error 1.6e-15 | 0.859 (106 instances) | not computable (below) |
| os_50m_small-samples_006000000 | -3376.88 | 0.689 [193; 0 / 0 / 0] | 772 records, max error 1.3e-15 | 0.874 (111 instances) | not computable (below) |
| sf_100m_full-samples_001500032 | -2551.96 | 0.690 [193; 0 / 0 / 0] | 772 records, max error 1.6e-15 | not stored | not computable (below) |
| sf_100m_small-samples_001500032 | -3457.93 | 0.574 [193; 0 / 0 / 0] | 772 records, max error 1.8e-15 | not stored | not computable (below) |
| sf_15m_full-samples_001500032 | -2762.38 | 0.641 [193; 0 / 0 / 0] | 772 records, max error 1.4e-15 | 0.848 (128 instances) | not computable (below) |
| sf_15m_small-samples_001500032 | -3009.65 | 0.608 [193; 0 / 0 / 0] | 772 records, max error 4.4e-16 | 0.822 (103 instances) | not computable (below) |
| sf_50m_full-samples_001500032 | -2648.47 | 0.621 [193; 0 / 0 / 0] | 772 records, max error 4.4e-16 | 0.860 (118 instances) | not computable (below) |
| sf_50m_small-samples_001500032 | -3272.12 | 0.602 [193; 0 / 0 / 0] | 772 records, max error 8.9e-16 | not stored | not computable (below) |

- Nine-seed engine mean, the 40 cities: from `<repo>/results/audit/engine_reference/tasks_v2_H24/A_instance_calibrated` (truth-seed pool mean plus truth residual minus residual); cross-checked with 1 other run(s), largest difference 0.0e+00.
- Nine-seed engine mean, the 80 new cities: no run under <repo>/results/audit/engine_reference/tasks_v2x_H24 stores the truth-seed pool mean (truth_pool_mean_behaviour) of every instance, from which the engine's nine-seed mean follows: the emulator's two-sample margins cannot be recovered from the audits' residuals.
- Recovered margins closer than 1e-09 are ranked as one value (the recovery reproduces the emulator's tied scores only to a few ulp); the largest gap merged and the smallest gap kept are in `checkpoints[].decision_fidelity.<cities>.ties`.

## The pool-seeded search on the analysis plan's nested set

x: `cem_seeded_c40_hack_1000`. A checkpoint is done when tasks_v2_H24_cem_seeded/reference.json exists; the audit reads with status ok; every family's instances at 10, 100 and 1,000 are complete and paired with the perfect emulator; the records reproduce reference.json's per-family values. The row is computed on the largest complete set (the same statistics as section 2); random search on the same checkpoints beside it.

| set | checkpoints (expected) | done | complete |
|---|---|---|---|
| all 24 checkpoints | 24 (24) | 24 | yes |
| the 12 final checkpoints | 12 (12) | 12 | yes |
| the 6 full-data finals | 6 (6) | 6 | yes |

**computed on all 24 checkpoints.**

| x | y | role | pairs (expected) | checkpoints | pooled Spearman | Kendall | within-family mean Spearman | ranked within family |
|---|---|---|---|---|---|---|---|---|
| `cem_seeded_c40_hack_1000` | `rl_inflation_1000000` | the row  | 120 (120) | 24 | +0.839 [+0.803, +0.870] | +0.650 [+0.614, +0.691] | +0.507 [+0.306, +0.651] | +0.505 [+0.307, +0.652] |
| `cem_seeded_c40_hack_1000` | `rl_gap_1000000` | the row  | 120 (120) | 24 | +0.794 [+0.733, +0.850] | +0.617 [+0.557, +0.681] | +0.534 [+0.355, +0.656] | +0.530 [+0.353, +0.656] |
| `random_c120_hack_1000` | `rl_inflation_1000000` | beside it: random search on the same checkpoints | 120 (120) | 24 | +0.843 [+0.765, +0.904] | +0.682 [+0.612, +0.749] | +0.553 [+0.309, +0.726] | +0.554 [+0.310, +0.724] |
| `random_c120_hack_1000` | `rl_gap_1000000` | beside it: random search on the same checkpoints | 120 (120) | 24 | +0.865 [+0.802, +0.914] | +0.691 [+0.620, +0.761] | +0.551 [+0.369, +0.682] | +0.554 [+0.369, +0.685] |
| `random_c40_hack_1000` | `rl_inflation_1000000` | beside it: random search on the same checkpoints | 120 (120) | 24 | +0.829 [+0.759, +0.884] | +0.667 [+0.607, +0.729] | +0.464 [+0.264, +0.617] | +0.478 [+0.260, +0.616] |
| `random_c40_hack_1000` | `rl_gap_1000000` | beside it: random search on the same checkpoints | 120 (120) | 24 | +0.826 [+0.764, +0.878] | +0.649 [+0.585, +0.715] | +0.441 [+0.267, +0.582] | +0.460 [+0.264, +0.583] |

- Done: os_100m_full-samples_003000064, os_100m_full-samples_006000000, os_100m_small-samples_003000064, os_100m_small-samples_006000000, os_15m_full-samples_003000064, os_15m_full-samples_006000000, os_15m_small-samples_003000064, os_15m_small-samples_006000000, os_50m_full-samples_003000064, os_50m_full-samples_006000000, os_50m_small-samples_003000064, os_50m_small-samples_006000000, sf_100m_full-samples_000750080, sf_100m_full-samples_001500032, sf_100m_small-samples_000750080, sf_100m_small-samples_001500032, sf_15m_full-samples_000750080, sf_15m_full-samples_001500032, sf_15m_small-samples_000750080, sf_15m_small-samples_001500032, sf_50m_full-samples_000750080, sf_50m_full-samples_001500032, sf_50m_small-samples_000750080, sf_50m_small-samples_001500032.

## Single-plan comparator: one logged plan per instance against the search  (COMPLETE)

Added after's review (M7) and defined in the analysis plan before any 120-city input was complete. E1: the statistics of sections 2 and 3 with random search's false acceptance at budget 1 (one logged plan per instance, judged by the emulator on 8 fresh samples and by the 32-seed oracle; no search) in place of budget 1,000. E2: Spearman at 1,000 minus Spearman at budget 1 on the pairs that hold both, both recomputed on every cluster resample (clusters = checkpoints; percentile intervals). The 120-city rows carry the wording fixed in advance; the 40- and 80-city rows are reported beside them. The protocol deciding row and rule (section 2) do not change.

Wording, read on E2's interval: above zero: "the search adds predictive value beyond a check on logged plans"; includes zero: "the prediction does not need the search: one logged plan per instance, judged by the emulator and the engine, predicts as well, so the audit cannot be told from a calibration check on logged plans"; below zero: "one logged plan predicts better than the search audit".

### E1: false acceptance at budget 1 as the predictor

| x: cities | y | pairs | checkpoints | Spearman [95 %] | Kendall [95 %] | Spearman, lineage clusters | mean of the within-family Spearman | ranked within family | role |
|---|---|---|---|---|---|---|---|---|---|
| all 120 cities | `rl_inflation_1000000` | 120 | 24 | +0.875 [+0.825, +0.913] | +0.721 [+0.669, +0.776] | +0.875 [+0.830, +0.914] | +0.681 [+0.508, +0.805] | +0.669 [+0.497, +0.804] | carries the wording  |
| all 120 cities | `rl_gap_1000000` | 120 | 24 | +0.883 [+0.834, +0.920] | +0.733 [+0.675, +0.790] | +0.883 [+0.856, +0.908] | +0.645 [+0.472, +0.773] | +0.642 [+0.477, +0.777] | carries the wording  |
| the 40 cities | `rl_inflation_1000000` | 120 | 24 | +0.821 [+0.770, +0.866] | +0.649 [+0.590, +0.709] | +0.821 [+0.739, +0.882] | +0.543 [+0.353, +0.714] | +0.510 [+0.258, +0.699] | reported beside it |
| the 40 cities | `rl_gap_1000000` | 120 | 24 | +0.864 [+0.823, +0.897] | +0.700 [+0.650, +0.748] | +0.864 [+0.810, +0.897] | +0.582 [+0.427, +0.714] | +0.572 [+0.388, +0.709] | reported beside it |
| the 80 new cities | `rl_inflation_1000000` | 120 | 24 | +0.859 [+0.796, +0.903] | +0.709 [+0.644, +0.769] | +0.859 [+0.835, +0.892] | +0.655 [+0.488, +0.771] | +0.647 [+0.480, +0.767] | reported beside it |
| the 80 new cities | `rl_gap_1000000` | 120 | 24 | +0.865 [+0.800, +0.914] | +0.718 [+0.644, +0.785] | +0.865 [+0.825, +0.906] | +0.611 [+0.435, +0.738] | +0.616 [+0.444, +0.744] | reported beside it |

Per family (one point per checkpoint), E1:

| x: cities | y | grow | solvent | treasury | recover | power |
|---|---|---|---|---|---|---|
| all 120 cities | `rl_inflation_1000000` | +0.738 [+0.468, +0.902] (24) | +0.779 [+0.527, +0.919] (24) | +0.574 [+0.142, +0.849] (24) | +0.870 [+0.637, +0.969] (24) | +0.442 [+0.028, +0.784] (24) |
| all 120 cities | `rl_gap_1000000` | +0.841 [+0.657, +0.932] (24) | +0.542 [+0.123, +0.827] (24) | +0.719 [+0.397, +0.897] (24) | +0.920 [+0.741, +0.988] (24) | +0.202 [-0.198, +0.575] (24) |
| the 40 cities | `rl_inflation_1000000` | +0.615 [+0.307, +0.830] (24) | +0.573 [+0.347, +0.755] (24) | +0.412 [-0.039, +0.754] (24) | +0.730 [+0.411, +0.924] (24) | +0.385 [+0.000, +0.640] (24) |
| the 40 cities | `rl_gap_1000000` | +0.814 [+0.606, +0.925] (24) | +0.573 [+0.347, +0.755] (24) | +0.585 [+0.228, +0.836] (24) | +0.767 [+0.485, +0.918] (24) | +0.171 [-0.154, +0.462] (24) |
| the 80 new cities | `rl_inflation_1000000` | +0.711 [+0.407, +0.893] (24) | +0.726 [+0.474, +0.882] (24) | +0.596 [+0.149, +0.889] (24) | +0.857 [+0.611, +0.962] (24) | +0.384 [-0.040, +0.736] (24) |
| the 80 new cities | `rl_gap_1000000` | +0.762 [+0.487, +0.903] (24) | +0.466 [+0.062, +0.760] (24) | +0.733 [+0.413, +0.901] (24) | +0.904 [+0.719, +0.982] (24) | +0.190 [-0.253, +0.588] (24) |

### E2: Spearman at 1,000 minus Spearman at budget 1 (same pairs, same resamples)

| x: cities | y | pairs | checkpoints | Spearman at 1,000 | Spearman at 1 | difference, pooled | difference, lineage clusters | difference, mean of the within-family values | difference, ranked within family | wording |
|---|---|---|---|---|---|---|---|---|---|---|
| all 120 cities | `rl_inflation_1000000` | 120 | 24 | +0.843 [+0.765, +0.904] | +0.875 [+0.825, +0.913] | -0.032 [-0.100, +0.037] | -0.032 [-0.071, +0.012] | -0.128 [-0.305, +0.059] | -0.115 [-0.298, +0.062] | pooled: "the prediction does not need the search: one logged plan per instance, judged by the emulator and the engine, predicts as well, so the audit cannot be told from a calibration check on logged plans"; mean of the within-family values: "the prediction does not need the search: one logged plan per instance, judged by the emulator and the engine, predicts as well, so the audit cannot be told from a calibration check on logged plans"; pooled after ranking within family: "the prediction does not need the search: one logged plan per instance, judged by the emulator and the engine, predicts as well, so the audit cannot be told from a calibration check on logged plans" |
| all 120 cities | `rl_gap_1000000` | 120 | 24 | +0.865 [+0.802, +0.914] | +0.883 [+0.834, +0.920] | -0.018 [-0.075, +0.033] | -0.018 [-0.065, +0.025] | -0.094 [-0.266, +0.062] | -0.088 [-0.267, +0.057] | pooled: "the prediction does not need the search: one logged plan per instance, judged by the emulator and the engine, predicts as well, so the audit cannot be told from a calibration check on logged plans"; mean of the within-family values: "the prediction does not need the search: one logged plan per instance, judged by the emulator and the engine, predicts as well, so the audit cannot be told from a calibration check on logged plans"; pooled after ranking within family: "the prediction does not need the search: one logged plan per instance, judged by the emulator and the engine, predicts as well, so the audit cannot be told from a calibration check on logged plans" |
| the 40 cities | `rl_inflation_1000000` | 120 | 24 | +0.829 [+0.759, +0.884] | +0.821 [+0.770, +0.866] | +0.008 [-0.055, +0.066] | +0.008 [-0.040, +0.066] | -0.079 [-0.229, +0.093] | -0.033 [-0.203, +0.140] | reported beside (no wording) |
| the 40 cities | `rl_gap_1000000` | 120 | 24 | +0.826 [+0.764, +0.878] | +0.864 [+0.823, +0.897] | -0.038 [-0.098, +0.021] | -0.038 [-0.092, +0.025] | -0.141 [-0.263, -0.010] | -0.112 [-0.278, +0.013] | reported beside (no wording) |
| the 80 new cities | `rl_inflation_1000000` | 120 | 24 | +0.839 [+0.756, +0.901] | +0.859 [+0.796, +0.903] | -0.020 [-0.092, +0.053] | -0.020 [-0.068, +0.016] | -0.093 [-0.274, +0.089] | -0.089 [-0.270, +0.086] | reported beside (no wording) |
| the 80 new cities | `rl_gap_1000000` | 120 | 24 | +0.865 [+0.804, +0.913] | +0.865 [+0.800, +0.914] | +0.001 [-0.051, +0.052] | +0.001 [-0.042, +0.045] | -0.058 [-0.230, +0.095] | -0.064 [-0.233, +0.086] | reported beside (no wording) |

Per family, E2 (difference [95 %] (pairs)):

| x: cities | y | grow | solvent | treasury | recover | power |
|---|---|---|---|---|---|---|
| all 120 cities | `rl_inflation_1000000` | -0.274 [-0.717, +0.067] (24) | +0.038 [-0.226, +0.311] (24) | +0.106 [-0.089, +0.340] (24) | -0.136 [-0.396, +0.083] (24) | -0.374 [-0.979, +0.255] (24) |
| all 120 cities | `rl_gap_1000000` | -0.115 [-0.444, +0.135] (24) | +0.305 [+0.029, +0.690] (24) | +0.052 [-0.104, +0.215] (24) | -0.255 [-0.508, -0.066] (24) | -0.455 [-1.021, +0.176] (24) |
| the 40 cities | `rl_inflation_1000000` | -0.242 [-0.581, +0.049] (24) | +0.186 [-0.134, +0.486] (24) | +0.036 [-0.347, +0.422] (24) | -0.060 [-0.446, +0.301] (24) | -0.315 [-0.731, +0.121] (24) |
| the 40 cities | `rl_gap_1000000` | -0.202 [-0.538, +0.041] (24) | +0.205 [-0.102, +0.498] (24) | -0.010 [-0.311, +0.308] (24) | -0.183 [-0.502, +0.139] (24) | -0.512 [-0.823, -0.070] (24) |
| the 80 new cities | `rl_inflation_1000000` | -0.138 [-0.570, +0.221] (24) | +0.027 [-0.274, +0.307] (24) | +0.073 [-0.077, +0.252] (24) | -0.130 [-0.384, +0.086] (24) | -0.298 [-0.978, +0.428] (24) |
| the 80 new cities | `rl_gap_1000000` | -0.020 [-0.264, +0.201] (24) | +0.331 [+0.005, +0.690] (24) | +0.033 [-0.134, +0.215] (24) | -0.229 [-0.483, -0.034] (24) | -0.404 [-1.059, +0.317] (24) |

- Per-pair values at budget 1: `pairs.csv`, columns `random_<cities>_<statistic>_1` (after every earlier column) and `missing_budget_1`.

## The analysis plan: the main claim's permutation null, sensitivities and within-family power (COMPLETE)

The verdict stays on the protocol row and rule (section 2). Beside it: (a) the pooled Spearman under a within-family permutation null (the RL variable permuted among checkpoints within each task family, 2000 permutations, seed 0): the pooled value "exceeds what the differences between task families alone produce" if it lies above the null's 97.5th percentile, "is no more than the differences between task families produce" otherwise; (b) the within-family Spearman (mean of the family values, section 3) as the reading for ranking emulators: "within a task family the audit ranks emulators" if its interval excludes zero (with the estimate and whether it reaches 0.4), "does not rank emulators within a task family" if it includes zero. The 120-city rows carry the wording; the 80-city row is the check on audit data unseen when every rule was fixed.

| x: cities | y | pairs | observed pooled Spearman | null 2.5 / 50 / 97.5 percentiles | above the 97.5th | within-family Spearman [95 %] | excludes 0 | reaches 0.4 | role | wording |
|---|---|---|---|---|---|---|---|---|---|---|
| all 120 cities | `rl_inflation_1000000` | 120 | 0.843 | +0.637 / +0.694 / +0.752 | yes | +0.553 [+0.309, +0.726] | yes | yes | carries the wording  | permutation_null: "exceeds what the differences between task families alone produce"; within_family: "within a task family the audit ranks emulators" |
| all 120 cities | `rl_gap_1000000` | 120 | 0.865 | +0.613 / +0.675 / +0.736 | yes | +0.551 [+0.369, +0.682] | yes | yes | carries the wording  | permutation_null: "exceeds what the differences between task families alone produce"; within_family: "within a task family the audit ranks emulators" |
| the 40 cities | `rl_inflation_1000000` | 120 | 0.829 | +0.643 / +0.702 / +0.757 | yes | +0.464 [+0.264, +0.617] | yes | yes | reported beside it | reported beside (no wording) |
| the 40 cities | `rl_gap_1000000` | 120 | 0.826 | +0.622 / +0.682 / +0.737 | yes | +0.441 [+0.267, +0.582] | yes | yes | reported beside it | reported beside (no wording) |
| the 80 new cities | `rl_inflation_1000000` | 120 | 0.839 | +0.619 / +0.679 / +0.738 | yes | +0.562 [+0.317, +0.738] | yes | yes | the check on audit data unseen when every rule was fixed  | reported beside (no wording) |
| the 80 new cities | `rl_gap_1000000` | 120 | 0.865 | +0.595 / +0.663 / +0.728 | yes | +0.553 [+0.372, +0.690] | yes | yes | the check on audit data unseen when every rule was fixed  | reported beside (no wording) |

### Sensitivities of the original design (appendix)

| x: cities | y | Spearman, clustered by task family [95 %] | Pearson, checkpoint clusters [95 %] | leave one lineage out: range of the pooled Spearman | lineages |
|---|---|---|---|---|---|
| all 120 cities | `rl_inflation_1000000` | +0.843 [+0.461, +0.927] | +0.862 [+0.833, +0.894] | +0.831 to +0.860 | 6 |
| all 120 cities | `rl_gap_1000000` | +0.865 [+0.435, +0.928] | +0.922 [+0.906, +0.940] | +0.856 to +0.875 | 6 |
| the 40 cities | `rl_inflation_1000000` | +0.829 [+0.413, +0.918] | +0.861 [+0.835, +0.890] | +0.819 to +0.843 | 6 |
| the 40 cities | `rl_gap_1000000` | +0.826 [+0.304, +0.910] | +0.902 [+0.876, +0.928] | +0.820 to +0.840 | 6 |
| the 80 new cities | `rl_inflation_1000000` | +0.839 [+0.467, +0.915] | +0.841 [+0.804, +0.882] | +0.827 to +0.854 | 6 |
| the 80 new cities | `rl_gap_1000000` | +0.865 [+0.445, +0.919] | +0.911 [+0.893, +0.930] | +0.858 to +0.874 | 6 |

Leave one lineage out, each lineage (pooled Spearman, checkpoint clusters):

- all 120 cities, `rl_inflation_1000000`: without os_100m_full: +0.831 [+0.739, +0.905] (100 pairs); without os_100m_small: +0.860 [+0.784, +0.917] (100 pairs); without os_15m_full: +0.837 [+0.745, +0.912] (100 pairs); without os_15m_small: +0.832 [+0.748, +0.900] (100 pairs); without os_50m_full: +0.839 [+0.747, +0.911] (100 pairs); without os_50m_small: +0.859 [+0.792, +0.913] (100 pairs).
- all 120 cities, `rl_gap_1000000`: without os_100m_full: +0.859 [+0.790, +0.914] (100 pairs); without os_100m_small: +0.868 [+0.802, +0.916] (100 pairs); without os_15m_full: +0.864 [+0.802, +0.916] (100 pairs); without os_15m_small: +0.856 [+0.779, +0.912] (100 pairs); without os_50m_full: +0.875 [+0.805, +0.926] (100 pairs); without os_50m_small: +0.866 [+0.790, +0.918] (100 pairs).
- the 40 cities, `rl_inflation_1000000`: without os_100m_full: +0.819 [+0.736, +0.886] (100 pairs); without os_100m_small: +0.843 [+0.769, +0.902] (100 pairs); without os_15m_full: +0.823 [+0.750, +0.884] (100 pairs); without os_15m_small: +0.819 [+0.740, +0.887] (100 pairs); without os_50m_full: +0.830 [+0.749, +0.893] (100 pairs); without os_50m_small: +0.839 [+0.779, +0.891] (100 pairs).
- the 40 cities, `rl_gap_1000000`: without os_100m_full: +0.821 [+0.756, +0.877] (100 pairs); without os_100m_small: +0.831 [+0.768, +0.885] (100 pairs); without os_15m_full: +0.820 [+0.763, +0.870] (100 pairs); without os_15m_small: +0.821 [+0.744, +0.880] (100 pairs); without os_50m_full: +0.840 [+0.772, +0.894] (100 pairs); without os_50m_small: +0.823 [+0.748, +0.882] (100 pairs).
- the 80 new cities, `rl_inflation_1000000`: without os_100m_full: +0.828 [+0.731, +0.902] (100 pairs); without os_100m_small: +0.854 [+0.778, +0.909] (100 pairs); without os_15m_full: +0.832 [+0.733, +0.906] (100 pairs); without os_15m_small: +0.827 [+0.738, +0.899] (100 pairs); without os_50m_full: +0.835 [+0.736, +0.909] (100 pairs); without os_50m_small: +0.852 [+0.781, +0.910] (100 pairs).
- the 80 new cities, `rl_gap_1000000`: without os_100m_full: +0.858 [+0.787, +0.910] (100 pairs); without os_100m_small: +0.869 [+0.807, +0.916] (100 pairs); without os_15m_full: +0.867 [+0.806, +0.917] (100 pairs); without os_15m_small: +0.858 [+0.786, +0.912] (100 pairs); without os_50m_full: +0.874 [+0.806, +0.922] (100 pairs); without os_50m_small: +0.863 [+0.790, +0.915] (100 pairs).

### Power of the within-family reading, by simulation

In each task family, the checkpoints' (audit, RL) values are bivariate normal with the stated true Spearman (Pearson 2 sin(pi rho / 6)); families and checkpoints independent (no checkpoint effect shared across families, which the measured intra-checkpoint correlations, near zero and negative, do not contradict); continuous values (no ties); the row's numbers of checkpoints and families; the statistic and interval as computed here (mean of the within-family Spearman, cluster bootstrap over checkpoints, percentile), with 1000 resamples in place of 2,000; 500 simulations per cell; power = the share whose 95 per cent interval excludes zero.

| checkpoints | families | true within-family Spearman | power (interval excludes 0) | interval above 0 | estimate at least 0.4 |
|---|---|---|---|---|---|
| 24 | 5 | 0.2 | 0.54 | 0.54 | 0.00 |
| 24 | 5 | 0.3 | 0.84 | 0.84 | 0.08 |
| 24 | 5 | 0.4 | 0.98 | 0.98 | 0.47 |
| 24 | 5 | 0.5 | 1.00 | 1.00 | 0.86 |

- Monte Carlo standard error of each power: at most 0.022. A row's own cells: its checkpoints now, and the protocol 24.

## The analysis plan: the secondary claim on its checkpoint set, the analysis plan's rule (COMPLETE)

Checkpoint set: all 24 checkpoints (test selection: finals from test/, half-trained checkpoints from test_half/).

The analysis plan: a measure is falsified if the interval on |Spearman| of its pooled verdict row lies above 0.3; the twelve-month rollout error (three readings) is falsified if any reading is; the claim is falsified if any measure is. The analysis plan: if it is not falsified and the power to falsify at a true |Spearman| of 0.5 is below 0.8, the wording is "not falsified, and not falsifiable at this size". Checkpoint-level rows (one point per checkpoint: the measure against the mean over the five families of the false acceptance) beside the pooled rows; they are not part of the rule.

| measure | verdict row | pairs | checkpoints | pooled Spearman [95 %] | interval on abs above 0.3 | power to falsify, pooled | checkpoint-level Spearman [95 %] (checkpoints) | power, checkpoint level |
|---|---|---|---|---|---|---|---|---|
| one-month F1 | `fid_test_f1_1m|c120` | 120 | 24 | -0.091 [-0.238, +0.064] | no | 0.00 | -0.225 [-0.609, +0.251] (24) | 0.19 |
| twelve-month rollout error | `fid_test_f1_since_start_12m|c120` | 120 | 24 | -0.065 [-0.223, +0.100] | no | 0.00 | -0.170 [-0.591, +0.285] (24) | 0.19 |
| twelve-month rollout error | `fid_test_funds_medrel_12m|c120` | 120 | 24 | -0.027 [-0.201, +0.157] | no | 0.00 | -0.190 [-0.663, +0.297] (24) | 0.19 |
| twelve-month rollout error | `fid_test_pop_medrel_12m|c120` | 120 | 24 | -0.043 [-0.180, +0.102] | no | 0.00 | -0.179 [-0.535, +0.206] (24) | 0.19 |
| held-out likelihood | `fid_test_loglik_elbo|c120` | 120 | 24 | +0.035 [-0.109, +0.186] | no | 0.00 | +0.075 [-0.376, +0.512] (24) | 0.19 |
| fixed-candidate decision fidelity | `fid_decision_c40|c80` | 120 | 24 | +0.044 [-0.117, +0.185] | no | 0.00 | +0.109 [-0.320, +0.500] (24) | 0.19 |

**Verdict : 0 of 4 measures falsified; the claim: "not falsified, and not falsifiable at this size".** By measure: one-month F1: "not falsified, and not falsifiable at this size"; twelve-month rollout error: "not falsified, and not falsifiable at this size"; held-out likelihood: "not falsified, and not falsifiable at this size"; fixed-candidate decision fidelity: "not falsified, and not falsifiable at this size".

### Power to falsify, by simulation

A true Spearman of 0.5 (either sign) between the fidelity measure and the checkpoint's mean false acceptance over the five families; the measure constant across a checkpoint's families; a pair's false acceptance = the observed grand mean + the observed family effect + (the observed SD of checkpoint means) x the checkpoint component + a normal residual of the observed residual SD (two-way additive fit on the row's own checkpoints), centred within the checkpoint; normal, continuous values (the observed rates are discrete); the row's checkpoints; the statistics and intervals as computed here, 1000 resamples in place of 2,000; 500 simulations; power = the share whose interval on |Spearman| lies above 0.3 (the analysis plan's rule).

| false acceptance: cities | checkpoints | share of variance between families | power, pooled row | power, checkpoint-level row |
|---|---|---|---|---|
| 120 | 24 | 0.77 | 0.00 | 0.19 |
| 80 | 24 | 0.73 | 0.00 | 0.19 |

### Checkpoint-level rows beside every pooled secondary row (on that row's own checkpoints)

| pooled row | checkpoints | checkpoint-level Spearman [95 %] | abs < 0.3 | interval on abs above 0.3 |
|---|---|---|---|---|
| `fid_dev_f1_1m|c120` | 24 | -0.176 [-0.569, +0.281] | yes | no |
| `fid_dev_f1_since_start_12m|c120` | 24 | -0.179 [-0.597, +0.283] | yes | no |
| `fid_dev_funds_medrel_12m|c120` | 24 | -0.204 [-0.655, +0.266] | yes | no |
| `fid_dev_pop_medrel_12m|c120` | 24 | -0.121 [-0.486, +0.275] | yes | no |
| `fid_test_f1_1m|c120` | 12 | -0.182 [-0.804, +0.482] | yes | no |
| `fid_test_f1_since_start_12m|c120` | 12 | -0.042 [-0.740, +0.638] | yes | no |
| `fid_test_funds_medrel_12m|c120` | 12 | -0.168 [-0.857, +0.552] | yes | no |
| `fid_test_pop_medrel_12m|c120` | 12 | -0.336 [-0.872, +0.376] | no | no |
| `fid_dev_f1_1m|c40` | 24 | -0.215 [-0.619, +0.242] | yes | no |
| `fid_dev_f1_since_start_12m|c40` | 24 | -0.098 [-0.536, +0.360] | yes | no |
| `fid_dev_funds_medrel_12m|c40` | 24 | -0.149 [-0.598, +0.294] | yes | no |
| `fid_dev_pop_medrel_12m|c40` | 24 | -0.114 [-0.484, +0.271] | yes | no |
| `fid_test_f1_1m|c40` | 12 | -0.161 [-0.816, +0.516] | yes | no |
| `fid_test_f1_since_start_12m|c40` | 12 | +0.028 [-0.730, +0.670] | yes | no |
| `fid_test_funds_medrel_12m|c40` | 12 | -0.147 [-0.787, +0.542] | yes | no |
| `fid_test_pop_medrel_12m|c40` | 12 | -0.249 [-0.749, +0.420] | yes | no |
| `fid_dev_f1_1m|c80` | 24 | -0.134 [-0.534, +0.320] | yes | no |
| `fid_dev_f1_since_start_12m|c80` | 24 | -0.160 [-0.580, +0.304] | yes | no |
| `fid_dev_funds_medrel_12m|c80` | 24 | -0.217 [-0.660, +0.240] | yes | no |
| `fid_dev_pop_medrel_12m|c80` | 24 | -0.117 [-0.492, +0.284] | yes | no |
| `fid_test_f1_1m|c80` | 12 | -0.105 [-0.776, +0.577] | yes | no |
| `fid_test_f1_since_start_12m|c80` | 12 | -0.007 [-0.732, +0.673] | yes | no |
| `fid_test_funds_medrel_12m|c80` | 12 | -0.161 [-0.860, +0.553] | yes | no |
| `fid_test_pop_medrel_12m|c80` | 12 | -0.301 [-0.827, +0.398] | no | no |
| `fid_test_loglik_elbo|c120` | 12 | -0.091 [-0.690, +0.545] | yes | no |
| `fid_test_loglik_elbo|c40` | 12 | -0.364 [-0.844, +0.265] | no | no |
| `fid_test_loglik_elbo|c80` | 12 | -0.063 [-0.657, +0.557] | yes | no |
| `fid_decision_c40|c80` | 12 | +0.252 [-0.379, +0.736] | yes | no |
| `fid_decision_c80|c40` | 0 | n/a (fewer than 3 checkpoints) | | |
| `fid_decision_c120|c120` | 0 | n/a (fewer than 3 checkpoints) | | |
| `fid_decision_c40|c40` | 12 | +0.252 [-0.418, +0.735] | yes | no |
| `fid_decision_c80|c80` | 0 | n/a (fewer than 3 checkpoints) | | |

## 24-month trajectory-fidelity predictors against consistent exploitation targets (COMPLETE)

Held-out 24-month rollout records: 12 finals in `test/` and 12 half-trained checkpoints in `test_half/` (24 of 24 ladder checkpoints; 24 on `dev/`). Bootstrap resamples: 20,000 (seed 0).

### all 24 ladder checkpoints (held-out test: 12 finals in test/, 12 half-trained in test_half/)

| 24m metric | target | pairs | ckpts | pooled Spearman [95 %] | within-family Spearman [95 %] | partial Spearman (size + data) [95 %] | within-family partial (size + data) [95 %] |
|---|---|---|---|---|---|---|---|
| mean 24m spatial overlay copy-ratio (open-loop plans) | `rl_inflation_1000000` | 120 | 24 | -0.105 [-0.253, +0.047] | -0.095 [-0.444, +0.247] | -0.112 [-0.231, +0.029] | -0.091 [-0.448, +0.259] |
| mean 24m spatial overlay copy-ratio (open-loop plans) | `rl_gap_1000000` | 120 | 24 | +0.090 [-0.063, +0.232] | +0.143 [-0.137, +0.388] | +0.082 [-0.093, +0.230] | +0.134 [-0.198, +0.401] |
| mean 24m spatial overlay copy-ratio (open-loop plans) | `random_c120_hack_1000` | 120 | 24 | +0.071 [-0.083, +0.217] | +0.132 [-0.168, +0.398] | +0.066 [-0.097, +0.217] | +0.120 [-0.238, +0.425] |
| mean 24m scalar copy-ratio (open-loop plans) | `rl_inflation_1000000` | 120 | 24 | -0.154 [-0.295, +0.022] | -0.206 [-0.534, +0.176] | -0.150 [-0.255, +0.001] | -0.194 [-0.508, +0.166] |
| mean 24m scalar copy-ratio (open-loop plans) | `rl_gap_1000000` | 120 | 24 | +0.048 [-0.114, +0.204] | +0.053 [-0.250, +0.342] | +0.047 [-0.120, +0.202] | +0.065 [-0.260, +0.354] |
| mean 24m scalar copy-ratio (open-loop plans) | `random_c120_hack_1000` | 120 | 24 | -0.006 [-0.141, +0.142] | -0.019 [-0.285, +0.253] | +0.003 [-0.133, +0.163] | -0.027 [-0.315, +0.278] |
| 24m open-loop powered-zone count error (MAE) | `rl_inflation_1000000` | 120 | 24 | -0.144 [-0.291, +0.035] | -0.195 [-0.533, +0.211] | -0.158 [-0.266, -0.001] | -0.227 [-0.541, +0.154] |
| 24m open-loop powered-zone count error (MAE) | `rl_gap_1000000` | 120 | 24 | +0.043 [-0.129, +0.216] | +0.036 [-0.275, +0.355] | +0.033 [-0.134, +0.201] | +0.027 [-0.299, +0.341] |
| 24m open-loop powered-zone count error (MAE) | `random_c120_hack_1000` | 120 | 24 | -0.000 [-0.138, +0.149] | -0.003 [-0.277, +0.280] | +0.004 [-0.136, +0.171] | -0.029 [-0.331, +0.292] |
| 24m open-loop pollution copy-ratio | `rl_inflation_1000000` | 120 | 24 | -0.103 [-0.252, +0.049] | -0.102 [-0.447, +0.228] | -0.127 [-0.233, +0.028] | -0.145 [-0.440, +0.225] |
| 24m open-loop pollution copy-ratio | `rl_gap_1000000` | 120 | 24 | +0.039 [-0.096, +0.168] | +0.106 [-0.180, +0.363] | +0.032 [-0.098, +0.175] | +0.097 [-0.193, +0.394] |
| 24m open-loop pollution copy-ratio | `random_c120_hack_1000` | 120 | 24 | +0.037 [-0.101, +0.169] | +0.074 [-0.206, +0.326] | +0.025 [-0.111, +0.168] | +0.059 [-0.241, +0.353] |
| mean 24m spatial overlay copy-ratio (all 500 plans, Table 16 scope) | `rl_inflation_1000000` | 120 | 24 | -0.120 [-0.265, +0.038] | -0.133 [-0.473, +0.214] | -0.121 [-0.235, +0.025] | -0.115 [-0.449, +0.239] |
| mean 24m spatial overlay copy-ratio (all 500 plans, Table 16 scope) | `rl_gap_1000000` | 120 | 24 | +0.065 [-0.077, +0.199] | +0.124 [-0.149, +0.368] | +0.061 [-0.093, +0.206] | +0.122 [-0.190, +0.391] |
| mean 24m spatial overlay copy-ratio (all 500 plans, Table 16 scope) | `random_c120_hack_1000` | 120 | 24 | +0.044 [-0.104, +0.188] | +0.075 [-0.214, +0.336] | +0.039 [-0.111, +0.191] | +0.069 [-0.261, +0.371] |
| 24m pollution copy-ratio (all 500 plans, Table 16 column) | `rl_inflation_1000000` | 120 | 24 | -0.094 [-0.241, +0.059] | -0.090 [-0.425, +0.238] | -0.121 [-0.228, +0.039] | -0.143 [-0.436, +0.235] |
| 24m pollution copy-ratio (all 500 plans, Table 16 column) | `rl_gap_1000000` | 120 | 24 | +0.041 [-0.093, +0.169] | +0.120 [-0.167, +0.381] | +0.031 [-0.097, +0.174] | +0.106 [-0.187, +0.412] |
| 24m pollution copy-ratio (all 500 plans, Table 16 column) | `random_c120_hack_1000` | 120 | 24 | +0.039 [-0.095, +0.167] | +0.080 [-0.193, +0.328] | +0.027 [-0.110, +0.172] | +0.060 [-0.247, +0.363] |

### the 12 converged final ladder checkpoints (held-out test/, Table 16 scope)

| 24m metric | target | pairs | ckpts | pooled Spearman [95 %] | within-family Spearman [95 %] | partial Spearman (size + data) [95 %] | within-family partial (size + data) [95 %] |
|---|---|---|---|---|---|---|---|
| mean 24m spatial overlay copy-ratio (open-loop plans) | `rl_inflation_1000000` | 60 | 12 | -0.045 [-0.269, +0.155] | -0.035 [-0.570, +0.434] | -0.089 [-0.251, +0.134] | -0.115 [-0.614, +0.556] |
| mean 24m spatial overlay copy-ratio (open-loop plans) | `rl_gap_1000000` | 60 | 12 | +0.106 [-0.120, +0.286] | +0.234 [-0.214, +0.560] | +0.090 [-0.195, +0.276] | +0.207 [-0.471, +0.688] |
| mean 24m spatial overlay copy-ratio (open-loop plans) | `random_c120_hack_1000` | 60 | 12 | +0.005 [-0.214, +0.229] | -0.038 [-0.482, +0.382] | -0.025 [-0.216, +0.200] | -0.090 [-0.734, +0.447] |
| mean 24m scalar copy-ratio (open-loop plans) | `rl_inflation_1000000` | 60 | 12 | -0.161 [-0.319, +0.078] | -0.301 [-0.675, +0.243] | -0.171 [-0.272, +0.099] | -0.331 [-0.706, +0.461] |
| mean 24m scalar copy-ratio (open-loop plans) | `rl_gap_1000000` | 60 | 12 | -0.009 [-0.197, +0.194] | -0.001 [-0.385, +0.400] | -0.017 [-0.226, +0.239] | -0.015 [-0.547, +0.601] |
| mean 24m scalar copy-ratio (open-loop plans) | `random_c120_hack_1000` | 60 | 12 | -0.091 [-0.263, +0.132] | -0.218 [-0.579, +0.223] | -0.101 [-0.241, +0.175] | -0.256 [-0.773, +0.406] |
| 24m open-loop powered-zone count error (MAE) | `rl_inflation_1000000` | 60 | 12 | -0.164 [-0.321, +0.078] | -0.320 [-0.685, +0.245] | -0.186 [-0.277, +0.094] | -0.387 [-0.725, +0.440] |
| 24m open-loop powered-zone count error (MAE) | `rl_gap_1000000` | 60 | 12 | -0.030 [-0.212, +0.168] | -0.043 [-0.414, +0.391] | -0.041 [-0.231, +0.228] | -0.067 [-0.566, +0.600] |
| 24m open-loop powered-zone count error (MAE) | `random_c120_hack_1000` | 60 | 12 | -0.111 [-0.265, +0.092] | -0.245 [-0.577, +0.186] | -0.125 [-0.244, +0.156] | -0.309 [-0.789, +0.380] |
| 24m open-loop pollution copy-ratio | `rl_inflation_1000000` | 60 | 12 | -0.021 [-0.261, +0.188] | +0.021 [-0.558, +0.482] | -0.084 [-0.251, +0.177] | -0.108 [-0.612, +0.708] |
| 24m open-loop pollution copy-ratio | `rl_gap_1000000` | 60 | 12 | +0.082 [-0.146, +0.279] | +0.229 [-0.268, +0.617] | +0.072 [-0.181, +0.300] | +0.211 [-0.452, +0.789] |
| 24m open-loop pollution copy-ratio | `random_c120_hack_1000` | 60 | 12 | -0.003 [-0.197, +0.181] | -0.003 [-0.437, +0.417] | -0.034 [-0.221, +0.205] | -0.062 [-0.710, +0.610] |
| mean 24m spatial overlay copy-ratio (all 500 plans, Table 16 scope) | `rl_inflation_1000000` | 60 | 12 | -0.063 [-0.273, +0.161] | -0.076 [-0.568, +0.431] | -0.092 [-0.250, +0.158] | -0.123 [-0.600, +0.633] |
| mean 24m spatial overlay copy-ratio (all 500 plans, Table 16 scope) | `rl_gap_1000000` | 60 | 12 | +0.094 [-0.122, +0.270] | +0.236 [-0.208, +0.565] | +0.080 [-0.177, +0.282] | +0.218 [-0.419, +0.730] |
| mean 24m spatial overlay copy-ratio (all 500 plans, Table 16 scope) | `random_c120_hack_1000` | 60 | 12 | -0.032 [-0.223, +0.179] | -0.106 [-0.507, +0.305] | -0.056 [-0.223, +0.192] | -0.153 [-0.743, +0.482] |
| 24m pollution copy-ratio (all 500 plans, Table 16 column) | `rl_inflation_1000000` | 60 | 12 | -0.039 [-0.274, +0.179] | -0.024 [-0.580, +0.459] | -0.095 [-0.255, +0.176] | -0.143 [-0.616, +0.705] |
| 24m pollution copy-ratio (all 500 plans, Table 16 column) | `rl_gap_1000000` | 60 | 12 | +0.069 [-0.151, +0.266] | +0.205 [-0.282, +0.602] | +0.058 [-0.183, +0.293] | +0.186 [-0.456, +0.781] |
| 24m pollution copy-ratio (all 500 plans, Table 16 column) | `random_c120_hack_1000` | 60 | 12 | -0.027 [-0.204, +0.155] | -0.049 [-0.454, +0.385] | -0.055 [-0.228, +0.193] | -0.108 [-0.725, +0.600] |

## 6-lineage cluster bootstrap alongside 24-checkpoint bootstrap (COMPLETE)

Lineages: {15m, 50m, 100m} x {small, full}: 6 four-checkpoint lineages (one-step half, one-step final, pushforward half, pushforward final). Bootstrap resamples: 20,000 (seed 0).

| predictor | target | pairs | pooled Spearman (24 ckpts) | pooled Spearman (6 lineages) | within-family Spearman (24 ckpts) | within-family Spearman (6 lineages) |
|---|---|---|---|---|---|---|
| `random_c120_hack_1000` | `rl_inflation_1000000` | 120 | +0.843 [+0.767, +0.905] | +0.843 [+0.799, +0.894] | +0.553 [+0.324, +0.728] | +0.553 [+0.359, +0.708] |
| `random_c120_hack_1000` | `rl_gap_1000000` | 120 | +0.865 [+0.803, +0.914] | +0.865 [+0.837, +0.895] | +0.551 [+0.372, +0.686] | +0.551 [+0.383, +0.655] |
| `random_c120_hack_1000` | `rl_fa0_1000000` | 120 | +0.841 [+0.784, +0.890] | +0.841 [+0.799, +0.876] | +0.607 [+0.419, +0.740] | +0.607 [+0.451, +0.739] |
| `random_c120_hack_1` | `rl_inflation_1000000` | 120 | +0.875 [+0.827, +0.914] | +0.875 [+0.828, +0.914] | +0.681 [+0.504, +0.808] | +0.681 [+0.467, +0.836] |
| `random_c120_hack_1` | `rl_gap_1000000` | 120 | +0.883 [+0.834, +0.921] | +0.883 [+0.856, +0.908] | +0.645 [+0.469, +0.775] | +0.645 [+0.423, +0.775] |
| `random_c120_hack_1` | `rl_fa0_1000000` | 120 | +0.839 [+0.780, +0.887] | +0.839 [+0.791, +0.891] | +0.636 [+0.481, +0.758] | +0.636 [+0.521, +0.764] |

## 7. What is missing

- Audit, random, the 40 cities: missing or unusable for 0 of 24 checkpoints.
- Audit, random, the 80 new cities: missing or unusable for 0 of 24 checkpoints.
- Audit, cem_seeded, the 40 cities: missing or unusable for 0 of 24 checkpoints.
- Audit, cem_seeded, the 80 new cities: missing or unusable for 23 of 24 checkpoints: os_100m_full-samples_003000064 (absent), os_100m_full-samples_006000000 (absent), os_100m_small-samples_003000064 (absent), os_100m_small-samples_006000000 (absent), os_15m_full-samples_003000064 (absent), os_15m_full-samples_006000000 (absent), os_15m_small-samples_003000064 (absent), os_15m_small-samples_006000000 (absent), os_50m_full-samples_003000064 (absent), os_50m_small-samples_003000064 (absent), os_50m_small-samples_006000000 (absent), sf_100m_full-samples_000750080 (absent), sf_100m_full-samples_001500032 (absent), sf_100m_small-samples_000750080 (absent), sf_100m_small-samples_001500032 (absent), sf_15m_full-samples_000750080 (absent), sf_15m_full-samples_001500032 (absent), sf_15m_small-samples_000750080 (absent), sf_15m_small-samples_001500032 (absent), sf_50m_full-samples_000750080 (absent), sf_50m_full-samples_001500032 (absent), sf_50m_small-samples_000750080 (absent), sf_50m_small-samples_001500032 (absent).
- RL runs (family x seed) with all three evaluation summaries short of 15 for 0 checkpoints.
- Excess over the perfect emulator not computable (records not all paired) for: none.
- Fidelity, development selection, missing for: none; test selection (finals) missing for: none.

## Checks made while reading

- Audit: the run's tasks sha256 equals its city file's; the card's judge checkpoint sha256 equals the checkpoint's; every record judged by the majority oracle; no duplicate record keys; the card's all-instance false acceptance equals the records' at every budget; every family's instances are exactly the city file's; the two city files share no instance; the perfect emulator paired on every record (else the excess is left empty); where a run has reference.json, the records reproduce its per-family values.
- RL: environment emulator, the frozen learner, the checkpoint path and sha256, the tasks file sha256 and the instance list as expected; each summary is evaluation version 3 at the month count of its file name with the family's instance count; the gap equals dream minus oracle acceptance.
- Fidelity: one decoding per checkpoint and split; the sample count and checkpoint sha256 as expected.
- `os_100m_full-samples_003000064` random_c40: reference.json agrees with the records in 100 values.
- `os_100m_full-samples_003000064` random_c80: reference.json agrees with the records in 100 values.
- `os_100m_full-samples_003000064` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_100m_full-samples_006000000` random_c40: reference.json agrees with the records in 100 values.
- `os_100m_full-samples_006000000` random_c80: reference.json agrees with the records in 100 values.
- `os_100m_full-samples_006000000` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_100m_small-samples_003000064` random_c40: reference.json agrees with the records in 100 values.
- `os_100m_small-samples_003000064` random_c80: reference.json agrees with the records in 100 values.
- `os_100m_small-samples_003000064` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_100m_small-samples_006000000` random_c40: reference.json agrees with the records in 100 values.
- `os_100m_small-samples_006000000` random_c80: reference.json agrees with the records in 100 values.
- `os_100m_small-samples_006000000` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_15m_full-samples_003000064` random_c40: reference.json agrees with the records in 100 values.
- `os_15m_full-samples_003000064` random_c80: reference.json agrees with the records in 100 values.
- `os_15m_full-samples_003000064` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_15m_full-samples_006000000` random_c40: reference.json agrees with the records in 100 values.
- `os_15m_full-samples_006000000` random_c80: reference.json agrees with the records in 100 values.
- `os_15m_full-samples_006000000` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_15m_small-samples_003000064` random_c40: reference.json agrees with the records in 100 values.
- `os_15m_small-samples_003000064` random_c80: reference.json agrees with the records in 100 values.
- `os_15m_small-samples_003000064` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_15m_small-samples_006000000` random_c40: reference.json agrees with the records in 100 values.
- `os_15m_small-samples_006000000` random_c80: reference.json agrees with the records in 100 values.
- `os_15m_small-samples_006000000` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_50m_full-samples_003000064` random_c40: reference.json agrees with the records in 100 values.
- `os_50m_full-samples_003000064` random_c80: reference.json agrees with the records in 100 values.
- `os_50m_full-samples_003000064` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_50m_full-samples_006000000` random_c40: reference.json agrees with the records in 100 values.
- `os_50m_full-samples_006000000` random_c80: reference.json agrees with the records in 100 values.
- `os_50m_full-samples_006000000` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_50m_full-samples_006000000` cem_seeded_c80: reference.json agrees with the records in 75 values.
- `os_50m_small-samples_003000064` random_c40: reference.json agrees with the records in 100 values.
- `os_50m_small-samples_003000064` random_c80: reference.json agrees with the records in 100 values.
- `os_50m_small-samples_003000064` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `os_50m_small-samples_006000000` random_c40: reference.json agrees with the records in 100 values.
- `os_50m_small-samples_006000000` random_c80: reference.json agrees with the records in 100 values.
- `os_50m_small-samples_006000000` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_100m_full-samples_000750080` random_c40: reference.json agrees with the records in 100 values.
- `sf_100m_full-samples_000750080` random_c80: reference.json agrees with the records in 100 values.
- `sf_100m_full-samples_000750080` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_100m_full-samples_001500032` random_c40: reference.json agrees with the records in 100 values.
- `sf_100m_full-samples_001500032` random_c80: reference.json agrees with the records in 100 values.
- `sf_100m_full-samples_001500032` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_100m_small-samples_000750080` random_c40: reference.json agrees with the records in 100 values.
- `sf_100m_small-samples_000750080` random_c80: reference.json agrees with the records in 100 values.
- `sf_100m_small-samples_000750080` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_100m_small-samples_001500032` random_c40: reference.json agrees with the records in 100 values.
- `sf_100m_small-samples_001500032` random_c80: reference.json agrees with the records in 100 values.
- `sf_100m_small-samples_001500032` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_15m_full-samples_000750080` random_c40: reference.json agrees with the records in 100 values.
- `sf_15m_full-samples_000750080` random_c80: reference.json agrees with the records in 100 values.
- `sf_15m_full-samples_000750080` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_15m_full-samples_001500032` random_c40: reference.json agrees with the records in 100 values.
- `sf_15m_full-samples_001500032` random_c80: reference.json agrees with the records in 100 values.
- `sf_15m_full-samples_001500032` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_15m_small-samples_000750080` random_c40: reference.json agrees with the records in 100 values.
- `sf_15m_small-samples_000750080` random_c80: reference.json agrees with the records in 100 values.
- `sf_15m_small-samples_000750080` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_15m_small-samples_001500032` random_c40: reference.json agrees with the records in 100 values.
- `sf_15m_small-samples_001500032` random_c80: reference.json agrees with the records in 100 values.
- `sf_15m_small-samples_001500032` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_50m_full-samples_000750080` random_c40: reference.json agrees with the records in 100 values.
- `sf_50m_full-samples_000750080` random_c80: reference.json agrees with the records in 100 values.
- `sf_50m_full-samples_000750080` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_50m_full-samples_001500032` random_c40: reference.json agrees with the records in 100 values.
- `sf_50m_full-samples_001500032` random_c80: reference.json agrees with the records in 100 values.
- `sf_50m_full-samples_001500032` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_50m_small-samples_000750080` random_c40: reference.json agrees with the records in 100 values.
- `sf_50m_small-samples_000750080` random_c80: reference.json agrees with the records in 100 values.
- `sf_50m_small-samples_000750080` cem_seeded_c40: reference.json agrees with the records in 75 values.
- `sf_50m_small-samples_001500032` random_c40: reference.json agrees with the records in 100 values.
- `sf_50m_small-samples_001500032` random_c80: reference.json agrees with the records in 100 values.
- `sf_50m_small-samples_001500032` cem_seeded_c40: reference.json agrees with the records in 75 values.
