## sf_100m_small_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.250 | 0.301 | 0.273 | 0.251 to 0.294 | 0.138 | 0.178 | 0.156 | 0.134 to 0.182 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.261 | 0.309 | 0.283 | 0.261 to 0.304 | 0.151 | 0.190 | 0.168 | 0.142 to 0.199 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.213 | 0.272 | 0.239 | 0.215 to 0.264 | 0.098 | 0.139 | 0.115 | 0.100 to 0.134 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.728 | 0.204 | 0.004 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.383 / 0.402 |
| all plans | 500 | 12 | 0.597 | 0.146 | 0.052 / 0.003 / 0.378 | 0.050 / 0.026 / 0.103 | 0.299 / 0.428 |
| all plans | 500 | 24 | 0.811 | 0.167 | 0.098 / 0.005 / 0.678 | 0.103 / 0.042 / 0.160 | 0.256 / 0.408 |
| state-reading plans | 394 | 1 | 0.833 | 0.208 | 0.005 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.420 / 0.436 |
| state-reading plans | 394 | 12 | 0.590 | 0.151 | 0.057 / 0.003 / 0.465 | 0.052 / 0.025 / 0.103 | 0.317 / 0.442 |
| state-reading plans | 394 | 24 | 0.816 | 0.184 | 0.113 / 0.005 / 0.791 | 0.103 / 0.044 / 0.150 | 0.269 / 0.412 |
| open-loop plans | 106 | 1 | 0.638 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.217 / 0.257 |
| open-loop plans | 106 | 12 | 1.212 | 0.131 | 0.030 / 0.002 / 0.061 | 0.046 / 0.031 / 0.103 | 0.232 / 0.372 |
| open-loop plans | 106 | 24 | 1.782 | 0.122 | 0.050 / 0.005 / 0.140 | 0.102 / 0.036 / 0.203 | 0.211 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1558 | 0.751 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2733 | 0.862 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2382.4800 | 0.551 |
| funds_mae_12m | 5714.0800 | 36.8760 | 793.7017 | 0.867 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 235.3882 | 0.761 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 559.5158 | 0.763 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 384.3035 | 0.809 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0504 | 0.683 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0524 | 0.868 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.2995 | 0.700 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.2995 | 0.697 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5645.3550 | 0.305 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1097.4043 | 0.859 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 353.6385 | 0.626 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 684.1748 | 0.650 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 688.4950 | 0.394 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1029 | 0.484 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0980 | 0.861 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2563 | 0.629 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2562 | 0.628 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1097.4 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 353.6 | 142.8 | 706.1 |
| com_valve | 684.2 | 508.6 | 1010.2 |
| ind_valve | 688.5 | 416.9 | 864.8 |
| pop | 5645.4 | 1754.6 | 7353.4 |
| res_pop | 117.5 | 39.0 | 139.9 |
| com_pop | 9.7 | 4.4 | 12.8 |
| ind_pop | 17.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 102.2 | 25.2 | 89.6 |
| tax_fund | 205.5 | 51.5 | 1444.5 |
| road_spend | 102.0 | 8.2 | 647.3 |
| fire_spend | 59.5 | 0.8 | 474.7 |
| police_spend | 99.1 | 6.0 | 604.1 |
| powered_zones | 11.8 | 0.7 | 8.6 |
| unpowered_zones | 7.3 | 0.6 | 7.0 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 1.0 | 0.0 | 0.3 |
| road_total | 61.6 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1111.9 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 320.3 | 130.7 | 533.4 |
| com_valve | 726.3 | 541.8 | 962.1 |
| ind_valve | 745.5 | 446.9 | 814.5 |
| pop | 5791.4 | 1810.1 | 6881.1 |
| res_pop | 117.6 | 39.6 | 131.0 |
| com_pop | 9.8 | 4.5 | 12.1 |
| ind_pop | 18.3 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 108.2 | 26.2 | 83.7 |
| tax_fund | 188.8 | 47.1 | 1400.1 |
| road_spend | 94.3 | 8.1 | 645.8 |
| fire_spend | 54.4 | 0.8 | 464.7 |
| police_spend | 94.7 | 6.4 | 591.3 |
| powered_zones | 12.6 | 0.9 | 10.7 |
| unpowered_zones | 7.7 | 0.8 | 7.0 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 1.0 | 0.0 | 0.4 |
| road_total | 62.0 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1043.6 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 477.6 | 187.8 | 1348.3 |
| com_valve | 527.5 | 385.4 | 1188.9 |
| ind_valve | 476.6 | 305.2 | 1051.7 |
| pop | 5102.5 | 1548.5 | 9108.7 |
| res_pop | 116.9 | 37.0 | 172.8 |
| com_pop | 9.6 | 4.2 | 15.7 |
| ind_pop | 15.1 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 79.8 | 21.3 | 111.7 |
| tax_fund | 267.5 | 68.0 | 1609.5 |
| road_spend | 130.4 | 8.8 | 653.2 |
| fire_spend | 78.7 | 1.1 | 512.0 |
| police_spend | 115.5 | 4.6 | 651.4 |
| powered_zones | 8.9 | 0.0 | 0.5 |
| unpowered_zones | 5.9 | 0.0 | 6.7 |
| coal_plants | 0.5 | 0.0 | 0.1 |
| nuclear_plants | 1.0 | 0.0 | 0.2 |
| road_total | 60.2 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.390 | 0.838 |
| traffic | 1.107 | 0.772 |
| pollution | 1.711 | 0.706 |
| land_value | 0.826 | 0.325 |
| crime | 1.389 | 0.566 |
| rate_of_growth | 1.257 | 0.819 |
| fire_coverage | 1.275 | 0.123 |
| police_coverage | 1.149 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.366 | 0.292 | 0.325 | 0.303 to 0.345 | 0.229 | 0.160 | 0.188 | 0.159 to 0.223 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.570 | 0.002 | 0.006 |
| all plans | 12 | 0.418 | 0.044 | 0.039 |
| all plans | 24 | 0.597 | 0.112 | 0.086 |
| state-reading plans | 1 | 0.652 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.418 | 0.046 | 0.039 |
| state-reading plans | 24 | 0.614 | 0.137 | 0.084 |
| open-loop plans | 1 | 0.490 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.727 | 0.027 | 0.037 |
| open-loop plans | 24 | 1.177 | 0.059 | 0.091 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -309.31 |
| tile_cat | -41.92 |
| flags | -18.44 |
| power | -5.65 |
| half | -2798.03 |
| eighth | -41.35 |
| scalars_s2 | -5.80 |
| build_cost | -1.18 |
| scalars | -15.94 |
| ledger | -21.97 |
| bk | -32.11 |
| sc_res_pop | -1.77 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.25 |
| sc_powered_zones | -0.09 |
| sc_unpowered_zones | -0.11 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.38 |
| sc_res_valve | -1.13 |
| sc_com_valve | -2.25 |
| sc_ind_valve | -1.90 |
| sc_score | -0.86 |
| sc_funds | -1.45 |
| sc_tax_fund | -0.80 |
| sc_road_spend | -1.14 |
| sc_fire_spend | -0.32 |
| sc_police_spend | -0.28 |
| lg_sprite_cycle | -0.92 |
| lg_total_pop | -2.15 |
| lg_res_hist0 | -1.32 |
| lg_res_hist1 | -0.94 |
| lg_com_hist0 | -0.40 |
| lg_com_hist1 | -0.26 |
| lg_ind_hist0 | -0.50 |
| lg_ind_hist1 | -0.48 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.01 |
| lg_need_hospital | -0.14 |
| lg_need_church | -0.13 |
| lg_road_fund | -1.14 |
| lg_police_fund | -0.27 |
| lg_fire_fund | -0.25 |
| lg_auto_budget | -0.04 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.35 |
| lg_city_center_y | -0.25 |
| lg_pollution_max_x | -4.62 |
| lg_pollution_max_y | -4.94 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.78 |
| terrain | -6.46 |
| com_rate | -6.36 |
| kl | 13.58 |
| elbo | -3280.19 |

