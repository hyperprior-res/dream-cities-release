## os_50m_full_s2_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.291 | 0.284 | 0.287 | 0.267 to 0.306 | 0.183 | 0.169 | 0.176 | 0.150 to 0.206 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.300 | 0.292 | 0.296 | 0.275 to 0.315 | 0.200 | 0.182 | 0.190 | 0.160 to 0.225 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.256 | 0.253 | 0.255 | 0.232 to 0.277 | 0.129 | 0.123 | 0.126 | 0.108 to 0.147 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.724 | 0.204 | 0.008 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.386 / 0.402 |
| all plans | 500 | 12 | 0.499 | 0.146 | 0.051 / 0.003 / 0.378 | 0.043 / 0.026 / 0.103 | 0.381 / 0.428 |
| all plans | 500 | 24 | 0.525 | 0.167 | 0.064 / 0.005 / 0.678 | 0.064 / 0.042 / 0.160 | 0.353 / 0.408 |
| state-reading plans | 394 | 1 | 0.654 | 0.208 | 0.010 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.420 / 0.436 |
| state-reading plans | 394 | 12 | 0.501 | 0.151 | 0.062 / 0.003 / 0.465 | 0.043 / 0.025 / 0.103 | 0.400 / 0.442 |
| state-reading plans | 394 | 24 | 0.543 | 0.184 | 0.081 / 0.005 / 0.791 | 0.062 / 0.044 / 0.150 | 0.366 / 0.412 |
| open-loop plans | 106 | 1 | 0.938 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.232 / 0.257 |
| open-loop plans | 106 | 12 | 0.734 | 0.131 | 0.017 / 0.002 / 0.061 | 0.046 / 0.031 / 0.103 | 0.305 / 0.372 |
| open-loop plans | 106 | 24 | 0.791 | 0.122 | 0.021 / 0.005 / 0.140 | 0.071 / 0.036 / 0.203 | 0.306 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1756 | 0.847 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2872 | 0.906 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1862.3500 | 0.724 |
| funds_mae_12m | 5714.0800 | 36.8760 | 677.8967 | 0.887 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 195.5817 | 0.836 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 493.3365 | 0.840 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 346.4520 | 0.867 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0431 | 0.778 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0512 | 0.871 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3807 | 0.890 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3742 | 0.871 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2911.1850 | 0.793 |
| funds_mae_24m | 7364.5720 | 66.5620 | 773.5638 | 0.903 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 251.8667 | 0.806 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 638.1665 | 0.742 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 631.3710 | 0.521 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0643 | 0.813 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0636 | 0.912 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3529 | 0.866 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3482 | 0.854 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 773.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 251.9 | 142.8 | 706.1 |
| com_valve | 638.2 | 508.6 | 1010.2 |
| ind_valve | 631.4 | 416.9 | 864.8 |
| pop | 2911.2 | 1754.6 | 7353.4 |
| res_pop | 62.0 | 39.0 | 139.9 |
| com_pop | 6.3 | 4.4 | 12.8 |
| ind_pop | 10.5 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.6 | 25.2 | 89.6 |
| tax_fund | 129.1 | 51.5 | 1444.5 |
| road_spend | 83.3 | 8.2 | 647.3 |
| fire_spend | 32.3 | 0.8 | 474.7 |
| police_spend | 57.6 | 6.0 | 604.1 |
| powered_zones | 6.8 | 0.7 | 8.6 |
| unpowered_zones | 4.5 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 54.0 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 801.2 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 234.8 | 130.7 | 533.4 |
| com_valve | 682.3 | 541.8 | 962.1 |
| ind_valve | 690.7 | 446.9 | 814.5 |
| pop | 2874.5 | 1810.1 | 6881.1 |
| res_pop | 61.0 | 39.6 | 131.0 |
| com_pop | 6.2 | 4.5 | 12.1 |
| ind_pop | 10.4 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 45.7 | 26.2 | 83.7 |
| tax_fund | 121.2 | 47.1 | 1400.1 |
| road_spend | 78.7 | 8.1 | 645.8 |
| fire_spend | 28.2 | 0.8 | 464.7 |
| police_spend | 53.6 | 6.4 | 591.3 |
| powered_zones | 7.8 | 0.9 | 10.7 |
| unpowered_zones | 4.9 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 53.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 670.7 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 315.2 | 187.8 | 1348.3 |
| com_valve | 474.2 | 385.4 | 1188.9 |
| ind_valve | 410.8 | 305.2 | 1051.7 |
| pop | 3047.6 | 1548.5 | 9108.7 |
| res_pop | 65.7 | 37.0 | 172.8 |
| com_pop | 7.0 | 4.2 | 15.7 |
| ind_pop | 10.5 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 35.8 | 21.3 | 111.7 |
| tax_fund | 158.4 | 68.0 | 1609.5 |
| road_spend | 100.5 | 8.8 | 653.2 |
| fire_spend | 47.7 | 1.1 | 512.0 |
| police_spend | 72.3 | 4.6 | 651.4 |
| powered_zones | 3.0 | 0.0 | 0.5 |
| unpowered_zones | 3.0 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 54.2 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.003 | 0.838 |
| traffic | 0.993 | 0.772 |
| pollution | 1.506 | 0.706 |
| land_value | 0.592 | 0.325 |
| crime | 0.963 | 0.566 |
| rate_of_growth | 0.988 | 0.819 |
| fire_coverage | 1.006 | 0.123 |
| police_coverage | 0.822 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.609 | 0.252 | 0.356 | 0.333 to 0.377 | 0.661 | 0.128 | 0.214 | 0.174 to 0.259 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.462 | 0.003 | 0.006 |
| all plans | 12 | 0.323 | 0.033 | 0.036 |
| all plans | 24 | 0.357 | 0.056 | 0.053 |
| state-reading plans | 1 | 0.394 | 0.004 | 0.006 |
| state-reading plans | 12 | 0.324 | 0.041 | 0.034 |
| state-reading plans | 24 | 0.375 | 0.068 | 0.052 |
| open-loop plans | 1 | 0.581 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.471 | 0.014 | 0.039 |
| open-loop plans | 24 | 0.493 | 0.016 | 0.056 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -219.99 |
| tile_cat | -31.50 |
| flags | -15.13 |
| power | -3.09 |
| half | -2416.57 |
| eighth | -36.69 |
| scalars_s2 | -6.87 |
| build_cost | -1.42 |
| scalars | -13.94 |
| ledger | -12.81 |
| bk | -19.87 |
| sc_res_pop | -2.16 |
| sc_com_pop | -0.37 |
| sc_ind_pop | -0.43 |
| sc_powered_zones | -0.17 |
| sc_unpowered_zones | -0.23 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.45 |
| sc_res_valve | -0.96 |
| sc_com_valve | -1.98 |
| sc_ind_valve | -1.51 |
| sc_score | -0.39 |
| sc_funds | -1.01 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.47 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.15 |
| lg_sprite_cycle | -0.72 |
| lg_total_pop | -1.54 |
| lg_res_hist0 | -0.49 |
| lg_res_hist1 | -0.36 |
| lg_com_hist0 | -0.11 |
| lg_com_hist1 | -0.08 |
| lg_ind_hist0 | -0.16 |
| lg_ind_hist1 | -0.26 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.51 |
| lg_police_fund | -0.14 |
| lg_fire_fund | -0.13 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.03 |
| lg_pollution_max_x | -2.91 |
| lg_pollution_max_y | -2.87 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -5.34 |
| com_rate | -3.43 |
| kl | 11.93 |
| elbo | -2771.82 |

