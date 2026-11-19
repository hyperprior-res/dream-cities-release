# Treasury identity: os_50m_full/samples_006000000

Form A (protocol): funds[t+1] = funds[t] - build_cost[t] + [budget month t] (tax_fund - road_spend - fire_spend - police_spend)[t+1]. The budget month is the month whose start city_time is 44 mod 48 (the yearly collectTax at cityTime % 48 == 0, simulate.cpp:206). Form B (the engine's accounting): in a budget month with auto-budget on at t+1 the paid amounts sum_i (int)(fund_i x level_i) (ledger road_fund, fire_fund, police_fund at t+1; the month's funding levels) replace the reported spends (budget.cpp:118-120, 296-306); otherwise A.

## On engine trajectories

5014 engine trajectories (1832 of the patched plans on oracle seeds 0..7; 3182 selected or behaviour plans of the identity pass on one seed each, `seed_for('patching-identity', start, forced events, plan hash)`), 120336 months, of which 10028 budget months.

| months | n | form A holds | form B holds |
|---|---|---|---|
| all | 120336 | 117645 | 120336 |
| not a budget month | 110308 | 110308 | 110308 |
| budget month | 10028 | 7337 | 10028 |
| budget, auto-budget on after, all three levels 100 | 6592 | 6592 | 6592 |
| budget, auto-budget on after, some level below 100 | 2696 | 5 | 2696 |
| budget, auto-budget off after | 740 | 740 | 740 |

## On the emulator's sampled trajectories (8 samples per plan, empty mask)

