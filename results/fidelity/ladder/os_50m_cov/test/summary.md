## os_50m_cov_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "41fa87fa081a5666", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.301 | 0.283 | 0.292 | 0.272 to 0.310 | 0.189 | 0.165 | 0.176 | 0.148 to 0.206 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.310 | 0.291 | 0.300 | 0.279 to 0.320 | 0.204 | 0.177 | 0.190 | 0.157 to 0.224 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.270 | 0.255 | 0.262 | 0.243 to 0.281 | 0.142 | 0.127 | 0.134 | 0.110 to 0.156 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.530 | 0.203 | 0.006 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.376 / 0.393 |
| all plans | 700 | 12 | 0.376 | 0.154 | 0.056 / 0.003 / 0.400 | 0.049 / 0.027 / 0.112 | 0.375 / 0.423 |
| all plans | 700 | 24 | 0.446 | 0.176 | 0.092 / 0.005 / 0.614 | 0.076 / 0.039 / 0.159 | 0.341 / 0.405 |
| state-reading plans | 527 | 1 | 0.529 | 0.201 | 0.009 / 0.000 / 0.018 | 0.008 / 0.006 / 0.008 | 0.421 / 0.431 |
| state-reading plans | 527 | 12 | 0.378 | 0.162 | 0.066 / 0.003 / 0.505 | 0.048 / 0.028 / 0.106 | 0.400 / 0.442 |
| state-reading plans | 527 | 24 | 0.461 | 0.194 | 0.111 / 0.005 / 0.776 | 0.076 / 0.039 / 0.155 | 0.359 / 0.415 |
| open-loop plans | 173 | 1 | 0.596 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.158 / 0.208 |
| open-loop plans | 173 | 12 | 0.576 | 0.133 | 0.029 / 0.002 / 0.054 | 0.051 / 0.026 / 0.133 | 0.280 / 0.349 |
| open-loop plans | 173 | 24 | 0.812 | 0.128 | 0.052 / 0.005 / 0.111 | 0.075 / 0.039 / 0.168 | 0.278 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.522 | 0.189 | 0.006 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.385 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.382 | 0.152 | 0.060 / 0.002 / 0.433 | 0.051 / 0.030 / 0.105 | 0.379 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.448 | 0.169 | 0.104 / 0.005 / 0.668 | 0.083 / 0.043 / 0.156 | 0.345 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1763 | 0.857 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2918 | 0.914 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2124.9000 | 0.658 |
| funds_mae_12m | 5673.7400 | 40.0829 | 826.7866 | 0.860 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 202.0202 | 0.812 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 535.6361 | 0.873 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 335.8225 | 0.891 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0489 | 0.742 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0563 | 0.866 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3749 | 0.887 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3668 | 0.860 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3677.1071 | 0.636 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1101.3843 | 0.858 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 281.5721 | 0.807 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 667.2791 | 0.678 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 559.6246 | 0.783 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0761 | 0.693 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0923 | 0.857 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3407 | 0.841 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3349 | 0.826 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1101.4 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 281.6 | 160.2 | 787.9 |
| com_valve | 667.3 | 507.1 | 1004.7 |
| ind_valve | 559.6 | 454.2 | 939.2 |
| pop | 3677.1 | 1749.1 | 7044.7 |
| res_pop | 78.5 | 37.1 | 135.5 |
| com_pop | 8.1 | 5.0 | 12.3 |
| ind_pop | 10.6 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 68.9 | 26.8 | 89.0 |
| tax_fund | 145.5 | 53.9 | 1490.0 |
| road_spend | 72.7 | 9.0 | 638.2 |
| fire_spend | 30.0 | 1.3 | 473.1 |
| police_spend | 48.4 | 3.4 | 618.5 |
| powered_zones | 6.0 | 0.9 | 9.0 |
| unpowered_zones | 4.4 | 0.8 | 7.1 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 47.6 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1135.8 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 255.2 | 128.0 | 549.2 |
| com_valve | 713.5 | 545.4 | 967.3 |
| ind_valve | 621.0 | 502.9 | 866.6 |
| pop | 3750.9 | 1820.5 | 6670.1 |
| res_pop | 78.4 | 37.8 | 127.8 |
| com_pop | 8.1 | 5.0 | 11.7 |
| ind_pop | 11.0 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 69.6 | 27.8 | 83.7 |
| tax_fund | 138.6 | 49.4 | 1392.4 |
| road_spend | 66.5 | 8.4 | 639.3 |
| fire_spend | 28.2 | 1.4 | 467.7 |
| police_spend | 47.5 | 4.3 | 609.4 |
| powered_zones | 6.6 | 1.2 | 11.7 |
| unpowered_zones | 5.2 | 1.1 | 7.9 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.4 |
| road_total | 47.7 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 996.6 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 361.8 | 258.1 | 1515.1 |
| com_valve | 526.5 | 390.3 | 1118.5 |
| ind_valve | 372.6 | 305.8 | 1160.1 |
| pop | 3452.3 | 1531.7 | 8185.8 |
| res_pop | 78.7 | 35.0 | 158.8 |
| com_pop | 7.9 | 4.9 | 14.2 |
| ind_pop | 9.5 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 66.8 | 23.7 | 105.2 |
| tax_fund | 166.7 | 67.8 | 1787.4 |
| road_spend | 91.4 | 10.5 | 634.9 |
| fire_spend | 35.4 | 0.9 | 489.5 |
| police_spend | 51.4 | 0.8 | 646.2 |
| powered_zones | 4.0 | 0.0 | 0.5 |
| unpowered_zones | 2.0 | 0.0 | 4.8 |
| coal_plants | 0.1 | 0.0 | 0.2 |
| nuclear_plants | 0.1 | 0.0 | 0.1 |
| road_total | 47.3 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.056 | 0.845 |
| traffic | 1.024 | 0.765 |
| pollution | 1.552 | 0.703 |
| land_value | 0.639 | 0.336 |
| crime | 1.022 | 0.580 |
| rate_of_growth | 1.008 | 0.835 |
| fire_coverage | 1.197 | 0.125 |
| police_coverage | 1.061 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.538 | 0.261 | 0.351 | 0.329 to 0.371 | 0.424 | 0.138 | 0.208 | 0.173 to 0.246 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.410 | 0.003 | 0.006 |
| all plans | 12 | 0.294 | 0.048 | 0.041 |
| all plans | 24 | 0.360 | 0.105 | 0.060 |
| state-reading plans | 1 | 0.408 | 0.004 | 0.006 |
| state-reading plans | 12 | 0.297 | 0.053 | 0.041 |
| state-reading plans | 24 | 0.374 | 0.128 | 0.060 |
| open-loop plans | 1 | 0.481 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.445 | 0.036 | 0.044 |
| open-loop plans | 24 | 0.674 | 0.060 | 0.062 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -210.67 |
| tile_cat | -28.51 |
| flags | -14.37 |
| power | -2.65 |
| half | -2280.31 |
| eighth | -32.96 |
| scalars_s2 | -5.16 |
| build_cost | -1.05 |
| scalars | -12.24 |
| ledger | -13.89 |
| bk | -20.97 |
| sc_res_pop | -1.48 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.14 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.35 |
| sc_res_valve | -1.02 |
| sc_com_valve | -2.05 |
| sc_ind_valve | -1.10 |
| sc_score | -0.50 |
| sc_funds | -1.03 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.59 |
| sc_fire_spend | -0.17 |
| sc_police_spend | -0.17 |
| lg_sprite_cycle | -1.10 |
| lg_total_pop | -1.60 |
| lg_res_hist0 | -0.28 |
| lg_res_hist1 | -0.71 |
| lg_com_hist0 | -0.07 |
| lg_com_hist1 | -0.38 |
| lg_ind_hist0 | -0.09 |
| lg_ind_hist1 | -0.28 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.62 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.11 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.01 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.12 |
| lg_pollution_max_y | -2.91 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -4.52 |
| com_rate | -1.57 |
| kl | 14.28 |
| elbo | -2617.02 |
