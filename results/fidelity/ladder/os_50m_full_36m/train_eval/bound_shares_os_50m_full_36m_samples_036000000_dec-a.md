# Shares at the engine's bounds: os_50m_full_36m_samples_036000000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 11.25% | 10.75% | n/a | n/a | 7.12% | 4.23% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 5.80% | 5.70% | 62.75% | 62.50% | 4.62% | 3.92% | 57.48% | 62.50% | 0 / 0 |
| com_valve | [-1500, 1500] | 19.10% | 19.00% | 23.35% | 23.00% | 16.12% | 15.02% | 32.16% | 26.35% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.85% | 16.95% | 26.95% | 26.95% | 13.20% | 13.93% | 37.72% | 30.93% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.17% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.15% | 0.25% | n/a | n/a | 0.63% | 0.08% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.76% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.13% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 14.75% | 14.75% | n/a | n/a | 27.30% | 28.05% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 13.60% | 13.60% | n/a | n/a | 26.63% | 26.70% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 25.60% | 25.60% | n/a | n/a | 35.22% | 34.74% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 23.10% | 23.15% | n/a | n/a | 31.10% | 30.43% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 0.80% | 0.85% | n/a | n/a | 0.00% | 0.30% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 48.50% | 48.55% | n/a | n/a | 42.63% | 50.06% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 25.20% | 25.15% | n/a | n/a | 27.70% | 24.66% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 33.50% | 33.40% | n/a | n/a | 39.48% | 36.51% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.16% | 0.20% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.05% | 0.00% | n/a | n/a | 0.25% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.35% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.22% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.20% | 0.25% | n/a | n/a | 0.74% | 0.08% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.15% | 0.15% | n/a | n/a | 0.71% | 0.09% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.95% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.80% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 98.10% | 98.15% | 1.90% | 1.85% | 97.76% | 99.21% | 2.24% | 0.79% | 0 / 0 |
| com_cap | [0, 1] | 98.85% | 98.90% | 1.15% | 1.10% | 99.17% | 99.22% | 0.83% | 0.78% | 0 / 0 |
| ind_cap | [0, 1] | 99.15% | 99.25% | 0.85% | 0.75% | 98.82% | 99.67% | 1.18% | 0.33% | 0 / 0 |
| need_hospital | [-1, 1] | 4.10% | 3.05% | 21.55% | 22.10% | 17.70% | 2.50% | 18.78% | 23.35% | 0 / 0 |
| need_church | [-1, 1] | 3.10% | 2.00% | 31.00% | 32.20% | 12.94% | 2.10% | 29.34% | 33.34% | 0 / 0 |
| road_fund | [0, inf] | 13.45% | 13.45% | n/a | n/a | 26.61% | 26.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 16.00% | 16.00% | n/a | n/a | 28.42% | 28.39% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 21.90% | 21.90% | n/a | n/a | 34.57% | 34.04% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 11.20% | 11.25% | 88.80% | 88.75% | 4.76% | 4.23% | 95.24% | 95.78% | 0 / 0 |
| fire_pop | [0, inf] | 89.40% | 93.40% | n/a | n/a | 49.38% | 94.92% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.25% | 0.00% | 0.55% | 0.00% | 0.59% | 0.00% | 0.62% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.45% | 0.00% | 0.20% | 0.00% | 0.88% | 0.00% | 1.22% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.55% | 99.55% | 0.00% | 0.00% | 98.78% | 99.47% | 0.13% | 0.03% | 0 / 0 |
| abs_dist | [0, inf] | 68.00% | 66.45% | n/a | n/a | 67.02% | 66.10% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 78.25% | 76.60% | n/a | n/a | 73.93% | 69.33% | n/a | n/a | 0 / 0 |
