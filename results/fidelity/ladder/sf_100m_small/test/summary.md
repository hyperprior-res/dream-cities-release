## sf_100m_small_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.250 | 0.301 | 0.273 | 0.252 to 0.294 | 0.138 | 0.177 | 0.155 | 0.134 to 0.181 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.259 | 0.308 | 0.281 | 0.260 to 0.303 | 0.151 | 0.190 | 0.168 | 0.142 to 0.197 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.221 | 0.275 | 0.245 | 0.221 to 0.269 | 0.102 | 0.138 | 0.117 | 0.100 to 0.134 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.551 | 0.203 | 0.001 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.365 / 0.393 |
| all plans | 700 | 12 | 0.571 | 0.154 | 0.039 / 0.003 / 0.400 | 0.061 / 0.027 / 0.112 | 0.290 / 0.423 |
| all plans | 700 | 24 | 0.805 | 0.176 | 0.086 / 0.005 / 0.614 | 0.114 / 0.039 / 0.159 | 0.246 / 0.405 |
| state-reading plans | 527 | 1 | 0.532 | 0.201 | 0.002 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.411 / 0.431 |
| state-reading plans | 527 | 12 | 0.554 | 0.162 | 0.044 / 0.003 / 0.505 | 0.061 / 0.028 / 0.106 | 0.314 / 0.442 |
| state-reading plans | 527 | 24 | 0.783 | 0.194 | 0.099 / 0.005 / 0.776 | 0.112 / 0.039 / 0.155 | 0.266 / 0.415 |
| open-loop plans | 173 | 1 | 0.506 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.150 / 0.208 |
| open-loop plans | 173 | 12 | 1.118 | 0.133 | 0.028 / 0.002 / 0.054 | 0.062 / 0.026 / 0.133 | 0.205 / 0.349 |
| open-loop plans | 173 | 24 | 2.074 | 0.128 | 0.055 / 0.005 / 0.111 | 0.121 / 0.039 / 0.168 | 0.181 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.514 | 0.189 | 0.001 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.373 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.566 | 0.152 | 0.042 / 0.002 / 0.433 | 0.060 / 0.030 / 0.105 | 0.294 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.774 | 0.169 | 0.088 / 0.005 / 0.668 | 0.113 / 0.043 / 0.156 | 0.251 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1555 | 0.756 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2730 | 0.855 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2915.8250 | 0.391 |
| funds_mae_12m | 5673.7400 | 40.0829 | 784.7784 | 0.868 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 228.6929 | 0.765 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 560.1430 | 0.840 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 379.9348 | 0.822 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0615 | 0.594 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0392 | 0.909 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.2903 | 0.687 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.2904 | 0.681 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 6381.0500 | 0.125 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1105.9061 | 0.857 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 422.6377 | 0.582 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 719.5396 | 0.573 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 708.8777 | 0.475 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.1139 | 0.378 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0861 | 0.867 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.2463 | 0.608 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.2463 | 0.607 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1105.9 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 422.6 | 160.2 | 787.9 |
| com_valve | 719.5 | 507.1 | 1004.7 |
| ind_valve | 708.9 | 454.2 | 939.2 |
| pop | 6381.1 | 1749.1 | 7044.7 |
| res_pop | 127.6 | 37.1 | 135.5 |
| com_pop | 11.2 | 5.0 | 12.3 |
| ind_pop | 20.2 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 103.8 | 26.8 | 89.0 |
| tax_fund | 234.4 | 53.9 | 1490.0 |
| road_spend | 101.5 | 9.0 | 638.2 |
| fire_spend | 56.8 | 1.3 | 473.1 |
| police_spend | 87.3 | 3.4 | 618.5 |
| powered_zones | 12.3 | 0.9 | 9.0 |
| unpowered_zones | 6.8 | 0.8 | 7.1 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.3 |
| road_total | 58.6 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1080.7 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 356.6 | 128.0 | 549.2 |
| com_valve | 753.9 | 545.4 | 967.3 |
| ind_valve | 776.5 | 502.9 | 866.6 |
| pop | 6382.4 | 1820.5 | 6670.1 |
| res_pop | 123.0 | 37.8 | 127.8 |
| com_pop | 11.2 | 5.0 | 11.7 |
| ind_pop | 20.5 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 104.5 | 27.8 | 83.7 |
| tax_fund | 210.7 | 49.4 | 1392.4 |
| road_spend | 96.3 | 8.4 | 639.3 |
| fire_spend | 53.3 | 1.4 | 467.7 |
| police_spend | 88.8 | 4.3 | 609.4 |
| powered_zones | 12.8 | 1.2 | 11.7 |
| unpowered_zones | 7.4 | 1.1 | 7.9 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.4 |
| road_total | 59.1 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1182.6 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 623.7 | 258.1 | 1515.1 |
| com_valve | 614.9 | 390.3 | 1118.5 |
| ind_valve | 502.9 | 305.8 | 1160.1 |
| pop | 6377.1 | 1531.7 | 8185.8 |
| res_pop | 141.7 | 35.0 | 158.8 |
| com_pop | 11.0 | 4.9 | 14.2 |
| ind_pop | 19.4 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 101.7 | 23.7 | 105.2 |
| tax_fund | 306.5 | 67.8 | 1787.4 |
| road_spend | 117.5 | 10.5 | 634.9 |
| fire_spend | 67.4 | 0.9 | 489.5 |
| police_spend | 83.0 | 0.8 | 646.2 |
| powered_zones | 11.0 | 0.0 | 0.5 |
| unpowered_zones | 4.9 | 0.0 | 4.8 |
| coal_plants | 0.4 | 0.0 | 0.2 |
| nuclear_plants | 0.8 | 0.0 | 0.1 |
| road_total | 57.1 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.487 | 0.845 |
| traffic | 1.074 | 0.765 |
| pollution | 1.698 | 0.703 |
| land_value | 0.885 | 0.336 |
| crime | 1.447 | 0.580 |
| rate_of_growth | 1.319 | 0.835 |
| fire_coverage | 1.232 | 0.125 |
| police_coverage | 1.199 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.335 | 0.296 | 0.314 | 0.292 to 0.336 | 0.195 | 0.166 | 0.180 | 0.151 to 0.211 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.461 | 0.001 | 0.006 |
| all plans | 12 | 0.431 | 0.033 | 0.053 |
| all plans | 24 | 0.629 | 0.094 | 0.106 |
| state-reading plans | 1 | 0.440 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.421 | 0.035 | 0.052 |
| state-reading plans | 24 | 0.618 | 0.116 | 0.104 |
| open-loop plans | 1 | 0.420 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.829 | 0.024 | 0.053 |
| open-loop plans | 24 | 1.713 | 0.064 | 0.112 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -347.78 |
| tile_cat | -43.12 |
| flags | -18.34 |
| power | -5.44 |
| half | -2902.15 |
| eighth | -41.18 |
| scalars_s2 | -5.21 |
| build_cost | -0.80 |
| scalars | -28.64 |
| ledger | -44.23 |
| bk | -67.66 |
| sc_res_pop | -1.50 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.15 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.35 |
| sc_res_valve | -1.73 |
| sc_com_valve | -2.99 |
| sc_ind_valve | -2.65 |
| sc_score | -5.26 |
| sc_funds | -2.92 |
| sc_tax_fund | -3.19 |
| sc_road_spend | -3.44 |
| sc_fire_spend | -0.54 |
| sc_police_spend | -0.72 |
| lg_sprite_cycle | -1.77 |
| lg_total_pop | -2.95 |
| lg_res_hist0 | -3.26 |
| lg_res_hist1 | -2.97 |
| lg_com_hist0 | -0.61 |
| lg_com_hist1 | -1.31 |
| lg_ind_hist0 | -1.24 |
| lg_ind_hist1 | -1.58 |
| lg_res_cap | -0.30 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.66 |
| lg_need_church | -0.34 |
| lg_road_fund | -1.89 |
| lg_police_fund | -0.65 |
| lg_fire_fund | -0.56 |
| lg_auto_budget | -0.04 |
| lg_fire_pop | -0.23 |
| lg_city_center_x | -0.58 |
| lg_city_center_y | -0.46 |
| lg_pollution_max_x | -8.96 |
| lg_pollution_max_y | -9.16 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -4.69 |
| terrain | -6.49 |
| com_rate | -5.89 |
| kl | 13.86 |
| elbo | -3457.93 |
