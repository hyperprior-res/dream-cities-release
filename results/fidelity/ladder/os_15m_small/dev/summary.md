## os_15m_small_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.288 | 0.280 | 0.284 | 0.263 to 0.303 | 0.181 | 0.161 | 0.170 | 0.145 to 0.201 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.297 | 0.288 | 0.292 | 0.271 to 0.312 | 0.197 | 0.174 | 0.185 | 0.155 to 0.221 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.254 | 0.249 | 0.252 | 0.228 to 0.275 | 0.127 | 0.117 | 0.122 | 0.105 to 0.143 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.757 | 0.204 | 0.009 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.381 / 0.402 |
| all plans | 500 | 12 | 0.522 | 0.146 | 0.065 / 0.003 / 0.378 | 0.046 / 0.026 / 0.103 | 0.372 / 0.428 |
| all plans | 500 | 24 | 0.558 | 0.167 | 0.087 / 0.005 / 0.678 | 0.070 / 0.042 / 0.160 | 0.342 / 0.408 |
| state-reading plans | 394 | 1 | 0.668 | 0.208 | 0.011 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.418 / 0.436 |
| state-reading plans | 394 | 12 | 0.522 | 0.151 | 0.073 / 0.003 / 0.465 | 0.045 / 0.025 / 0.103 | 0.392 / 0.442 |
| state-reading plans | 394 | 24 | 0.574 | 0.184 | 0.106 / 0.005 / 0.791 | 0.068 / 0.044 / 0.150 | 0.355 / 0.412 |
| open-loop plans | 106 | 1 | 0.941 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.221 / 0.257 |
| open-loop plans | 106 | 12 | 0.754 | 0.131 | 0.027 / 0.002 / 0.061 | 0.049 / 0.031 / 0.103 | 0.292 / 0.372 |
| open-loop plans | 106 | 24 | 0.835 | 0.122 | 0.037 / 0.005 / 0.140 | 0.081 / 0.036 / 0.203 | 0.291 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1705 | 0.822 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2836 | 0.894 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2001.8300 | 0.678 |
| funds_mae_12m | 5714.0800 | 36.8760 | 938.5767 | 0.841 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 227.8767 | 0.775 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 531.0855 | 0.796 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 360.2513 | 0.846 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0460 | 0.740 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0648 | 0.835 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3715 | 0.869 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3644 | 0.848 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3298.7950 | 0.724 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1145.8608 | 0.852 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 290.8093 | 0.737 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 649.9452 | 0.718 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 697.1232 | 0.374 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0702 | 0.763 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0869 | 0.878 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3418 | 0.839 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3369 | 0.826 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1145.9 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 290.8 | 142.8 | 706.1 |
| com_valve | 649.9 | 508.6 | 1010.2 |
| ind_valve | 697.1 | 416.9 | 864.8 |
| pop | 3298.8 | 1754.6 | 7353.4 |
| res_pop | 68.5 | 39.0 | 139.9 |
| com_pop | 7.2 | 4.4 | 12.8 |
| ind_pop | 11.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 48.7 | 25.2 | 89.6 |
| tax_fund | 163.4 | 51.5 | 1444.5 |
| road_spend | 96.7 | 8.2 | 647.3 |
| fire_spend | 59.4 | 0.8 | 474.7 |
| police_spend | 97.0 | 6.0 | 604.1 |
| powered_zones | 7.0 | 0.7 | 8.6 |
| unpowered_zones | 4.6 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 57.6 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1090.0 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 256.4 | 130.7 | 533.4 |
| com_valve | 680.3 | 541.8 | 962.1 |
| ind_valve | 755.8 | 446.9 | 814.5 |
| pop | 3215.6 | 1810.1 | 6881.1 |
| res_pop | 67.9 | 39.6 | 131.0 |
| com_pop | 7.1 | 4.5 | 12.1 |
| ind_pop | 11.5 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 50.5 | 26.2 | 83.7 |
| tax_fund | 151.2 | 47.1 | 1400.1 |
| road_spend | 90.9 | 8.1 | 645.8 |
| fire_spend | 54.1 | 0.8 | 464.7 |
| police_spend | 90.7 | 6.4 | 591.3 |
| powered_zones | 8.0 | 0.9 | 10.7 |
| unpowered_zones | 5.0 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 57.1 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1353.5 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 418.7 | 187.8 | 1348.3 |
| com_valve | 537.1 | 385.4 | 1188.9 |
| ind_valve | 478.9 | 305.2 | 1051.7 |
| pop | 3608.0 | 1548.5 | 9108.7 |
| res_pop | 71.0 | 37.0 | 172.8 |
| com_pop | 7.6 | 4.2 | 15.7 |
| ind_pop | 12.1 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 41.7 | 21.3 | 111.7 |
| tax_fund | 208.4 | 68.0 | 1609.5 |
| road_spend | 118.2 | 8.8 | 653.2 |
| fire_spend | 79.3 | 1.1 | 512.0 |
| police_spend | 120.3 | 4.6 | 651.4 |
| powered_zones | 3.3 | 0.0 | 0.5 |
| unpowered_zones | 3.3 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 59.5 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.021 | 0.838 |
| traffic | 1.100 | 0.772 |
| pollution | 1.527 | 0.706 |
| land_value | 0.643 | 0.325 |
| crime | 0.997 | 0.566 |
| rate_of_growth | 1.005 | 0.819 |
| fire_coverage | 1.358 | 0.123 |
| police_coverage | 0.853 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.607 | 0.254 | 0.358 | 0.335 to 0.379 | 0.773 | 0.123 | 0.212 | 0.172 to 0.256 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.503 | 0.004 | 0.006 |
| all plans | 12 | 0.350 | 0.041 | 0.041 |
| all plans | 24 | 0.393 | 0.087 | 0.059 |
| state-reading plans | 1 | 0.470 | 0.005 | 0.006 |
| state-reading plans | 12 | 0.349 | 0.048 | 0.040 |
| state-reading plans | 24 | 0.408 | 0.106 | 0.053 |
| open-loop plans | 1 | 0.540 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.505 | 0.020 | 0.046 |
| open-loop plans | 24 | 0.521 | 0.041 | 0.075 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -238.73 |
| tile_cat | -34.45 |
| flags | -18.71 |
| power | -3.27 |
| half | -2554.70 |
| eighth | -39.84 |
| scalars_s2 | -6.87 |
| build_cost | -1.42 |
| scalars | -16.49 |
| ledger | -16.91 |
| bk | -26.53 |
| sc_res_pop | -2.15 |
| sc_com_pop | -0.36 |
| sc_ind_pop | -0.44 |
| sc_powered_zones | -0.18 |
| sc_unpowered_zones | -0.24 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.45 |
| sc_res_valve | -1.07 |
| sc_com_valve | -2.14 |
| sc_ind_valve | -1.71 |
| sc_score | -0.89 |
| sc_funds | -1.39 |
| sc_tax_fund | -0.73 |
| sc_road_spend | -1.13 |
| sc_fire_spend | -0.31 |
| sc_police_spend | -0.24 |
| lg_sprite_cycle | -0.80 |
| lg_total_pop | -2.11 |
| lg_res_hist0 | -0.93 |
| lg_res_hist1 | -0.42 |
| lg_com_hist0 | -0.20 |
| lg_com_hist1 | -0.12 |
| lg_ind_hist0 | -0.25 |
| lg_ind_hist1 | -0.20 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.09 |
| lg_need_church | -0.08 |
| lg_road_fund | -1.13 |
| lg_police_fund | -0.22 |
| lg_fire_fund | -0.24 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.29 |
| lg_city_center_y | -0.14 |
| lg_pollution_max_x | -3.55 |
| lg_pollution_max_y | -3.44 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.60 |
| terrain | -7.13 |
| com_rate | -6.05 |
| kl | 10.06 |
| elbo | -2947.76 |

