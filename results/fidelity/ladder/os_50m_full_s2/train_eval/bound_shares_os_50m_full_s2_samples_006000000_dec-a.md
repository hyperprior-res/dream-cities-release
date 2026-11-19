# Shares at the engine's bounds: os_50m_full_s2_samples_006000000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 11.85% | 10.75% | n/a | n/a | 7.92% | 4.23% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 5.80% | 5.70% | 62.90% | 62.50% | 3.88% | 3.92% | 63.85% | 62.50% | 0 / 0 |
| com_valve | [-1500, 1500] | 19.15% | 19.00% | 23.40% | 23.00% | 19.96% | 15.02% | 25.50% | 26.35% | 0 / 0 |
| ind_valve | [-1500, 1500] | 16.90% | 16.95% | 27.00% | 26.95% | 16.61% | 13.93% | 32.01% | 30.93% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.15% | 0.25% | n/a | n/a | 0.07% | 0.08% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 14.75% | 14.75% | n/a | n/a | 27.95% | 28.05% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 13.60% | 13.60% | n/a | n/a | 26.87% | 26.70% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 25.55% | 25.60% | n/a | n/a | 34.86% | 34.74% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 23.05% | 23.15% | n/a | n/a | 30.97% | 30.43% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 0.80% | 0.85% | n/a | n/a | 0.00% | 0.30% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 48.45% | 48.55% | n/a | n/a | 43.95% | 50.06% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 25.20% | 25.15% | n/a | n/a | 26.03% | 24.66% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 33.55% | 33.40% | n/a | n/a | 37.82% | 36.51% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.19% | 0.20% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.15% | 0.00% | n/a | n/a | 0.18% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.15% | 0.25% | n/a | n/a | 0.07% | 0.08% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.15% | 0.15% | n/a | n/a | 0.09% | 0.09% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.02% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 98.10% | 98.15% | 1.90% | 1.85% | 99.05% | 99.21% | 0.95% | 0.79% | 0 / 0 |
| com_cap | [0, 1] | 98.95% | 98.90% | 1.05% | 1.10% | 98.54% | 99.22% | 1.46% | 0.78% | 0 / 0 |
| ind_cap | [0, 1] | 99.20% | 99.25% | 0.80% | 0.75% | 99.64% | 99.67% | 0.36% | 0.33% | 0 / 0 |
| need_hospital | [-1, 1] | 3.15% | 3.05% | 21.40% | 22.10% | 9.14% | 2.50% | 24.74% | 23.35% | 0 / 0 |
| need_church | [-1, 1] | 2.60% | 2.00% | 31.35% | 32.20% | 8.78% | 2.10% | 35.23% | 33.34% | 0 / 0 |
| road_fund | [0, inf] | 13.45% | 13.45% | n/a | n/a | 26.74% | 26.69% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 16.00% | 16.00% | n/a | n/a | 28.53% | 28.39% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 21.90% | 21.90% | n/a | n/a | 33.92% | 34.04% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 11.15% | 11.25% | 88.85% | 88.75% | 4.66% | 4.23% | 95.34% | 95.78% | 0 / 0 |
| fire_pop | [0, inf] | 91.05% | 93.40% | n/a | n/a | 61.61% | 94.92% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.30% | 0.00% | 0.35% | 0.00% | 0.71% | 0.00% | 0.96% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 0.35% | 0.00% | 0.20% | 0.00% | 0.73% | 0.00% | 0.89% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.60% | 99.55% | 0.00% | 0.00% | 99.48% | 99.47% | 0.01% | 0.03% | 0 / 0 |
| abs_dist | [0, inf] | 67.50% | 66.45% | n/a | n/a | 67.44% | 66.10% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 75.25% | 76.60% | n/a | n/a | 67.01% | 69.33% | n/a | n/a | 0 / 0 |
