## sf_15m_full_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.235 | 0.287 | 0.258 | 0.239 to 0.277 | 0.136 | 0.178 | 0.154 | 0.133 to 0.179 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.242 | 0.295 | 0.266 | 0.247 to 0.286 | 0.146 | 0.191 | 0.165 | 0.142 to 0.193 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.209 | 0.255 | 0.230 | 0.209 to 0.253 | 0.102 | 0.133 | 0.115 | 0.100 to 0.132 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.684 | 0.204 | 0.004 / 0.000 / 0.017 | 0.010 / 0.006 / 0.007 | 0.350 / 0.402 |
| all plans | 500 | 12 | 0.519 | 0.146 | 0.060 / 0.003 / 0.378 | 0.049 / 0.026 / 0.103 | 0.319 / 0.428 |
| all plans | 500 | 24 | 0.620 | 0.167 | 0.101 / 0.005 / 0.678 | 0.076 / 0.042 / 0.160 | 0.286 / 0.408 |
| state-reading plans | 394 | 1 | 0.691 | 0.208 | 0.005 / 0.000 / 0.018 | 0.010 / 0.006 / 0.007 | 0.382 / 0.436 |
| state-reading plans | 394 | 12 | 0.510 | 0.151 | 0.061 / 0.003 / 0.465 | 0.050 / 0.025 / 0.103 | 0.337 / 0.442 |
| state-reading plans | 394 | 24 | 0.617 | 0.184 | 0.108 / 0.005 / 0.791 | 0.076 / 0.044 / 0.150 | 0.300 / 0.412 |
| open-loop plans | 106 | 1 | 0.706 | 0.199 | 0.000 / 0.000 / 0.000 | 0.010 / 0.008 / 0.007 | 0.208 / 0.257 |
| open-loop plans | 106 | 12 | 1.109 | 0.131 | 0.055 / 0.002 / 0.061 | 0.048 / 0.031 / 0.103 | 0.251 / 0.372 |
| open-loop plans | 106 | 24 | 1.461 | 0.122 | 0.075 / 0.005 / 0.140 | 0.077 / 0.036 / 0.203 | 0.238 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1541 | 0.743 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2584 | 0.815 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2093.0600 | 0.647 |
| funds_mae_12m | 5714.0800 | 36.8760 | 864.3323 | 0.854 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 235.6160 | 0.760 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 572.0130 | 0.748 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 374.4910 | 0.824 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0490 | 0.702 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0598 | 0.848 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3191 | 0.746 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3194 | 0.743 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3514.7000 | 0.686 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1189.3998 | 0.846 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 334.9030 | 0.659 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 617.2560 | 0.783 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 562.8388 | 0.674 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0765 | 0.709 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1008 | 0.857 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2865 | 0.703 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2852 | 0.699 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1189.4 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 334.9 | 142.8 | 706.1 |
| com_valve | 617.3 | 508.6 | 1010.2 |
| ind_valve | 562.8 | 416.9 | 864.8 |
| pop | 3514.7 | 1754.6 | 7353.4 |
| res_pop | 86.1 | 39.0 | 139.9 |
| com_pop | 9.0 | 4.4 | 12.8 |
| ind_pop | 10.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 75.4 | 25.2 | 89.6 |
| tax_fund | 163.8 | 51.5 | 1444.5 |
| road_spend | 86.8 | 8.2 | 647.3 |
| fire_spend | 43.8 | 0.8 | 474.7 |
| police_spend | 67.9 | 6.0 | 604.1 |
| powered_zones | 8.6 | 0.7 | 8.6 |
| unpowered_zones | 5.8 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.3 |
| road_total | 57.3 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1075.4 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 308.5 | 130.7 | 533.4 |
| com_valve | 642.1 | 541.8 | 962.1 |
| ind_valve | 604.6 | 446.9 | 814.5 |
| pop | 3575.9 | 1810.1 | 6881.1 |
| res_pop | 84.9 | 39.6 | 131.0 |
| com_pop | 9.1 | 4.5 | 12.1 |
| ind_pop | 10.7 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 76.7 | 26.2 | 83.7 |
| tax_fund | 158.8 | 47.1 | 1400.1 |
| road_spend | 81.6 | 8.1 | 645.8 |
| fire_spend | 38.4 | 0.8 | 464.7 |
| police_spend | 64.0 | 6.4 | 591.3 |
| powered_zones | 8.9 | 0.9 | 10.7 |
| unpowered_zones | 6.0 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 57.2 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1613.0 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 433.2 | 187.8 | 1348.3 |
| com_valve | 524.9 | 385.4 | 1188.9 |
| ind_valve | 407.7 | 305.2 | 1051.7 |
| pop | 3287.3 | 1548.5 | 9108.7 |
| res_pop | 90.3 | 37.0 | 172.8 |
| com_pop | 8.6 | 4.2 | 15.7 |
| ind_pop | 10.6 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 70.5 | 21.3 | 111.7 |
| tax_fund | 182.6 | 68.0 | 1609.5 |
| road_spend | 106.1 | 8.8 | 653.2 |
| fire_spend | 63.5 | 1.1 | 512.0 |
| police_spend | 82.3 | 4.6 | 651.4 |
| powered_zones | 7.3 | 0.0 | 0.5 |
| unpowered_zones | 5.1 | 0.0 | 6.7 |
| coal_plants | 0.4 | 0.0 | 0.1 |
| nuclear_plants | 0.7 | 0.0 | 0.2 |
| road_total | 57.8 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.233 | 0.838 |
| traffic | 1.117 | 0.772 |
| pollution | 1.636 | 0.706 |
| land_value | 0.675 | 0.325 |
| crime | 1.199 | 0.566 |
| rate_of_growth | 1.213 | 0.819 |
| fire_coverage | 1.697 | 0.123 |
| police_coverage | 0.924 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.598 | 0.261 | 0.363 | 0.340 to 0.384 | 0.665 | 0.137 | 0.227 | 0.185 to 0.271 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.471 | 0.002 | 0.006 |
| all plans | 12 | 0.353 | 0.054 | 0.037 |
| all plans | 24 | 0.433 | 0.114 | 0.056 |
| state-reading plans | 1 | 0.477 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.351 | 0.054 | 0.037 |
| state-reading plans | 24 | 0.437 | 0.122 | 0.055 |
| open-loop plans | 1 | 0.473 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.633 | 0.053 | 0.033 |
| open-loop plans | 24 | 1.001 | 0.094 | 0.056 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -224.18 |
| tile_cat | -32.82 |
| flags | -16.42 |
| power | -2.88 |
| half | -2478.07 |
| eighth | -38.53 |
| scalars_s2 | -5.67 |
| build_cost | -1.18 |
| scalars | -12.90 |
| ledger | -13.10 |
| bk | -20.32 |
| sc_res_pop | -1.71 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.22 |
| sc_powered_zones | -0.08 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.39 |
| sc_res_valve | -0.98 |
| sc_com_valve | -2.02 |
| sc_ind_valve | -1.61 |
| sc_score | -0.39 |
| sc_funds | -1.03 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.44 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.16 |
| lg_sprite_cycle | -0.78 |
| lg_total_pop | -1.56 |
| lg_res_hist0 | -0.60 |
| lg_res_hist1 | -0.40 |
| lg_com_hist0 | -0.17 |
| lg_com_hist1 | -0.10 |
| lg_ind_hist0 | -0.25 |
| lg_ind_hist1 | -0.20 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.50 |
| lg_police_fund | -0.18 |
| lg_fire_fund | -0.14 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.03 |
| lg_pollution_max_x | -2.86 |
| lg_pollution_max_y | -2.84 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -5.65 |
| com_rate | -4.87 |
| kl | 12.39 |
| elbo | -2842.99 |

