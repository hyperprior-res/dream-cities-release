## sf_100m_full_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.272 | 0.288 | 0.280 | 0.259 to 0.300 | 0.164 | 0.178 | 0.171 | 0.147 to 0.198 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.281 | 0.297 | 0.289 | 0.267 to 0.309 | 0.177 | 0.190 | 0.183 | 0.155 to 0.214 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.240 | 0.257 | 0.248 | 0.225 to 0.270 | 0.122 | 0.136 | 0.128 | 0.111 to 0.149 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.588 | 0.204 | 0.003 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.384 / 0.402 |
| all plans | 500 | 12 | 0.423 | 0.146 | 0.035 / 0.003 / 0.378 | 0.040 / 0.026 / 0.103 | 0.351 / 0.428 |
| all plans | 500 | 24 | 0.497 | 0.167 | 0.056 / 0.005 / 0.678 | 0.071 / 0.042 / 0.160 | 0.319 / 0.408 |
| state-reading plans | 394 | 1 | 0.600 | 0.208 | 0.004 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.420 / 0.436 |
| state-reading plans | 394 | 12 | 0.419 | 0.151 | 0.038 / 0.003 / 0.465 | 0.040 / 0.025 / 0.103 | 0.370 / 0.442 |
| state-reading plans | 394 | 24 | 0.503 | 0.184 | 0.063 / 0.005 / 0.791 | 0.069 / 0.044 / 0.150 | 0.334 / 0.412 |
| open-loop plans | 106 | 1 | 0.600 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.230 / 0.257 |
| open-loop plans | 106 | 12 | 0.740 | 0.131 | 0.020 / 0.002 / 0.061 | 0.039 / 0.031 / 0.103 | 0.278 / 0.372 |
| open-loop plans | 106 | 24 | 0.932 | 0.122 | 0.033 / 0.005 / 0.140 | 0.078 / 0.036 / 0.203 | 0.267 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1707 | 0.823 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2800 | 0.883 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1714.4500 | 0.773 |
| funds_mae_12m | 5714.0800 | 36.8760 | 585.9985 | 0.903 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 218.5940 | 0.793 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 532.2805 | 0.794 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 369.2395 | 0.832 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0398 | 0.821 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0350 | 0.914 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3505 | 0.820 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3504 | 0.816 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3273.8700 | 0.729 |
| funds_mae_24m | 7364.5720 | 66.5620 | 724.2437 | 0.910 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 291.6765 | 0.736 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 610.4333 | 0.797 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 577.4655 | 0.641 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0709 | 0.757 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0560 | 0.924 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3194 | 0.784 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3189 | 0.782 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 724.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 291.7 | 142.8 | 706.1 |
| com_valve | 610.4 | 508.6 | 1010.2 |
| ind_valve | 577.5 | 416.9 | 864.8 |
| pop | 3273.9 | 1754.6 | 7353.4 |
| res_pop | 72.1 | 39.0 | 139.9 |
| com_pop | 6.8 | 4.4 | 12.8 |
| ind_pop | 11.0 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 54.9 | 25.2 | 89.6 |
| tax_fund | 143.6 | 51.5 | 1444.5 |
| road_spend | 83.9 | 8.2 | 647.3 |
| fire_spend | 39.6 | 0.8 | 474.7 |
| police_spend | 60.8 | 6.0 | 604.1 |
| powered_zones | 6.0 | 0.7 | 8.6 |
| unpowered_zones | 4.3 | 0.6 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 49.7 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 675.1 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 260.7 | 130.7 | 533.4 |
| com_valve | 634.7 | 541.8 | 962.1 |
| ind_valve | 622.2 | 446.9 | 814.5 |
| pop | 3205.5 | 1810.1 | 6881.1 |
| res_pop | 68.9 | 39.6 | 131.0 |
| com_pop | 6.7 | 4.5 | 12.1 |
| ind_pop | 10.8 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 56.8 | 26.2 | 83.7 |
| tax_fund | 131.3 | 47.1 | 1400.1 |
| road_spend | 79.0 | 8.1 | 645.8 |
| fire_spend | 36.3 | 0.8 | 464.7 |
| police_spend | 58.9 | 6.4 | 591.3 |
| powered_zones | 6.5 | 0.9 | 10.7 |
| unpowered_zones | 4.6 | 0.8 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 50.0 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 906.9 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 406.6 | 187.8 | 1348.3 |
| com_valve | 520.3 | 385.4 | 1188.9 |
| ind_valve | 411.2 | 305.2 | 1051.7 |
| pop | 3528.2 | 1548.5 | 9108.7 |
| res_pop | 83.6 | 37.0 | 172.8 |
| com_pop | 7.0 | 4.2 | 15.7 |
| ind_pop | 11.7 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 47.8 | 21.3 | 111.7 |
| tax_fund | 189.2 | 68.0 | 1609.5 |
| road_spend | 102.3 | 8.8 | 653.2 |
| fire_spend | 51.9 | 1.1 | 512.0 |
| police_spend | 68.0 | 4.6 | 651.4 |
| powered_zones | 4.1 | 0.0 | 0.5 |
| unpowered_zones | 2.9 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 48.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.151 | 0.838 |
| traffic | 0.976 | 0.772 |
| pollution | 1.670 | 0.706 |
| land_value | 0.622 | 0.325 |
| crime | 1.078 | 0.566 |
| rate_of_growth | 1.090 | 0.819 |
| fire_coverage | 0.944 | 0.123 |
| police_coverage | 0.849 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.562 | 0.265 | 0.360 | 0.339 to 0.380 | 0.500 | 0.146 | 0.226 | 0.189 to 0.265 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.440 | 0.001 | 0.006 |
| all plans | 12 | 0.288 | 0.025 | 0.028 |
| all plans | 24 | 0.349 | 0.061 | 0.053 |
| state-reading plans | 1 | 0.479 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.289 | 0.027 | 0.028 |
| state-reading plans | 24 | 0.358 | 0.072 | 0.053 |
| open-loop plans | 1 | 0.416 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.454 | 0.021 | 0.033 |
| open-loop plans | 24 | 0.572 | 0.042 | 0.049 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -208.94 |
| tile_cat | -30.62 |
| flags | -15.09 |
| power | -3.00 |
| half | -2286.45 |
| eighth | -34.24 |
| scalars_s2 | -5.77 |
| build_cost | -1.19 |
| scalars | -12.86 |
| ledger | -12.58 |
| bk | -19.67 |
| sc_res_pop | -1.79 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.24 |
| sc_powered_zones | -0.09 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.38 |
| sc_res_valve | -0.96 |
| sc_com_valve | -1.97 |
| sc_ind_valve | -1.38 |
| sc_score | -0.41 |
| sc_funds | -1.06 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.55 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.16 |
| lg_sprite_cycle | -0.76 |
| lg_total_pop | -1.46 |
| lg_res_hist0 | -0.38 |
| lg_res_hist1 | -0.30 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.08 |
| lg_ind_hist0 | -0.09 |
| lg_ind_hist1 | -0.18 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.57 |
| lg_police_fund | -0.16 |
| lg_fire_fund | -0.20 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.94 |
| lg_pollution_max_y | -2.89 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -4.47 |
| com_rate | -1.84 |
| kl | 15.20 |
| elbo | -2626.49 |

