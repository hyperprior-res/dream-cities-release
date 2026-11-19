## os_50m_full_s1_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.295 | 0.286 | 0.290 | 0.270 to 0.309 | 0.191 | 0.174 | 0.182 | 0.157 to 0.212 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.303 | 0.292 | 0.298 | 0.276 to 0.317 | 0.205 | 0.185 | 0.195 | 0.165 to 0.229 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.265 | 0.261 | 0.263 | 0.240 to 0.284 | 0.142 | 0.135 | 0.138 | 0.120 to 0.160 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.726 | 0.204 | 0.009 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.391 / 0.402 |
| all plans | 500 | 12 | 0.491 | 0.146 | 0.053 / 0.003 / 0.378 | 0.042 / 0.026 / 0.103 | 0.382 / 0.428 |
| all plans | 500 | 24 | 0.521 | 0.167 | 0.071 / 0.005 / 0.678 | 0.066 / 0.042 / 0.160 | 0.354 / 0.408 |
| state-reading plans | 394 | 1 | 0.725 | 0.208 | 0.011 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.427 / 0.436 |
| state-reading plans | 394 | 12 | 0.496 | 0.151 | 0.062 / 0.003 / 0.465 | 0.042 / 0.025 / 0.103 | 0.402 / 0.442 |
| state-reading plans | 394 | 24 | 0.541 | 0.184 | 0.086 / 0.005 / 0.791 | 0.065 / 0.044 / 0.150 | 0.368 / 0.412 |
| open-loop plans | 106 | 1 | 0.805 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.236 / 0.257 |
| open-loop plans | 106 | 12 | 0.676 | 0.131 | 0.020 / 0.002 / 0.061 | 0.042 / 0.031 / 0.103 | 0.303 / 0.372 |
| open-loop plans | 106 | 24 | 0.721 | 0.122 | 0.025 / 0.005 / 0.140 | 0.074 / 0.036 / 0.203 | 0.302 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1819 | 0.877 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2903 | 0.915 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1793.5950 | 0.747 |
| funds_mae_12m | 5714.0800 | 36.8760 | 728.8102 | 0.878 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 206.6265 | 0.815 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 511.9468 | 0.818 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 349.3508 | 0.862 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0423 | 0.789 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0532 | 0.865 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3819 | 0.893 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3759 | 0.875 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3053.0850 | 0.768 |
| funds_mae_24m | 7364.5720 | 66.5620 | 847.0472 | 0.893 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 264.5532 | 0.784 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 607.6045 | 0.803 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 604.6380 | 0.581 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0662 | 0.797 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0713 | 0.901 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3540 | 0.869 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3497 | 0.857 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 847.0 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 264.6 | 142.8 | 706.1 |
| com_valve | 607.6 | 508.6 | 1010.2 |
| ind_valve | 604.6 | 416.9 | 864.8 |
| pop | 3053.1 | 1754.6 | 7353.4 |
| res_pop | 67.2 | 39.0 | 139.9 |
| com_pop | 6.6 | 4.4 | 12.8 |
| ind_pop | 9.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 42.8 | 25.2 | 89.6 |
| tax_fund | 170.2 | 51.5 | 1444.5 |
| road_spend | 83.3 | 8.2 | 647.3 |
| fire_spend | 44.1 | 0.8 | 474.7 |
| police_spend | 63.9 | 6.0 | 604.1 |
| powered_zones | 6.7 | 0.7 | 8.6 |
| unpowered_zones | 4.5 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 56.2 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 870.6 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 245.5 | 130.7 | 533.4 |
| com_valve | 642.2 | 541.8 | 962.1 |
| ind_valve | 653.1 | 446.9 | 814.5 |
| pop | 3006.0 | 1810.1 | 6881.1 |
| res_pop | 66.7 | 39.6 | 131.0 |
| com_pop | 6.4 | 4.5 | 12.1 |
| ind_pop | 9.7 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 44.7 | 26.2 | 83.7 |
| tax_fund | 162.9 | 47.1 | 1400.1 |
| road_spend | 79.5 | 8.1 | 645.8 |
| fire_spend | 40.3 | 0.8 | 464.7 |
| police_spend | 61.3 | 6.4 | 591.3 |
| powered_zones | 7.7 | 0.9 | 10.7 |
| unpowered_zones | 4.8 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 57.2 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 759.6 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 335.2 | 187.8 | 1348.3 |
| com_valve | 478.9 | 385.4 | 1188.9 |
| ind_valve | 424.5 | 305.2 | 1051.7 |
| pop | 3227.9 | 1548.5 | 9108.7 |
| res_pop | 68.8 | 37.0 | 172.8 |
| com_pop | 7.4 | 4.2 | 15.7 |
| ind_pop | 9.7 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 35.7 | 21.3 | 111.7 |
| tax_fund | 197.7 | 68.0 | 1609.5 |
| road_spend | 97.2 | 8.8 | 653.2 |
| fire_spend | 58.0 | 1.1 | 512.0 |
| police_spend | 73.7 | 4.6 | 651.4 |
| powered_zones | 2.7 | 0.0 | 0.5 |
| unpowered_zones | 3.2 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 52.5 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 0.989 | 0.838 |
| traffic | 1.008 | 0.772 |
| pollution | 1.415 | 0.706 |
| land_value | 0.593 | 0.325 |
| crime | 0.954 | 0.566 |
| rate_of_growth | 0.979 | 0.819 |
| fire_coverage | 1.006 | 0.123 |
| police_coverage | 0.721 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.607 | 0.257 | 0.362 | 0.339 to 0.382 | 0.642 | 0.139 | 0.228 | 0.188 to 0.272 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.475 | 0.005 | 0.006 |
| all plans | 12 | 0.318 | 0.031 | 0.031 |
| all plans | 24 | 0.355 | 0.055 | 0.053 |
| state-reading plans | 1 | 0.493 | 0.005 | 0.006 |
| state-reading plans | 12 | 0.322 | 0.035 | 0.032 |
| state-reading plans | 24 | 0.374 | 0.064 | 0.050 |
| open-loop plans | 1 | 0.468 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.404 | 0.014 | 0.030 |
| open-loop plans | 24 | 0.420 | 0.030 | 0.060 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -219.37 |
| tile_cat | -31.35 |
| flags | -14.91 |
| power | -3.16 |
| half | -2424.02 |
| eighth | -36.91 |
| scalars_s2 | -6.84 |
| build_cost | -1.42 |
| scalars | -13.89 |
| ledger | -13.25 |
| bk | -20.31 |
| sc_res_pop | -2.17 |
| sc_com_pop | -0.35 |
| sc_ind_pop | -0.43 |
| sc_powered_zones | -0.17 |
| sc_unpowered_zones | -0.23 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.42 |
| sc_res_valve | -0.95 |
| sc_com_valve | -2.00 |
| sc_ind_valve | -1.51 |
| sc_score | -0.38 |
| sc_funds | -1.05 |
| sc_tax_fund | -0.43 |
| sc_road_spend | -0.45 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.13 |
| lg_sprite_cycle | -0.74 |
| lg_total_pop | -1.54 |
| lg_res_hist0 | -0.52 |
| lg_res_hist1 | -0.37 |
| lg_com_hist0 | -0.12 |
| lg_com_hist1 | -0.11 |
| lg_ind_hist0 | -0.18 |
| lg_ind_hist1 | -0.20 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.51 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.14 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.03 |
| lg_pollution_max_x | -3.35 |
| lg_pollution_max_y | -2.82 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -5.36 |
| com_rate | -3.86 |
| kl | 12.55 |
| elbo | -2780.05 |

