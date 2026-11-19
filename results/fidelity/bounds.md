# Bounds of the engine's state space

Each bounded quantity has a censored likelihood: the predictive mass beyond a bound is the probability of the bound, so sampling and pinning to the bound is exactly the trained model (dc.model.BOUND_SOURCES; code/scripts/bounds_table.py writes this file). A bound is kept only where the engine makes it a fact; paths are under engine/ (src/ for the simulator).

## Table

| kind | entry | bound | engine source or data type | caveat |
|---|---|---|---|---|
| scalar | funds | [0, inf] | totalFunds changes only in spend/setFunds (src/micropolis.cpp:1066-1081): a tool is refused when totalFunds < cost (src/tool.cpp:154, charged at :127); the budget pays at most taxFund + totalFunds, otherwise nothing and auto-budget switches off (src/budget.cpp:124-230, 268-310); setFunds is otherwise called only at load or reset | spend/setFunds take a 32-bit int: holds below 2,147,483,647 |
| scalar | res_valve | [-2000, 2000] | clamp to +-RES_VALVE_RANGE (src/simulate.cpp:671; = 2000, src/micropolis.h:286) |  |
| scalar | com_valve | [-1500, 1500] | clamp to +-COM_VALVE_RANGE (src/simulate.cpp:672; = 1500, src/micropolis.h:287) |  |
| scalar | ind_valve | [-1500, 1500] | clamp to +-IND_VALVE_RANGE (src/simulate.cpp:673; = 1500, src/micropolis.h:288) |  |
| scalar | res_pop | [0, inf] | zeroed by the census (src/simulate.cpp:699), then += zone population 0..40 (src/zone.cpp:556-562, 711-715) | 16-bit short: would wrap only above 32,767 (more than 819 fully grown residential zones) |
| scalar | com_pop | [0, inf] | zeroed by the census (src/simulate.cpp:700), then += zone population 0..5 (src/zone.cpp:774, 866-873) |  |
| scalar | ind_pop | [0, inf] | zeroed by the census (src/simulate.cpp:701), then += zone population 0..4 (src/zone.cpp:926, 1001-1008) |  |
| scalar | score | [0, 1000] | cityScore = (cityScore + clamp(z, 0, 1000)) / 2 (src/evaluate.cpp:464-466); starts at 500 (src/evaluate.cpp:155, src/initialize.cpp:94); a loaded score outside 1..999 becomes 500 (src/simulate.cpp:504-506) |  |
| scalar | tax_fund | [0, inf] | totalPop * landValueAverage / 120 * cityTax * FLevels, all factors non-negative (src/simulate.cpp:887); 0 at src/simulate.cpp:559 |  |
| scalar | road_spend | [0, inf] | set to an allocation min(fund x percent, cash left) or to the fund (src/budget.cpp:115-230, 280-282, 306-308); percents clamped to [0, 1] (c_api.cpp:139-141) |  |
| scalar | fire_spend | [0, inf] | as road_spend (src/budget.cpp:280, 306) |  |
| scalar | police_spend | [0, inf] | as road_spend (src/budget.cpp:281, 307) |  |
| scalar | powered_zones | [0, inf] | zeroed by the census (src/simulate.cpp:694), ++ per powered zone (src/zone.cpp:100) |  |
| scalar | unpowered_zones | [0, inf] | zeroed by the census (src/simulate.cpp:695), ++ per unpowered zone (src/zone.cpp:102) |  |
| scalar | coal_plants | [0, inf] | zeroed by the census (src/simulate.cpp:710), ++ per plant (src/simulate.cpp:1462) |  |
| scalar | nuclear_plants | [0, inf] | zeroed by the census (src/simulate.cpp:711), ++ per plant (src/simulate.cpp:1482) |  |
| scalar | road_total | [0, inf] | zeroed by the census (src/simulate.cpp:697), += 1, 2 or 4 per road tile (src/simulate.cpp:1077, 1102, 1113) | 16-bit short: would wrap only above 32,767 |
| cost | build_cost | [0, inf] | monthBuildCost += before - after only when funds fell (c_api.cpp:151-153); zeroed every month (c_api.cpp:178) |  |
| ledger | sprite_cycle | none | unbounded: tick counter spriteCycle++ (src/sprite.cpp:570) in a short; it wraps from 32,767 to -32,768, so a saturating bound would be wrong |  |
| ledger | total_pop | [0, inf] | (short)(resPop / 8 + comPop + indPop) (src/simulate.cpp:611-613); 1 or 0 at src/simulate.cpp:314, 418 | non-negative while res_pop is |
| ledger | res_hist0 | [0, inf] | resHist[0] = resPop / 8 (src/simulate.cpp:733, 761) | non-negative while res_pop is |
| ledger | res_hist1 | [0, inf] | previous resHist[0] (shift at src/simulate.cpp:748) | non-negative while res_pop is |
| ledger | com_hist0 | [0, inf] | comHist[0] = comPop (src/simulate.cpp:762) |  |
| ledger | com_hist1 | [0, inf] | previous comHist[0] (src/simulate.cpp:749) |  |
| ledger | ind_hist0 | [0, inf] | indHist[0] = indPop (src/simulate.cpp:763) |  |
| ledger | ind_hist1 | [0, inf] | previous indHist[0] (src/simulate.cpp:750) |  |
| ledger | res_cap | [0, 1] | bool resCap (src/micropolis.h:2117) |  |
| ledger | com_cap | [0, 1] | bool comCap (src/micropolis.h:2118) |  |
| ledger | ind_cap | [0, 1] | bool indCap (src/micropolis.h:2119) |  |
| ledger | need_hospital | [-1, 1] | assigned only -1, 0 or 1 (src/simulate.cpp:778-787; src/zone.cpp:296) |  |
| ledger | need_church | [-1, 1] | assigned only -1, 0 or 1 (src/simulate.cpp:792-801; src/zone.cpp:312) |  |
| ledger | road_fund | [0, inf] | (roadTotal + 2 railTotal) * RLevels (src/simulate.cpp:886); 0 at src/initialize.cpp:101 |  |
| ledger | police_fund | [0, inf] | policeStationPop * 100 (src/simulate.cpp:884); 0 at src/initialize.cpp:102 |  |
| ledger | fire_fund | [0, inf] | fireStationPop * 100 (src/simulate.cpp:885); 0 at src/initialize.cpp:103 |  |
| ledger | auto_budget | [0, 1] | bool autoBudget (src/micropolis.h:2354) |  |
| ledger | fire_pop | [0, inf] | zeroed by the census (src/simulate.cpp:696), ++ per fire tile (src/simulate.cpp:975) |  |
| ledger | city_center_x | [0, 119] | mean x of zone tiles, x in 0..119, or WORLD_W / 2 with no zones (src/scan.cpp:143-154, 177-182) |  |
| ledger | city_center_y | [0, 99] | mean y of zone tiles, y in 0..99, or WORLD_H / 2 with no zones (src/scan.cpp:143-154, 177-182) |  |
| ledger | pollution_max_x | [0, 118] | x of a 2 x 2 pollution block, x = 0, 2, ..., 118 (src/scan.cpp:305-317); 0 at src/micropolis.cpp:516 |  |
| ledger | pollution_max_y | [0, 98] | y of a 2 x 2 pollution block, y = 0, 2, ..., 98 (src/scan.cpp:305-317); 0 at src/micropolis.cpp:516 |  |
| ledger | flood_count | [0, 30] | set to 30 (src/disasters.cpp:369), decremented while non-zero (src/disasters.cpp:102-103) |  |
| ledger | abs_dist | [0, inf] | absoluteValue(dispX) + absoluteValue(dispY) (src/sprite.cpp:508-510); 0 at src/micropolis.cpp:613 |  |
| overlay | half overlays (5) | [0, 255] | byte maps MapByte2 (src/map_type.h:346; src/micropolis.h:1262-1266) |  |
| overlay | rate of growth | [-200, 200] | clamp to +-200 (src/zone.cpp:355; decay src/simulate.cpp:385, 392) |  |
| overlay | fire, police coverage | [0, inf] | sums of non-negative station effects (src/simulate.cpp:1515-1517, 1545-1547), smoothed by averaging (src/scan.cpp:90-112) |  |
| overlay | terrain | [0, 255] | byte map MapByte4 (src/micropolis.h:1273) |  |
| overlay | com_rate | [-64, 64] | 64 - 4 * (min(distance, 64) / 2) (src/scan.cpp:591-594, 408) |  |

