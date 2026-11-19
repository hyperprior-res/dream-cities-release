## os_50m_small_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.281 | 0.284 | 0.282 | 0.261 to 0.302 | 0.170 | 0.166 | 0.168 | 0.142 to 0.199 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.288 | 0.291 | 0.289 | 0.267 to 0.310 | 0.182 | 0.177 | 0.180 | 0.150 to 0.215 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.254 | 0.257 | 0.256 | 0.231 to 0.278 | 0.129 | 0.128 | 0.129 | 0.110 to 0.151 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.739 | 0.204 | 0.009 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.376 / 0.402 |
| all plans | 500 | 12 | 0.508 | 0.146 | 0.060 / 0.003 / 0.378 | 0.038 / 0.026 / 0.103 | 0.376 / 0.428 |
| all plans | 500 | 24 | 0.526 | 0.167 | 0.079 / 0.005 / 0.678 | 0.062 / 0.042 / 0.160 | 0.347 / 0.408 |
| state-reading plans | 394 | 1 | 0.704 | 0.208 | 0.011 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.413 / 0.436 |
| state-reading plans | 394 | 12 | 0.507 | 0.151 | 0.069 / 0.003 / 0.465 | 0.038 / 0.025 / 0.103 | 0.397 / 0.442 |
| state-reading plans | 394 | 24 | 0.539 | 0.184 | 0.097 / 0.005 / 0.791 | 0.062 / 0.044 / 0.150 | 0.361 / 0.412 |
| open-loop plans | 106 | 1 | 0.822 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.217 / 0.257 |
| open-loop plans | 106 | 12 | 0.740 | 0.131 | 0.025 / 0.002 / 0.061 | 0.040 / 0.031 / 0.103 | 0.297 / 0.372 |
| open-loop plans | 106 | 24 | 0.784 | 0.122 | 0.026 / 0.005 / 0.140 | 0.064 / 0.036 / 0.203 | 0.297 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1680 | 0.810 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2821 | 0.890 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1626.5150 | 0.803 |
| funds_mae_12m | 5714.0800 | 36.8760 | 863.7337 | 0.854 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 219.1605 | 0.791 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 489.3635 | 0.845 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 328.2292 | 0.894 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0384 | 0.839 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0600 | 0.847 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3764 | 0.880 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3680 | 0.856 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2836.0750 | 0.807 |
| funds_mae_24m | 7364.5720 | 66.5620 | 968.2090 | 0.876 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 260.2008 | 0.792 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 565.3460 | 0.887 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 531.3787 | 0.744 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0621 | 0.832 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0787 | 0.890 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3471 | 0.852 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3414 | 0.837 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 968.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 260.2 | 142.8 | 706.1 |
| com_valve | 565.3 | 508.6 | 1010.2 |
| ind_valve | 531.4 | 416.9 | 864.8 |
| pop | 2836.1 | 1754.6 | 7353.4 |
| res_pop | 63.1 | 39.0 | 139.9 |
| com_pop | 6.2 | 4.4 | 12.8 |
| ind_pop | 9.3 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.6 | 25.2 | 89.6 |
| tax_fund | 169.5 | 51.5 | 1444.5 |
| road_spend | 101.1 | 8.2 | 647.3 |
| fire_spend | 55.8 | 0.8 | 474.7 |
| police_spend | 93.5 | 6.0 | 604.1 |
| powered_zones | 7.1 | 0.7 | 8.6 |
| unpowered_zones | 4.5 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 55.8 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1000.0 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 240.2 | 130.7 | 533.4 |
| com_valve | 595.0 | 541.8 | 962.1 |
| ind_valve | 572.2 | 446.9 | 814.5 |
| pop | 2844.6 | 1810.1 | 6881.1 |
| res_pop | 62.2 | 39.6 | 131.0 |
| com_pop | 6.1 | 4.5 | 12.1 |
| ind_pop | 9.4 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 46.0 | 26.2 | 83.7 |
| tax_fund | 159.3 | 47.1 | 1400.1 |
| road_spend | 93.8 | 8.1 | 645.8 |
| fire_spend | 49.5 | 0.8 | 464.7 |
| police_spend | 85.5 | 6.4 | 591.3 |
| powered_zones | 8.2 | 0.9 | 10.7 |
| unpowered_zones | 4.9 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 56.2 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 849.9 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 334.4 | 187.8 | 1348.3 |
| com_valve | 454.9 | 385.4 | 1188.9 |
| ind_valve | 379.5 | 305.2 | 1051.7 |
| pop | 2804.6 | 1548.5 | 9108.7 |
| res_pop | 66.6 | 37.0 | 172.8 |
| com_pop | 6.4 | 4.2 | 15.7 |
| ind_pop | 8.7 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 34.7 | 21.3 | 111.7 |
| tax_fund | 207.3 | 68.0 | 1609.5 |
| road_spend | 128.4 | 8.8 | 653.2 |
| fire_spend | 79.4 | 1.1 | 512.0 |
| police_spend | 123.2 | 4.6 | 651.4 |
| powered_zones | 2.9 | 0.0 | 0.5 |
| unpowered_zones | 3.1 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.5 | 0.0 | 0.2 |
| road_total | 54.2 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.010 | 0.838 |
| traffic | 1.063 | 0.772 |
| pollution | 1.440 | 0.706 |
| land_value | 0.646 | 0.325 |
| crime | 0.975 | 0.566 |
| rate_of_growth | 1.008 | 0.819 |
| fire_coverage | 1.191 | 0.123 |
| police_coverage | 0.892 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.533 | 0.263 | 0.352 | 0.330 to 0.374 | 0.507 | 0.132 | 0.210 | 0.172 to 0.255 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.490 | 0.004 | 0.006 |
| all plans | 12 | 0.331 | 0.041 | 0.029 |
| all plans | 24 | 0.356 | 0.063 | 0.051 |
| state-reading plans | 1 | 0.522 | 0.005 | 0.006 |
| state-reading plans | 12 | 0.331 | 0.048 | 0.029 |
| state-reading plans | 24 | 0.369 | 0.078 | 0.051 |
| open-loop plans | 1 | 0.454 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.454 | 0.025 | 0.029 |
| open-loop plans | 24 | 0.450 | 0.025 | 0.057 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -247.92 |
| tile_cat | -34.26 |
| flags | -17.70 |
| power | -3.73 |
| half | -2550.70 |
| eighth | -39.29 |
| scalars_s2 | -6.88 |
| build_cost | -1.42 |
| scalars | -16.87 |
| ledger | -19.06 |
| bk | -29.06 |
| sc_res_pop | -2.15 |
| sc_com_pop | -0.37 |
| sc_ind_pop | -0.43 |
| sc_powered_zones | -0.18 |
| sc_unpowered_zones | -0.24 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.45 |
| sc_res_valve | -1.13 |
| sc_com_valve | -2.19 |
| sc_ind_valve | -1.80 |
| sc_score | -0.93 |
| sc_funds | -1.39 |
| sc_tax_fund | -0.83 |
| sc_road_spend | -1.09 |
| sc_fire_spend | -0.32 |
| sc_police_spend | -0.32 |
| lg_sprite_cycle | -0.84 |
| lg_total_pop | -2.26 |
| lg_res_hist0 | -1.22 |
| lg_res_hist1 | -0.90 |
| lg_com_hist0 | -0.28 |
| lg_com_hist1 | -0.20 |
| lg_ind_hist0 | -0.32 |
| lg_ind_hist1 | -0.44 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.02 |
| lg_ind_cap | -0.01 |
| lg_need_hospital | -0.14 |
| lg_need_church | -0.11 |
| lg_road_fund | -1.08 |
| lg_police_fund | -0.32 |
| lg_fire_fund | -0.22 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.09 |
| lg_city_center_x | -0.17 |
| lg_city_center_y | -0.18 |
| lg_pollution_max_x | -3.66 |
| lg_pollution_max_y | -3.87 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.68 |
| terrain | -6.24 |
| com_rate | -4.47 |
| kl | 10.12 |
| elbo | -2951.77 |

