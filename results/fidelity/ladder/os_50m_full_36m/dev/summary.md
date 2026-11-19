## os_50m_full_36m_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "3eed58d3b821a96c", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.300 | 0.282 | 0.291 | 0.270 to 0.310 | 0.194 | 0.171 | 0.182 | 0.154 to 0.213 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.141 | 0.050 | 0.052 | 0.051 | 0.046 to 0.056 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.307 | 0.290 | 0.298 | 0.277 to 0.317 | 0.208 | 0.184 | 0.195 | 0.164 to 0.230 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.133 | 0.134 | 0.123 to 0.145 | 0.054 | 0.055 | 0.054 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.272 | 0.254 | 0.263 | 0.240 to 0.285 | 0.146 | 0.127 | 0.136 | 0.116 to 0.160 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.113 | 0.118 | 0.116 | 0.102 to 0.129 | 0.038 | 0.042 | 0.040 | 0.035 to 0.045 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.904 | 0.204 | 0.011 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.399 / 0.402 |
| all plans | 500 | 12 | 0.632 | 0.146 | 0.070 / 0.003 / 0.378 | 0.048 / 0.026 / 0.103 | 0.387 / 0.428 |
| all plans | 500 | 24 | 0.665 | 0.167 | 0.087 / 0.005 / 0.678 | 0.068 / 0.042 / 0.160 | 0.356 / 0.408 |
| state-reading plans | 394 | 1 | 0.862 | 0.208 | 0.014 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.434 / 0.436 |
| state-reading plans | 394 | 12 | 0.631 | 0.151 | 0.085 / 0.003 / 0.465 | 0.047 / 0.025 / 0.103 | 0.407 / 0.442 |
| state-reading plans | 394 | 24 | 0.679 | 0.184 | 0.112 / 0.005 / 0.791 | 0.065 / 0.044 / 0.150 | 0.368 / 0.412 |
| open-loop plans | 106 | 1 | 1.152 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.242 / 0.257 |
| open-loop plans | 106 | 12 | 1.023 | 0.131 | 0.018 / 0.002 / 0.061 | 0.053 / 0.031 / 0.103 | 0.310 / 0.372 |
| open-loop plans | 106 | 24 | 1.162 | 0.122 | 0.020 / 0.005 / 0.140 | 0.081 / 0.036 / 0.203 | 0.309 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1821 | 0.878 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2906 | 0.916 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2056.4100 | 0.660 |
| funds_mae_12m | 5714.0800 | 36.8760 | 898.8083 | 0.848 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 222.6735 | 0.785 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 543.3107 | 0.782 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 350.1742 | 0.861 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0484 | 0.710 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0703 | 0.820 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3871 | 0.905 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3810 | 0.887 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3223.2750 | 0.738 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1036.0048 | 0.867 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 304.6282 | 0.713 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 774.1458 | 0.471 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 644.5725 | 0.492 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0676 | 0.785 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0867 | 0.878 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3557 | 0.873 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3510 | 0.861 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1036.0 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 304.6 | 142.8 | 706.1 |
| com_valve | 774.1 | 508.6 | 1010.2 |
| ind_valve | 644.6 | 416.9 | 864.8 |
| pop | 3223.3 | 1754.6 | 7353.4 |
| res_pop | 69.1 | 39.0 | 139.9 |
| com_pop | 8.8 | 4.4 | 12.8 |
| ind_pop | 10.4 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.9 | 25.2 | 89.6 |
| tax_fund | 148.4 | 51.5 | 1444.5 |
| road_spend | 84.8 | 8.2 | 647.3 |
| fire_spend | 40.9 | 0.8 | 474.7 |
| police_spend | 74.5 | 6.0 | 604.1 |
| powered_zones | 10.4 | 0.7 | 8.6 |
| unpowered_zones | 5.7 | 0.6 | 7.0 |
| coal_plants | 0.7 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.3 |
| road_total | 58.0 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1103.8 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 288.2 | 130.7 | 533.4 |
| com_valve | 824.5 | 541.8 | 962.1 |
| ind_valve | 692.6 | 446.9 | 814.5 |
| pop | 3117.7 | 1810.1 | 6881.1 |
| res_pop | 67.1 | 39.6 | 131.0 |
| com_pop | 8.3 | 4.5 | 12.1 |
| ind_pop | 10.4 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 52.1 | 26.2 | 83.7 |
| tax_fund | 135.4 | 47.1 | 1400.1 |
| road_spend | 81.3 | 8.1 | 645.8 |
| fire_spend | 38.7 | 0.8 | 464.7 |
| police_spend | 70.8 | 6.4 | 591.3 |
| powered_zones | 11.8 | 0.9 | 10.7 |
| unpowered_zones | 6.1 | 0.8 | 7.0 |
| coal_plants | 0.8 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.4 |
| road_total | 58.8 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 784.0 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 365.6 | 187.8 | 1348.3 |
| com_valve | 586.8 | 385.4 | 1188.9 |
| ind_valve | 466.1 | 305.2 | 1051.7 |
| pop | 3615.6 | 1548.5 | 9108.7 |
| res_pop | 76.5 | 37.0 | 172.8 |
| com_pop | 10.7 | 4.2 | 15.7 |
| ind_pop | 10.3 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 41.8 | 21.3 | 111.7 |
| tax_fund | 196.6 | 68.0 | 1609.5 |
| road_spend | 97.7 | 8.8 | 653.2 |
| fire_spend | 49.1 | 1.1 | 512.0 |
| police_spend | 88.0 | 4.6 | 651.4 |
| powered_zones | 5.4 | 0.0 | 0.5 |
| unpowered_zones | 4.2 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.5 | 0.0 | 0.2 |
| road_total | 55.3 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.008 | 0.838 |
| traffic | 0.965 | 0.772 |
| pollution | 1.439 | 0.706 |
| land_value | 0.586 | 0.325 |
| crime | 0.929 | 0.566 |
| rate_of_growth | 0.994 | 0.819 |
| fire_coverage | 0.938 | 0.123 |
| police_coverage | 0.797 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.570 | 0.256 | 0.353 | 0.330 to 0.373 | 0.496 | 0.137 | 0.215 | 0.175 to 0.255 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.572 | 0.005 | 0.006 |
| all plans | 12 | 0.395 | 0.044 | 0.041 |
| all plans | 24 | 0.438 | 0.073 | 0.056 |
| state-reading plans | 1 | 0.613 | 0.006 | 0.006 |
| state-reading plans | 12 | 0.395 | 0.053 | 0.039 |
| state-reading plans | 24 | 0.455 | 0.098 | 0.054 |
| open-loop plans | 1 | 0.580 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.593 | 0.015 | 0.047 |
| open-loop plans | 24 | 0.623 | 0.025 | 0.065 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -208.80 |
| tile_cat | -30.56 |
| flags | -14.69 |
| power | -3.18 |
| half | -2353.13 |
| eighth | -34.12 |
| scalars_s2 | -7.62 |
| build_cost | -1.51 |
| scalars | -14.77 |
| ledger | -13.12 |
| bk | -20.27 |
| sc_res_pop | -2.38 |
| sc_com_pop | -0.55 |
| sc_ind_pop | -0.62 |
| sc_powered_zones | -0.21 |
| sc_unpowered_zones | -0.29 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.50 |
| sc_res_valve | -0.95 |
| sc_com_valve | -1.97 |
| sc_ind_valve | -1.43 |
| sc_score | -0.41 |
| sc_funds | -1.01 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.57 |
| sc_fire_spend | -0.20 |
| sc_police_spend | -0.17 |
| lg_sprite_cycle | -0.77 |
| lg_total_pop | -1.42 |
| lg_res_hist0 | -0.41 |
| lg_res_hist1 | -0.32 |
| lg_com_hist0 | -0.08 |
| lg_com_hist1 | -0.08 |
| lg_ind_hist0 | -0.13 |
| lg_ind_hist1 | -0.25 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.04 |
| lg_road_fund | -0.61 |
| lg_police_fund | -0.16 |
| lg_fire_fund | -0.17 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.01 |
| lg_pollution_max_y | -3.14 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.35 |
| terrain | -4.61 |
| com_rate | -3.08 |
| kl | 13.51 |
| elbo | -2695.07 |