Derived, not learned (no likelihood): sim_cycle (+4 mod 1024), initial_eval (0), disasters (copied); tax (the action's), city_time (+4), pop = 20 (res_pop + 8 (com_pop + ind_pop)).

## Funds below zero

Funds below zero is impossible in the engine, not merely unseen: totalFunds changes only through spend and setFunds (src/micropolis.cpp:1066-1081); every charge is checked first (a tool is refused when totalFunds < cost, src/tool.cpp:154; the yearly budget pays at most taxFund + totalFunds and otherwise pays nothing and switches auto-budget off, src/budget.cpp:124-230, 268-310); setFunds is otherwise called only at load or reset with a fixed positive amount. The one caveat is arithmetic: spend and setFunds take a 32-bit int, so the bound holds while funds stay below 2,147,483,647.

## The stores' values

Minimum and maximum, share of observations at the lower / upper bound, and observations beyond the bounds (transitions for build_cost). Overlays: every cell of every observation of heldout_eval and train_eval.

### train_full

| entry | bound | n | min | max | at lower | at upper | beyond |
|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 3,049,000 | 0 | 1012171 | 14.24% | n/a | 0 |
| res_valve | [-2000, 2000] | 3,049,000 | -2000 | 2000 | 5.36% | 63.83% | 0 |
| com_valve | [-1500, 1500] | 3,049,000 | -1500 | 1500 | 17.46% | 23.55% | 0 |
| ind_valve | [-1500, 1500] | 3,049,000 | -1500 | 1500 | 15.49% | 26.34% | 0 |
| res_pop | [0, inf] | 3,049,000 | 0 | 6054 | 0.09% | n/a | 0 |
| com_pop | [0, inf] | 3,049,000 | 0 | 329 | 0.29% | n/a | 0 |
| ind_pop | [0, inf] | 3,049,000 | 0 | 488 | 0.14% | n/a | 0 |
| score | [0, 1000] | 3,049,000 | 0 | 903 | 0.0039% | 0.00% | 0 |
| tax_fund | [0, inf] | 3,049,000 | 0 | 15008 | 13.32% | n/a | 0 |
| road_spend | [0, inf] | 3,049,000 | 0 | 3780 | 12.70% | n/a | 0 |
| fire_spend | [0, inf] | 3,049,000 | 0 | 3800 | 24.04% | n/a | 0 |
| police_spend | [0, inf] | 3,049,000 | 0 | 3700 | 23.21% | n/a | 0 |
| powered_zones | [0, inf] | 3,049,000 | 0 | 618 | 1.50% | n/a | 0 |
| unpowered_zones | [0, inf] | 3,049,000 | 0 | 608 | 46.74% | n/a | 0 |
| coal_plants | [0, inf] | 3,049,000 | 0 | 22 | 24.26% | n/a | 0 |
| nuclear_plants | [0, inf] | 3,049,000 | 0 | 13 | 36.03% | n/a | 0 |
| road_total | [0, inf] | 3,049,000 | 0 | 5418 | 0.10% | n/a | 0 |
| build_cost | [0, inf] | 3,000,000 | 0 | 21018 | 80.62% | n/a | 0 |
| sprite_cycle | [-inf, inf] | 3,049,000 | -32608 | 32609 | n/a | n/a | 0 |
| total_pop | [0, inf] | 3,049,000 | 0 | 1349 | 0.03% | n/a | 0 |
| res_hist0 | [0, inf] | 3,049,000 | 0 | 759 | 0.15% | n/a | 0 |
| res_hist1 | [0, inf] | 3,049,000 | 0 | 759 | 0.15% | n/a | 0 |
| com_hist0 | [0, inf] | 3,049,000 | 0 | 329 | 0.30% | n/a | 0 |
| com_hist1 | [0, inf] | 3,049,000 | 0 | 329 | 0.33% | n/a | 0 |
| ind_hist0 | [0, inf] | 3,049,000 | 0 | 488 | 0.14% | n/a | 0 |
| ind_hist1 | [0, inf] | 3,049,000 | 0 | 488 | 0.13% | n/a | 0 |
| res_cap | [0, 1] | 3,049,000 | 0 | 1 | 98.06% | 1.94% | 0 |
| com_cap | [0, 1] | 3,049,000 | 0 | 1 | 98.92% | 1.08% | 0 |
| ind_cap | [0, 1] | 3,049,000 | 0 | 1 | 99.36% | 0.64% | 0 |
| need_hospital | [-1, 1] | 3,049,000 | -1 | 1 | 2.71% | 20.21% | 0 |
| need_church | [-1, 1] | 3,049,000 | -1 | 1 | 2.12% | 30.49% | 0 |
| road_fund | [0, inf] | 3,049,000 | 0 | 3811 | 11.79% | n/a | 0 |
| police_fund | [0, inf] | 3,049,000 | 0 | 3700 | 13.93% | n/a | 0 |
| fire_fund | [0, inf] | 3,049,000 | 0 | 3800 | 19.08% | n/a | 0 |
| auto_budget | [0, 1] | 3,049,000 | 0 | 1 | 15.61% | 84.39% | 0 |
| fire_pop | [0, inf] | 3,049,000 | 0 | 854 | 92.33% | n/a | 0 |
| city_center_x | [0, 119] | 3,049,000 | 17 | 101 | 0.00% | 0.00% | 0 |
| city_center_y | [0, 99] | 3,049,000 | 9 | 84 | 0.00% | 0.00% | 0 |
| pollution_max_x | [0, 118] | 3,049,000 | 0 | 118 | 0.0004% | 0.0020% | 0 |
| pollution_max_y | [0, 98] | 3,049,000 | 0 | 98 | 0.0003% | 0.0002% | 0 |
| flood_count | [0, 30] | 3,049,000 | 0 | 30 | 99.43% | 0.0066% | 0 |
| abs_dist | [0, inf] | 3,049,000 | 0 | 3588 | 64.94% | n/a | 0 |

### heldout_eval

| entry | bound | n | min | max | at lower | at upper | beyond |
|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 73,200 | 0 | 49230 | 11.75% | n/a | 0 |
| res_valve | [-2000, 2000] | 73,200 | -2000 | 2000 | 6.23% | 63.99% | 0 |
| com_valve | [-1500, 1500] | 73,200 | -1500 | 1500 | 17.08% | 27.76% | 0 |
| ind_valve | [-1500, 1500] | 73,200 | -1500 | 1500 | 16.40% | 25.56% | 0 |
| res_pop | [0, inf] | 73,200 | 0 | 4385 | 0.02% | n/a | 0 |
| com_pop | [0, inf] | 73,200 | 0 | 276 | 0.09% | n/a | 0 |
| ind_pop | [0, inf] | 73,200 | 0 | 402 | 0.03% | n/a | 0 |
| score | [0, 1000] | 73,200 | 1 | 807 | 0.00% | 0.00% | 0 |
| tax_fund | [0, inf] | 73,200 | 0 | 13524 | 12.51% | n/a | 0 |
| road_spend | [0, inf] | 73,200 | 0 | 1903 | 12.27% | n/a | 0 |
| fire_spend | [0, inf] | 73,200 | 0 | 1700 | 14.22% | n/a | 0 |
| police_spend | [0, inf] | 73,200 | 0 | 2300 | 18.10% | n/a | 0 |
| powered_zones | [0, inf] | 73,200 | 0 | 428 | 1.20% | n/a | 0 |
| unpowered_zones | [0, inf] | 73,200 | 0 | 306 | 48.06% | n/a | 0 |
| coal_plants | [0, inf] | 73,200 | 0 | 9 | 38.99% | n/a | 0 |
| nuclear_plants | [0, inf] | 73,200 | 0 | 9 | 24.21% | n/a | 0 |
| road_total | [0, inf] | 73,200 | 33 | 1152 | 0.00% | n/a | 0 |
| build_cost | [0, inf] | 72,000 | 0 | 15550 | 79.84% | n/a | 0 |
| sprite_cycle | [-inf, inf] | 73,200 | -32608 | 32609 | n/a | n/a | 0 |
| total_pop | [0, inf] | 73,200 | 1 | 1099 | 0.00% | n/a | 0 |
| res_hist0 | [0, inf] | 73,200 | 0 | 548 | 0.05% | n/a | 0 |
| res_hist1 | [0, inf] | 73,200 | 0 | 548 | 0.05% | n/a | 0 |
| com_hist0 | [0, inf] | 73,200 | 0 | 276 | 0.09% | n/a | 0 |
| com_hist1 | [0, inf] | 73,200 | 0 | 276 | 0.09% | n/a | 0 |
| ind_hist0 | [0, inf] | 73,200 | 0 | 402 | 0.03% | n/a | 0 |
| ind_hist1 | [0, inf] | 73,200 | 0 | 402 | 0.03% | n/a | 0 |
| res_cap | [0, 1] | 73,200 | 0 | 1 | 96.84% | 3.16% | 0 |
| com_cap | [0, 1] | 73,200 | 0 | 1 | 99.54% | 0.46% | 0 |
| ind_cap | [0, 1] | 73,200 | 0 | 1 | 99.71% | 0.29% | 0 |
| need_hospital | [-1, 1] | 73,200 | -1 | 1 | 1.75% | 22.65% | 0 |
| need_church | [-1, 1] | 73,200 | -1 | 1 | 1.35% | 36.85% | 0 |
| road_fund | [0, inf] | 73,200 | 0 | 1903 | 11.52% | n/a | 0 |
| police_fund | [0, inf] | 73,200 | 0 | 2300 | 11.54% | n/a | 0 |
| fire_fund | [0, inf] | 73,200 | 0 | 1700 | 11.56% | n/a | 0 |
| auto_budget | [0, 1] | 73,200 | 0 | 1 | 12.69% | 87.31% | 0 |
| fire_pop | [0, inf] | 73,200 | 0 | 367 | 95.46% | n/a | 0 |
| city_center_x | [0, 119] | 73,200 | 19 | 98 | 0.00% | 0.00% | 0 |
| city_center_y | [0, 99] | 73,200 | 16 | 83 | 0.00% | 0.00% | 0 |
| pollution_max_x | [0, 118] | 73,200 | 2 | 116 | 0.00% | 0.00% | 0 |
| pollution_max_y | [0, 98] | 73,200 | 2 | 96 | 0.00% | 0.00% | 0 |
| flood_count | [0, 30] | 73,200 | 0 | 26 | 99.57% | 0.00% | 0 |
| abs_dist | [0, inf] | 73,200 | 0 | 3305 | 65.59% | n/a | 0 |
| half overlays (5) | [0, 255] | 1,098,000,000 | 0 | 255 | 84.48% | 0.06% | 0 |
| rate of growth | [-200, 200] | 14,274,000 | -200 | 200 | 0.06% | 0.03% | 0 |
| fire, police coverage | [0, inf] | 28,548,000 | 0 | 684 | 68.29% | n/a | 0 |
| terrain | [0, 255] | 54,900,000 | 0 | 127 | 11.44% | 0.00% | 0 |
| com_rate | [-64, 64] | 14,274,000 | -64 | 64 | 44.92% | 0.04% | 0 |

### train_eval

| entry | bound | n | min | max | at lower | at upper | beyond |
|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 98,000 | 0 | 1000000 | 10.56% | n/a | 0 |
| res_valve | [-2000, 2000] | 98,000 | -2000 | 2000 | 4.83% | 63.90% | 0 |
| com_valve | [-1500, 1500] | 98,000 | -1500 | 1500 | 17.20% | 24.04% | 0 |
| ind_valve | [-1500, 1500] | 98,000 | -1500 | 1500 | 15.15% | 27.03% | 0 |
| res_pop | [0, inf] | 98,000 | 2 | 6037 | 0.00% | n/a | 0 |
| com_pop | [0, inf] | 98,000 | 0 | 326 | 0.12% | n/a | 0 |
| ind_pop | [0, inf] | 98,000 | 1 | 442 | 0.00% | n/a | 0 |
| score | [0, 1000] | 98,000 | 30 | 878 | 0.00% | 0.00% | 0 |
| tax_fund | [0, inf] | 98,000 | 0 | 14140 | 16.63% | n/a | 0 |
| road_spend | [0, inf] | 98,000 | 0 | 3621 | 15.32% | n/a | 0 |
| fire_spend | [0, inf] | 98,000 | 0 | 3500 | 26.38% | n/a | 0 |
| police_spend | [0, inf] | 98,000 | 0 | 3500 | 23.27% | n/a | 0 |
| powered_zones | [0, inf] | 98,000 | 0 | 619 | 0.68% | n/a | 0 |
| unpowered_zones | [0, inf] | 98,000 | 0 | 476 | 49.03% | n/a | 0 |
| coal_plants | [0, inf] | 98,000 | 0 | 12 | 24.45% | n/a | 0 |
| nuclear_plants | [0, inf] | 98,000 | 0 | 12 | 35.16% | n/a | 0 |
| road_total | [0, inf] | 98,000 | 0 | 5180 | 0.16% | n/a | 0 |
| build_cost | [0, inf] | 96,000 | 0 | 20534 | 77.45% | n/a | 0 |
| sprite_cycle | [-inf, inf] | 98,000 | 0 | 15346 | n/a | n/a | 0 |
| total_pop | [0, inf] | 98,000 | 1 | 1347 | 0.00% | n/a | 0 |
| res_hist0 | [0, inf] | 98,000 | 0 | 753 | 0.01% | n/a | 0 |
| res_hist1 | [0, inf] | 98,000 | 0 | 753 | 0.01% | n/a | 0 |
| com_hist0 | [0, inf] | 98,000 | 0 | 326 | 0.12% | n/a | 0 |
| com_hist1 | [0, inf] | 98,000 | 0 | 326 | 0.17% | n/a | 0 |
| ind_hist0 | [0, inf] | 98,000 | 1 | 442 | 0.00% | n/a | 0 |
| ind_hist1 | [0, inf] | 98,000 | 1 | 442 | 0.00% | n/a | 0 |
| res_cap | [0, 1] | 98,000 | 0 | 1 | 98.35% | 1.65% | 0 |
| com_cap | [0, 1] | 98,000 | 0 | 1 | 98.80% | 1.20% | 0 |
| ind_cap | [0, 1] | 98,000 | 0 | 1 | 99.32% | 0.68% | 0 |
| need_hospital | [-1, 1] | 98,000 | -1 | 1 | 2.63% | 21.56% | 0 |
| need_church | [-1, 1] | 98,000 | -1 | 1 | 2.13% | 32.06% | 0 |
| road_fund | [0, inf] | 98,000 | 0 | 3651 | 14.95% | n/a | 0 |
| police_fund | [0, inf] | 98,000 | 0 | 3500 | 16.75% | n/a | 0 |
| fire_fund | [0, inf] | 98,000 | 0 | 3500 | 22.67% | n/a | 0 |
| auto_budget | [0, 1] | 98,000 | 0 | 1 | 10.76% | 89.24% | 0 |
| fire_pop | [0, inf] | 98,000 | 0 | 789 | 93.23% | n/a | 0 |
| city_center_x | [0, 119] | 98,000 | 18 | 101 | 0.00% | 0.00% | 0 |
| city_center_y | [0, 99] | 98,000 | 13 | 83 | 0.00% | 0.00% | 0 |
| pollution_max_x | [0, 118] | 98,000 | 2 | 116 | 0.00% | 0.00% | 0 |
| pollution_max_y | [0, 98] | 98,000 | 2 | 96 | 0.00% | 0.00% | 0 |
| flood_count | [0, 30] | 98,000 | 0 | 30 | 99.43% | 0.0092% | 0 |
| abs_dist | [0, inf] | 98,000 | 0 | 3198 | 66.23% | n/a | 0 |
| half overlays (5) | [0, 255] | 1,470,000,000 | 0 | 255 | 81.42% | 0.05% | 0 |
| rate of growth | [-200, 200] | 19,110,000 | -200 | 200 | 0.03% | 0.04% | 0 |
| fire, police coverage | [0, inf] | 38,220,000 | 0 | 548 | 70.34% | n/a | 0 |
| terrain | [0, 255] | 73,500,000 | 0 | 127 | 11.96% | 0.00% | 0 |
| com_rate | [-64, 64] | 19,110,000 | -64 | 64 | 44.06% | 0.06% | 0 |
