# Monthly replanning 

Generated 2026-11-12T23:19:00Z by `code/scripts/replan_axis.py` from {'emulator': 'results/replan/dryrun/emulator_cpu', 'engine': 'results/replan/dryrun/engine', 'audit_emulator': 'results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24', 'audit_engine': 'results/audit/engine_reference/tasks_v2_H24/B_economy'}. 2 instances (grow 1, solvent 1, treasury 0, recover 0, power 0) in 2 start-state families; plans per replan {'emulator': [8], 'engine': [50]}. means over instances; cluster bootstrap over start-state families, 2000 resamples, seed 0, BCa 95 per cent (pressure_axis.bca_est); differences paired by instance; a reading uses the BCa limits, or the percentile limits where BCa is undefined.

Definitions: **real_success**: the realised trajectory (the instance's oracle seed 0) passes the task; **false_acceptance**: the model accepts its month-0 choice (8 samples, at least 4 pass) and the realised trajectory fails; **replan**: random search replanned every month from the engine's real state, the selected plan's month executed each month; **open_loop**: the model's month-0 choice executed in full on the same realised seed; **open_loop_oracle**: the open-loop arm judged by the oracle's majority of 32 seeds (as the audit judges); **excess_false_acceptance**: emulator minus perfect emulator, paired by instance; **shortfall_real_success**: perfect emulator minus emulator, paired by instance.

## Readings

| reading | quantity | estimate [interval] | reading | wording |
|---|---|---|---|---|
| R-a | excess false acceptance under replanning (emulator minus perfect emulator) | +0.000 [+0.000, +0.000] | includes_zero | "under monthly replanning no excess false acceptance is established on these instances". Interval width 0.000; the paper gives the interval's width and says this is not evidence of absence. |
| R-b | excess false acceptance under replanning minus the open-loop excess, same instances and seed | +0.000 [+0.000, +0.000] | includes_zero | "no change in the excess under replanning is established". |
| R-c | shortfall in real success under replanning (perfect emulator minus emulator) | +0.000 [+0.000, +0.000] | includes_zero | "under monthly replanning no shortfall in real success is established on these instances". Interval width 0.000; the paper gives the interval's width and says this is not evidence of absence. |
| R-d | shortfall in real success under replanning minus the open-loop shortfall, same instances and seed | +0.000 [+0.000, +0.000] | includes_zero | "no change in the shortfall in real success under replanning is established". |

## Measures per model and arm

| subset | n | model | judge accepts month-0 choice | real success, replan | real success, open loop | false acceptance, replan | false acceptance, open loop |
|---|---|---|---|---|---|---|---|
| pooled | 2 | emulator | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] |
| pooled | 2 | engine | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] |
| grow | 1 | emulator | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] |
| grow | 1 | engine | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] |
| solvent | 1 | emulator | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] |
| solvent | 1 | engine | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] | 0.000 [0.000, 0.950] |

## Excess false acceptance and shortfall in real success, per arm

| subset | n | excess, replan | excess, open loop | shortfall, replan | shortfall, open loop |
|---|---|---|---|---|---|
| pooled | 2 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| grow | 1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| solvent | 1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

## The open-loop arm under the oracle's majority beside the audit's random search at B = 1,000

the replanning run draws fresh proposals at month 0, the audit searched the logged plans: the two agree up to those draws; both are printed.

| model | n | source | judge accepts | real success (majority) | false acceptance (majority) | agreement |
|---|---|---|---|---|---|---|
| emulator | 2 | replanning run, month-0 choice | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] |  |
| emulator | 2 | audit | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | same judge verdict 2, same oracle verdict 2, same false acceptance 2 |
| engine | 2 | replanning run, month-0 choice | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] |  |
| engine | 2 | audit | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | 0.000 [0.000, 0.776] | same judge verdict 2, same oracle verdict 2, same false acceptance 2 |

Coverage: emulator only 0, perfect emulator only 0.
