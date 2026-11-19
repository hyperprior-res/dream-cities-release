## sf_50m_full_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.273 | 0.289 | 0.281 | 0.260 to 0.300 | 0.163 | 0.177 | 0.170 | 0.145 to 0.197 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.283 | 0.297 | 0.290 | 0.270 to 0.310 | 0.178 | 0.188 | 0.183 | 0.155 to 0.214 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.234 | 0.260 | 0.246 | 0.224 to 0.267 | 0.117 | 0.136 | 0.126 | 0.110 to 0.145 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.616 | 0.204 | 0.004 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.380 / 0.402 |
| all plans | 500 | 12 | 0.462 | 0.146 | 0.035 / 0.003 / 0.378 | 0.044 / 0.026 / 0.103 | 0.345 / 0.428 |
| all plans | 500 | 24 | 0.551 | 0.167 | 0.056 / 0.005 / 0.678 | 0.069 / 0.042 / 0.160 | 0.313 / 0.408 |
| state-reading plans | 394 | 1 | 0.667 | 0.208 | 0.005 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.415 / 0.436 |
| state-reading plans | 394 | 12 | 0.454 | 0.151 | 0.039 / 0.003 / 0.465 | 0.044 / 0.025 / 0.103 | 0.363 / 0.442 |
| state-reading plans | 394 | 24 | 0.558 | 0.184 | 0.062 / 0.005 / 0.791 | 0.068 / 0.044 / 0.150 | 0.326 / 0.412 |
| open-loop plans | 106 | 1 | 0.588 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.228 / 0.257 |
| open-loop plans | 106 | 12 | 0.897 | 0.131 | 0.021 / 0.002 / 0.061 | 0.044 / 0.031 / 0.103 | 0.274 / 0.372 |
| open-loop plans | 106 | 24 | 1.088 | 0.122 | 0.032 / 0.005 / 0.140 | 0.072 / 0.036 / 0.203 | 0.268 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1696 | 0.818 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2806 | 0.885 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1927.8450 | 0.702 |
| funds_mae_12m | 5714.0800 | 36.8760 | 599.1883 | 0.901 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 239.0337 | 0.754 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 517.2545 | 0.812 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 346.2677 | 0.867 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0441 | 0.765 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0352 | 0.913 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3448 | 0.806 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3436 | 0.800 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3436.5700 | 0.700 |
| funds_mae_24m | 7364.5720 | 66.5620 | 747.3122 | 0.907 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 279.6935 | 0.757 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 640.4878 | 0.737 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 619.5885 | 0.547 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0687 | 0.776 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0560 | 0.924 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3135 | 0.769 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3116 | 0.764 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 747.3 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 279.7 | 142.8 | 706.1 |
| com_valve | 640.5 | 508.6 | 1010.2 |
| ind_valve | 619.6 | 416.9 | 864.8 |
| pop | 3436.6 | 1754.6 | 7353.4 |
| res_pop | 82.4 | 39.0 | 139.9 |
| com_pop | 7.8 | 4.4 | 12.8 |
| ind_pop | 10.1 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 66.9 | 25.2 | 89.6 |
| tax_fund | 191.6 | 51.5 | 1444.5 |
| road_spend | 88.7 | 8.2 | 647.3 |
| fire_spend | 50.6 | 0.8 | 474.7 |
| police_spend | 74.9 | 6.0 | 604.1 |
| powered_zones | 7.3 | 0.7 | 8.6 |
| unpowered_zones | 5.1 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 53.3 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 716.5 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 251.6 | 130.7 | 533.4 |
| com_valve | 674.7 | 541.8 | 962.1 |
| ind_valve | 665.3 | 446.9 | 814.5 |
| pop | 3492.6 | 1810.1 | 6881.1 |
| res_pop | 81.7 | 39.6 | 131.0 |
| com_pop | 7.9 | 4.5 | 12.1 |
| ind_pop | 10.2 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 70.4 | 26.2 | 83.7 |
| tax_fund | 171.2 | 47.1 | 1400.1 |
| road_spend | 82.3 | 8.1 | 645.8 |
| fire_spend | 44.9 | 0.8 | 464.7 |
| police_spend | 67.4 | 6.4 | 591.3 |
| powered_zones | 8.0 | 0.9 | 10.7 |
| unpowered_zones | 5.4 | 0.8 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 52.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 861.8 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 384.2 | 187.8 | 1348.3 |
| com_valve | 513.2 | 385.4 | 1188.9 |
| ind_valve | 449.6 | 305.2 | 1051.7 |
| pop | 3228.1 | 1548.5 | 9108.7 |
| res_pop | 84.7 | 37.0 | 172.8 |
| com_pop | 7.6 | 4.2 | 15.7 |
| ind_pop | 9.8 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 53.7 | 21.3 | 111.7 |
| tax_fund | 267.3 | 68.0 | 1609.5 |
| road_spend | 112.6 | 8.8 | 653.2 |
| fire_spend | 71.8 | 1.1 | 512.0 |
| police_spend | 102.7 | 4.6 | 651.4 |
| powered_zones | 5.1 | 0.0 | 0.5 |
| unpowered_zones | 4.0 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.5 | 0.0 | 0.2 |
| road_total | 54.5 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.167 | 0.838 |
| traffic | 1.046 | 0.772 |
| pollution | 1.658 | 0.706 |
| land_value | 0.632 | 0.325 |
| crime | 1.105 | 0.566 |
| rate_of_growth | 1.089 | 0.819 |
| fire_coverage | 1.139 | 0.123 |
| police_coverage | 0.979 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.581 | 0.265 | 0.364 | 0.341 to 0.384 | 0.562 | 0.140 | 0.224 | 0.185 to 0.266 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.476 | 0.002 | 0.006 |
| all plans | 12 | 0.319 | 0.029 | 0.035 |
| all plans | 24 | 0.396 | 0.056 | 0.054 |
| state-reading plans | 1 | 0.529 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.315 | 0.031 | 0.036 |
| state-reading plans | 24 | 0.410 | 0.063 | 0.053 |
| open-loop plans | 1 | 0.447 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.565 | 0.018 | 0.032 |
| open-loop plans | 24 | 0.695 | 0.040 | 0.054 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -213.21 |
| tile_cat | -30.94 |
| flags | -14.92 |
| power | -2.74 |
| half | -2372.98 |
| eighth | -36.09 |
| scalars_s2 | -5.74 |
| build_cost | -1.18 |
| scalars | -12.81 |
| ledger | -12.71 |
| bk | -19.78 |
| sc_res_pop | -1.77 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.23 |
| sc_powered_zones | -0.08 |
| sc_unpowered_zones | -0.11 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.38 |
| sc_res_valve | -0.94 |
| sc_com_valve | -1.98 |
| sc_ind_valve | -1.45 |
| sc_score | -0.39 |
| sc_funds | -1.01 |
| sc_tax_fund | -0.45 |
| sc_road_spend | -0.48 |
| sc_fire_spend | -0.20 |
| sc_police_spend | -0.16 |
| lg_sprite_cycle | -0.80 |
| lg_total_pop | -1.43 |
| lg_res_hist0 | -0.43 |
| lg_res_hist1 | -0.31 |
| lg_com_hist0 | -0.10 |
| lg_com_hist1 | -0.08 |
| lg_ind_hist0 | -0.13 |
| lg_ind_hist1 | -0.17 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.54 |
| lg_police_fund | -0.19 |
| lg_fire_fund | -0.22 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.90 |
| lg_pollution_max_y | -2.90 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.56 |
| com_rate | -3.31 |
| kl | 13.83 |
| elbo | -2719.29 |

