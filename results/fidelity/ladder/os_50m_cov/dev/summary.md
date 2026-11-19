## os_50m_cov_samples_001200000_dec-a

samples consumed: 1200000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "8477bf32c75b0a4a", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.276 | 0.277 | 0.276 | 0.255 to 0.296 | 0.170 | 0.161 | 0.166 | 0.139 to 0.197 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.284 | 0.285 | 0.284 | 0.262 to 0.304 | 0.185 | 0.175 | 0.180 | 0.149 to 0.216 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.245 | 0.244 | 0.244 | 0.222 to 0.267 | 0.118 | 0.113 | 0.115 | 0.098 to 0.135 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.789 | 0.204 | 0.018 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.370 / 0.402 |
| all plans | 500 | 12 | 0.534 | 0.146 | 0.175 / 0.003 / 0.378 | 0.036 / 0.026 / 0.103 | 0.370 / 0.428 |
| all plans | 500 | 24 | 0.558 | 0.167 | 0.211 / 0.005 / 0.678 | 0.063 / 0.042 / 0.160 | 0.339 / 0.408 |
| state-reading plans | 394 | 1 | 0.794 | 0.208 | 0.023 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.406 / 0.436 |
| state-reading plans | 394 | 12 | 0.539 | 0.151 | 0.215 / 0.003 / 0.465 | 0.036 / 0.025 / 0.103 | 0.391 / 0.442 |
| state-reading plans | 394 | 24 | 0.575 | 0.184 | 0.277 / 0.005 / 0.791 | 0.063 / 0.044 / 0.150 | 0.352 / 0.412 |
| open-loop plans | 106 | 1 | 0.911 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.214 / 0.257 |
| open-loop plans | 106 | 12 | 0.790 | 0.131 | 0.017 / 0.002 / 0.061 | 0.035 / 0.031 / 0.103 | 0.286 / 0.372 |
| open-loop plans | 106 | 24 | 0.795 | 0.122 | 0.022 / 0.005 / 0.140 | 0.063 / 0.036 / 0.203 | 0.290 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1655 | 0.798 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2761 | 0.871 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1570.0950 | 0.821 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1951.1225 | 0.663 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 203.7508 | 0.821 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 496.0340 | 0.837 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 320.5415 | 0.906 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0362 | 0.868 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1751 | 0.541 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3697 | 0.865 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3629 | 0.845 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2767.1900 | 0.819 |
| funds_mae_24m | 7364.5720 | 66.5620 | 2242.6658 | 0.702 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 257.3030 | 0.797 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 591.5527 | 0.835 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 555.9615 | 0.689 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0627 | 0.827 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.2113 | 0.693 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3386 | 0.831 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3340 | 0.819 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 2242.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 257.3 | 142.8 | 706.1 |
| com_valve | 591.6 | 508.6 | 1010.2 |
| ind_valve | 556.0 | 416.9 | 864.8 |
| pop | 2767.2 | 1754.6 | 7353.4 |
| res_pop | 61.3 | 39.0 | 139.9 |
| com_pop | 6.1 | 4.4 | 12.8 |
| ind_pop | 9.0 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 41.7 | 25.2 | 89.6 |
| tax_fund | 135.8 | 51.5 | 1444.5 |
| road_spend | 88.5 | 8.2 | 647.3 |
| fire_spend | 56.1 | 0.8 | 474.7 |
| police_spend | 98.0 | 6.0 | 604.1 |
| powered_zones | 7.7 | 0.7 | 8.6 |
| unpowered_zones | 5.3 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 61.7 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 2451.3 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 226.9 | 130.7 | 533.4 |
| com_valve | 621.0 | 541.8 | 962.1 |
| ind_valve | 602.6 | 446.9 | 814.5 |
| pop | 2787.0 | 1810.1 | 6881.1 |
| res_pop | 61.2 | 39.6 | 131.0 |
| com_pop | 6.0 | 4.5 | 12.1 |
| ind_pop | 9.0 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 44.2 | 26.2 | 83.7 |
| tax_fund | 128.5 | 47.1 | 1400.1 |
| road_spend | 82.6 | 8.1 | 645.8 |
| fire_spend | 53.3 | 0.8 | 464.7 |
| police_spend | 103.9 | 6.4 | 591.3 |
| powered_zones | 9.0 | 0.9 | 10.7 |
| unpowered_zones | 5.6 | 0.8 | 7.0 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 61.6 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1467.1 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 370.5 | 187.8 | 1348.3 |
| com_valve | 482.0 | 385.4 | 1188.9 |
| ind_valve | 382.5 | 305.2 | 1051.7 |
| pop | 2693.4 | 1548.5 | 9108.7 |
| res_pop | 61.6 | 37.0 | 172.8 |
| com_pop | 6.3 | 4.2 | 15.7 |
| ind_pop | 8.9 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 32.6 | 21.3 | 111.7 |
| tax_fund | 162.8 | 68.0 | 1609.5 |
| road_spend | 110.1 | 8.8 | 653.2 |
| fire_spend | 66.6 | 1.1 | 512.0 |
| police_spend | 76.2 | 4.6 | 651.4 |
| powered_zones | 3.0 | 0.0 | 0.5 |
| unpowered_zones | 4.2 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 62.1 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.009 | 0.838 |
| traffic | 1.096 | 0.772 |
| pollution | 1.564 | 0.706 |
| land_value | 0.686 | 0.325 |
| crime | 1.059 | 0.566 |
| rate_of_growth | 0.975 | 0.819 |
| fire_coverage | 1.879 | 0.123 |
| police_coverage | 1.112 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.623 | 0.245 | 0.351 | 0.327 to 0.373 | 0.840 | 0.119 | 0.208 | 0.167 to 0.254 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.508 | 0.016 | 0.006 |
| all plans | 12 | 0.347 | 0.139 | 0.027 |
| all plans | 24 | 0.382 | 0.245 | 0.053 |
| state-reading plans | 1 | 0.516 | 0.019 | 0.006 |
| state-reading plans | 12 | 0.352 | 0.183 | 0.028 |
| state-reading plans | 24 | 0.399 | 0.294 | 0.051 |
| open-loop plans | 1 | 0.583 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.473 | 0.018 | 0.024 |
| open-loop plans | 24 | 0.486 | 0.030 | 0.059 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -247.45 |
| tile_cat | -36.03 |
| flags | -16.90 |
| power | -4.46 |
| half | -2680.03 |
| eighth | -42.07 |
| scalars_s2 | -7.91 |
| build_cost | -1.77 |
| scalars | -15.63 |
| ledger | -13.92 |
| bk | -21.64 |
| sc_res_pop | -2.59 |
| sc_com_pop | -0.58 |
| sc_ind_pop | -0.64 |
| sc_powered_zones | -0.20 |
| sc_unpowered_zones | -0.29 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.53 |
| sc_res_valve | -1.04 |
| sc_com_valve | -2.10 |
| sc_ind_valve | -1.84 |
| sc_score | -0.37 |
| sc_funds | -1.19 |
| sc_tax_fund | -0.43 |
| sc_road_spend | -0.45 |
| sc_fire_spend | -0.15 |
| sc_police_spend | -0.14 |
| lg_sprite_cycle | -1.20 |
| lg_total_pop | -1.58 |
| lg_res_hist0 | -0.71 |
| lg_res_hist1 | -0.56 |
| lg_com_hist0 | -0.18 |
| lg_com_hist1 | -0.24 |
| lg_ind_hist0 | -0.28 |
| lg_ind_hist1 | -0.39 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.04 |
| lg_road_fund | -0.47 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.12 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.08 |
| lg_city_center_y | -0.06 |
| lg_pollution_max_x | -2.74 |
| lg_pollution_max_y | -2.68 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -6.68 |
| com_rate | -5.10 |
| kl | 5.48 |
| elbo | -3075.52 |

