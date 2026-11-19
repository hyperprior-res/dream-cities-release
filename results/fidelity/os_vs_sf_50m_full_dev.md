# Check: self-forced final against one-step 6.0M

Selection dev (2000 transitions, 500 plans, key f5d737081dd2e7ae); one-step 6.0M: <cache>/ckpt/ladder_v2/os_50m_full/samples_006000000.pt (6,000,000 samples, decoding a, weights ema); self-forced final: <cache>/ckpt/ladder_v2/sf_50m_full/samples_001500032.pt (1,500,032 samples, decoding a, weights ema). One model sample at T=1 in every row.

| metric | one-step 6.0M | one-step 6.0M, other noise seed | self-forced final | evaluation noise | verdict |
|---|---|---|---|---|---|
| tile structural F1, one month | 0.1822 | n/a | 0.1718 | n/a | n/a |
| tile structural F1 since start, 12 months | 0.3746 | n/a | 0.3204 | n/a | n/a |
| tile structural F1 since start, 24 months | 0.3396 | n/a | 0.2822 | n/a | n/a |
| funds median rel. error, 12 months | 0.0383 | n/a | 0.0363 | n/a | better |
| funds median rel. error, 24 months | 0.0569 | n/a | 0.0705 | n/a | n/a |
| population median rel. error, 12 months | 0.0544 | n/a | 0.0485 | n/a | better |
| population median rel. error, 24 months | 0.0797 | n/a | 0.0799 | n/a | n/a |
| res_valve, one month from start (x copy) | 0.1001 | n/a | 0.1043 | n/a | n/a |
| com_valve, one month from start (x copy) | 0.0945 | n/a | 0.1022 | n/a | n/a |
| ind_valve, one month from start (x copy) | 0.0417 | n/a | 0.0507 | n/a | n/a |
| score, one month from start (x copy) | 0.2225 | n/a | 0.2218 | n/a | better |
| res_valve, 12 months (x copy) | 0.3820 | n/a | 0.3671 | n/a | better |
| com_valve, 12 months (x copy) | 0.4122 | n/a | 0.4753 | n/a | n/a |
| ind_valve, 12 months (x copy) | 0.3736 | n/a | 0.3955 | n/a | n/a |
| res_valve, 24 months (x copy) | 0.4616 | n/a | 0.4548 | n/a | better |
| com_valve, 24 months (x copy) | 0.6495 | n/a | 0.7243 | n/a | n/a |
| ind_valve, 24 months (x copy) | 0.7663 | n/a | 0.7906 | n/a | n/a |
| funds, one month on random transitions (MAE) | 40.4810 | n/a | 29.9490 | n/a | better |
| mean ratio over scalars, 24 months | 0.4839 | n/a | 0.6218 | n/a | n/a |

Verdicts: better 6, n/a 13

## self-forced final: shares at the engine's bounds, one month (random transitions)

| entry | bounds | model at lower | engine at lower | model at upper | engine at upper | model beyond | engine beyond |
|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 11.85% | 11.25% | n/a | n/a | 0 | 0 |
| res_valve | [-2000, 2000] | 6.75% | 6.90% | 63.85% | 63.90% | 0 | 0 |
| com_valve | [-1500, 1500] | 17.90% | 18.20% | 27.70% | 27.80% | 0 | 0 |
| ind_valve | [-1500, 1500] | 16.55% | 16.60% | 25.70% | 25.65% | 0 | 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0 | 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0 | 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 0 | 0 |
| road_spend | [0, inf] | 11.45% | 11.40% | n/a | n/a | 0 | 0 |
| fire_spend | [0, inf] | 13.40% | 13.40% | n/a | n/a | 0 | 0 |
| police_spend | [0, inf] | 17.70% | 17.75% | n/a | n/a | 0 | 0 |
| powered_zones | [0, inf] | 1.10% | 1.10% | n/a | n/a | 0 | 0 |
| unpowered_zones | [0, inf] | 46.85% | 46.90% | n/a | n/a | 0 | 0 |
| coal_plants | [0, inf] | 39.55% | 39.35% | n/a | n/a | 0 | 0 |
| nuclear_plants | [0, inf] | 23.15% | 23.10% | n/a | n/a | 0 | 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| total_pop | [0, inf] | 0.10% | 0.00% | n/a | n/a | 0 | 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0 | 0 |
| res_hist1 | [0, inf] | 0.10% | 0.05% | n/a | n/a | 0 | 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0 | 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0 | 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| res_cap | [0, 1] | 96.80% | 96.65% | 3.20% | 3.35% | 0 | 0 |
| com_cap | [0, 1] | 99.35% | 99.55% | 0.65% | 0.45% | 0 | 0 |
| ind_cap | [0, 1] | 99.75% | 99.75% | 0.25% | 0.25% | 0 | 0 |
| need_hospital | [-1, 1] | 2.55% | 2.45% | 23.80% | 22.85% | 0 | 0 |
| need_church | [-1, 1] | 1.60% | 1.45% | 38.90% | 37.90% | 0 | 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 0 | 0 |
| police_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 0 | 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 0 | 0 |
| auto_budget | [0, 1] | 12.65% | 12.65% | 87.35% | 87.35% | 0 | 0 |
| fire_pop | [0, inf] | 93.40% | 95.25% | n/a | n/a | 0 | 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| pollution_max_x | [0, 118] | 0.10% | 0.00% | 0.40% | 0.00% | 0 | 0 |
| pollution_max_y | [0, 98] | 0.60% | 0.00% | 0.70% | 0.00% | 0 | 0 |
| flood_count | [0, 30] | 99.60% | 99.65% | 0.00% | 0.00% | 0 | 0 |
| abs_dist | [0, inf] | 65.85% | 63.95% | n/a | n/a | 0 | 0 |
| build_cost | [0, inf] | 77.60% | 78.60% | n/a | n/a | 0 | 0 |

