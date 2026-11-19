## os_50m_full_samples_001200000_dec-a

samples consumed: 1200000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.279 | 0.277 | 0.278 | 0.256 to 0.298 | 0.174 | 0.164 | 0.169 | 0.143 to 0.201 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.289 | 0.285 | 0.287 | 0.265 to 0.307 | 0.190 | 0.177 | 0.183 | 0.152 to 0.219 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.242 | 0.246 | 0.244 | 0.222 to 0.266 | 0.121 | 0.120 | 0.121 | 0.102 to 0.143 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 1.050 | 0.204 | 0.010 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.371 / 0.402 |
| all plans | 500 | 12 | 0.594 | 0.146 | 0.063 / 0.003 / 0.378 | 0.041 / 0.026 / 0.103 | 0.371 / 0.428 |
| all plans | 500 | 24 | 0.604 | 0.167 | 0.082 / 0.005 / 0.678 | 0.063 / 0.042 / 0.160 | 0.345 / 0.408 |
| state-reading plans | 394 | 1 | 0.879 | 0.208 | 0.013 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.406 / 0.436 |
| state-reading plans | 394 | 12 | 0.597 | 0.151 | 0.075 / 0.003 / 0.465 | 0.041 / 0.025 / 0.103 | 0.392 / 0.442 |
| state-reading plans | 394 | 24 | 0.623 | 0.184 | 0.103 / 0.005 / 0.791 | 0.062 / 0.044 / 0.150 | 0.359 / 0.412 |
| open-loop plans | 106 | 1 | 1.423 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.221 / 0.257 |
| open-loop plans | 106 | 12 | 0.872 | 0.131 | 0.016 / 0.002 / 0.061 | 0.041 / 0.031 / 0.103 | 0.290 / 0.372 |
| open-loop plans | 106 | 24 | 0.863 | 0.122 | 0.019 / 0.005 / 0.140 | 0.066 / 0.036 / 0.203 | 0.294 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1689 | 0.814 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2780 | 0.877 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1758.9900 | 0.759 |
| funds_mae_12m | 5714.0800 | 36.8760 | 905.2228 | 0.847 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 220.4903 | 0.789 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 525.0728 | 0.803 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 337.4128 | 0.880 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0412 | 0.803 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0635 | 0.838 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3713 | 0.868 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3645 | 0.848 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2879.7900 | 0.799 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1041.6927 | 0.866 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 276.3160 | 0.763 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 605.4372 | 0.807 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 627.7135 | 0.529 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0629 | 0.825 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0819 | 0.885 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3448 | 0.846 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3394 | 0.832 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1041.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 276.3 | 142.8 | 706.1 |
| com_valve | 605.4 | 508.6 | 1010.2 |
| ind_valve | 627.7 | 416.9 | 864.8 |
| pop | 2879.8 | 1754.6 | 7353.4 |
| res_pop | 64.6 | 39.0 | 139.9 |
| com_pop | 6.6 | 4.4 | 12.8 |
| ind_pop | 9.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 42.3 | 25.2 | 89.6 |
| tax_fund | 143.5 | 51.5 | 1444.5 |
| road_spend | 84.6 | 8.2 | 647.3 |
| fire_spend | 53.9 | 0.8 | 474.7 |
| police_spend | 78.2 | 6.0 | 604.1 |
| powered_zones | 8.9 | 0.7 | 8.6 |
| unpowered_zones | 5.4 | 0.6 | 7.0 |
| coal_plants | 0.7 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.3 |
| road_total | 62.5 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1049.9 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 251.3 | 130.7 | 533.4 |
| com_valve | 633.7 | 541.8 | 962.1 |
| ind_valve | 678.2 | 446.9 | 814.5 |
| pop | 2876.1 | 1810.1 | 6881.1 |
| res_pop | 64.3 | 39.6 | 131.0 |
| com_pop | 6.6 | 4.5 | 12.1 |
| ind_pop | 9.9 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.7 | 26.2 | 83.7 |
| tax_fund | 139.7 | 47.1 | 1400.1 |
| road_spend | 79.2 | 8.1 | 645.8 |
| fire_spend | 46.7 | 0.8 | 464.7 |
| police_spend | 69.7 | 6.4 | 591.3 |
| powered_zones | 10.4 | 0.9 | 10.7 |
| unpowered_zones | 5.7 | 0.8 | 7.0 |
| coal_plants | 0.8 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.4 |
| road_total | 62.7 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1011.1 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 369.2 | 187.8 | 1348.3 |
| com_valve | 500.5 | 385.4 | 1188.9 |
| ind_valve | 440.2 | 305.2 | 1051.7 |
| pop | 2893.5 | 1548.5 | 9108.7 |
| res_pop | 65.8 | 37.0 | 172.8 |
| com_pop | 6.9 | 4.2 | 15.7 |
| ind_pop | 9.8 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 36.9 | 21.3 | 111.7 |
| tax_fund | 157.3 | 68.0 | 1609.5 |
| road_spend | 104.8 | 8.8 | 653.2 |
| fire_spend | 80.6 | 1.1 | 512.0 |
| police_spend | 109.9 | 4.6 | 651.4 |
| powered_zones | 3.3 | 0.0 | 0.5 |
| unpowered_zones | 4.1 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 62.0 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.025 | 0.838 |
| traffic | 1.099 | 0.772 |
| pollution | 1.557 | 0.706 |
| land_value | 0.675 | 0.325 |
| crime | 1.034 | 0.566 |
| rate_of_growth | 1.002 | 0.819 |
| fire_coverage | 1.626 | 0.123 |
| police_coverage | 1.031 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.628 | 0.249 | 0.357 | 0.332 to 0.379 | 0.835 | 0.123 | 0.214 | 0.171 to 0.261 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.718 | 0.004 | 0.006 |
| all plans | 12 | 0.370 | 0.042 | 0.031 |
| all plans | 24 | 0.396 | 0.065 | 0.053 |
| state-reading plans | 1 | 0.546 | 0.005 | 0.006 |
| state-reading plans | 12 | 0.372 | 0.047 | 0.031 |
| state-reading plans | 24 | 0.415 | 0.085 | 0.052 |
| open-loop plans | 1 | 0.973 | 0.000 | 0.007 |
| open-loop plans | 12 | 0.532 | 0.015 | 0.033 |
| open-loop plans | 24 | 0.500 | 0.019 | 0.057 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -243.17 |
| tile_cat | -35.07 |
| flags | -17.60 |
| power | -4.25 |
| half | -2638.50 |
| eighth | -41.68 |
| scalars_s2 | -7.90 |
| build_cost | -1.54 |
| scalars | -15.48 |
| ledger | -13.70 |
| bk | -21.29 |
| sc_res_pop | -2.55 |
| sc_com_pop | -0.58 |
| sc_ind_pop | -0.66 |
| sc_powered_zones | -0.22 |
| sc_unpowered_zones | -0.29 |
| sc_coal_plants | -0.04 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.52 |
| sc_res_valve | -1.01 |
| sc_com_valve | -2.08 |
| sc_ind_valve | -1.79 |
| sc_score | -0.37 |
| sc_funds | -1.14 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.45 |
| sc_fire_spend | -0.17 |
| sc_police_spend | -0.14 |
| lg_sprite_cycle | -1.09 |
| lg_total_pop | -1.58 |
| lg_res_hist0 | -0.70 |
| lg_res_hist1 | -0.55 |
| lg_com_hist0 | -0.17 |
| lg_com_hist1 | -0.20 |
| lg_ind_hist0 | -0.25 |
| lg_ind_hist1 | -0.32 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.46 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.15 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.13 |
| lg_city_center_y | -0.08 |
| lg_pollution_max_x | -2.74 |
| lg_pollution_max_y | -2.67 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -7.48 |
| com_rate | -6.45 |
| kl | 7.59 |
| elbo | -3032.52 |

