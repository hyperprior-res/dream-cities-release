## os_15m_small_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.294 | 0.281 | 0.287 | 0.267 to 0.306 | 0.186 | 0.157 | 0.170 | 0.143 to 0.200 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.302 | 0.290 | 0.296 | 0.275 to 0.315 | 0.201 | 0.172 | 0.186 | 0.155 to 0.219 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.266 | 0.250 | 0.258 | 0.235 to 0.279 | 0.133 | 0.108 | 0.119 | 0.097 to 0.142 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.586 | 0.203 | 0.004 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.375 / 0.393 |
| all plans | 700 | 12 | 0.422 | 0.154 | 0.046 / 0.003 / 0.400 | 0.057 / 0.027 / 0.112 | 0.369 / 0.423 |
| all plans | 700 | 24 | 0.482 | 0.176 | 0.073 / 0.005 / 0.614 | 0.079 / 0.039 / 0.159 | 0.337 / 0.405 |
| state-reading plans | 527 | 1 | 0.579 | 0.201 | 0.006 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.420 / 0.431 |
| state-reading plans | 527 | 12 | 0.424 | 0.162 | 0.052 / 0.003 / 0.505 | 0.056 / 0.028 / 0.106 | 0.395 / 0.442 |
| state-reading plans | 527 | 24 | 0.497 | 0.194 | 0.084 / 0.005 / 0.776 | 0.075 / 0.039 / 0.155 | 0.356 / 0.415 |
| open-loop plans | 173 | 1 | 0.583 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.157 / 0.208 |
| open-loop plans | 173 | 12 | 0.564 | 0.133 | 0.030 / 0.002 / 0.054 | 0.064 / 0.026 / 0.133 | 0.270 / 0.349 |
| open-loop plans | 173 | 24 | 0.703 | 0.128 | 0.053 / 0.005 / 0.111 | 0.091 / 0.039 / 0.168 | 0.269 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.580 | 0.189 | 0.005 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.384 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.426 | 0.152 | 0.049 / 0.002 / 0.433 | 0.057 / 0.030 / 0.105 | 0.372 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.479 | 0.169 | 0.083 / 0.005 / 0.668 | 0.084 / 0.043 / 0.156 | 0.341 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1702 | 0.828 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2874 | 0.900 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2317.1571 | 0.594 |
| funds_mae_12m | 5673.7400 | 40.0829 | 806.9570 | 0.864 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 227.8537 | 0.767 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 555.9109 | 0.845 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 349.6252 | 0.869 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0574 | 0.642 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0457 | 0.892 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3692 | 0.874 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3594 | 0.843 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3671.9571 | 0.637 |
| funds_mae_24m | 7303.4900 | 72.8329 | 969.7245 | 0.876 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 369.6657 | 0.666 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 703.1738 | 0.606 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 709.6221 | 0.473 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0790 | 0.669 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0726 | 0.889 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3372 | 0.833 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3303 | 0.815 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 969.7 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 369.7 | 160.2 | 787.9 |
| com_valve | 703.2 | 507.1 | 1004.7 |
| ind_valve | 709.6 | 454.2 | 939.2 |
| pop | 3672.0 | 1749.1 | 7044.7 |
| res_pop | 75.9 | 37.1 | 135.5 |
| com_pop | 7.8 | 5.0 | 12.3 |
| ind_pop | 13.5 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 54.8 | 26.8 | 89.0 |
| tax_fund | 193.3 | 53.9 | 1490.0 |
| road_spend | 101.6 | 9.0 | 638.2 |
| fire_spend | 56.5 | 1.3 | 473.1 |
| police_spend | 93.9 | 3.4 | 618.5 |
| powered_zones | 5.4 | 0.9 | 9.0 |
| unpowered_zones | 4.5 | 0.8 | 7.1 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 52.5 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 909.1 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 309.2 | 128.0 | 549.2 |
| com_valve | 747.0 | 545.4 | 967.3 |
| ind_valve | 789.7 | 502.9 | 866.6 |
| pop | 3617.4 | 1820.5 | 6670.1 |
| res_pop | 75.1 | 37.8 | 127.8 |
| com_pop | 7.9 | 5.0 | 11.7 |
| ind_pop | 13.5 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 56.9 | 27.8 | 83.7 |
| tax_fund | 178.8 | 49.4 | 1392.4 |
| road_spend | 99.0 | 8.4 | 639.3 |
| fire_spend | 55.4 | 1.4 | 467.7 |
| police_spend | 92.6 | 4.3 | 609.4 |
| powered_zones | 6.4 | 1.2 | 11.7 |
| unpowered_zones | 5.3 | 1.1 | 7.9 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.4 |
| road_total | 51.8 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1154.5 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 553.9 | 258.1 | 1515.1 |
| com_valve | 569.6 | 390.3 | 1118.5 |
| ind_valve | 465.8 | 305.8 | 1160.1 |
| pop | 3838.3 | 1531.7 | 8185.8 |
| res_pop | 78.2 | 35.0 | 158.8 |
| com_pop | 7.8 | 4.9 | 14.2 |
| ind_pop | 13.4 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 48.7 | 23.7 | 105.2 |
| tax_fund | 237.5 | 67.8 | 1787.4 |
| road_spend | 109.6 | 10.5 | 634.9 |
| fire_spend | 59.9 | 0.9 | 489.5 |
| police_spend | 97.9 | 0.8 | 646.2 |
| powered_zones | 2.4 | 0.0 | 0.5 |
| unpowered_zones | 2.0 | 0.0 | 4.8 |
| coal_plants | 0.1 | 0.0 | 0.2 |
| nuclear_plants | 0.2 | 0.0 | 0.1 |
| road_total | 54.5 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.047 | 0.845 |
| traffic | 1.095 | 0.765 |
| pollution | 1.455 | 0.703 |
| land_value | 0.664 | 0.336 |
| crime | 0.993 | 0.580 |
| rate_of_growth | 1.047 | 0.835 |
| fire_coverage | 0.989 | 0.125 |
| police_coverage | 0.812 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.470 | 0.262 | 0.336 | 0.313 to 0.358 | 0.356 | 0.131 | 0.191 | 0.157 to 0.229 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.474 | 0.003 | 0.006 |
| all plans | 12 | 0.333 | 0.037 | 0.053 |
| all plans | 24 | 0.391 | 0.073 | 0.067 |
| state-reading plans | 1 | 0.471 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.333 | 0.041 | 0.051 |
| state-reading plans | 24 | 0.404 | 0.081 | 0.065 |
| open-loop plans | 1 | 0.462 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.439 | 0.030 | 0.062 |
| open-loop plans | 24 | 0.546 | 0.055 | 0.078 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -254.78 |
| tile_cat | -34.18 |
| flags | -22.27 |
| power | -4.27 |
| half | -2557.11 |
| eighth | -37.07 |
| scalars_s2 | -5.27 |
| build_cost | -0.88 |
| scalars | -34.02 |
| ledger | -41.39 |
| bk | -70.15 |
| sc_res_pop | -1.51 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.15 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.04 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.36 |
| sc_res_valve | -1.61 |
| sc_com_valve | -2.97 |
| sc_ind_valve | -2.18 |
| sc_score | -8.30 |
| sc_funds | -3.59 |
| sc_tax_fund | -3.06 |
| sc_road_spend | -5.03 |
| sc_fire_spend | -0.92 |
| sc_police_spend | -1.10 |
| lg_sprite_cycle | -1.37 |
| lg_total_pop | -3.90 |
| lg_res_hist0 | -5.90 |
| lg_res_hist1 | -2.04 |
| lg_com_hist0 | -0.43 |
| lg_com_hist1 | -0.33 |
| lg_ind_hist0 | -1.24 |
| lg_ind_hist1 | -0.67 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.36 |
| lg_need_church | -0.21 |
| lg_road_fund | -3.02 |
| lg_police_fund | -0.92 |
| lg_fire_fund | -0.45 |
| lg_auto_budget | -0.06 |
| lg_fire_pop | -0.12 |
| lg_city_center_x | -0.15 |
| lg_city_center_y | -0.16 |
| lg_pollution_max_x | -7.22 |
| lg_pollution_max_y | -7.53 |
| lg_flood_count | -0.03 |
| lg_abs_dist | -5.25 |
| terrain | -6.44 |
| com_rate | -8.08 |
| kl | 12.75 |
| elbo | -3013.26 |
