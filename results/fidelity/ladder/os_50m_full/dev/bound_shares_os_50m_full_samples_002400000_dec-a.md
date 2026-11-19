# Shares at the engine's bounds: os_50m_full_samples_002400000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 12.40% | 11.25% | n/a | n/a | 6.52% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.85% | 6.90% | 64.10% | 63.90% | 2.76% | 3.19% | 67.64% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 17.95% | 18.20% | 27.85% | 27.80% | 20.36% | 14.96% | 26.59% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.50% | 16.60% | 25.70% | 25.65% | 20.77% | 14.17% | 25.83% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.64% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.40% | 11.40% | n/a | n/a | 25.82% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.45% | 13.40% | n/a | n/a | 26.32% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.75% | 17.75% | n/a | n/a | 27.09% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 48.80% | 46.90% | n/a | n/a | 56.58% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.65% | 39.35% | n/a | n/a | 45.27% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.25% | 23.10% | n/a | n/a | 28.81% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.11% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.10% | 0.00% | n/a | n/a | 0.34% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.80% | 96.65% | 3.20% | 3.35% | 97.74% | 96.87% | 2.26% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.15% | 99.55% | 0.85% | 0.45% | 99.14% | 99.58% | 0.86% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.80% | 99.75% | 0.20% | 0.25% | 99.94% | 100.00% | 0.06% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 3.10% | 2.45% | 22.70% | 22.85% | 6.41% | 1.28% | 27.69% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 2.10% | 1.45% | 38.90% | 37.90% | 3.60% | 0.94% | 43.27% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.73% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 25.77% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.79% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.60% | 12.65% | 87.40% | 87.35% | 3.44% | 2.82% | 96.56% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 93.50% | 95.25% | n/a | n/a | 82.93% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.05% | 0.00% | 0.40% | 0.00% | 0.96% | 0.00% | 0.68% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.80% | 0.00% | 1.10% | 0.00% | 0.72% | 0.00% | 1.23% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.65% | 99.65% | 0.00% | 0.00% | 99.44% | 99.64% | 0.01% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 65.55% | 63.95% | n/a | n/a | 69.01% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 83.45% | 78.60% | n/a | n/a | 73.92% | 67.62% | n/a | n/a | 0 / 0 |