## os_50m_full_36m_samples_012000000_dec-a

samples consumed: 12000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "3eed58d3b821a96c", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.301 | 0.288 | 0.294 | 0.274 to 0.313 | 0.191 | 0.172 | 0.181 | 0.154 to 0.211 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.141 | 0.050 | 0.052 | 0.051 | 0.046 to 0.056 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.309 | 0.295 | 0.302 | 0.281 to 0.321 | 0.205 | 0.184 | 0.194 | 0.162 to 0.228 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.133 | 0.134 | 0.123 to 0.145 | 0.054 | 0.055 | 0.054 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.273 | 0.261 | 0.267 | 0.245 to 0.288 | 0.144 | 0.130 | 0.137 | 0.119 to 0.158 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.113 | 0.118 | 0.116 | 0.102 to 0.129 | 0.038 | 0.042 | 0.040 | 0.035 to 0.045 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.892 | 0.204 | 0.010 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.397 / 0.402 |
| all plans | 500 | 12 | 0.624 | 0.146 | 0.062 / 0.003 / 0.378 | 0.050 / 0.026 / 0.103 | 0.383 / 0.428 |
| all plans | 500 | 24 | 0.687 | 0.167 | 0.077 / 0.005 / 0.678 | 0.072 / 0.042 / 0.160 | 0.350 / 0.408 |
| state-reading plans | 394 | 1 | 0.909 | 0.208 | 0.013 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.431 / 0.436 |
| state-reading plans | 394 | 12 | 0.627 | 0.151 | 0.074 / 0.003 / 0.465 | 0.051 / 0.025 / 0.103 | 0.401 / 0.442 |
| state-reading plans | 394 | 24 | 0.701 | 0.184 | 0.093 / 0.005 / 0.791 | 0.068 / 0.044 / 0.150 | 0.361 / 0.412 |
| open-loop plans | 106 | 1 | 1.073 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.244 / 0.257 |
| open-loop plans | 106 | 12 | 1.182 | 0.131 | 0.017 / 0.002 / 0.061 | 0.049 / 0.031 / 0.103 | 0.312 / 0.372 |
| open-loop plans | 106 | 24 | 1.512 | 0.122 | 0.019 / 0.005 / 0.140 | 0.087 / 0.036 / 0.203 | 0.309 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1811 | 0.873 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2945 | 0.929 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2138.6600 | 0.632 |
| funds_mae_12m | 5714.0800 | 36.8760 | 826.8507 | 0.861 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 228.4123 | 0.774 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 539.4040 | 0.786 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 344.5105 | 0.869 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0502 | 0.686 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0622 | 0.842 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3830 | 0.896 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3774 | 0.878 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3532.7750 | 0.682 |
| funds_mae_24m | 7364.5720 | 66.5620 | 959.3350 | 0.878 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 327.9388 | 0.671 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 736.8463 | 0.545 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 625.5327 | 0.534 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0717 | 0.751 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0765 | 0.893 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3500 | 0.859 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3456 | 0.847 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 959.3 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 327.9 | 142.8 | 706.1 |
| com_valve | 736.8 | 508.6 | 1010.2 |
| ind_valve | 625.5 | 416.9 | 864.8 |
| pop | 3532.8 | 1754.6 | 7353.4 |
| res_pop | 76.2 | 39.0 | 139.9 |
| com_pop | 9.3 | 4.4 | 12.8 |
| ind_pop | 11.3 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 63.3 | 25.2 | 89.6 |
| tax_fund | 156.4 | 51.5 | 1444.5 |
| road_spend | 85.6 | 8.2 | 647.3 |
| fire_spend | 44.9 | 0.8 | 474.7 |
| police_spend | 76.2 | 6.0 | 604.1 |
| powered_zones | 12.0 | 0.7 | 8.6 |
| unpowered_zones | 5.8 | 0.6 | 7.0 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.3 |
| road_total | 55.7 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1012.1 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 307.4 | 130.7 | 533.4 |
| com_valve | 783.1 | 541.8 | 962.1 |
| ind_valve | 682.6 | 446.9 | 814.5 |
| pop | 3450.4 | 1810.1 | 6881.1 |
| res_pop | 75.7 | 39.6 | 131.0 |
| com_pop | 8.8 | 4.5 | 12.1 |
| ind_pop | 11.2 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 66.6 | 26.2 | 83.7 |
| tax_fund | 144.9 | 47.1 | 1400.1 |
| road_spend | 80.5 | 8.1 | 645.8 |
| fire_spend | 42.0 | 0.8 | 464.7 |
| police_spend | 72.8 | 6.4 | 591.3 |
| powered_zones | 12.9 | 0.9 | 10.7 |
| unpowered_zones | 6.2 | 0.8 | 7.0 |
| coal_plants | 0.7 | 0.0 | 0.5 |
| nuclear_plants | 1.0 | 0.0 | 0.4 |
| road_total | 56.5 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 763.1 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 404.3 | 187.8 | 1348.3 |
| com_valve | 564.9 | 385.4 | 1188.9 |
| ind_valve | 413.4 | 305.2 | 1051.7 |
| pop | 3839.1 | 1548.5 | 9108.7 |
| res_pop | 78.1 | 37.0 | 172.8 |
| com_pop | 11.2 | 4.2 | 15.7 |
| ind_pop | 11.3 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 51.4 | 21.3 | 111.7 |
| tax_fund | 199.3 | 68.0 | 1609.5 |
| road_spend | 104.6 | 8.8 | 653.2 |
| fire_spend | 55.6 | 1.1 | 512.0 |
| police_spend | 88.8 | 4.6 | 651.4 |
| powered_zones | 8.8 | 0.0 | 0.5 |
| unpowered_zones | 4.2 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.6 | 0.0 | 0.2 |
| road_total | 52.5 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.055 | 0.838 |
| traffic | 0.948 | 0.772 |
| pollution | 1.422 | 0.706 |
| land_value | 0.590 | 0.325 |
| crime | 0.955 | 0.566 |
| rate_of_growth | 1.016 | 0.819 |
| fire_coverage | 0.974 | 0.123 |
| police_coverage | 0.866 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.546 | 0.264 | 0.355 | 0.333 to 0.376 | 0.438 | 0.137 | 0.209 | 0.171 to 0.250 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.576 | 0.005 | 0.005 |
| all plans | 12 | 0.393 | 0.043 | 0.042 |
| all plans | 24 | 0.454 | 0.072 | 0.057 |
| state-reading plans | 1 | 0.607 | 0.006 | 0.006 |
| state-reading plans | 12 | 0.398 | 0.049 | 0.043 |
| state-reading plans | 24 | 0.472 | 0.089 | 0.055 |
| open-loop plans | 1 | 0.634 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.629 | 0.011 | 0.040 |
| open-loop plans | 24 | 0.813 | 0.020 | 0.071 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -202.79 |
| tile_cat | -29.65 |
| flags | -14.14 |
| power | -2.78 |
| half | -2319.11 |
| eighth | -32.52 |
| scalars_s2 | -7.18 |
| build_cost | -1.46 |
| scalars | -14.96 |
| ledger | -14.32 |
| bk | -22.10 |
| sc_res_pop | -2.23 |
| sc_com_pop | -0.45 |
| sc_ind_pop | -0.52 |
| sc_powered_zones | -0.19 |
| sc_unpowered_zones | -0.26 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.47 |
| sc_res_valve | -1.03 |
| sc_com_valve | -2.06 |
| sc_ind_valve | -1.75 |
| sc_score | -0.38 |
| sc_funds | -1.12 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.59 |
| sc_fire_spend | -0.22 |
| sc_police_spend | -0.17 |
| lg_sprite_cycle | -0.97 |
| lg_total_pop | -1.47 |
| lg_res_hist0 | -0.65 |
| lg_res_hist1 | -0.54 |
| lg_com_hist0 | -0.16 |
| lg_com_hist1 | -0.18 |
| lg_ind_hist0 | -0.24 |
| lg_ind_hist1 | -0.31 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.02 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.04 |
| lg_road_fund | -0.67 |
| lg_police_fund | -0.17 |
| lg_fire_fund | -0.18 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.03 |
| lg_pollution_max_y | -3.17 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.35 |
| terrain | -3.97 |
| com_rate | -3.02 |
| kl | 14.78 |
| elbo | -2653.51 |

