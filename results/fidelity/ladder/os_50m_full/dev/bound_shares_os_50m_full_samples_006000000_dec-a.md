# Shares at the engine's bounds: os_50m_full_samples_006000000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 11.95% | 11.25% | n/a | n/a | 5.19% | 3.27% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.80% | 6.90% | 64.30% | 63.90% | 2.92% | 3.19% | 66.33% | 65.26% | 0 / 0 |
| com_valve | [-1500, 1500] | 17.85% | 18.20% | 27.85% | 27.80% | 18.67% | 14.96% | 29.11% | 28.68% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.60% | 16.60% | 25.70% | 25.65% | 19.90% | 14.17% | 28.16% | 24.52% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 26.59% | 26.63% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.35% | 11.40% | n/a | n/a | 25.64% | 25.73% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 13.40% | 13.40% | n/a | n/a | 26.37% | 25.96% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 17.60% | 17.75% | n/a | n/a | 26.95% | 26.40% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0.00% | 0.27% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 47.10% | 46.90% | n/a | n/a | 43.36% | 50.18% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 39.40% | 39.35% | n/a | n/a | 41.92% | 39.12% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 23.15% | 23.10% | n/a | n/a | 24.65% | 23.54% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.10% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.10% | 0.00% | n/a | n/a | 0.28% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0.09% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.12% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.80% | 96.65% | 3.20% | 3.35% | 97.26% | 96.87% | 2.74% | 3.13% | 0 / 0 |
| com_cap | [0, 1] | 99.35% | 99.55% | 0.65% | 0.45% | 99.16% | 99.58% | 0.84% | 0.42% | 0 / 0 |
| ind_cap | [0, 1] | 99.80% | 99.75% | 0.20% | 0.25% | 99.68% | 100.00% | 0.32% | 0.00% | 0 / 0 |
| need_hospital | [-1, 1] | 2.70% | 2.45% | 22.75% | 22.85% | 5.24% | 1.28% | 28.10% | 24.30% | 0 / 0 |
| need_church | [-1, 1] | 1.65% | 1.45% | 39.05% | 37.90% | 2.77% | 0.94% | 46.13% | 39.90% | 0 / 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 25.57% | 25.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.70% | 10.65% | n/a | n/a | 26.62% | 25.69% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 26.03% | 25.69% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.65% | 12.65% | 87.35% | 87.35% | 3.04% | 2.82% | 96.96% | 97.18% | 0 / 0 |
| fire_pop | [0, inf] | 91.30% | 95.25% | n/a | n/a | 52.92% | 97.75% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.20% | 0.00% | 0.70% | 0.00% | 0.56% | 0.00% | 0.59% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.65% | 0.00% | 1.85% | 0.00% | 0.81% | 0.00% | 1.60% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.60% | 99.65% | 0.00% | 0.00% | 99.37% | 99.64% | 0.01% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 65.15% | 63.95% | n/a | n/a | 68.55% | 67.43% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 78.75% | 78.60% | n/a | n/a | 67.50% | 67.62% | n/a | n/a | 0 / 0 |