## self-forced final: shares at the engine's bounds, rollouts (months 1..H of the plans)

| entry | bounds | model at lower | engine at lower | model at upper | engine at upper | model beyond | engine beyond |
|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 5.55% | 3.27% | n/a | n/a | 0 | 0 |
| res_valve | [-2000, 2000] | 2.76% | 3.19% | 66.64% | 65.26% | 0 | 0 |
| com_valve | [-1500, 1500] | 22.74% | 14.96% | 27.01% | 28.68% | 0 | 0 |
| ind_valve | [-1500, 1500] | 21.53% | 14.17% | 26.19% | 24.52% | 0 | 0 |
| res_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| com_pop | [0, inf] | 0.01% | 0.00% | n/a | n/a | 0 | 0 |
| ind_pop | [0, inf] | 0.01% | 0.00% | n/a | n/a | 0 | 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| tax_fund | [0, inf] | 26.98% | 26.63% | n/a | n/a | 0 | 0 |
| road_spend | [0, inf] | 26.12% | 25.73% | n/a | n/a | 0 | 0 |
| fire_spend | [0, inf] | 26.50% | 25.96% | n/a | n/a | 0 | 0 |
| police_spend | [0, inf] | 27.50% | 26.40% | n/a | n/a | 0 | 0 |
| powered_zones | [0, inf] | 0.00% | 0.27% | n/a | n/a | 0 | 0 |
| unpowered_zones | [0, inf] | 34.41% | 50.18% | n/a | n/a | 0 | 0 |
| coal_plants | [0, inf] | 40.77% | 39.12% | n/a | n/a | 0 | 0 |
| nuclear_plants | [0, inf] | 24.91% | 23.54% | n/a | n/a | 0 | 0 |
| road_total | [0, inf] | 0.10% | 0.00% | n/a | n/a | 0 | 0 |
| total_pop | [0, inf] | 0.28% | 0.00% | n/a | n/a | 0 | 0 |
| res_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| res_hist1 | [0, inf] | 0.01% | 0.00% | n/a | n/a | 0 | 0 |
| com_hist0 | [0, inf] | 0.07% | 0.00% | n/a | n/a | 0 | 0 |
| com_hist1 | [0, inf] | 0.02% | 0.00% | n/a | n/a | 0 | 0 |
| ind_hist0 | [0, inf] | 0.11% | 0.00% | n/a | n/a | 0 | 0 |
| ind_hist1 | [0, inf] | 0.04% | 0.00% | n/a | n/a | 0 | 0 |
| res_cap | [0, 1] | 97.28% | 96.87% | 2.72% | 3.13% | 0 | 0 |
| com_cap | [0, 1] | 99.28% | 99.58% | 0.72% | 0.42% | 0 | 0 |
| ind_cap | [0, 1] | 99.60% | 100.00% | 0.40% | 0.00% | 0 | 0 |
| need_hospital | [-1, 1] | 6.02% | 1.28% | 35.43% | 24.30% | 0 | 0 |
| need_church | [-1, 1] | 4.96% | 0.94% | 47.60% | 39.90% | 0 | 0 |
| road_fund | [0, inf] | 25.95% | 25.69% | n/a | n/a | 0 | 0 |
| police_fund | [0, inf] | 27.00% | 25.69% | n/a | n/a | 0 | 0 |
| fire_fund | [0, inf] | 26.59% | 25.69% | n/a | n/a | 0 | 0 |
| auto_budget | [0, 1] | 2.89% | 2.82% | 97.11% | 97.18% | 0 | 0 |
| fire_pop | [0, inf] | 39.46% | 97.75% | n/a | n/a | 0 | 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| pollution_max_x | [0, 118] | 0.26% | 0.00% | 0.41% | 0.00% | 0 | 0 |
| pollution_max_y | [0, 98] | 0.68% | 0.00% | 1.27% | 0.00% | 0 | 0 |
| flood_count | [0, 30] | 99.19% | 99.64% | 0.02% | 0.00% | 0 | 0 |
| abs_dist | [0, inf] | 68.64% | 67.43% | n/a | n/a | 0 | 0 |
| build_cost | [0, inf] | 61.90% | 67.62% | n/a | n/a | 0 | 0 |