## os_50m_full_36m_samples_018000000_dec-a

samples consumed: 18000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "3eed58d3b821a96c", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.303 | 0.288 | 0.295 | 0.275 to 0.314 | 0.191 | 0.172 | 0.181 | 0.155 to 0.211 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.141 | 0.050 | 0.052 | 0.051 | 0.046 to 0.056 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.310 | 0.295 | 0.302 | 0.281 to 0.322 | 0.205 | 0.184 | 0.194 | 0.163 to 0.229 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.133 | 0.134 | 0.123 to 0.145 | 0.054 | 0.055 | 0.054 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.275 | 0.261 | 0.268 | 0.246 to 0.289 | 0.145 | 0.130 | 0.137 | 0.120 to 0.158 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.113 | 0.118 | 0.116 | 0.102 to 0.129 | 0.038 | 0.042 | 0.040 | 0.035 to 0.045 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.741 | 0.204 | 0.009 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.400 / 0.402 |
| all plans | 500 | 12 | 0.584 | 0.146 | 0.053 / 0.003 / 0.378 | 0.054 / 0.026 / 0.103 | 0.380 / 0.428 |
| all plans | 500 | 24 | 0.669 | 0.167 | 0.068 / 0.005 / 0.678 | 0.081 / 0.042 / 0.160 | 0.345 / 0.408 |
| state-reading plans | 394 | 1 | 0.737 | 0.208 | 0.011 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.435 / 0.436 |
| state-reading plans | 394 | 12 | 0.588 | 0.151 | 0.062 / 0.003 / 0.465 | 0.053 / 0.025 / 0.103 | 0.397 / 0.442 |
| state-reading plans | 394 | 24 | 0.690 | 0.184 | 0.084 / 0.005 / 0.791 | 0.079 / 0.044 / 0.150 | 0.355 / 0.412 |
| open-loop plans | 106 | 1 | 0.796 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.246 / 0.257 |
| open-loop plans | 106 | 12 | 1.100 | 0.131 | 0.014 / 0.002 / 0.061 | 0.055 / 0.031 / 0.103 | 0.311 / 0.372 |
| open-loop plans | 106 | 24 | 1.378 | 0.122 | 0.021 / 0.005 / 0.140 | 0.087 / 0.036 / 0.203 | 0.307 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1811 | 0.873 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2950 | 0.930 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2323.7400 | 0.571 |
| funds_mae_12m | 5714.0800 | 36.8760 | 722.4020 | 0.879 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 241.5325 | 0.749 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 520.4488 | 0.808 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 346.8628 | 0.866 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0540 | 0.637 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0532 | 0.865 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3797 | 0.888 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3740 | 0.870 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 4114.8100 | 0.578 |
| funds_mae_24m | 7364.5720 | 66.5620 | 880.6935 | 0.888 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 350.3750 | 0.632 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 736.8172 | 0.545 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 633.1815 | 0.517 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0807 | 0.674 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0680 | 0.906 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3452 | 0.847 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3405 | 0.835 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 880.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 350.4 | 142.8 | 706.1 |
| com_valve | 736.8 | 508.6 | 1010.2 |
| ind_valve | 633.2 | 416.9 | 864.8 |
| pop | 4114.8 | 1754.6 | 7353.4 |
| res_pop | 86.4 | 39.0 | 139.9 |
| com_pop | 9.5 | 4.4 | 12.8 |
| ind_pop | 12.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 70.7 | 25.2 | 89.6 |
| tax_fund | 153.0 | 51.5 | 1444.5 |
| road_spend | 93.2 | 8.2 | 647.3 |
| fire_spend | 46.2 | 0.8 | 474.7 |
| police_spend | 79.6 | 6.0 | 604.1 |
| powered_zones | 10.7 | 0.7 | 8.6 |
| unpowered_zones | 5.3 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.3 |
| road_total | 48.1 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 927.1 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 329.3 | 130.7 | 533.4 |
| com_valve | 773.2 | 541.8 | 962.1 |
| ind_valve | 679.4 | 446.9 | 814.5 |
| pop | 4083.3 | 1810.1 | 6881.1 |
| res_pop | 86.1 | 39.6 | 131.0 |
| com_pop | 9.0 | 4.5 | 12.1 |
| ind_pop | 13.0 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 74.4 | 26.2 | 83.7 |
| tax_fund | 142.3 | 47.1 | 1400.1 |
| road_spend | 91.6 | 8.1 | 645.8 |
| fire_spend | 43.2 | 0.8 | 464.7 |
| police_spend | 77.2 | 6.4 | 591.3 |
| powered_zones | 11.4 | 0.9 | 10.7 |
| unpowered_zones | 5.7 | 0.8 | 7.0 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.4 |
| road_total | 48.8 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 708.2 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 428.9 | 187.8 | 1348.3 |
| com_valve | 601.6 | 385.4 | 1188.9 |
| ind_valve | 461.5 | 305.2 | 1051.7 |
| pop | 4231.8 | 1548.5 | 9108.7 |
| res_pop | 87.6 | 37.0 | 172.8 |
| com_pop | 11.2 | 4.2 | 15.7 |
| ind_pop | 12.3 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 56.6 | 21.3 | 111.7 |
| tax_fund | 192.7 | 68.0 | 1609.5 |
| road_spend | 99.4 | 8.8 | 653.2 |
| fire_spend | 57.4 | 1.1 | 512.0 |
| police_spend | 88.2 | 4.6 | 651.4 |
| powered_zones | 8.0 | 0.0 | 0.5 |
| unpowered_zones | 3.6 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.5 | 0.0 | 0.2 |
| road_total | 45.5 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.090 | 0.838 |
| traffic | 0.953 | 0.772 |
| pollution | 1.411 | 0.706 |
| land_value | 0.592 | 0.325 |
| crime | 0.967 | 0.566 |
| rate_of_growth | 1.048 | 0.819 |
| fire_coverage | 1.238 | 0.123 |
| police_coverage | 0.856 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.530 | 0.266 | 0.354 | 0.331 to 0.374 | 0.410 | 0.139 | 0.208 | 0.169 to 0.248 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.472 | 0.004 | 0.006 |
| all plans | 12 | 0.378 | 0.035 | 0.044 |
| all plans | 24 | 0.462 | 0.062 | 0.067 |
| state-reading plans | 1 | 0.509 | 0.004 | 0.006 |
| state-reading plans | 12 | 0.383 | 0.039 | 0.044 |
| state-reading plans | 24 | 0.484 | 0.076 | 0.067 |
| open-loop plans | 1 | 0.454 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.602 | 0.014 | 0.044 |
| open-loop plans | 24 | 0.823 | 0.024 | 0.066 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -198.64 |
| tile_cat | -29.13 |
| flags | -14.33 |
| power | -2.94 |
| half | -2251.07 |
| eighth | -31.30 |
| scalars_s2 | -6.48 |
| build_cost | -1.39 |
| scalars | -14.20 |
| ledger | -14.79 |
| bk | -22.51 |
| sc_res_pop | -1.97 |
| sc_com_pop | -0.30 |
| sc_ind_pop | -0.35 |
| sc_powered_zones | -0.17 |
| sc_unpowered_zones | -0.22 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.42 |
| sc_res_valve | -1.01 |
| sc_com_valve | -1.96 |
| sc_ind_valve | -1.40 |
| sc_score | -0.47 |
| sc_funds | -1.04 |
| sc_tax_fund | -0.51 |
| sc_road_spend | -0.81 |
| sc_fire_spend | -0.29 |
| sc_police_spend | -0.24 |
| lg_sprite_cycle | -1.72 |
| lg_total_pop | -1.38 |
| lg_res_hist0 | -0.36 |
| lg_res_hist1 | -0.32 |
| lg_com_hist0 | -0.05 |
| lg_com_hist1 | -0.07 |
| lg_ind_hist0 | -0.10 |
| lg_ind_hist1 | -0.25 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.02 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.04 |
| lg_road_fund | -0.90 |
| lg_police_fund | -0.21 |
| lg_fire_fund | -0.25 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.01 |
| lg_pollution_max_x | -3.18 |
| lg_pollution_max_y | -3.40 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.38 |
| terrain | -3.65 |
| com_rate | -2.65 |
| kl | 15.78 |
| elbo | -2579.86 |