## os_50m_cov_samples_002400000_dec-a

samples consumed: 2400000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "8477bf32c75b0a4a", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.289 | 0.282 | 0.285 | 0.263 to 0.305 | 0.186 | 0.168 | 0.177 | 0.149 to 0.208 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.297 | 0.290 | 0.293 | 0.271 to 0.314 | 0.201 | 0.183 | 0.192 | 0.160 to 0.227 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.260 | 0.249 | 0.254 | 0.233 to 0.275 | 0.133 | 0.119 | 0.126 | 0.107 to 0.147 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.789 | 0.204 | 0.018 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.386 / 0.402 |
| all plans | 500 | 12 | 0.489 | 0.146 | 0.155 / 0.003 / 0.378 | 0.041 / 0.026 / 0.103 | 0.375 / 0.428 |
| all plans | 500 | 24 | 0.518 | 0.167 | 0.205 / 0.005 / 0.678 | 0.066 / 0.042 / 0.160 | 0.342 / 0.408 |
| state-reading plans | 394 | 1 | 0.763 | 0.208 | 0.021 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.422 / 0.436 |
| state-reading plans | 394 | 12 | 0.492 | 0.151 | 0.197 / 0.003 / 0.465 | 0.041 / 0.025 / 0.103 | 0.396 / 0.442 |
| state-reading plans | 394 | 24 | 0.536 | 0.184 | 0.263 / 0.005 / 0.791 | 0.066 / 0.044 / 0.150 | 0.355 / 0.412 |
| open-loop plans | 106 | 1 | 0.933 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.230 / 0.257 |
| open-loop plans | 106 | 12 | 0.669 | 0.131 | 0.031 / 0.002 / 0.061 | 0.040 / 0.031 / 0.103 | 0.293 / 0.372 |
| open-loop plans | 106 | 24 | 0.699 | 0.122 | 0.036 / 0.005 / 0.140 | 0.067 / 0.036 / 0.203 | 0.294 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1767 | 0.852 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2853 | 0.900 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1738.1200 | 0.765 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1772.0732 | 0.694 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 202.6428 | 0.823 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 502.7245 | 0.829 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 322.8810 | 0.902 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0410 | 0.805 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1554 | 0.594 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3749 | 0.877 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3687 | 0.858 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2933.5300 | 0.789 |
| funds_mae_24m | 7364.5720 | 66.5620 | 2132.7360 | 0.717 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 233.3798 | 0.839 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 590.0295 | 0.838 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 576.2455 | 0.644 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0664 | 0.795 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.2046 | 0.703 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3423 | 0.840 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3381 | 0.829 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 2132.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 233.4 | 142.8 | 706.1 |
| com_valve | 590.0 | 508.6 | 1010.2 |
| ind_valve | 576.2 | 416.9 | 864.8 |
| pop | 2933.5 | 1754.6 | 7353.4 |
| res_pop | 64.4 | 39.0 | 139.9 |
| com_pop | 6.5 | 4.4 | 12.8 |
| ind_pop | 9.3 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.0 | 25.2 | 89.6 |
| tax_fund | 131.5 | 51.5 | 1444.5 |
| road_spend | 83.8 | 8.2 | 647.3 |
| fire_spend | 49.4 | 0.8 | 474.7 |
| police_spend | 89.8 | 6.0 | 604.1 |
| powered_zones | 6.6 | 0.7 | 8.6 |
| unpowered_zones | 4.8 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 58.4 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 2331.4 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 222.9 | 130.7 | 533.4 |
| com_valve | 619.3 | 541.8 | 962.1 |
| ind_valve | 629.0 | 446.9 | 814.5 |
| pop | 2933.5 | 1810.1 | 6881.1 |
| res_pop | 63.9 | 39.6 | 131.0 |
| com_pop | 6.5 | 4.5 | 12.1 |
| ind_pop | 9.3 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 44.9 | 26.2 | 83.7 |
| tax_fund | 125.6 | 47.1 | 1400.1 |
| road_spend | 77.6 | 8.1 | 645.8 |
| fire_spend | 42.9 | 0.8 | 464.7 |
| police_spend | 91.3 | 6.4 | 591.3 |
| powered_zones | 7.8 | 0.9 | 10.7 |
| unpowered_zones | 5.2 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 59.2 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1394.4 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 272.5 | 187.8 | 1348.3 |
| com_valve | 481.3 | 385.4 | 1188.9 |
| ind_valve | 380.0 | 305.2 | 1051.7 |
| pop | 2933.8 | 1548.5 | 9108.7 |
| res_pop | 66.1 | 37.0 | 172.8 |
| com_pop | 6.6 | 4.2 | 15.7 |
| ind_pop | 9.5 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 35.9 | 21.3 | 111.7 |
| tax_fund | 153.3 | 68.0 | 1609.5 |
| road_spend | 107.2 | 8.8 | 653.2 |
| fire_spend | 73.7 | 1.1 | 512.0 |
| police_spend | 84.2 | 4.6 | 651.4 |
| powered_zones | 2.3 | 0.0 | 0.5 |
| unpowered_zones | 3.3 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 55.7 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 0.983 | 0.838 |
| traffic | 1.050 | 0.772 |
| pollution | 1.533 | 0.706 |
| land_value | 0.631 | 0.325 |
| crime | 0.986 | 0.566 |
| rate_of_growth | 0.973 | 0.819 |
| fire_coverage | 1.849 | 0.123 |
| police_coverage | 0.946 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.630 | 0.254 | 0.362 | 0.338 to 0.383 | 0.822 | 0.129 | 0.223 | 0.180 to 0.269 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.525 | 0.012 | 0.007 |
| all plans | 12 | 0.321 | 0.150 | 0.031 |
| all plans | 24 | 0.359 | 0.243 | 0.054 |
| state-reading plans | 1 | 0.485 | 0.014 | 0.007 |
| state-reading plans | 12 | 0.325 | 0.172 | 0.031 |
| state-reading plans | 24 | 0.379 | 0.284 | 0.057 |
| open-loop plans | 1 | 0.585 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.392 | 0.026 | 0.034 |
| open-loop plans | 24 | 0.403 | 0.042 | 0.051 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -228.77 |
| tile_cat | -32.45 |
| flags | -15.44 |
| power | -3.47 |
| half | -2486.48 |
| eighth | -38.59 |
| scalars_s2 | -7.28 |
| build_cost | -1.69 |
| scalars | -14.78 |
| ledger | -13.45 |
| bk | -20.95 |
| sc_res_pop | -2.37 |
| sc_com_pop | -0.44 |
| sc_ind_pop | -0.51 |
| sc_powered_zones | -0.17 |
| sc_unpowered_zones | -0.26 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.48 |
| sc_res_valve | -1.02 |
| sc_com_valve | -2.07 |
| sc_ind_valve | -1.74 |
| sc_score | -0.37 |
| sc_funds | -1.13 |
| sc_tax_fund | -0.43 |
| sc_road_spend | -0.45 |
| sc_fire_spend | -0.15 |
| sc_police_spend | -0.14 |
| lg_sprite_cycle | -0.88 |
| lg_total_pop | -1.57 |
| lg_res_hist0 | -0.61 |
| lg_res_hist1 | -0.46 |
| lg_com_hist0 | -0.19 |
| lg_com_hist1 | -0.19 |
| lg_ind_hist0 | -0.28 |
| lg_ind_hist1 | -0.35 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.49 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.12 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.04 |
| lg_city_center_y | -0.03 |
| lg_pollution_max_x | -2.84 |
| lg_pollution_max_y | -2.77 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -5.15 |
| com_rate | -3.53 |
| kl | 10.08 |
| elbo | -2853.88 |