## os_50m_full_samples_002400000_dec-a

samples consumed: 2400000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.288 | 0.284 | 0.286 | 0.265 to 0.305 | 0.182 | 0.172 | 0.177 | 0.150 to 0.207 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.297 | 0.292 | 0.294 | 0.273 to 0.314 | 0.197 | 0.184 | 0.191 | 0.159 to 0.225 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.255 | 0.255 | 0.255 | 0.233 to 0.276 | 0.131 | 0.128 | 0.129 | 0.110 to 0.151 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.804 | 0.204 | 0.009 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.383 / 0.402 |
| all plans | 500 | 12 | 0.551 | 0.146 | 0.059 / 0.003 / 0.378 | 0.048 / 0.026 / 0.103 | 0.378 / 0.428 |
| all plans | 500 | 24 | 0.583 | 0.167 | 0.077 / 0.005 / 0.678 | 0.069 / 0.042 / 0.160 | 0.348 / 0.408 |
| state-reading plans | 394 | 1 | 0.692 | 0.208 | 0.012 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.417 / 0.436 |
| state-reading plans | 394 | 12 | 0.554 | 0.151 | 0.068 / 0.003 / 0.465 | 0.047 / 0.025 / 0.103 | 0.397 / 0.442 |
| state-reading plans | 394 | 24 | 0.601 | 0.184 | 0.094 / 0.005 / 0.791 | 0.067 / 0.044 / 0.150 | 0.361 / 0.412 |
| open-loop plans | 106 | 1 | 1.060 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.231 / 0.257 |
| open-loop plans | 106 | 12 | 0.803 | 0.131 | 0.014 / 0.002 / 0.061 | 0.052 / 0.031 / 0.103 | 0.301 / 0.372 |
| open-loop plans | 106 | 24 | 0.876 | 0.122 | 0.021 / 0.005 / 0.140 | 0.080 / 0.036 / 0.203 | 0.301 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1766 | 0.851 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2860 | 0.902 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2005.8800 | 0.676 |
| funds_mae_12m | 5714.0800 | 36.8760 | 789.1023 | 0.868 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 212.9772 | 0.803 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 514.9217 | 0.815 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 355.4490 | 0.853 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0481 | 0.714 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0589 | 0.850 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3776 | 0.883 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3717 | 0.865 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3300.8300 | 0.724 |
| funds_mae_24m | 7364.5720 | 66.5620 | 903.5778 | 0.885 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 269.8080 | 0.775 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 659.6612 | 0.699 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 682.7012 | 0.406 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0692 | 0.772 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0771 | 0.892 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3485 | 0.855 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3442 | 0.844 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 903.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 269.8 | 142.8 | 706.1 |
| com_valve | 659.7 | 508.6 | 1010.2 |
| ind_valve | 682.7 | 416.9 | 864.8 |
| pop | 3300.8 | 1754.6 | 7353.4 |
| res_pop | 68.3 | 39.0 | 139.9 |
| com_pop | 7.1 | 4.4 | 12.8 |
| ind_pop | 11.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 47.0 | 25.2 | 89.6 |
| tax_fund | 144.3 | 51.5 | 1444.5 |
| road_spend | 80.5 | 8.2 | 647.3 |
| fire_spend | 44.9 | 0.8 | 474.7 |
| police_spend | 68.1 | 6.0 | 604.1 |
| powered_zones | 8.1 | 0.7 | 8.6 |
| unpowered_zones | 4.9 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.3 |
| road_total | 57.6 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 950.5 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 244.5 | 130.7 | 533.4 |
| com_valve | 700.2 | 541.8 | 962.1 |
| ind_valve | 740.9 | 446.9 | 814.5 |
| pop | 3263.4 | 1810.1 | 6881.1 |
| res_pop | 67.7 | 39.6 | 131.0 |
| com_pop | 6.9 | 4.5 | 12.1 |
| ind_pop | 11.5 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.0 | 26.2 | 83.7 |
| tax_fund | 138.7 | 47.1 | 1400.1 |
| road_spend | 75.7 | 8.1 | 645.8 |
| fire_spend | 37.0 | 0.8 | 464.7 |
| police_spend | 59.1 | 6.4 | 591.3 |
| powered_zones | 9.3 | 0.9 | 10.7 |
| unpowered_zones | 5.3 | 0.8 | 7.0 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 57.8 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 729.4 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 363.8 | 187.8 | 1348.3 |
| com_valve | 509.1 | 385.4 | 1188.9 |
| ind_valve | 466.5 | 305.2 | 1051.7 |
| pop | 3440.0 | 1548.5 | 9108.7 |
| res_pop | 70.4 | 37.0 | 172.8 |
| com_pop | 7.6 | 4.2 | 15.7 |
| ind_pop | 11.9 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 39.4 | 21.3 | 111.7 |
| tax_fund | 165.1 | 68.0 | 1609.5 |
| road_spend | 98.3 | 8.8 | 653.2 |
| fire_spend | 74.1 | 1.1 | 512.0 |
| police_spend | 101.6 | 4.6 | 651.4 |
| powered_zones | 3.6 | 0.0 | 0.5 |
| unpowered_zones | 3.3 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 56.8 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.030 | 0.838 |
| traffic | 1.013 | 0.772 |
| pollution | 1.472 | 0.706 |
| land_value | 0.613 | 0.325 |
| crime | 0.980 | 0.566 |
| rate_of_growth | 1.009 | 0.819 |
| fire_coverage | 1.070 | 0.123 |
| police_coverage | 0.846 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.620 | 0.255 | 0.362 | 0.338 to 0.383 | 0.705 | 0.137 | 0.229 | 0.185 to 0.275 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.542 | 0.004 | 0.005 |
| all plans | 12 | 0.354 | 0.035 | 0.044 |
| all plans | 24 | 0.396 | 0.059 | 0.055 |
| state-reading plans | 1 | 0.430 | 0.005 | 0.005 |
| state-reading plans | 12 | 0.357 | 0.040 | 0.042 |
| state-reading plans | 24 | 0.413 | 0.079 | 0.052 |
| open-loop plans | 1 | 0.749 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.494 | 0.011 | 0.047 |
| open-loop plans | 24 | 0.518 | 0.015 | 0.059 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -223.15 |
| tile_cat | -32.13 |
| flags | -15.54 |
| power | -3.47 |
| half | -2463.68 |
| eighth | -37.34 |
| scalars_s2 | -7.27 |
| build_cost | -1.46 |
| scalars | -14.38 |
| ledger | -12.71 |
| bk | -19.83 |
| sc_res_pop | -2.32 |
| sc_com_pop | -0.45 |
| sc_ind_pop | -0.52 |
| sc_powered_zones | -0.19 |
| sc_unpowered_zones | -0.26 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.47 |
| sc_res_valve | -0.96 |
| sc_com_valve | -1.99 |
| sc_ind_valve | -1.51 |
| sc_score | -0.37 |
| sc_funds | -1.05 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.46 |
| sc_fire_spend | -0.19 |
| sc_police_spend | -0.15 |
| lg_sprite_cycle | -0.80 |
| lg_total_pop | -1.55 |
| lg_res_hist0 | -0.49 |
| lg_res_hist1 | -0.37 |
| lg_com_hist0 | -0.10 |
| lg_com_hist1 | -0.09 |
| lg_ind_hist0 | -0.16 |
| lg_ind_hist1 | -0.21 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.48 |
| lg_police_fund | -0.14 |
| lg_fire_fund | -0.19 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.04 |
| lg_city_center_y | -0.03 |
| lg_pollution_max_x | -2.83 |
| lg_pollution_max_y | -2.77 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -5.50 |
| com_rate | -4.41 |
| kl | 11.84 |
| elbo | -2825.63 |

