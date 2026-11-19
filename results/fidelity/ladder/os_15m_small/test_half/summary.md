## os_15m_small_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.282 | 0.277 | 0.280 | 0.260 to 0.298 | 0.174 | 0.159 | 0.166 | 0.140 to 0.195 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.290 | 0.285 | 0.287 | 0.266 to 0.307 | 0.189 | 0.172 | 0.180 | 0.149 to 0.213 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.255 | 0.251 | 0.253 | 0.232 to 0.273 | 0.127 | 0.116 | 0.121 | 0.098 to 0.143 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.834 | 0.203 | 0.007 / 0.000 / 0.013 | 0.009 / 0.006 / 0.007 | 0.364 / 0.393 |
| all plans | 700 | 12 | 0.538 | 0.154 | 0.056 / 0.003 / 0.400 | 0.050 / 0.027 / 0.112 | 0.370 / 0.423 |
| all plans | 700 | 24 | 0.576 | 0.176 | 0.080 / 0.005 / 0.614 | 0.072 / 0.039 / 0.159 | 0.338 / 0.405 |
| state-reading plans | 527 | 1 | 0.783 | 0.201 | 0.010 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.408 / 0.431 |
| state-reading plans | 527 | 12 | 0.543 | 0.162 | 0.068 / 0.003 / 0.505 | 0.049 / 0.028 / 0.106 | 0.396 / 0.442 |
| state-reading plans | 527 | 24 | 0.593 | 0.194 | 0.102 / 0.005 / 0.776 | 0.070 / 0.039 / 0.155 | 0.356 / 0.415 |
| open-loop plans | 173 | 1 | 1.024 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.153 / 0.208 |
| open-loop plans | 173 | 12 | 0.700 | 0.133 | 0.023 / 0.002 / 0.054 | 0.052 / 0.026 / 0.133 | 0.274 / 0.349 |
| open-loop plans | 173 | 24 | 0.793 | 0.128 | 0.034 / 0.005 / 0.111 | 0.078 / 0.039 / 0.168 | 0.272 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.790 | 0.189 | 0.008 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.374 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.547 | 0.152 | 0.061 / 0.002 / 0.433 | 0.051 / 0.030 / 0.105 | 0.372 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.571 | 0.169 | 0.091 / 0.005 / 0.668 | 0.078 / 0.043 / 0.156 | 0.343 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1660 | 0.807 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2798 | 0.876 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2025.8821 | 0.692 |
| funds_mae_12m | 5673.7400 | 40.0829 | 945.8507 | 0.839 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 218.8954 | 0.782 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 539.2446 | 0.868 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 346.8559 | 0.874 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0495 | 0.735 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0558 | 0.867 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3699 | 0.875 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3627 | 0.851 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3227.2000 | 0.721 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1112.0029 | 0.856 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 341.7902 | 0.711 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 707.3727 | 0.597 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 678.5350 | 0.537 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0722 | 0.726 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0801 | 0.877 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3380 | 0.835 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3332 | 0.822 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1112.0 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 341.8 | 160.2 | 787.9 |
| com_valve | 707.4 | 507.1 | 1004.7 |
| ind_valve | 678.5 | 454.2 | 939.2 |
| pop | 3227.2 | 1749.1 | 7044.7 |
| res_pop | 66.3 | 37.1 | 135.5 |
| com_pop | 7.6 | 5.0 | 12.3 |
| ind_pop | 11.7 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.3 | 26.8 | 89.0 |
| tax_fund | 174.9 | 53.9 | 1490.0 |
| road_spend | 94.9 | 9.0 | 638.2 |
| fire_spend | 58.1 | 1.3 | 473.1 |
| police_spend | 98.6 | 3.4 | 618.5 |
| powered_zones | 7.5 | 0.9 | 9.0 |
| unpowered_zones | 5.3 | 0.8 | 7.1 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 59.0 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1104.5 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 282.4 | 128.0 | 549.2 |
| com_valve | 751.9 | 545.4 | 967.3 |
| ind_valve | 753.1 | 502.9 | 866.6 |
| pop | 3240.7 | 1820.5 | 6670.1 |
| res_pop | 66.9 | 37.8 | 127.8 |
| com_pop | 7.5 | 5.0 | 11.7 |
| ind_pop | 11.9 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 52.2 | 27.8 | 83.7 |
| tax_fund | 161.9 | 49.4 | 1392.4 |
| road_spend | 93.6 | 8.4 | 639.3 |
| fire_spend | 57.6 | 1.4 | 467.7 |
| police_spend | 99.6 | 4.3 | 609.4 |
| powered_zones | 9.1 | 1.2 | 11.7 |
| unpowered_zones | 6.1 | 1.1 | 7.9 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 58.7 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1135.0 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 522.7 | 258.1 | 1515.1 |
| com_valve | 571.7 | 390.3 | 1118.5 |
| ind_valve | 451.4 | 305.8 | 1160.1 |
| pop | 3185.9 | 1531.7 | 8185.8 |
| res_pop | 64.4 | 35.0 | 158.8 |
| com_pop | 7.7 | 4.9 | 14.2 |
| ind_pop | 11.1 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 40.7 | 23.7 | 105.2 |
| tax_fund | 214.2 | 67.8 | 1787.4 |
| road_spend | 98.7 | 10.5 | 634.9 |
| fire_spend | 59.9 | 0.9 | 489.5 |
| police_spend | 95.6 | 0.8 | 646.2 |
| powered_zones | 2.7 | 0.0 | 0.5 |
| unpowered_zones | 2.8 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.3 | 0.0 | 0.1 |
| road_total | 59.9 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.042 | 0.845 |
| traffic | 1.082 | 0.765 |
| pollution | 1.549 | 0.703 |
| land_value | 0.672 | 0.336 |
| crime | 1.013 | 0.580 |
| rate_of_growth | 1.027 | 0.835 |
| fire_coverage | 1.140 | 0.125 |
| police_coverage | 0.832 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.603 | 0.250 | 0.354 | 0.329 to 0.375 | 0.742 | 0.122 | 0.209 | 0.170 to 0.253 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.628 | 0.003 | 0.006 |
| all plans | 12 | 0.363 | 0.041 | 0.046 |
| all plans | 24 | 0.405 | 0.074 | 0.062 |
| state-reading plans | 1 | 0.578 | 0.004 | 0.006 |
| state-reading plans | 12 | 0.367 | 0.049 | 0.043 |
| state-reading plans | 24 | 0.421 | 0.092 | 0.060 |
| open-loop plans | 1 | 0.610 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.466 | 0.020 | 0.050 |
| open-loop plans | 24 | 0.523 | 0.037 | 0.071 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -237.54 |
| tile_cat | -32.41 |
| flags | -17.86 |
| power | -2.47 |
| half | -2508.72 |
| eighth | -37.13 |
| scalars_s2 | -6.73 |
| build_cost | -1.26 |
| scalars | -16.28 |
| ledger | -17.32 |
| bk | -26.87 |
| sc_res_pop | -2.16 |
| sc_com_pop | -0.36 |
| sc_ind_pop | -0.38 |
| sc_powered_zones | -0.15 |
| sc_unpowered_zones | -0.22 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.43 |
| sc_res_valve | -1.15 |
| sc_com_valve | -2.27 |
| sc_ind_valve | -1.65 |
| sc_score | -0.94 |
| sc_funds | -1.32 |
| sc_tax_fund | -0.75 |
| sc_road_spend | -1.00 |
| sc_fire_spend | -0.21 |
| sc_police_spend | -0.26 |
| lg_sprite_cycle | -0.85 |
| lg_total_pop | -2.18 |
| lg_res_hist0 | -0.96 |
| lg_res_hist1 | -0.48 |
| lg_com_hist0 | -0.20 |
| lg_com_hist1 | -0.12 |
| lg_ind_hist0 | -0.27 |
| lg_ind_hist1 | -0.18 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.14 |
| lg_need_church | -0.10 |
| lg_road_fund | -1.00 |
| lg_police_fund | -0.16 |
| lg_fire_fund | -0.12 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.10 |
| lg_city_center_x | -0.20 |
| lg_city_center_y | -0.15 |
| lg_pollution_max_x | -3.67 |
| lg_pollution_max_y | -3.68 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.71 |
| terrain | -7.12 |
| com_rate | -5.31 |
| kl | 9.96 |
| elbo | -2893.38 |