## os_50m_cov_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "8477bf32c75b0a4a", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.296 | 0.283 | 0.289 | 0.269 to 0.308 | 0.191 | 0.168 | 0.179 | 0.152 to 0.209 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.305 | 0.292 | 0.298 | 0.276 to 0.318 | 0.207 | 0.182 | 0.193 | 0.162 to 0.228 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.263 | 0.248 | 0.255 | 0.233 to 0.276 | 0.136 | 0.121 | 0.128 | 0.111 to 0.148 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.736 | 0.204 | 0.017 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.385 / 0.402 |
| all plans | 500 | 12 | 0.466 | 0.146 | 0.133 / 0.003 / 0.378 | 0.044 / 0.026 / 0.103 | 0.377 / 0.428 |
| all plans | 500 | 24 | 0.496 | 0.167 | 0.171 / 0.005 / 0.678 | 0.068 / 0.042 / 0.160 | 0.345 / 0.408 |
| state-reading plans | 394 | 1 | 0.691 | 0.208 | 0.019 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.421 / 0.436 |
| state-reading plans | 394 | 12 | 0.468 | 0.151 | 0.160 / 0.003 / 0.465 | 0.043 / 0.025 / 0.103 | 0.398 / 0.442 |
| state-reading plans | 394 | 24 | 0.515 | 0.184 | 0.216 / 0.005 / 0.791 | 0.067 / 0.044 / 0.150 | 0.358 / 0.412 |
| open-loop plans | 106 | 1 | 0.841 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.225 / 0.257 |
| open-loop plans | 106 | 12 | 0.679 | 0.131 | 0.031 / 0.002 / 0.061 | 0.050 / 0.031 / 0.103 | 0.296 / 0.372 |
| open-loop plans | 106 | 24 | 0.708 | 0.122 | 0.038 / 0.005 / 0.140 | 0.076 / 0.036 / 0.203 | 0.297 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1786 | 0.861 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2892 | 0.912 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1903.5650 | 0.710 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1564.9705 | 0.731 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 196.1207 | 0.835 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 517.9172 | 0.811 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 333.7165 | 0.886 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0442 | 0.763 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1334 | 0.652 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3770 | 0.881 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3705 | 0.862 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3092.1350 | 0.761 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1939.3263 | 0.743 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 246.5600 | 0.816 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 600.7363 | 0.816 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 580.4103 | 0.635 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0684 | 0.778 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1713 | 0.752 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3450 | 0.846 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3406 | 0.835 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1939.3 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 246.6 | 142.8 | 706.1 |
| com_valve | 600.7 | 508.6 | 1010.2 |
| ind_valve | 580.4 | 416.9 | 864.8 |
| pop | 3092.1 | 1754.6 | 7353.4 |
| res_pop | 67.0 | 39.0 | 139.9 |
| com_pop | 6.7 | 4.4 | 12.8 |
| ind_pop | 9.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 44.2 | 25.2 | 89.6 |
| tax_fund | 136.3 | 51.5 | 1444.5 |
| road_spend | 81.0 | 8.2 | 647.3 |
| fire_spend | 42.9 | 0.8 | 474.7 |
| police_spend | 80.1 | 6.0 | 604.1 |
| powered_zones | 6.3 | 0.7 | 8.6 |
| unpowered_zones | 4.6 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 55.9 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 2094.0 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 231.6 | 130.7 | 533.4 |
| com_valve | 633.7 | 541.8 | 962.1 |
| ind_valve | 631.9 | 446.9 | 814.5 |
| pop | 3080.2 | 1810.1 | 6881.1 |
| res_pop | 66.6 | 39.6 | 131.0 |
| com_pop | 6.7 | 4.5 | 12.1 |
| ind_pop | 9.6 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 46.4 | 26.2 | 83.7 |
| tax_fund | 129.3 | 47.1 | 1400.1 |
| road_spend | 76.2 | 8.1 | 645.8 |
| fire_spend | 39.5 | 0.8 | 464.7 |
| police_spend | 82.2 | 6.4 | 591.3 |
| powered_zones | 7.3 | 0.9 | 10.7 |
| unpowered_zones | 5.0 | 0.8 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 56.7 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1364.6 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 302.2 | 187.8 | 1348.3 |
| com_valve | 478.1 | 385.4 | 1188.9 |
| ind_valve | 389.0 | 305.2 | 1051.7 |
| pop | 3136.3 | 1548.5 | 9108.7 |
| res_pop | 68.5 | 37.0 | 172.8 |
| com_pop | 6.8 | 4.2 | 15.7 |
| ind_pop | 9.9 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 36.1 | 21.3 | 111.7 |
| tax_fund | 162.2 | 68.0 | 1609.5 |
| road_spend | 99.1 | 8.8 | 653.2 |
| fire_spend | 55.8 | 1.1 | 512.0 |
| police_spend | 72.1 | 4.6 | 651.4 |
| powered_zones | 2.6 | 0.0 | 0.5 |
| unpowered_zones | 3.0 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 53.0 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 0.983 | 0.838 |
| traffic | 1.035 | 0.772 |
| pollution | 1.513 | 0.706 |
| land_value | 0.619 | 0.325 |
| crime | 0.979 | 0.566 |
| rate_of_growth | 0.968 | 0.819 |
| fire_coverage | 1.754 | 0.123 |
| police_coverage | 0.921 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.614 | 0.258 | 0.363 | 0.341 to 0.383 | 0.696 | 0.135 | 0.226 | 0.185 to 0.271 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.488 | 0.011 | 0.006 |
| all plans | 12 | 0.317 | 0.128 | 0.034 |
| all plans | 24 | 0.352 | 0.185 | 0.059 |
| state-reading plans | 1 | 0.458 | 0.013 | 0.006 |
| state-reading plans | 12 | 0.322 | 0.140 | 0.033 |
| state-reading plans | 24 | 0.372 | 0.242 | 0.060 |
| open-loop plans | 1 | 0.526 | 0.002 | 0.006 |
| open-loop plans | 12 | 0.415 | 0.030 | 0.039 |
| open-loop plans | 24 | 0.403 | 0.051 | 0.055 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -222.51 |
| tile_cat | -31.62 |
| flags | -15.28 |
| power | -3.30 |
| half | -2428.49 |
| eighth | -37.34 |
| scalars_s2 | -6.85 |
| build_cost | -1.64 |
| scalars | -14.18 |
| ledger | -12.99 |
| bk | -20.32 |
| sc_res_pop | -2.21 |
| sc_com_pop | -0.35 |
| sc_ind_pop | -0.42 |
| sc_powered_zones | -0.16 |
| sc_unpowered_zones | -0.24 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.43 |
| sc_res_valve | -1.00 |
| sc_com_valve | -2.02 |
| sc_ind_valve | -1.62 |
| sc_score | -0.38 |
| sc_funds | -1.10 |
| sc_tax_fund | -0.43 |
| sc_road_spend | -0.46 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.15 |
| lg_sprite_cycle | -0.76 |
| lg_total_pop | -1.56 |
| lg_res_hist0 | -0.53 |
| lg_res_hist1 | -0.40 |
| lg_com_hist0 | -0.11 |
| lg_com_hist1 | -0.14 |
| lg_ind_hist0 | -0.20 |
| lg_ind_hist1 | -0.27 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.52 |
| lg_police_fund | -0.14 |
| lg_fire_fund | -0.13 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.04 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.87 |
| lg_pollution_max_y | -2.81 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.84 |
| com_rate | -2.61 |
| kl | 11.59 |
| elbo | -2786.37 |