## os_50m_full_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.291 | 0.286 | 0.289 | 0.267 to 0.308 | 0.183 | 0.172 | 0.177 | 0.150 to 0.208 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.300 | 0.294 | 0.297 | 0.276 to 0.317 | 0.197 | 0.185 | 0.191 | 0.160 to 0.225 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.258 | 0.256 | 0.257 | 0.234 to 0.280 | 0.134 | 0.129 | 0.131 | 0.112 to 0.155 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.733 | 0.204 | 0.009 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.382 / 0.402 |
| all plans | 500 | 12 | 0.519 | 0.146 | 0.052 / 0.003 / 0.378 | 0.046 / 0.026 / 0.103 | 0.377 / 0.428 |
| all plans | 500 | 24 | 0.575 | 0.167 | 0.066 / 0.005 / 0.678 | 0.071 / 0.042 / 0.160 | 0.348 / 0.408 |
| state-reading plans | 394 | 1 | 0.691 | 0.208 | 0.011 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.417 / 0.436 |
| state-reading plans | 394 | 12 | 0.521 | 0.151 | 0.061 / 0.003 / 0.465 | 0.045 / 0.025 / 0.103 | 0.397 / 0.442 |
| state-reading plans | 394 | 24 | 0.592 | 0.184 | 0.081 / 0.005 / 0.791 | 0.069 / 0.044 / 0.150 | 0.361 / 0.412 |
| open-loop plans | 106 | 1 | 0.873 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.229 / 0.257 |
| open-loop plans | 106 | 12 | 0.778 | 0.131 | 0.017 / 0.002 / 0.061 | 0.050 / 0.031 / 0.103 | 0.301 / 0.372 |
| open-loop plans | 106 | 24 | 0.939 | 0.122 | 0.022 / 0.005 / 0.140 | 0.078 / 0.036 / 0.203 | 0.300 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1773 | 0.855 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2886 | 0.910 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1986.9150 | 0.683 |
| funds_mae_12m | 5714.0800 | 36.8760 | 693.3438 | 0.884 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 216.1827 | 0.797 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 514.3895 | 0.815 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 364.6653 | 0.839 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0463 | 0.736 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0523 | 0.868 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3775 | 0.883 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3720 | 0.866 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3457.5450 | 0.696 |
| funds_mae_24m | 7364.5720 | 66.5620 | 800.0963 | 0.899 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 283.2633 | 0.751 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 663.8630 | 0.691 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 695.5118 | 0.378 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0710 | 0.756 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0662 | 0.909 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3478 | 0.853 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3435 | 0.842 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 800.1 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 283.3 | 142.8 | 706.1 |
| com_valve | 663.9 | 508.6 | 1010.2 |
| ind_valve | 695.5 | 416.9 | 864.8 |
| pop | 3457.5 | 1754.6 | 7353.4 |
| res_pop | 71.7 | 39.0 | 139.9 |
| com_pop | 7.2 | 4.4 | 12.8 |
| ind_pop | 12.0 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 54.8 | 25.2 | 89.6 |
| tax_fund | 135.4 | 51.5 | 1444.5 |
| road_spend | 81.0 | 8.2 | 647.3 |
| fire_spend | 48.1 | 0.8 | 474.7 |
| police_spend | 66.2 | 6.0 | 604.1 |
| powered_zones | 8.1 | 0.7 | 8.6 |
| unpowered_zones | 4.8 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 54.8 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 824.2 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 258.0 | 130.7 | 533.4 |
| com_valve | 701.1 | 541.8 | 962.1 |
| ind_valve | 753.5 | 446.9 | 814.5 |
| pop | 3386.9 | 1810.1 | 6881.1 |
| res_pop | 71.2 | 39.6 | 131.0 |
| com_pop | 7.0 | 4.5 | 12.1 |
| ind_pop | 11.9 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 57.6 | 26.2 | 83.7 |
| tax_fund | 128.8 | 47.1 | 1400.1 |
| road_spend | 74.2 | 8.1 | 645.8 |
| fire_spend | 41.4 | 0.8 | 464.7 |
| police_spend | 59.0 | 6.4 | 591.3 |
| powered_zones | 9.1 | 0.9 | 10.7 |
| unpowered_zones | 5.2 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 54.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 710.3 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 377.2 | 187.8 | 1348.3 |
| com_valve | 525.4 | 385.4 | 1188.9 |
| ind_valve | 479.8 | 305.2 | 1051.7 |
| pop | 3720.1 | 1548.5 | 9108.7 |
| res_pop | 73.3 | 37.0 | 172.8 |
| com_pop | 7.9 | 4.2 | 15.7 |
| ind_pop | 12.1 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 44.5 | 21.3 | 111.7 |
| tax_fund | 160.2 | 68.0 | 1609.5 |
| road_spend | 106.0 | 8.8 | 653.2 |
| fire_spend | 73.0 | 1.1 | 512.0 |
| police_spend | 93.2 | 4.6 | 651.4 |
| powered_zones | 4.2 | 0.0 | 0.5 |
| unpowered_zones | 3.2 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 54.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.034 | 0.838 |
| traffic | 1.016 | 0.772 |
| pollution | 1.486 | 0.706 |
| land_value | 0.609 | 0.325 |
| crime | 0.981 | 0.566 |
| rate_of_growth | 1.010 | 0.819 |
| fire_coverage | 1.128 | 0.123 |
| police_coverage | 0.847 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.584 | 0.258 | 0.358 | 0.335 to 0.379 | 0.556 | 0.139 | 0.223 | 0.181 to 0.265 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.458 | 0.003 | 0.007 |
| all plans | 12 | 0.338 | 0.033 | 0.039 |
| all plans | 24 | 0.401 | 0.057 | 0.055 |
| state-reading plans | 1 | 0.463 | 0.004 | 0.006 |
| state-reading plans | 12 | 0.339 | 0.037 | 0.039 |
| state-reading plans | 24 | 0.416 | 0.070 | 0.052 |
| open-loop plans | 1 | 0.500 | 0.000 | 0.007 |
| open-loop plans | 12 | 0.503 | 0.015 | 0.040 |
| open-loop plans | 24 | 0.627 | 0.020 | 0.068 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -218.38 |
| tile_cat | -31.40 |
| flags | -14.96 |
| power | -3.08 |
| half | -2417.52 |
| eighth | -36.35 |
| scalars_s2 | -6.89 |
| build_cost | -1.42 |
| scalars | -13.92 |
| ledger | -12.57 |
| bk | -19.61 |
| sc_res_pop | -2.18 |
| sc_com_pop | -0.36 |
| sc_ind_pop | -0.43 |
| sc_powered_zones | -0.17 |
| sc_unpowered_zones | -0.23 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.45 |
| sc_res_valve | -0.95 |
| sc_com_valve | -1.97 |
| sc_ind_valve | -1.43 |
| sc_score | -0.39 |
| sc_funds | -1.02 |
| sc_tax_fund | -0.45 |
| sc_road_spend | -0.47 |
| sc_fire_spend | -0.20 |
| sc_police_spend | -0.16 |
| lg_sprite_cycle | -0.74 |
| lg_total_pop | -1.53 |
| lg_res_hist0 | -0.44 |
| lg_res_hist1 | -0.31 |
| lg_com_hist0 | -0.08 |
| lg_com_hist1 | -0.07 |
| lg_ind_hist0 | -0.13 |
| lg_ind_hist1 | -0.17 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.50 |
| lg_police_fund | -0.15 |
| lg_fire_fund | -0.21 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.86 |
| lg_pollution_max_y | -2.86 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -5.05 |
| com_rate | -4.04 |
| kl | 12.55 |
| elbo | -2771.23 |

