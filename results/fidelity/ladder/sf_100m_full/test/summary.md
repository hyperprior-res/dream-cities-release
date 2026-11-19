## sf_100m_full_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.272 | 0.288 | 0.280 | 0.260 to 0.298 | 0.161 | 0.175 | 0.168 | 0.143 to 0.194 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.281 | 0.296 | 0.288 | 0.267 to 0.309 | 0.173 | 0.187 | 0.180 | 0.151 to 0.211 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.241 | 0.260 | 0.250 | 0.230 to 0.269 | 0.122 | 0.136 | 0.129 | 0.108 to 0.149 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.521 | 0.203 | 0.001 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.369 / 0.393 |
| all plans | 700 | 12 | 0.412 | 0.154 | 0.027 / 0.003 / 0.400 | 0.044 / 0.027 / 0.112 | 0.338 / 0.423 |
| all plans | 700 | 24 | 0.512 | 0.176 | 0.058 / 0.005 / 0.614 | 0.069 / 0.039 / 0.159 | 0.302 / 0.405 |
| state-reading plans | 527 | 1 | 0.507 | 0.201 | 0.002 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.413 / 0.431 |
| state-reading plans | 527 | 12 | 0.407 | 0.162 | 0.030 / 0.003 / 0.505 | 0.044 / 0.028 / 0.106 | 0.362 / 0.442 |
| state-reading plans | 527 | 24 | 0.508 | 0.194 | 0.061 / 0.005 / 0.776 | 0.066 / 0.039 / 0.155 | 0.323 / 0.415 |
| open-loop plans | 173 | 1 | 0.548 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.158 / 0.208 |
| open-loop plans | 173 | 12 | 0.676 | 0.133 | 0.021 / 0.002 / 0.054 | 0.043 / 0.026 / 0.133 | 0.251 / 0.349 |
| open-loop plans | 173 | 24 | 1.021 | 0.128 | 0.048 / 0.005 / 0.111 | 0.076 / 0.039 / 0.168 | 0.233 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.515 | 0.189 | 0.001 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.379 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.410 | 0.152 | 0.030 / 0.002 / 0.433 | 0.045 / 0.030 / 0.105 | 0.342 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.498 | 0.169 | 0.063 / 0.005 / 0.668 | 0.068 / 0.043 / 0.156 | 0.307 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1676 | 0.815 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2797 | 0.876 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 1836.3107 | 0.756 |
| funds_mae_12m | 5673.7400 | 40.0829 | 558.6159 | 0.908 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 211.8757 | 0.795 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 550.4871 | 0.853 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 338.3982 | 0.887 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0441 | 0.798 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0271 | 0.939 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3380 | 0.800 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3388 | 0.795 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3256.8929 | 0.715 |
| funds_mae_24m | 7303.4900 | 72.8329 | 799.6259 | 0.899 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 347.5532 | 0.702 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 684.5861 | 0.643 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 619.8805 | 0.658 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0688 | 0.754 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0577 | 0.914 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3021 | 0.746 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3022 | 0.745 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 799.6 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 347.6 | 160.2 | 787.9 |
| com_valve | 684.6 | 507.1 | 1004.7 |
| ind_valve | 619.9 | 454.2 | 939.2 |
| pop | 3256.9 | 1749.1 | 7044.7 |
| res_pop | 79.5 | 37.1 | 135.5 |
| com_pop | 7.6 | 5.0 | 12.3 |
| ind_pop | 10.2 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 63.1 | 26.8 | 89.0 |
| tax_fund | 157.6 | 53.9 | 1490.0 |
| road_spend | 81.2 | 9.0 | 638.2 |
| fire_spend | 39.1 | 1.3 | 473.1 |
| police_spend | 57.1 | 3.4 | 618.5 |
| powered_zones | 6.6 | 0.9 | 9.0 |
| unpowered_zones | 5.1 | 0.8 | 7.1 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 50.8 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 743.9 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 279.4 | 128.0 | 549.2 |
| com_valve | 729.1 | 545.4 | 967.3 |
| ind_valve | 682.0 | 502.9 | 866.6 |
| pop | 3197.6 | 1820.5 | 6670.1 |
| res_pop | 76.1 | 37.8 | 127.8 |
| com_pop | 7.5 | 5.0 | 11.7 |
| ind_pop | 10.2 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 64.2 | 27.8 | 83.7 |
| tax_fund | 144.5 | 49.4 | 1392.4 |
| road_spend | 76.8 | 8.4 | 639.3 |
| fire_spend | 36.1 | 1.4 | 467.7 |
| police_spend | 55.2 | 4.3 | 609.4 |
| powered_zones | 7.3 | 1.2 | 11.7 |
| unpowered_zones | 5.7 | 1.1 | 7.9 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.4 |
| road_total | 50.5 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 969.5 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 555.1 | 258.1 | 1515.1 |
| com_valve | 548.9 | 390.3 | 1118.5 |
| ind_valve | 430.6 | 305.8 | 1160.1 |
| pop | 3437.6 | 1531.7 | 8185.8 |
| res_pop | 89.9 | 35.0 | 158.8 |
| com_pop | 7.8 | 4.9 | 14.2 |
| ind_pop | 10.2 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 59.8 | 23.7 | 105.2 |
| tax_fund | 197.7 | 67.8 | 1787.4 |
| road_spend | 94.8 | 10.5 | 634.9 |
| fire_spend | 48.3 | 0.9 | 489.5 |
| police_spend | 62.7 | 0.8 | 646.2 |
| powered_zones | 4.4 | 0.0 | 0.5 |
| unpowered_zones | 3.2 | 0.0 | 4.8 |
| coal_plants | 0.3 | 0.0 | 0.2 |
| nuclear_plants | 0.4 | 0.0 | 0.1 |
| road_total | 51.5 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.187 | 0.845 |
| traffic | 0.980 | 0.765 |
| pollution | 1.731 | 0.703 |
| land_value | 0.701 | 0.336 |
| crime | 1.124 | 0.580 |
| rate_of_growth | 1.142 | 0.835 |
| fire_coverage | 1.067 | 0.125 |
| police_coverage | 0.926 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.542 | 0.264 | 0.355 | 0.333 to 0.375 | 0.436 | 0.143 | 0.215 | 0.178 to 0.254 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.424 | 0.001 | 0.006 |
| all plans | 12 | 0.298 | 0.026 | 0.035 |
| all plans | 24 | 0.387 | 0.064 | 0.058 |
| state-reading plans | 1 | 0.406 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.295 | 0.027 | 0.035 |
| state-reading plans | 24 | 0.388 | 0.069 | 0.057 |
| open-loop plans | 1 | 0.462 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.451 | 0.025 | 0.036 |
| open-loop plans | 24 | 0.724 | 0.060 | 0.059 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -205.30 |
| tile_cat | -28.56 |
| flags | -13.80 |
| power | -1.97 |
| half | -2221.17 |
| eighth | -31.95 |
| scalars_s2 | -5.13 |
| build_cost | -0.78 |
| scalars | -12.46 |
| ledger | -13.52 |
| bk | -20.85 |
| sc_res_pop | -1.45 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.15 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.36 |
| sc_res_valve | -1.01 |
| sc_com_valve | -2.04 |
| sc_ind_valve | -1.07 |
| sc_score | -0.61 |
| sc_funds | -1.00 |
| sc_tax_fund | -0.47 |
| sc_road_spend | -0.77 |
| sc_fire_spend | -0.14 |
| sc_police_spend | -0.21 |
| lg_sprite_cycle | -0.84 |
| lg_total_pop | -1.43 |
| lg_res_hist0 | -0.24 |
| lg_res_hist1 | -0.53 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.28 |
| lg_ind_hist0 | -0.04 |
| lg_ind_hist1 | -0.11 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.80 |
| lg_police_fund | -0.16 |
| lg_fire_fund | -0.17 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.01 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.13 |
| lg_pollution_max_y | -3.24 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -4.52 |
| com_rate | -1.96 |
| kl | 15.97 |
| elbo | -2551.96 |
