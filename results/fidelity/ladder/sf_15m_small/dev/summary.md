## sf_15m_small_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.230 | 0.292 | 0.257 | 0.238 to 0.276 | 0.127 | 0.176 | 0.148 | 0.127 to 0.172 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.237 | 0.299 | 0.264 | 0.244 to 0.283 | 0.137 | 0.188 | 0.159 | 0.134 to 0.187 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.205 | 0.269 | 0.233 | 0.210 to 0.255 | 0.095 | 0.136 | 0.112 | 0.097 to 0.131 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.737 | 0.204 | 0.005 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.357 / 0.402 |
| all plans | 500 | 12 | 0.558 | 0.146 | 0.056 / 0.003 / 0.378 | 0.048 / 0.026 / 0.103 | 0.313 / 0.428 |
| all plans | 500 | 24 | 0.693 | 0.167 | 0.103 / 0.005 / 0.678 | 0.088 / 0.042 / 0.160 | 0.277 / 0.408 |
| state-reading plans | 394 | 1 | 0.844 | 0.208 | 0.006 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.391 / 0.436 |
| state-reading plans | 394 | 12 | 0.551 | 0.151 | 0.061 / 0.003 / 0.465 | 0.050 / 0.025 / 0.103 | 0.330 / 0.442 |
| state-reading plans | 394 | 24 | 0.698 | 0.184 | 0.114 / 0.005 / 0.791 | 0.088 / 0.044 / 0.150 | 0.288 / 0.412 |
| open-loop plans | 106 | 1 | 0.684 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.212 / 0.257 |
| open-loop plans | 106 | 12 | 1.141 | 0.131 | 0.037 / 0.002 / 0.061 | 0.043 / 0.031 / 0.103 | 0.248 / 0.372 |
| open-loop plans | 106 | 24 | 1.439 | 0.122 | 0.068 / 0.005 / 0.140 | 0.087 / 0.036 / 0.203 | 0.235 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1478 | 0.713 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2575 | 0.812 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2035.5350 | 0.667 |
| funds_mae_12m | 5714.0800 | 36.8760 | 916.1855 | 0.845 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 225.2012 | 0.780 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 572.4662 | 0.747 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 387.9552 | 0.804 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0480 | 0.715 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0559 | 0.858 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3131 | 0.732 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3113 | 0.724 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 4117.5150 | 0.578 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1256.6760 | 0.837 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 335.7898 | 0.657 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 625.4745 | 0.767 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 672.7815 | 0.429 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0880 | 0.611 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1035 | 0.853 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2769 | 0.680 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2754 | 0.675 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1256.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 335.8 | 142.8 | 706.1 |
| com_valve | 625.5 | 508.6 | 1010.2 |
| ind_valve | 672.8 | 416.9 | 864.8 |
| pop | 4117.5 | 1754.6 | 7353.4 |
| res_pop | 96.5 | 39.0 | 139.9 |
| com_pop | 8.3 | 4.4 | 12.8 |
| ind_pop | 13.1 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 79.7 | 25.2 | 89.6 |
| tax_fund | 175.8 | 51.5 | 1444.5 |
| road_spend | 103.4 | 8.2 | 647.3 |
| fire_spend | 61.1 | 0.8 | 474.7 |
| police_spend | 102.4 | 6.0 | 604.1 |
| powered_zones | 8.8 | 0.7 | 8.6 |
| unpowered_zones | 5.8 | 0.6 | 7.0 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.3 |
| road_total | 68.1 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1181.6 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 303.9 | 130.7 | 533.4 |
| com_valve | 644.4 | 541.8 | 962.1 |
| ind_valve | 727.4 | 446.9 | 814.5 |
| pop | 4168.4 | 1810.1 | 6881.1 |
| res_pop | 94.4 | 39.6 | 131.0 |
| com_pop | 8.4 | 4.5 | 12.1 |
| ind_pop | 13.3 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 84.0 | 26.2 | 83.7 |
| tax_fund | 174.5 | 47.1 | 1400.1 |
| road_spend | 97.6 | 8.1 | 645.8 |
| fire_spend | 57.5 | 0.8 | 464.7 |
| police_spend | 101.0 | 6.4 | 591.3 |
| powered_zones | 9.4 | 0.9 | 10.7 |
| unpowered_zones | 6.2 | 0.8 | 7.0 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.4 |
| road_total | 68.5 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1535.6 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 454.3 | 187.8 | 1348.3 |
| com_valve | 555.0 | 385.4 | 1188.9 |
| ind_valve | 469.8 | 305.2 | 1051.7 |
| pop | 3928.3 | 1548.5 | 9108.7 |
| res_pop | 104.3 | 37.0 | 172.8 |
| com_pop | 7.9 | 4.2 | 15.7 |
| ind_pop | 12.5 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 63.9 | 21.3 | 111.7 |
| tax_fund | 180.6 | 68.0 | 1609.5 |
| road_spend | 124.9 | 8.8 | 653.2 |
| fire_spend | 74.8 | 1.1 | 512.0 |
| police_spend | 107.6 | 4.6 | 651.4 |
| powered_zones | 6.7 | 0.0 | 0.5 |
| unpowered_zones | 4.5 | 0.0 | 6.7 |
| coal_plants | 0.5 | 0.0 | 0.1 |
| nuclear_plants | 0.7 | 0.0 | 0.2 |
| road_total | 66.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.257 | 0.838 |
| traffic | 1.140 | 0.772 |
| pollution | 1.644 | 0.706 |
| land_value | 0.741 | 0.325 |
| crime | 1.257 | 0.566 |
| rate_of_growth | 1.275 | 0.819 |
| fire_coverage | 1.699 | 0.123 |
| police_coverage | 1.058 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.506 | 0.274 | 0.356 | 0.334 to 0.375 | 0.453 | 0.143 | 0.218 | 0.183 to 0.257 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.559 | 0.002 | 0.006 |
| all plans | 12 | 0.380 | 0.048 | 0.033 |
| all plans | 24 | 0.498 | 0.106 | 0.073 |
| state-reading plans | 1 | 0.643 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.376 | 0.055 | 0.033 |
| state-reading plans | 24 | 0.507 | 0.117 | 0.072 |
| open-loop plans | 1 | 0.490 | 0.001 | 0.007 |
| open-loop plans | 12 | 0.677 | 0.033 | 0.032 |
| open-loop plans | 24 | 0.917 | 0.069 | 0.077 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -245.04 |
| tile_cat | -36.48 |
| flags | -22.27 |
| power | -4.83 |
| half | -2591.13 |
| eighth | -39.57 |
| scalars_s2 | -5.75 |
| build_cost | -1.19 |
| scalars | -15.64 |
| ledger | -17.39 |
| bk | -27.28 |
| sc_res_pop | -1.74 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.24 |
| sc_powered_zones | -0.09 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.38 |
| sc_res_valve | -1.08 |
| sc_com_valve | -2.15 |
| sc_ind_valve | -1.73 |
| sc_score | -0.92 |
| sc_funds | -1.42 |
| sc_tax_fund | -0.77 |
| sc_road_spend | -1.22 |
| sc_fire_spend | -0.33 |
| sc_police_spend | -0.28 |
| lg_sprite_cycle | -0.82 |
| lg_total_pop | -2.13 |
| lg_res_hist0 | -0.94 |
| lg_res_hist1 | -0.45 |
| lg_com_hist0 | -0.20 |
| lg_com_hist1 | -0.12 |
| lg_ind_hist0 | -0.28 |
| lg_ind_hist1 | -0.22 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.01 |
| lg_need_hospital | -0.09 |
| lg_need_church | -0.07 |
| lg_road_fund | -1.18 |
| lg_police_fund | -0.23 |
| lg_fire_fund | -0.24 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.31 |
| lg_city_center_y | -0.14 |
| lg_pollution_max_x | -3.67 |
| lg_pollution_max_y | -3.55 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.62 |
| terrain | -6.70 |
| com_rate | -6.45 |
| kl | 12.92 |
| elbo | -2999.60 |

