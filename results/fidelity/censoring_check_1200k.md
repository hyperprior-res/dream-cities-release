# Check: ladder-v2 at 1.2M against ladder-v1 at 1.2M

Selection dev (2000 transitions, 500 plans, key 3eed58d3b821a96c); ladder-v1 at 1.2M: <cache>/ckpt/v1_provisional_os_50m_full/samples_001200000.pt (1,200,000 samples, decoding a, weights ema); ladder-v2 at 1.2M: <cache>/ckpt/ladder_v2/os_50m_full/samples_001200000.pt (1,200,000 samples, decoding a, weights ema). One model sample at T=1 in every row.

| metric | ladder-v1 at 1.2M | ladder-v1 at 1.2M, other noise seed | ladder-v2 at 1.2M | evaluation noise | verdict |
|---|---|---|---|---|---|
| tile structural F1, one month | 0.1677 | n/a | 0.1689 | n/a | better |
| tile structural F1 since start, 12 months | 0.3730 | n/a | 0.3712 | n/a | n/a |
| tile structural F1 since start, 24 months | 0.3446 | n/a | 0.3444 | n/a | n/a |
| funds median rel. error, 12 months | 0.0666 | n/a | 0.0635 | n/a | better |
| funds median rel. error, 24 months | 0.0801 | n/a | 0.0824 | n/a | n/a |
| population median rel. error, 12 months | 0.0379 | n/a | 0.0409 | n/a | n/a |
| population median rel. error, 24 months | 0.0626 | n/a | 0.0630 | n/a | n/a |
| res_valve, one month from start (x copy) | 0.2155 | n/a | 0.1601 | n/a | better |
| com_valve, one month from start (x copy) | 0.1728 | n/a | 0.1400 | n/a | better |
| ind_valve, one month from start (x copy) | 0.1329 | n/a | 0.0921 | n/a | better |
| score, one month from start (x copy) | 0.2237 | n/a | 0.2513 | n/a | n/a |
| res_valve, 12 months (x copy) | 0.3342 | n/a | 0.3445 | n/a | n/a |
| com_valve, 12 months (x copy) | 0.4108 | n/a | 0.4341 | n/a | n/a |
| ind_valve, 12 months (x copy) | 0.3671 | n/a | 0.3659 | n/a | better |
| res_valve, 24 months (x copy) | 0.3488 | n/a | 0.3900 | n/a | n/a |
| com_valve, 24 months (x copy) | 0.5861 | n/a | 0.5973 | n/a | n/a |
| ind_valve, 24 months (x copy) | 0.7033 | n/a | 0.7201 | n/a | n/a |
| funds, one month on random transitions (MAE) | 80.1945 | n/a | 76.9120 | n/a | better |
| mean ratio over scalars, 24 months | 0.5966 | n/a | 0.6124 | n/a | n/a |

Verdicts: better 7, n/a 12

## ladder-v2 at 1.2M: shares at the engine's bounds, one month (random transitions)

| entry | bounds | model at lower | engine at lower | model at upper | engine at upper | model beyond | engine beyond |
|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 12.55% | 11.25% | n/a | n/a | 0 | 0 |
| res_valve | [-2000, 2000] | 6.80% | 6.90% | 64.00% | 63.90% | 0 | 0 |
| com_valve | [-1500, 1500] | 17.75% | 18.20% | 27.85% | 27.80% | 0 | 0 |
| ind_valve | [-1500, 1500] | 16.50% | 16.60% | 25.80% | 25.65% | 0 | 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0 | 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0 | 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 0 | 0 |
| road_spend | [0, inf] | 11.40% | 11.40% | n/a | n/a | 0 | 0 |
| fire_spend | [0, inf] | 13.45% | 13.40% | n/a | n/a | 0 | 0 |
| police_spend | [0, inf] | 17.60% | 17.75% | n/a | n/a | 0 | 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0 | 0 |
| unpowered_zones | [0, inf] | 48.55% | 46.90% | n/a | n/a | 0 | 0 |
| coal_plants | [0, inf] | 39.65% | 39.35% | n/a | n/a | 0 | 0 |
| nuclear_plants | [0, inf] | 23.45% | 23.10% | n/a | n/a | 0 | 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| total_pop | [0, inf] | 0.20% | 0.00% | n/a | n/a | 0 | 0 |
| res_hist0 | [0, inf] | 0.10% | 0.05% | n/a | n/a | 0 | 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0 | 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0 | 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0 | 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| res_cap | [0, 1] | 96.75% | 96.65% | 3.25% | 3.35% | 0 | 0 |
| com_cap | [0, 1] | 99.40% | 99.55% | 0.60% | 0.45% | 0 | 0 |
| ind_cap | [0, 1] | 99.80% | 99.75% | 0.20% | 0.25% | 0 | 0 |
| need_hospital | [-1, 1] | 3.55% | 2.45% | 24.20% | 22.85% | 0 | 0 |
| need_church | [-1, 1] | 2.80% | 1.45% | 38.30% | 37.90% | 0 | 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 0 | 0 |
| police_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 0 | 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 0 | 0 |
| auto_budget | [0, 1] | 12.70% | 12.65% | 87.30% | 87.35% | 0 | 0 |
| fire_pop | [0, inf] | 94.10% | 95.25% | n/a | n/a | 0 | 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| pollution_max_x | [0, 118] | 0.10% | 0.00% | 0.60% | 0.00% | 0 | 0 |
| pollution_max_y | [0, 98] | 0.55% | 0.00% | 1.00% | 0.00% | 0 | 0 |
| flood_count | [0, 30] | 99.65% | 99.65% | 0.00% | 0.00% | 0 | 0 |
| abs_dist | [0, inf] | 65.40% | 63.95% | n/a | n/a | 0 | 0 |
| build_cost | [0, inf] | 83.15% | 78.60% | n/a | n/a | 0 | 0 |

