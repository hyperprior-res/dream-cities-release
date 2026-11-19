## pilot6_censored_samples_000600064_dec-a_seed1

samples consumed: 600064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "c0a3ceceb9a2a0bf", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.262 | 0.264 | 0.263 | 0.241 to 0.283 | 0.148 | 0.145 | 0.146 | 0.122 to 0.173 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.271 | 0.273 | 0.272 | 0.249 to 0.293 | 0.162 | 0.159 | 0.160 | 0.132 to 0.192 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.228 | 0.231 | 0.229 | 0.207 to 0.252 | 0.098 | 0.097 | 0.098 | 0.085 to 0.112 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.514 | 0.204 | 0.004 / 0.000 / 0.017 | 0.007 / 0.006 / 0.007 | 0.346 / 0.402 |
| all plans | 500 | 12 | 0.370 | 0.146 | 0.040 / 0.003 / 0.378 | 0.031 / 0.026 / 0.103 | 0.343 / 0.428 |
| all plans | 500 | 24 | 0.409 | 0.167 | 0.058 / 0.005 / 0.678 | 0.057 / 0.042 / 0.160 | 0.317 / 0.408 |
| state-reading plans | 394 | 1 | 0.507 | 0.208 | 0.004 / 0.000 / 0.018 | 0.007 / 0.006 / 0.007 | 0.383 / 0.436 |
| state-reading plans | 394 | 12 | 0.369 | 0.151 | 0.047 / 0.003 / 0.465 | 0.031 / 0.025 / 0.103 | 0.365 / 0.442 |
| state-reading plans | 394 | 24 | 0.422 | 0.184 | 0.072 / 0.005 / 0.791 | 0.057 / 0.044 / 0.150 | 0.331 / 0.412 |
| open-loop plans | 106 | 1 | 0.539 | 0.199 | 0.000 / 0.000 / 0.000 | 0.007 / 0.008 / 0.007 | 0.187 / 0.257 |
| open-loop plans | 106 | 12 | 0.503 | 0.131 | 0.014 / 0.002 / 0.061 | 0.031 / 0.031 / 0.103 | 0.259 / 0.372 |
| open-loop plans | 106 | 24 | 0.525 | 0.122 | 0.017 / 0.005 / 0.140 | 0.058 / 0.036 / 0.203 | 0.263 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1462 | 0.705 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2631 | 0.830 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1342.2300 | 0.897 |
| funds_mae_12m | 5714.0800 | 36.8760 | 955.5010 | 0.838 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 177.9717 | 0.869 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 490.9995 | 0.843 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 302.2635 | 0.933 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0313 | 0.931 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0402 | 0.900 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3431 | 0.802 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3373 | 0.785 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2464.9650 | 0.873 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1140.6043 | 0.853 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 225.0445 | 0.854 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 577.7302 | 0.862 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 495.6848 | 0.824 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0570 | 0.875 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0576 | 0.921 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3165 | 0.777 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3122 | 0.766 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1140.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 225.0 | 142.8 | 706.1 |
| com_valve | 577.7 | 508.6 | 1010.2 |
| ind_valve | 495.7 | 416.9 | 864.8 |
| pop | 2465.0 | 1754.6 | 7353.4 |
| res_pop | 56.3 | 39.0 | 139.9 |
| com_pop | 5.9 | 4.4 | 12.8 |
| ind_pop | 7.4 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.5 | 25.2 | 89.6 |
| tax_fund | 125.1 | 51.5 | 1444.5 |
| road_spend | 85.0 | 8.2 | 647.3 |
| fire_spend | 33.9 | 0.8 | 474.7 |
| police_spend | 58.5 | 6.0 | 604.1 |
| powered_zones | 4.8 | 0.7 | 8.6 |
| unpowered_zones | 4.4 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 50.8 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1006.1 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 215.3 | 130.7 | 533.4 |
| com_valve | 607.3 | 541.8 | 962.1 |
| ind_valve | 537.8 | 446.9 | 814.5 |
| pop | 2458.0 | 1810.1 | 6881.1 |
| res_pop | 56.0 | 39.6 | 131.0 |
| com_pop | 5.8 | 4.5 | 12.1 |
| ind_pop | 7.3 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 45.5 | 26.2 | 83.7 |
| tax_fund | 120.1 | 47.1 | 1400.1 |
| road_spend | 79.6 | 8.1 | 645.8 |
| fire_spend | 28.0 | 0.8 | 464.7 |
| police_spend | 56.5 | 6.4 | 591.3 |
| powered_zones | 5.7 | 0.9 | 10.7 |
| unpowered_zones | 4.6 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.4 |
| road_total | 50.8 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1640.7 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 261.2 | 187.8 | 1348.3 |
| com_valve | 467.9 | 385.4 | 1188.9 |
| ind_valve | 339.3 | 305.2 | 1051.7 |
| pop | 2490.9 | 1548.5 | 9108.7 |
| res_pop | 57.7 | 37.0 | 172.8 |
| com_pop | 6.3 | 4.2 | 15.7 |
| ind_pop | 7.4 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 35.9 | 21.3 | 111.7 |
| tax_fund | 143.9 | 68.0 | 1609.5 |
| road_spend | 105.0 | 8.8 | 653.2 |
| fire_spend | 55.8 | 1.1 | 512.0 |
| police_spend | 65.6 | 4.6 | 651.4 |
| powered_zones | 1.4 | 0.0 | 0.5 |
| unpowered_zones | 3.3 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 50.9 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.100 | 0.838 |
| traffic | 1.196 | 0.772 |
| pollution | 1.668 | 0.706 |
| land_value | 0.831 | 0.325 |
| crime | 1.176 | 0.566 |
| rate_of_growth | 1.026 | 0.819 |
| fire_coverage | 1.407 | 0.123 |
| police_coverage | 0.984 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.607 | 0.239 | 0.343 | 0.318 to 0.365 | 0.826 | 0.107 | 0.189 | 0.148 to 0.235 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.451 | 0.002 | 0.005 |
| all plans | 12 | 0.301 | 0.030 | 0.029 |
| all plans | 24 | 0.338 | 0.064 | 0.052 |
| state-reading plans | 1 | 0.448 | 0.002 | 0.005 |
| state-reading plans | 12 | 0.299 | 0.039 | 0.029 |
| state-reading plans | 24 | 0.349 | 0.077 | 0.052 |
| open-loop plans | 1 | 0.443 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.391 | 0.009 | 0.025 |
| open-loop plans | 24 | 0.400 | 0.018 | 0.052 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -259.52 |
| tile_cat | -40.47 |
| flags | -20.65 |
| power | -5.62 |
| half | -2950.09 |
| eighth | -44.79 |
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
| com_rate | -12.11 |
| kl | 3.81 |
| elbo | -3373.08 |