## os_50m_small_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.291 | 0.292 | 0.291 | 0.269 to 0.311 | 0.173 | 0.164 | 0.168 | 0.143 to 0.199 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.300 | 0.300 | 0.300 | 0.278 to 0.320 | 0.190 | 0.178 | 0.184 | 0.154 to 0.220 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.257 | 0.261 | 0.259 | 0.234 to 0.284 | 0.118 | 0.116 | 0.117 | 0.100 to 0.137 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.523 | 0.204 | 0.005 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.384 / 0.402 |
| all plans | 500 | 12 | 0.389 | 0.146 | 0.044 / 0.003 / 0.378 | 0.046 / 0.026 / 0.103 | 0.373 / 0.428 |
| all plans | 500 | 24 | 0.448 | 0.167 | 0.061 / 0.005 / 0.678 | 0.079 / 0.042 / 0.160 | 0.343 / 0.408 |
| state-reading plans | 394 | 1 | 0.538 | 0.208 | 0.006 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.422 / 0.436 |
| state-reading plans | 394 | 12 | 0.390 | 0.151 | 0.047 / 0.003 / 0.465 | 0.047 / 0.025 / 0.103 | 0.393 / 0.442 |
| state-reading plans | 394 | 24 | 0.469 | 0.184 | 0.068 / 0.005 / 0.791 | 0.078 / 0.044 / 0.150 | 0.356 / 0.412 |
| open-loop plans | 106 | 1 | 0.507 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.218 / 0.257 |
| open-loop plans | 106 | 12 | 0.537 | 0.131 | 0.027 / 0.002 / 0.061 | 0.045 / 0.031 / 0.103 | 0.295 / 0.372 |
| open-loop plans | 106 | 24 | 0.650 | 0.122 | 0.033 / 0.005 / 0.140 | 0.080 / 0.036 / 0.203 | 0.297 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1685 | 0.812 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2913 | 0.919 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1964.6950 | 0.690 |
| funds_mae_12m | 5714.0800 | 36.8760 | 722.2860 | 0.879 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 250.6002 | 0.732 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 520.4257 | 0.808 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 337.4170 | 0.880 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0464 | 0.736 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0442 | 0.889 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3728 | 0.872 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3616 | 0.842 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3779.6700 | 0.638 |
| funds_mae_24m | 7364.5720 | 66.5620 | 821.1650 | 0.897 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 310.3290 | 0.703 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 595.9380 | 0.826 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 592.3660 | 0.608 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0785 | 0.692 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0606 | 0.917 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3434 | 0.843 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3354 | 0.823 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 821.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 310.3 | 142.8 | 706.1 |
| com_valve | 595.9 | 508.6 | 1010.2 |
| ind_valve | 592.4 | 416.9 | 864.8 |
| pop | 3779.7 | 1754.6 | 7353.4 |
| res_pop | 83.2 | 39.0 | 139.9 |
| com_pop | 7.1 | 4.4 | 12.8 |
| ind_pop | 11.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 60.3 | 25.2 | 89.6 |
| tax_fund | 194.1 | 51.5 | 1444.5 |
| road_spend | 99.1 | 8.2 | 647.3 |
| fire_spend | 54.2 | 0.8 | 474.7 |
| police_spend | 95.7 | 6.0 | 604.1 |
| powered_zones | 5.3 | 0.7 | 8.6 |
| unpowered_zones | 3.7 | 0.6 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 46.6 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 795.9 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 293.0 | 130.7 | 533.4 |
| com_valve | 621.3 | 541.8 | 962.1 |
| ind_valve | 633.9 | 446.9 | 814.5 |
| pop | 3817.4 | 1810.1 | 6881.1 |
| res_pop | 82.7 | 39.6 | 131.0 |
| com_pop | 7.1 | 4.5 | 12.1 |
| ind_pop | 12.0 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 64.0 | 26.2 | 83.7 |
| tax_fund | 181.1 | 47.1 | 1400.1 |
| road_spend | 92.2 | 8.1 | 645.8 |
| fire_spend | 48.0 | 0.8 | 464.7 |
| police_spend | 89.5 | 6.4 | 591.3 |
| powered_zones | 6.0 | 0.9 | 10.7 |
| unpowered_zones | 4.2 | 0.8 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.4 |
| road_total | 47.2 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 915.2 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 374.6 | 187.8 | 1348.3 |
| com_valve | 501.6 | 385.4 | 1188.9 |
| ind_valve | 437.8 | 305.2 | 1051.7 |
| pop | 3639.6 | 1548.5 | 9108.7 |
| res_pop | 85.1 | 37.0 | 172.8 |
| com_pop | 7.3 | 4.2 | 15.7 |
| ind_pop | 10.8 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 46.9 | 21.3 | 111.7 |
| tax_fund | 242.4 | 68.0 | 1609.5 |
| road_spend | 124.9 | 8.8 | 653.2 |
| fire_spend | 77.0 | 1.1 | 512.0 |
| police_spend | 118.4 | 4.6 | 651.4 |
| powered_zones | 2.6 | 0.0 | 0.5 |
| unpowered_zones | 2.0 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 44.1 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.036 | 0.838 |
| traffic | 1.077 | 0.772 |
| pollution | 1.336 | 0.706 |
| land_value | 0.660 | 0.325 |
| crime | 0.974 | 0.566 |
| rate_of_growth | 1.053 | 0.819 |
| fire_coverage | 1.066 | 0.123 |
| police_coverage | 0.930 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.357 | 0.287 | 0.318 | 0.295 to 0.340 | 0.210 | 0.152 | 0.177 | 0.147 to 0.212 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.411 | 0.003 | 0.006 |
| all plans | 12 | 0.303 | 0.032 | 0.035 |
| all plans | 24 | 0.362 | 0.056 | 0.072 |
| state-reading plans | 1 | 0.444 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.306 | 0.033 | 0.036 |
| state-reading plans | 24 | 0.382 | 0.065 | 0.072 |
| open-loop plans | 1 | 0.363 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.402 | 0.026 | 0.035 |
| open-loop plans | 24 | 0.495 | 0.027 | 0.072 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -330.35 |
| tile_cat | -41.78 |
| flags | -22.20 |
| power | -6.73 |
| half | -2855.56 |
| eighth | -50.14 |
| scalars_s2 | -5.33 |
| build_cost | -0.99 |
| scalars | -34.06 |
| ledger | -45.74 |
| bk | -74.47 |
| sc_res_pop | -1.49 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.22 |
| sc_powered_zones | -0.05 |
| sc_unpowered_zones | -0.04 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.36 |
| sc_res_valve | -1.75 |
| sc_com_valve | -3.02 |
| sc_ind_valve | -2.60 |
| sc_score | -6.99 |
| sc_funds | -4.02 |
| sc_tax_fund | -2.52 |
| sc_road_spend | -4.97 |
| sc_fire_spend | -1.52 |
| sc_police_spend | -1.35 |
| lg_sprite_cycle | -1.32 |
| lg_total_pop | -5.18 |
| lg_res_hist0 | -4.45 |
| lg_res_hist1 | -5.62 |
| lg_com_hist0 | -0.82 |
| lg_com_hist1 | -0.82 |
| lg_ind_hist0 | -0.65 |
| lg_ind_hist1 | -1.94 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.08 |
| lg_ind_cap | -0.01 |
| lg_need_hospital | -0.31 |
| lg_need_church | -0.20 |
| lg_road_fund | -2.43 |
| lg_police_fund | -0.65 |
| lg_fire_fund | -0.71 |
| lg_auto_budget | -0.02 |
| lg_fire_pop | -0.18 |
| lg_city_center_x | -0.26 |
| lg_city_center_y | -0.78 |
| lg_pollution_max_x | -7.24 |
| lg_pollution_max_y | -7.76 |
| lg_flood_count | -0.04 |
| lg_abs_dist | -4.26 |
| terrain | -6.02 |
| com_rate | -8.82 |
| kl | 11.80 |
| elbo | -3414.19 |
