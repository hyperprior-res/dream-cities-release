## os_15m_full_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.283 | 0.273 | 0.278 | 0.258 to 0.297 | 0.174 | 0.158 | 0.166 | 0.140 to 0.194 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.292 | 0.281 | 0.287 | 0.265 to 0.306 | 0.189 | 0.170 | 0.179 | 0.149 to 0.213 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.252 | 0.246 | 0.249 | 0.230 to 0.267 | 0.128 | 0.119 | 0.123 | 0.103 to 0.143 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.641 | 0.203 | 0.006 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.361 / 0.393 |
| all plans | 700 | 12 | 0.515 | 0.154 | 0.051 / 0.003 / 0.400 | 0.046 / 0.027 / 0.112 | 0.374 / 0.423 |
| all plans | 700 | 24 | 0.550 | 0.176 | 0.072 / 0.005 / 0.614 | 0.072 / 0.039 / 0.159 | 0.346 / 0.405 |
| state-reading plans | 527 | 1 | 0.613 | 0.201 | 0.009 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.405 / 0.431 |
| state-reading plans | 527 | 12 | 0.524 | 0.162 | 0.063 / 0.003 / 0.505 | 0.046 / 0.028 / 0.106 | 0.398 / 0.442 |
| state-reading plans | 527 | 24 | 0.571 | 0.194 | 0.090 / 0.005 / 0.776 | 0.071 / 0.039 / 0.155 | 0.362 / 0.415 |
| open-loop plans | 173 | 1 | 0.817 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.149 / 0.208 |
| open-loop plans | 173 | 12 | 0.628 | 0.133 | 0.020 / 0.002 / 0.054 | 0.047 / 0.026 / 0.133 | 0.283 / 0.349 |
| open-loop plans | 173 | 24 | 0.704 | 0.128 | 0.034 / 0.005 / 0.111 | 0.075 / 0.039 / 0.168 | 0.289 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.604 | 0.189 | 0.007 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.369 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.531 | 0.152 | 0.054 / 0.002 / 0.433 | 0.045 / 0.030 / 0.105 | 0.376 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.549 | 0.169 | 0.082 / 0.005 / 0.668 | 0.077 / 0.043 / 0.156 | 0.349 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1658 | 0.806 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2783 | 0.872 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 1965.1250 | 0.712 |
| funds_mae_12m | 5673.7400 | 40.0829 | 853.3923 | 0.856 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 221.3777 | 0.778 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 553.5179 | 0.849 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 349.0330 | 0.870 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0459 | 0.778 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0510 | 0.879 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3740 | 0.885 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3691 | 0.866 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3176.7536 | 0.730 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1020.7946 | 0.869 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 292.8596 | 0.789 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 770.8913 | 0.470 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 641.7254 | 0.613 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0722 | 0.726 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0722 | 0.890 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3459 | 0.854 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3420 | 0.844 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1020.8 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 292.9 | 160.2 | 787.9 |
| com_valve | 770.9 | 507.1 | 1004.7 |
| ind_valve | 641.7 | 454.2 | 939.2 |
| pop | 3176.8 | 1749.1 | 7044.7 |
| res_pop | 64.0 | 37.1 | 135.5 |
| com_pop | 7.8 | 5.0 | 12.3 |
| ind_pop | 10.9 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 47.2 | 26.8 | 89.0 |
| tax_fund | 120.1 | 53.9 | 1490.0 |
| road_spend | 84.8 | 9.0 | 638.2 |
| fire_spend | 36.2 | 1.3 | 473.1 |
| police_spend | 52.0 | 3.4 | 618.5 |
| powered_zones | 7.3 | 0.9 | 9.0 |
| unpowered_zones | 5.0 | 0.8 | 7.1 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 55.8 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 981.9 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 253.4 | 128.0 | 549.2 |
| com_valve | 826.3 | 545.4 | 967.3 |
| ind_valve | 712.9 | 502.9 | 866.6 |
| pop | 3212.6 | 1820.5 | 6670.1 |
| res_pop | 64.1 | 37.8 | 127.8 |
| com_pop | 7.6 | 5.0 | 11.7 |
| ind_pop | 11.3 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 50.6 | 27.8 | 83.7 |
| tax_fund | 109.7 | 49.4 | 1392.4 |
| road_spend | 82.5 | 8.4 | 639.3 |
| fire_spend | 35.2 | 1.4 | 467.7 |
| police_spend | 52.5 | 4.3 | 609.4 |
| powered_zones | 8.9 | 1.2 | 11.7 |
| unpowered_zones | 5.8 | 1.1 | 7.9 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 56.2 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1139.2 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 413.1 | 258.1 | 1515.1 |
| com_valve | 602.2 | 390.3 | 1118.5 |
| ind_valve | 425.0 | 305.8 | 1160.1 |
| pop | 3067.5 | 1531.7 | 8185.8 |
| res_pop | 63.5 | 35.0 | 158.8 |
| com_pop | 8.3 | 4.9 | 14.2 |
| ind_pop | 9.5 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 37.1 | 23.7 | 105.2 |
| tax_fund | 151.8 | 67.8 | 1787.4 |
| road_spend | 91.7 | 10.5 | 634.9 |
| fire_spend | 39.3 | 0.9 | 489.5 |
| police_spend | 50.5 | 0.8 | 646.2 |
| powered_zones | 2.3 | 0.0 | 0.5 |
| unpowered_zones | 2.5 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.2 | 0.0 | 0.1 |
| road_total | 54.8 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.022 | 0.845 |
| traffic | 1.028 | 0.765 |
| pollution | 1.563 | 0.703 |
| land_value | 0.609 | 0.336 |
| crime | 1.000 | 0.580 |
| rate_of_growth | 1.017 | 0.835 |
| fire_coverage | 0.920 | 0.125 |
| police_coverage | 0.772 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.644 | 0.246 | 0.356 | 0.331 to 0.379 | 0.824 | 0.123 | 0.214 | 0.174 to 0.257 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.475 | 0.003 | 0.006 |
| all plans | 12 | 0.355 | 0.035 | 0.039 |
| all plans | 24 | 0.398 | 0.070 | 0.063 |
| state-reading plans | 1 | 0.438 | 0.004 | 0.006 |
| state-reading plans | 12 | 0.362 | 0.040 | 0.039 |
| state-reading plans | 24 | 0.419 | 0.084 | 0.063 |
| open-loop plans | 1 | 0.551 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.417 | 0.022 | 0.038 |
| open-loop plans | 24 | 0.459 | 0.035 | 0.065 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -230.10 |
| tile_cat | -31.33 |
| flags | -15.76 |
| power | -2.09 |
| half | -2512.40 |
| eighth | -36.16 |
| scalars_s2 | -6.72 |
| build_cost | -1.25 |
| scalars | -13.92 |
| ledger | -12.90 |
| bk | -20.10 |
| sc_res_pop | -2.15 |
| sc_com_pop | -0.37 |
| sc_ind_pop | -0.37 |
| sc_powered_zones | -0.14 |
| sc_unpowered_zones | -0.22 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.44 |
| sc_res_valve | -1.03 |
| sc_com_valve | -2.13 |
| sc_ind_valve | -1.51 |
| sc_score | -0.41 |
| sc_funds | -0.98 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.46 |
| sc_fire_spend | -0.11 |
| sc_police_spend | -0.12 |
| lg_sprite_cycle | -0.75 |
| lg_total_pop | -1.60 |
| lg_res_hist0 | -0.56 |
| lg_res_hist1 | -0.40 |
| lg_com_hist0 | -0.12 |
| lg_com_hist1 | -0.11 |
| lg_ind_hist0 | -0.18 |
| lg_ind_hist1 | -0.19 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.04 |
| lg_road_fund | -0.48 |
| lg_police_fund | -0.10 |
| lg_fire_fund | -0.07 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.04 |
| lg_city_center_y | -0.07 |
| lg_pollution_max_x | -2.97 |
| lg_pollution_max_y | -2.80 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -6.51 |
| com_rate | -9.33 |
| kl | 8.37 |
| elbo | -2880.13 |
