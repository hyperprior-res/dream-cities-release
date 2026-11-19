# Shares at the engine's bounds: os_50m_cov_samples_001200000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 12.70% | 11.25% | n/a | n/a | 15.16% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.80% | 6.90% | 63.95% | 63.90% | 2.90% | 3.19% | 68.31% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 18.00% | 18.20% | 28.10% | 27.80% | 18.29% | 14.96% | 28.47% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.75% | 16.60% | 25.60% | 25.65% | 16.46% | 14.17% | 25.66% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.90% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.50% | 11.40% | n/a | n/a | 25.94% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.45% | 13.40% | n/a | n/a | 27.07% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.70% | 17.75% | n/a | n/a | 30.48% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 48.50% | 46.90% | n/a | n/a | 58.76% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.70% | 39.35% | n/a | n/a | 45.51% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.10% | 23.10% | n/a | n/a | 28.60% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.10% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.25% | 0.00% | n/a | n/a | 0.34% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.85% | 96.65% | 3.15% | 3.35% | 98.78% | 96.87% | 1.22% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.40% | 99.55% | 0.60% | 0.45% | 99.34% | 99.58% | 0.66% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.80% | 99.75% | 0.20% | 0.25% | 99.79% | 100.00% | 0.21% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 3.30% | 2.45% | 23.40% | 22.85% | 8.08% | 1.28% | 34.71% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 2.10% | 1.45% | 37.75% | 37.90% | 6.61% | 0.94% | 42.69% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.73% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 26.29% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 25.73% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.70% | 12.65% | 87.30% | 87.35% | 7.83% | 2.82% | 92.17% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 94.60% | 95.25% | n/a | n/a | 89.24% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.40% | 0.00% | 0.90% | 0.00% | 0.87% | 0.00% | 1.56% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.95% | 0.00% | 1.75% | 0.00% | 0.79% | 0.00% | 1.28% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.55% | 99.65% | 0.05% | 0.00% | 99.41% | 99.64% | 0.01% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 64.90% | 63.95% | n/a | n/a | 68.13% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 85.90% | 78.60% | n/a | n/a | 80.28% | 67.62% | n/a | n/a | 0 / 0 |
