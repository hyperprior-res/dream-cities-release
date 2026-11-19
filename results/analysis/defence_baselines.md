# Defences beside their own undefended model 

Generated 2026-11-12T13:00:46Z by `PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/defence_baselines.py` from `results/defences/frontier.json` only (sha256 632a9abe44905377). B = 1,000; 60 instances in 39 city families. Each setting beside its own undefended model, read from its `judge` field: member 0 for member-0 settings, the ensemble for ensemble settings. Rates: value [95 % BCa] as stored (cluster bootstrap over city families, 2,000 resamples, seed 0; `*` percentile where BCa is undefined; `†` no hacked unit, the exact one-sided bound on clusters). Differences are point values on the same 60 instances; the only paired interval frontier.json stores is false acceptance minus the undefended ensemble's, shown for ensemble settings. Real success: the oracle accepts the selected plan.

## random search

Undefended: member 0: false acceptance 0.133 [0.059, 0.245], false rejection 0.292 [0.133, 0.500], real success 0.400 [0.288, 0.507]; ensemble: false acceptance 0.217 [0.116, 0.388], false rejection 0.269 [0.130, 0.440], real success 0.433 [0.322, 0.568].
Perfect emulator: false acceptance 0.050 [0.015, 0.136], false rejection 0.088 [0.025, 0.229], real success 0.567 [0.437, 0.722].

