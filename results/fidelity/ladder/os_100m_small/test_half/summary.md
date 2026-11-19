## os_100m_small_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.290 | 0.282 | 0.286 | 0.265 to 0.307 | 0.180 | 0.164 | 0.171 | 0.143 to 0.201 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.297 | 0.289 | 0.293 | 0.270 to 0.314 | 0.192 | 0.176 | 0.184 | 0.151 to 0.219 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.268 | 0.257 | 0.262 | 0.240 to 0.283 | 0.139 | 0.125 | 0.132 | 0.110 to 0.154 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.676 | 0.203 | 0.006 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.372 / 0.393 |
| all plans | 700 | 12 | 0.533 | 0.154 | 0.046 / 0.003 / 0.400 | 0.045 / 0.027 / 0.112 | 0.380 / 0.423 |
| all plans | 700 | 24 | 0.566 | 0.176 | 0.060 / 0.005 / 0.614 | 0.070 / 0.039 / 0.159 | 0.348 / 0.405 |
| state-reading plans | 527 | 1 | 0.660 | 0.201 | 0.010 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.417 / 0.431 |
| state-reading plans | 527 | 12 | 0.538 | 0.162 | 0.059 / 0.003 / 0.505 | 0.044 / 0.028 / 0.106 | 0.406 / 0.442 |
| state-reading plans | 527 | 24 | 0.583 | 0.194 | 0.082 / 0.005 / 0.776 | 0.069 / 0.039 / 0.155 | 0.366 / 0.415 |
| open-loop plans | 173 | 1 | 0.721 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.156 / 0.208 |
| open-loop plans | 173 | 12 | 0.677 | 0.133 | 0.016 / 0.002 / 0.054 | 0.046 / 0.026 / 0.133 | 0.284 / 0.349 |
| open-loop plans | 173 | 24 | 0.823 | 0.128 | 0.025 / 0.005 / 0.111 | 0.070 / 0.039 / 0.168 | 0.285 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.655 | 0.189 | 0.007 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.380 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.550 | 0.152 | 0.050 / 0.002 / 0.433 | 0.045 / 0.030 / 0.105 | 0.383 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.566 | 0.169 | 0.063 / 0.005 / 0.668 | 0.074 / 0.043 / 0.156 | 0.353 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1714 | 0.833 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2861 | 0.896 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 1915.1750 | 0.729 |
| funds_mae_12m | 5673.7400 | 40.0829 | 791.9813 | 0.867 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 214.1846 | 0.790 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 514.4512 | 0.901 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 342.4530 | 0.881 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0450 | 0.788 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0465 | 0.890 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3804 | 0.900 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3702 | 0.868 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3148.0857 | 0.736 |
| funds_mae_24m | 7303.4900 | 72.8329 | 889.3357 | 0.887 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 285.8396 | 0.800 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 617.0411 | 0.779 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 575.3341 | 0.750 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0696 | 0.748 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0604 | 0.909 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3485 | 0.860 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3412 | 0.842 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 889.3 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 285.8 | 160.2 | 787.9 |
| com_valve | 617.0 | 507.1 | 1004.7 |
| ind_valve | 575.3 | 454.2 | 939.2 |
| pop | 3148.1 | 1749.1 | 7044.7 |
| res_pop | 68.5 | 37.1 | 135.5 |
| com_pop | 6.8 | 5.0 | 12.3 |
| ind_pop | 10.5 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 47.3 | 26.8 | 89.0 |
| tax_fund | 197.9 | 53.9 | 1490.0 |
| road_spend | 96.8 | 9.0 | 638.2 |
| fire_spend | 53.2 | 1.3 | 473.1 |
| police_spend | 86.2 | 3.4 | 618.5 |
| powered_zones | 7.9 | 0.9 | 9.0 |
| unpowered_zones | 5.2 | 0.8 | 7.1 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 55.8 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 929.1 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 249.0 | 128.0 | 549.2 |
| com_valve | 662.7 | 545.4 | 967.3 |
| ind_valve | 635.5 | 502.9 | 866.6 |
| pop | 3223.2 | 1820.5 | 6670.1 |
| res_pop | 69.5 | 37.8 | 127.8 |
| com_pop | 6.9 | 5.0 | 11.7 |
| ind_pop | 11.0 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.8 | 27.8 | 83.7 |
| tax_fund | 187.4 | 49.4 | 1392.4 |
| road_spend | 92.4 | 8.4 | 639.3 |
| fire_spend | 51.8 | 1.4 | 467.7 |
| police_spend | 86.9 | 4.3 | 609.4 |
| powered_zones | 9.5 | 1.2 | 11.7 |
| unpowered_zones | 6.0 | 1.1 | 7.9 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 56.3 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 768.3 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 398.0 | 258.1 | 1515.1 |
| com_valve | 477.9 | 390.3 | 1118.5 |
| ind_valve | 392.0 | 305.8 | 1160.1 |
| pop | 2919.3 | 1531.7 | 8185.8 |
| res_pop | 65.5 | 35.0 | 158.8 |
| com_pop | 6.8 | 4.9 | 14.2 |
| ind_pop | 9.1 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 39.6 | 23.7 | 105.2 |
| tax_fund | 229.8 | 67.8 | 1787.4 |
| road_spend | 110.2 | 10.5 | 634.9 |
| fire_spend | 57.2 | 0.9 | 489.5 |
| police_spend | 84.1 | 0.8 | 646.2 |
| powered_zones | 3.1 | 0.0 | 0.5 |
| unpowered_zones | 2.7 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.3 | 0.0 | 0.1 |
| road_total | 54.3 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.030 | 0.845 |
| traffic | 1.022 | 0.765 |
| pollution | 1.414 | 0.703 |
| land_value | 0.649 | 0.336 |
| crime | 0.983 | 0.580 |
| rate_of_growth | 1.039 | 0.835 |
| fire_coverage | 0.846 | 0.125 |
| police_coverage | 0.803 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.512 | 0.263 | 0.347 | 0.324 to 0.369 | 0.454 | 0.132 | 0.204 | 0.166 to 0.245 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.433 | 0.003 | 0.006 |
| all plans | 12 | 0.368 | 0.030 | 0.038 |
| all plans | 24 | 0.403 | 0.049 | 0.057 |
| state-reading plans | 1 | 0.424 | 0.004 | 0.006 |
| state-reading plans | 12 | 0.372 | 0.037 | 0.037 |
| state-reading plans | 24 | 0.420 | 0.062 | 0.058 |
| open-loop plans | 1 | 0.425 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.463 | 0.012 | 0.041 |
| open-loop plans | 24 | 0.546 | 0.020 | 0.056 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -240.45 |
| tile_cat | -32.80 |
| flags | -14.94 |
| power | -1.67 |
| half | -2458.03 |
| eighth | -36.68 |
| scalars_s2 | -6.74 |
| build_cost | -1.27 |
| scalars | -16.84 |
| ledger | -20.57 |
| bk | -30.67 |
| sc_res_pop | -2.16 |
| sc_com_pop | -0.36 |
| sc_ind_pop | -0.38 |
| sc_powered_zones | -0.15 |
| sc_unpowered_zones | -0.22 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.42 |
| sc_res_valve | -1.18 |
| sc_com_valve | -2.35 |
| sc_ind_valve | -1.77 |
| sc_score | -1.06 |
| sc_funds | -1.42 |
| sc_tax_fund | -0.81 |
| sc_road_spend | -1.01 |
| sc_fire_spend | -0.22 |
| sc_police_spend | -0.29 |
| lg_sprite_cycle | -0.87 |
| lg_total_pop | -2.13 |
| lg_res_hist0 | -1.34 |
| lg_res_hist1 | -0.96 |
| lg_com_hist0 | -0.30 |
| lg_com_hist1 | -0.23 |
| lg_ind_hist0 | -0.55 |
| lg_ind_hist1 | -0.52 |
| lg_res_cap | -0.04 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.18 |
| lg_need_church | -0.12 |
| lg_road_fund | -1.03 |
| lg_police_fund | -0.18 |
| lg_fire_fund | -0.14 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.11 |
| lg_city_center_x | -0.21 |
| lg_city_center_y | -0.21 |
| lg_pollution_max_x | -4.29 |
| lg_pollution_max_y | -4.37 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.76 |
| terrain | -6.40 |
| com_rate | -4.24 |
| kl | 12.26 |
| elbo | -2846.16 |