## os_50m_full_samples_003600000_dec-a

samples consumed: 3600000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.296 | 0.285 | 0.291 | 0.270 to 0.309 | 0.188 | 0.171 | 0.179 | 0.152 to 0.209 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.305 | 0.292 | 0.298 | 0.277 to 0.318 | 0.203 | 0.183 | 0.193 | 0.161 to 0.227 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.265 | 0.259 | 0.262 | 0.240 to 0.283 | 0.137 | 0.129 | 0.133 | 0.114 to 0.154 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.691 | 0.204 | 0.007 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.388 / 0.402 |
| all plans | 500 | 12 | 0.487 | 0.146 | 0.049 / 0.003 / 0.378 | 0.048 / 0.026 / 0.103 | 0.377 / 0.428 |
| all plans | 500 | 24 | 0.541 | 0.167 | 0.066 / 0.005 / 0.678 | 0.070 / 0.042 / 0.160 | 0.347 / 0.408 |
| state-reading plans | 394 | 1 | 0.638 | 0.208 | 0.009 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.422 / 0.436 |
| state-reading plans | 394 | 12 | 0.485 | 0.151 | 0.054 / 0.003 / 0.465 | 0.047 / 0.025 / 0.103 | 0.397 / 0.442 |
| state-reading plans | 394 | 24 | 0.556 | 0.184 | 0.079 / 0.005 / 0.791 | 0.068 / 0.044 / 0.150 | 0.360 / 0.412 |
| open-loop plans | 106 | 1 | 0.831 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.234 / 0.257 |
| open-loop plans | 106 | 12 | 0.812 | 0.131 | 0.019 / 0.002 / 0.061 | 0.050 / 0.031 / 0.103 | 0.299 / 0.372 |
| open-loop plans | 106 | 24 | 0.975 | 0.122 | 0.028 / 0.005 / 0.140 | 0.078 / 0.036 / 0.203 | 0.297 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1790 | 0.863 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2906 | 0.916 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2037.6350 | 0.666 |
| funds_mae_12m | 5714.0800 | 36.8760 | 653.2780 | 0.891 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 210.8233 | 0.807 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 509.6182 | 0.821 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 355.2862 | 0.853 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0477 | 0.718 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0488 | 0.877 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3771 | 0.882 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3716 | 0.865 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3492.8150 | 0.690 |
| funds_mae_24m | 7364.5720 | 66.5620 | 790.5633 | 0.901 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 277.6550 | 0.761 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 657.7840 | 0.703 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 672.8148 | 0.429 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0697 | 0.767 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0660 | 0.909 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3467 | 0.851 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3423 | 0.839 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 790.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 277.7 | 142.8 | 706.1 |
| com_valve | 657.8 | 508.6 | 1010.2 |
| ind_valve | 672.8 | 416.9 | 864.8 |
| pop | 3492.8 | 1754.6 | 7353.4 |
| res_pop | 75.2 | 39.0 | 139.9 |
| com_pop | 7.4 | 4.4 | 12.8 |
| ind_pop | 11.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 61.0 | 25.2 | 89.6 |
| tax_fund | 141.1 | 51.5 | 1444.5 |
| road_spend | 78.9 | 8.2 | 647.3 |
| fire_spend | 42.2 | 0.8 | 474.7 |
| police_spend | 68.7 | 6.0 | 604.1 |
| powered_zones | 7.8 | 0.7 | 8.6 |
| unpowered_zones | 4.6 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 52.0 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 798.8 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 246.0 | 130.7 | 533.4 |
| com_valve | 693.9 | 541.8 | 962.1 |
| ind_valve | 730.8 | 446.9 | 814.5 |
| pop | 3437.9 | 1810.1 | 6881.1 |
| res_pop | 74.2 | 39.6 | 131.0 |
| com_pop | 7.2 | 4.5 | 12.1 |
| ind_pop | 11.6 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 64.0 | 26.2 | 83.7 |
| tax_fund | 134.0 | 47.1 | 1400.1 |
| road_spend | 75.1 | 8.1 | 645.8 |
| fire_spend | 36.7 | 0.8 | 464.7 |
| police_spend | 59.8 | 6.4 | 591.3 |
| powered_zones | 8.6 | 0.9 | 10.7 |
| unpowered_zones | 5.0 | 0.8 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 52.4 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 759.9 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 395.2 | 187.8 | 1348.3 |
| com_valve | 523.5 | 385.4 | 1188.9 |
| ind_valve | 457.3 | 305.2 | 1051.7 |
| pop | 3697.0 | 1548.5 | 9108.7 |
| res_pop | 79.2 | 37.0 | 172.8 |
| com_pop | 8.0 | 4.2 | 15.7 |
| ind_pop | 12.1 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.5 | 21.3 | 111.7 |
| tax_fund | 167.6 | 68.0 | 1609.5 |
| road_spend | 93.4 | 8.8 | 653.2 |
| fire_spend | 62.5 | 1.1 | 512.0 |
| police_spend | 101.7 | 4.6 | 651.4 |
| powered_zones | 4.8 | 0.0 | 0.5 |
| unpowered_zones | 3.2 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 50.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.033 | 0.838 |
| traffic | 1.005 | 0.772 |
| pollution | 1.486 | 0.706 |
| land_value | 0.613 | 0.325 |
| crime | 0.977 | 0.566 |
| rate_of_growth | 0.999 | 0.819 |
| fire_coverage | 1.092 | 0.123 |
| police_coverage | 0.877 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.558 | 0.259 | 0.354 | 0.331 to 0.374 | 0.477 | 0.139 | 0.216 | 0.178 to 0.255 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.482 | 0.003 | 0.006 |
| all plans | 12 | 0.331 | 0.029 | 0.045 |
| all plans | 24 | 0.387 | 0.060 | 0.058 |
| state-reading plans | 1 | 0.452 | 0.004 | 0.005 |
| state-reading plans | 12 | 0.329 | 0.032 | 0.044 |
| state-reading plans | 24 | 0.402 | 0.066 | 0.056 |
| open-loop plans | 1 | 0.559 | 0.000 | 0.007 |
| open-loop plans | 12 | 0.515 | 0.017 | 0.046 |
| open-loop plans | 24 | 0.614 | 0.025 | 0.067 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -215.84 |
| tile_cat | -31.00 |
| flags | -14.72 |
| power | -2.97 |
| half | -2387.43 |
| eighth | -35.52 |
| scalars_s2 | -6.44 |
| build_cost | -1.35 |
| scalars | -13.56 |
| ledger | -12.82 |
| bk | -19.94 |
| sc_res_pop | -2.01 |
| sc_com_pop | -0.26 |
| sc_ind_pop | -0.34 |
| sc_powered_zones | -0.15 |
| sc_unpowered_zones | -0.20 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.42 |
| sc_res_valve | -0.95 |
| sc_com_valve | -1.99 |
| sc_ind_valve | -1.50 |
| sc_score | -0.39 |
| sc_funds | -1.02 |
| sc_tax_fund | -0.45 |
| sc_road_spend | -0.47 |
| sc_fire_spend | -0.20 |
| sc_police_spend | -0.17 |
| lg_sprite_cycle | -0.76 |
| lg_total_pop | -1.53 |
| lg_res_hist0 | -0.48 |
| lg_res_hist1 | -0.33 |
| lg_com_hist0 | -0.13 |
| lg_com_hist1 | -0.09 |
| lg_ind_hist0 | -0.17 |
| lg_ind_hist1 | -0.20 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.52 |
| lg_police_fund | -0.15 |
| lg_fire_fund | -0.21 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.87 |
| lg_pollution_max_y | -2.88 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.75 |
| com_rate | -3.99 |
| kl | 13.10 |
| elbo | -2737.06 |

