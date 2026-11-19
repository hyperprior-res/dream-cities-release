## sf_50m_full_s1_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.276 | 0.290 | 0.283 | 0.262 to 0.301 | 0.168 | 0.176 | 0.172 | 0.149 to 0.200 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.284 | 0.298 | 0.291 | 0.270 to 0.311 | 0.180 | 0.188 | 0.184 | 0.157 to 0.215 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.246 | 0.259 | 0.253 | 0.229 to 0.275 | 0.127 | 0.134 | 0.130 | 0.113 to 0.151 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.567 | 0.204 | 0.004 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.379 / 0.402 |
| all plans | 500 | 12 | 0.413 | 0.146 | 0.037 / 0.003 / 0.378 | 0.041 / 0.026 / 0.103 | 0.352 / 0.428 |
| all plans | 500 | 24 | 0.501 | 0.167 | 0.058 / 0.005 / 0.678 | 0.064 / 0.042 / 0.160 | 0.317 / 0.408 |
| state-reading plans | 394 | 1 | 0.579 | 0.208 | 0.005 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.415 / 0.436 |
| state-reading plans | 394 | 12 | 0.409 | 0.151 | 0.042 / 0.003 / 0.465 | 0.042 / 0.025 / 0.103 | 0.373 / 0.442 |
| state-reading plans | 394 | 24 | 0.510 | 0.184 | 0.070 / 0.005 / 0.791 | 0.064 / 0.044 / 0.150 | 0.332 / 0.412 |
| open-loop plans | 106 | 1 | 0.573 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.222 / 0.257 |
| open-loop plans | 106 | 12 | 0.774 | 0.131 | 0.022 / 0.002 / 0.061 | 0.040 / 0.031 / 0.103 | 0.272 / 0.372 |
| open-loop plans | 106 | 24 | 1.059 | 0.122 | 0.033 / 0.005 / 0.140 | 0.062 / 0.036 / 0.203 | 0.260 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1720 | 0.829 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2826 | 0.891 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1735.2050 | 0.766 |
| funds_mae_12m | 5714.0800 | 36.8760 | 559.2075 | 0.908 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 200.0507 | 0.828 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 512.9733 | 0.817 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 360.8000 | 0.845 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0414 | 0.800 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0373 | 0.908 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3520 | 0.823 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3516 | 0.818 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2881.9050 | 0.799 |
| funds_mae_24m | 7364.5720 | 66.5620 | 747.0335 | 0.907 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 281.9377 | 0.753 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 631.5728 | 0.755 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 612.8745 | 0.562 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0637 | 0.819 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0582 | 0.921 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3166 | 0.777 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3166 | 0.776 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 747.0 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 281.9 | 142.8 | 706.1 |
| com_valve | 631.6 | 508.6 | 1010.2 |
| ind_valve | 612.9 | 416.9 | 864.8 |
| pop | 2881.9 | 1754.6 | 7353.4 |
| res_pop | 67.0 | 39.0 | 139.9 |
| com_pop | 6.7 | 4.4 | 12.8 |
| ind_pop | 9.8 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 73.0 | 25.2 | 89.6 |
| tax_fund | 138.4 | 51.5 | 1444.5 |
| road_spend | 77.9 | 8.2 | 647.3 |
| fire_spend | 39.0 | 0.8 | 474.7 |
| police_spend | 54.8 | 6.0 | 604.1 |
| powered_zones | 7.1 | 0.7 | 8.6 |
| unpowered_zones | 4.7 | 0.6 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 50.9 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 729.5 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 266.5 | 130.7 | 533.4 |
| com_valve | 669.2 | 541.8 | 962.1 |
| ind_valve | 657.6 | 446.9 | 814.5 |
| pop | 2914.6 | 1810.1 | 6881.1 |
| res_pop | 66.8 | 39.6 | 131.0 |
| com_pop | 6.7 | 4.5 | 12.1 |
| ind_pop | 9.9 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 75.5 | 26.2 | 83.7 |
| tax_fund | 131.1 | 47.1 | 1400.1 |
| road_spend | 72.5 | 8.1 | 645.8 |
| fire_spend | 34.0 | 0.8 | 464.7 |
| police_spend | 50.9 | 6.4 | 591.3 |
| powered_zones | 7.5 | 0.9 | 10.7 |
| unpowered_zones | 5.0 | 0.8 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.4 |
| road_total | 50.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 812.3 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 339.5 | 187.8 | 1348.3 |
| com_valve | 491.6 | 385.4 | 1188.9 |
| ind_valve | 446.5 | 305.2 | 1051.7 |
| pop | 2760.3 | 1548.5 | 9108.7 |
| res_pop | 67.7 | 37.0 | 172.8 |
| com_pop | 6.7 | 4.2 | 15.7 |
| ind_pop | 9.5 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 63.8 | 21.3 | 111.7 |
| tax_fund | 165.4 | 68.0 | 1609.5 |
| road_spend | 97.8 | 8.8 | 653.2 |
| fire_spend | 57.4 | 1.1 | 512.0 |
| police_spend | 69.3 | 4.6 | 651.4 |
| powered_zones | 5.4 | 0.0 | 0.5 |
| unpowered_zones | 3.6 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 51.2 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.157 | 0.838 |
| traffic | 1.029 | 0.772 |
| pollution | 1.600 | 0.706 |
| land_value | 0.615 | 0.325 |
| crime | 1.023 | 0.566 |
| rate_of_growth | 1.056 | 0.819 |
| fire_coverage | 1.586 | 0.123 |
| police_coverage | 0.897 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.590 | 0.261 | 0.362 | 0.340 to 0.383 | 0.644 | 0.137 | 0.225 | 0.184 to 0.268 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.416 | 0.002 | 0.006 |
| all plans | 12 | 0.282 | 0.028 | 0.029 |
| all plans | 24 | 0.358 | 0.061 | 0.046 |
| state-reading plans | 1 | 0.444 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.282 | 0.032 | 0.029 |
| state-reading plans | 24 | 0.371 | 0.068 | 0.044 |
| open-loop plans | 1 | 0.383 | 0.001 | 0.004 |
| open-loop plans | 12 | 0.455 | 0.017 | 0.030 |
| open-loop plans | 24 | 0.701 | 0.035 | 0.049 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -213.64 |
| tile_cat | -30.62 |
| flags | -14.90 |
| power | -2.68 |
| half | -2371.04 |
| eighth | -35.94 |
| scalars_s2 | -5.73 |
| build_cost | -1.17 |
| scalars | -12.68 |
| ledger | -12.35 |
| bk | -19.30 |
| sc_res_pop | -1.77 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.23 |
| sc_powered_zones | -0.08 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.37 |
| sc_res_valve | -0.93 |
| sc_com_valve | -1.96 |
| sc_ind_valve | -1.40 |
| sc_score | -0.40 |
| sc_funds | -1.06 |
| sc_tax_fund | -0.43 |
| sc_road_spend | -0.48 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.13 |
| lg_sprite_cycle | -0.73 |
| lg_total_pop | -1.48 |
| lg_res_hist0 | -0.39 |
| lg_res_hist1 | -0.30 |
| lg_com_hist0 | -0.07 |
| lg_com_hist1 | -0.08 |
| lg_ind_hist0 | -0.12 |
| lg_ind_hist1 | -0.17 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.03 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.54 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.14 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.81 |
| lg_pollution_max_y | -2.89 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.79 |
| com_rate | -3.18 |
| kl | 14.91 |
| elbo | -2717.91 |

