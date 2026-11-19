## os_100m_full_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.288 | 0.280 | 0.284 | 0.265 to 0.302 | 0.179 | 0.168 | 0.173 | 0.147 to 0.203 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.297 | 0.289 | 0.293 | 0.273 to 0.312 | 0.193 | 0.180 | 0.186 | 0.156 to 0.220 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.257 | 0.250 | 0.254 | 0.234 to 0.273 | 0.133 | 0.127 | 0.130 | 0.107 to 0.152 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.657 | 0.203 | 0.006 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.370 / 0.393 |
| all plans | 700 | 12 | 0.523 | 0.154 | 0.045 / 0.003 / 0.400 | 0.044 / 0.027 / 0.112 | 0.383 / 0.423 |
| all plans | 700 | 24 | 0.564 | 0.176 | 0.057 / 0.005 / 0.614 | 0.069 / 0.039 / 0.159 | 0.352 / 0.405 |
| state-reading plans | 527 | 1 | 0.637 | 0.201 | 0.010 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.415 / 0.431 |
| state-reading plans | 527 | 12 | 0.526 | 0.162 | 0.057 / 0.003 / 0.505 | 0.044 / 0.028 / 0.106 | 0.408 / 0.442 |
| state-reading plans | 527 | 24 | 0.578 | 0.194 | 0.079 / 0.005 / 0.776 | 0.068 / 0.039 / 0.155 | 0.370 / 0.415 |
| open-loop plans | 173 | 1 | 0.865 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.158 / 0.208 |
| open-loop plans | 173 | 12 | 0.722 | 0.133 | 0.016 / 0.002 / 0.054 | 0.044 / 0.026 / 0.133 | 0.290 / 0.349 |
| open-loop plans | 173 | 24 | 0.879 | 0.128 | 0.022 / 0.005 / 0.111 | 0.072 / 0.039 / 0.168 | 0.289 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.632 | 0.189 | 0.007 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.378 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.527 | 0.152 | 0.050 / 0.002 / 0.433 | 0.044 / 0.030 / 0.105 | 0.387 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.557 | 0.169 | 0.066 / 0.005 / 0.668 | 0.074 / 0.043 / 0.156 | 0.357 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1729 | 0.841 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2842 | 0.890 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 1818.6714 | 0.762 |
| funds_mae_12m | 5673.7400 | 40.0829 | 783.7632 | 0.868 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 213.5030 | 0.792 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 523.5020 | 0.889 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 349.8391 | 0.869 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0442 | 0.798 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0453 | 0.893 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3834 | 0.907 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3773 | 0.885 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3127.0500 | 0.740 |
| funds_mae_24m | 7303.4900 | 72.8329 | 854.7107 | 0.892 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 288.0986 | 0.796 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 673.5068 | 0.666 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 603.9857 | 0.691 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0689 | 0.753 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0574 | 0.914 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3524 | 0.870 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3478 | 0.858 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 854.7 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 288.1 | 160.2 | 787.9 |
| com_valve | 673.5 | 507.1 | 1004.7 |
| ind_valve | 604.0 | 454.2 | 939.2 |
| pop | 3127.1 | 1749.1 | 7044.7 |
| res_pop | 61.9 | 37.1 | 135.5 |
| com_pop | 7.5 | 5.0 | 12.3 |
| ind_pop | 10.3 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.9 | 26.8 | 89.0 |
| tax_fund | 132.4 | 53.9 | 1490.0 |
| road_spend | 77.3 | 9.0 | 638.2 |
| fire_spend | 38.5 | 1.3 | 473.1 |
| police_spend | 52.2 | 3.4 | 618.5 |
| powered_zones | 8.3 | 0.9 | 9.0 |
| unpowered_zones | 5.2 | 0.8 | 7.1 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 55.9 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 900.9 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 251.4 | 128.0 | 549.2 |
| com_valve | 720.2 | 545.4 | 967.3 |
| ind_valve | 667.2 | 502.9 | 866.6 |
| pop | 3187.6 | 1820.5 | 6670.1 |
| res_pop | 61.7 | 37.8 | 127.8 |
| com_pop | 7.3 | 5.0 | 11.7 |
| ind_pop | 10.7 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 51.9 | 27.8 | 83.7 |
| tax_fund | 122.2 | 49.4 | 1392.4 |
| road_spend | 74.0 | 8.4 | 639.3 |
| fire_spend | 35.9 | 1.4 | 467.7 |
| police_spend | 52.4 | 4.3 | 609.4 |
| powered_zones | 9.8 | 1.2 | 11.7 |
| unpowered_zones | 6.0 | 1.1 | 7.9 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 56.0 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 713.9 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 399.8 | 258.1 | 1515.1 |
| com_valve | 531.3 | 390.3 | 1118.5 |
| ind_valve | 411.5 | 305.8 | 1160.1 |
| pop | 2942.5 | 1531.7 | 8185.8 |
| res_pop | 62.6 | 35.0 | 158.8 |
| com_pop | 7.8 | 4.9 | 14.2 |
| ind_pop | 9.0 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.7 | 23.7 | 105.2 |
| tax_fund | 163.5 | 67.8 | 1787.4 |
| road_spend | 87.4 | 10.5 | 634.9 |
| fire_spend | 46.3 | 0.9 | 489.5 |
| police_spend | 51.6 | 0.8 | 646.2 |
| powered_zones | 3.6 | 0.0 | 0.5 |
| unpowered_zones | 2.8 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.4 | 0.0 | 0.1 |
| road_total | 55.4 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.031 | 0.845 |
| traffic | 0.963 | 0.765 |
| pollution | 1.483 | 0.703 |
| land_value | 0.618 | 0.336 |
| crime | 0.987 | 0.580 |
| rate_of_growth | 1.026 | 0.835 |
| fire_coverage | 0.841 | 0.125 |
| police_coverage | 0.800 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.595 | 0.253 | 0.355 | 0.331 to 0.376 | 0.575 | 0.129 | 0.210 | 0.171 to 0.252 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.462 | 0.003 | 0.005 |
| all plans | 12 | 0.345 | 0.030 | 0.036 |
| all plans | 24 | 0.389 | 0.047 | 0.059 |
| state-reading plans | 1 | 0.454 | 0.004 | 0.005 |
| state-reading plans | 12 | 0.346 | 0.035 | 0.036 |
| state-reading plans | 24 | 0.405 | 0.069 | 0.057 |
| open-loop plans | 1 | 0.564 | 0.000 | 0.004 |
| open-loop plans | 12 | 0.488 | 0.014 | 0.037 |
| open-loop plans | 24 | 0.537 | 0.018 | 0.059 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -215.36 |
| tile_cat | -29.17 |
| flags | -13.71 |
| power | -1.97 |
| half | -2309.91 |
| eighth | -34.63 |
| scalars_s2 | -6.76 |
| build_cost | -1.26 |
| scalars | -13.82 |
| ledger | -12.82 |
| bk | -19.89 |
| sc_res_pop | -2.18 |
| sc_com_pop | -0.35 |
| sc_ind_pop | -0.38 |
| sc_powered_zones | -0.15 |
| sc_unpowered_zones | -0.22 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.44 |
| sc_res_valve | -0.98 |
| sc_com_valve | -2.08 |
| sc_ind_valve | -1.35 |
| sc_score | -0.46 |
| sc_funds | -0.98 |
| sc_tax_fund | -0.45 |
| sc_road_spend | -0.54 |
| sc_fire_spend | -0.10 |
| sc_police_spend | -0.12 |
| lg_sprite_cycle | -0.76 |
| lg_total_pop | -1.57 |
| lg_res_hist0 | -0.41 |
| lg_res_hist1 | -0.30 |
| lg_com_hist0 | -0.08 |
| lg_com_hist1 | -0.13 |
| lg_ind_hist0 | -0.11 |
| lg_ind_hist1 | -0.19 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.55 |
| lg_police_fund | -0.09 |
| lg_fire_fund | -0.07 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.03 |
| lg_pollution_max_x | -3.07 |
| lg_pollution_max_y | -3.01 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -5.08 |
| com_rate | -2.30 |
| kl | 12.37 |
| elbo | -2652.39 |
