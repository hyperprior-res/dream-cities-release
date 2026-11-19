## os_100m_small_samples_003000064_dec-a

samples consumed: 3000064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.293 | 0.284 | 0.288 | 0.268 to 0.307 | 0.182 | 0.164 | 0.173 | 0.146 to 0.204 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.301 | 0.291 | 0.296 | 0.275 to 0.315 | 0.197 | 0.177 | 0.186 | 0.155 to 0.222 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.263 | 0.256 | 0.259 | 0.238 to 0.282 | 0.133 | 0.121 | 0.127 | 0.107 to 0.150 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.710 | 0.204 | 0.008 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.390 / 0.402 |
| all plans | 500 | 12 | 0.509 | 0.146 | 0.053 / 0.003 / 0.378 | 0.043 / 0.026 / 0.103 | 0.382 / 0.428 |
| all plans | 500 | 24 | 0.534 | 0.167 | 0.068 / 0.005 / 0.678 | 0.069 / 0.042 / 0.160 | 0.353 / 0.408 |
| state-reading plans | 394 | 1 | 0.667 | 0.208 | 0.010 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.427 / 0.436 |
| state-reading plans | 394 | 12 | 0.512 | 0.151 | 0.063 / 0.003 / 0.465 | 0.044 / 0.025 / 0.103 | 0.402 / 0.442 |
| state-reading plans | 394 | 24 | 0.552 | 0.184 | 0.087 / 0.005 / 0.791 | 0.067 / 0.044 / 0.150 | 0.366 / 0.412 |
| open-loop plans | 106 | 1 | 0.810 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.226 / 0.257 |
| open-loop plans | 106 | 12 | 0.701 | 0.131 | 0.018 / 0.002 / 0.061 | 0.042 / 0.031 / 0.103 | 0.304 / 0.372 |
| open-loop plans | 106 | 24 | 0.767 | 0.122 | 0.023 / 0.005 / 0.140 | 0.074 / 0.036 / 0.203 | 0.306 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1726 | 0.832 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2883 | 0.909 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1864.1850 | 0.724 |
| funds_mae_12m | 5714.0800 | 36.8760 | 763.6843 | 0.872 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 213.9080 | 0.801 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 510.2473 | 0.820 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 350.5955 | 0.860 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0433 | 0.776 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0534 | 0.865 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3821 | 0.893 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3721 | 0.866 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3174.4650 | 0.746 |
| funds_mae_24m | 7364.5720 | 66.5620 | 882.8535 | 0.888 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 267.2452 | 0.779 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 566.0593 | 0.886 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 594.2432 | 0.604 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0689 | 0.774 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0685 | 0.905 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3531 | 0.866 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3459 | 0.848 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 882.9 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 267.2 | 142.8 | 706.1 |
| com_valve | 566.1 | 508.6 | 1010.2 |
| ind_valve | 594.2 | 416.9 | 864.8 |
| pop | 3174.5 | 1754.6 | 7353.4 |
| res_pop | 69.3 | 39.0 | 139.9 |
| com_pop | 6.3 | 4.4 | 12.8 |
| ind_pop | 10.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.8 | 25.2 | 89.6 |
| tax_fund | 189.4 | 51.5 | 1444.5 |
| road_spend | 96.0 | 8.2 | 647.3 |
| fire_spend | 55.5 | 0.8 | 474.7 |
| police_spend | 91.4 | 6.0 | 604.1 |
| powered_zones | 7.1 | 0.7 | 8.6 |
| unpowered_zones | 4.6 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 54.8 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 904.9 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 257.2 | 130.7 | 533.4 |
| com_valve | 594.7 | 541.8 | 962.1 |
| ind_valve | 643.2 | 446.9 | 814.5 |
| pop | 3150.8 | 1810.1 | 6881.1 |
| res_pop | 68.3 | 39.6 | 131.0 |
| com_pop | 6.2 | 4.5 | 12.1 |
| ind_pop | 10.7 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 46.2 | 26.2 | 83.7 |
| tax_fund | 174.9 | 47.1 | 1400.1 |
| road_spend | 87.6 | 8.1 | 645.8 |
| fire_spend | 51.3 | 0.8 | 464.7 |
| police_spend | 89.3 | 6.4 | 591.3 |
| powered_zones | 8.3 | 0.9 | 10.7 |
| unpowered_zones | 4.9 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 55.1 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 800.8 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 304.6 | 187.8 | 1348.3 |
| com_valve | 459.5 | 385.4 | 1188.9 |
| ind_valve | 412.3 | 305.2 | 1051.7 |
| pop | 3262.5 | 1548.5 | 9108.7 |
| res_pop | 73.3 | 37.0 | 172.8 |
| com_pop | 6.4 | 4.2 | 15.7 |
| ind_pop | 10.5 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 35.1 | 21.3 | 111.7 |
| tax_fund | 243.0 | 68.0 | 1609.5 |
| road_spend | 127.4 | 8.8 | 653.2 |
| fire_spend | 71.3 | 1.1 | 512.0 |
| police_spend | 99.1 | 4.6 | 651.4 |
| powered_zones | 2.9 | 0.0 | 0.5 |
| unpowered_zones | 3.3 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 53.8 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.009 | 0.838 |
| traffic | 1.044 | 0.772 |
| pollution | 1.397 | 0.706 |
| land_value | 0.625 | 0.325 |
| crime | 0.972 | 0.566 |
| rate_of_growth | 1.013 | 0.819 |
| fire_coverage | 0.902 | 0.123 |
| police_coverage | 0.864 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.512 | 0.266 | 0.350 | 0.329 to 0.369 | 0.456 | 0.133 | 0.206 | 0.168 to 0.248 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.488 | 0.004 | 0.005 |
| all plans | 12 | 0.338 | 0.037 | 0.035 |
| all plans | 24 | 0.368 | 0.061 | 0.059 |
| state-reading plans | 1 | 0.464 | 0.004 | 0.005 |
| state-reading plans | 12 | 0.342 | 0.041 | 0.035 |
| state-reading plans | 24 | 0.386 | 0.071 | 0.059 |
| open-loop plans | 1 | 0.523 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.443 | 0.013 | 0.036 |
| open-loop plans | 24 | 0.471 | 0.025 | 0.059 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -243.51 |
| tile_cat | -34.54 |
| flags | -17.09 |
| power | -3.60 |
| half | -2505.68 |
| eighth | -38.96 |
| scalars_s2 | -6.89 |
| build_cost | -1.42 |
| scalars | -16.99 |
| ledger | -20.39 |
| bk | -30.49 |
| sc_res_pop | -2.16 |
| sc_com_pop | -0.36 |
| sc_ind_pop | -0.44 |
| sc_powered_zones | -0.18 |
| sc_unpowered_zones | -0.24 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.44 |
| sc_res_valve | -1.12 |
| sc_com_valve | -2.24 |
| sc_ind_valve | -1.86 |
| sc_score | -0.90 |
| sc_funds | -1.44 |
| sc_tax_fund | -0.79 |
| sc_road_spend | -1.13 |
| sc_fire_spend | -0.33 |
| sc_police_spend | -0.30 |
| lg_sprite_cycle | -0.86 |
| lg_total_pop | -2.15 |
| lg_res_hist0 | -1.32 |
| lg_res_hist1 | -0.91 |
| lg_com_hist0 | -0.41 |
| lg_com_hist1 | -0.20 |
| lg_ind_hist0 | -0.49 |
| lg_ind_hist1 | -0.47 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.01 |
| lg_need_hospital | -0.13 |
| lg_need_church | -0.12 |
| lg_road_fund | -1.18 |
| lg_police_fund | -0.24 |
| lg_fire_fund | -0.24 |
| lg_auto_budget | -0.02 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.27 |
| lg_city_center_y | -0.25 |
| lg_pollution_max_x | -4.04 |
| lg_pollution_max_y | -4.34 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.66 |
| terrain | -6.24 |
| com_rate | -4.55 |
| kl | 12.29 |
| elbo | -2905.26 |

