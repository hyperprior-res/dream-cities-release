# Shares at the engine's bounds: os_100m_full_samples_006000000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 12.05% | 11.25% | n/a | n/a | 4.74% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.85% | 6.90% | 64.15% | 63.90% | 3.02% | 3.19% | 66.19% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 18.15% | 18.20% | 28.00% | 27.80% | 18.12% | 14.96% | 29.77% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.55% | 16.60% | 25.60% | 25.65% | 16.81% | 14.17% | 28.42% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.15% | 0.10% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.60% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.40% | 11.40% | n/a | n/a | 25.89% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.45% | 13.40% | n/a | n/a | 26.32% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.70% | 17.75% | n/a | n/a | 26.84% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 0.95% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 46.85% | 46.90% | n/a | n/a | 41.04% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.35% | 39.35% | n/a | n/a | 41.62% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.25% | 23.10% | n/a | n/a | 24.94% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.04% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.15% | 0.00% | n/a | n/a | 0.24% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.15% | 0.10% | n/a | n/a | 0.04% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.03% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.80% | 96.65% | 3.20% | 3.35% | 97.52% | 96.87% | 2.48% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.40% | 99.55% | 0.60% | 0.45% | 99.39% | 99.58% | 0.61% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.75% | 99.75% | 0.25% | 0.25% | 99.86% | 100.00% | 0.14% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 2.60% | 2.45% | 22.15% | 22.85% | 6.13% | 1.28% | 25.04% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 1.40% | 1.45% | 37.60% | 37.90% | 2.91% | 0.94% | 41.48% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 25.84% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 26.01% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 26.10% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.70% | 12.65% | 87.30% | 87.35% | 2.74% | 2.82% | 97.26% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 88.35% | 95.25% | n/a | n/a | 47.66% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.20% | 0.00% | 0.10% | 0.00% | 0.55% | 0.00% | 0.47% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 1.05% | 0.00% | 1.10% | 0.00% | 1.45% | 0.00% | 1.95% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.65% | 99.65% | 0.00% | 0.00% | 99.06% | 99.64% | 0.12% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 64.75% | 63.95% | n/a | n/a | 69.15% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 79.20% | 78.60% | n/a | n/a | 68.49% | 67.62% | n/a | n/a | 0 / 0 |