## sf_15m_small_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.228 | 0.294 | 0.257 | 0.237 to 0.277 | 0.127 | 0.178 | 0.148 | 0.128 to 0.174 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.234 | 0.301 | 0.264 | 0.243 to 0.283 | 0.136 | 0.190 | 0.158 | 0.134 to 0.188 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.206 | 0.269 | 0.233 | 0.213 to 0.255 | 0.098 | 0.139 | 0.115 | 0.101 to 0.132 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.598 | 0.204 | 0.003 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.361 / 0.402 |
| all plans | 500 | 12 | 0.554 | 0.146 | 0.068 / 0.003 / 0.378 | 0.053 / 0.026 / 0.103 | 0.295 / 0.428 |
| all plans | 500 | 24 | 0.775 | 0.167 | 0.139 / 0.005 / 0.678 | 0.109 / 0.042 / 0.160 | 0.252 / 0.408 |
| state-reading plans | 394 | 1 | 0.621 | 0.208 | 0.004 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.396 / 0.436 |
| state-reading plans | 394 | 12 | 0.549 | 0.151 | 0.073 / 0.003 / 0.465 | 0.052 / 0.025 / 0.103 | 0.312 / 0.442 |
| state-reading plans | 394 | 24 | 0.778 | 0.184 | 0.156 / 0.005 / 0.791 | 0.108 / 0.044 / 0.150 | 0.264 / 0.412 |
| open-loop plans | 106 | 1 | 0.601 | 0.199 | 0.000 / 0.000 / 0.000 | 0.010 / 0.008 / 0.007 | 0.213 / 0.257 |
| open-loop plans | 106 | 12 | 1.070 | 0.131 | 0.047 / 0.002 / 0.061 | 0.054 / 0.031 / 0.103 | 0.229 / 0.372 |
| open-loop plans | 106 | 24 | 1.730 | 0.122 | 0.107 / 0.005 / 0.140 | 0.114 / 0.036 / 0.203 | 0.211 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1484 | 0.716 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2571 | 0.811 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2360.5350 | 0.559 |
| funds_mae_12m | 5714.0800 | 36.8760 | 964.1780 | 0.837 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 237.9385 | 0.756 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 592.5635 | 0.724 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 392.8080 | 0.796 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0528 | 0.653 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0675 | 0.827 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.2951 | 0.690 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.2945 | 0.685 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5317.7650 | 0.364 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1534.2738 | 0.799 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 388.3655 | 0.564 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 635.5730 | 0.747 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 670.3217 | 0.434 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1092 | 0.431 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1393 | 0.800 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2525 | 0.620 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2513 | 0.616 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1534.3 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 388.4 | 142.8 | 706.1 |
| com_valve | 635.6 | 508.6 | 1010.2 |
| ind_valve | 670.3 | 416.9 | 864.8 |
| pop | 5317.8 | 1754.6 | 7353.4 |
| res_pop | 104.2 | 39.0 | 139.9 |
| com_pop | 9.1 | 4.4 | 12.8 |
| ind_pop | 18.5 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 109.5 | 25.2 | 89.6 |
| tax_fund | 187.8 | 51.5 | 1444.5 |
| road_spend | 104.9 | 8.2 | 647.3 |
| fire_spend | 65.6 | 0.8 | 474.7 |
| police_spend | 107.6 | 6.0 | 604.1 |
| powered_zones | 10.7 | 0.7 | 8.6 |
| unpowered_zones | 5.9 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.3 |
| road_total | 72.8 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1447.6 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 354.7 | 130.7 | 533.4 |
| com_valve | 658.1 | 541.8 | 962.1 |
| ind_valve | 721.3 | 446.9 | 814.5 |
| pop | 5282.9 | 1810.1 | 6881.1 |
| res_pop | 101.5 | 39.6 | 131.0 |
| com_pop | 9.2 | 4.5 | 12.1 |
| ind_pop | 18.6 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 113.8 | 26.2 | 83.7 |
| tax_fund | 182.6 | 47.1 | 1400.1 |
| road_spend | 99.0 | 8.1 | 645.8 |
| fire_spend | 60.4 | 0.8 | 464.7 |
| police_spend | 106.0 | 6.4 | 591.3 |
| powered_zones | 11.2 | 0.9 | 10.7 |
| unpowered_zones | 6.2 | 0.8 | 7.0 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.4 |
| road_total | 73.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1856.3 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 513.5 | 187.8 | 1348.3 |
| com_valve | 551.8 | 385.4 | 1188.9 |
| ind_valve | 480.8 | 305.2 | 1051.7 |
| pop | 5447.3 | 1548.5 | 9108.7 |
| res_pop | 114.1 | 37.0 | 172.8 |
| com_pop | 8.7 | 4.2 | 15.7 |
| ind_pop | 18.1 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 93.6 | 21.3 | 111.7 |
| tax_fund | 206.9 | 68.0 | 1609.5 |
| road_spend | 127.2 | 8.8 | 653.2 |
| fire_spend | 84.8 | 1.1 | 512.0 |
| police_spend | 113.7 | 4.6 | 651.4 |
| powered_zones | 8.9 | 0.0 | 0.5 |
| unpowered_zones | 4.7 | 0.0 | 6.7 |
| coal_plants | 0.4 | 0.0 | 0.1 |
| nuclear_plants | 0.8 | 0.0 | 0.2 |
| road_total | 68.9 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.342 | 0.838 |
| traffic | 1.131 | 0.772 |
| pollution | 1.673 | 0.706 |
| land_value | 0.781 | 0.325 |
| crime | 1.361 | 0.566 |
| rate_of_growth | 1.314 | 0.819 |
| fire_coverage | 2.143 | 0.123 |
| police_coverage | 1.307 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.469 | 0.278 | 0.349 | 0.327 to 0.369 | 0.373 | 0.147 | 0.211 | 0.177 to 0.250 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.449 | 0.002 | 0.006 |
| all plans | 12 | 0.404 | 0.065 | 0.038 |
| all plans | 24 | 0.601 | 0.163 | 0.095 |
| state-reading plans | 1 | 0.475 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.401 | 0.070 | 0.038 |
| state-reading plans | 24 | 0.604 | 0.180 | 0.094 |
| open-loop plans | 1 | 0.430 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.745 | 0.053 | 0.038 |
| open-loop plans | 24 | 1.417 | 0.120 | 0.103 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -253.54 |
| tile_cat | -37.35 |
| flags | -23.04 |
| power | -5.21 |
| half | -2621.52 |
| eighth | -39.59 |
| scalars_s2 | -5.29 |
| build_cost | -0.90 |
| scalars | -26.66 |
| ledger | -28.35 |
| bk | -49.72 |
| sc_res_pop | -1.48 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.22 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.37 |
| sc_res_valve | -1.35 |
| sc_com_valve | -2.53 |
| sc_ind_valve | -2.00 |
| sc_score | -5.42 |
| sc_funds | -3.14 |
| sc_tax_fund | -2.29 |
| sc_road_spend | -2.90 |
| sc_fire_spend | -0.97 |
| sc_police_spend | -0.77 |
| lg_sprite_cycle | -1.21 |
| lg_total_pop | -3.16 |
| lg_res_hist0 | -2.13 |
| lg_res_hist1 | -0.90 |
| lg_com_hist0 | -0.19 |
| lg_com_hist1 | -0.15 |
| lg_ind_hist0 | -0.35 |
| lg_ind_hist1 | -0.48 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.02 |
| lg_need_hospital | -0.12 |
| lg_need_church | -0.11 |
| lg_road_fund | -2.96 |
| lg_police_fund | -0.75 |
| lg_fire_fund | -0.52 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.12 |
| lg_city_center_x | -0.59 |
| lg_city_center_y | -0.15 |
| lg_pollution_max_x | -5.69 |
| lg_pollution_max_y | -5.16 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -3.54 |
| terrain | -6.65 |
| com_rate | -7.14 |
| kl | 13.19 |
| elbo | -3063.16 |