## os_50m_full_s1_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.306 | 0.285 | 0.295 | 0.275 to 0.314 | 0.197 | 0.170 | 0.183 | 0.157 to 0.212 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.314 | 0.294 | 0.304 | 0.283 to 0.323 | 0.212 | 0.183 | 0.197 | 0.166 to 0.230 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.273 | 0.251 | 0.262 | 0.239 to 0.283 | 0.146 | 0.124 | 0.134 | 0.115 to 0.158 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.484 | 0.204 | 0.005 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.398 / 0.402 |
| all plans | 500 | 12 | 0.359 | 0.146 | 0.037 / 0.003 / 0.378 | 0.046 / 0.026 / 0.103 | 0.384 / 0.428 |
| all plans | 500 | 24 | 0.410 | 0.167 | 0.055 / 0.005 / 0.678 | 0.071 / 0.042 / 0.160 | 0.354 / 0.408 |
| state-reading plans | 394 | 1 | 0.485 | 0.208 | 0.006 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.434 / 0.436 |
| state-reading plans | 394 | 12 | 0.361 | 0.151 | 0.041 / 0.003 / 0.465 | 0.046 / 0.025 / 0.103 | 0.404 / 0.442 |
| state-reading plans | 394 | 24 | 0.427 | 0.184 | 0.063 / 0.005 / 0.791 | 0.070 / 0.044 / 0.150 | 0.366 / 0.412 |
| open-loop plans | 106 | 1 | 0.504 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.237 / 0.257 |
| open-loop plans | 106 | 12 | 0.463 | 0.131 | 0.022 / 0.002 / 0.061 | 0.047 / 0.031 / 0.103 | 0.307 / 0.372 |
| open-loop plans | 106 | 24 | 0.555 | 0.122 | 0.030 / 0.005 / 0.140 | 0.078 / 0.036 / 0.203 | 0.310 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1826 | 0.880 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2952 | 0.931 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2013.8200 | 0.674 |
| funds_mae_12m | 5714.0800 | 36.8760 | 547.0900 | 0.910 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 208.9575 | 0.811 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 516.0072 | 0.814 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 354.4592 | 0.854 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0463 | 0.737 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0370 | 0.908 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3840 | 0.898 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3771 | 0.878 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3390.5100 | 0.708 |
| funds_mae_24m | 7364.5720 | 66.5620 | 692.9785 | 0.914 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 295.9585 | 0.728 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 627.4657 | 0.763 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 605.8635 | 0.578 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0714 | 0.753 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0551 | 0.925 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3544 | 0.870 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3494 | 0.857 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 693.0 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 296.0 | 142.8 | 706.1 |
| com_valve | 627.5 | 508.6 | 1010.2 |
| ind_valve | 605.9 | 416.9 | 864.8 |
| pop | 3390.5 | 1754.6 | 7353.4 |
| res_pop | 72.8 | 39.0 | 139.9 |
| com_pop | 7.0 | 4.4 | 12.8 |
| ind_pop | 10.8 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 50.3 | 25.2 | 89.6 |
| tax_fund | 169.4 | 51.5 | 1444.5 |
| road_spend | 76.1 | 8.2 | 647.3 |
| fire_spend | 39.4 | 0.8 | 474.7 |
| police_spend | 54.6 | 6.0 | 604.1 |
| powered_zones | 4.3 | 0.7 | 8.6 |
| unpowered_zones | 3.5 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 41.1 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 693.2 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 271.7 | 130.7 | 533.4 |
| com_valve | 659.3 | 541.8 | 962.1 |
| ind_valve | 648.6 | 446.9 | 814.5 |
| pop | 3323.0 | 1810.1 | 6881.1 |
| res_pop | 71.1 | 39.6 | 131.0 |
| com_pop | 6.9 | 4.5 | 12.1 |
| ind_pop | 10.7 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 53.2 | 26.2 | 83.7 |
| tax_fund | 160.3 | 47.1 | 1400.1 |
| road_spend | 69.6 | 8.1 | 645.8 |
| fire_spend | 32.9 | 0.8 | 464.7 |
| police_spend | 50.4 | 6.4 | 591.3 |
| powered_zones | 5.0 | 0.9 | 10.7 |
| unpowered_zones | 4.0 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.4 |
| road_total | 41.5 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 692.1 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 386.0 | 187.8 | 1348.3 |
| com_valve | 509.3 | 385.4 | 1188.9 |
| ind_valve | 446.9 | 305.2 | 1051.7 |
| pop | 3641.3 | 1548.5 | 9108.7 |
| res_pop | 79.2 | 37.0 | 172.8 |
| com_pop | 7.5 | 4.2 | 15.7 |
| ind_pop | 10.8 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 39.6 | 21.3 | 111.7 |
| tax_fund | 203.3 | 68.0 | 1609.5 |
| road_spend | 100.4 | 8.8 | 653.2 |
| fire_spend | 63.4 | 1.1 | 512.0 |
| police_spend | 70.2 | 4.6 | 651.4 |
| powered_zones | 1.9 | 0.0 | 0.5 |
| unpowered_zones | 1.9 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 39.7 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 0.997 | 0.838 |
| traffic | 0.985 | 0.772 |
| pollution | 1.359 | 0.706 |
| land_value | 0.567 | 0.325 |
| crime | 0.915 | 0.566 |
| rate_of_growth | 0.971 | 0.819 |
| fire_coverage | 1.118 | 0.123 |
| police_coverage | 0.702 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.518 | 0.262 | 0.348 | 0.328 to 0.367 | 0.395 | 0.142 | 0.209 | 0.175 to 0.246 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.364 | 0.003 | 0.006 |
| all plans | 12 | 0.270 | 0.025 | 0.037 |
| all plans | 24 | 0.317 | 0.055 | 0.059 |
| state-reading plans | 1 | 0.371 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.271 | 0.028 | 0.035 |
| state-reading plans | 24 | 0.333 | 0.061 | 0.057 |
| open-loop plans | 1 | 0.358 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.328 | 0.018 | 0.039 |
| open-loop plans | 24 | 0.404 | 0.025 | 0.070 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -209.22 |
| tile_cat | -29.90 |
| flags | -14.63 |
| power | -2.88 |
| half | -2321.94 |
| eighth | -34.07 |
| scalars_s2 | -5.23 |
| build_cost | -0.96 |
| scalars | -12.05 |
| ledger | -13.45 |
| bk | -20.27 |
| sc_res_pop | -1.46 |
| sc_com_pop | -0.12 |
| sc_ind_pop | -0.21 |
| sc_powered_zones | -0.04 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.35 |
| sc_res_valve | -0.93 |
| sc_com_valve | -1.94 |
| sc_ind_valve | -1.07 |
| sc_score | -0.47 |
| sc_funds | -0.92 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.59 |
| sc_fire_spend | -0.23 |
| sc_police_spend | -0.22 |
| lg_sprite_cycle | -0.78 |
| lg_total_pop | -1.47 |
| lg_res_hist0 | -0.24 |
| lg_res_hist1 | -0.79 |
| lg_com_hist0 | -0.05 |
| lg_com_hist1 | -0.20 |
| lg_ind_hist0 | -0.06 |
| lg_ind_hist1 | -0.36 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.02 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.66 |
| lg_police_fund | -0.21 |
| lg_fire_fund | -0.24 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.96 |
| lg_pollution_max_y | -2.91 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.46 |
| com_rate | -2.94 |
| kl | 15.41 |
| elbo | -2661.91 |