## os_50m_cov_samples_003600000_dec-a

samples consumed: 3600000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "8477bf32c75b0a4a", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.297 | 0.284 | 0.290 | 0.270 to 0.309 | 0.192 | 0.170 | 0.180 | 0.154 to 0.210 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.305 | 0.293 | 0.299 | 0.277 to 0.319 | 0.208 | 0.184 | 0.195 | 0.164 to 0.230 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.263 | 0.248 | 0.255 | 0.234 to 0.275 | 0.137 | 0.122 | 0.129 | 0.113 to 0.148 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.699 | 0.204 | 0.014 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.384 / 0.402 |
| all plans | 500 | 12 | 0.442 | 0.146 | 0.116 / 0.003 / 0.378 | 0.045 / 0.026 / 0.103 | 0.375 / 0.428 |
| all plans | 500 | 24 | 0.477 | 0.167 | 0.148 / 0.005 / 0.678 | 0.072 / 0.042 / 0.160 | 0.344 / 0.408 |
| state-reading plans | 394 | 1 | 0.694 | 0.208 | 0.018 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.421 / 0.436 |
| state-reading plans | 394 | 12 | 0.444 | 0.151 | 0.135 / 0.003 / 0.465 | 0.044 / 0.025 / 0.103 | 0.396 / 0.442 |
| state-reading plans | 394 | 24 | 0.494 | 0.184 | 0.187 / 0.005 / 0.791 | 0.070 / 0.044 / 0.150 | 0.356 / 0.412 |
| open-loop plans | 106 | 1 | 0.761 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.225 / 0.257 |
| open-loop plans | 106 | 12 | 0.648 | 0.131 | 0.031 / 0.002 / 0.061 | 0.049 / 0.031 / 0.103 | 0.296 / 0.372 |
| open-loop plans | 106 | 24 | 0.677 | 0.122 | 0.041 / 0.005 / 0.140 | 0.076 / 0.036 / 0.203 | 0.298 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1803 | 0.869 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2899 | 0.914 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1987.9800 | 0.682 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1332.3520 | 0.772 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 203.3882 | 0.821 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 520.1917 | 0.809 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 337.2303 | 0.881 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0453 | 0.750 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1164 | 0.697 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3752 | 0.877 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3686 | 0.858 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3264.4750 | 0.730 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1647.7845 | 0.783 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 247.2330 | 0.815 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 602.5432 | 0.813 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 585.4405 | 0.624 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0717 | 0.750 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1477 | 0.787 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3441 | 0.844 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3397 | 0.833 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1647.8 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 247.2 | 142.8 | 706.1 |
| com_valve | 602.5 | 508.6 | 1010.2 |
| ind_valve | 585.4 | 416.9 | 864.8 |
| pop | 3264.5 | 1754.6 | 7353.4 |
| res_pop | 72.5 | 39.0 | 139.9 |
| com_pop | 7.0 | 4.4 | 12.8 |
| ind_pop | 9.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.1 | 25.2 | 89.6 |
| tax_fund | 141.6 | 51.5 | 1444.5 |
| road_spend | 80.3 | 8.2 | 647.3 |
| fire_spend | 41.6 | 0.8 | 474.7 |
| police_spend | 71.9 | 6.0 | 604.1 |
| powered_zones | 5.8 | 0.7 | 8.6 |
| unpowered_zones | 4.3 | 0.6 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 52.6 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1768.8 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 231.5 | 130.7 | 533.4 |
| com_valve | 628.9 | 541.8 | 962.1 |
| ind_valve | 636.4 | 446.9 | 814.5 |
| pop | 3259.3 | 1810.1 | 6881.1 |
| res_pop | 71.9 | 39.6 | 131.0 |
| com_pop | 6.9 | 4.5 | 12.1 |
| ind_pop | 10.0 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 51.6 | 26.2 | 83.7 |
| tax_fund | 139.7 | 47.1 | 1400.1 |
| road_spend | 74.8 | 8.1 | 645.8 |
| fire_spend | 37.4 | 0.8 | 464.7 |
| police_spend | 73.4 | 6.4 | 591.3 |
| powered_zones | 6.7 | 0.9 | 10.7 |
| unpowered_zones | 4.7 | 0.8 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.4 |
| road_total | 52.5 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1197.9 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 305.5 | 187.8 | 1348.3 |
| com_valve | 504.5 | 385.4 | 1188.9 |
| ind_valve | 396.1 | 305.2 | 1051.7 |
| pop | 3283.6 | 1548.5 | 9108.7 |
| res_pop | 75.0 | 37.0 | 172.8 |
| com_pop | 7.2 | 4.2 | 15.7 |
| ind_pop | 9.7 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 39.7 | 21.3 | 111.7 |
| tax_fund | 148.6 | 68.0 | 1609.5 |
| road_spend | 100.8 | 8.8 | 653.2 |
| fire_spend | 57.2 | 1.1 | 512.0 |
| police_spend | 66.2 | 4.6 | 651.4 |
| powered_zones | 2.4 | 0.0 | 0.5 |
| unpowered_zones | 2.6 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 53.2 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.002 | 0.838 |
| traffic | 1.032 | 0.772 |
| pollution | 1.509 | 0.706 |
| land_value | 0.616 | 0.325 |
| crime | 0.983 | 0.566 |
| rate_of_growth | 0.975 | 0.819 |
| fire_coverage | 1.701 | 0.123 |
| police_coverage | 0.923 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.582 | 0.258 | 0.358 | 0.336 to 0.377 | 0.562 | 0.140 | 0.224 | 0.185 to 0.265 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.503 | 0.008 | 0.006 |
| all plans | 12 | 0.308 | 0.092 | 0.037 |
| all plans | 24 | 0.345 | 0.170 | 0.059 |
| state-reading plans | 1 | 0.522 | 0.009 | 0.006 |
| state-reading plans | 12 | 0.311 | 0.115 | 0.037 |
| state-reading plans | 24 | 0.364 | 0.219 | 0.058 |
| open-loop plans | 1 | 0.513 | 0.001 | 0.007 |
| open-loop plans | 12 | 0.420 | 0.037 | 0.038 |
| open-loop plans | 24 | 0.424 | 0.060 | 0.065 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -218.44 |
| tile_cat | -30.98 |
| flags | -14.79 |
| power | -2.93 |
| half | -2386.90 |
| eighth | -36.41 |
| scalars_s2 | -6.43 |
| build_cost | -1.58 |
| scalars | -13.74 |
| ledger | -13.11 |
| bk | -20.43 |
| sc_res_pop | -2.05 |
| sc_com_pop | -0.26 |
| sc_ind_pop | -0.33 |
| sc_powered_zones | -0.14 |
| sc_unpowered_zones | -0.20 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.41 |
| sc_res_valve | -1.00 |
| sc_com_valve | -2.02 |
| sc_ind_valve | -1.62 |
| sc_score | -0.39 |
| sc_funds | -1.09 |
| sc_tax_fund | -0.43 |
| sc_road_spend | -0.46 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.15 |
| lg_sprite_cycle | -0.75 |
| lg_total_pop | -1.57 |
| lg_res_hist0 | -0.54 |
| lg_res_hist1 | -0.42 |
| lg_com_hist0 | -0.13 |
| lg_com_hist1 | -0.13 |
| lg_ind_hist0 | -0.20 |
| lg_ind_hist1 | -0.28 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.54 |
| lg_police_fund | -0.14 |
| lg_fire_fund | -0.13 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.90 |
| lg_pollution_max_y | -2.86 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.58 |
| com_rate | -2.12 |
| kl | 12.58 |
| elbo | -2738.17 |