## sf_50m_full_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.284 | 0.289 | 0.286 | 0.264 to 0.306 | 0.172 | 0.172 | 0.172 | 0.146 to 0.200 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.292 | 0.297 | 0.294 | 0.271 to 0.314 | 0.185 | 0.185 | 0.185 | 0.154 to 0.219 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.254 | 0.261 | 0.258 | 0.236 to 0.279 | 0.127 | 0.129 | 0.128 | 0.112 to 0.145 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.498 | 0.204 | 0.002 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.385 / 0.402 |
| all plans | 500 | 12 | 0.465 | 0.146 | 0.036 / 0.003 / 0.378 | 0.048 / 0.026 / 0.103 | 0.320 / 0.428 |
| all plans | 500 | 24 | 0.622 | 0.167 | 0.071 / 0.005 / 0.678 | 0.080 / 0.042 / 0.160 | 0.282 / 0.408 |
| state-reading plans | 394 | 1 | 0.485 | 0.208 | 0.002 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.421 / 0.436 |
| state-reading plans | 394 | 12 | 0.458 | 0.151 | 0.039 / 0.003 / 0.465 | 0.049 / 0.025 / 0.103 | 0.340 / 0.442 |
| state-reading plans | 394 | 24 | 0.628 | 0.184 | 0.079 / 0.005 / 0.791 | 0.078 / 0.044 / 0.150 | 0.296 / 0.412 |
| open-loop plans | 106 | 1 | 0.513 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.228 / 0.257 |
| open-loop plans | 106 | 12 | 0.950 | 0.131 | 0.025 / 0.002 / 0.061 | 0.047 / 0.031 / 0.103 | 0.247 / 0.372 |
| open-loop plans | 106 | 24 | 1.424 | 0.122 | 0.047 / 0.005 / 0.140 | 0.087 / 0.036 / 0.203 | 0.233 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1718 | 0.828 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2865 | 0.903 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2133.5700 | 0.634 |
| funds_mae_12m | 5714.0800 | 36.8760 | 618.3180 | 0.898 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 233.9630 | 0.763 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 575.2450 | 0.744 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 363.6355 | 0.841 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0485 | 0.709 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0363 | 0.910 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3204 | 0.749 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3204 | 0.746 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 4023.2550 | 0.595 |
| funds_mae_24m | 7364.5720 | 66.5620 | 898.5462 | 0.886 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 321.1675 | 0.683 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 731.6543 | 0.555 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 683.6648 | 0.404 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0799 | 0.680 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0705 | 0.902 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2822 | 0.693 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2816 | 0.690 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 898.5 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 321.2 | 142.8 | 706.1 |
| com_valve | 731.7 | 508.6 | 1010.2 |
| ind_valve | 683.7 | 416.9 | 864.8 |
| pop | 4023.3 | 1754.6 | 7353.4 |
| res_pop | 89.2 | 39.0 | 139.9 |
| com_pop | 9.4 | 4.4 | 12.8 |
| ind_pop | 12.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 103.0 | 25.2 | 89.6 |
| tax_fund | 219.2 | 51.5 | 1444.5 |
| road_spend | 86.2 | 8.2 | 647.3 |
| fire_spend | 55.9 | 0.8 | 474.7 |
| police_spend | 97.3 | 6.0 | 604.1 |
| powered_zones | 9.8 | 0.7 | 8.6 |
| unpowered_zones | 5.8 | 0.6 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 58.5 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 868.2 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 284.0 | 130.7 | 533.4 |
| com_valve | 767.0 | 541.8 | 962.1 |
| ind_valve | 734.8 | 446.9 | 814.5 |
| pop | 3996.8 | 1810.1 | 6881.1 |
| res_pop | 88.0 | 39.6 | 131.0 |
| com_pop | 9.4 | 4.5 | 12.1 |
| ind_pop | 12.6 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 106.6 | 26.2 | 83.7 |
| tax_fund | 206.0 | 47.1 | 1400.1 |
| road_spend | 79.0 | 8.1 | 645.8 |
| fire_spend | 47.3 | 0.8 | 464.7 |
| police_spend | 86.4 | 6.4 | 591.3 |
| powered_zones | 10.3 | 0.9 | 10.7 |
| unpowered_zones | 6.2 | 0.8 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 59.3 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1011.4 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 459.3 | 187.8 | 1348.3 |
| com_valve | 600.3 | 385.4 | 1188.9 |
| ind_valve | 493.4 | 305.2 | 1051.7 |
| pop | 4121.6 | 1548.5 | 9108.7 |
| res_pop | 94.0 | 37.0 | 172.8 |
| com_pop | 9.3 | 4.2 | 15.7 |
| ind_pop | 12.8 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 89.8 | 21.3 | 111.7 |
| tax_fund | 268.2 | 68.0 | 1609.5 |
| road_spend | 112.6 | 8.8 | 653.2 |
| fire_spend | 87.9 | 1.1 | 512.0 |
| police_spend | 138.1 | 4.6 | 651.4 |
| powered_zones | 8.0 | 0.0 | 0.5 |
| unpowered_zones | 4.4 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.5 | 0.0 | 0.2 |
| road_total | 55.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.293 | 0.838 |
| traffic | 1.079 | 0.772 |
| pollution | 1.806 | 0.706 |
| land_value | 0.712 | 0.325 |
| crime | 1.210 | 0.566 |
| rate_of_growth | 1.203 | 0.819 |
| fire_coverage | 1.875 | 0.123 |
| police_coverage | 1.351 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.554 | 0.267 | 0.361 | 0.338 to 0.379 | 0.480 | 0.140 | 0.217 | 0.181 to 0.256 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.375 | 0.001 | 0.006 |
| all plans | 12 | 0.340 | 0.032 | 0.036 |
| all plans | 24 | 0.488 | 0.089 | 0.068 |
| state-reading plans | 1 | 0.359 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.337 | 0.034 | 0.037 |
| state-reading plans | 24 | 0.497 | 0.096 | 0.065 |
| open-loop plans | 1 | 0.380 | 0.000 | 0.007 |
| open-loop plans | 12 | 0.654 | 0.029 | 0.031 |
| open-loop plans | 24 | 1.145 | 0.050 | 0.073 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -211.78 |
| tile_cat | -30.81 |
| flags | -14.88 |
| power | -2.71 |
| half | -2356.52 |
| eighth | -35.70 |
| scalars_s2 | -5.22 |
| build_cost | -0.88 |
| scalars | -12.23 |
| ledger | -13.63 |
| bk | -20.64 |
| sc_res_pop | -1.46 |
| sc_com_pop | -0.12 |
| sc_ind_pop | -0.21 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.36 |
| sc_res_valve | -0.94 |
| sc_com_valve | -1.96 |
| sc_ind_valve | -1.12 |
| sc_score | -0.47 |
| sc_funds | -0.95 |
| sc_tax_fund | -0.48 |
| sc_road_spend | -0.58 |
| sc_fire_spend | -0.27 |
| sc_police_spend | -0.25 |
| lg_sprite_cycle | -1.11 |
| lg_total_pop | -1.36 |
| lg_res_hist0 | -0.24 |
| lg_res_hist1 | -0.55 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.10 |
| lg_ind_hist0 | -0.05 |
| lg_ind_hist1 | -0.21 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.65 |
| lg_police_fund | -0.28 |
| lg_fire_fund | -0.46 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.95 |
| lg_pollution_max_y | -3.08 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.35 |
| terrain | -4.48 |
| com_rate | -3.09 |
| kl | 14.27 |
| elbo | -2700.99 |