## os_50m_full_36m_samples_024000000_dec-a

samples consumed: 24000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "3eed58d3b821a96c", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.303 | 0.285 | 0.294 | 0.273 to 0.313 | 0.191 | 0.172 | 0.181 | 0.154 to 0.211 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.141 | 0.050 | 0.052 | 0.051 | 0.046 to 0.056 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.309 | 0.292 | 0.301 | 0.279 to 0.320 | 0.202 | 0.183 | 0.192 | 0.162 to 0.227 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.133 | 0.134 | 0.123 to 0.145 | 0.054 | 0.055 | 0.054 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.279 | 0.257 | 0.267 | 0.244 to 0.290 | 0.152 | 0.132 | 0.141 | 0.122 to 0.165 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.113 | 0.118 | 0.116 | 0.102 to 0.129 | 0.038 | 0.042 | 0.040 | 0.035 to 0.045 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.720 | 0.204 | 0.007 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.402 / 0.402 |
| all plans | 500 | 12 | 0.520 | 0.146 | 0.046 / 0.003 / 0.378 | 0.057 / 0.026 / 0.103 | 0.377 / 0.428 |
| all plans | 500 | 24 | 0.654 | 0.167 | 0.060 / 0.005 / 0.678 | 0.099 / 0.042 / 0.160 | 0.337 / 0.408 |
| state-reading plans | 394 | 1 | 0.753 | 0.208 | 0.009 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.436 / 0.436 |
| state-reading plans | 394 | 12 | 0.526 | 0.151 | 0.052 / 0.003 / 0.465 | 0.057 / 0.025 / 0.103 | 0.394 / 0.442 |
| state-reading plans | 394 | 24 | 0.679 | 0.184 | 0.075 / 0.005 / 0.791 | 0.098 / 0.044 / 0.150 | 0.347 / 0.412 |
| open-loop plans | 106 | 1 | 0.772 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.249 / 0.257 |
| open-loop plans | 106 | 12 | 0.941 | 0.131 | 0.016 / 0.002 / 0.061 | 0.054 / 0.031 / 0.103 | 0.310 / 0.372 |
| open-loop plans | 106 | 24 | 1.312 | 0.122 | 0.020 / 0.005 / 0.140 | 0.105 / 0.036 / 0.203 | 0.301 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1809 | 0.872 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2938 | 0.926 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2527.6550 | 0.503 |
| funds_mae_12m | 5714.0800 | 36.8760 | 649.9260 | 0.892 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 245.2827 | 0.742 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 540.0855 | 0.785 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 360.7310 | 0.845 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0568 | 0.601 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0458 | 0.885 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3765 | 0.880 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3701 | 0.861 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5048.8650 | 0.412 |
| funds_mae_24m | 7364.5720 | 66.5620 | 804.9225 | 0.899 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 409.5253 | 0.527 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 735.7435 | 0.547 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 648.7717 | 0.482 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0987 | 0.520 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0601 | 0.918 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3372 | 0.827 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3322 | 0.815 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 804.9 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 409.5 | 142.8 | 706.1 |
| com_valve | 735.7 | 508.6 | 1010.2 |
| ind_valve | 648.8 | 416.9 | 864.8 |
| pop | 5048.9 | 1754.6 | 7353.4 |
| res_pop | 108.1 | 39.0 | 139.9 |
| com_pop | 10.5 | 4.4 | 12.8 |
| ind_pop | 14.4 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 100.4 | 25.2 | 89.6 |
| tax_fund | 181.8 | 51.5 | 1444.5 |
| road_spend | 101.6 | 8.2 | 647.3 |
| fire_spend | 46.2 | 0.8 | 474.7 |
| police_spend | 77.3 | 6.0 | 604.1 |
| powered_zones | 9.7 | 0.7 | 8.6 |
| unpowered_zones | 4.9 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 37.5 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 829.5 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 392.7 | 130.7 | 533.4 |
| com_valve | 766.6 | 541.8 | 962.1 |
| ind_valve | 686.6 | 446.9 | 814.5 |
| pop | 5050.0 | 1810.1 | 6881.1 |
| res_pop | 106.9 | 39.6 | 131.0 |
| com_pop | 10.2 | 4.5 | 12.1 |
| ind_pop | 14.6 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 104.7 | 26.2 | 83.7 |
| tax_fund | 172.8 | 47.1 | 1400.1 |
| road_spend | 94.3 | 8.1 | 645.8 |
| fire_spend | 42.6 | 0.8 | 464.7 |
| police_spend | 72.5 | 6.4 | 591.3 |
| powered_zones | 10.3 | 0.9 | 10.7 |
| unpowered_zones | 5.3 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 38.4 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 713.4 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 472.2 | 187.8 | 1348.3 |
| com_valve | 621.2 | 385.4 | 1188.9 |
| ind_valve | 508.1 | 305.2 | 1051.7 |
| pop | 5044.7 | 1548.5 | 9108.7 |
| res_pop | 112.5 | 37.0 | 172.8 |
| com_pop | 12.0 | 4.2 | 15.7 |
| ind_pop | 13.6 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 84.5 | 21.3 | 111.7 |
| tax_fund | 215.3 | 68.0 | 1609.5 |
| road_spend | 128.9 | 8.8 | 653.2 |
| fire_spend | 59.6 | 1.1 | 512.0 |
| police_spend | 95.0 | 4.6 | 651.4 |
| powered_zones | 7.6 | 0.0 | 0.5 |
| unpowered_zones | 3.1 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 33.9 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.127 | 0.838 |
| traffic | 0.965 | 0.772 |
| pollution | 1.444 | 0.706 |
| land_value | 0.626 | 0.325 |
| crime | 0.997 | 0.566 |
| rate_of_growth | 1.074 | 0.819 |
| fire_coverage | 1.236 | 0.123 |
| police_coverage | 0.959 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.518 | 0.261 | 0.348 | 0.326 to 0.368 | 0.390 | 0.140 | 0.206 | 0.169 to 0.247 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.509 | 0.003 | 0.005 |
| all plans | 12 | 0.359 | 0.034 | 0.044 |
| all plans | 24 | 0.483 | 0.060 | 0.092 |
| state-reading plans | 1 | 0.540 | 0.003 | 0.005 |
| state-reading plans | 12 | 0.363 | 0.039 | 0.045 |
| state-reading plans | 24 | 0.505 | 0.071 | 0.091 |
| open-loop plans | 1 | 0.516 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.582 | 0.016 | 0.044 |
| open-loop plans | 24 | 0.908 | 0.016 | 0.099 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -192.12 |
| tile_cat | -28.36 |
| flags | -14.27 |
| power | -2.83 |
| half | -2161.30 |
| eighth | -30.08 |
| scalars_s2 | -5.73 |
| build_cost | -1.27 |
| scalars | -13.98 |
| ledger | -16.18 |
| bk | -24.43 |
| sc_res_pop | -1.69 |
| sc_com_pop | -0.17 |
| sc_ind_pop | -0.21 |
| sc_powered_zones | -0.13 |
| sc_unpowered_zones | -0.16 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.34 |
| sc_res_valve | -1.03 |
| sc_com_valve | -1.94 |
| sc_ind_valve | -1.10 |
| sc_score | -0.64 |
| sc_funds | -1.04 |
| sc_tax_fund | -0.66 |
| sc_road_spend | -1.15 |
| sc_fire_spend | -0.34 |
| sc_police_spend | -0.35 |
| lg_sprite_cycle | -2.45 |
| lg_total_pop | -1.32 |
| lg_res_hist0 | -0.21 |
| lg_res_hist1 | -0.35 |
| lg_com_hist0 | -0.03 |
| lg_com_hist1 | -0.10 |
| lg_ind_hist0 | -0.04 |
| lg_ind_hist1 | -0.38 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.06 |
| lg_need_church | -0.05 |
| lg_road_fund | -1.26 |
| lg_police_fund | -0.24 |
| lg_fire_fund | -0.29 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.01 |
| lg_pollution_max_x | -3.32 |
| lg_pollution_max_y | -3.54 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.41 |
| terrain | -3.33 |
| com_rate | -2.15 |
| kl | 18.15 |
| elbo | -2484.01 |

