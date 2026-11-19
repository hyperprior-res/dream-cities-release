## os_100m_full_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.294 | 0.284 | 0.289 | 0.269 to 0.308 | 0.185 | 0.171 | 0.178 | 0.151 to 0.208 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.301 | 0.291 | 0.296 | 0.275 to 0.315 | 0.199 | 0.182 | 0.190 | 0.161 to 0.225 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.265 | 0.258 | 0.261 | 0.241 to 0.282 | 0.139 | 0.132 | 0.135 | 0.117 to 0.158 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.694 | 0.204 | 0.009 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.387 / 0.402 |
| all plans | 500 | 12 | 0.511 | 0.146 | 0.051 / 0.003 / 0.378 | 0.042 / 0.026 / 0.103 | 0.384 / 0.428 |
| all plans | 500 | 24 | 0.548 | 0.167 | 0.065 / 0.005 / 0.678 | 0.068 / 0.042 / 0.160 | 0.356 / 0.408 |
| state-reading plans | 394 | 1 | 0.670 | 0.208 | 0.011 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.423 / 0.436 |
| state-reading plans | 394 | 12 | 0.518 | 0.151 | 0.058 / 0.003 / 0.465 | 0.042 / 0.025 / 0.103 | 0.404 / 0.442 |
| state-reading plans | 394 | 24 | 0.568 | 0.184 | 0.081 / 0.005 / 0.791 | 0.067 / 0.044 / 0.150 | 0.368 / 0.412 |
| open-loop plans | 106 | 1 | 0.810 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.231 / 0.257 |
| open-loop plans | 106 | 12 | 0.737 | 0.131 | 0.016 / 0.002 / 0.061 | 0.044 / 0.031 / 0.103 | 0.309 / 0.372 |
| open-loop plans | 106 | 24 | 0.887 | 0.122 | 0.020 / 0.005 / 0.140 | 0.071 / 0.036 / 0.203 | 0.310 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1778 | 0.857 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2887 | 0.910 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1749.7000 | 0.762 |
| funds_mae_12m | 5714.0800 | 36.8760 | 767.4165 | 0.871 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 216.2007 | 0.797 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 524.1895 | 0.804 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 372.8852 | 0.827 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0424 | 0.787 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0513 | 0.871 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3844 | 0.899 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3787 | 0.881 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3128.7300 | 0.755 |
| funds_mae_24m | 7364.5720 | 66.5620 | 870.7490 | 0.890 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 285.8380 | 0.746 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 631.5868 | 0.755 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 622.8117 | 0.540 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0679 | 0.783 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0647 | 0.911 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3559 | 0.873 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3513 | 0.862 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 870.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 285.8 | 142.8 | 706.1 |
| com_valve | 631.6 | 508.6 | 1010.2 |
| ind_valve | 622.8 | 416.9 | 864.8 |
| pop | 3128.7 | 1754.6 | 7353.4 |
| res_pop | 62.9 | 39.0 | 139.9 |
| com_pop | 6.8 | 4.4 | 12.8 |
| ind_pop | 10.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.2 | 25.2 | 89.6 |
| tax_fund | 131.7 | 51.5 | 1444.5 |
| road_spend | 80.4 | 8.2 | 647.3 |
| fire_spend | 36.1 | 0.8 | 474.7 |
| police_spend | 57.3 | 6.0 | 604.1 |
| powered_zones | 7.8 | 0.7 | 8.6 |
| unpowered_zones | 4.6 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 54.5 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 870.0 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 268.0 | 130.7 | 533.4 |
| com_valve | 660.8 | 541.8 | 962.1 |
| ind_valve | 673.8 | 446.9 | 814.5 |
| pop | 3116.4 | 1810.1 | 6881.1 |
| res_pop | 62.5 | 39.6 | 131.0 |
| com_pop | 6.7 | 4.5 | 12.1 |
| ind_pop | 10.7 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 51.4 | 26.2 | 83.7 |
| tax_fund | 123.0 | 47.1 | 1400.1 |
| road_spend | 74.4 | 8.1 | 645.8 |
| fire_spend | 32.5 | 0.8 | 464.7 |
| police_spend | 55.9 | 6.4 | 591.3 |
| powered_zones | 8.8 | 0.9 | 10.7 |
| unpowered_zones | 5.0 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 54.1 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 873.7 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 352.2 | 187.8 | 1348.3 |
| com_valve | 522.8 | 385.4 | 1188.9 |
| ind_valve | 433.4 | 305.2 | 1051.7 |
| pop | 3174.7 | 1548.5 | 9108.7 |
| res_pop | 64.3 | 37.0 | 172.8 |
| com_pop | 7.4 | 4.2 | 15.7 |
| ind_pop | 10.3 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 41.1 | 21.3 | 111.7 |
| tax_fund | 163.8 | 68.0 | 1609.5 |
| road_spend | 102.5 | 8.8 | 653.2 |
| fire_spend | 49.5 | 1.1 | 512.0 |
| police_spend | 62.6 | 4.6 | 651.4 |
| powered_zones | 4.1 | 0.0 | 0.5 |
| unpowered_zones | 3.2 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 55.8 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.014 | 0.838 |
| traffic | 0.978 | 0.772 |
| pollution | 1.464 | 0.706 |
| land_value | 0.597 | 0.325 |
| crime | 0.970 | 0.566 |
| rate_of_growth | 1.010 | 0.819 |
| fire_coverage | 1.014 | 0.123 |
| police_coverage | 0.806 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.594 | 0.255 | 0.357 | 0.334 to 0.378 | 0.594 | 0.131 | 0.215 | 0.177 to 0.257 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.469 | 0.004 | 0.006 |
| all plans | 12 | 0.327 | 0.030 | 0.035 |
| all plans | 24 | 0.367 | 0.056 | 0.055 |
| state-reading plans | 1 | 0.476 | 0.005 | 0.006 |
| state-reading plans | 12 | 0.333 | 0.035 | 0.034 |
| state-reading plans | 24 | 0.387 | 0.066 | 0.054 |
| open-loop plans | 1 | 0.474 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.446 | 0.012 | 0.037 |
| open-loop plans | 24 | 0.516 | 0.020 | 0.055 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -217.77 |
| tile_cat | -31.13 |
| flags | -14.89 |
| power | -3.21 |
| half | -2353.87 |
| eighth | -36.58 |
| scalars_s2 | -6.91 |
| build_cost | -1.42 |
| scalars | -13.98 |
| ledger | -12.67 |
| bk | -19.73 |
| sc_res_pop | -2.18 |
| sc_com_pop | -0.36 |
| sc_ind_pop | -0.45 |
| sc_powered_zones | -0.18 |
| sc_unpowered_zones | -0.24 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.45 |
| sc_res_valve | -0.95 |
| sc_com_valve | -1.98 |
| sc_ind_valve | -1.41 |
| sc_score | -0.41 |
| sc_funds | -1.03 |
| sc_tax_fund | -0.43 |
| sc_road_spend | -0.54 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.16 |
| lg_sprite_cycle | -0.76 |
| lg_total_pop | -1.54 |
| lg_res_hist0 | -0.41 |
| lg_res_hist1 | -0.26 |
| lg_com_hist0 | -0.08 |
| lg_com_hist1 | -0.10 |
| lg_ind_hist0 | -0.12 |
| lg_ind_hist1 | -0.23 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.58 |
| lg_police_fund | -0.16 |
| lg_fire_fund | -0.15 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.92 |
| lg_pollution_max_y | -2.85 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -4.96 |
| com_rate | -2.11 |
| kl | 12.38 |
| elbo | -2704.96 |