## sf_15m_full_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.248 | 0.287 | 0.266 | 0.245 to 0.286 | 0.145 | 0.174 | 0.158 | 0.135 to 0.186 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.257 | 0.294 | 0.274 | 0.252 to 0.295 | 0.157 | 0.186 | 0.171 | 0.143 to 0.202 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.218 | 0.258 | 0.236 | 0.215 to 0.259 | 0.105 | 0.131 | 0.117 | 0.101 to 0.136 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.563 | 0.204 | 0.003 / 0.000 / 0.017 | 0.010 / 0.006 / 0.007 | 0.357 / 0.402 |
| all plans | 500 | 12 | 0.488 | 0.146 | 0.062 / 0.003 / 0.378 | 0.050 / 0.026 / 0.103 | 0.309 / 0.428 |
| all plans | 500 | 24 | 0.631 | 0.167 | 0.120 / 0.005 / 0.678 | 0.076 / 0.042 / 0.160 | 0.271 / 0.408 |
| state-reading plans | 394 | 1 | 0.579 | 0.208 | 0.003 / 0.000 / 0.018 | 0.010 / 0.006 / 0.007 | 0.390 / 0.436 |
| state-reading plans | 394 | 12 | 0.479 | 0.151 | 0.064 / 0.003 / 0.465 | 0.050 / 0.025 / 0.103 | 0.328 / 0.442 |
| state-reading plans | 394 | 24 | 0.629 | 0.184 | 0.126 / 0.005 / 0.791 | 0.075 / 0.044 / 0.150 | 0.286 / 0.412 |
| open-loop plans | 106 | 1 | 0.539 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.212 / 0.257 |
| open-loop plans | 106 | 12 | 1.044 | 0.131 | 0.053 / 0.002 / 0.061 | 0.048 / 0.031 / 0.103 | 0.238 / 0.372 |
| open-loop plans | 106 | 24 | 1.522 | 0.122 | 0.101 / 0.005 / 0.140 | 0.080 / 0.036 / 0.203 | 0.219 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1581 | 0.762 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2661 | 0.839 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2112.9850 | 0.641 |
| funds_mae_12m | 5714.0800 | 36.8760 | 886.7055 | 0.850 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 230.6308 | 0.770 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 599.5593 | 0.716 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 387.2312 | 0.805 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0496 | 0.694 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0616 | 0.843 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3090 | 0.722 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3096 | 0.720 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3608.0550 | 0.669 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1299.7960 | 0.831 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 365.6603 | 0.604 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 659.9868 | 0.698 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 607.7610 | 0.574 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0762 | 0.712 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1199 | 0.829 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2713 | 0.666 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2703 | 0.663 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1299.8 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 365.7 | 142.8 | 706.1 |
| com_valve | 660.0 | 508.6 | 1010.2 |
| ind_valve | 607.8 | 416.9 | 864.8 |
| pop | 3608.1 | 1754.6 | 7353.4 |
| res_pop | 87.5 | 39.0 | 139.9 |
| com_pop | 9.3 | 4.4 | 12.8 |
| ind_pop | 10.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 90.9 | 25.2 | 89.6 |
| tax_fund | 159.8 | 51.5 | 1444.5 |
| road_spend | 89.0 | 8.2 | 647.3 |
| fire_spend | 48.2 | 0.8 | 474.7 |
| police_spend | 70.4 | 6.0 | 604.1 |
| powered_zones | 8.7 | 0.7 | 8.6 |
| unpowered_zones | 5.8 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.3 |
| road_total | 58.8 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1220.3 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 346.5 | 130.7 | 533.4 |
| com_valve | 689.8 | 541.8 | 962.1 |
| ind_valve | 655.7 | 446.9 | 814.5 |
| pop | 3610.1 | 1810.1 | 6881.1 |
| res_pop | 86.6 | 39.6 | 131.0 |
| com_pop | 9.4 | 4.5 | 12.1 |
| ind_pop | 10.8 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 92.2 | 26.2 | 83.7 |
| tax_fund | 153.3 | 47.1 | 1400.1 |
| road_spend | 82.5 | 8.1 | 645.8 |
| fire_spend | 43.6 | 0.8 | 464.7 |
| police_spend | 66.1 | 6.4 | 591.3 |
| powered_zones | 8.9 | 0.9 | 10.7 |
| unpowered_zones | 6.0 | 0.8 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 58.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1595.3 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 437.0 | 187.8 | 1348.3 |
| com_valve | 549.1 | 385.4 | 1188.9 |
| ind_valve | 429.5 | 305.2 | 1051.7 |
| pop | 3600.4 | 1548.5 | 9108.7 |
| res_pop | 90.8 | 37.0 | 172.8 |
| com_pop | 9.1 | 4.2 | 15.7 |
| ind_pop | 11.4 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 86.0 | 21.3 | 111.7 |
| tax_fund | 183.9 | 68.0 | 1609.5 |
| road_spend | 113.2 | 8.8 | 653.2 |
| fire_spend | 65.3 | 1.1 | 512.0 |
| police_spend | 86.1 | 4.6 | 651.4 |
| powered_zones | 8.1 | 0.0 | 0.5 |
| unpowered_zones | 4.8 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.7 | 0.0 | 0.2 |
| road_total | 58.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.273 | 0.838 |
| traffic | 1.121 | 0.772 |
| pollution | 1.639 | 0.706 |
| land_value | 0.723 | 0.325 |
| crime | 1.242 | 0.566 |
| rate_of_growth | 1.254 | 0.819 |
| fire_coverage | 2.342 | 0.123 |
| police_coverage | 1.150 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.580 | 0.260 | 0.359 | 0.336 to 0.379 | 0.602 | 0.135 | 0.220 | 0.179 to 0.262 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.422 | 0.001 | 0.006 |
| all plans | 12 | 0.349 | 0.062 | 0.039 |
| all plans | 24 | 0.467 | 0.143 | 0.055 |
| state-reading plans | 1 | 0.448 | 0.001 | 0.007 |
| state-reading plans | 12 | 0.345 | 0.063 | 0.041 |
| state-reading plans | 24 | 0.470 | 0.147 | 0.054 |
| open-loop plans | 1 | 0.385 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.688 | 0.059 | 0.038 |
| open-loop plans | 24 | 1.157 | 0.125 | 0.066 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -223.00 |
| tile_cat | -32.48 |
| flags | -16.34 |
| power | -2.87 |
| half | -2460.49 |
| eighth | -38.16 |
| scalars_s2 | -5.20 |
| build_cost | -0.87 |
| scalars | -12.02 |
| ledger | -12.78 |
| bk | -19.60 |
| sc_res_pop | -1.46 |
| sc_com_pop | -0.12 |
| sc_ind_pop | -0.20 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.36 |
| sc_res_valve | -0.96 |
| sc_com_valve | -1.95 |
| sc_ind_valve | -1.14 |
| sc_score | -0.47 |
| sc_funds | -0.91 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.51 |
| sc_fire_spend | -0.21 |
| sc_police_spend | -0.21 |
| lg_sprite_cycle | -0.78 |
| lg_total_pop | -1.55 |
| lg_res_hist0 | -0.27 |
| lg_res_hist1 | -0.31 |
| lg_com_hist0 | -0.04 |
| lg_com_hist1 | -0.06 |
| lg_ind_hist0 | -0.06 |
| lg_ind_hist1 | -0.11 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.02 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.03 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.65 |
| lg_police_fund | -0.32 |
| lg_fire_fund | -0.25 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.92 |
| lg_pollution_max_y | -2.94 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.35 |
| terrain | -5.55 |
| com_rate | -4.54 |
| kl | 12.57 |
| elbo | -2821.68 |