## os_50m_cov_samples_004800000_dec-a

samples consumed: 4800000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "8477bf32c75b0a4a", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.299 | 0.283 | 0.291 | 0.270 to 0.310 | 0.192 | 0.168 | 0.179 | 0.153 to 0.210 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.308 | 0.293 | 0.300 | 0.279 to 0.320 | 0.208 | 0.182 | 0.195 | 0.163 to 0.229 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.265 | 0.248 | 0.256 | 0.235 to 0.277 | 0.136 | 0.118 | 0.126 | 0.109 to 0.147 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.550 | 0.204 | 0.011 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.390 / 0.402 |
| all plans | 500 | 12 | 0.383 | 0.146 | 0.079 / 0.003 / 0.378 | 0.046 / 0.026 / 0.103 | 0.378 / 0.428 |
| all plans | 500 | 24 | 0.435 | 0.167 | 0.114 / 0.005 / 0.678 | 0.073 / 0.042 / 0.160 | 0.346 / 0.408 |
| state-reading plans | 394 | 1 | 0.558 | 0.208 | 0.013 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.425 / 0.436 |
| state-reading plans | 394 | 12 | 0.386 | 0.151 | 0.090 / 0.003 / 0.465 | 0.046 / 0.025 / 0.103 | 0.397 / 0.442 |
| state-reading plans | 394 | 24 | 0.452 | 0.184 | 0.135 / 0.005 / 0.791 | 0.072 / 0.044 / 0.150 | 0.358 / 0.412 |
| open-loop plans | 106 | 1 | 0.539 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.234 / 0.257 |
| open-loop plans | 106 | 12 | 0.555 | 0.131 | 0.036 / 0.002 / 0.061 | 0.049 / 0.031 / 0.103 | 0.300 / 0.372 |
| open-loop plans | 106 | 24 | 0.665 | 0.122 | 0.043 / 0.005 / 0.140 | 0.079 / 0.036 / 0.203 | 0.300 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1792 | 0.864 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2911 | 0.918 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2095.5000 | 0.647 |
| funds_mae_12m | 5714.0800 | 36.8760 | 968.6432 | 0.836 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 209.9133 | 0.809 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 553.0733 | 0.770 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 346.7638 | 0.866 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0464 | 0.735 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0794 | 0.796 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3776 | 0.883 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3703 | 0.862 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3563.0050 | 0.677 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1267.3130 | 0.835 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 258.1030 | 0.795 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 615.0182 | 0.788 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 592.7625 | 0.607 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0733 | 0.737 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1135 | 0.838 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3458 | 0.849 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3408 | 0.836 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1267.3 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 258.1 | 142.8 | 706.1 |
| com_valve | 615.0 | 508.6 | 1010.2 |
| ind_valve | 592.8 | 416.9 | 864.8 |
| pop | 3563.0 | 1754.6 | 7353.4 |
| res_pop | 77.8 | 39.0 | 139.9 |
| com_pop | 7.4 | 4.4 | 12.8 |
| ind_pop | 10.4 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 58.6 | 25.2 | 89.6 |
| tax_fund | 142.1 | 51.5 | 1444.5 |
| road_spend | 75.5 | 8.2 | 647.3 |
| fire_spend | 35.8 | 0.8 | 474.7 |
| police_spend | 54.3 | 6.0 | 604.1 |
| powered_zones | 5.2 | 0.7 | 8.6 |
| unpowered_zones | 3.7 | 0.6 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 47.9 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1320.9 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 238.6 | 130.7 | 533.4 |
| com_valve | 643.7 | 541.8 | 962.1 |
| ind_valve | 638.7 | 446.9 | 814.5 |
| pop | 3563.1 | 1810.1 | 6881.1 |
| res_pop | 76.7 | 39.6 | 131.0 |
| com_pop | 7.4 | 4.5 | 12.1 |
| ind_pop | 10.4 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 60.9 | 26.2 | 83.7 |
| tax_fund | 137.0 | 47.1 | 1400.1 |
| road_spend | 70.1 | 8.1 | 645.8 |
| fire_spend | 32.8 | 0.8 | 464.7 |
| police_spend | 53.6 | 6.4 | 591.3 |
| powered_zones | 5.8 | 0.9 | 10.7 |
| unpowered_zones | 4.1 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.4 |
| road_total | 48.3 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1068.2 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 330.7 | 187.8 | 1348.3 |
| com_valve | 508.4 | 385.4 | 1188.9 |
| ind_valve | 422.0 | 305.2 | 1051.7 |
| pop | 3562.6 | 1548.5 | 9108.7 |
| res_pop | 81.9 | 37.0 | 172.8 |
| com_pop | 7.2 | 4.2 | 15.7 |
| ind_pop | 10.3 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.7 | 21.3 | 111.7 |
| tax_fund | 161.2 | 68.0 | 1609.5 |
| road_spend | 95.8 | 8.8 | 653.2 |
| fire_spend | 47.1 | 1.1 | 512.0 |
| police_spend | 56.9 | 4.6 | 651.4 |
| powered_zones | 2.7 | 0.0 | 0.5 |
| unpowered_zones | 2.3 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 46.5 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.020 | 0.838 |
| traffic | 1.025 | 0.772 |
| pollution | 1.515 | 0.706 |
| land_value | 0.608 | 0.325 |
| crime | 0.981 | 0.566 |
| rate_of_growth | 0.987 | 0.819 |
| fire_coverage | 1.644 | 0.123 |
| police_coverage | 0.918 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.551 | 0.261 | 0.354 | 0.333 to 0.373 | 0.469 | 0.140 | 0.216 | 0.178 to 0.255 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.408 | 0.005 | 0.006 |
| all plans | 12 | 0.288 | 0.066 | 0.040 |
| all plans | 24 | 0.340 | 0.131 | 0.063 |
| state-reading plans | 1 | 0.425 | 0.006 | 0.006 |
| state-reading plans | 12 | 0.290 | 0.075 | 0.040 |
| state-reading plans | 24 | 0.357 | 0.156 | 0.062 |
| open-loop plans | 1 | 0.380 | 0.001 | 0.007 |
| open-loop plans | 12 | 0.386 | 0.042 | 0.037 |
| open-loop plans | 24 | 0.470 | 0.053 | 0.067 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -215.29 |
| tile_cat | -30.47 |
| flags | -14.52 |
| power | -2.71 |
| half | -2341.16 |
| eighth | -35.29 |
| scalars_s2 | -5.63 |
| build_cost | -1.39 |
| scalars | -12.59 |
| ledger | -12.99 |
| bk | -19.95 |
| sc_res_pop | -1.69 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.22 |
| sc_powered_zones | -0.07 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.37 |
| sc_res_valve | -0.97 |
| sc_com_valve | -1.94 |
| sc_ind_valve | -1.26 |
| sc_score | -0.44 |
| sc_funds | -1.00 |
| sc_tax_fund | -0.43 |
| sc_road_spend | -0.53 |
| sc_fire_spend | -0.20 |
| sc_police_spend | -0.19 |
| lg_sprite_cycle | -0.92 |
| lg_total_pop | -1.55 |
| lg_res_hist0 | -0.32 |
| lg_res_hist1 | -0.35 |
| lg_com_hist0 | -0.04 |
| lg_com_hist1 | -0.09 |
| lg_ind_hist0 | -0.08 |
| lg_ind_hist1 | -0.26 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.63 |
| lg_police_fund | -0.17 |
| lg_fire_fund | -0.16 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.01 |
| lg_pollution_max_x | -2.94 |
| lg_pollution_max_y | -2.93 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.34 |
| com_rate | -1.62 |
| kl | 13.55 |
| elbo | -2685.92 |