## os_50m_full_36m_samples_030000000_dec-a

samples consumed: 30000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "3eed58d3b821a96c", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.310 | 0.286 | 0.297 | 0.277 to 0.316 | 0.200 | 0.172 | 0.185 | 0.158 to 0.214 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.141 | 0.050 | 0.052 | 0.051 | 0.046 to 0.056 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.316 | 0.294 | 0.304 | 0.283 to 0.324 | 0.211 | 0.185 | 0.197 | 0.166 to 0.232 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.133 | 0.134 | 0.123 to 0.145 | 0.054 | 0.055 | 0.054 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.286 | 0.257 | 0.271 | 0.248 to 0.292 | 0.158 | 0.130 | 0.143 | 0.123 to 0.168 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.113 | 0.118 | 0.116 | 0.102 to 0.129 | 0.038 | 0.042 | 0.040 | 0.035 to 0.045 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.584 | 0.204 | 0.005 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.406 / 0.402 |
| all plans | 500 | 12 | 0.503 | 0.146 | 0.038 / 0.003 / 0.378 | 0.057 / 0.026 / 0.103 | 0.374 / 0.428 |
| all plans | 500 | 24 | 0.712 | 0.167 | 0.054 / 0.005 / 0.678 | 0.133 / 0.042 / 0.160 | 0.330 / 0.408 |
| state-reading plans | 394 | 1 | 0.645 | 0.208 | 0.006 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.441 / 0.436 |
| state-reading plans | 394 | 12 | 0.509 | 0.151 | 0.044 / 0.003 / 0.465 | 0.057 / 0.025 / 0.103 | 0.390 / 0.442 |
| state-reading plans | 394 | 24 | 0.745 | 0.184 | 0.062 / 0.005 / 0.791 | 0.135 / 0.044 / 0.150 | 0.338 / 0.412 |
| open-loop plans | 106 | 1 | 0.560 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.251 / 0.257 |
| open-loop plans | 106 | 12 | 0.851 | 0.131 | 0.019 / 0.002 / 0.061 | 0.060 / 0.031 / 0.103 | 0.308 / 0.372 |
| open-loop plans | 106 | 24 | 1.487 | 0.122 | 0.023 / 0.005 / 0.140 | 0.129 / 0.036 / 0.203 | 0.296 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1850 | 0.892 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2973 | 0.938 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2651.3850 | 0.462 |
| funds_mae_12m | 5714.0800 | 36.8760 | 582.7592 | 0.904 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 274.1225 | 0.687 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 573.3193 | 0.746 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 371.6740 | 0.828 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0574 | 0.594 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0378 | 0.906 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3736 | 0.873 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3659 | 0.851 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 6354.3500 | 0.178 |
| funds_mae_24m | 7364.5720 | 66.5620 | 777.3613 | 0.903 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 528.8027 | 0.315 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 726.1980 | 0.566 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 689.2192 | 0.392 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1332 | 0.226 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0538 | 0.927 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3296 | 0.809 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3236 | 0.794 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 777.4 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 528.8 | 142.8 | 706.1 |
| com_valve | 726.2 | 508.6 | 1010.2 |
| ind_valve | 689.2 | 416.9 | 864.8 |
| pop | 6354.4 | 1754.6 | 7353.4 |
| res_pop | 129.7 | 39.0 | 139.9 |
| com_pop | 11.6 | 4.4 | 12.8 |
| ind_pop | 17.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 124.6 | 25.2 | 89.6 |
| tax_fund | 187.0 | 51.5 | 1444.5 |
| road_spend | 97.3 | 8.2 | 647.3 |
| fire_spend | 53.8 | 0.8 | 474.7 |
| police_spend | 86.6 | 6.0 | 604.1 |
| powered_zones | 11.2 | 0.7 | 8.6 |
| unpowered_zones | 4.7 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 36.9 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 783.2 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 527.7 | 130.7 | 533.4 |
| com_valve | 735.0 | 541.8 | 962.1 |
| ind_valve | 721.8 | 446.9 | 814.5 |
| pop | 6536.8 | 1810.1 | 6881.1 |
| res_pop | 132.1 | 39.6 | 131.0 |
| com_pop | 11.6 | 4.5 | 12.1 |
| ind_pop | 18.1 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 130.8 | 26.2 | 83.7 |
| tax_fund | 180.4 | 47.1 | 1400.1 |
| road_spend | 92.5 | 8.1 | 645.8 |
| fire_spend | 47.0 | 0.8 | 464.7 |
| police_spend | 78.1 | 6.4 | 591.3 |
| powered_zones | 11.8 | 0.9 | 10.7 |
| unpowered_zones | 5.1 | 0.8 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 38.3 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 755.7 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 533.1 | 187.8 | 1348.3 |
| com_valve | 693.4 | 385.4 | 1188.9 |
| ind_valve | 567.9 | 305.2 | 1051.7 |
| pop | 5676.2 | 1548.5 | 9108.7 |
| res_pop | 120.8 | 37.0 | 172.8 |
| com_pop | 11.6 | 4.2 | 15.7 |
| ind_pop | 15.7 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 101.5 | 21.3 | 111.7 |
| tax_fund | 211.7 | 68.0 | 1609.5 |
| road_spend | 115.1 | 8.8 | 653.2 |
| fire_spend | 79.4 | 1.1 | 512.0 |
| police_spend | 118.1 | 4.6 | 651.4 |
| powered_zones | 9.0 | 0.0 | 0.5 |
| unpowered_zones | 3.1 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 31.8 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.139 | 0.838 |
| traffic | 0.990 | 0.772 |
| pollution | 1.463 | 0.706 |
| land_value | 0.648 | 0.325 |
| crime | 1.006 | 0.566 |
| rate_of_growth | 1.079 | 0.819 |
| fire_coverage | 1.522 | 0.123 |
| police_coverage | 0.989 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.514 | 0.265 | 0.350 | 0.327 to 0.370 | 0.392 | 0.142 | 0.208 | 0.172 to 0.248 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.428 | 0.002 | 0.006 |
| all plans | 12 | 0.375 | 0.025 | 0.044 |
| all plans | 24 | 0.575 | 0.052 | 0.131 |
| state-reading plans | 1 | 0.477 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.382 | 0.028 | 0.043 |
| state-reading plans | 24 | 0.604 | 0.057 | 0.129 |
| open-loop plans | 1 | 0.402 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.609 | 0.012 | 0.048 |
| open-loop plans | 24 | 1.289 | 0.033 | 0.133 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -188.62 |
| tile_cat | -27.99 |
| flags | -14.04 |
| power | -2.55 |
| half | -2121.74 |
| eighth | -29.01 |
| scalars_s2 | -5.05 |
| build_cost | -1.09 |
| scalars | -14.44 |
| ledger | -17.70 |
| bk | -27.10 |
| sc_res_pop | -1.43 |
| sc_com_pop | -0.10 |
| sc_ind_pop | -0.14 |
| sc_powered_zones | -0.06 |
| sc_unpowered_zones | -0.07 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.22 |
| sc_res_valve | -1.08 |
| sc_com_valve | -1.96 |
| sc_ind_valve | -1.06 |
| sc_score | -0.85 |
| sc_funds | -1.20 |
| sc_tax_fund | -0.81 |
| sc_road_spend | -1.56 |
| sc_fire_spend | -0.39 |
| sc_police_spend | -0.49 |
| lg_sprite_cycle | -2.58 |
| lg_total_pop | -1.33 |
| lg_res_hist0 | -0.18 |
| lg_res_hist1 | -0.69 |
| lg_com_hist0 | -0.04 |
| lg_com_hist1 | -0.18 |
| lg_ind_hist0 | -0.06 |
| lg_ind_hist1 | -0.50 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.08 |
| lg_need_church | -0.06 |
| lg_road_fund | -1.79 |
| lg_police_fund | -0.30 |
| lg_fire_fund | -0.36 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.39 |
| lg_pollution_max_y | -3.58 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.44 |
| terrain | -3.09 |
| com_rate | -2.27 |
| kl | 19.36 |
| elbo | -2441.91 |

