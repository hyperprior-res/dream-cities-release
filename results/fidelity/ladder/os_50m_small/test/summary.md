## os_50m_small_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.284 | 0.291 | 0.287 | 0.266 to 0.307 | 0.167 | 0.164 | 0.166 | 0.141 to 0.193 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.293 | 0.299 | 0.296 | 0.275 to 0.316 | 0.183 | 0.178 | 0.181 | 0.151 to 0.213 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.253 | 0.261 | 0.257 | 0.233 to 0.279 | 0.118 | 0.117 | 0.117 | 0.098 to 0.139 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.557 | 0.203 | 0.003 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.367 / 0.393 |
| all plans | 700 | 12 | 0.401 | 0.154 | 0.038 / 0.003 / 0.400 | 0.045 / 0.027 / 0.112 | 0.372 / 0.423 |
| all plans | 700 | 24 | 0.466 | 0.176 | 0.052 / 0.005 / 0.614 | 0.080 / 0.039 / 0.159 | 0.338 / 0.405 |
| state-reading plans | 527 | 1 | 0.520 | 0.201 | 0.005 / 0.000 / 0.018 | 0.008 / 0.006 / 0.008 | 0.413 / 0.431 |
| state-reading plans | 527 | 12 | 0.403 | 0.162 | 0.044 / 0.003 / 0.505 | 0.045 / 0.028 / 0.106 | 0.398 / 0.442 |
| state-reading plans | 527 | 24 | 0.481 | 0.194 | 0.062 / 0.005 / 0.776 | 0.079 / 0.039 / 0.155 | 0.357 / 0.415 |
| open-loop plans | 173 | 1 | 0.546 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.150 / 0.208 |
| open-loop plans | 173 | 12 | 0.571 | 0.133 | 0.022 / 0.002 / 0.054 | 0.047 / 0.026 / 0.133 | 0.272 / 0.349 |
| open-loop plans | 173 | 24 | 0.787 | 0.128 | 0.032 / 0.005 / 0.111 | 0.083 / 0.039 / 0.168 | 0.271 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.536 | 0.189 | 0.003 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.375 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.402 | 0.152 | 0.039 / 0.002 / 0.433 | 0.046 / 0.030 / 0.105 | 0.375 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.460 | 0.169 | 0.056 / 0.005 / 0.668 | 0.085 / 0.043 / 0.156 | 0.343 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1656 | 0.805 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2873 | 0.900 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 1962.5714 | 0.713 |
| funds_mae_12m | 5673.7400 | 40.0829 | 779.0921 | 0.869 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 224.6580 | 0.772 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 530.4937 | 0.880 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 333.1550 | 0.895 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0454 | 0.784 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0379 | 0.912 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3715 | 0.879 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3597 | 0.844 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3744.1821 | 0.623 |
| funds_mae_24m | 7303.4900 | 72.8329 | 812.5196 | 0.898 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 326.6066 | 0.735 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 627.6354 | 0.758 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 583.9098 | 0.733 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0800 | 0.661 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0520 | 0.923 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3384 | 0.836 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3302 | 0.814 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 812.5 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 326.6 | 160.2 | 787.9 |
| com_valve | 627.6 | 507.1 | 1004.7 |
| ind_valve | 583.9 | 454.2 | 939.2 |
| pop | 3744.2 | 1749.1 | 7044.7 |
| res_pop | 79.2 | 37.1 | 135.5 |
| com_pop | 7.7 | 5.0 | 12.3 |
| ind_pop | 11.6 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 61.8 | 26.8 | 89.0 |
| tax_fund | 202.9 | 53.9 | 1490.0 |
| road_spend | 101.3 | 9.0 | 638.2 |
| fire_spend | 54.8 | 1.3 | 473.1 |
| police_spend | 91.5 | 3.4 | 618.5 |
| powered_zones | 6.1 | 0.9 | 9.0 |
| unpowered_zones | 4.5 | 0.8 | 7.1 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 49.3 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 825.1 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 301.4 | 128.0 | 549.2 |
| com_valve | 673.6 | 545.4 | 967.3 |
| ind_valve | 647.5 | 502.9 | 866.6 |
| pop | 3772.5 | 1820.5 | 6670.1 |
| res_pop | 79.7 | 37.8 | 127.8 |
| com_pop | 7.7 | 5.0 | 11.7 |
| ind_pop | 11.8 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 62.8 | 27.8 | 83.7 |
| tax_fund | 184.5 | 49.4 | 1392.4 |
| road_spend | 99.5 | 8.4 | 639.3 |
| fire_spend | 50.9 | 1.4 | 467.7 |
| police_spend | 90.0 | 4.3 | 609.4 |
| powered_zones | 6.9 | 1.2 | 11.7 |
| unpowered_zones | 5.3 | 1.1 | 7.9 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.4 |
| road_total | 49.0 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 774.1 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 403.4 | 258.1 | 1515.1 |
| com_valve | 487.5 | 390.3 | 1118.5 |
| ind_valve | 390.3 | 305.8 | 1160.1 |
| pop | 3657.9 | 1531.7 | 8185.8 |
| res_pop | 78.0 | 35.0 | 158.8 |
| com_pop | 7.6 | 4.9 | 14.2 |
| ind_pop | 11.2 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 58.7 | 23.7 | 105.2 |
| tax_fund | 259.0 | 67.8 | 1787.4 |
| road_spend | 106.8 | 10.5 | 634.9 |
| fire_spend | 66.6 | 0.9 | 489.5 |
| police_spend | 96.0 | 0.8 | 646.2 |
| powered_zones | 3.4 | 0.0 | 0.5 |
| unpowered_zones | 2.2 | 0.0 | 4.8 |
| coal_plants | 0.1 | 0.0 | 0.2 |
| nuclear_plants | 0.2 | 0.0 | 0.1 |
| road_total | 50.3 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.051 | 0.845 |
| traffic | 1.053 | 0.765 |
| pollution | 1.351 | 0.703 |
| land_value | 0.683 | 0.336 |
| crime | 0.978 | 0.580 |
| rate_of_growth | 1.073 | 0.835 |
| fire_coverage | 0.955 | 0.125 |
| police_coverage | 0.893 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.351 | 0.284 | 0.314 | 0.292 to 0.334 | 0.203 | 0.151 | 0.173 | 0.145 to 0.203 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.447 | 0.002 | 0.006 |
| all plans | 12 | 0.322 | 0.026 | 0.039 |
| all plans | 24 | 0.383 | 0.045 | 0.069 |
| state-reading plans | 1 | 0.415 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.325 | 0.029 | 0.039 |
| state-reading plans | 24 | 0.397 | 0.050 | 0.068 |
| open-loop plans | 1 | 0.414 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.470 | 0.018 | 0.034 |
| open-loop plans | 24 | 0.655 | 0.031 | 0.071 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -328.20 |
| tile_cat | -39.93 |
| flags | -22.00 |
| power | -6.50 |
| half | -2818.28 |
| eighth | -51.14 |
| scalars_s2 | -5.24 |
| build_cost | -0.88 |
| scalars | -33.92 |
| ledger | -50.90 |
| bk | -79.58 |
| sc_res_pop | -1.50 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.15 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.04 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.36 |
| sc_res_valve | -1.82 |
| sc_com_valve | -3.22 |
| sc_ind_valve | -2.53 |
| sc_score | -7.85 |
| sc_funds | -4.13 |
| sc_tax_fund | -2.20 |
| sc_road_spend | -4.47 |
| sc_fire_spend | -1.27 |
| sc_police_spend | -1.18 |
| lg_sprite_cycle | -1.38 |
| lg_total_pop | -5.59 |
| lg_res_hist0 | -5.61 |
| lg_res_hist1 | -5.76 |
| lg_com_hist0 | -1.43 |
| lg_com_hist1 | -1.67 |
| lg_ind_hist0 | -1.16 |
| lg_ind_hist1 | -2.50 |
| lg_res_cap | -0.04 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.37 |
| lg_need_church | -0.27 |
| lg_road_fund | -2.21 |
| lg_police_fund | -0.44 |
| lg_fire_fund | -0.50 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.42 |
| lg_city_center_x | -0.63 |
| lg_city_center_y | -0.27 |
| lg_pollution_max_x | -7.46 |
| lg_pollution_max_y | -8.05 |
| lg_flood_count | -0.02 |
| lg_abs_dist | -5.09 |
| terrain | -6.19 |
| com_rate | -7.15 |
| kl | 11.82 |
| elbo | -3376.88 |
