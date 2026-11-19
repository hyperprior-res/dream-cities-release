## pilot6_censored_samples_000600064_dec-b

samples consumed: 600064; weights loaded: ema; decoding b (T=1.0, overlays mean)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "c0a3ceceb9a2a0bf", "split": "heldout_eval"}

**Appendix decoding (b): not a headline result.**

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.262 | 0.265 | 0.264 | 0.241 to 0.284 | 0.148 | 0.145 | 0.147 | 0.123 to 0.175 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.271 | 0.273 | 0.272 | 0.250 to 0.293 | 0.163 | 0.158 | 0.160 | 0.133 to 0.192 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.228 | 0.235 | 0.232 | 0.209 to 0.254 | 0.100 | 0.100 | 0.100 | 0.087 to 0.117 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.508 | 0.204 | 0.004 / 0.000 / 0.017 | 0.007 / 0.006 / 0.007 | 0.345 / 0.402 |
| all plans | 500 | 12 | 0.368 | 0.146 | 0.042 / 0.003 / 0.378 | 0.033 / 0.026 / 0.103 | 0.344 / 0.428 |
| all plans | 500 | 24 | 0.402 | 0.167 | 0.056 / 0.005 / 0.678 | 0.056 / 0.042 / 0.160 | 0.317 / 0.408 |
| state-reading plans | 394 | 1 | 0.506 | 0.208 | 0.004 / 0.000 / 0.018 | 0.007 / 0.006 / 0.007 | 0.382 / 0.436 |
| state-reading plans | 394 | 12 | 0.368 | 0.151 | 0.050 / 0.003 / 0.465 | 0.033 / 0.025 / 0.103 | 0.366 / 0.442 |
| state-reading plans | 394 | 24 | 0.414 | 0.184 | 0.070 / 0.005 / 0.791 | 0.056 / 0.044 / 0.150 | 0.332 / 0.412 |
| open-loop plans | 106 | 1 | 0.531 | 0.199 | 0.000 / 0.000 / 0.000 | 0.007 / 0.008 / 0.007 | 0.185 / 0.257 |
| open-loop plans | 106 | 12 | 0.497 | 0.131 | 0.013 / 0.002 / 0.061 | 0.033 / 0.031 / 0.103 | 0.260 / 0.372 |
| open-loop plans | 106 | 24 | 0.518 | 0.122 | 0.018 / 0.005 / 0.140 | 0.058 / 0.036 / 0.203 | 0.264 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1466 | 0.707 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2636 | 0.831 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1393.7150 | 0.880 |
| funds_mae_12m | 5714.0800 | 36.8760 | 964.5530 | 0.837 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 172.4503 | 0.880 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 455.6558 | 0.884 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 294.1375 | 0.946 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0334 | 0.903 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0415 | 0.896 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3444 | 0.805 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3406 | 0.793 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2419.6300 | 0.881 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1125.6343 | 0.855 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 229.2970 | 0.846 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 530.7787 | 0.956 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 474.3492 | 0.872 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0562 | 0.882 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0560 | 0.924 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3175 | 0.779 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3148 | 0.772 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1125.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 229.3 | 142.8 | 706.1 |
| com_valve | 530.8 | 508.6 | 1010.2 |
| ind_valve | 474.3 | 416.9 | 864.8 |
| pop | 2419.6 | 1754.6 | 7353.4 |
| res_pop | 57.3 | 39.0 | 139.9 |
| com_pop | 5.7 | 4.4 | 12.8 |
| ind_pop | 7.1 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 46.7 | 25.2 | 89.6 |
| tax_fund | 132.6 | 51.5 | 1444.5 |
| road_spend | 81.6 | 8.2 | 647.3 |
| fire_spend | 34.3 | 0.8 | 474.7 |
| police_spend | 57.1 | 6.0 | 604.1 |
| powered_zones | 4.8 | 0.7 | 8.6 |
| unpowered_zones | 4.4 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 46.9 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1011.8 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 220.5 | 130.7 | 533.4 |
| com_valve | 554.7 | 541.8 | 962.1 |
| ind_valve | 511.4 | 446.9 | 814.5 |
| pop | 2419.3 | 1810.1 | 6881.1 |
| res_pop | 57.4 | 39.6 | 131.0 |
| com_pop | 5.6 | 4.5 | 12.1 |
| ind_pop | 7.2 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 47.6 | 26.2 | 83.7 |
| tax_fund | 128.3 | 47.1 | 1400.1 |
| road_spend | 74.1 | 8.1 | 645.8 |
| fire_spend | 28.9 | 0.8 | 464.7 |
| police_spend | 55.1 | 6.4 | 591.3 |
| powered_zones | 5.7 | 0.9 | 10.7 |
| unpowered_zones | 4.7 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.4 |
| road_total | 46.8 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1548.8 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 261.9 | 187.8 | 1348.3 |
| com_valve | 441.7 | 385.4 | 1188.9 |
| ind_valve | 336.5 | 305.2 | 1051.7 |
| pop | 2420.9 | 1548.5 | 9108.7 |
| res_pop | 56.8 | 37.0 | 172.8 |
| com_pop | 6.2 | 4.2 | 15.7 |
| ind_pop | 6.6 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.2 | 21.3 | 111.7 |
| tax_fund | 148.6 | 68.0 | 1609.5 |
| road_spend | 109.8 | 8.8 | 653.2 |
| fire_spend | 54.4 | 1.1 | 512.0 |
| police_spend | 64.7 | 4.6 | 651.4 |
| powered_zones | 1.3 | 0.0 | 0.5 |
| unpowered_zones | 3.3 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 47.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 0.856 | 0.838 |
| traffic | 0.909 | 0.772 |
| pollution | 1.074 | 0.706 |
| land_value | 0.647 | 0.325 |
| crime | 0.869 | 0.566 |
| rate_of_growth | 0.746 | 0.819 |
| fire_coverage | 1.319 | 0.123 |
| police_coverage | 0.910 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.607 | 0.239 | 0.343 | 0.318 to 0.365 | 0.826 | 0.107 | 0.189 | 0.148 to 0.235 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.439 | 0.002 | 0.006 |
| all plans | 12 | 0.302 | 0.033 | 0.027 |
| all plans | 24 | 0.333 | 0.059 | 0.049 |
| state-reading plans | 1 | 0.443 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.300 | 0.038 | 0.028 |
| state-reading plans | 24 | 0.343 | 0.074 | 0.048 |
| open-loop plans | 1 | 0.447 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.385 | 0.011 | 0.026 |
| open-loop plans | 24 | 0.384 | 0.015 | 0.055 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -259.55 |
| tile_cat | -40.57 |
| flags | -20.60 |
| power | -5.57 |
| half | -2950.08 |
| eighth | -44.72 |
| scalars_s2 | -5.94 |
| build_cost | -1.17 |
| scalars | -12.74 |
| ledger | -12.90 |
| bk | -19.71 |
| sc_res_pop | -1.81 |
| sc_com_pop | -0.21 |
| sc_ind_pop | -0.29 |
| sc_powered_zones | -0.08 |
| sc_unpowered_zones | -0.08 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.43 |
| sc_res_valve | -0.95 |
| sc_com_valve | -1.94 |
| sc_ind_valve | -1.21 |
| sc_score | -0.44 |
| sc_funds | -0.94 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.47 |
| sc_fire_spend | -0.20 |
| sc_police_spend | -0.19 |
| lg_sprite_cycle | -0.73 |
| lg_total_pop | -1.55 |
| lg_res_hist0 | -0.36 |
| lg_res_hist1 | -0.27 |
| lg_com_hist0 | -0.05 |
| lg_com_hist1 | -0.19 |
| lg_ind_hist0 | -0.06 |
| lg_ind_hist1 | -0.29 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.60 |
| lg_police_fund | -0.16 |
| lg_fire_fund | -0.19 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.10 |
| lg_city_center_y | -0.10 |
| lg_pollution_max_x | -2.92 |
| lg_pollution_max_y | -2.84 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -9.19 |
| com_rate | -11.82 |
| kl | 3.81 |
| elbo | -3372.74 |