## os_50m_full_s2_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.306 | 0.287 | 0.296 | 0.276 to 0.315 | 0.196 | 0.168 | 0.181 | 0.155 to 0.211 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.314 | 0.295 | 0.304 | 0.284 to 0.323 | 0.211 | 0.181 | 0.195 | 0.165 to 0.229 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.275 | 0.258 | 0.266 | 0.244 to 0.287 | 0.144 | 0.124 | 0.133 | 0.113 to 0.154 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.469 | 0.204 | 0.004 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.392 / 0.402 |
| all plans | 500 | 12 | 0.378 | 0.146 | 0.039 / 0.003 / 0.378 | 0.047 / 0.026 / 0.103 | 0.378 / 0.428 |
| all plans | 500 | 24 | 0.472 | 0.167 | 0.058 / 0.005 / 0.678 | 0.073 / 0.042 / 0.160 | 0.344 / 0.408 |
| state-reading plans | 394 | 1 | 0.463 | 0.208 | 0.006 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.428 / 0.436 |
| state-reading plans | 394 | 12 | 0.379 | 0.151 | 0.042 / 0.003 / 0.465 | 0.047 / 0.025 / 0.103 | 0.397 / 0.442 |
| state-reading plans | 394 | 24 | 0.489 | 0.184 | 0.064 / 0.005 / 0.791 | 0.071 / 0.044 / 0.150 | 0.357 / 0.412 |
| open-loop plans | 106 | 1 | 0.481 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.235 / 0.257 |
| open-loop plans | 106 | 12 | 0.591 | 0.131 | 0.024 / 0.002 / 0.061 | 0.048 / 0.031 / 0.103 | 0.302 / 0.372 |
| open-loop plans | 106 | 24 | 0.949 | 0.122 | 0.037 / 0.005 / 0.140 | 0.078 / 0.036 / 0.203 | 0.299 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1810 | 0.873 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2963 | 0.935 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2064.8200 | 0.657 |
| funds_mae_12m | 5714.0800 | 36.8760 | 537.7542 | 0.912 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 199.3197 | 0.829 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 520.9968 | 0.808 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 356.2597 | 0.852 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0472 | 0.725 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0392 | 0.903 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3779 | 0.884 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3700 | 0.861 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3668.2400 | 0.658 |
| funds_mae_24m | 7364.5720 | 66.5620 | 700.5978 | 0.913 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 288.1567 | 0.742 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 682.7568 | 0.653 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 646.6730 | 0.487 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0730 | 0.739 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0580 | 0.921 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3445 | 0.845 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3389 | 0.831 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 700.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 288.2 | 142.8 | 706.1 |
| com_valve | 682.8 | 508.6 | 1010.2 |
| ind_valve | 646.7 | 416.9 | 864.8 |
| pop | 3668.2 | 1754.6 | 7353.4 |
| res_pop | 72.9 | 39.0 | 139.9 |
| com_pop | 7.8 | 4.4 | 12.8 |
| ind_pop | 12.2 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 78.2 | 25.2 | 89.6 |
| tax_fund | 134.2 | 51.5 | 1444.5 |
| road_spend | 75.7 | 8.2 | 647.3 |
| fire_spend | 29.9 | 0.8 | 474.7 |
| police_spend | 54.4 | 6.0 | 604.1 |
| powered_zones | 6.8 | 0.7 | 8.6 |
| unpowered_zones | 3.9 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 47.2 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 695.3 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 267.9 | 130.7 | 533.4 |
| com_valve | 711.5 | 541.8 | 962.1 |
| ind_valve | 692.2 | 446.9 | 814.5 |
| pop | 3632.8 | 1810.1 | 6881.1 |
| res_pop | 71.5 | 39.6 | 131.0 |
| com_pop | 7.8 | 4.5 | 12.1 |
| ind_pop | 12.2 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 81.4 | 26.2 | 83.7 |
| tax_fund | 126.3 | 47.1 | 1400.1 |
| road_spend | 69.0 | 8.1 | 645.8 |
| fire_spend | 26.3 | 0.8 | 464.7 |
| police_spend | 52.3 | 6.4 | 591.3 |
| powered_zones | 7.2 | 0.9 | 10.7 |
| unpowered_zones | 4.3 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.4 |
| road_total | 47.6 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 720.3 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 363.3 | 187.8 | 1348.3 |
| com_valve | 575.8 | 385.4 | 1188.9 |
| ind_valve | 477.4 | 305.2 | 1051.7 |
| pop | 3800.1 | 1548.5 | 9108.7 |
| res_pop | 77.8 | 37.0 | 172.8 |
| com_pop | 7.9 | 4.2 | 15.7 |
| ind_pop | 12.2 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 66.5 | 21.3 | 111.7 |
| tax_fund | 163.5 | 68.0 | 1609.5 |
| road_spend | 100.4 | 8.8 | 653.2 |
| fire_spend | 43.1 | 1.1 | 512.0 |
| police_spend | 62.3 | 4.6 | 651.4 |
| powered_zones | 5.3 | 0.0 | 0.5 |
| unpowered_zones | 2.4 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 46.0 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.048 | 0.838 |
| traffic | 1.008 | 0.772 |
| pollution | 1.544 | 0.706 |
| land_value | 0.594 | 0.325 |
| crime | 0.987 | 0.566 |
| rate_of_growth | 0.991 | 0.819 |
| fire_coverage | 1.344 | 0.123 |
| police_coverage | 1.004 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.529 | 0.263 | 0.352 | 0.330 to 0.370 | 0.404 | 0.134 | 0.201 | 0.166 to 0.237 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.350 | 0.002 | 0.006 |
| all plans | 12 | 0.290 | 0.028 | 0.039 |
| all plans | 24 | 0.377 | 0.053 | 0.059 |
| state-reading plans | 1 | 0.354 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.292 | 0.030 | 0.038 |
| state-reading plans | 24 | 0.393 | 0.061 | 0.060 |
| open-loop plans | 1 | 0.332 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.435 | 0.020 | 0.041 |
| open-loop plans | 24 | 0.792 | 0.042 | 0.057 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -211.04 |
| tile_cat | -30.31 |
| flags | -14.46 |
| power | -2.57 |
| half | -2324.88 |
| eighth | -34.72 |
| scalars_s2 | -5.21 |
| build_cost | -0.97 |
| scalars | -12.14 |
| ledger | -13.49 |
| bk | -20.42 |
| sc_res_pop | -1.46 |
| sc_com_pop | -0.12 |
| sc_ind_pop | -0.20 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.35 |
| sc_res_valve | -1.01 |
| sc_com_valve | -1.92 |
| sc_ind_valve | -1.06 |
| sc_score | -0.49 |
| sc_funds | -0.86 |
| sc_tax_fund | -0.48 |
| sc_road_spend | -0.58 |
| sc_fire_spend | -0.25 |
| sc_police_spend | -0.28 |
| lg_sprite_cycle | -0.80 |
| lg_total_pop | -1.49 |
| lg_res_hist0 | -0.27 |
| lg_res_hist1 | -0.70 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.12 |
| lg_ind_hist0 | -0.07 |
| lg_ind_hist1 | -0.32 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.76 |
| lg_police_fund | -0.22 |
| lg_fire_fund | -0.18 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.01 |
| lg_pollution_max_y | -2.98 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.42 |
| com_rate | -2.84 |
| kl | 14.08 |
| elbo | -2665.94 |