## os_50m_full_samples_004800000_dec-a

samples consumed: 4800000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.305 | 0.287 | 0.296 | 0.275 to 0.314 | 0.195 | 0.171 | 0.182 | 0.155 to 0.212 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.313 | 0.295 | 0.304 | 0.282 to 0.323 | 0.211 | 0.183 | 0.196 | 0.165 to 0.230 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.273 | 0.260 | 0.266 | 0.244 to 0.288 | 0.142 | 0.128 | 0.135 | 0.116 to 0.157 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.543 | 0.204 | 0.005 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.393 / 0.402 |
| all plans | 500 | 12 | 0.408 | 0.146 | 0.039 / 0.003 / 0.378 | 0.052 / 0.026 / 0.103 | 0.376 / 0.428 |
| all plans | 500 | 24 | 0.476 | 0.167 | 0.057 / 0.005 / 0.678 | 0.074 / 0.042 / 0.160 | 0.344 / 0.408 |
| state-reading plans | 394 | 1 | 0.533 | 0.208 | 0.007 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.428 / 0.436 |
| state-reading plans | 394 | 12 | 0.407 | 0.151 | 0.043 / 0.003 / 0.465 | 0.051 / 0.025 / 0.103 | 0.395 / 0.442 |
| state-reading plans | 394 | 24 | 0.492 | 0.184 | 0.064 / 0.005 / 0.791 | 0.071 / 0.044 / 0.150 | 0.357 / 0.412 |
| open-loop plans | 106 | 1 | 0.567 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.239 / 0.257 |
| open-loop plans | 106 | 12 | 0.647 | 0.131 | 0.022 / 0.002 / 0.061 | 0.057 / 0.031 / 0.103 | 0.299 / 0.372 |
| open-loop plans | 106 | 24 | 0.849 | 0.122 | 0.032 / 0.005 / 0.140 | 0.088 / 0.036 / 0.203 | 0.295 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1821 | 0.878 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2957 | 0.932 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2242.4850 | 0.598 |
| funds_mae_12m | 5714.0800 | 36.8760 | 572.1387 | 0.906 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 240.4067 | 0.751 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 499.0565 | 0.833 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 340.9482 | 0.875 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0523 | 0.659 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0393 | 0.903 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3758 | 0.879 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3691 | 0.859 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3771.1000 | 0.640 |
| funds_mae_24m | 7364.5720 | 66.5620 | 691.6760 | 0.914 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 312.8635 | 0.698 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 655.0440 | 0.708 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 671.8770 | 0.431 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0742 | 0.729 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0570 | 0.922 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3438 | 0.843 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3387 | 0.830 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 691.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 312.9 | 142.8 | 706.1 |
| com_valve | 655.0 | 508.6 | 1010.2 |
| ind_valve | 671.9 | 416.9 | 864.8 |
| pop | 3771.1 | 1754.6 | 7353.4 |
| res_pop | 82.9 | 39.0 | 139.9 |
| com_pop | 7.8 | 4.4 | 12.8 |
| ind_pop | 12.1 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 65.4 | 25.2 | 89.6 |
| tax_fund | 157.4 | 51.5 | 1444.5 |
| road_spend | 78.9 | 8.2 | 647.3 |
| fire_spend | 45.6 | 0.8 | 474.7 |
| police_spend | 75.1 | 6.0 | 604.1 |
| powered_zones | 6.4 | 0.7 | 8.6 |
| unpowered_zones | 4.2 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 45.2 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 685.3 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 292.6 | 130.7 | 533.4 |
| com_valve | 683.4 | 541.8 | 962.1 |
| ind_valve | 726.7 | 446.9 | 814.5 |
| pop | 3648.3 | 1810.1 | 6881.1 |
| res_pop | 80.2 | 39.6 | 131.0 |
| com_pop | 7.7 | 4.5 | 12.1 |
| ind_pop | 12.1 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 68.8 | 26.2 | 83.7 |
| tax_fund | 150.6 | 47.1 | 1400.1 |
| road_spend | 74.0 | 8.1 | 645.8 |
| fire_spend | 36.6 | 0.8 | 464.7 |
| police_spend | 61.6 | 6.4 | 591.3 |
| powered_zones | 6.9 | 0.9 | 10.7 |
| unpowered_zones | 4.6 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.4 |
| road_total | 45.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 715.4 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 388.3 | 187.8 | 1348.3 |
| com_valve | 549.6 | 385.4 | 1188.9 |
| ind_valve | 468.0 | 305.2 | 1051.7 |
| pop | 4227.7 | 1548.5 | 9108.7 |
| res_pop | 93.1 | 37.0 | 172.8 |
| com_pop | 8.2 | 4.2 | 15.7 |
| ind_pop | 12.4 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 52.5 | 21.3 | 111.7 |
| tax_fund | 182.5 | 68.0 | 1609.5 |
| road_spend | 97.3 | 8.8 | 653.2 |
| fire_spend | 79.0 | 1.1 | 512.0 |
| police_spend | 125.3 | 4.6 | 651.4 |
| powered_zones | 4.2 | 0.0 | 0.5 |
| unpowered_zones | 2.7 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 42.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.045 | 0.838 |
| traffic | 0.999 | 0.772 |
| pollution | 1.481 | 0.706 |
| land_value | 0.611 | 0.325 |
| crime | 0.969 | 0.566 |
| rate_of_growth | 1.002 | 0.819 |
| fire_coverage | 1.107 | 0.123 |
| police_coverage | 0.893 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.532 | 0.265 | 0.354 | 0.331 to 0.373 | 0.418 | 0.140 | 0.209 | 0.172 to 0.248 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.403 | 0.003 | 0.006 |
| all plans | 12 | 0.305 | 0.027 | 0.046 |
| all plans | 24 | 0.370 | 0.050 | 0.061 |
| state-reading plans | 1 | 0.401 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.304 | 0.030 | 0.044 |
| state-reading plans | 24 | 0.385 | 0.054 | 0.058 |
| open-loop plans | 1 | 0.414 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.466 | 0.016 | 0.051 |
| open-loop plans | 24 | 0.622 | 0.034 | 0.079 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -211.89 |
| tile_cat | -30.56 |
| flags | -14.61 |
| power | -2.76 |
| half | -2345.22 |
| eighth | -34.67 |
| scalars_s2 | -5.64 |
| build_cost | -1.17 |
| scalars | -12.58 |
| ledger | -12.80 |
| bk | -19.75 |
| sc_res_pop | -1.67 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.23 |
| sc_powered_zones | -0.09 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.38 |
| sc_res_valve | -0.95 |
| sc_com_valve | -1.95 |
| sc_ind_valve | -1.23 |
| sc_score | -0.44 |
| sc_funds | -0.96 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.52 |
| sc_fire_spend | -0.23 |
| sc_police_spend | -0.20 |
| lg_sprite_cycle | -0.79 |
| lg_total_pop | -1.45 |
| lg_res_hist0 | -0.33 |
| lg_res_hist1 | -0.30 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.09 |
| lg_ind_hist0 | -0.07 |
| lg_ind_hist1 | -0.18 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.57 |
| lg_police_fund | -0.18 |
| lg_fire_fund | -0.31 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.92 |
| lg_pollution_max_y | -3.01 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.38 |
| com_rate | -3.77 |
| kl | 14.00 |
| elbo | -2688.42 |