## pilot6_censored_samples_000600064_dec-c

samples consumed: 600064; weights loaded: ema; decoding c (T=0.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "c0a3ceceb9a2a0bf", "split": "heldout_eval"}

**Appendix decoding (c): not a headline result.**

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.262 | 0.265 | 0.264 | 0.241 to 0.284 | 0.148 | 0.145 | 0.147 | 0.123 to 0.175 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.271 | 0.273 | 0.272 | 0.250 to 0.293 | 0.163 | 0.158 | 0.160 | 0.133 to 0.192 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.228 | 0.235 | 0.232 | 0.209 to 0.254 | 0.100 | 0.100 | 0.100 | 0.087 to 0.117 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.426 | 0.204 | 0.001 / 0.000 / 0.017 | 0.006 / 0.006 / 0.007 | 0.494 / 0.402 |
| all plans | 500 | 12 | 0.464 | 0.146 | 0.016 / 0.003 / 0.378 | 0.106 / 0.026 / 0.103 | 0.385 / 0.428 |
| all plans | 500 | 24 | 0.571 | 0.167 | 0.036 / 0.005 / 0.678 | 0.161 / 0.042 / 0.160 | 0.336 / 0.408 |
| state-reading plans | 394 | 1 | 0.467 | 0.208 | 0.001 / 0.000 / 0.018 | 0.006 / 0.006 / 0.007 | 0.535 / 0.436 |
| state-reading plans | 394 | 12 | 0.459 | 0.151 | 0.017 / 0.003 / 0.465 | 0.107 / 0.025 / 0.103 | 0.425 / 0.442 |
| state-reading plans | 394 | 24 | 0.584 | 0.184 | 0.038 / 0.005 / 0.791 | 0.151 / 0.044 / 0.150 | 0.372 / 0.412 |
| open-loop plans | 106 | 1 | 0.405 | 0.199 | 0.000 / 0.000 / 0.000 | 0.006 / 0.008 / 0.007 | 0.292 / 0.257 |
| open-loop plans | 106 | 12 | 0.571 | 0.131 | 0.013 / 0.002 / 0.061 | 0.105 / 0.031 / 0.103 | 0.211 / 0.372 |
| open-loop plans | 106 | 24 | 0.631 | 0.122 | 0.027 / 0.005 / 0.140 | 0.197 / 0.036 / 0.203 | 0.188 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1466 | 0.707 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2636 | 0.831 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 4004.5500 | 0.012 |
| funds_mae_12m | 5714.0800 | 36.8760 | 732.3900 | 0.877 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 316.8080 | 0.607 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 792.5220 | 0.490 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 501.3660 | 0.632 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.1064 | -0.040 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0156 | 0.965 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3850 | 0.900 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3691 | 0.859 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 7284.1550 | 0.012 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1073.9977 | 0.862 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 375.4980 | 0.587 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 1201.5840 | -0.382 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 1035.1200 | -0.380 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1610 | -0.011 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0361 | 0.953 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3360 | 0.825 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3272 | 0.802 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1074.0 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 375.5 | 142.8 | 706.1 |
| com_valve | 1201.6 | 508.6 | 1010.2 |
| ind_valve | 1035.1 | 416.9 | 864.8 |
| pop | 7284.2 | 1754.6 | 7353.4 |
| res_pop | 136.6 | 39.0 | 139.9 |
| com_pop | 12.9 | 4.4 | 12.8 |
| ind_pop | 19.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 46.3 | 25.2 | 89.6 |
| tax_fund | 224.7 | 51.5 | 1444.5 |
| road_spend | 72.6 | 8.2 | 647.3 |
| fire_spend | 23.4 | 0.8 | 474.7 |
| police_spend | 42.5 | 6.0 | 604.1 |
| powered_zones | 3.2 | 0.7 | 8.6 |
| unpowered_zones | 3.6 | 0.6 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 72.1 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 703.4 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 331.2 | 130.7 | 533.4 |
| com_valve | 1276.0 | 541.8 | 962.1 |
| ind_valve | 1129.3 | 446.9 | 814.5 |
| pop | 6833.1 | 1810.1 | 6881.1 |
| res_pop | 128.4 | 39.6 | 131.0 |
| com_pop | 12.2 | 4.5 | 12.1 |
| ind_pop | 19.0 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 48.6 | 26.2 | 83.7 |
| tax_fund | 204.4 | 47.1 | 1400.1 |
| road_spend | 67.4 | 8.1 | 645.8 |
| fire_spend | 21.3 | 0.8 | 464.7 |
| police_spend | 41.9 | 6.4 | 591.3 |
| powered_zones | 3.9 | 0.9 | 10.7 |
| unpowered_zones | 3.7 | 0.8 | 7.0 |
| coal_plants | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.1 | 0.0 | 0.4 |
| road_total | 72.8 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 2451.5 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 540.0 | 187.8 | 1348.3 |
| com_valve | 925.0 | 385.4 | 1188.9 |
| ind_valve | 685.2 | 305.2 | 1051.7 |
| pop | 8960.6 | 1548.5 | 9108.7 |
| res_pop | 167.2 | 37.0 | 172.8 |
| com_pop | 15.6 | 4.2 | 15.7 |
| ind_pop | 22.2 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 37.5 | 21.3 | 111.7 |
| tax_fund | 300.1 | 68.0 | 1609.5 |
| road_spend | 92.0 | 8.8 | 653.2 |
| fire_spend | 31.5 | 1.1 | 512.0 |
| police_spend | 45.0 | 4.6 | 651.4 |
| powered_zones | 0.5 | 0.0 | 0.5 |
| unpowered_zones | 3.0 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 69.3 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.043 | 0.838 |
| traffic | 0.948 | 0.772 |
| pollution | 1.646 | 0.706 |
| land_value | 0.707 | 0.325 |
| crime | 0.927 | 0.566 |
| rate_of_growth | 1.027 | 0.819 |
| fire_coverage | 0.982 | 0.123 |
| police_coverage | 0.820 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.607 | 0.239 | 0.343 | 0.318 to 0.365 | 0.826 | 0.107 | 0.189 | 0.148 to 0.235 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.426 | 0.001 | 0.006 |
| all plans | 12 | 0.464 | 0.016 | 0.106 |
| all plans | 24 | 0.571 | 0.036 | 0.161 |
| state-reading plans | 1 | 0.467 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.459 | 0.017 | 0.107 |
| state-reading plans | 24 | 0.584 | 0.038 | 0.151 |
| open-loop plans | 1 | 0.405 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.571 | 0.013 | 0.105 |
| open-loop plans | 24 | 0.631 | 0.027 | 0.197 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -259.55 |
| tile_cat | -40.57 |
| flags | -20.60 |
| power | -5.57 |
| half | -2950.08 |
| eighth | -44.72 |
| scalars_s2 | -5.94 |
| build_cost | -1.17 |
| scalars | -12.74 |
| ledger | -12.90 |
| bk | -19.71 |
| sc_res_pop | -1.81 |
| sc_com_pop | -0.21 |
| sc_ind_pop | -0.29 |
| sc_powered_zones | -0.08 |
| sc_unpowered_zones | -0.08 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.43 |
| sc_res_valve | -0.95 |
| sc_com_valve | -1.94 |
| sc_ind_valve | -1.21 |
| sc_score | -0.44 |
| sc_funds | -0.94 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.47 |
| sc_fire_spend | -0.20 |
| sc_police_spend | -0.19 |
| lg_sprite_cycle | -0.73 |
| lg_total_pop | -1.55 |
| lg_res_hist0 | -0.36 |
| lg_res_hist1 | -0.27 |
| lg_com_hist0 | -0.05 |
| lg_com_hist1 | -0.19 |
| lg_ind_hist0 | -0.06 |
| lg_ind_hist1 | -0.29 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.60 |
| lg_police_fund | -0.16 |
| lg_fire_fund | -0.19 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.10 |
| lg_city_center_y | -0.10 |
| lg_pollution_max_x | -2.92 |
| lg_pollution_max_y | -2.84 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -9.19 |
| com_rate | -11.82 |
| kl | 3.81 |
| elbo | -3372.74 |
