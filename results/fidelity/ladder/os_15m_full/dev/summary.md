## os_15m_full_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.287 | 0.276 | 0.282 | 0.261 to 0.301 | 0.178 | 0.161 | 0.169 | 0.143 to 0.199 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.295 | 0.284 | 0.289 | 0.268 to 0.308 | 0.191 | 0.173 | 0.182 | 0.152 to 0.215 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.258 | 0.248 | 0.253 | 0.230 to 0.274 | 0.131 | 0.119 | 0.124 | 0.106 to 0.147 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.767 | 0.204 | 0.009 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.378 / 0.402 |
| all plans | 500 | 12 | 0.501 | 0.146 | 0.056 / 0.003 / 0.378 | 0.043 / 0.026 / 0.103 | 0.376 / 0.428 |
| all plans | 500 | 24 | 0.538 | 0.167 | 0.076 / 0.005 / 0.678 | 0.069 / 0.042 / 0.160 | 0.349 / 0.408 |
| state-reading plans | 394 | 1 | 0.702 | 0.208 | 0.011 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.413 / 0.436 |
| state-reading plans | 394 | 12 | 0.506 | 0.151 | 0.065 / 0.003 / 0.465 | 0.042 / 0.025 / 0.103 | 0.394 / 0.442 |
| state-reading plans | 394 | 24 | 0.562 | 0.184 | 0.089 / 0.005 / 0.791 | 0.069 / 0.044 / 0.150 | 0.361 / 0.412 |
| open-loop plans | 106 | 1 | 0.922 | 0.199 | 0.000 / 0.000 / 0.000 | 0.010 / 0.008 / 0.007 | 0.222 / 0.257 |
| open-loop plans | 106 | 12 | 0.683 | 0.131 | 0.018 / 0.002 / 0.061 | 0.044 / 0.031 / 0.103 | 0.304 / 0.372 |
| open-loop plans | 106 | 24 | 0.733 | 0.122 | 0.029 / 0.005 / 0.140 | 0.074 / 0.036 / 0.203 | 0.307 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1686 | 0.813 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2816 | 0.888 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1932.6200 | 0.701 |
| funds_mae_12m | 5714.0800 | 36.8760 | 820.8848 | 0.862 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 229.5545 | 0.772 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 553.1985 | 0.770 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 358.8575 | 0.848 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0426 | 0.784 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0560 | 0.858 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3758 | 0.879 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3714 | 0.864 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3224.1950 | 0.738 |
| funds_mae_24m | 7364.5720 | 66.5620 | 994.9240 | 0.873 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 285.2005 | 0.747 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 709.6493 | 0.599 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 679.1470 | 0.414 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0693 | 0.770 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0756 | 0.895 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3492 | 0.857 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3454 | 0.847 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 994.9 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 285.2 | 142.8 | 706.1 |
| com_valve | 709.6 | 508.6 | 1010.2 |
| ind_valve | 679.1 | 416.9 | 864.8 |
| pop | 3224.2 | 1754.6 | 7353.4 |
| res_pop | 64.3 | 39.0 | 139.9 |
| com_pop | 7.6 | 4.4 | 12.8 |
| ind_pop | 11.0 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 44.9 | 25.2 | 89.6 |
| tax_fund | 120.8 | 51.5 | 1444.5 |
| road_spend | 85.1 | 8.2 | 647.3 |
| fire_spend | 40.9 | 0.8 | 474.7 |
| police_spend | 58.2 | 6.0 | 604.1 |
| powered_zones | 6.8 | 0.7 | 8.6 |
| unpowered_zones | 4.3 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 52.9 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 922.6 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 266.1 | 130.7 | 533.4 |
| com_valve | 763.0 | 541.8 | 962.1 |
| ind_valve | 738.7 | 446.9 | 814.5 |
| pop | 3196.9 | 1810.1 | 6881.1 |
| res_pop | 64.3 | 39.6 | 131.0 |
| com_pop | 7.5 | 4.5 | 12.1 |
| ind_pop | 10.9 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 47.5 | 26.2 | 83.7 |
| tax_fund | 115.6 | 47.1 | 1400.1 |
| road_spend | 79.5 | 8.1 | 645.8 |
| fire_spend | 36.7 | 0.8 | 464.7 |
| police_spend | 56.1 | 6.4 | 591.3 |
| powered_zones | 7.9 | 0.9 | 10.7 |
| unpowered_zones | 4.7 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 53.3 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1263.8 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 356.2 | 187.8 | 1348.3 |
| com_valve | 511.5 | 385.4 | 1188.9 |
| ind_valve | 457.7 | 305.2 | 1051.7 |
| pop | 3325.7 | 1548.5 | 9108.7 |
| res_pop | 64.6 | 37.0 | 172.8 |
| com_pop | 8.0 | 4.2 | 15.7 |
| ind_pop | 11.4 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 35.4 | 21.3 | 111.7 |
| tax_fund | 140.0 | 68.0 | 1609.5 |
| road_spend | 106.0 | 8.8 | 653.2 |
| fire_spend | 56.6 | 1.1 | 512.0 |
| police_spend | 65.9 | 4.6 | 651.4 |
| powered_zones | 2.7 | 0.0 | 0.5 |
| unpowered_zones | 3.0 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 51.6 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.005 | 0.838 |
| traffic | 1.044 | 0.772 |
| pollution | 1.542 | 0.706 |
| land_value | 0.581 | 0.325 |
| crime | 0.983 | 0.566 |
| rate_of_growth | 1.000 | 0.819 |
| fire_coverage | 1.132 | 0.123 |
| police_coverage | 0.767 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.637 | 0.251 | 0.360 | 0.337 to 0.381 | 0.820 | 0.129 | 0.223 | 0.180 to 0.269 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.500 | 0.003 | 0.006 |
| all plans | 12 | 0.329 | 0.040 | 0.037 |
| all plans | 24 | 0.378 | 0.070 | 0.062 |
| state-reading plans | 1 | 0.455 | 0.004 | 0.006 |
| state-reading plans | 12 | 0.334 | 0.045 | 0.038 |
| state-reading plans | 24 | 0.401 | 0.084 | 0.062 |
| open-loop plans | 1 | 0.568 | 0.000 | 0.007 |
| open-loop plans | 12 | 0.417 | 0.019 | 0.035 |
| open-loop plans | 24 | 0.440 | 0.026 | 0.060 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -232.92 |
| tile_cat | -33.47 |
| flags | -16.83 |
| power | -3.27 |
| half | -2550.79 |
| eighth | -38.82 |
| scalars_s2 | -6.85 |
| build_cost | -1.41 |
| scalars | -14.02 |
| ledger | -12.80 |
| bk | -19.97 |
| sc_res_pop | -2.14 |
| sc_com_pop | -0.37 |
| sc_ind_pop | -0.43 |
| sc_powered_zones | -0.17 |
| sc_unpowered_zones | -0.23 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.45 |
| sc_res_valve | -0.98 |
| sc_com_valve | -2.02 |
| sc_ind_valve | -1.57 |
| sc_score | -0.39 |
| sc_funds | -1.02 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.44 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.15 |
| lg_sprite_cycle | -0.75 |
| lg_total_pop | -1.56 |
| lg_res_hist0 | -0.54 |
| lg_res_hist1 | -0.38 |
| lg_com_hist0 | -0.12 |
| lg_com_hist1 | -0.09 |
| lg_ind_hist0 | -0.19 |
| lg_ind_hist1 | -0.18 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.51 |
| lg_police_fund | -0.18 |
| lg_fire_fund | -0.14 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.04 |
| lg_city_center_y | -0.05 |
| lg_pollution_max_x | -2.84 |
| lg_pollution_max_y | -2.77 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -6.42 |
| com_rate | -8.73 |
| kl | 8.48 |
| elbo | -2927.96 |

