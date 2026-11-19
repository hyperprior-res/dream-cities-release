# Shares at the engine's bounds: os_50m_full_s1_samples_006000000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 11.45% | 10.75% | n/a | n/a | 7.20% | 4.23% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 5.75% | 5.70% | 62.80% | 62.50% | 4.02% | 3.92% | 62.15% | 62.50% | 0 / 0 |
| com_valve | [-1500, 1500] | 19.00% | 19.00% | 23.30% | 23.00% | 17.57% | 15.02% | 25.99% | 26.35% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.85% | 16.95% | 27.00% | 26.95% | 15.74% | 13.93% | 32.62% | 30.93% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.15% | 0.25% | n/a | n/a | 0.11% | 0.08% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.03% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 14.75% | 14.75% | n/a | n/a | 27.70% | 28.05% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 13.60% | 13.60% | n/a | n/a | 26.70% | 26.70% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 25.55% | 25.60% | n/a | n/a | 34.01% | 34.74% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 23.05% | 23.15% | n/a | n/a | 30.38% | 30.43% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 0.80% | 0.85% | n/a | n/a | 0.00% | 0.30% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 48.80% | 48.55% | n/a | n/a | 47.31% | 50.06% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 25.20% | 25.15% | n/a | n/a | 26.12% | 24.66% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 33.45% | 33.40% | n/a | n/a | 37.90% | 36.51% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.22% | 0.20% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.20% | 0.00% | n/a | n/a | 0.11% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.15% | 0.25% | n/a | n/a | 0.12% | 0.08% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.15% | 0.15% | n/a | n/a | 0.14% | 0.09% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 97.95% | 98.15% | 2.05% | 1.85% | 99.00% | 99.21% | 1.00% | 0.79% | 0 / 0 |
| com_cap | [0, 1] | 98.95% | 98.90% | 1.05% | 1.10% | 98.95% | 99.22% | 1.05% | 0.78% | 0 / 0 |
| ind_cap | [0, 1] | 99.25% | 99.25% | 0.75% | 0.75% | 99.48% | 99.67% | 0.52% | 0.33% | 0 / 0 |
| need_hospital | [-1, 1] | 3.35% | 3.05% | 21.20% | 22.10% | 9.24% | 2.50% | 25.78% | 23.35% | 0 / 0 |
| need_church | [-1, 1] | 2.85% | 2.00% | 31.95% | 32.20% | 9.02% | 2.10% | 36.26% | 33.34% | 0 / 0 |
| road_fund | [0, inf] | 13.45% | 13.45% | n/a | n/a | 26.58% | 26.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 16.00% | 16.00% | n/a | n/a | 28.20% | 28.39% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 21.90% | 21.90% | n/a | n/a | 33.99% | 34.04% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 11.05% | 11.25% | 88.95% | 88.75% | 4.25% | 4.23% | 95.75% | 95.78% | 0 / 0 |
| fire_pop | [0, inf] | 91.75% | 93.40% | n/a | n/a | 76.64% | 94.92% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.30% | 0.00% | 0.55% | 0.00% | 1.19% | 0.00% | 1.31% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.25% | 0.00% | 0.10% | 0.00% | 0.51% | 0.00% | 0.50% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.55% | 99.55% | 0.00% | 0.00% | 99.40% | 99.47% | 0.04% | 0.03% | 0 / 0 |
| abs_dist | [0, inf] | 67.55% | 66.45% | n/a | n/a | 69.34% | 66.10% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 76.05% | 76.60% | n/a | n/a | 67.96% | 69.33% | n/a | n/a | 0 / 0 |