## os_50m_full_36m_samples_036000000_dec-a

samples consumed: 36000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "3eed58d3b821a96c", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.318 | 0.285 | 0.300 | 0.279 to 0.318 | 0.207 | 0.167 | 0.185 | 0.158 to 0.216 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.141 | 0.050 | 0.052 | 0.051 | 0.046 to 0.056 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.327 | 0.292 | 0.308 | 0.287 to 0.328 | 0.223 | 0.180 | 0.199 | 0.168 to 0.234 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.133 | 0.134 | 0.123 to 0.145 | 0.054 | 0.055 | 0.054 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.286 | 0.257 | 0.271 | 0.246 to 0.293 | 0.153 | 0.124 | 0.137 | 0.117 to 0.162 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.113 | 0.118 | 0.116 | 0.102 to 0.129 | 0.038 | 0.042 | 0.040 | 0.035 to 0.045 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.580 | 0.204 | 0.004 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.411 / 0.402 |
| all plans | 500 | 12 | 0.513 | 0.146 | 0.034 / 0.003 / 0.378 | 0.062 / 0.026 / 0.103 | 0.371 / 0.428 |
| all plans | 500 | 24 | 0.759 | 0.167 | 0.047 / 0.005 / 0.678 | 0.169 / 0.042 / 0.160 | 0.326 / 0.408 |
| state-reading plans | 394 | 1 | 0.598 | 0.208 | 0.005 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.446 / 0.436 |
| state-reading plans | 394 | 12 | 0.518 | 0.151 | 0.037 / 0.003 / 0.465 | 0.063 / 0.025 / 0.103 | 0.388 / 0.442 |
| state-reading plans | 394 | 24 | 0.797 | 0.184 | 0.054 / 0.005 / 0.791 | 0.173 / 0.044 / 0.150 | 0.335 / 0.412 |
| open-loop plans | 106 | 1 | 0.572 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.257 / 0.257 |
| open-loop plans | 106 | 12 | 0.869 | 0.131 | 0.018 / 0.002 / 0.061 | 0.059 / 0.031 / 0.103 | 0.304 / 0.372 |
| open-loop plans | 106 | 24 | 1.607 | 0.122 | 0.021 / 0.005 / 0.140 | 0.152 / 0.036 / 0.203 | 0.291 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1850 | 0.892 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.3004 | 0.947 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 3032.2700 | 0.335 |
| funds_mae_12m | 5714.0800 | 36.8760 | 543.3668 | 0.911 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 285.3308 | 0.666 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 585.0030 | 0.733 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 384.4413 | 0.809 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0617 | 0.538 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0339 | 0.917 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3709 | 0.867 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3634 | 0.846 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 8014.3150 | -0.118 |
| funds_mae_24m | 7364.5720 | 66.5620 | 715.7342 | 0.911 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 587.2685 | 0.211 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 738.4953 | 0.542 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 736.4108 | 0.287 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1690 | -0.080 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0471 | 0.937 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3256 | 0.799 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3204 | 0.786 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 715.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 587.3 | 142.8 | 706.1 |
| com_valve | 738.5 | 508.6 | 1010.2 |
| ind_valve | 736.4 | 416.9 | 864.8 |
| pop | 8014.3 | 1754.6 | 7353.4 |
| res_pop | 164.5 | 39.0 | 139.9 |
| com_pop | 13.8 | 4.4 | 12.8 |
| ind_pop | 20.2 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 137.4 | 25.2 | 89.6 |
| tax_fund | 208.3 | 51.5 | 1444.5 |
| road_spend | 97.2 | 8.2 | 647.3 |
| fire_spend | 59.9 | 0.8 | 474.7 |
| police_spend | 93.0 | 6.0 | 604.1 |
| powered_zones | 11.5 | 0.7 | 8.6 |
| unpowered_zones | 4.1 | 0.6 | 7.0 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 39.6 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 707.6 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 600.3 | 130.7 | 533.4 |
| com_valve | 748.5 | 541.8 | 962.1 |
| ind_valve | 766.6 | 446.9 | 814.5 |
| pop | 8257.9 | 1810.1 | 6881.1 |
| res_pop | 168.1 | 39.6 | 131.0 |
| com_pop | 14.1 | 4.5 | 12.1 |
| ind_pop | 20.6 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 143.8 | 26.2 | 83.7 |
| tax_fund | 201.5 | 47.1 | 1400.1 |
| road_spend | 92.8 | 8.1 | 645.8 |
| fire_spend | 49.9 | 0.8 | 464.7 |
| police_spend | 78.3 | 6.4 | 591.3 |
| powered_zones | 12.0 | 0.9 | 10.7 |
| unpowered_zones | 4.5 | 0.8 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 41.0 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 745.8 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 538.8 | 187.8 | 1348.3 |
| com_valve | 701.4 | 385.4 | 1188.9 |
| ind_valve | 624.3 | 305.2 | 1051.7 |
| pop | 7109.0 | 1548.5 | 9108.7 |
| res_pop | 151.4 | 37.0 | 172.8 |
| com_pop | 12.6 | 4.2 | 15.7 |
| ind_pop | 18.6 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 113.5 | 21.3 | 111.7 |
| tax_fund | 233.7 | 68.0 | 1609.5 |
| road_spend | 113.6 | 8.8 | 653.2 |
| fire_spend | 97.2 | 1.1 | 512.0 |
| police_spend | 147.7 | 4.6 | 651.4 |
| powered_zones | 9.6 | 0.0 | 0.5 |
| unpowered_zones | 2.6 | 0.0 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 34.4 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.147 | 0.838 |
| traffic | 1.000 | 0.772 |
| pollution | 1.477 | 0.706 |
| land_value | 0.654 | 0.325 |
| crime | 1.007 | 0.566 |
| rate_of_growth | 1.084 | 0.819 |
| fire_coverage | 1.917 | 0.123 |
| police_coverage | 0.999 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.519 | 0.266 | 0.352 | 0.329 to 0.373 | 0.404 | 0.140 | 0.208 | 0.171 to 0.248 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.434 | 0.002 | 0.006 |
| all plans | 12 | 0.391 | 0.024 | 0.049 |
| all plans | 24 | 0.630 | 0.040 | 0.179 |
| state-reading plans | 1 | 0.445 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.398 | 0.026 | 0.048 |
| state-reading plans | 24 | 0.668 | 0.049 | 0.183 |
| open-loop plans | 1 | 0.419 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.661 | 0.012 | 0.050 |
| open-loop plans | 24 | 1.432 | 0.019 | 0.164 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -186.93 |
| tile_cat | -27.95 |
| flags | -14.11 |
| power | -2.63 |
| half | -2102.87 |
| eighth | -28.53 |
| scalars_s2 | -4.74 |
| build_cost | -0.93 |
| scalars | -15.39 |
| ledger | -19.64 |
| bk | -30.29 |
| sc_res_pop | -1.29 |
| sc_com_pop | -0.09 |
| sc_ind_pop | -0.13 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.17 |
| sc_res_valve | -1.11 |
| sc_com_valve | -1.96 |
| sc_ind_valve | -1.08 |
| sc_score | -1.09 |
| sc_funds | -1.41 |
| sc_tax_fund | -0.97 |
| sc_road_spend | -1.94 |
| sc_fire_spend | -0.47 |
| sc_police_spend | -0.61 |
| lg_sprite_cycle | -2.59 |
| lg_total_pop | -1.35 |
| lg_res_hist0 | -0.18 |
| lg_res_hist1 | -1.15 |
| lg_com_hist0 | -0.04 |
| lg_com_hist1 | -0.26 |
| lg_ind_hist0 | -0.07 |
| lg_ind_hist1 | -0.79 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.11 |
| lg_need_church | -0.06 |
| lg_road_fund | -2.56 |
| lg_police_fund | -0.39 |
| lg_fire_fund | -0.45 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.42 |
| lg_pollution_max_y | -3.61 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.47 |
| terrain | -3.01 |
| com_rate | -2.21 |
| kl | 20.30 |
| elbo | -2424.50 |
