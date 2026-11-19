## os_100m_small_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.304 | 0.290 | 0.297 | 0.275 to 0.318 | 0.186 | 0.161 | 0.172 | 0.145 to 0.203 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.312 | 0.298 | 0.305 | 0.282 to 0.328 | 0.201 | 0.174 | 0.186 | 0.156 to 0.222 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.276 | 0.262 | 0.269 | 0.247 to 0.290 | 0.137 | 0.118 | 0.127 | 0.103 to 0.149 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.520 | 0.203 | 0.003 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.385 / 0.393 |
| all plans | 700 | 12 | 0.392 | 0.154 | 0.034 / 0.003 / 0.400 | 0.052 / 0.027 / 0.112 | 0.376 / 0.423 |
| all plans | 700 | 24 | 0.454 | 0.176 | 0.047 / 0.005 / 0.614 | 0.083 / 0.039 / 0.159 | 0.344 / 0.405 |
| state-reading plans | 527 | 1 | 0.510 | 0.201 | 0.005 / 0.000 / 0.018 | 0.008 / 0.006 / 0.008 | 0.432 / 0.431 |
| state-reading plans | 527 | 12 | 0.397 | 0.162 | 0.039 / 0.003 / 0.505 | 0.051 / 0.028 / 0.106 | 0.404 / 0.442 |
| state-reading plans | 527 | 24 | 0.474 | 0.194 | 0.058 / 0.005 / 0.776 | 0.082 / 0.039 / 0.155 | 0.364 / 0.415 |
| open-loop plans | 173 | 1 | 0.510 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.157 / 0.208 |
| open-loop plans | 173 | 12 | 0.502 | 0.133 | 0.021 / 0.002 / 0.054 | 0.054 / 0.026 / 0.133 | 0.272 / 0.349 |
| open-loop plans | 173 | 24 | 0.692 | 0.128 | 0.028 / 0.005 / 0.111 | 0.085 / 0.039 / 0.168 | 0.272 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.520 | 0.189 | 0.003 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.393 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.397 | 0.152 | 0.036 / 0.002 / 0.433 | 0.052 / 0.030 / 0.105 | 0.381 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.451 | 0.169 | 0.049 / 0.005 / 0.668 | 0.089 / 0.043 / 0.156 | 0.350 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1722 | 0.837 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2970 | 0.930 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2255.4679 | 0.614 |
| funds_mae_12m | 5673.7400 | 40.0829 | 677.9704 | 0.887 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 223.1930 | 0.775 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 540.2032 | 0.867 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 358.7732 | 0.855 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0519 | 0.707 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0340 | 0.922 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3765 | 0.891 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3630 | 0.851 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3908.2464 | 0.592 |
| funds_mae_24m | 7303.4900 | 72.8329 | 750.4362 | 0.906 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 356.8991 | 0.687 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 644.9471 | 0.723 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 604.2198 | 0.691 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0827 | 0.639 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0473 | 0.931 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3438 | 0.849 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3347 | 0.825 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 750.4 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 356.9 | 160.2 | 787.9 |
| com_valve | 644.9 | 507.1 | 1004.7 |
| ind_valve | 604.2 | 454.2 | 939.2 |
| pop | 3908.2 | 1749.1 | 7044.7 |
| res_pop | 86.2 | 37.1 | 135.5 |
| com_pop | 7.7 | 5.0 | 12.3 |
| ind_pop | 12.2 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 58.4 | 26.8 | 89.0 |
| tax_fund | 225.0 | 53.9 | 1490.0 |
| road_spend | 94.6 | 9.0 | 638.2 |
| fire_spend | 51.5 | 1.3 | 473.1 |
| police_spend | 78.1 | 3.4 | 618.5 |
| powered_zones | 5.4 | 0.9 | 9.0 |
| unpowered_zones | 4.4 | 0.8 | 7.1 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 43.2 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 709.6 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 337.9 | 128.0 | 549.2 |
| com_valve | 692.5 | 545.4 | 967.3 |
| ind_valve | 665.0 | 502.9 | 866.6 |
| pop | 3982.7 | 1820.5 | 6670.1 |
| res_pop | 87.0 | 37.8 | 127.8 |
| com_pop | 7.8 | 5.0 | 11.7 |
| ind_pop | 12.6 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 59.8 | 27.8 | 83.7 |
| tax_fund | 213.2 | 49.4 | 1392.4 |
| road_spend | 89.3 | 8.4 | 639.3 |
| fire_spend | 48.3 | 1.4 | 467.7 |
| police_spend | 80.4 | 4.3 | 609.4 |
| powered_zones | 6.2 | 1.2 | 11.7 |
| unpowered_zones | 5.1 | 1.1 | 7.9 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.4 |
| road_total | 43.0 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 875.0 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 414.7 | 258.1 | 1515.1 |
| com_valve | 500.0 | 390.3 | 1118.5 |
| ind_valve | 418.9 | 305.8 | 1160.1 |
| pop | 3681.3 | 1531.7 | 8185.8 |
| res_pop | 83.7 | 35.0 | 158.8 |
| com_pop | 7.5 | 4.9 | 14.2 |
| ind_pop | 11.1 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 54.1 | 23.7 | 105.2 |
| tax_fund | 260.9 | 67.8 | 1787.4 |
| road_spend | 110.7 | 10.5 | 634.9 |
| fire_spend | 61.4 | 0.9 | 489.5 |
| police_spend | 71.2 | 0.8 | 646.2 |
| powered_zones | 2.7 | 0.0 | 0.5 |
| unpowered_zones | 2.1 | 0.0 | 4.8 |
| coal_plants | 0.1 | 0.0 | 0.2 |
| nuclear_plants | 0.2 | 0.0 | 0.1 |
| road_total | 43.8 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.052 | 0.845 |
| traffic | 1.002 | 0.765 |
| pollution | 1.270 | 0.703 |
| land_value | 0.658 | 0.336 |
| crime | 0.976 | 0.580 |
| rate_of_growth | 1.065 | 0.835 |
| fire_coverage | 0.814 | 0.125 |
| police_coverage | 0.848 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.350 | 0.287 | 0.315 | 0.292 to 0.338 | 0.210 | 0.151 | 0.176 | 0.147 to 0.208 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.437 | 0.002 | 0.005 |
| all plans | 12 | 0.319 | 0.020 | 0.045 |
| all plans | 24 | 0.372 | 0.037 | 0.073 |
| state-reading plans | 1 | 0.423 | 0.003 | 0.005 |
| state-reading plans | 12 | 0.325 | 0.022 | 0.045 |
| state-reading plans | 24 | 0.392 | 0.044 | 0.073 |
| open-loop plans | 1 | 0.415 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.400 | 0.014 | 0.050 |
| open-loop plans | 24 | 0.570 | 0.020 | 0.072 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -375.47 |
| tile_cat | -43.62 |
| flags | -18.04 |
| power | -4.59 |
| half | -2993.73 |
| eighth | -59.91 |
| scalars_s2 | -5.19 |
| build_cost | -0.88 |
| scalars | -33.04 |
| ledger | -55.83 |
| bk | -83.67 |
| sc_res_pop | -1.50 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.15 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.31 |
| sc_res_valve | -1.83 |
| sc_com_valve | -3.07 |
| sc_ind_valve | -3.02 |
| sc_score | -7.13 |
| sc_funds | -3.63 |
| sc_tax_fund | -3.86 |
| sc_road_spend | -4.04 |
| sc_fire_spend | -0.63 |
| sc_police_spend | -0.64 |
| lg_sprite_cycle | -1.54 |
| lg_total_pop | -3.03 |
| lg_res_hist0 | -4.92 |
| lg_res_hist1 | -5.01 |
| lg_com_hist0 | -0.89 |
| lg_com_hist1 | -3.11 |
| lg_ind_hist0 | -2.37 |
| lg_ind_hist1 | -3.37 |
| lg_res_cap | -0.32 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.01 |
| lg_need_hospital | -0.72 |
| lg_need_church | -0.89 |
| lg_road_fund | -2.14 |
| lg_police_fund | -0.44 |
| lg_fire_fund | -0.72 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.31 |
| lg_city_center_x | -0.70 |
| lg_city_center_y | -0.37 |
| lg_pollution_max_x | -10.08 |
| lg_pollution_max_y | -9.66 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -5.20 |
| terrain | -6.12 |
| com_rate | -9.01 |
| kl | 13.51 |
| elbo | -3613.74 |