## sf_100m_small_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.250 | 0.301 | 0.273 | 0.251 to 0.294 | 0.138 | 0.177 | 0.155 | 0.133 to 0.181 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.260 | 0.308 | 0.282 | 0.260 to 0.304 | 0.151 | 0.188 | 0.168 | 0.141 to 0.198 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.212 | 0.272 | 0.238 | 0.215 to 0.263 | 0.098 | 0.139 | 0.115 | 0.100 to 0.135 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.502 | 0.204 | 0.002 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.379 / 0.402 |
| all plans | 500 | 12 | 0.549 | 0.146 | 0.042 / 0.003 / 0.378 | 0.056 / 0.026 / 0.103 | 0.291 / 0.428 |
| all plans | 500 | 24 | 0.787 | 0.167 | 0.088 / 0.005 / 0.678 | 0.112 / 0.042 / 0.160 | 0.250 / 0.408 |
| state-reading plans | 394 | 1 | 0.505 | 0.208 | 0.002 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.416 / 0.436 |
| state-reading plans | 394 | 12 | 0.539 | 0.151 | 0.045 / 0.003 / 0.465 | 0.057 / 0.025 / 0.103 | 0.309 / 0.442 |
| state-reading plans | 394 | 24 | 0.782 | 0.184 | 0.102 / 0.005 / 0.791 | 0.110 / 0.044 / 0.150 | 0.264 / 0.412 |
| open-loop plans | 106 | 1 | 0.500 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.214 / 0.257 |
| open-loop plans | 106 | 12 | 1.092 | 0.131 | 0.027 / 0.002 / 0.061 | 0.053 / 0.031 / 0.103 | 0.223 / 0.372 |
| open-loop plans | 106 | 24 | 1.875 | 0.122 | 0.049 / 0.005 / 0.140 | 0.116 / 0.036 / 0.203 | 0.200 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1550 | 0.747 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2727 | 0.860 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2694.9700 | 0.447 |
| funds_mae_12m | 5714.0800 | 36.8760 | 796.3267 | 0.866 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 236.7028 | 0.758 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 557.6627 | 0.765 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 387.6322 | 0.804 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0555 | 0.618 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0421 | 0.895 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.2913 | 0.681 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.2915 | 0.678 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 6197.3100 | 0.206 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1123.0583 | 0.855 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 387.7722 | 0.565 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 703.3440 | 0.612 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 705.6893 | 0.355 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1118 | 0.408 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0879 | 0.876 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2503 | 0.614 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2502 | 0.613 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1123.1 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 387.8 | 142.8 | 706.1 |
| com_valve | 703.3 | 508.6 | 1010.2 |
| ind_valve | 705.7 | 416.9 | 864.8 |
| pop | 6197.3 | 1754.6 | 7353.4 |
| res_pop | 127.9 | 39.0 | 139.9 |
| com_pop | 10.6 | 4.4 | 12.8 |
| ind_pop | 19.5 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 105.2 | 25.2 | 89.6 |
| tax_fund | 214.2 | 51.5 | 1444.5 |
| road_spend | 99.6 | 8.2 | 647.3 |
| fire_spend | 56.8 | 0.8 | 474.7 |
| police_spend | 95.8 | 6.0 | 604.1 |
| powered_zones | 11.7 | 0.7 | 8.6 |
| unpowered_zones | 6.0 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.3 |
| road_total | 57.9 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1105.5 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 351.9 | 130.7 | 533.4 |
| com_valve | 742.3 | 541.8 | 962.1 |
| ind_valve | 751.8 | 446.9 | 814.5 |
| pop | 6272.7 | 1810.1 | 6881.1 |
| res_pop | 125.6 | 39.6 | 131.0 |
| com_pop | 10.5 | 4.5 | 12.1 |
| ind_pop | 20.1 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 110.2 | 26.2 | 83.7 |
| tax_fund | 194.6 | 47.1 | 1400.1 |
| road_spend | 92.0 | 8.1 | 645.8 |
| fire_spend | 51.7 | 0.8 | 464.7 |
| police_spend | 93.3 | 6.4 | 591.3 |
| powered_zones | 12.3 | 0.9 | 10.7 |
| unpowered_zones | 6.3 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.4 |
| road_total | 58.4 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1188.4 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 521.1 | 187.8 | 1348.3 |
| com_valve | 558.7 | 385.4 | 1188.9 |
| ind_valve | 534.5 | 305.2 | 1051.7 |
| pop | 5917.0 | 1548.5 | 9108.7 |
| res_pop | 136.5 | 37.0 | 172.8 |
| com_pop | 10.8 | 4.2 | 15.7 |
| ind_pop | 17.3 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 86.5 | 21.3 | 111.7 |
| tax_fund | 287.3 | 68.0 | 1609.5 |
| road_spend | 128.0 | 8.8 | 653.2 |
| fire_spend | 75.7 | 1.1 | 512.0 |
| police_spend | 105.1 | 4.6 | 651.4 |
| powered_zones | 9.6 | 0.0 | 0.5 |
| unpowered_zones | 4.8 | 0.0 | 6.7 |
| coal_plants | 0.5 | 0.0 | 0.1 |
| nuclear_plants | 1.0 | 0.0 | 0.2 |
| road_total | 56.1 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.451 | 0.838 |
| traffic | 1.092 | 0.772 |
| pollution | 1.705 | 0.706 |
| land_value | 0.857 | 0.325 |
| crime | 1.417 | 0.566 |
| rate_of_growth | 1.287 | 0.819 |
| fire_coverage | 1.342 | 0.123 |
| police_coverage | 1.140 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.336 | 0.297 | 0.315 | 0.292 to 0.337 | 0.197 | 0.167 | 0.181 | 0.153 to 0.214 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.386 | 0.001 | 0.006 |
| all plans | 12 | 0.406 | 0.037 | 0.044 |
| all plans | 24 | 0.608 | 0.100 | 0.104 |
| state-reading plans | 1 | 0.388 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.402 | 0.039 | 0.043 |
| state-reading plans | 24 | 0.617 | 0.109 | 0.100 |
| open-loop plans | 1 | 0.374 | 0.000 | 0.004 |
| open-loop plans | 12 | 0.780 | 0.028 | 0.047 |
| open-loop plans | 24 | 1.476 | 0.054 | 0.113 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -350.07 |
| tile_cat | -45.13 |
| flags | -18.83 |
| power | -6.00 |
| half | -2951.01 |
| eighth | -42.92 |
| scalars_s2 | -5.30 |
| build_cost | -0.90 |
| scalars | -28.93 |
| ledger | -42.11 |
| bk | -65.74 |
| sc_res_pop | -1.49 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.23 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.35 |
| sc_res_valve | -1.63 |
| sc_com_valve | -2.97 |
| sc_ind_valve | -2.76 |
| sc_score | -4.88 |
| sc_funds | -2.98 |
| sc_tax_fund | -3.19 |
| sc_road_spend | -3.71 |
| sc_fire_spend | -0.77 |
| sc_police_spend | -0.76 |
| lg_sprite_cycle | -1.62 |
| lg_total_pop | -3.24 |
| lg_res_hist0 | -2.92 |
| lg_res_hist1 | -3.21 |
| lg_com_hist0 | -0.90 |
| lg_com_hist1 | -0.69 |
| lg_ind_hist0 | -1.17 |
| lg_ind_hist1 | -1.47 |
| lg_res_cap | -0.04 |
| lg_com_cap | -0.06 |
| lg_ind_cap | -0.01 |
| lg_need_hospital | -0.26 |
| lg_need_church | -0.32 |
| lg_road_fund | -2.01 |
| lg_police_fund | -0.80 |
| lg_fire_fund | -0.89 |
| lg_auto_budget | -0.05 |
| lg_fire_pop | -0.09 |
| lg_city_center_x | -0.78 |
| lg_city_center_y | -0.52 |
| lg_pollution_max_x | -7.96 |
| lg_pollution_max_y | -8.99 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -4.11 |
| terrain | -6.45 |
| com_rate | -7.50 |
| kl | 13.80 |
| elbo | -3513.64 |
