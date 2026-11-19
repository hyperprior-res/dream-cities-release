# Treasury identity: pilot5_bk/samples_000600064

Form A (protocol): funds[t+1] = funds[t] - build_cost[t] + [budget month t] (tax_fund - road_spend - fire_spend - police_spend)[t+1]. The budget month is the month whose start city_time is 44 mod 48 (the yearly collectTax at cityTime % 48 == 0, simulate.cpp:206). Form B (the engine's accounting): in a budget month with auto-budget on at t+1 the paid amounts sum_i (int)(fund_i x level_i) (ledger road_fund, fire_fund, police_fund at t+1; the month's funding levels) replace the reported spends (budget.cpp:118-120, 296-306); otherwise A.

## On engine trajectories

465 engine trajectories (168 of the patched plans on oracle seeds 0..7; 297 selected or behaviour plans of the identity pass on one seed each, `seed_for('patching-identity', start, forced events, plan hash)`), 11160 months, of which 930 budget months.

| months | n | form A holds | form B holds |
|---|---|---|---|
| all | 11160 | 10889 | 11160 |
| not a budget month | 10230 | 10230 | 10230 |
| budget month | 930 | 659 | 930 |
| budget, auto-budget on after, all three levels 100 | 591 | 591 | 591 |
| budget, auto-budget on after, some level below 100 | 271 | 0 | 271 |
| budget, auto-budget off after | 68 | 68 | 68 |

## On the emulator's sampled trajectories (8 samples per plan, empty mask)

Breach = residual not 0 (the emulator's scalars are integers in float32; months with |funds| >= 2^24 are left out and counted). Rates per month; 'any' = share of samples with at least one breach.

Selected plans are counted once per record (method, search budget); behaviour plans are the first behaviour-mix plans of each (start, forced events) group.

| plans | samples | months | unrepresentable months | A: rate all / yearly-budget / other months | B: rate all / yearly-budget / other months | B: any | B: median, p90 abs residual | B on samples passing the predicate: rate, any |
|---|---|---|---|---|---|---|---|---|

Not computable on 10 start groups: the model revision's sampled state carries no build_cost (ladder-v1 samples the charged cost inside its third stage but does not keep it in the state; ladder-v2 does), so the identity's build-cost term is unknown on the emulator side.