## ladder-v2 at 1.2M: shares at the engine's bounds, rollouts (months 1..H of the plans)

| entry | bounds | model at lower | engine at lower | model at upper | engine at upper | model beyond | engine beyond |
|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 7.29% | 3.27% | n/a | n/a | 0 | 0 |
| res_valve | [-2000, 2000] | 2.84% | 3.19% | 68.19% | 65.26% | 0 | 0 |
| com_valve | [-1500, 1500] | 18.66% | 14.96% | 29.85% | 28.68% | 0 | 0 |
| ind_valve | [-1500, 1500] | 18.97% | 14.17% | 27.28% | 24.52% | 0 | 0 |
| res_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| com_pop | [0, inf] | 0.01% | 0.00% | n/a | n/a | 0 | 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| tax_fund | [0, inf] | 26.85% | 26.63% | n/a | n/a | 0 | 0 |
| road_spend | [0, inf] | 26.00% | 25.73% | n/a | n/a | 0 | 0 |
| fire_spend | [0, inf] | 27.01% | 25.96% | n/a | n/a | 0 | 0 |
| police_spend | [0, inf] | 27.37% | 26.40% | n/a | n/a | 0 | 0 |
| powered_zones | [0, inf] | 0.00% | 0.27% | n/a | n/a | 0 | 0 |
| unpowered_zones | [0, inf] | 57.81% | 50.18% | n/a | n/a | 0 | 0 |
| coal_plants | [0, inf] | 47.22% | 39.12% | n/a | n/a | 0 | 0 |
| nuclear_plants | [0, inf] | 31.01% | 23.54% | n/a | n/a | 0 | 0 |
| road_total | [0, inf] | 0.14% | 0.00% | n/a | n/a | 0 | 0 |
| total_pop | [0, inf] | 0.40% | 0.00% | n/a | n/a | 0 | 0 |
| res_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| res_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| com_hist0 | [0, inf] | 0.01% | 0.00% | n/a | n/a | 0 | 0 |
| com_hist1 | [0, inf] | 0.01% | 0.00% | n/a | n/a | 0 | 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| res_cap | [0, 1] | 98.19% | 96.87% | 1.81% | 3.13% | 0 | 0 |
| com_cap | [0, 1] | 99.50% | 99.58% | 0.50% | 0.42% | 0 | 0 |
| ind_cap | [0, 1] | 100.00% | 100.00% | 0.00% | 0.00% | 0 | 0 |
| need_hospital | [-1, 1] | 9.52% | 1.28% | 33.81% | 24.30% | 0 | 0 |
| need_church | [-1, 1] | 7.36% | 0.94% | 43.14% | 39.90% | 0 | 0 |
| road_fund | [0, inf] | 25.76% | 25.69% | n/a | n/a | 0 | 0 |
| police_fund | [0, inf] | 25.84% | 25.69% | n/a | n/a | 0 | 0 |
| fire_fund | [0, inf] | 26.12% | 25.69% | n/a | n/a | 0 | 0 |
| auto_budget | [0, 1] | 3.66% | 2.82% | 96.34% | 97.18% | 0 | 0 |
| fire_pop | [0, inf] | 87.91% | 97.75% | n/a | n/a | 0 | 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| pollution_max_x | [0, 118] | 0.87% | 0.00% | 1.15% | 0.00% | 0 | 0 |
| pollution_max_y | [0, 98] | 0.82% | 0.00% | 1.68% | 0.00% | 0 | 0 |
| flood_count | [0, 30] | 99.38% | 99.64% | 0.01% | 0.00% | 0 | 0 |
| abs_dist | [0, inf] | 69.04% | 67.43% | n/a | n/a | 0 | 0 |
| build_cost | [0, inf] | 75.16% | 67.62% | n/a | n/a | 0 | 0 |