| setting | own baseline | false acceptance | minus baseline | paired interval | false rejection | minus baseline | real success | minus baseline | hacked / false rejections / oracle accepts (baseline) |
|---|---|---|---|---|---|---|---|---|---|
| member 0, temperature 0.75 | member 0 | 0.183 [0.082, 0.309] | +0.050 | point only | 0.278 [0.125, 0.500] | -0.014 | 0.300 [0.197, 0.425] | -0.100 | 11 / 5 / 18 (8 / 7 / 24) |
| member 0, temperature 1.25 | member 0 | 0.067 [0.018, 0.145] | -0.067 | point only | 0.842 [0.616, 1.000] | +0.550 | 0.317 [0.212, 0.432] | -0.083 | 4 / 16 / 19 (8 / 7 / 24) |
| member 0, temperature 1.5 | member 0 | 0.000 [0.000, 0.074]† | -0.133 | point only | 1.000 [1.000, 1.000] | +0.708 | 0.267 [0.156, 0.400] | -0.133 | 0 / 16 / 16 (8 / 7 / 24) |
| ensemble, disagreement penalty lambda 1 | ensemble | 0.083 [0.021, 0.186] | -0.133 | [-0.226, -0.041] | 0.739 [0.500, 0.905] | +0.470 | 0.383 [0.275, 0.518] | -0.050 | 5 / 17 / 23 (13 / 7 / 26) |
| ensemble, disagreement penalty lambda 2 | ensemble | 0.050 [0.014, 0.127] | -0.167 | [-0.350, -0.065] | 0.769 [0.560, 0.909] | +0.500 | 0.433 [0.308, 0.582] | +0.000 | 3 / 20 / 26 (13 / 7 / 26) |
| ensemble, halt above 95th percentile | ensemble | 0.217 [0.116, 0.388] | +0.000 | [+0.000, +0.000] | 0.269 [0.130, 0.440] | +0.000 | 0.433 [0.322, 0.568] | +0.000 | 13 / 7 / 26 (13 / 7 / 26) |
| ensemble, halt above 80th percentile | ensemble | 0.200 [0.098, 0.375] | -0.017 | [-0.094, +0.000] | 0.308 [0.160, 0.500] | +0.038 | 0.433 [0.322, 0.568] | +0.000 | 12 / 8 / 26 (13 / 7 / 26) |
| ensemble, detector p > 0.5 | ensemble | 0.133 [0.068, 0.226] | -0.083 | [-0.183, +0.018] | 0.423 [0.241, 0.625] | +0.154 | 0.433 [0.333, 0.549] | +0.000 | 8 / 11 / 26 (13 / 7 / 26) |
| ensemble, detector p > 0.2 | ensemble | 0.033 [0.000, 0.107] | -0.183 | [-0.313, -0.091] | 0.720 [0.538, 0.846] | +0.451 | 0.417 [0.292, 0.547] | -0.017 | 2 / 18 / 25 (13 / 7 / 26) |
| member 0, deflation (Smith-Winkler) | member 0 | 0.017 [0.000, 0.102] | -0.117 | point only | 0.625 [0.455, 0.773] | +0.333 | 0.400 [0.288, 0.507] | +0.000 | 1 / 15 / 24 (8 / 7 / 24) |
| ensemble, deflation (Smith-Winkler) | ensemble | 0.067 [0.000, 0.231] | -0.150 | [-0.237, -0.083] | 0.615 [0.458, 0.777] | +0.346 | 0.433 [0.322, 0.568] | +0.000 | 4 / 16 / 26 (13 / 7 / 26) |
| ensemble, penalty lambda 0 (neutral point: the verdict's added mean-margin condition) | ensemble | 0.100 [0.036, 0.200] | -0.117 | [-0.211, -0.051] | 0.654 [0.439, 0.828] | +0.385 | 0.433 [0.322, 0.568] | +0.000 | 6 / 17 / 26 (13 / 7 / 26) |
| policy-aware | - | slot: trained and attacked by another builder; not run here | | | | | | | |

### Disagreement penalty as increments over lambda = 0

lambda = 0 (ensemble, penalty lambda 0 (neutral point: the verdict's added mean-margin condition)) selects the same plan as the undefended ensemble on 60 of 60 instances; against the ensemble it changes false acceptance by -0.117 [-0.211, -0.051] (paired, stored), false rejection by +0.385 and real success by +0.000 (points).

| lambda | same plan as ensemble | false acceptance | minus lambda 0 | false rejection | minus lambda 0 | real success | minus lambda 0 |
|---|---|---|---|---|---|---|---|
| 1 | 30 | 0.083 [0.021, 0.186] | -0.017 | 0.739 [0.500, 0.905] | +0.085 | 0.383 [0.275, 0.518] | -0.050 |
| 2 | 22 | 0.050 [0.014, 0.127] | -0.050 | 0.769 [0.560, 0.909] | +0.115 | 0.433 [0.308, 0.582] | +0.000 |

Increments are point values: frontier.json stores each penalty setting's paired difference from the undefended ensemble, not from lambda 0, and no per-instance outcomes.

## pool-seeded search

Undefended: member 0: false acceptance 0.250 [0.136, 0.383], false rejection 0.333 [0.083, 0.712], real success 0.200 [0.111, 0.301]; ensemble: false acceptance 0.217 [0.119, 0.314], false rejection 0.059 [0.000, 0.312], real success 0.283 [0.197, 0.386].
Perfect emulator: false acceptance 0.100 [0.033, 0.194], false rejection 0.138 [0.045, 0.269], real success 0.483 [0.357, 0.667].

| setting | own baseline | false acceptance | minus baseline | paired interval | false rejection | minus baseline | real success | minus baseline | hacked / false rejections / oracle accepts (baseline) |
|---|---|---|---|---|---|---|---|---|---|
| member 0, temperature 0.75 | member 0 | 0.233 [0.143, 0.339] | -0.017 | point only | 0.176 [0.050, 0.467] | -0.157 | 0.283 [0.180, 0.388] | +0.083 | 14 / 3 / 17 (15 / 4 / 12) |
| member 0, temperature 1.25 | member 0 | 0.050 [0.014, 0.130] | -0.200 | point only | 0.750 [0.550, 0.923] | +0.417 | 0.267 [0.170, 0.424] | +0.067 | 3 / 12 / 16 (15 / 4 / 12) |
| member 0, temperature 1.5 | member 0 | 0.000 [0.000, 0.074]† | -0.250 | point only | 0.923 [0.600, 1.000] | +0.590 | 0.217 [0.104, 0.397] | +0.017 | 0 / 12 / 13 (15 / 4 / 12) |
| ensemble, disagreement penalty lambda 1 | ensemble | 0.117 [0.038, 0.231] | -0.100 | [-0.194, -0.017] | 0.762 [0.533, 0.923] | +0.703 | 0.350 [0.248, 0.500] | +0.067 | 7 / 16 / 21 (13 / 1 / 17) |
| ensemble, disagreement penalty lambda 2 | ensemble | 0.033 [0.000, 0.114] | -0.183 | [-0.292, -0.100] | 0.727 [0.487, 0.905] | +0.668 | 0.367 [0.271, 0.479] | +0.083 | 2 / 16 / 22 (13 / 1 / 17) |
| ensemble, halt above 95th percentile | ensemble | 0.250 [0.143, 0.366] | +0.033 | [+0.000, +0.102] | 0.062 [0.000, 0.308] | +0.004 | 0.267 [0.172, 0.393] | -0.017 | 15 / 1 / 16 (13 / 1 / 17) |
| ensemble, halt above 80th percentile | ensemble | 0.217 [0.133, 0.312] | +0.000 | [-0.085, +0.083] | 0.150 [0.042, 0.389] | +0.091 | 0.333 [0.236, 0.463] | +0.050 | 13 / 3 / 20 (13 / 1 / 17) |
| ensemble, detector p > 0.5 | ensemble | 0.167 [0.081, 0.297] | -0.050 | [-0.167, +0.079] | 0.385 [0.143, 0.667] | +0.326 | 0.217 [0.133, 0.322] | -0.067 | 10 / 5 / 13 (13 / 1 / 17) |
| ensemble, detector p > 0.2 | ensemble | 0.050 [0.016, 0.100] | -0.167 | [-0.286, -0.054] | 0.846 [0.583, 1.000] | +0.787 | 0.217 [0.125, 0.340] | -0.067 | 3 / 11 / 13 (13 / 1 / 17) |
| member 0, deflation (Smith-Winkler) | member 0 | 0.050 [0.000, 0.156] | -0.200 | point only | 0.667 [0.364, 0.909] | +0.333 | 0.200 [0.111, 0.301] | +0.000 | 3 / 8 / 12 (15 / 4 / 12) |
| ensemble, deflation (Smith-Winkler) | ensemble | 0.083 [0.020, 0.182] | -0.133 | [-0.235, -0.056] | 0.412 [0.188, 0.647] | +0.353 | 0.283 [0.197, 0.386] | +0.000 | 5 / 7 / 17 (13 / 1 / 17) |
| ensemble, penalty lambda 0 (neutral point: the verdict's added mean-margin condition) | ensemble | 0.100 [0.037, 0.186] | -0.117 | [-0.192, -0.056] | 0.471 [0.235, 0.722] | +0.412 | 0.283 [0.197, 0.386] | +0.000 | 6 / 8 / 17 (13 / 1 / 17) |
| policy-aware | - | slot: trained and attacked by another builder; not run here | | | | | | | |

### Disagreement penalty as increments over lambda = 0

lambda = 0 (ensemble, penalty lambda 0 (neutral point: the verdict's added mean-margin condition)) selects the same plan as the undefended ensemble on 60 of 60 instances; against the ensemble it changes false acceptance by -0.117 [-0.192, -0.056] (paired, stored), false rejection by +0.412 and real success by +0.000 (points).

| lambda | same plan as ensemble | false acceptance | minus lambda 0 | false rejection | minus lambda 0 | real success | minus lambda 0 |
|---|---|---|---|---|---|---|---|
| 1 | 14 | 0.117 [0.038, 0.231] | +0.017 | 0.762 [0.533, 0.923] | +0.291 | 0.350 [0.248, 0.500] | +0.067 |
| 2 | 9 | 0.033 [0.000, 0.114] | -0.067 | 0.727 [0.487, 0.905] | +0.257 | 0.367 [0.271, 0.479] | +0.083 |

Increments are point values: frontier.json stores each penalty setting's paired difference from the undefended ensemble, not from lambda 0, and no per-instance outcomes.

## Checks

- random temp0.75: stored hackability_minus_ensemble -0.033333 equals the rates' difference -0.033333.
- random temp1.25: stored hackability_minus_ensemble -0.150000 equals the rates' difference -0.150000.
- random temp1.5: stored hackability_minus_ensemble -0.216667 equals the rates' difference -0.216667.
- random penalty1: stored hackability_minus_ensemble -0.133333 equals the rates' difference -0.133333.
- random penalty2: stored hackability_minus_ensemble -0.166667 equals the rates' difference -0.166667.
- random halt95: stored hackability_minus_ensemble +0.000000 equals the rates' difference +0.000000.
- random halt80: stored hackability_minus_ensemble -0.016667 equals the rates' difference -0.016667.
- random detector0.5: stored hackability_minus_ensemble -0.083333 equals the rates' difference -0.083333.
- random detector0.2: stored hackability_minus_ensemble -0.183333 equals the rates' difference -0.183333.
- random deflation-member0: stored hackability_minus_ensemble -0.200000 equals the rates' difference -0.200000.
- random deflation-ensemble: stored hackability_minus_ensemble -0.150000 equals the rates' difference -0.150000.
- random penalty0: stored hackability_minus_ensemble -0.116667 equals the rates' difference -0.116667.
- cem_seeded temp0.75: stored hackability_minus_ensemble +0.016667 equals the rates' difference +0.016667.
- cem_seeded temp1.25: stored hackability_minus_ensemble -0.166667 equals the rates' difference -0.166667.
- cem_seeded temp1.5: stored hackability_minus_ensemble -0.216667 equals the rates' difference -0.216667.
- cem_seeded penalty1: stored hackability_minus_ensemble -0.100000 equals the rates' difference -0.100000.
- cem_seeded penalty2: stored hackability_minus_ensemble -0.183333 equals the rates' difference -0.183333.
- cem_seeded halt95: stored hackability_minus_ensemble +0.033333 equals the rates' difference +0.033333.
- cem_seeded halt80: stored hackability_minus_ensemble +0.000000 equals the rates' difference +0.000000.
- cem_seeded detector0.5: stored hackability_minus_ensemble -0.050000 equals the rates' difference -0.050000.
- cem_seeded detector0.2: stored hackability_minus_ensemble -0.166667 equals the rates' difference -0.166667.
- cem_seeded deflation-member0: stored hackability_minus_ensemble -0.166667 equals the rates' difference -0.166667.
- cem_seeded deflation-ensemble: stored hackability_minus_ensemble -0.133333 equals the rates' difference -0.133333.
- cem_seeded penalty0: stored hackability_minus_ensemble -0.116667 equals the rates' difference -0.116667.
