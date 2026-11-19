# Shares at the engine's bounds: os_50m_full_36m_samples_030000000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 11.80% | 11.25% | n/a | n/a | 5.78% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.95% | 6.90% | 64.40% | 63.90% | 3.64% | 3.19% | 61.66% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 18.30% | 18.20% | 28.05% | 27.80% | 18.50% | 14.96% | 33.24% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.60% | 16.60% | 25.70% | 25.65% | 16.27% | 14.17% | 31.35% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.06% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.11% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.39% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.30% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.59% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.35% | 11.40% | n/a | n/a | 25.40% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.40% | 13.40% | n/a | n/a | 26.80% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.70% | 17.75% | n/a | n/a | 28.50% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 46.95% | 46.90% | n/a | n/a | 43.32% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.45% | 39.35% | n/a | n/a | 44.51% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.20% | 23.10% | n/a | n/a | 26.59% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.05% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.18% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.13% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.06% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.17% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.19% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.49% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.44% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.80% | 96.65% | 3.20% | 3.35% | 97.54% | 96.87% | 2.46% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.40% | 99.55% | 0.60% | 0.45% | 99.30% | 99.58% | 0.70% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.80% | 99.75% | 0.20% | 0.25% | 98.59% | 100.00% | 1.41% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 3.00% | 2.45% | 22.45% | 22.85% | 8.85% | 1.28% | 21.79% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 1.40% | 1.45% | 38.05% | 37.90% | 3.83% | 0.94% | 38.07% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.60% | 10.65% | n/a | n/a | 25.61% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.75% | 10.65% | n/a | n/a | 27.06% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 27.27% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.70% | 12.65% | 87.30% | 87.35% | 3.49% | 2.82% | 96.51% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 91.35% | 95.25% | n/a | n/a | 50.79% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.01% | 0.00% | 0.01% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.01% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.25% | 0.00% | 0.30% | 0.00% | 0.55% | 0.00% | 0.78% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.70% | 0.00% | 1.05% | 0.00% | 1.06% | 0.00% | 1.08% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.60% | 99.65% | 0.00% | 0.00% | 98.51% | 99.64% | 0.23% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 65.40% | 63.95% | n/a | n/a | 69.64% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 80.85% | 78.60% | n/a | n/a | 72.34% | 67.62% | n/a | n/a | 0 / 0 |
