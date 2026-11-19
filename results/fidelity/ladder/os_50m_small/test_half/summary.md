## os_50m_small_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.279 | 0.282 | 0.280 | 0.260 to 0.299 | 0.168 | 0.164 | 0.166 | 0.140 to 0.196 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.288 | 0.291 | 0.289 | 0.267 to 0.311 | 0.182 | 0.176 | 0.179 | 0.149 to 0.214 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.247 | 0.251 | 0.249 | 0.228 to 0.269 | 0.124 | 0.124 | 0.124 | 0.102 to 0.147 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.776 | 0.203 | 0.006 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.359 / 0.393 |
| all plans | 700 | 12 | 0.525 | 0.154 | 0.050 / 0.003 / 0.400 | 0.040 / 0.027 / 0.112 | 0.376 / 0.423 |
| all plans | 700 | 24 | 0.548 | 0.176 | 0.071 / 0.005 / 0.614 | 0.063 / 0.039 / 0.159 | 0.344 / 0.405 |
| state-reading plans | 527 | 1 | 0.688 | 0.201 | 0.009 / 0.000 / 0.018 | 0.008 / 0.006 / 0.008 | 0.403 / 0.431 |
| state-reading plans | 527 | 12 | 0.532 | 0.162 | 0.063 / 0.003 / 0.505 | 0.040 / 0.028 / 0.106 | 0.402 / 0.442 |
| state-reading plans | 527 | 24 | 0.568 | 0.194 | 0.089 / 0.005 / 0.776 | 0.064 / 0.039 / 0.155 | 0.362 / 0.415 |
| open-loop plans | 173 | 1 | 0.796 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.152 / 0.208 |
| open-loop plans | 173 | 12 | 0.659 | 0.133 | 0.022 / 0.002 / 0.054 | 0.039 / 0.026 / 0.133 | 0.282 / 0.349 |
| open-loop plans | 173 | 24 | 0.781 | 0.128 | 0.031 / 0.005 / 0.111 | 0.060 / 0.039 / 0.168 | 0.282 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.682 | 0.189 | 0.007 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.365 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.528 | 0.152 | 0.052 / 0.002 / 0.433 | 0.041 / 0.030 / 0.105 | 0.378 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.536 | 0.169 | 0.073 / 0.005 / 0.668 | 0.067 / 0.043 / 0.156 | 0.348 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1661 | 0.807 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2803 | 0.878 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 1679.8214 | 0.809 |
| funds_mae_12m | 5673.7400 | 40.0829 | 880.8552 | 0.851 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 205.1205 | 0.806 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 501.5034 | 0.918 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 311.7859 | 0.928 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0396 | 0.851 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0502 | 0.881 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3765 | 0.891 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3673 | 0.861 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 2830.6786 | 0.796 |
| funds_mae_24m | 7303.4900 | 72.8329 | 980.9784 | 0.874 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 265.0366 | 0.833 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 615.4523 | 0.782 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 533.5209 | 0.836 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0634 | 0.799 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0712 | 0.892 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3444 | 0.850 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3380 | 0.834 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 981.0 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 265.0 | 160.2 | 787.9 |
| com_valve | 615.5 | 507.1 | 1004.7 |
| ind_valve | 533.5 | 454.2 | 939.2 |
| pop | 2830.7 | 1749.1 | 7044.7 |
| res_pop | 62.7 | 37.1 | 135.5 |
| com_pop | 6.8 | 5.0 | 12.3 |
| ind_pop | 8.7 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 45.8 | 26.8 | 89.0 |
| tax_fund | 176.4 | 53.9 | 1490.0 |
| road_spend | 103.7 | 9.0 | 638.2 |
| fire_spend | 55.3 | 1.3 | 473.1 |
| police_spend | 88.6 | 3.4 | 618.5 |
| powered_zones | 7.6 | 0.9 | 9.0 |
| unpowered_zones | 5.2 | 0.8 | 7.1 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 57.9 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1022.5 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 235.4 | 128.0 | 549.2 |
| com_valve | 663.5 | 545.4 | 967.3 |
| ind_valve | 596.0 | 502.9 | 866.6 |
| pop | 2937.2 | 1820.5 | 6670.1 |
| res_pop | 64.5 | 37.8 | 127.8 |
| com_pop | 7.0 | 5.0 | 11.7 |
| ind_pop | 9.0 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 48.1 | 27.8 | 83.7 |
| tax_fund | 161.4 | 49.4 | 1392.4 |
| road_spend | 102.5 | 8.4 | 639.3 |
| fire_spend | 53.5 | 1.4 | 467.7 |
| police_spend | 86.4 | 4.3 | 609.4 |
| powered_zones | 9.1 | 1.2 | 11.7 |
| unpowered_zones | 6.1 | 1.1 | 7.9 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 57.7 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 854.3 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 355.2 | 258.1 | 1515.1 |
| com_valve | 469.1 | 390.3 | 1118.5 |
| ind_valve | 343.2 | 305.8 | 1160.1 |
| pop | 2506.3 | 1531.7 | 8185.8 |
| res_pop | 57.1 | 35.0 | 158.8 |
| com_pop | 6.3 | 4.9 | 14.2 |
| ind_pop | 7.6 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 38.6 | 23.7 | 105.2 |
| tax_fund | 221.8 | 67.8 | 1787.4 |
| road_spend | 107.5 | 10.5 | 634.9 |
| fire_spend | 60.7 | 0.9 | 489.5 |
| police_spend | 95.2 | 0.8 | 646.2 |
| powered_zones | 3.2 | 0.0 | 0.5 |
| unpowered_zones | 2.5 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.3 | 0.0 | 0.1 |
| road_total | 58.4 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.025 | 0.845 |
| traffic | 1.045 | 0.765 |
| pollution | 1.455 | 0.703 |
| land_value | 0.666 | 0.336 |
| crime | 0.984 | 0.580 |
| rate_of_growth | 1.024 | 0.835 |
| fire_coverage | 1.001 | 0.125 |
| police_coverage | 0.854 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.535 | 0.259 | 0.349 | 0.326 to 0.370 | 0.505 | 0.129 | 0.206 | 0.167 to 0.248 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.566 | 0.003 | 0.005 |
| all plans | 12 | 0.349 | 0.035 | 0.034 |
| all plans | 24 | 0.374 | 0.058 | 0.052 |
| state-reading plans | 1 | 0.481 | 0.004 | 0.005 |
| state-reading plans | 12 | 0.358 | 0.041 | 0.035 |
| state-reading plans | 24 | 0.397 | 0.078 | 0.053 |
| open-loop plans | 1 | 0.490 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.417 | 0.022 | 0.031 |
| open-loop plans | 24 | 0.469 | 0.035 | 0.047 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -244.55 |
| tile_cat | -32.41 |
| flags | -16.66 |
| power | -2.72 |
| half | -2501.40 |
| eighth | -36.90 |
| scalars_s2 | -6.74 |
| build_cost | -1.26 |
| scalars | -16.86 |
| ledger | -19.92 |
| bk | -30.05 |
| sc_res_pop | -2.16 |
| sc_com_pop | -0.36 |
| sc_ind_pop | -0.38 |
| sc_powered_zones | -0.15 |
| sc_unpowered_zones | -0.22 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.44 |
| sc_res_valve | -1.23 |
| sc_com_valve | -2.31 |
| sc_ind_valve | -1.72 |
| sc_score | -1.12 |
| sc_funds | -1.35 |
| sc_tax_fund | -0.81 |
| sc_road_spend | -1.04 |
| sc_fire_spend | -0.27 |
| sc_police_spend | -0.28 |
| lg_sprite_cycle | -0.85 |
| lg_total_pop | -2.36 |
| lg_res_hist0 | -1.31 |
| lg_res_hist1 | -0.93 |
| lg_com_hist0 | -0.36 |
| lg_com_hist1 | -0.30 |
| lg_ind_hist0 | -0.41 |
| lg_ind_hist1 | -0.50 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.13 |
| lg_need_church | -0.11 |
| lg_road_fund | -1.03 |
| lg_police_fund | -0.18 |
| lg_fire_fund | -0.16 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.11 |
| lg_city_center_x | -0.29 |
| lg_city_center_y | -0.18 |
| lg_pollution_max_x | -3.82 |
| lg_pollution_max_y | -4.07 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.77 |
| terrain | -6.41 |
| com_rate | -3.84 |
| kl | 10.12 |
| elbo | -2893.05 |
