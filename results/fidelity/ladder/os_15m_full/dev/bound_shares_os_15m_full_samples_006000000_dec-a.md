# Shares at the engine's bounds: os_15m_full_samples_006000000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 12.10% | 11.25% | n/a | n/a | 6.26% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.85% | 6.90% | 64.15% | 63.90% | 2.93% | 3.19% | 68.46% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 18.05% | 18.20% | 28.15% | 27.80% | 21.73% | 14.96% | 29.44% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.60% | 16.60% | 25.75% | 25.65% | 21.72% | 14.17% | 26.07% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.43% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.45% | 11.40% | n/a | n/a | 25.82% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.55% | 13.40% | n/a | n/a | 27.84% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.65% | 17.75% | n/a | n/a | 28.58% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 46.80% | 46.90% | n/a | n/a | 45.99% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.35% | 39.35% | n/a | n/a | 42.18% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.20% | 23.10% | n/a | n/a | 25.46% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.10% | 0.00% | n/a | n/a | 0.25% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.75% | 96.65% | 3.25% | 3.35% | 96.03% | 96.87% | 3.97% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.35% | 99.55% | 0.65% | 0.45% | 99.71% | 99.58% | 0.29% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.85% | 99.75% | 0.15% | 0.25% | 99.97% | 100.00% | 0.03% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 3.30% | 2.45% | 23.10% | 22.85% | 5.73% | 1.28% | 30.30% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 1.55% | 1.45% | 38.25% | 37.90% | 3.52% | 0.94% | 42.34% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.65% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.87% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.75% | 10.65% | n/a | n/a | 27.21% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.65% | 12.65% | 87.35% | 87.35% | 3.23% | 2.82% | 96.77% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 93.45% | 95.25% | n/a | n/a | 73.84% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.10% | 0.00% | 0.10% | 0.00% | 0.19% | 0.00% | 0.30% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.85% | 0.00% | 0.35% | 0.00% | 0.51% | 0.00% | 0.47% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.65% | 99.65% | 0.00% | 0.00% | 99.42% | 99.64% | 0.00% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 65.40% | 63.95% | n/a | n/a | 69.04% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 77.80% | 78.60% | n/a | n/a | 64.00% | 67.62% | n/a | n/a | 0 / 0 |
