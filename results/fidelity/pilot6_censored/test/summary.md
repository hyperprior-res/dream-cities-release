## pilot6_censored_samples_000600064_dec-a

samples consumed: 600064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "e273b6d5a2e47448", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.261 | 0.261 | 0.261 | 0.241 to 0.280 | 0.144 | 0.140 | 0.142 | 0.121 to 0.167 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.052 | 0.050 | 0.046 to 0.056 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.268 | 0.269 | 0.269 | 0.246 to 0.289 | 0.156 | 0.152 | 0.154 | 0.128 to 0.185 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.133 | 0.133 | 0.133 | 0.122 to 0.144 | 0.052 | 0.054 | 0.053 | 0.048 to 0.059 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.234 | 0.234 | 0.234 | 0.212 to 0.254 | 0.106 | 0.104 | 0.105 | 0.089 to 0.122 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.117 | 0.120 | 0.118 | 0.105 to 0.132 | 0.040 | 0.044 | 0.042 | 0.034 to 0.049 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.510 | 0.203 | 0.003 / 0.000 / 0.013 | 0.007 / 0.006 / 0.007 | 0.335 / 0.393 |
| all plans | 700 | 12 | 0.383 | 0.154 | 0.035 / 0.003 / 0.400 | 0.034 / 0.027 / 0.112 | 0.342 / 0.423 |
| all plans | 700 | 24 | 0.428 | 0.176 | 0.051 / 0.005 / 0.614 | 0.059 / 0.039 / 0.159 | 0.313 / 0.405 |
| state-reading plans | 527 | 1 | 0.484 | 0.201 | 0.004 / 0.000 / 0.018 | 0.007 / 0.006 / 0.008 | 0.376 / 0.431 |
| state-reading plans | 527 | 12 | 0.388 | 0.162 | 0.045 / 0.003 / 0.505 | 0.034 / 0.028 / 0.106 | 0.368 / 0.442 |
| state-reading plans | 527 | 24 | 0.444 | 0.194 | 0.068 / 0.005 / 0.776 | 0.061 / 0.039 / 0.155 | 0.331 / 0.415 |
| open-loop plans | 173 | 1 | 0.564 | 0.226 | 0.000 / 0.000 / 0.000 | 0.006 / 0.005 / 0.007 | 0.137 / 0.208 |
| open-loop plans | 173 | 12 | 0.473 | 0.133 | 0.012 / 0.002 / 0.054 | 0.032 / 0.026 / 0.133 | 0.245 / 0.349 |
| open-loop plans | 173 | 24 | 0.501 | 0.128 | 0.018 / 0.005 / 0.111 | 0.053 / 0.039 / 0.168 | 0.252 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.504 | 0.189 | 0.003 / 0.000 / 0.015 | 0.007 / 0.006 / 0.009 | 0.345 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.388 | 0.152 | 0.036 / 0.002 / 0.433 | 0.034 / 0.030 / 0.105 | 0.343 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.429 | 0.169 | 0.061 / 0.005 / 0.668 | 0.064 / 0.043 / 0.156 | 0.317 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1424 | 0.692 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2608 | 0.817 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 1376.1500 | 0.911 |
| funds_mae_12m | 5673.7400 | 40.0829 | 996.3911 | 0.830 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 174.1420 | 0.861 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 497.4862 | 0.924 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 294.6373 | 0.955 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0339 | 0.919 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0349 | 0.919 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3418 | 0.809 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3355 | 0.787 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 2560.6071 | 0.847 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1209.9359 | 0.843 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 255.6082 | 0.848 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 647.0725 | 0.719 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 498.8605 | 0.908 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0591 | 0.836 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0515 | 0.924 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3133 | 0.774 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3090 | 0.762 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1209.9 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 255.6 | 160.2 | 787.9 |
| com_valve | 647.1 | 507.1 | 1004.7 |
| ind_valve | 498.9 | 454.2 | 939.2 |
| pop | 2560.6 | 1749.1 | 7044.7 |
| res_pop | 55.6 | 37.1 | 135.5 |
| com_pop | 6.4 | 5.0 | 12.3 |
| ind_pop | 7.4 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 46.0 | 26.8 | 89.0 |
| tax_fund | 123.7 | 53.9 | 1490.0 |
| road_spend | 82.6 | 9.0 | 638.2 |
| fire_spend | 30.1 | 1.3 | 473.1 |
| police_spend | 45.5 | 3.4 | 618.5 |
| powered_zones | 5.2 | 0.9 | 9.0 |
| unpowered_zones | 5.0 | 0.8 | 7.1 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 53.2 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1113.7 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 219.2 | 128.0 | 549.2 |
| com_valve | 684.6 | 545.4 | 967.3 |
| ind_valve | 544.4 | 502.9 | 866.6 |
| pop | 2696.7 | 1820.5 | 6670.1 |
| res_pop | 57.4 | 37.8 | 127.8 |
| com_pop | 6.4 | 5.0 | 11.7 |
| ind_pop | 7.7 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 48.7 | 27.8 | 83.7 |
| tax_fund | 117.6 | 49.4 | 1392.4 |
| road_spend | 81.4 | 8.4 | 639.3 |
| fire_spend | 27.9 | 1.4 | 467.7 |
| police_spend | 44.4 | 4.3 | 609.4 |
| powered_zones | 6.6 | 1.2 | 11.7 |
| unpowered_zones | 5.8 | 1.1 | 7.9 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.4 |
| road_total | 53.3 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1503.1 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 366.6 | 258.1 | 1515.1 |
| com_valve | 532.9 | 390.3 | 1118.5 |
| ind_valve | 360.2 | 305.8 | 1160.1 |
| pop | 2146.1 | 1531.7 | 8185.8 |
| res_pop | 50.0 | 35.0 | 158.8 |
| com_pop | 6.1 | 4.9 | 14.2 |
| ind_pop | 6.4 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 37.8 | 23.7 | 105.2 |
| tax_fund | 142.2 | 67.8 | 1787.4 |
| road_spend | 86.3 | 10.5 | 634.9 |
| fire_spend | 36.7 | 0.9 | 489.5 |
| police_spend | 48.5 | 0.8 | 646.2 |
| powered_zones | 1.1 | 0.0 | 0.5 |
| unpowered_zones | 2.5 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.2 | 0.0 | 0.1 |
| road_total | 53.2 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.121 | 0.845 |
| traffic | 1.180 | 0.765 |
| pollution | 1.688 | 0.703 |
| land_value | 0.858 | 0.336 |
| crime | 1.197 | 0.580 |
| rate_of_growth | 1.049 | 0.835 |
| fire_coverage | 1.193 | 0.125 |
| police_coverage | 0.981 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.613 | 0.236 | 0.341 | 0.315 to 0.364 | 0.835 | 0.105 | 0.186 | 0.148 to 0.228 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.443 | 0.001 | 0.005 |
| all plans | 12 | 0.314 | 0.025 | 0.030 |
| all plans | 24 | 0.355 | 0.051 | 0.053 |
| state-reading plans | 1 | 0.428 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.318 | 0.034 | 0.030 |
| state-reading plans | 24 | 0.370 | 0.069 | 0.058 |
| open-loop plans | 1 | 0.440 | 0.000 | 0.004 |
| open-loop plans | 12 | 0.377 | 0.010 | 0.030 |
| open-loop plans | 24 | 0.390 | 0.018 | 0.049 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -256.66 |
| tile_cat | -38.61 |
| flags | -17.77 |
| power | -3.16 |
| half | -2910.26 |
| eighth | -41.43 |
| scalars_s2 | -5.84 |
| build_cost | -1.04 |
| scalars | -12.61 |
| ledger | -13.18 |
| bk | -19.94 |
| sc_res_pop | -1.82 |
| sc_com_pop | -0.24 |
| sc_ind_pop | -0.22 |
| sc_powered_zones | -0.06 |
| sc_unpowered_zones | -0.07 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.41 |
| sc_res_valve | -0.99 |
| sc_com_valve | -2.07 |
| sc_ind_valve | -1.16 |
| sc_score | -0.47 |
| sc_funds | -0.90 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.50 |
| sc_fire_spend | -0.12 |
| sc_police_spend | -0.12 |
| lg_sprite_cycle | -0.72 |
| lg_total_pop | -1.60 |
| lg_res_hist0 | -0.37 |
| lg_res_hist1 | -0.37 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.42 |
| lg_ind_hist0 | -0.06 |
| lg_ind_hist1 | -0.29 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.54 |
| lg_police_fund | -0.09 |
| lg_fire_fund | -0.08 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.11 |
| lg_city_center_y | -0.11 |
| lg_pollution_max_x | -3.03 |
| lg_pollution_max_y | -2.89 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -8.94 |
| com_rate | -11.36 |
| kl | 3.62 |
| elbo | -3318.65 |
