# Treasury identity: os_50m_full/samples_006000000

Form A (protocol): funds[t+1] = funds[t] - build_cost[t] + [budget month t] (tax_fund - road_spend - fire_spend - police_spend)[t+1]. The budget month is the month whose start city_time is 44 mod 48 (the yearly collectTax at cityTime % 48 == 0, simulate.cpp:206). Form B (the engine's accounting): in a budget month with auto-budget on at t+1 the paid amounts sum_i (int)(fund_i x level_i) (ledger road_fund, fire_fund, police_fund at t+1; the month's funding levels) replace the reported spends (budget.cpp:118-120, 296-306); otherwise A.

## On engine trajectories

840 engine trajectories (840 of the patched plans on oracle seeds 0..7; 0 selected or behaviour plans of the identity pass on one seed each, `seed_for('patching-identity', start, forced events, plan hash)`), 20160 months, of which 1680 budget months.

| months | n | form A holds | form B holds |
|---|---|---|---|
| all | 20160 | 20024 | 20160 |
| not a budget month | 18480 | 18480 | 18480 |
| budget month | 1680 | 1544 | 1680 |
| budget, auto-budget on after, all three levels 100 | 1452 | 1452 | 1452 |
| budget, auto-budget on after, some level below 100 | 136 | 0 | 136 |
| budget, auto-budget off after | 92 | 92 | 92 |

## On the emulator's sampled trajectories (8 samples per plan, empty mask)

Breach = residual not 0 (the emulator's scalars are integers in float32; months with |funds| >= 2^24 are left out and counted). Rates per month; 'any' = share of samples with at least one breach.

Selected plans are counted once per record (method, search budget); behaviour plans are the first behaviour-mix plans of each (start, forced events) group.

| plans | samples | months | unrepresentable months | A: rate all / yearly-budget / other months | B: rate all / yearly-budget / other months | B: any | B: median, p90 abs residual | B on samples passing the predicate: rate, any |
|---|---|---|---|---|---|---|---|---|