## os_50m_cov_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "8477bf32c75b0a4a", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.302 | 0.285 | 0.293 | 0.273 to 0.313 | 0.194 | 0.168 | 0.180 | 0.154 to 0.211 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.311 | 0.294 | 0.302 | 0.281 to 0.322 | 0.210 | 0.182 | 0.195 | 0.164 to 0.230 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.268 | 0.251 | 0.259 | 0.238 to 0.281 | 0.139 | 0.122 | 0.130 | 0.113 to 0.149 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.514 | 0.204 | 0.008 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.395 / 0.402 |
| all plans | 500 | 12 | 0.364 | 0.146 | 0.067 / 0.003 / 0.378 | 0.047 / 0.026 / 0.103 | 0.377 / 0.428 |
| all plans | 500 | 24 | 0.433 | 0.167 | 0.099 / 0.005 / 0.678 | 0.074 / 0.042 / 0.160 | 0.345 / 0.408 |
| state-reading plans | 394 | 1 | 0.515 | 0.208 | 0.010 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.432 / 0.436 |
| state-reading plans | 394 | 12 | 0.367 | 0.151 | 0.074 / 0.003 / 0.465 | 0.047 / 0.025 / 0.103 | 0.397 / 0.442 |
| state-reading plans | 394 | 24 | 0.451 | 0.184 | 0.114 / 0.005 / 0.791 | 0.073 / 0.044 / 0.150 | 0.357 / 0.412 |
| open-loop plans | 106 | 1 | 0.519 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.234 / 0.257 |
| open-loop plans | 106 | 12 | 0.556 | 0.131 | 0.035 / 0.002 / 0.061 | 0.046 / 0.031 / 0.103 | 0.300 / 0.372 |
| open-loop plans | 106 | 24 | 0.735 | 0.122 | 0.055 / 0.005 / 0.140 | 0.079 / 0.036 / 0.203 | 0.299 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1803 | 0.869 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2933 | 0.925 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2101.8850 | 0.645 |
| funds_mae_12m | 5714.0800 | 36.8760 | 831.6458 | 0.860 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 214.3845 | 0.800 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 537.9155 | 0.788 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 345.0560 | 0.869 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0467 | 0.732 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0667 | 0.829 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3768 | 0.881 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3695 | 0.860 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3664.0500 | 0.659 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1131.9760 | 0.854 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 280.7518 | 0.755 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 637.1270 | 0.744 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 577.9385 | 0.640 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0738 | 0.732 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0987 | 0.860 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3447 | 0.846 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3391 | 0.832 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1132.0 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 280.8 | 142.8 | 706.1 |
| com_valve | 637.1 | 508.6 | 1010.2 |
| ind_valve | 577.9 | 416.9 | 864.8 |
| pop | 3664.1 | 1754.6 | 7353.4 |
| res_pop | 79.3 | 39.0 | 139.9 |
| com_pop | 7.7 | 4.4 | 12.8 |
| ind_pop | 10.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 70.0 | 25.2 | 89.6 |
| tax_fund | 141.0 | 51.5 | 1444.5 |
| road_spend | 73.2 | 8.2 | 647.3 |
| fire_spend | 34.9 | 0.8 | 474.7 |
| police_spend | 49.1 | 6.0 | 604.1 |
| powered_zones | 5.4 | 0.7 | 8.6 |
| unpowered_zones | 3.7 | 0.6 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 45.4 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1142.5 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 265.4 | 130.7 | 533.4 |
| com_valve | 669.8 | 541.8 | 962.1 |
| ind_valve | 626.2 | 446.9 | 814.5 |
| pop | 3647.9 | 1810.1 | 6881.1 |
| res_pop | 78.0 | 39.6 | 131.0 |
| com_pop | 7.7 | 4.5 | 12.1 |
| ind_pop | 10.7 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 73.5 | 26.2 | 83.7 |
| tax_fund | 136.3 | 47.1 | 1400.1 |
| road_spend | 67.3 | 8.1 | 645.8 |
| fire_spend | 30.7 | 0.8 | 464.7 |
| police_spend | 48.1 | 6.4 | 591.3 |
| powered_zones | 5.9 | 0.9 | 10.7 |
| unpowered_zones | 4.1 | 0.8 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.4 |
| road_total | 45.8 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1093.0 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 337.7 | 187.8 | 1348.3 |
| com_valve | 515.5 | 385.4 | 1188.9 |
| ind_valve | 398.4 | 305.2 | 1051.7 |
| pop | 3724.1 | 1548.5 | 9108.7 |
| res_pop | 84.5 | 37.0 | 172.8 |
| com_pop | 7.7 | 4.2 | 15.7 |
| ind_pop | 10.6 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 56.8 | 21.3 | 111.7 |
| tax_fund | 158.2 | 68.0 | 1609.5 |
| road_spend | 94.9 | 8.8 | 653.2 |
| fire_spend | 50.5 | 1.1 | 512.0 |
| police_spend | 53.2 | 4.6 | 651.4 |
| powered_zones | 3.4 | 0.0 | 0.5 |
| unpowered_zones | 2.2 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 43.8 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.036 | 0.838 |
| traffic | 1.041 | 0.772 |
| pollution | 1.529 | 0.706 |
| land_value | 0.612 | 0.325 |
| crime | 1.003 | 0.566 |
| rate_of_growth | 0.986 | 0.819 |
| fire_coverage | 1.707 | 0.123 |
| police_coverage | 0.964 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.538 | 0.263 | 0.353 | 0.332 to 0.372 | 0.438 | 0.141 | 0.214 | 0.176 to 0.253 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.388 | 0.004 | 0.006 |
| all plans | 12 | 0.281 | 0.057 | 0.033 |
| all plans | 24 | 0.345 | 0.098 | 0.062 |
| state-reading plans | 1 | 0.416 | 0.005 | 0.006 |
| state-reading plans | 12 | 0.284 | 0.060 | 0.033 |
| state-reading plans | 24 | 0.362 | 0.118 | 0.061 |
| open-loop plans | 1 | 0.361 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.422 | 0.040 | 0.034 |
| open-loop plans | 24 | 0.583 | 0.058 | 0.063 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -213.17 |
| tile_cat | -30.34 |
| flags | -14.51 |
| power | -2.65 |
| half | -2321.39 |
| eighth | -34.78 |
| scalars_s2 | -5.24 |
| build_cost | -1.18 |
| scalars | -12.17 |
| ledger | -13.71 |
| bk | -20.65 |
| sc_res_pop | -1.50 |
| sc_com_pop | -0.12 |
| sc_ind_pop | -0.20 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.35 |
| sc_res_valve | -0.97 |
| sc_com_valve | -1.93 |
| sc_ind_valve | -1.13 |
| sc_score | -0.46 |
| sc_funds | -0.99 |
| sc_tax_fund | -0.43 |
| sc_road_spend | -0.56 |
| sc_fire_spend | -0.24 |
| sc_police_spend | -0.21 |
| lg_sprite_cycle | -1.07 |
| lg_total_pop | -1.54 |
| lg_res_hist0 | -0.26 |
| lg_res_hist1 | -0.64 |
| lg_com_hist0 | -0.04 |
| lg_com_hist1 | -0.20 |
| lg_ind_hist0 | -0.09 |
| lg_ind_hist1 | -0.35 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.71 |
| lg_police_fund | -0.21 |
| lg_fire_fund | -0.17 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.01 |
| lg_pollution_max_x | -2.96 |
| lg_pollution_max_y | -2.94 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.24 |
| com_rate | -1.51 |
| kl | 14.27 |
| elbo | -2663.94 |