## os_100m_small_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.305 | 0.292 | 0.298 | 0.276 to 0.319 | 0.185 | 0.160 | 0.171 | 0.144 to 0.202 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.312 | 0.300 | 0.306 | 0.283 to 0.327 | 0.199 | 0.172 | 0.184 | 0.152 to 0.220 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.276 | 0.261 | 0.269 | 0.244 to 0.293 | 0.137 | 0.120 | 0.128 | 0.109 to 0.151 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.499 | 0.204 | 0.005 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.404 / 0.402 |
| all plans | 500 | 12 | 0.379 | 0.146 | 0.036 / 0.003 / 0.378 | 0.051 / 0.026 / 0.103 | 0.379 / 0.428 |
| all plans | 500 | 24 | 0.444 | 0.167 | 0.050 / 0.005 / 0.678 | 0.083 / 0.042 / 0.160 | 0.348 / 0.408 |
| state-reading plans | 394 | 1 | 0.475 | 0.208 | 0.006 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.442 / 0.436 |
| state-reading plans | 394 | 12 | 0.377 | 0.151 | 0.040 / 0.003 / 0.465 | 0.050 / 0.025 / 0.103 | 0.399 / 0.442 |
| state-reading plans | 394 | 24 | 0.463 | 0.184 | 0.056 / 0.005 / 0.791 | 0.080 / 0.044 / 0.150 | 0.362 / 0.412 |
| open-loop plans | 106 | 1 | 0.537 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.230 / 0.257 |
| open-loop plans | 106 | 12 | 0.543 | 0.131 | 0.021 / 0.002 / 0.061 | 0.055 / 0.031 / 0.103 | 0.298 / 0.372 |
| open-loop plans | 106 | 24 | 0.687 | 0.122 | 0.028 / 0.005 / 0.140 | 0.093 / 0.036 / 0.203 | 0.297 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1713 | 0.826 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2982 | 0.940 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2239.9200 | 0.599 |
| funds_mae_12m | 5714.0800 | 36.8760 | 620.3513 | 0.897 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 238.9257 | 0.754 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 515.3278 | 0.814 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 364.5585 | 0.839 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0510 | 0.675 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0356 | 0.912 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3788 | 0.886 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3657 | 0.851 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3981.1850 | 0.602 |
| funds_mae_24m | 7364.5720 | 66.5620 | 726.6220 | 0.910 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 355.1737 | 0.623 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 613.9578 | 0.790 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 636.1268 | 0.510 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0835 | 0.650 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0495 | 0.933 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3479 | 0.854 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3389 | 0.831 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 726.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 355.2 | 142.8 | 706.1 |
| com_valve | 614.0 | 508.6 | 1010.2 |
| ind_valve | 636.1 | 416.9 | 864.8 |
| pop | 3981.2 | 1754.6 | 7353.4 |
| res_pop | 91.3 | 39.0 | 139.9 |
| com_pop | 7.1 | 4.4 | 12.8 |
| ind_pop | 12.3 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 61.3 | 25.2 | 89.6 |
| tax_fund | 213.1 | 51.5 | 1444.5 |
| road_spend | 95.1 | 8.2 | 647.3 |
| fire_spend | 49.5 | 0.8 | 474.7 |
| police_spend | 78.8 | 6.0 | 604.1 |
| powered_zones | 5.0 | 0.7 | 8.6 |
| unpowered_zones | 3.7 | 0.6 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 41.3 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 686.3 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 359.9 | 130.7 | 533.4 |
| com_valve | 645.7 | 541.8 | 962.1 |
| ind_valve | 681.7 | 446.9 | 814.5 |
| pop | 3883.6 | 1810.1 | 6881.1 |
| res_pop | 88.6 | 39.6 | 131.0 |
| com_pop | 7.0 | 4.5 | 12.1 |
| ind_pop | 12.4 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 63.8 | 26.2 | 83.7 |
| tax_fund | 197.4 | 47.1 | 1400.1 |
| road_spend | 86.7 | 8.1 | 645.8 |
| fire_spend | 45.5 | 0.8 | 464.7 |
| police_spend | 76.1 | 6.4 | 591.3 |
| powered_zones | 5.7 | 0.9 | 10.7 |
| unpowered_zones | 4.1 | 0.8 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.4 |
| road_total | 41.6 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 876.5 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 337.6 | 187.8 | 1348.3 |
| com_valve | 495.8 | 385.4 | 1188.9 |
| ind_valve | 466.8 | 305.2 | 1051.7 |
| pop | 4344.0 | 1548.5 | 9108.7 |
| res_pop | 101.3 | 37.0 | 172.8 |
| com_pop | 7.5 | 4.2 | 15.7 |
| ind_pop | 12.2 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 52.3 | 21.3 | 111.7 |
| tax_fund | 271.7 | 68.0 | 1609.5 |
| road_spend | 126.2 | 8.8 | 653.2 |
| fire_spend | 64.6 | 1.1 | 512.0 |
| police_spend | 88.8 | 4.6 | 651.4 |
| powered_zones | 2.7 | 0.0 | 0.5 |
| unpowered_zones | 2.2 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 40.3 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.037 | 0.838 |
| traffic | 1.028 | 0.772 |
| pollution | 1.263 | 0.706 |
| land_value | 0.641 | 0.325 |
| crime | 0.972 | 0.566 |
| rate_of_growth | 1.043 | 0.819 |
| fire_coverage | 0.829 | 0.123 |
| police_coverage | 0.885 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.355 | 0.289 | 0.318 | 0.295 to 0.340 | 0.212 | 0.150 | 0.176 | 0.147 to 0.210 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.397 | 0.002 | 0.005 |
| all plans | 12 | 0.307 | 0.024 | 0.043 |
| all plans | 24 | 0.366 | 0.048 | 0.077 |
| state-reading plans | 1 | 0.377 | 0.003 | 0.005 |
| state-reading plans | 12 | 0.305 | 0.026 | 0.042 |
| state-reading plans | 24 | 0.384 | 0.055 | 0.073 |
| open-loop plans | 1 | 0.421 | 0.001 | 0.005 |
| open-loop plans | 12 | 0.435 | 0.015 | 0.057 |
| open-loop plans | 24 | 0.553 | 0.030 | 0.087 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -379.61 |
| tile_cat | -44.76 |
| flags | -19.70 |
| power | -6.34 |
| half | -3039.99 |
| eighth | -57.78 |
| scalars_s2 | -5.31 |
| build_cost | -0.98 |
| scalars | -33.76 |
| ledger | -52.86 |
| bk | -81.31 |
| sc_res_pop | -1.51 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.23 |
| sc_powered_zones | -0.05 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.33 |
| sc_res_valve | -1.75 |
| sc_com_valve | -3.06 |
| sc_ind_valve | -3.15 |
| sc_score | -7.03 |
| sc_funds | -3.63 |
| sc_tax_fund | -3.89 |
| sc_road_spend | -4.34 |
| sc_fire_spend | -0.92 |
| sc_police_spend | -0.67 |
| lg_sprite_cycle | -1.50 |
| lg_total_pop | -3.35 |
| lg_res_hist0 | -4.27 |
| lg_res_hist1 | -4.79 |
| lg_com_hist0 | -1.97 |
| lg_com_hist1 | -1.43 |
| lg_ind_hist0 | -1.85 |
| lg_ind_hist1 | -3.42 |
| lg_res_cap | -0.05 |
| lg_com_cap | -0.07 |
| lg_ind_cap | -0.02 |
| lg_need_hospital | -0.32 |
| lg_need_church | -0.39 |
| lg_road_fund | -2.38 |
| lg_police_fund | -0.52 |
| lg_fire_fund | -1.30 |
| lg_auto_budget | -0.04 |
| lg_fire_pop | -0.11 |
| lg_city_center_x | -1.12 |
| lg_city_center_y | -0.82 |
| lg_pollution_max_x | -9.01 |
| lg_pollution_max_y | -9.69 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -4.45 |
| terrain | -5.98 |
| com_rate | -9.54 |
| kl | 13.53 |
| elbo | -3664.83 |
