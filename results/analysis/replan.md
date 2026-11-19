# Monthly replanning 

Generated 2026-11-13T09:30:07Z by `code/scripts/replan_axis.py` from {'emulator': 'results/replan/emulator', 'engine': 'results/replan/engine', 'audit_emulator': 'results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24', 'audit_engine': 'results/audit/engine_reference/tasks_v2_H24/B_economy'}. 100 instances (grow 20, solvent 20, treasury 20, recover 20, power 20) in 39 start-state families; plans per replan {'emulator': [1000], 'engine': [1000]}. means over instances; cluster bootstrap over start-state families, 2000 resamples, seed 0, BCa 95 per cent (pressure_axis.bca_est); differences paired by instance; a reading uses the BCa limits, or the percentile limits where BCa is undefined.

Definitions: **real_success**: the realised trajectory (the instance's oracle seed 0) passes the task; **false_acceptance**: the model accepts its month-0 choice (8 samples, at least 4 pass) and the realised trajectory fails; **replan**: random search replanned every month from the engine's real state, the selected plan's month executed each month; **open_loop**: the model's month-0 choice executed in full on the same realised seed; **open_loop_oracle**: the open-loop arm judged by the oracle's majority of 32 seeds (as the audit judges); **excess_false_acceptance**: emulator minus perfect emulator, paired by instance; **shortfall_real_success**: perfect emulator minus emulator, paired by instance.

## Readings

| reading | quantity | estimate [interval] | reading | wording |
|---|---|---|---|---|
| R-a | excess false acceptance under replanning (emulator minus perfect emulator) | +0.130 [+0.055, +0.205] | above | "the excess false acceptance survives monthly replanning". |
| R-b | excess false acceptance under replanning minus the open-loop excess, same instances and seed | +0.170 [+0.090, +0.257] | above | "replanning increases the excess". |
| R-c | shortfall in real success under replanning (perfect emulator minus emulator) | +0.300 [+0.196, +0.423] | above | "the shortfall in real success survives monthly replanning". |
| R-d | shortfall in real success under replanning minus the open-loop shortfall, same instances and seed | +0.200 [+0.086, +0.337] | above | "replanning increases the shortfall in real success". |

## Measures per model and arm

| subset | n | model | judge accepts month-0 choice | real success, replan | real success, open loop | false acceptance, replan | false acceptance, open loop | months the plan in hand was kept (mean, of 23) |
|---|---|---|---|---|---|---|---|---|
| pooled | 100 | emulator | 0.410 [0.314, 0.514] | 0.400 [0.301, 0.509] | 0.390 [0.307, 0.477] | 0.230 [0.165, 0.300] | 0.160 [0.099, 0.231] | 21.5 |
| pooled | 100 | engine | 0.630 [0.537, 0.740] | 0.700 [0.617, 0.787] | 0.490 [0.410, 0.585] | 0.100 [0.057, 0.148] | 0.200 [0.126, 0.288] | 21.7 |
| grow | 20 | emulator | 0.150 [0.050, 0.400] | 0.400 [0.200, 0.600] | 0.350 [0.150, 0.600] | 0.050 [0.000, 0.250] | 0.050 [0.000, 0.250] | 21.8 |
| grow | 20 | engine | 0.500 [0.300, 0.700] | 0.550 [0.350, 0.750] | 0.400 [0.200, 0.650] | 0.200 [0.050, 0.450] | 0.300 [0.150, 0.550] | 21.6 |
| solvent | 20 | emulator | 0.000 [0.000, 0.139] | 0.300 [0.150, 0.550] | 0.150 [0.050, 0.350] | 0.000 [0.000, 0.139] | 0.000 [0.000, 0.139] | 21.2 |
| solvent | 20 | engine | 0.300 [0.107, 0.550] | 0.400 [0.200, 0.600] | 0.200 [0.050, 0.400] | 0.050 [0.000, 0.299] | 0.150 [0.050, 0.350] | 21.3 |
| treasury | 20 | emulator | 0.450 [0.250, 0.700] | 0.500 [0.300, 0.700] | 0.300 [0.100, 0.550] | 0.200 [0.050, 0.400] | 0.250 [0.100, 0.500] | 21.2 |
| treasury | 20 | engine | 0.700 [0.450, 0.900] | 1.000 [0.861, 1.000] | 0.450 [0.200, 0.650] | 0.000 [0.000, 0.139] | 0.250 [0.100, 0.500] | 21.9 |
| recover | 20 | emulator | 0.650 [0.400, 0.850] | 0.600 [0.350, 0.800] | 0.350 [0.150, 0.585] | 0.250 [0.100, 0.500] | 0.400 [0.200, 0.650] | 21.8 |
| recover | 20 | engine | 0.650 [0.400, 0.850] | 0.550 [0.350, 0.750] | 0.400 [0.200, 0.650] | 0.250 [0.100, 0.500] | 0.300 [0.150, 0.550] | 21.4 |
| power | 20 | emulator | 0.800 [0.550, 0.950] | 0.200 [0.050, 0.400] | 0.800 [0.558, 0.950] | 0.650 [0.400, 0.850] | 0.100 [0.000, 0.300] | 21.3 |
| power | 20 | engine | 1.000 [0.861, 1.000] | 1.000 [0.861, 1.000] | 1.000 [0.861, 1.000] | 0.000 [0.000, 0.139] | 0.000 [0.000, 0.139] | 22.3 |

## Excess false acceptance and shortfall in real success, per arm

| subset | n | excess, replan | excess, open loop | shortfall, replan | shortfall, open loop |
|---|---|---|---|---|---|
| pooled | 100 | +0.130 [+0.055, +0.205] | -0.040 [-0.146, +0.056] | +0.300 [+0.196, +0.423] | +0.100 [+0.028, +0.173] |
| grow | 20 | -0.150 [-0.400, +0.050] | -0.250 [-0.500, -0.050] | +0.150 [-0.100, +0.400] | +0.050 [-0.200, +0.300] |
| solvent | 20 | -0.050 [-0.299, +0.000] | -0.150 [-0.350, -0.050] | +0.100 [-0.150, +0.382] | +0.050 [-0.100, +0.200] |
| treasury | 20 | +0.200 [+0.050, +0.400] | +0.000 [-0.250, +0.300] | +0.500 [+0.300, +0.700] | +0.150 [-0.100, +0.400] |
| recover | 20 | +0.000 [-0.250, +0.250] | +0.100 [-0.150, +0.350] | -0.050 [-0.250, +0.150] | +0.050 [-0.150, +0.250] |
| power | 20 | +0.650 [+0.400, +0.850] | +0.100 [+0.000, +0.300] | +0.800 [+0.600, +0.950] | +0.200 [+0.050, +0.442] |

## The open-loop arm under the oracle's majority beside the audit's random search at B = 1,000

the replanning run draws fresh proposals at month 0, the audit searched the logged plans: the two agree up to those draws; both are printed.

| model | n | source | judge accepts | real success (majority) | false acceptance (majority) | agreement |
|---|---|---|---|---|---|---|
| emulator | 100 | replanning run, month-0 choice | 0.410 [0.314, 0.514] | 0.340 [0.246, 0.446] | 0.150 [0.092, 0.228] |  |
| emulator | 100 | audit | 0.410 [0.326, 0.495] | 0.370 [0.295, 0.457] | 0.150 [0.091, 0.225] | same judge verdict 78, same oracle verdict 85, same false acceptance 86 |
| engine | 100 | replanning run, month-0 choice | 0.630 [0.537, 0.740] | 0.580 [0.487, 0.682] | 0.110 [0.053, 0.190] |  |
| engine | 100 | audit | 0.550 [0.450, 0.670] | 0.510 [0.403, 0.627] | 0.080 [0.033, 0.168] | same judge verdict 68, same oracle verdict 77, same false acceptance 81 |

Coverage: emulator only 0, perfect emulator only 0. Analysed: the first 100 positions of the fixed order (the largest prefix of 5k complete on both sides); held by both beyond it: 0.
