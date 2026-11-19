# Monthly replanning 

Generated 2026-11-13T09:30:07Z by `code/scripts/replan_axis.py` from {'emulator': 'results/replan/emulator', 'engine': 'results/replan/engine_fresh', 'audit_emulator': 'results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24', 'audit_engine': 'results/audit/engine_reference/tasks_v2_H24/B_economy'}. 100 instances (grow 20, solvent 20, treasury 20, recover 20, power 20) in 39 start-state families; plans per replan {'emulator': [1000], 'engine': [1000]}. means over instances; cluster bootstrap over start-state families, 2000 resamples, seed 0, BCa 95 per cent (pressure_axis.bca_est); differences paired by instance; a reading uses the BCa limits, or the percentile limits where BCa is undefined.

Definitions: **real_success**: the realised trajectory (the instance's oracle seed 0) passes the task; **false_acceptance**: the model accepts its month-0 choice (8 samples, at least 4 pass) and the realised trajectory fails; **replan**: random search replanned every month from the engine's real state, the selected plan's month executed each month; **open_loop**: the model's month-0 choice executed in full on the same realised seed; **open_loop_oracle**: the open-loop arm judged by the oracle's majority of 32 seeds (as the audit judges); **excess_false_acceptance**: emulator minus perfect emulator, paired by instance; **shortfall_real_success**: perfect emulator minus emulator, paired by instance.

## Readings

| reading | quantity | estimate [interval] | reading | wording |
|---|---|---|---|---|
| R-a | excess false acceptance under replanning (emulator minus perfect emulator) | +0.160 [+0.049, +0.245] | above | "the excess false acceptance survives monthly replanning". |
| R-b | excess false acceptance under replanning minus the open-loop excess, same instances and seed | +0.080 [+0.018, +0.154] | above | "replanning increases the excess". |
| R-c | shortfall in real success under replanning (perfect emulator minus emulator) | +0.320 [+0.193, +0.436] | above | "the shortfall in real success survives monthly replanning". |
| R-d | shortfall in real success under replanning minus the open-loop shortfall, same instances and seed | +0.080 [-0.029, +0.222] | includes_zero | "no change in the shortfall in real success under replanning is established". |

## Measures per model and arm

| subset | n | model | judge accepts month-0 choice | real success, replan | real success, open loop | false acceptance, replan | false acceptance, open loop | months the plan in hand was kept (mean, of 23) |
|---|---|---|---|---|---|---|---|---|
| pooled | 100 | emulator | 0.410 [0.314, 0.514] | 0.400 [0.301, 0.509] | 0.390 [0.307, 0.477] | 0.230 [0.165, 0.300] | 0.160 [0.099, 0.231] | 21.5 |
| pooled | 100 | engine | 0.590 [0.472, 0.701] | 0.720 [0.655, 0.785] | 0.630 [0.532, 0.700] | 0.070 [0.026, 0.149] | 0.080 [0.036, 0.148] | 22.0 |
| grow | 20 | emulator | 0.150 [0.050, 0.400] | 0.400 [0.200, 0.600] | 0.350 [0.150, 0.600] | 0.050 [0.000, 0.250] | 0.050 [0.000, 0.250] | 21.8 |
| grow | 20 | engine | 0.550 [0.350, 0.750] | 0.750 [0.528, 0.900] | 0.600 [0.400, 0.800] | 0.050 [0.000, 0.250] | 0.100 [0.000, 0.300] | 21.9 |
| solvent | 20 | emulator | 0.000 [0.000, 0.139] | 0.300 [0.150, 0.550] | 0.150 [0.050, 0.350] | 0.000 [0.000, 0.139] | 0.000 [0.000, 0.139] | 21.2 |
| solvent | 20 | engine | 0.300 [0.100, 0.550] | 0.450 [0.250, 0.650] | 0.300 [0.150, 0.550] | 0.050 [0.000, 0.299] | 0.050 [0.000, 0.299] | 21.8 |
| treasury | 20 | emulator | 0.450 [0.250, 0.700] | 0.500 [0.300, 0.700] | 0.300 [0.100, 0.550] | 0.200 [0.050, 0.400] | 0.250 [0.100, 0.500] | 21.2 |
| treasury | 20 | engine | 0.600 [0.400, 0.800] | 0.950 [0.750, 1.000] | 0.750 [0.500, 0.900] | 0.000 [0.000, 0.139] | 0.050 [0.000, 0.300] | 22.4 |
| recover | 20 | emulator | 0.650 [0.400, 0.850] | 0.600 [0.350, 0.800] | 0.350 [0.150, 0.585] | 0.250 [0.100, 0.500] | 0.400 [0.200, 0.650] | 21.8 |
| recover | 20 | engine | 0.500 [0.300, 0.700] | 0.450 [0.250, 0.650] | 0.500 [0.300, 0.700] | 0.250 [0.100, 0.450] | 0.200 [0.050, 0.400] | 21.7 |
| power | 20 | emulator | 0.800 [0.550, 0.950] | 0.200 [0.050, 0.400] | 0.800 [0.558, 0.950] | 0.650 [0.400, 0.850] | 0.100 [0.000, 0.300] | 21.3 |
| power | 20 | engine | 1.000 [0.861, 1.000] | 1.000 [0.861, 1.000] | 1.000 [0.861, 1.000] | 0.000 [0.000, 0.139] | 0.000 [0.000, 0.139] | 22.1 |

## Excess false acceptance and shortfall in real success, per arm

| subset | n | excess, replan | excess, open loop | shortfall, replan | shortfall, open loop |
|---|---|---|---|---|---|
| pooled | 100 | +0.160 [+0.049, +0.245] | +0.080 [-0.010, +0.160] | +0.320 [+0.193, +0.436] | +0.240 [+0.120, +0.343] |
| grow | 20 | +0.000 [-0.150, +0.150] | -0.050 [-0.250, +0.100] | +0.350 [+0.050, +0.600] | +0.250 [-0.050, +0.500] |
| solvent | 20 | -0.050 [-0.299, +0.000] | -0.050 [-0.299, +0.000] | +0.150 [-0.100, +0.400] | +0.150 [-0.050, +0.400] |
| treasury | 20 | +0.200 [+0.050, +0.400] | +0.200 [+0.050, +0.448] | +0.450 [+0.250, +0.650] | +0.450 [+0.250, +0.650] |
| recover | 20 | +0.000 [-0.250, +0.250] | +0.200 [-0.050, +0.425] | -0.150 [-0.450, +0.100] | +0.150 [-0.100, +0.400] |
| power | 20 | +0.650 [+0.400, +0.850] | +0.100 [+0.000, +0.300] | +0.800 [+0.600, +0.950] | +0.200 [+0.050, +0.442] |

## The open-loop arm under the oracle's majority beside the audit's random search at B = 1,000

the replanning run draws fresh proposals at month 0, the audit searched the logged plans: the two agree up to those draws; both are printed.

| model | n | source | judge accepts | real success (majority) | false acceptance (majority) | agreement |
|---|---|---|---|---|---|---|
| emulator | 100 | replanning run, month-0 choice | 0.410 [0.314, 0.514] | 0.340 [0.246, 0.446] | 0.150 [0.092, 0.228] |  |
| emulator | 100 | audit | 0.410 [0.326, 0.495] | 0.370 [0.295, 0.457] | 0.150 [0.091, 0.225] | same judge verdict 78, same oracle verdict 85, same false acceptance 86 |
| engine | 100 | replanning run, month-0 choice | 0.590 [0.472, 0.701] | 0.600 [0.500, 0.680] | 0.060 [0.027, 0.120] |  |
| engine | 100 | audit | 0.550 [0.450, 0.670] | 0.510 [0.403, 0.627] | 0.080 [0.033, 0.168] | same judge verdict 74, same oracle verdict 69, same false acceptance 88 |

Coverage: emulator only 0, perfect emulator only 0. Analysed: the first 100 positions of the fixed order (the largest prefix of 5k complete on both sides); held by both beyond it: 0.
