## sf_100m_small_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.249 | 0.298 | 0.271 | 0.250 to 0.293 | 0.138 | 0.179 | 0.156 | 0.135 to 0.181 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.257 | 0.306 | 0.279 | 0.257 to 0.302 | 0.149 | 0.192 | 0.168 | 0.143 to 0.197 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.220 | 0.270 | 0.243 | 0.220 to 0.264 | 0.102 | 0.135 | 0.116 | 0.101 to 0.133 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.795 | 0.203 | 0.003 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.365 / 0.393 |
| all plans | 700 | 12 | 0.610 | 0.154 | 0.043 / 0.003 / 0.400 | 0.054 / 0.027 / 0.112 | 0.299 / 0.423 |
| all plans | 700 | 24 | 0.823 | 0.176 | 0.087 / 0.005 / 0.614 | 0.105 / 0.039 / 0.159 | 0.253 / 0.405 |
| state-reading plans | 527 | 1 | 0.750 | 0.201 | 0.004 / 0.000 / 0.018 | 0.008 / 0.006 / 0.008 | 0.409 / 0.431 |
| state-reading plans | 527 | 12 | 0.593 | 0.162 | 0.049 / 0.003 / 0.505 | 0.054 / 0.028 / 0.106 | 0.323 / 0.442 |
| state-reading plans | 527 | 24 | 0.796 | 0.194 | 0.104 / 0.005 / 0.776 | 0.101 / 0.039 / 0.155 | 0.272 / 0.415 |
| open-loop plans | 173 | 1 | 0.672 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.153 / 0.208 |
| open-loop plans | 173 | 12 | 1.218 | 0.133 | 0.026 / 0.002 / 0.054 | 0.057 / 0.026 / 0.133 | 0.215 / 0.349 |
| open-loop plans | 173 | 24 | 2.084 | 0.128 | 0.051 / 0.005 / 0.111 | 0.119 / 0.039 / 0.168 | 0.189 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.657 | 0.189 | 0.003 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.374 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.612 | 0.152 | 0.046 / 0.002 / 0.433 | 0.055 / 0.030 / 0.105 | 0.303 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.792 | 0.169 | 0.099 / 0.005 / 0.668 | 0.103 / 0.043 / 0.156 | 0.258 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1557 | 0.757 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2712 | 0.849 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2528.4750 | 0.522 |
| funds_mae_12m | 5673.7400 | 40.0829 | 787.1059 | 0.867 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 223.0357 | 0.775 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 566.9150 | 0.831 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 363.9857 | 0.847 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0545 | 0.677 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0432 | 0.899 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.2992 | 0.708 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.2993 | 0.702 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 5766.0857 | 0.241 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1061.4845 | 0.863 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 396.1071 | 0.624 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 674.0936 | 0.664 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 664.9436 | 0.565 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.1050 | 0.452 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0873 | 0.865 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.2529 | 0.624 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.2529 | 0.624 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1061.5 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 396.1 | 160.2 | 787.9 |
| com_valve | 674.1 | 507.1 | 1004.7 |
| ind_valve | 664.9 | 454.2 | 939.2 |
| pop | 5766.1 | 1749.1 | 7044.7 |
| res_pop | 115.7 | 37.1 | 135.5 |
| com_pop | 10.2 | 5.0 | 12.3 |
| ind_pop | 18.2 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 101.3 | 26.8 | 89.0 |
| tax_fund | 222.8 | 53.9 | 1490.0 |
| road_spend | 98.4 | 9.0 | 638.2 |
| fire_spend | 58.6 | 1.3 | 473.1 |
| police_spend | 87.7 | 3.4 | 618.5 |
| powered_zones | 12.4 | 0.9 | 9.0 |
| unpowered_zones | 8.0 | 0.8 | 7.1 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 1.0 | 0.0 | 0.3 |
| road_total | 63.0 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1067.9 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 326.2 | 128.0 | 549.2 |
| com_valve | 722.8 | 545.4 | 967.3 |
| ind_valve | 726.8 | 502.9 | 866.6 |
| pop | 5725.3 | 1820.5 | 6670.1 |
| res_pop | 110.3 | 37.8 | 127.8 |
| com_pop | 10.2 | 5.0 | 11.7 |
| ind_pop | 18.4 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 102.7 | 27.8 | 83.7 |
| tax_fund | 204.1 | 49.4 | 1392.4 |
| road_spend | 94.4 | 8.4 | 639.3 |
| fire_spend | 55.4 | 1.4 | 467.7 |
| police_spend | 88.7 | 4.3 | 609.4 |
| powered_zones | 13.0 | 1.2 | 11.7 |
| unpowered_zones | 8.6 | 1.1 | 7.9 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 1.0 | 0.0 | 0.4 |
| road_total | 63.9 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1041.9 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 608.9 | 258.1 | 1515.1 |
| com_valve | 525.6 | 390.3 | 1118.5 |
| ind_valve | 476.4 | 305.8 | 1160.1 |
| pop | 5890.4 | 1531.7 | 8185.8 |
| res_pop | 132.4 | 35.0 | 158.8 |
| com_pop | 10.3 | 4.9 | 14.2 |
| ind_pop | 17.6 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 97.1 | 23.7 | 105.2 |
| tax_fund | 279.8 | 67.8 | 1787.4 |
| road_spend | 110.5 | 10.5 | 634.9 |
| fire_spend | 68.6 | 0.9 | 489.5 |
| police_spend | 84.6 | 0.8 | 646.2 |
| powered_zones | 10.7 | 0.0 | 0.5 |
| unpowered_zones | 6.2 | 0.0 | 4.8 |
| coal_plants | 0.5 | 0.0 | 0.2 |
| nuclear_plants | 0.9 | 0.0 | 0.1 |
| road_total | 60.4 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.419 | 0.845 |
| traffic | 1.080 | 0.765 |
| pollution | 1.704 | 0.703 |
| land_value | 0.850 | 0.336 |
| crime | 1.412 | 0.580 |
| rate_of_growth | 1.286 | 0.835 |
| fire_coverage | 1.108 | 0.125 |
| police_coverage | 1.188 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.368 | 0.291 | 0.325 | 0.302 to 0.347 | 0.229 | 0.159 | 0.188 | 0.156 to 0.221 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.614 | 0.001 | 0.005 |
| all plans | 12 | 0.434 | 0.035 | 0.042 |
| all plans | 24 | 0.617 | 0.091 | 0.094 |
| state-reading plans | 1 | 0.580 | 0.002 | 0.005 |
| state-reading plans | 12 | 0.424 | 0.039 | 0.042 |
| state-reading plans | 24 | 0.605 | 0.108 | 0.089 |
| open-loop plans | 1 | 0.510 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.785 | 0.022 | 0.043 |
| open-loop plans | 24 | 1.538 | 0.061 | 0.112 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -306.30 |
| tile_cat | -40.00 |
| flags | -16.60 |
| power | -3.73 |
| half | -2749.60 |
| eighth | -39.19 |
| scalars_s2 | -5.71 |
| build_cost | -1.05 |
| scalars | -15.85 |
| ledger | -22.27 |
| bk | -32.41 |
| sc_res_pop | -1.78 |
| sc_com_pop | -0.17 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.08 |
| sc_unpowered_zones | -0.11 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.37 |
| sc_res_valve | -1.20 |
| sc_com_valve | -2.36 |
| sc_ind_valve | -1.81 |
| sc_score | -1.00 |
| sc_funds | -1.45 |
| sc_tax_fund | -0.82 |
| sc_road_spend | -0.99 |
| sc_fire_spend | -0.23 |
| sc_police_spend | -0.29 |
| lg_sprite_cycle | -0.93 |
| lg_total_pop | -2.12 |
| lg_res_hist0 | -1.39 |
| lg_res_hist1 | -0.94 |
| lg_com_hist0 | -0.34 |
| lg_com_hist1 | -0.30 |
| lg_ind_hist0 | -0.54 |
| lg_ind_hist1 | -0.51 |
| lg_res_cap | -0.06 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.20 |
| lg_need_church | -0.15 |
| lg_road_fund | -0.99 |
| lg_police_fund | -0.20 |
| lg_fire_fund | -0.16 |
| lg_auto_budget | -0.02 |
| lg_fire_pop | -0.11 |
| lg_city_center_x | -0.29 |
| lg_city_center_y | -0.21 |
| lg_pollution_max_x | -4.91 |
| lg_pollution_max_y | -5.04 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.88 |
| terrain | -6.49 |
| com_rate | -4.97 |
| kl | 13.64 |
| elbo | -3219.70 |
