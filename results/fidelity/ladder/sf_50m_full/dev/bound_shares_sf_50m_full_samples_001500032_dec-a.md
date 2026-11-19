# Shares at the engine's bounds: sf_50m_full_samples_001500032_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 11.85% | 11.25% | n/a | n/a | 5.55% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.75% | 6.90% | 63.85% | 63.90% | 2.76% | 3.19% | 66.64% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 17.90% | 18.20% | 27.70% | 27.80% | 22.74% | 14.96% | 27.01% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.55% | 16.60% | 25.70% | 25.65% | 21.53% | 14.17% | 26.19% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.98% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.45% | 11.40% | n/a | n/a | 26.12% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.40% | 13.40% | n/a | n/a | 26.50% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.70% | 17.75% | n/a | n/a | 27.50% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.10% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 46.85% | 46.90% | n/a | n/a | 34.41% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.55% | 39.35% | n/a | n/a | 40.77% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.15% | 23.10% | n/a | n/a | 24.91% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.10% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.10% | 0.00% | n/a | n/a | 0.28% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.10% | 0.05% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.07% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.11% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.04% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.80% | 96.65% | 3.20% | 3.35% | 97.28% | 96.87% | 2.72% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.35% | 99.55% | 0.65% | 0.45% | 99.28% | 99.58% | 0.72% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.75% | 99.75% | 0.25% | 0.25% | 99.60% | 100.00% | 0.40% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 2.55% | 2.45% | 23.80% | 22.85% | 6.02% | 1.28% | 35.43% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 1.60% | 1.45% | 38.90% | 37.90% | 4.96% | 0.94% | 47.60% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.95% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 27.00% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 26.59% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.65% | 12.65% | 87.35% | 87.35% | 2.89% | 2.82% | 97.11% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 93.40% | 95.25% | n/a | n/a | 39.46% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.10% | 0.00% | 0.40% | 0.00% | 0.26% | 0.00% | 0.41% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.60% | 0.00% | 0.70% | 0.00% | 0.68% | 0.00% | 1.27% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.60% | 99.65% | 0.00% | 0.00% | 99.19% | 99.64% | 0.02% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 65.85% | 63.95% | n/a | n/a | 68.64% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 77.60% | 78.60% | n/a | n/a | 61.90% | 67.62% | n/a | n/a | 0 / 0 |