## os_15m_full_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.290 | 0.280 | 0.285 | 0.265 to 0.304 | 0.182 | 0.163 | 0.172 | 0.146 to 0.202 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.298 | 0.288 | 0.293 | 0.272 to 0.312 | 0.196 | 0.175 | 0.185 | 0.155 to 0.219 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.259 | 0.251 | 0.255 | 0.232 to 0.277 | 0.132 | 0.120 | 0.126 | 0.107 to 0.147 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.544 | 0.204 | 0.005 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.380 / 0.402 |
| all plans | 500 | 12 | 0.382 | 0.146 | 0.051 / 0.003 / 0.378 | 0.049 / 0.026 / 0.103 | 0.374 / 0.428 |
| all plans | 500 | 24 | 0.447 | 0.167 | 0.086 / 0.005 / 0.678 | 0.073 / 0.042 / 0.160 | 0.346 / 0.408 |
| state-reading plans | 394 | 1 | 0.543 | 0.208 | 0.006 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.416 / 0.436 |
| state-reading plans | 394 | 12 | 0.381 | 0.151 | 0.053 / 0.003 / 0.465 | 0.048 / 0.025 / 0.103 | 0.394 / 0.442 |
| state-reading plans | 394 | 24 | 0.463 | 0.184 | 0.093 / 0.005 / 0.791 | 0.070 / 0.044 / 0.150 | 0.359 / 0.412 |
| open-loop plans | 106 | 1 | 0.577 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.226 / 0.257 |
| open-loop plans | 106 | 12 | 0.582 | 0.131 | 0.042 / 0.002 / 0.061 | 0.049 / 0.031 / 0.103 | 0.296 / 0.372 |
| open-loop plans | 106 | 24 | 0.748 | 0.122 | 0.060 / 0.005 / 0.140 | 0.089 / 0.036 / 0.203 | 0.297 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1716 | 0.827 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2852 | 0.900 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2095.0000 | 0.647 |
| funds_mae_12m | 5714.0800 | 36.8760 | 691.9995 | 0.885 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 237.5662 | 0.757 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 594.5600 | 0.721 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 372.4455 | 0.827 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0486 | 0.707 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0507 | 0.872 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3736 | 0.874 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3694 | 0.860 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3483.6150 | 0.691 |
| funds_mae_24m | 7364.5720 | 66.5620 | 947.2477 | 0.879 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 316.9610 | 0.691 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 741.1693 | 0.536 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 694.9145 | 0.379 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0728 | 0.741 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0862 | 0.879 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3462 | 0.850 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3424 | 0.840 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 947.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 317.0 | 142.8 | 706.1 |
| com_valve | 741.2 | 508.6 | 1010.2 |
| ind_valve | 694.9 | 416.9 | 864.8 |
| pop | 3483.6 | 1754.6 | 7353.4 |
| res_pop | 70.4 | 39.0 | 139.9 |
| com_pop | 8.6 | 4.4 | 12.8 |
| ind_pop | 10.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 55.5 | 25.2 | 89.6 |
| tax_fund | 127.4 | 51.5 | 1444.5 |
| road_spend | 84.2 | 8.2 | 647.3 |
| fire_spend | 41.7 | 0.8 | 474.7 |
| police_spend | 57.1 | 6.0 | 604.1 |
| powered_zones | 5.0 | 0.7 | 8.6 |
| unpowered_zones | 3.7 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 46.2 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 859.2 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 295.0 | 130.7 | 533.4 |
| com_valve | 795.3 | 541.8 | 962.1 |
| ind_valve | 749.4 | 446.9 | 814.5 |
| pop | 3341.6 | 1810.1 | 6881.1 |
| res_pop | 68.5 | 39.6 | 131.0 |
| com_pop | 8.4 | 4.5 | 12.1 |
| ind_pop | 10.4 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 58.1 | 26.2 | 83.7 |
| tax_fund | 121.9 | 47.1 | 1400.1 |
| road_spend | 80.1 | 8.1 | 645.8 |
| fire_spend | 38.5 | 0.8 | 464.7 |
| police_spend | 53.4 | 6.4 | 591.3 |
| powered_zones | 5.5 | 0.9 | 10.7 |
| unpowered_zones | 4.1 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.4 |
| road_total | 45.6 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1274.4 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 398.8 | 187.8 | 1348.3 |
| com_valve | 540.0 | 385.4 | 1188.9 |
| ind_valve | 492.4 | 305.2 | 1051.7 |
| pop | 4011.3 | 1548.5 | 9108.7 |
| res_pop | 77.4 | 37.0 | 172.8 |
| com_pop | 9.3 | 4.2 | 15.7 |
| ind_pop | 11.5 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 45.7 | 21.3 | 111.7 |
| tax_fund | 148.1 | 68.0 | 1609.5 |
| road_spend | 99.3 | 8.8 | 653.2 |
| fire_spend | 53.8 | 1.1 | 512.0 |
| police_spend | 70.8 | 4.6 | 651.4 |
| powered_zones | 3.3 | 0.0 | 0.5 |
| unpowered_zones | 2.5 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 48.7 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.013 | 0.838 |
| traffic | 1.055 | 0.772 |
| pollution | 1.513 | 0.706 |
| land_value | 0.565 | 0.325 |
| crime | 0.974 | 0.566 |
| rate_of_growth | 1.012 | 0.819 |
| fire_coverage | 1.745 | 0.123 |
| police_coverage | 0.745 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.592 | 0.259 | 0.360 | 0.337 to 0.382 | 0.609 | 0.133 | 0.218 | 0.176 to 0.262 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.381 | 0.003 | 0.006 |
| all plans | 12 | 0.289 | 0.045 | 0.042 |
| all plans | 24 | 0.352 | 0.092 | 0.061 |
| state-reading plans | 1 | 0.406 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.288 | 0.047 | 0.040 |
| state-reading plans | 24 | 0.369 | 0.103 | 0.058 |
| open-loop plans | 1 | 0.372 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.405 | 0.041 | 0.046 |
| open-loop plans | 24 | 0.527 | 0.069 | 0.067 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -220.89 |
| tile_cat | -31.63 |
| flags | -16.35 |
| power | -2.99 |
| half | -2422.97 |
| eighth | -36.84 |
| scalars_s2 | -5.21 |
| build_cost | -0.97 |
| scalars | -11.98 |
| ledger | -12.98 |
| bk | -19.75 |
| sc_res_pop | -1.47 |
| sc_com_pop | -0.12 |
| sc_ind_pop | -0.20 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.34 |
| sc_res_valve | -0.95 |
| sc_com_valve | -1.96 |
| sc_ind_valve | -1.10 |
| sc_score | -0.48 |
| sc_funds | -0.87 |
| sc_tax_fund | -0.45 |
| sc_road_spend | -0.52 |
| sc_fire_spend | -0.22 |
| sc_police_spend | -0.22 |
| lg_sprite_cycle | -0.82 |
| lg_total_pop | -1.55 |
| lg_res_hist0 | -0.25 |
| lg_res_hist1 | -0.41 |
| lg_com_hist0 | -0.04 |
| lg_com_hist1 | -0.04 |
| lg_ind_hist0 | -0.08 |
| lg_ind_hist1 | -0.16 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.03 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.02 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.67 |
| lg_police_fund | -0.34 |
| lg_fire_fund | -0.24 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.03 |
| lg_pollution_max_x | -2.94 |
| lg_pollution_max_y | -2.92 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -5.23 |
| com_rate | -4.33 |
| kl | 11.91 |
| elbo | -2779.08 |
