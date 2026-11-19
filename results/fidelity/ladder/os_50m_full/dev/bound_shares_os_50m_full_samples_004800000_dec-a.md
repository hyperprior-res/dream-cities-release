# Shares at the engine's bounds: os_50m_full_samples_004800000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 11.85% | 11.25% | n/a | n/a | 5.28% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.80% | 6.90% | 64.20% | 63.90% | 2.97% | 3.19% | 66.24% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 17.95% | 18.20% | 27.85% | 27.80% | 18.86% | 14.96% | 28.47% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.50% | 16.60% | 25.80% | 25.65% | 19.67% | 14.17% | 27.61% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.62% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.45% | 11.40% | n/a | n/a | 25.78% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.40% | 13.40% | n/a | n/a | 26.13% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.70% | 17.75% | n/a | n/a | 26.98% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 47.45% | 46.90% | n/a | n/a | 49.45% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.45% | 39.35% | n/a | n/a | 42.09% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.20% | 23.10% | n/a | n/a | 25.48% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.05% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.10% | 0.00% | n/a | n/a | 0.26% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.80% | 96.65% | 3.20% | 3.35% | 97.56% | 96.87% | 2.44% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.25% | 99.55% | 0.75% | 0.45% | 99.46% | 99.58% | 0.54% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.80% | 99.75% | 0.20% | 0.25% | 99.79% | 100.00% | 0.21% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 2.80% | 2.45% | 23.00% | 22.85% | 5.30% | 1.28% | 28.86% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 1.80% | 1.45% | 38.60% | 37.90% | 2.48% | 0.94% | 45.69% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.55% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 26.18% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.87% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.65% | 12.65% | 87.35% | 87.35% | 3.05% | 2.82% | 96.95% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 91.80% | 95.25% | n/a | n/a | 62.43% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.25% | 0.00% | 0.50% | 0.00% | 0.51% | 0.00% | 0.62% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.70% | 0.00% | 2.30% | 0.00% | 0.74% | 0.00% | 1.31% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.65% | 99.65% | 0.00% | 0.00% | 99.40% | 99.64% | 0.01% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 65.45% | 63.95% | n/a | n/a | 68.35% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 80.05% | 78.60% | n/a | n/a | 68.61% | 67.62% | n/a | n/a | 0 / 0 |