## os_100m_full_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.308 | 0.287 | 0.297 | 0.277 to 0.316 | 0.198 | 0.169 | 0.182 | 0.156 to 0.213 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.315 | 0.295 | 0.304 | 0.283 to 0.324 | 0.212 | 0.181 | 0.195 | 0.164 to 0.229 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.280 | 0.258 | 0.269 | 0.247 to 0.290 | 0.152 | 0.128 | 0.139 | 0.122 to 0.161 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.521 | 0.204 | 0.004 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.398 / 0.402 |
| all plans | 500 | 12 | 0.390 | 0.146 | 0.031 / 0.003 / 0.378 | 0.046 / 0.026 / 0.103 | 0.380 / 0.428 |
| all plans | 500 | 24 | 0.511 | 0.167 | 0.050 / 0.005 / 0.678 | 0.082 / 0.042 / 0.160 | 0.341 / 0.408 |
| state-reading plans | 394 | 1 | 0.526 | 0.208 | 0.005 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.435 / 0.436 |
| state-reading plans | 394 | 12 | 0.389 | 0.151 | 0.034 / 0.003 / 0.465 | 0.046 / 0.025 / 0.103 | 0.399 / 0.442 |
| state-reading plans | 394 | 24 | 0.528 | 0.184 | 0.055 / 0.005 / 0.791 | 0.082 / 0.044 / 0.150 | 0.353 / 0.412 |
| open-loop plans | 106 | 1 | 0.530 | 0.199 | 0.000 / 0.000 / 0.000 | 0.007 / 0.008 / 0.007 | 0.237 / 0.257 |
| open-loop plans | 106 | 12 | 0.728 | 0.131 | 0.020 / 0.002 / 0.061 | 0.048 / 0.031 / 0.103 | 0.305 / 0.372 |
| open-loop plans | 106 | 24 | 1.164 | 0.122 | 0.028 / 0.005 / 0.140 | 0.084 / 0.036 / 0.203 | 0.297 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1824 | 0.879 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2969 | 0.936 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2070.4000 | 0.655 |
| funds_mae_12m | 5714.0800 | 36.8760 | 584.2832 | 0.904 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 221.8720 | 0.786 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 532.4908 | 0.794 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 367.4162 | 0.835 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0463 | 0.737 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0313 | 0.924 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3797 | 0.888 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3731 | 0.868 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 4046.8150 | 0.591 |
| funds_mae_24m | 7364.5720 | 66.5620 | 696.4870 | 0.914 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 346.6410 | 0.638 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 672.4573 | 0.673 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 661.8970 | 0.453 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0818 | 0.664 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0501 | 0.933 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3414 | 0.838 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3360 | 0.824 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 696.5 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 346.6 | 142.8 | 706.1 |
| com_valve | 672.5 | 508.6 | 1010.2 |
| ind_valve | 661.9 | 416.9 | 864.8 |
| pop | 4046.8 | 1754.6 | 7353.4 |
| res_pop | 80.7 | 39.0 | 139.9 |
| com_pop | 8.1 | 4.4 | 12.8 |
| ind_pop | 12.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 93.9 | 25.2 | 89.6 |
| tax_fund | 146.4 | 51.5 | 1444.5 |
| road_spend | 82.1 | 8.2 | 647.3 |
| fire_spend | 42.9 | 0.8 | 474.7 |
| police_spend | 56.8 | 6.0 | 604.1 |
| powered_zones | 8.1 | 0.7 | 8.6 |
| unpowered_zones | 4.6 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 43.6 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 664.3 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 337.7 | 130.7 | 533.4 |
| com_valve | 704.8 | 541.8 | 962.1 |
| ind_valve | 710.3 | 446.9 | 814.5 |
| pop | 4069.0 | 1810.1 | 6881.1 |
| res_pop | 79.5 | 39.6 | 131.0 |
| com_pop | 8.0 | 4.5 | 12.1 |
| ind_pop | 12.9 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 97.7 | 26.2 | 83.7 |
| tax_fund | 136.6 | 47.1 | 1400.1 |
| road_spend | 74.7 | 8.1 | 645.8 |
| fire_spend | 37.3 | 0.8 | 464.7 |
| police_spend | 55.7 | 6.4 | 591.3 |
| powered_zones | 8.5 | 0.9 | 10.7 |
| unpowered_zones | 5.0 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.4 |
| road_total | 44.2 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 816.1 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 379.7 | 187.8 | 1348.3 |
| com_valve | 552.2 | 385.4 | 1188.9 |
| ind_valve | 482.0 | 305.2 | 1051.7 |
| pop | 3964.4 | 1548.5 | 9108.7 |
| res_pop | 85.0 | 37.0 | 172.8 |
| com_pop | 8.4 | 4.2 | 15.7 |
| ind_pop | 11.9 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 79.6 | 21.3 | 111.7 |
| tax_fund | 182.6 | 68.0 | 1609.5 |
| road_spend | 109.7 | 8.8 | 653.2 |
| fire_spend | 63.7 | 1.1 | 512.0 |
| police_spend | 60.7 | 4.6 | 651.4 |
| powered_zones | 7.0 | 0.0 | 0.5 |
| unpowered_zones | 3.3 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 41.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.076 | 0.838 |
| traffic | 0.973 | 0.772 |
| pollution | 1.528 | 0.706 |
| land_value | 0.641 | 0.325 |
| crime | 1.029 | 0.566 |
| rate_of_growth | 1.002 | 0.819 |
| fire_coverage | 1.477 | 0.123 |
| police_coverage | 1.003 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.533 | 0.265 | 0.354 | 0.333 to 0.371 | 0.415 | 0.138 | 0.208 | 0.175 to 0.242 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.407 | 0.002 | 0.006 |
| all plans | 12 | 0.295 | 0.024 | 0.038 |
| all plans | 24 | 0.410 | 0.049 | 0.073 |
| state-reading plans | 1 | 0.418 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.294 | 0.025 | 0.036 |
| state-reading plans | 24 | 0.427 | 0.053 | 0.074 |
| open-loop plans | 1 | 0.398 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.548 | 0.015 | 0.039 |
| open-loop plans | 24 | 0.992 | 0.027 | 0.071 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -206.45 |
| tile_cat | -29.97 |
| flags | -14.72 |
| power | -3.03 |
| half | -2237.63 |
| eighth | -34.43 |
| scalars_s2 | -5.25 |
| build_cost | -0.97 |
| scalars | -12.65 |
| ledger | -13.53 |
| bk | -20.93 |
| sc_res_pop | -1.47 |
| sc_com_pop | -0.13 |
| sc_ind_pop | -0.21 |
| sc_powered_zones | -0.04 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.35 |
| sc_res_valve | -0.98 |
| sc_com_valve | -1.95 |
| sc_ind_valve | -1.09 |
| sc_score | -0.56 |
| sc_funds | -0.99 |
| sc_tax_fund | -0.47 |
| sc_road_spend | -0.78 |
| sc_fire_spend | -0.29 |
| sc_police_spend | -0.29 |
| lg_sprite_cycle | -0.87 |
| lg_total_pop | -1.47 |
| lg_res_hist0 | -0.22 |
| lg_res_hist1 | -0.16 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.28 |
| lg_ind_hist0 | -0.05 |
| lg_ind_hist1 | -0.49 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.81 |
| lg_police_fund | -0.22 |
| lg_fire_fund | -0.38 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.04 |
| lg_pollution_max_y | -2.97 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -4.11 |
| com_rate | -1.54 |
| kl | 15.35 |
| elbo | -2574.38 |