## os_50m_full_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.308 | 0.288 | 0.298 | 0.277 to 0.316 | 0.197 | 0.169 | 0.182 | 0.156 to 0.212 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.315 | 0.296 | 0.305 | 0.284 to 0.324 | 0.212 | 0.182 | 0.196 | 0.165 to 0.230 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.280 | 0.261 | 0.270 | 0.247 to 0.291 | 0.147 | 0.126 | 0.136 | 0.116 to 0.158 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.507 | 0.204 | 0.004 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.398 / 0.402 |
| all plans | 500 | 12 | 0.395 | 0.146 | 0.038 / 0.003 / 0.378 | 0.054 / 0.026 / 0.103 | 0.375 / 0.428 |
| all plans | 500 | 24 | 0.484 | 0.167 | 0.057 / 0.005 / 0.678 | 0.080 / 0.042 / 0.160 | 0.340 / 0.408 |
| state-reading plans | 394 | 1 | 0.501 | 0.208 | 0.005 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.432 / 0.436 |
| state-reading plans | 394 | 12 | 0.396 | 0.151 | 0.042 / 0.003 / 0.465 | 0.054 / 0.025 / 0.103 | 0.394 / 0.442 |
| state-reading plans | 394 | 24 | 0.502 | 0.184 | 0.065 / 0.005 / 0.791 | 0.077 / 0.044 / 0.150 | 0.351 / 0.412 |
| open-loop plans | 106 | 1 | 0.511 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.243 / 0.257 |
| open-loop plans | 106 | 12 | 0.637 | 0.131 | 0.023 / 0.002 / 0.061 | 0.057 / 0.031 / 0.103 | 0.299 / 0.372 |
| open-loop plans | 106 | 24 | 0.898 | 0.122 | 0.034 / 0.005 / 0.140 | 0.089 / 0.036 / 0.203 | 0.295 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1822 | 0.878 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2977 | 0.939 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2351.8150 | 0.561 |
| funds_mae_12m | 5714.0800 | 36.8760 | 574.5113 | 0.905 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 243.4462 | 0.745 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 498.8335 | 0.834 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 343.4937 | 0.871 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0544 | 0.632 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0383 | 0.905 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3746 | 0.876 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3669 | 0.854 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 4045.7050 | 0.591 |
| funds_mae_24m | 7364.5720 | 66.5620 | 711.5655 | 0.912 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 325.9237 | 0.675 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 656.1660 | 0.706 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 662.6548 | 0.451 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0797 | 0.682 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0569 | 0.922 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3396 | 0.833 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3335 | 0.818 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 711.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 325.9 | 142.8 | 706.1 |
| com_valve | 656.2 | 508.6 | 1010.2 |
| ind_valve | 662.7 | 416.9 | 864.8 |
| pop | 4045.7 | 1754.6 | 7353.4 |
| res_pop | 87.1 | 39.0 | 139.9 |
| com_pop | 8.3 | 4.4 | 12.8 |
| ind_pop | 12.8 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 79.7 | 25.2 | 89.6 |
| tax_fund | 180.0 | 51.5 | 1444.5 |
| road_spend | 81.1 | 8.2 | 647.3 |
| fire_spend | 45.3 | 0.8 | 474.7 |
| police_spend | 85.6 | 6.0 | 604.1 |
| powered_zones | 7.0 | 0.7 | 8.6 |
| unpowered_zones | 4.2 | 0.6 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 43.7 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 707.3 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 306.9 | 130.7 | 533.4 |
| com_valve | 677.8 | 541.8 | 962.1 |
| ind_valve | 716.2 | 446.9 | 814.5 |
| pop | 3957.9 | 1810.1 | 6881.1 |
| res_pop | 85.4 | 39.6 | 131.0 |
| com_pop | 8.2 | 4.5 | 12.1 |
| ind_pop | 12.6 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 85.0 | 26.2 | 83.7 |
| tax_fund | 177.1 | 47.1 | 1400.1 |
| road_spend | 77.2 | 8.1 | 645.8 |
| fire_spend | 38.8 | 0.8 | 464.7 |
| police_spend | 70.2 | 6.4 | 591.3 |
| powered_zones | 7.7 | 0.9 | 10.7 |
| unpowered_zones | 4.7 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.4 |
| road_total | 44.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 727.4 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 396.6 | 187.8 | 1348.3 |
| com_valve | 575.9 | 385.4 | 1188.9 |
| ind_valve | 463.6 | 305.2 | 1051.7 |
| pop | 4372.2 | 1548.5 | 9108.7 |
| res_pop | 93.4 | 37.0 | 172.8 |
| com_pop | 8.6 | 4.2 | 15.7 |
| ind_pop | 13.5 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 60.1 | 21.3 | 111.7 |
| tax_fund | 190.9 | 68.0 | 1609.5 |
| road_spend | 95.4 | 8.8 | 653.2 |
| fire_spend | 69.4 | 1.1 | 512.0 |
| police_spend | 142.9 | 4.6 | 651.4 |
| powered_zones | 4.7 | 0.0 | 0.5 |
| unpowered_zones | 2.7 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 39.6 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.059 | 0.838 |
| traffic | 1.017 | 0.772 |
| pollution | 1.505 | 0.706 |
| land_value | 0.628 | 0.325 |
| crime | 0.993 | 0.566 |
| rate_of_growth | 1.000 | 0.819 |
| fire_coverage | 1.335 | 0.123 |
| police_coverage | 1.000 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.526 | 0.267 | 0.354 | 0.333 to 0.374 | 0.404 | 0.141 | 0.209 | 0.173 to 0.247 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.385 | 0.002 | 0.006 |
| all plans | 12 | 0.307 | 0.028 | 0.048 |
| all plans | 24 | 0.393 | 0.049 | 0.068 |
| state-reading plans | 1 | 0.389 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.309 | 0.029 | 0.047 |
| state-reading plans | 24 | 0.411 | 0.057 | 0.067 |
| open-loop plans | 1 | 0.373 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.457 | 0.020 | 0.049 |
| open-loop plans | 24 | 0.713 | 0.036 | 0.076 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -210.27 |
| tile_cat | -30.46 |
| flags | -14.55 |
| power | -2.72 |
| half | -2322.13 |
| eighth | -34.25 |
| scalars_s2 | -5.25 |
| build_cost | -0.97 |
| scalars | -12.27 |
| ledger | -14.01 |
| bk | -21.03 |
| sc_res_pop | -1.48 |
| sc_com_pop | -0.13 |
| sc_ind_pop | -0.20 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.04 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.36 |
| sc_res_valve | -0.98 |
| sc_com_valve | -1.94 |
| sc_ind_valve | -1.07 |
| sc_score | -0.49 |
| sc_funds | -0.92 |
| sc_tax_fund | -0.49 |
| sc_road_spend | -0.58 |
| sc_fire_spend | -0.29 |
| sc_police_spend | -0.26 |
| lg_sprite_cycle | -0.87 |
| lg_total_pop | -1.38 |
| lg_res_hist0 | -0.23 |
| lg_res_hist1 | -0.73 |
| lg_com_hist0 | -0.07 |
| lg_com_hist1 | -0.25 |
| lg_ind_hist0 | -0.07 |
| lg_ind_hist1 | -0.41 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.06 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.63 |
| lg_police_fund | -0.20 |
| lg_fire_fund | -0.53 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.94 |
| lg_pollution_max_y | -3.16 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.35 |
| terrain | -4.26 |
| com_rate | -3.69 |
| kl | 14.63 |
| elbo | -2664.23 |