## os_15m_small_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.296 | 0.284 | 0.290 | 0.269 to 0.309 | 0.187 | 0.158 | 0.171 | 0.145 to 0.203 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.304 | 0.291 | 0.298 | 0.276 to 0.317 | 0.203 | 0.170 | 0.185 | 0.154 to 0.221 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.266 | 0.254 | 0.260 | 0.236 to 0.283 | 0.134 | 0.116 | 0.124 | 0.105 to 0.148 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.556 | 0.204 | 0.006 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.392 / 0.402 |
| all plans | 500 | 12 | 0.408 | 0.146 | 0.050 / 0.003 / 0.378 | 0.055 / 0.026 / 0.103 | 0.371 / 0.428 |
| all plans | 500 | 24 | 0.466 | 0.167 | 0.077 / 0.005 / 0.678 | 0.079 / 0.042 / 0.160 | 0.341 / 0.408 |
| state-reading plans | 394 | 1 | 0.566 | 0.208 | 0.007 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.429 / 0.436 |
| state-reading plans | 394 | 12 | 0.406 | 0.151 | 0.056 / 0.003 / 0.465 | 0.054 / 0.025 / 0.103 | 0.392 / 0.442 |
| state-reading plans | 394 | 24 | 0.482 | 0.184 | 0.086 / 0.005 / 0.791 | 0.074 / 0.044 / 0.150 | 0.354 / 0.412 |
| open-loop plans | 106 | 1 | 0.594 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.230 / 0.257 |
| open-loop plans | 106 | 12 | 0.590 | 0.131 | 0.030 / 0.002 / 0.061 | 0.058 / 0.031 / 0.103 | 0.288 / 0.372 |
| open-loop plans | 106 | 24 | 0.667 | 0.122 | 0.043 / 0.005 / 0.140 | 0.094 / 0.036 / 0.203 | 0.290 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1713 | 0.826 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2897 | 0.914 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2257.9900 | 0.593 |
| funds_mae_12m | 5714.0800 | 36.8760 | 769.5610 | 0.871 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 230.0330 | 0.771 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 562.4588 | 0.759 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 378.9735 | 0.817 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0549 | 0.625 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0500 | 0.874 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3710 | 0.867 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3618 | 0.842 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3787.7350 | 0.637 |
| funds_mae_24m | 7364.5720 | 66.5620 | 963.6498 | 0.877 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 328.8152 | 0.670 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 672.1503 | 0.674 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 735.7332 | 0.288 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0787 | 0.690 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0765 | 0.893 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3406 | 0.836 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3341 | 0.819 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 963.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 328.8 | 142.8 | 706.1 |
| com_valve | 672.2 | 508.6 | 1010.2 |
| ind_valve | 735.7 | 416.9 | 864.8 |
| pop | 3787.7 | 1754.6 | 7353.4 |
| res_pop | 78.2 | 39.0 | 139.9 |
| com_pop | 7.4 | 4.4 | 12.8 |
| ind_pop | 13.4 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 54.0 | 25.2 | 89.6 |
| tax_fund | 186.0 | 51.5 | 1444.5 |
| road_spend | 98.8 | 8.2 | 647.3 |
| fire_spend | 57.0 | 0.8 | 474.7 |
| police_spend | 92.6 | 6.0 | 604.1 |
| powered_zones | 4.8 | 0.7 | 8.6 |
| unpowered_zones | 3.9 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 50.7 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 864.5 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 300.5 | 130.7 | 533.4 |
| com_valve | 708.3 | 541.8 | 962.1 |
| ind_valve | 802.2 | 446.9 | 814.5 |
| pop | 3650.8 | 1810.1 | 6881.1 |
| res_pop | 76.1 | 39.6 | 131.0 |
| com_pop | 7.3 | 4.5 | 12.1 |
| ind_pop | 13.2 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 56.6 | 26.2 | 83.7 |
| tax_fund | 174.0 | 47.1 | 1400.1 |
| road_spend | 93.6 | 8.1 | 645.8 |
| fire_spend | 53.6 | 0.8 | 464.7 |
| police_spend | 88.1 | 6.4 | 591.3 |
| powered_zones | 5.5 | 0.9 | 10.7 |
| unpowered_zones | 4.3 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.4 |
| road_total | 50.6 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1332.1 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 434.1 | 187.8 | 1348.3 |
| com_valve | 538.0 | 385.4 | 1188.9 |
| ind_valve | 488.7 | 305.2 | 1051.7 |
| pop | 4296.8 | 1548.5 | 9108.7 |
| res_pop | 86.1 | 37.0 | 172.8 |
| com_pop | 7.9 | 4.2 | 15.7 |
| ind_pop | 14.0 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 44.4 | 21.3 | 111.7 |
| tax_fund | 230.6 | 68.0 | 1609.5 |
| road_spend | 118.1 | 8.8 | 653.2 |
| fire_spend | 69.6 | 1.1 | 512.0 |
| police_spend | 109.5 | 4.6 | 651.4 |
| powered_zones | 2.3 | 0.0 | 0.5 |
| unpowered_zones | 2.4 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 51.3 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.027 | 0.838 |
| traffic | 1.112 | 0.772 |
| pollution | 1.441 | 0.706 |
| land_value | 0.637 | 0.325 |
| crime | 0.977 | 0.566 |
| rate_of_growth | 1.025 | 0.819 |
| fire_coverage | 1.155 | 0.123 |
| police_coverage | 0.832 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.473 | 0.267 | 0.341 | 0.319 to 0.361 | 0.361 | 0.132 | 0.193 | 0.160 to 0.232 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.445 | 0.003 | 0.005 |
| all plans | 12 | 0.318 | 0.034 | 0.053 |
| all plans | 24 | 0.373 | 0.075 | 0.068 |
| state-reading plans | 1 | 0.457 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.317 | 0.036 | 0.052 |
| state-reading plans | 24 | 0.390 | 0.081 | 0.063 |
| open-loop plans | 1 | 0.461 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.442 | 0.027 | 0.056 |
| open-loop plans | 24 | 0.484 | 0.050 | 0.086 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -256.26 |
| tile_cat | -36.58 |
| flags | -22.66 |
| power | -4.80 |
| half | -2598.36 |
| eighth | -40.63 |
| scalars_s2 | -5.33 |
| build_cost | -0.98 |
| scalars | -35.12 |
| ledger | -37.04 |
| bk | -66.83 |
| sc_res_pop | -1.49 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.22 |
| sc_powered_zones | -0.05 |
| sc_unpowered_zones | -0.04 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.35 |
| sc_res_valve | -1.48 |
| sc_com_valve | -2.65 |
| sc_ind_valve | -2.17 |
| sc_score | -9.04 |
| sc_funds | -3.68 |
| sc_tax_fund | -2.92 |
| sc_road_spend | -5.79 |
| sc_fire_spend | -1.15 |
| sc_police_spend | -0.91 |
| lg_sprite_cycle | -1.22 |
| lg_total_pop | -3.59 |
| lg_res_hist0 | -4.31 |
| lg_res_hist1 | -1.74 |
| lg_com_hist0 | -0.36 |
| lg_com_hist1 | -0.44 |
| lg_ind_hist0 | -0.62 |
| lg_ind_hist1 | -0.89 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.02 |
| lg_need_hospital | -0.14 |
| lg_need_church | -0.15 |
| lg_road_fund | -3.58 |
| lg_police_fund | -1.11 |
| lg_fire_fund | -0.68 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.15 |
| lg_city_center_x | -0.85 |
| lg_city_center_y | -0.14 |
| lg_pollution_max_x | -7.06 |
| lg_pollution_max_y | -5.95 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -4.00 |
| terrain | -6.33 |
| com_rate | -9.88 |
| kl | 12.79 |
| elbo | -3061.44 |