## sf_50m_full_s1_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.279 | 0.289 | 0.284 | 0.263 to 0.304 | 0.169 | 0.175 | 0.172 | 0.148 to 0.200 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.288 | 0.298 | 0.293 | 0.271 to 0.314 | 0.184 | 0.188 | 0.186 | 0.157 to 0.218 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.244 | 0.256 | 0.250 | 0.226 to 0.273 | 0.123 | 0.130 | 0.126 | 0.109 to 0.147 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.505 | 0.204 | 0.002 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.383 / 0.402 |
| all plans | 500 | 12 | 0.424 | 0.146 | 0.042 / 0.003 / 0.378 | 0.041 / 0.026 / 0.103 | 0.330 / 0.428 |
| all plans | 500 | 24 | 0.623 | 0.167 | 0.095 / 0.005 / 0.678 | 0.077 / 0.042 / 0.160 | 0.281 / 0.408 |
| state-reading plans | 394 | 1 | 0.503 | 0.208 | 0.002 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.419 / 0.436 |
| state-reading plans | 394 | 12 | 0.418 | 0.151 | 0.045 / 0.003 / 0.465 | 0.041 / 0.025 / 0.103 | 0.352 / 0.442 |
| state-reading plans | 394 | 24 | 0.627 | 0.184 | 0.106 / 0.005 / 0.791 | 0.078 / 0.044 / 0.150 | 0.299 / 0.412 |
| open-loop plans | 106 | 1 | 0.525 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.225 / 0.257 |
| open-loop plans | 106 | 12 | 0.862 | 0.131 | 0.030 / 0.002 / 0.061 | 0.042 / 0.031 / 0.103 | 0.248 / 0.372 |
| open-loop plans | 106 | 24 | 1.574 | 0.122 | 0.056 / 0.005 / 0.140 | 0.075 / 0.036 / 0.203 | 0.219 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1720 | 0.829 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2840 | 0.895 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1811.2200 | 0.741 |
| funds_mae_12m | 5714.0800 | 36.8760 | 630.2943 | 0.895 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 212.2332 | 0.805 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 540.6040 | 0.785 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 355.5347 | 0.853 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0413 | 0.801 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0418 | 0.896 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3303 | 0.772 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3309 | 0.770 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3529.9550 | 0.683 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1096.8095 | 0.859 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 426.1383 | 0.497 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 637.3628 | 0.743 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 643.4053 | 0.494 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0774 | 0.702 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0946 | 0.866 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2811 | 0.690 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2818 | 0.691 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1096.8 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 426.1 | 142.8 | 706.1 |
| com_valve | 637.4 | 508.6 | 1010.2 |
| ind_valve | 643.4 | 416.9 | 864.8 |
| pop | 3530.0 | 1754.6 | 7353.4 |
| res_pop | 72.9 | 39.0 | 139.9 |
| com_pop | 7.3 | 4.4 | 12.8 |
| ind_pop | 14.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 127.1 | 25.2 | 89.6 |
| tax_fund | 133.0 | 51.5 | 1444.5 |
| road_spend | 79.1 | 8.2 | 647.3 |
| fire_spend | 44.0 | 0.8 | 474.7 |
| police_spend | 65.2 | 6.0 | 604.1 |
| powered_zones | 10.0 | 0.7 | 8.6 |
| unpowered_zones | 5.7 | 0.6 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 56.9 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1059.4 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 409.4 | 130.7 | 533.4 |
| com_valve | 677.3 | 541.8 | 962.1 |
| ind_valve | 676.0 | 446.9 | 814.5 |
| pop | 3580.0 | 1810.1 | 6881.1 |
| res_pop | 72.9 | 39.6 | 131.0 |
| com_pop | 7.2 | 4.5 | 12.1 |
| ind_pop | 15.1 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 131.1 | 26.2 | 83.7 |
| tax_fund | 127.4 | 47.1 | 1400.1 |
| road_spend | 73.7 | 8.1 | 645.8 |
| fire_spend | 37.5 | 0.8 | 464.7 |
| police_spend | 59.9 | 6.4 | 591.3 |
| powered_zones | 10.3 | 0.9 | 10.7 |
| unpowered_zones | 5.9 | 0.8 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 56.2 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1236.0 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 488.2 | 187.8 | 1348.3 |
| com_valve | 488.9 | 385.4 | 1188.9 |
| ind_valve | 522.3 | 305.2 | 1051.7 |
| pop | 3343.8 | 1548.5 | 9108.7 |
| res_pop | 73.0 | 37.0 | 172.8 |
| com_pop | 7.5 | 4.2 | 15.7 |
| ind_pop | 14.1 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 112.1 | 21.3 | 111.7 |
| tax_fund | 153.8 | 68.0 | 1609.5 |
| road_spend | 99.2 | 8.8 | 653.2 |
| fire_spend | 68.4 | 1.1 | 512.0 |
| police_spend | 84.8 | 4.6 | 651.4 |
| powered_zones | 8.8 | 0.0 | 0.5 |
| unpowered_zones | 4.8 | 0.0 | 6.7 |
| coal_plants | 0.4 | 0.0 | 0.1 |
| nuclear_plants | 0.5 | 0.0 | 0.2 |
| road_total | 59.5 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.251 | 0.838 |
| traffic | 1.064 | 0.772 |
| pollution | 1.745 | 0.706 |
| land_value | 0.727 | 0.325 |
| crime | 1.163 | 0.566 |
| rate_of_growth | 1.118 | 0.819 |
| fire_coverage | 4.279 | 0.123 |
| police_coverage | 1.380 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.569 | 0.263 | 0.360 | 0.338 to 0.380 | 0.564 | 0.137 | 0.221 | 0.182 to 0.262 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.376 | 0.001 | 0.006 |
| all plans | 12 | 0.303 | 0.037 | 0.030 |
| all plans | 24 | 0.489 | 0.105 | 0.062 |
| state-reading plans | 1 | 0.370 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.301 | 0.039 | 0.031 |
| state-reading plans | 24 | 0.497 | 0.125 | 0.062 |
| open-loop plans | 1 | 0.387 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.566 | 0.029 | 0.028 |
| open-loop plans | 24 | 1.293 | 0.059 | 0.060 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -212.54 |
| tile_cat | -30.47 |
| flags | -14.81 |
| power | -2.74 |
| half | -2355.06 |
| eighth | -35.62 |
| scalars_s2 | -5.19 |
| build_cost | -0.87 |
| scalars | -12.12 |
| ledger | -12.79 |
| bk | -19.72 |
| sc_res_pop | -1.45 |
| sc_com_pop | -0.12 |
| sc_ind_pop | -0.21 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.34 |
| sc_res_valve | -0.93 |
| sc_com_valve | -1.94 |
| sc_ind_valve | -1.14 |
| sc_score | -0.46 |
| sc_funds | -1.01 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.59 |
| sc_fire_spend | -0.22 |
| sc_police_spend | -0.21 |
| lg_sprite_cycle | -0.83 |
| lg_total_pop | -1.43 |
| lg_res_hist0 | -0.24 |
| lg_res_hist1 | -0.45 |
| lg_com_hist0 | -0.04 |
| lg_com_hist1 | -0.15 |
| lg_ind_hist0 | -0.06 |
| lg_ind_hist1 | -0.17 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.03 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.67 |
| lg_police_fund | -0.21 |
| lg_fire_fund | -0.22 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.01 |
| lg_pollution_max_x | -2.89 |
| lg_pollution_max_y | -2.93 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.68 |
| com_rate | -3.06 |
| kl | 15.38 |
| elbo | -2700.14 |
