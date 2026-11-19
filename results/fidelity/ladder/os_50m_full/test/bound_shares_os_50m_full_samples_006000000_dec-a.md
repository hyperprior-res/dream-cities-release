# Shares at the engine's bounds: os_50m_full_samples_006000000_dec-a

Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. 'beyond' counts values outside the bounds (model / engine).

| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |
|---|---|---|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 11.85% | 11.15% | n/a | n/a | 5.01% | 3.09% | n/a | n/a | 0 / 0 |
| res_valve | [-2000, 2000] | 6.35% | 6.40% | 62.40% | 62.50% | 3.78% | 4.20% | 64.75% | 63.78% | 0 / 0 |
| com_valve | [-1500, 1500] | 17.55% | 17.40% | 25.30% | 25.40% | 19.48% | 15.52% | 26.29% | 26.02% | 0 / 0 |
| ind_valve | [-1500, 1500] | 18.15% | 18.35% | 25.65% | 25.65% | 20.96% | 15.00% | 27.87% | 24.62% | 0 / 0 |
| res_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| com_pop | [0, inf] | 0.15% | 0.15% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| tax_fund | [0, inf] | 11.35% | 11.35% | n/a | n/a | 24.99% | 25.09% | n/a | n/a | 0 / 0 |
| road_spend | [0, inf] | 11.20% | 11.20% | n/a | n/a | 24.75% | 24.75% | n/a | n/a | 0 / 0 |
| fire_spend | [0, inf] | 12.90% | 12.80% | n/a | n/a | 25.49% | 25.25% | n/a | n/a | 0 / 0 |
| police_spend | [0, inf] | 16.15% | 16.15% | n/a | n/a | 26.21% | 25.84% | n/a | n/a | 0 / 0 |
| powered_zones | [0, inf] | 1.30% | 1.30% | n/a | n/a | 0.00% | 0.12% | n/a | n/a | 0 / 0 |
| unpowered_zones | [0, inf] | 48.55% | 48.80% | n/a | n/a | 43.19% | 50.74% | n/a | n/a | 0 / 0 |
| coal_plants | [0, inf] | 38.35% | 38.35% | n/a | n/a | 41.91% | 39.38% | n/a | n/a | 0 / 0 |
| nuclear_plants | [0, inf] | 24.70% | 24.75% | n/a | n/a | 23.92% | 23.29% | n/a | n/a | 0 / 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.11% | 0.00% | n/a | n/a | 0 / 0 |
| total_pop | [0, inf] | 0.15% | 0.00% | n/a | n/a | 0.28% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| res_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist0 | [0, inf] | 0.15% | 0.15% | n/a | n/a | 0.10% | 0.00% | n/a | n/a | 0 / 0 |
| com_hist1 | [0, inf] | 0.10% | 0.10% | n/a | n/a | 0.00% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0.13% | 0.00% | n/a | n/a | 0 / 0 |
| ind_hist1 | [0, inf] | 0.05% | 0.00% | n/a | n/a | 0.01% | 0.00% | n/a | n/a | 0 / 0 |
| res_cap | [0, 1] | 96.45% | 96.50% | 3.55% | 3.50% | 96.62% | 96.38% | 3.38% | 3.62% | 0 / 0 |
| com_cap | [0, 1] | 99.15% | 99.50% | 0.85% | 0.50% | 99.19% | 99.23% | 0.81% | 0.77% | 0 / 0 |
| ind_cap | [0, 1] | 99.75% | 99.75% | 0.25% | 0.25% | 99.61% | 99.98% | 0.39% | 0.02% | 0 / 0 |
| need_hospital | [-1, 1] | 2.30% | 2.40% | 23.90% | 23.25% | 5.40% | 1.37% | 27.21% | 25.88% | 0 / 0 |
| need_church | [-1, 1] | 2.05% | 1.80% | 38.05% | 36.80% | 2.94% | 0.92% | 45.97% | 39.73% | 0 / 0 |
| road_fund | [0, inf] | 10.45% | 10.45% | n/a | n/a | 24.52% | 24.68% | n/a | n/a | 0 / 0 |
| police_fund | [0, inf] | 10.45% | 10.45% | n/a | n/a | 25.78% | 24.68% | n/a | n/a | 0 / 0 |
| fire_fund | [0, inf] | 10.60% | 10.60% | n/a | n/a | 25.13% | 24.74% | n/a | n/a | 0 / 0 |
| auto_budget | [0, 1] | 12.50% | 12.50% | 87.50% | 87.50% | 2.92% | 2.77% | 97.08% | 97.23% | 0 / 0 |
| fire_pop | [0, inf] | 91.30% | 95.80% | n/a | n/a | 53.04% | 97.74% | n/a | n/a | 0 / 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0 / 0 |
| pollution_max_x | [0, 118] | 0.25% | 0.00% | 0.60% | 0.00% | 0.48% | 0.00% | 0.56% | 0.00% | 0 / 0 |
| pollution_max_y | [0, 98] | 1.10% | 0.00% | 1.70% | 0.00% | 0.77% | 0.00% | 1.62% | 0.00% | 0 / 0 |
| flood_count | [0, 30] | 99.50% | 99.50% | 0.00% | 0.00% | 99.17% | 99.42% | 0.01% | 0.00% | 0 / 0 |
| abs_dist | [0, inf] | 66.15% | 64.50% | n/a | n/a | 68.65% | 67.65% | n/a | n/a | 0 / 0 |
| build_cost | [0, inf] | 81.15% | 80.80% | n/a | n/a | 68.28% | 69.02% | n/a | n/a | 0 / 0 |
