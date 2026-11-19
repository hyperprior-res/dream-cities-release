# The RL point in the audit's unit and its perfect-emulator reference 

Runs: the 360 ladder runs (24 checkpoints x 5 task families x 3 seeds; os_50m_cov excluded), the coverage model's 15 runs, and the engine-trained learner's 11 runs of `results/rl/bc/decision_table_pooled.json` (seeds per family: grow 3, solvent 1, treasury 3, recover 3, power 1). Every number is recomputed from the per-instance records (`eval3_<months>.jsonl`) and checked against each run's summary.

Aggregation: a run's rate is the mean over its instances (8 episodes each); a cell is the mean over task families of the mean over the family's runs (the ladder: the mean over runs, as the paper; the engine-trained learner: as `\RlEngFull`). Intervals, 95 per cent, 2,000 resamples: **two-way** (checkpoints and held-out cities resampled independently, percentile), **checkpoint only** (BCa, the paper's current intervals), **city only** (checkpoints fixed, percentile). Cities are the audit's clusters (`family_id`, 40). Differences between a cell and the engine-trained learner share the city draws (paired by city).

Macro check: 85 printed RL values and intervals of `paper/numbers.tex` compared; all equal.

## 1. What the paper prints, with the three intervals (ladder)

| snapshot | scope | quantity | value | two-way | checkpoint only (BCa) | city only |
|---|---|---|---|---|---|---|
| 250,000 | all | dream acceptance | 0.210 | [0.174, 0.247] | [0.191, 0.232] | [0.182, 0.240] |
| 250,000 | all | oracle acceptance (open loop) | 0.056 | [0.039, 0.074] | [0.053, 0.058] | [0.039, 0.074] |
| 250,000 | all | acceptance gap | +0.154 | [+0.116, +0.195] | [+0.137, +0.176] | [+0.122, +0.189] |
| 250,000 | all | margin inflation | -0.018 | [-0.156, +0.118] | [-0.093, +0.045] | [-0.132, +0.101] |
| 250,000 | all | closed-loop pass rate on the engine | 0.104 | [0.084, 0.125] | [0.100, 0.108] | [0.084, 0.125] |
| 500,000 | all | dream acceptance | 0.263 | [0.224, 0.304] | [0.243, 0.289] | [0.232, 0.294] |
| 500,000 | all | oracle acceptance (open loop) | 0.091 | [0.068, 0.115] | [0.087, 0.095] | [0.069, 0.114] |
| 500,000 | all | acceptance gap | +0.172 | [+0.129, +0.219] | [+0.153, +0.199] | [+0.137, +0.212] |
| 500,000 | all | margin inflation | -0.001 | [-0.130, +0.128] | [-0.079, +0.062] | [-0.108, +0.112] |
| 500,000 | all | closed-loop pass rate on the engine | 0.148 | [0.122, 0.176] | [0.141, 0.155] | [0.123, 0.175] |
| 1,000,000 | all | dream acceptance | 0.319 | [0.276, 0.362] | [0.296, 0.349] | [0.286, 0.352] |
| 1,000,000 | all | oracle acceptance (open loop) | 0.141 | [0.110, 0.174] | [0.135, 0.148] | [0.110, 0.173] |
| 1,000,000 | all | acceptance gap | +0.178 | [+0.127, +0.231] | [+0.155, +0.209] | [+0.137, +0.222] |
| 1,000,000 | all | margin inflation | +0.028 | [-0.092, +0.149] | [-0.042, +0.092] | [-0.071, +0.133] |
| 1,000,000 | all | closed-loop pass rate on the engine | 0.202 | [0.169, 0.236] | [0.192, 0.211] | [0.170, 0.234] |
| 1,000,000 | grow | dream acceptance | 0.126 | [0.078, 0.182] | [0.096, 0.171] | [0.091, 0.165] |
| 1,000,000 | grow | oracle acceptance (open loop) | 0.067 | [0.016, 0.134] | [0.065, 0.070] | [0.016, 0.135] |
| 1,000,000 | grow | acceptance gap | +0.058 | [-0.008, +0.123] | [+0.028, +0.104] | [+0.004, +0.105] |
| 1,000,000 | grow | margin inflation | -0.331 | [-0.490, -0.178] | [-0.431, -0.230] | [-0.451, -0.208] |
| 1,000,000 | grow | closed-loop pass rate on the engine | 0.129 | [0.075, 0.190] | [0.124, 0.134] | [0.073, 0.190] |
| 1,000,000 | solvent | dream acceptance | 0.127 | [0.072, 0.192] | [0.095, 0.168] | [0.080, 0.179] |
| 1,000,000 | solvent | oracle acceptance (open loop) | 0.094 | [0.034, 0.166] | [0.079, 0.112] | [0.037, 0.162] |
| 1,000,000 | solvent | acceptance gap | +0.033 | [-0.045, +0.109] | [+0.008, +0.071] | [-0.039, +0.106] |
| 1,000,000 | solvent | margin inflation | -0.313 | [-0.450, -0.171] | [-0.395, -0.235] | [-0.422, -0.199] |
| 1,000,000 | solvent | closed-loop pass rate on the engine | 0.142 | [0.090, 0.199] | [0.116, 0.169] | [0.095, 0.192] |
| 1,000,000 | treasury | dream acceptance | 0.620 | [0.534, 0.698] | [0.596, 0.649] | [0.540, 0.690] |
| 1,000,000 | treasury | oracle acceptance (open loop) | 0.370 | [0.276, 0.458] | [0.355, 0.391] | [0.277, 0.458] |
| 1,000,000 | treasury | acceptance gap | +0.250 | [+0.160, +0.340] | [+0.210, +0.285] | [+0.175, +0.330] |
| 1,000,000 | treasury | margin inflation | +0.099 | [-0.011, +0.222] | [+0.070, +0.131] | [-0.014, +0.216] |
| 1,000,000 | treasury | closed-loop pass rate on the engine | 0.373 | [0.293, 0.449] | [0.359, 0.393] | [0.293, 0.449] |
| 1,000,000 | recover | dream acceptance | 0.672 | [0.573, 0.760] | [0.621, 0.719] | [0.589, 0.748] |
| 1,000,000 | recover | oracle acceptance (open loop) | 0.133 | [0.063, 0.214] | [0.127, 0.139] | [0.063, 0.213] |
| 1,000,000 | recover | acceptance gap | +0.539 | [+0.427, +0.648] | [+0.491, +0.584] | [+0.435, +0.639] |
| 1,000,000 | recover | margin inflation | +0.901 | [+0.692, +1.130] | [+0.796, +1.017] | [+0.722, +1.104] |
| 1,000,000 | recover | closed-loop pass rate on the engine | 0.296 | [0.244, 0.348] | [0.290, 0.301] | [0.244, 0.349] |
| 1,000,000 | power | dream acceptance | 0.052 | [0.021, 0.091] | [0.046, 0.058] | [0.021, 0.090] |
| 1,000,000 | power | oracle acceptance (open loop) | 0.040 | [0.010, 0.080] | [0.036, 0.045] | [0.010, 0.078] |
| 1,000,000 | power | acceptance gap | +0.012 | [+0.003, +0.023] | [+0.006, +0.019] | [+0.006, +0.018] |
| 1,000,000 | power | margin inflation | -0.213 | [-0.343, -0.092] | [-0.329, -0.108] | [-0.270, -0.159] |
| 1,000,000 | power | closed-loop pass rate on the engine | 0.070 | [0.019, 0.136] | [0.061, 0.076] | [0.019, 0.135] |

## 2. Plan 0 under the audit's verdict rule, beside the perfect emulator (ladder, 1,000,000 months)

Plan 0: the first sampled episode's action log of each instance. Emulator: 8 fresh samples, accepted at 4 or more of 8; perfect emulator: the engine on 8 seeds disjoint from the oracle's (EngineSeedJudge), accepted at 4 of 8; oracle: 32-seed majority. False acceptance = accepted and oracle rejects. Value [two-way].

| scope | emulator accepts | perfect emulator accepts | oracle accepts | false acceptance, emulator | false acceptance, perfect emulator (replayed) | excess | plug-in estimate of the perfect value |
|---|---|---|---|---|---|---|---|
| all | 0.332 [0.281, 0.382] | 0.188 [0.152, 0.225] | 0.141 [0.109, 0.175] | 0.233 [0.186, 0.284] | 0.064 [0.050, 0.079] | +0.170 [+0.124, +0.220] | 0.058 [0.046, 0.070] |
| grow | 0.108 [0.052, 0.178] | 0.097 [0.037, 0.167] | 0.070 [0.017, 0.140] | 0.085 [0.038, 0.146] | 0.036 [0.016, 0.064] | +0.048 [-0.003, +0.107] | 0.036 [0.019, 0.058] |
| solvent | 0.126 [0.060, 0.204] | 0.129 [0.064, 0.204] | 0.094 [0.031, 0.170] | 0.095 [0.037, 0.165] | 0.045 [0.024, 0.069] | +0.049 [-0.006, +0.111] | 0.042 [0.025, 0.061] |
| treasury | 0.682 [0.577, 0.776] | 0.393 [0.300, 0.484] | 0.368 [0.272, 0.460] | 0.359 [0.277, 0.444] | 0.053 [0.037, 0.073] | +0.306 [+0.224, +0.389] | 0.050 [0.037, 0.063] |
| recover | 0.726 [0.611, 0.822] | 0.282 [0.198, 0.368] | 0.134 [0.061, 0.218] | 0.619 [0.512, 0.725] | 0.183 [0.133, 0.233] | +0.436 [+0.336, +0.539] | 0.161 [0.124, 0.197] |
| power | 0.016 [0.001, 0.036] | 0.041 [0.009, 0.082] | 0.041 [0.009, 0.082] | 0.009 [0.001, 0.020] | 0.000 [0.000, 0.000] | +0.009 [+0.001, +0.020] | 0.000 [0.000, 0.000] |

Main checkpoint (15 runs; city intervals): false acceptance 0.178 [0.137, 0.225], perfect emulator 0.056 [0.033, 0.080], excess +0.122 [+0.076, +0.175]. Engine-trained learner's own plan 0 under the perfect emulator (replayed): false acceptance 0.075 [0.047, 0.106] (plug-in 0.071 [0.056, 0.086]). Plug-in over all 8 episodes' plans (not plan 0 only; R2's computation): emulator-trained 0.058, engine-trained 0.075.

Replays: 126,424 engine replays (3,034,176 city-months), each run's plan 0 of its first instance also replayed on its 32 oracle seeds: largest margin error against the stored oracle margins 0.0e+00.

## 3. The engine-trained learner: the perfect-emulator reference of the gap and the inflation

Own-episode pass rate = closed loop on the engine (its own environment); reference gap = own-episode pass rate minus the oracle's open-loop acceptance of the same action logs; reference inflation = own-episode margin minus the oracle's mean margin of the same logs. Intervals over cities (value [city percentile]; BCa in the JSON).

| snapshot | scope | seeds | own-episode pass rate | oracle acceptance | reference gap | reference inflation |
|---|---|---|---|---|---|---|
| 250,000 | all | 1 or 3 | 0.123 [0.097, 0.153] | 0.078 [0.057, 0.102] | +0.045 [+0.028, +0.062] | -0.008 [-0.023, +0.009] |
| 250,000 | grow | 3 | 0.068 [0.029, 0.120] | 0.033 [0.001, 0.086] | +0.034 [+0.016, +0.054] | -0.007 [-0.023, +0.011] |
| 250,000 | solvent | 1 | 0.095 [0.049, 0.148] | 0.046 [0.007, 0.095] | +0.049 [+0.007, +0.095] | -0.029 [-0.067, +0.009] |
| 250,000 | treasury | 3 | 0.196 [0.145, 0.249] | 0.176 [0.118, 0.237] | +0.020 [-0.011, +0.047] | -0.016 [-0.031, -0.000] |
| 250,000 | recover | 3 | 0.185 [0.129, 0.243] | 0.064 [0.011, 0.127] | +0.120 [+0.067, +0.170] | +0.013 [-0.062, +0.089] |
| 250,000 | power | 1 | 0.072 [0.019, 0.141] | 0.072 [0.019, 0.141] | +0.000 [+0.000, +0.000] | -0.001 [-0.003, +0.001] |
| 500,000 | all | 1 or 3 | 0.199 [0.165, 0.235] | 0.135 [0.103, 0.170] | +0.064 [+0.048, +0.080] | -0.009 [-0.023, +0.004] |
| 500,000 | grow | 3 | 0.115 [0.065, 0.173] | 0.059 [0.009, 0.124] | +0.055 [+0.029, +0.083] | +0.004 [-0.013, +0.021] |
| 500,000 | solvent | 1 | 0.191 [0.125, 0.266] | 0.112 [0.036, 0.204] | +0.079 [+0.020, +0.138] | -0.005 [-0.048, +0.036] |
| 500,000 | treasury | 3 | 0.331 [0.261, 0.397] | 0.309 [0.231, 0.390] | +0.022 [-0.006, +0.049] | -0.006 [-0.026, +0.010] |
| 500,000 | recover | 3 | 0.242 [0.182, 0.302] | 0.080 [0.023, 0.148] | +0.162 [+0.114, +0.208] | -0.038 [-0.091, +0.014] |
| 500,000 | power | 1 | 0.116 [0.037, 0.206] | 0.116 [0.037, 0.206] | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.000] |
| 1,000,000 | all | 1 or 3 | 0.307 [0.266, 0.349] | 0.230 [0.190, 0.271] | +0.077 [+0.059, +0.095] | +0.008 [-0.009, +0.026] |
| 1,000,000 | grow | 3 | 0.159 [0.091, 0.236] | 0.078 [0.011, 0.154] | +0.081 [+0.053, +0.109] | +0.017 [-0.009, +0.041] |
| 1,000,000 | solvent | 1 | 0.309 [0.220, 0.405] | 0.161 [0.063, 0.273] | +0.148 [+0.079, +0.220] | +0.008 [-0.017, +0.035] |
| 1,000,000 | treasury | 3 | 0.600 [0.509, 0.682] | 0.620 [0.520, 0.709] | -0.020 [-0.054, +0.011] | +0.006 [-0.003, +0.013] |
| 1,000,000 | recover | 3 | 0.337 [0.275, 0.405] | 0.162 [0.083, 0.245] | +0.175 [+0.111, +0.242] | +0.012 [-0.054, +0.082] |
| 1,000,000 | power | 1 | 0.131 [0.044, 0.234] | 0.131 [0.044, 0.234] | +0.000 [+0.000, +0.000] | -0.002 [-0.007, +0.000] |

Instance-weighted (every instance once, its seeds averaged): reference gap +0.074, city BCa [+0.058, +0.095].

## 4. Excess of the emulator-trained gap and inflation over the reference

Emulator-trained minus engine-trained, paired by city; ladder two-way, main checkpoint and coverage model city only (one checkpoint each).

| snapshot | scope | gap excess, ladder | gap excess, main checkpoint | inflation excess, ladder | inflation excess, main checkpoint |
|---|---|---|---|---|---|
| 250,000 | all | +0.109 [+0.071, +0.149] | +0.078 [+0.035, +0.119] | -0.010 [-0.150, +0.130] | +0.012 [-0.123, +0.153] |
| 500,000 | all | +0.109 [+0.069, +0.153] | +0.084 [+0.044, +0.126] | +0.008 [-0.122, +0.141] | -0.004 [-0.121, +0.116] |
| 1,000,000 | all | +0.101 [+0.053, +0.153] | +0.057 [+0.007, +0.108] | +0.020 [-0.098, +0.144] | -0.024 [-0.127, +0.086] |
| 1,000,000 | grow | -0.023 [-0.089, +0.039] | -0.096 [-0.161, -0.036] | -0.348 [-0.503, -0.194] | -0.410 [-0.529, -0.288] |
| 1,000,000 | solvent | -0.115 [-0.206, -0.030] | -0.154 [-0.238, -0.077] | -0.321 [-0.457, -0.180] | -0.368 [-0.492, -0.238] |
| 1,000,000 | treasury | +0.270 [+0.184, +0.359] | +0.279 [+0.186, +0.378] | +0.093 [-0.014, +0.214] | +0.141 [+0.032, +0.257] |
| 1,000,000 | recover | +0.364 [+0.275, +0.452] | +0.265 [+0.152, +0.381] | +0.888 [+0.685, +1.110] | +0.724 [+0.518, +0.938] |
| 1,000,000 | power | +0.012 [+0.003, +0.023] | -0.012 [-0.030, +0.002] | -0.211 [-0.340, -0.091] | -0.210 [-0.261, -0.161] |

## 5. Real success given up against the engine-trained learner

Engine-trained minus emulator-trained, paired by city: open loop (the oracle's acceptance of each policy's own logs; `\RlLost*`) and closed loop (each policy acting on the engine).

| snapshot | scope | open loop, ladder | closed loop, ladder | open loop, main checkpoint | closed loop, main checkpoint | open loop, ladder, instance-weighted |
|---|---|---|---|---|---|---|
| 250,000 | all | +0.023 [+0.011, +0.036] | +0.019 [+0.005, +0.032] | +0.026 [+0.014, +0.041] | +0.025 [+0.011, +0.039] | +0.023 [+0.012, +0.036] |
| 500,000 | all | +0.045 [+0.025, +0.066] | +0.050 [+0.031, +0.071] | +0.051 [+0.030, +0.074] | +0.057 [+0.037, +0.078] | +0.046 [+0.026, +0.067] |
| 1,000,000 | all | +0.089 [+0.067, +0.114] | +0.106 [+0.083, +0.132] | +0.093 [+0.069, +0.118] | +0.105 [+0.080, +0.133] | +0.091 [+0.069, +0.116] |
| 1,000,000 | grow | +0.011 [-0.016, +0.047] | +0.031 [-0.003, +0.073] | -0.002 [-0.027, +0.033] | +0.008 [-0.041, +0.057] | +0.011 [-0.016, +0.047] |
| 1,000,000 | solvent | +0.067 [+0.007, +0.140] | +0.168 [+0.101, +0.242] | +0.087 [+0.014, +0.175] | +0.196 [+0.124, +0.277] | +0.067 [+0.007, +0.140] |
| 1,000,000 | treasury | +0.250 [+0.202, +0.302] | +0.227 [+0.183, +0.277] | +0.280 [+0.221, +0.343] | +0.255 [+0.202, +0.316] | +0.250 [+0.202, +0.302] |
| 1,000,000 | recover | +0.028 [+0.003, +0.056] | +0.041 [+0.006, +0.080] | +0.019 [-0.017, +0.054] | +0.023 [-0.020, +0.073] | +0.028 [+0.003, +0.056] |
| 1,000,000 | power | +0.091 [+0.032, +0.160] | +0.062 [+0.021, +0.110] | +0.079 [+0.025, +0.144] | +0.044 [+0.008, +0.088] | +0.091 [+0.032, +0.160] |

Instance-weighted open-loop loss at 1,000,000 months, city BCa: +0.091 [+0.070, +0.115]. Engine-seed variation of the reference is not in any interval (1 or 3 seeds per family).

## 6. Coverage: the coverage model and the main checkpoint against the same reference (1,000,000 months)

| scope | gap, main | gap, coverage | gap excess, main | gap excess, coverage | coverage minus main (gap) | inflation excess, main | inflation excess, coverage |
|---|---|---|---|---|---|---|---|
| all | +0.133 [+0.083, +0.185] | +0.059 [+0.014, +0.104] | +0.057 [+0.007, +0.108] | -0.018 [-0.062, +0.026] | -0.074 [-0.103, -0.047] | -0.024 [-0.127, +0.086] | -0.106 [-0.199, -0.007] |
| grow | -0.015 [-0.078, +0.039] | -0.022 [-0.086, +0.033] | -0.096 [-0.161, -0.036] | -0.103 [-0.171, -0.042] | -0.007 [-0.027, +0.015] | -0.410 [-0.529, -0.288] | -0.398 [-0.521, -0.270] |
| solvent | -0.005 [-0.083, +0.059] | -0.023 [-0.106, +0.059] | -0.154 [-0.238, -0.077] | -0.171 [-0.262, -0.084] | -0.018 [-0.057, +0.023] | -0.368 [-0.492, -0.238] | -0.369 [-0.485, -0.251] |
| treasury | +0.259 [+0.161, +0.359] | +0.076 [-0.006, +0.159] | +0.279 [+0.186, +0.378] | +0.096 [+0.017, +0.180] | -0.183 [-0.258, -0.117] | +0.141 [+0.032, +0.257] | -0.014 [-0.117, +0.100] |
| recover | +0.440 [+0.304, +0.577] | +0.263 [+0.143, +0.381] | +0.265 [+0.152, +0.381] | +0.088 [-0.006, +0.181] | -0.177 [-0.246, -0.104] | +0.724 [+0.518, +0.938] | +0.325 [+0.145, +0.517] |
| power | -0.012 [-0.030, +0.002] | +0.001 [-0.012, +0.014] | -0.012 [-0.030, +0.002] | +0.001 [-0.012, +0.014] | +0.014 [+0.000, +0.033] | -0.210 [-0.261, -0.161] | -0.076 [-0.124, -0.031] |

City intervals only: one coverage model against one main checkpoint, 3 RL seeds each.

## 7. How the reference learner was chosen (facts for the paper)

The engine-trained learner is the RL arm's frozen learner  trained on the engine for 1,000,000 months. The variant was chosen by rule 2 of the working notes: the better of `b8` and `stab_spatial` by the mean of the power and grow oracle pass rates at 1,000,000 months of engine-trained seed-0 runs, judged on the same 40 evaluation instances per family on which every RL number is read . Two of the runs that made the choice (`engine__power__s0__tasks_v2_H24__v-stab_spatial`, `engine__grow__s0__tasks_v2_H24__v-stab_spatial`) are cells of the reference. Seeds per family in the reference: grow 3, solvent 1, treasury 3, recover 3, power 1 (runs: grow: engine__grow__s0__tasks_v2_H24__v-stab_spatial, engine__grow__s1__tasks_v2_H24, engine__grow__s2__tasks_v2_H24; solvent: engine__solvent__s0__tasks_v2_H24__v-stab_spatial; treasury: engine__treasury__s0__tasks_v2_H24, engine__treasury__s1__tasks_v2_H24, engine__treasury__s2__tasks_v2_H24; recover: engine__recover__s0__tasks_v2_H24__v-stab_spatial, engine__recover__s1__tasks_v2_H24, engine__recover__s2__tasks_v2_H24; power: engine__power__s0__tasks_v2_H24__v-stab_spatial). `results/rl/bc/variant_rule.json` is a different rule (the higher mean of the power and grow oracle pass rates at 1,000,000 months; a tie keeps bc: chose `bc`) between the warm-started variants (`bc`, `bc_kl`); the reference runs are trained from scratch and are not warm-started.
