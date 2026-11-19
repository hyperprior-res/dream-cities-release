# Shares at the engine's bounds: os_50m_full_samples_001200000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 12.55% | 11.25% | n/a | n/a | 7.24% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.80% | 6.90% | 64.00% | 63.90% | 2.84% | 3.19% | 68.27% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 17.75% | 18.20% | 27.85% | 27.80% | 18.87% | 14.96% | 29.85% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.50% | 16.60% | 25.80% | 25.65% | 19.05% | 14.17% | 27.39% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.81% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.40% | 11.40% | n/a | n/a | 25.96% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.45% | 13.40% | n/a | n/a | 27.01% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.60% | 17.75% | n/a | n/a | 27.31% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 48.55% | 46.90% | n/a | n/a | 57.86% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.65% | 39.35% | n/a | n/a | 47.05% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.45% | 23.10% | n/a | n/a | 30.87% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.12% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.20% | 0.00% | n/a | n/a | 0.38% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.10% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.75% | 96.65% | 3.25% | 3.35% | 98.22% | 96.87% | 1.78% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.40% | 99.55% | 0.60% | 0.45% | 99.49% | 99.58% | 0.51% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.80% | 99.75% | 0.20% | 0.25% | 99.99% | 100.00% | 0.01% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 3.50% | 2.45% | 24.20% | 22.85% | 9.43% | 1.28% | 33.59% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 2.80% | 1.45% | 38.30% | 37.90% | 7.47% | 0.94% | 43.21% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.73% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 25.78% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 26.12% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.70% | 12.65% | 87.30% | 87.35% | 3.68% | 2.82% | 96.32% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 94.05% | 95.25% | n/a | n/a | 88.39% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.10% | 0.00% | 0.60% | 0.00% | 0.85% | 0.00% | 1.13% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.55% | 0.00% | 1.00% | 0.00% | 0.81% | 0.00% | 1.66% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.65% | 99.65% | 0.00% | 0.00% | 99.41% | 99.64% | 0.00% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 65.40% | 63.95% | n/a | n/a | 69.08% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 83.20% | 78.60% | n/a | n/a | 75.10% | 67.62% | n/a | n/a | 0 / 0 |