Breach = residual not 0 (the emulator's scalars are integers in float32; months with |funds| >= 2^24 are left out and counted). Rates per month; 'any' = share of samples with at least one breach.

### The secondary claim's measure (amendment 5): money created as a share of the starting treasury

Per trajectory (one of the 8 samples of a plan): the sum over the 24 months of the form-B residual (positive: funds rose by more than the accounts allow), divided by the funds at month 0. Breached above 5%, with 1% and 10% beside it. Selected plans are split by the audit's verdict on the record (`grader_p` >= 0.5: the emulator accepts) and counted once per record. Interval: 95 % BCa cluster bootstrap over held-out families (2,000 resamples). Left out: trajectories with a non-positive starting treasury or a month with |funds| >= 2^24.

| plans | trajectories | left out | B: > 1% | B: > 5% | B: > 10% | B: mean share | A: > 5% | A: mean share |
|---|---|---|---|---|---|---|---|---|
| behaviour plans | 14168 | 0 | 2819/14168 0.199 | 1206/14168 0.09 [0.06, 0.14] | 677/14168 0.048 | +0.0088 | 2701/14168 0.191 | +0.0340 |
| selected: best_of_n B=1, emulator accepts | 120 | 0 | 24/120 0.200 | 3/120 0.03 [0.01, 0.06] | 0/120 0.000 | +0.0053 | 3/120 0.025 | +0.0051 |
| selected: best_of_n B=1, emulator rejects | 672 | 0 | 98/672 0.146 | 36/672 0.05 [0.02, 0.11] | 6/672 0.009 | +0.0056 | 36/672 0.054 | +0.0057 |
| selected: best_of_n B=10, emulator accepts | 336 | 0 | 79/336 0.235 | 18/336 0.05 [0.03, 0.09] | 3/336 0.009 | +0.0093 | 19/336 0.057 | +0.0095 |
| selected: best_of_n B=10, emulator rejects | 456 | 0 | 104/456 0.228 | 19/456 0.04 [0.02, 0.09] | 4/456 0.009 | +0.0069 | 22/456 0.048 | +0.0074 |
| selected: best_of_n B=100, emulator accepts | 368 | 0 | 89/368 0.242 | 15/368 0.04 [0.02, 0.08] | 3/368 0.008 | +0.0086 | 17/368 0.046 | +0.0087 |
| selected: best_of_n B=100, emulator rejects | 424 | 0 | 65/424 0.153 | 15/424 0.04 [0.02, 0.06] | 1/424 0.002 | +0.0044 | 15/424 0.035 | +0.0046 |
| selected: best_of_n B=1000, emulator accepts | 320 | 0 | 76/320 0.237 | 24/320 0.07 [0.04, 0.14] | 6/320 0.019 | +0.0115 | 24/320 0.075 | +0.0115 |
| selected: best_of_n B=1000, emulator rejects | 472 | 0 | 87/472 0.184 | 20/472 0.04 [0.02, 0.08] | 4/472 0.008 | +0.0063 | 20/472 0.042 | +0.0061 |
| selected: cem B=1, emulator accepts | 32 | 0 | 3/32 0.094 | 1/32 0.03 [0.00, 0.09] | 0/32 0.000 | +0.0002 | 2/32 0.062 | +0.0261 |
| selected: cem B=1, emulator rejects | 1512 | 0 | 230/1512 0.152 | 80/1512 0.05 [0.03, 0.10] | 38/1512 0.025 | -0.0034 | 358/1512 0.237 | +0.0384 |
| selected: cem B=10, emulator accepts | 32 | 0 | 4/32 0.125 | 1/32 0.03 [0.00, 0.09] | 1/32 0.031 | +0.0029 | 8/32 0.250 | +0.0332 |
| selected: cem B=10, emulator rejects | 1512 | 0 | 303/1512 0.200 | 151/1512 0.10 [0.06, 0.16] | 80/1512 0.053 | +0.0079 | 358/1512 0.237 | +0.0457 |
| selected: cem B=100, emulator accepts | 40 | 0 | 7/40 0.175 | 6/40 0.15 [0.00, 0.60] | 3/40 0.075 | +0.0186 | 9/40 0.225 | +0.0402 |
| selected: cem B=100, emulator rejects | 1504 | 0 | 411/1504 0.273 | 188/1504 0.12 [0.08, 0.19] | 107/1504 0.071 | +0.0142 | 462/1504 0.307 | +0.0541 |
| selected: cem B=1000, emulator accepts | 88 | 0 | 19/88 0.216 | 9/88 0.10 [0.03, 0.20] | 5/88 0.057 | +0.0110 | 18/88 0.205 | +0.0328 |
| selected: cem B=1000, emulator rejects | 1456 | 0 | 404/1456 0.277 | 188/1456 0.13 [0.08, 0.20] | 97/1456 0.067 | +0.0111 | 416/1456 0.286 | +0.0488 |
| selected: random B=1, emulator accepts | 152 | 0 | 6/152 0.039 | 0/152 0.00 [0.00, 0.00] | 0/152 0.000 | +0.0001 | 5/152 0.033 | +0.0045 |
| selected: random B=1, emulator rejects | 1392 | 0 | 231/1392 0.166 | 71/1392 0.05 [0.02, 0.11] | 41/1392 0.029 | -0.0023 | 189/1392 0.136 | +0.0078 |
| selected: random B=10, emulator accepts | 336 | 0 | 47/336 0.140 | 11/336 0.03 [0.01, 0.08] | 6/336 0.018 | +0.0044 | 20/336 0.060 | +0.0076 |
| selected: random B=10, emulator rejects | 1208 | 0 | 260/1208 0.215 | 118/1208 0.10 [0.06, 0.16] | 71/1208 0.059 | +0.0143 | 250/1208 0.207 | +0.0420 |
| selected: random B=100, emulator accepts | 488 | 0 | 114/488 0.234 | 42/488 0.09 [0.05, 0.15] | 17/488 0.035 | +0.0112 | 65/488 0.133 | +0.0223 |
| selected: random B=100, emulator rejects | 1056 | 0 | 230/1056 0.218 | 111/1056 0.11 [0.06, 0.17] | 50/1056 0.047 | +0.0096 | 216/1056 0.205 | +0.0391 |
| selected: random B=1000, emulator accepts | 560 | 0 | 173/560 0.309 | 64/560 0.11 [0.06, 0.19] | 34/560 0.061 | +0.0181 | 87/560 0.155 | +0.0303 |
| selected: random B=1000, emulator rejects | 984 | 0 | 243/984 0.247 | 124/984 0.13 [0.07, 0.21] | 69/984 0.070 | +0.0134 | 249/984 0.253 | +0.0454 |
| selected: random_verdict B=1, emulator accepts | 144 | 0 | 6/144 0.042 | 0/144 0.00 [0.00, 0.00] | 0/144 0.000 | +0.0004 | 5/144 0.035 | +0.0045 |
| selected: random_verdict B=1, emulator rejects | 1400 | 0 | 231/1400 0.165 | 71/1400 0.05 [0.02, 0.11] | 41/1400 0.029 | -0.0023 | 189/1400 0.135 | +0.0078 |
| selected: random_verdict B=10, emulator accepts | 464 | 0 | 81/464 0.175 | 34/464 0.07 [0.03, 0.15] | 18/464 0.039 | +0.0099 | 60/464 0.129 | +0.0208 |
| selected: random_verdict B=10, emulator rejects | 1080 | 0 | 179/1080 0.166 | 73/1080 0.07 [0.04, 0.13] | 40/1080 0.037 | +0.0034 | 179/1080 0.166 | +0.0221 |
| selected: random_verdict B=100, emulator accepts | 848 | 0 | 192/848 0.226 | 74/848 0.09 [0.06, 0.13] | 32/848 0.038 | +0.0096 | 117/848 0.138 | +0.0213 |
| selected: random_verdict B=100, emulator rejects | 696 | 0 | 114/696 0.164 | 55/696 0.08 [0.04, 0.14] | 37/696 0.053 | +0.0077 | 157/696 0.226 | +0.0475 |
| selected: random_verdict B=1000, emulator accepts | 200 | 0 | 48/200 0.240 | 19/200 0.10 [0.03, 0.22] | 8/200 0.040 | +0.0107 | 34/200 0.170 | +0.0475 |
| selected: random_verdict B=1000, emulator rejects | 120 | 0 | 32/120 0.267 | 14/120 0.12 [0.04, 0.27] | 10/120 0.083 | +0.0213 | 27/120 0.225 | +0.0647 |

### Per month

Selected plans are counted once per record (method, search budget); behaviour plans are the first behaviour-mix plans of each (start, forced events) group.

| plans | samples | months | unrepresentable months | A: rate all / yearly-budget / other months | B: rate all / yearly-budget / other months | B: any | B: median, p90 abs residual | B on samples passing the predicate: rate, any |
|---|---|---|---|---|---|---|---|---|
| behaviour plans | 14168 | 340032 | 0 | 0.364 / 0.988 / 0.308 | 0.364 / 0.987 / 0.308 | 1.000 | 7, 70 | n/a (no instance) |
| selected: best_of_n B=1 | 792 | 19008 | 0 | 0.368 / 0.985 / 0.312 | 0.366 / 0.970 / 0.312 | 1.000 | 5, 33 | 0.501, 1.000 (117 samples) |
| selected: best_of_n B=10 | 792 | 19008 | 0 | 0.441 / 0.978 / 0.393 | 0.442 / 0.989 / 0.393 | 1.000 | 4, 34 | 0.475, 1.000 (288 samples) |
| selected: best_of_n B=100 | 792 | 19008 | 0 | 0.451 / 0.983 / 0.402 | 0.451 / 0.985 / 0.402 | 1.000 | 4, 33 | 0.503, 1.000 (320 samples) |
| selected: best_of_n B=1000 | 792 | 19008 | 0 | 0.450 / 0.982 / 0.401 | 0.450 / 0.984 / 0.401 | 1.000 | 4, 33 | 0.504, 1.000 (330 samples) |
| selected: cem B=1 | 1544 | 37056 | 0 | 0.385 / 0.995 / 0.330 | 0.385 / 0.992 / 0.330 | 1.000 | 6, 61 | 0.457, 1.000 (48 samples) |
| selected: cem B=10 | 1544 | 37056 | 0 | 0.422 / 0.997 / 0.369 | 0.421 / 0.991 / 0.369 | 1.000 | 6, 77 | 0.465, 1.000 (51 samples) |
| selected: cem B=100 | 1544 | 37056 | 0 | 0.454 / 0.998 / 0.404 | 0.453 / 0.991 / 0.404 | 1.000 | 6, 85 | 0.480, 1.000 (64 samples) |
| selected: cem B=1000 | 1544 | 37056 | 0 | 0.457 / 0.998 / 0.408 | 0.456 / 0.989 / 0.408 | 1.000 | 6, 82 | 0.513, 1.000 (96 samples) |
| selected: random B=1 | 1544 | 37056 | 0 | 0.296 / 0.986 / 0.233 | 0.296 / 0.987 / 0.233 | 1.000 | 9, 79 | 0.390, 1.000 (175 samples) |
| selected: random B=10 | 1544 | 37056 | 0 | 0.415 / 0.983 / 0.363 | 0.415 / 0.983 / 0.363 | 1.000 | 6, 65 | 0.474, 1.000 (325 samples) |
| selected: random B=100 | 1544 | 37056 | 0 | 0.432 / 0.990 / 0.381 | 0.432 / 0.993 / 0.381 | 1.000 | 5, 63 | 0.457, 1.000 (513 samples) |
| selected: random B=1000 | 1544 | 37056 | 0 | 0.416 / 0.981 / 0.365 | 0.416 / 0.978 / 0.365 | 1.000 | 6, 75 | 0.482, 1.000 (516 samples) |
| selected: random_verdict B=1 | 1544 | 37056 | 0 | 0.296 / 0.986 / 0.233 | 0.296 / 0.987 / 0.233 | 1.000 | 9, 79 | 0.390, 1.000 (175 samples) |
| selected: random_verdict B=10 | 1544 | 37056 | 0 | 0.372 / 0.986 / 0.317 | 0.372 / 0.983 / 0.317 | 1.000 | 6, 59 | 0.478, 1.000 (305 samples) |
| selected: random_verdict B=100 | 1544 | 37056 | 0 | 0.396 / 0.992 / 0.342 | 0.396 / 0.990 / 0.342 | 1.000 | 6, 69 | 0.447, 1.000 (497 samples) |
| selected: random_verdict B=1000 | 320 | 7680 | 0 | 0.407 / 0.989 / 0.354 | 0.408 / 0.995 / 0.354 | 1.000 | 6, 75 | 0.489, 1.000 (124 samples) |