## sf_100m_full_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.275 | 0.288 | 0.281 | 0.261 to 0.300 | 0.168 | 0.178 | 0.173 | 0.150 to 0.201 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.286 | 0.296 | 0.291 | 0.269 to 0.311 | 0.183 | 0.190 | 0.187 | 0.159 to 0.219 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.236 | 0.259 | 0.247 | 0.226 to 0.268 | 0.119 | 0.137 | 0.127 | 0.110 to 0.148 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.476 | 0.204 | 0.002 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.388 / 0.402 |
| all plans | 500 | 12 | 0.400 | 0.146 | 0.028 / 0.003 / 0.378 | 0.041 / 0.026 / 0.103 | 0.339 / 0.428 |
| all plans | 500 | 24 | 0.492 | 0.167 | 0.057 / 0.005 / 0.678 | 0.068 / 0.042 / 0.160 | 0.306 / 0.408 |
| state-reading plans | 394 | 1 | 0.471 | 0.208 | 0.002 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.424 / 0.436 |
| state-reading plans | 394 | 12 | 0.397 | 0.151 | 0.030 / 0.003 / 0.465 | 0.041 / 0.025 / 0.103 | 0.358 / 0.442 |
| state-reading plans | 394 | 24 | 0.498 | 0.184 | 0.063 / 0.005 / 0.791 | 0.067 / 0.044 / 0.150 | 0.321 / 0.412 |
| open-loop plans | 106 | 1 | 0.463 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.229 / 0.257 |
| open-loop plans | 106 | 12 | 0.691 | 0.131 | 0.021 / 0.002 / 0.061 | 0.042 / 0.031 / 0.103 | 0.268 / 0.372 |
| open-loop plans | 106 | 24 | 0.921 | 0.122 | 0.040 / 0.005 / 0.140 | 0.073 / 0.036 / 0.203 | 0.253 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1727 | 0.833 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2815 | 0.888 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1779.7650 | 0.752 |
| funds_mae_12m | 5714.0800 | 36.8760 | 530.9818 | 0.913 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 219.3967 | 0.791 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 535.7397 | 0.790 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 355.8413 | 0.852 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0410 | 0.806 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0278 | 0.933 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3388 | 0.792 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3397 | 0.790 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3224.4200 | 0.737 |
| funds_mae_24m | 7364.5720 | 66.5620 | 754.4473 | 0.906 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 301.8390 | 0.718 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 641.1443 | 0.736 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 638.4000 | 0.505 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0677 | 0.784 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0569 | 0.922 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3060 | 0.751 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3058 | 0.750 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 754.4 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 301.8 | 142.8 | 706.1 |
| com_valve | 641.1 | 508.6 | 1010.2 |
| ind_valve | 638.4 | 416.9 | 864.8 |
| pop | 3224.4 | 1754.6 | 7353.4 |
| res_pop | 78.6 | 39.0 | 139.9 |
| com_pop | 7.4 | 4.4 | 12.8 |
| ind_pop | 10.2 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 60.1 | 25.2 | 89.6 |
| tax_fund | 151.9 | 51.5 | 1444.5 |
| road_spend | 82.3 | 8.2 | 647.3 |
| fire_spend | 39.5 | 0.8 | 474.7 |
| police_spend | 64.2 | 6.0 | 604.1 |
| powered_zones | 5.9 | 0.7 | 8.6 |
| unpowered_zones | 4.5 | 0.6 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 50.2 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 712.8 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 257.7 | 130.7 | 533.4 |
| com_valve | 668.7 | 541.8 | 962.1 |
| ind_valve | 692.5 | 446.9 | 814.5 |
| pop | 3190.5 | 1810.1 | 6881.1 |
| res_pop | 75.6 | 39.6 | 131.0 |
| com_pop | 7.3 | 4.5 | 12.1 |
| ind_pop | 10.2 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 62.8 | 26.2 | 83.7 |
| tax_fund | 143.7 | 47.1 | 1400.1 |
| road_spend | 77.7 | 8.1 | 645.8 |
| fire_spend | 35.7 | 0.8 | 464.7 |
| police_spend | 63.6 | 6.4 | 591.3 |
| powered_zones | 6.4 | 0.9 | 10.7 |
| unpowered_zones | 4.8 | 0.8 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.4 |
| road_total | 50.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 909.3 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 466.1 | 187.8 | 1348.3 |
| com_valve | 538.5 | 385.4 | 1188.9 |
| ind_valve | 437.5 | 305.2 | 1051.7 |
| pop | 3350.4 | 1548.5 | 9108.7 |
| res_pop | 89.9 | 37.0 | 172.8 |
| com_pop | 7.5 | 4.2 | 15.7 |
| ind_pop | 10.3 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 50.0 | 21.3 | 111.7 |
| tax_fund | 182.5 | 68.0 | 1609.5 |
| road_spend | 99.2 | 8.8 | 653.2 |
| fire_spend | 53.6 | 1.1 | 512.0 |
| police_spend | 66.4 | 4.6 | 651.4 |
| powered_zones | 4.1 | 0.0 | 0.5 |
| unpowered_zones | 3.5 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 47.5 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.163 | 0.838 |
| traffic | 0.994 | 0.772 |
| pollution | 1.714 | 0.706 |
| land_value | 0.670 | 0.325 |
| crime | 1.114 | 0.566 |
| rate_of_growth | 1.120 | 0.819 |
| fire_coverage | 1.276 | 0.123 |
| police_coverage | 0.941 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.540 | 0.266 | 0.357 | 0.337 to 0.374 | 0.448 | 0.147 | 0.222 | 0.186 to 0.261 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.366 | 0.001 | 0.006 |
| all plans | 12 | 0.287 | 0.024 | 0.031 |
| all plans | 24 | 0.364 | 0.065 | 0.051 |
| state-reading plans | 1 | 0.371 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.289 | 0.025 | 0.030 |
| state-reading plans | 24 | 0.374 | 0.074 | 0.048 |
| open-loop plans | 1 | 0.335 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.425 | 0.022 | 0.036 |
| open-loop plans | 24 | 0.589 | 0.045 | 0.063 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -207.75 |
| tile_cat | -30.31 |
| flags | -14.95 |
| power | -3.01 |
| half | -2265.71 |
| eighth | -33.72 |
| scalars_s2 | -5.21 |
| build_cost | -0.88 |
| scalars | -12.46 |
| ledger | -13.18 |
| bk | -20.42 |
| sc_res_pop | -1.46 |
| sc_com_pop | -0.13 |
| sc_ind_pop | -0.21 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.35 |
| sc_res_valve | -0.99 |
| sc_com_valve | -1.94 |
| sc_ind_valve | -1.13 |
| sc_score | -0.50 |
| sc_funds | -1.03 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.71 |
| sc_fire_spend | -0.21 |
| sc_police_spend | -0.26 |
| lg_sprite_cycle | -0.88 |
| lg_total_pop | -1.41 |
| lg_res_hist0 | -0.23 |
| lg_res_hist1 | -0.42 |
| lg_com_hist0 | -0.04 |
| lg_com_hist1 | -0.15 |
| lg_ind_hist0 | -0.04 |
| lg_ind_hist1 | -0.15 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.03 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.73 |
| lg_police_fund | -0.24 |
| lg_fire_fund | -0.42 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.01 |
| lg_pollution_max_x | -3.00 |
| lg_pollution_max_y | -2.98 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -4.35 |
| com_rate | -1.97 |
| kl | 15.93 |
| elbo | -2604.23 |
