# Shares at the engine's bounds: os_50m_full_samples_003600000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 12.20% | 11.25% | n/a | n/a | 5.75% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.80% | 6.90% | 64.15% | 63.90% | 2.67% | 3.19% | 67.89% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 17.95% | 18.20% | 27.95% | 27.80% | 19.90% | 14.96% | 26.84% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.60% | 16.60% | 25.80% | 25.65% | 20.36% | 14.17% | 26.12% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.64% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.40% | 11.40% | n/a | n/a | 25.76% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.35% | 13.40% | n/a | n/a | 26.28% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.70% | 17.75% | n/a | n/a | 26.88% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 47.85% | 46.90% | n/a | n/a | 53.13% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.60% | 39.35% | n/a | n/a | 43.89% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.20% | 23.10% | n/a | n/a | 27.22% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.08% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.15% | 0.00% | n/a | n/a | 0.31% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.85% | 96.65% | 3.15% | 3.35% | 97.55% | 96.87% | 2.45% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.30% | 99.55% | 0.70% | 0.45% | 99.19% | 99.58% | 0.81% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.80% | 99.75% | 0.20% | 0.25% | 99.93% | 100.00% | 0.07% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 3.10% | 2.45% | 22.45% | 22.85% | 6.14% | 1.28% | 27.84% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 1.55% | 1.45% | 38.05% | 37.90% | 3.50% | 0.94% | 44.12% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.67% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 26.02% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.80% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.65% | 12.65% | 87.35% | 87.35% | 3.03% | 2.82% | 96.97% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 92.95% | 95.25% | n/a | n/a | 70.39% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.25% | 0.00% | 0.45% | 0.00% | 0.61% | 0.00% | 0.52% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 1.05% | 0.00% | 1.90% | 0.00% | 0.84% | 0.00% | 1.33% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.65% | 99.65% | 0.00% | 0.00% | 99.46% | 99.64% | 0.01% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 65.55% | 63.95% | n/a | n/a | 68.62% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 81.85% | 78.60% | n/a | n/a | 71.44% | 67.62% | n/a | n/a | 0 / 0 |
