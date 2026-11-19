## os_15m_full_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.288 | 0.277 | 0.282 | 0.263 to 0.299 | 0.180 | 0.160 | 0.169 | 0.143 to 0.198 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.296 | 0.285 | 0.290 | 0.270 to 0.309 | 0.195 | 0.172 | 0.183 | 0.152 to 0.217 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.259 | 0.249 | 0.254 | 0.234 to 0.270 | 0.132 | 0.119 | 0.125 | 0.104 to 0.146 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.540 | 0.203 | 0.004 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.363 / 0.393 |
| all plans | 700 | 12 | 0.395 | 0.154 | 0.048 / 0.003 / 0.400 | 0.052 / 0.027 / 0.112 | 0.373 / 0.423 |
| all plans | 700 | 24 | 0.458 | 0.176 | 0.086 / 0.005 / 0.614 | 0.072 / 0.039 / 0.159 | 0.343 / 0.405 |
| state-reading plans | 527 | 1 | 0.530 | 0.201 | 0.006 / 0.000 / 0.018 | 0.008 / 0.006 / 0.008 | 0.408 / 0.431 |
| state-reading plans | 527 | 12 | 0.399 | 0.162 | 0.052 / 0.003 / 0.505 | 0.051 / 0.028 / 0.106 | 0.397 / 0.442 |
| state-reading plans | 527 | 24 | 0.474 | 0.194 | 0.096 / 0.005 / 0.776 | 0.068 / 0.039 / 0.155 | 0.360 / 0.415 |
| open-loop plans | 173 | 1 | 0.605 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.151 / 0.208 |
| open-loop plans | 173 | 12 | 0.528 | 0.133 | 0.037 / 0.002 / 0.054 | 0.055 / 0.026 / 0.133 | 0.280 / 0.349 |
| open-loop plans | 173 | 24 | 0.712 | 0.128 | 0.062 / 0.005 / 0.111 | 0.082 / 0.039 / 0.168 | 0.282 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.534 | 0.189 | 0.005 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.373 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.401 | 0.152 | 0.051 / 0.002 / 0.433 | 0.052 / 0.030 / 0.105 | 0.375 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.454 | 0.169 | 0.096 / 0.005 / 0.668 | 0.074 / 0.043 / 0.156 | 0.347 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1690 | 0.822 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2820 | 0.883 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2115.1464 | 0.662 |
| funds_mae_12m | 5673.7400 | 40.0829 | 727.9507 | 0.878 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 232.5277 | 0.758 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 580.5388 | 0.812 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 349.7855 | 0.869 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0522 | 0.703 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0475 | 0.888 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3726 | 0.881 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3675 | 0.862 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3239.7714 | 0.719 |
| funds_mae_24m | 7303.4900 | 72.8329 | 998.7016 | 0.872 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 327.0829 | 0.734 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 807.2643 | 0.397 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 670.0939 | 0.555 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0715 | 0.732 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0861 | 0.867 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3431 | 0.847 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3391 | 0.836 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 998.7 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 327.1 | 160.2 | 787.9 |
| com_valve | 807.3 | 507.1 | 1004.7 |
| ind_valve | 670.1 | 454.2 | 939.2 |
| pop | 3239.8 | 1749.1 | 7044.7 |
| res_pop | 68.6 | 37.1 | 135.5 |
| com_pop | 8.3 | 5.0 | 12.3 |
| ind_pop | 10.4 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 57.4 | 26.8 | 89.0 |
| tax_fund | 125.3 | 53.9 | 1490.0 |
| road_spend | 83.3 | 9.0 | 638.2 |
| fire_spend | 32.3 | 1.3 | 473.1 |
| police_spend | 49.3 | 3.4 | 618.5 |
| powered_zones | 5.6 | 0.9 | 9.0 |
| unpowered_zones | 4.5 | 0.8 | 7.1 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 48.5 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 933.9 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 285.1 | 128.0 | 549.2 |
| com_valve | 874.8 | 545.4 | 967.3 |
| ind_valve | 743.7 | 502.9 | 866.6 |
| pop | 3167.3 | 1820.5 | 6670.1 |
| res_pop | 67.4 | 37.8 | 127.8 |
| com_pop | 8.0 | 5.0 | 11.7 |
| ind_pop | 10.6 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 60.4 | 27.8 | 83.7 |
| tax_fund | 116.9 | 49.4 | 1392.4 |
| road_spend | 80.4 | 8.4 | 639.3 |
| fire_spend | 30.2 | 1.4 | 467.7 |
| police_spend | 47.9 | 4.3 | 609.4 |
| powered_zones | 6.6 | 1.2 | 11.7 |
| unpowered_zones | 5.3 | 1.1 | 7.9 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.4 |
| road_total | 48.6 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1196.2 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 455.0 | 258.1 | 1515.1 |
| com_valve | 601.6 | 390.3 | 1118.5 |
| ind_valve | 446.0 | 305.8 | 1160.1 |
| pop | 3460.6 | 1531.7 | 8185.8 |
| res_pop | 72.1 | 35.0 | 158.8 |
| com_pop | 9.0 | 4.9 | 14.2 |
| ind_pop | 9.6 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 48.3 | 23.7 | 105.2 |
| tax_fund | 150.7 | 67.8 | 1787.4 |
| road_spend | 92.0 | 10.5 | 634.9 |
| fire_spend | 38.7 | 0.9 | 489.5 |
| police_spend | 53.6 | 0.8 | 646.2 |
| powered_zones | 2.8 | 0.0 | 0.5 |
| unpowered_zones | 2.1 | 0.0 | 4.8 |
| coal_plants | 0.1 | 0.0 | 0.2 |
| nuclear_plants | 0.2 | 0.0 | 0.1 |
| road_total | 48.3 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.022 | 0.845 |
| traffic | 1.036 | 0.765 |
| pollution | 1.530 | 0.703 |
| land_value | 0.592 | 0.336 |
| crime | 0.995 | 0.580 |
| rate_of_growth | 1.030 | 0.835 |
| fire_coverage | 1.017 | 0.125 |
| police_coverage | 0.770 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.591 | 0.255 | 0.356 | 0.331 to 0.378 | 0.588 | 0.127 | 0.209 | 0.172 to 0.251 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.435 | 0.002 | 0.006 |
| all plans | 12 | 0.309 | 0.042 | 0.049 |
| all plans | 24 | 0.367 | 0.095 | 0.062 |
| state-reading plans | 1 | 0.429 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.310 | 0.042 | 0.048 |
| state-reading plans | 24 | 0.382 | 0.109 | 0.062 |
| open-loop plans | 1 | 0.466 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.405 | 0.039 | 0.053 |
| open-loop plans | 24 | 0.540 | 0.071 | 0.065 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -218.41 |
| tile_cat | -29.73 |
| flags | -15.40 |
| power | -1.80 |
| half | -2376.50 |
| eighth | -34.34 |
| scalars_s2 | -5.16 |
| build_cost | -0.86 |
| scalars | -11.98 |
| ledger | -13.30 |
| bk | -20.12 |
| sc_res_pop | -1.47 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.14 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.34 |
| sc_res_valve | -0.99 |
| sc_com_valve | -2.08 |
| sc_ind_valve | -1.06 |
| sc_score | -0.56 |
| sc_funds | -0.85 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.53 |
| sc_fire_spend | -0.12 |
| sc_police_spend | -0.17 |
| lg_sprite_cycle | -0.76 |
| lg_total_pop | -1.58 |
| lg_res_hist0 | -0.27 |
| lg_res_hist1 | -0.57 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.19 |
| lg_ind_hist0 | -0.09 |
| lg_ind_hist1 | -0.30 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.03 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.60 |
| lg_police_fund | -0.16 |
| lg_fire_fund | -0.08 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.03 |
| lg_pollution_max_x | -3.08 |
| lg_pollution_max_y | -3.04 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -5.44 |
| com_rate | -4.01 |
| kl | 11.94 |
| elbo | -2723.70 |
