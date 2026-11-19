## sf_50m_small_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.234 | 0.295 | 0.261 | 0.240 to 0.281 | 0.130 | 0.179 | 0.150 | 0.129 to 0.176 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.241 | 0.302 | 0.268 | 0.247 to 0.289 | 0.139 | 0.190 | 0.161 | 0.136 to 0.190 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.208 | 0.269 | 0.235 | 0.212 to 0.258 | 0.098 | 0.139 | 0.115 | 0.100 to 0.133 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.782 | 0.204 | 0.004 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.355 / 0.402 |
| all plans | 500 | 12 | 0.533 | 0.146 | 0.046 / 0.003 / 0.378 | 0.048 / 0.026 / 0.103 | 0.318 / 0.428 |
| all plans | 500 | 24 | 0.668 | 0.167 | 0.072 / 0.005 / 0.678 | 0.086 / 0.042 / 0.160 | 0.283 / 0.408 |
| state-reading plans | 394 | 1 | 0.906 | 0.208 | 0.005 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.393 / 0.436 |
| state-reading plans | 394 | 12 | 0.524 | 0.151 | 0.050 / 0.003 / 0.465 | 0.049 / 0.025 / 0.103 | 0.336 / 0.442 |
| state-reading plans | 394 | 24 | 0.674 | 0.184 | 0.081 / 0.005 / 0.791 | 0.087 / 0.044 / 0.150 | 0.296 / 0.412 |
| open-loop plans | 106 | 1 | 0.686 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.193 / 0.257 |
| open-loop plans | 106 | 12 | 1.091 | 0.131 | 0.033 / 0.002 / 0.061 | 0.048 / 0.031 / 0.103 | 0.250 / 0.372 |
| open-loop plans | 106 | 24 | 1.451 | 0.122 | 0.044 / 0.005 / 0.140 | 0.085 / 0.036 / 0.203 | 0.237 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1504 | 0.725 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2610 | 0.823 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2117.0600 | 0.639 |
| funds_mae_12m | 5714.0800 | 36.8760 | 781.7425 | 0.869 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 219.2660 | 0.791 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 544.9575 | 0.780 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 350.5755 | 0.860 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0484 | 0.710 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0459 | 0.885 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3179 | 0.743 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3156 | 0.734 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 4515.0250 | 0.507 |
| funds_mae_24m | 7364.5720 | 66.5620 | 955.2118 | 0.878 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 327.4388 | 0.672 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 640.0933 | 0.738 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 620.7790 | 0.545 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0862 | 0.626 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0720 | 0.900 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2835 | 0.696 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2815 | 0.690 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 955.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 327.4 | 142.8 | 706.1 |
| com_valve | 640.1 | 508.6 | 1010.2 |
| ind_valve | 620.8 | 416.9 | 864.8 |
| pop | 4515.0 | 1754.6 | 7353.4 |
| res_pop | 92.0 | 39.0 | 139.9 |
| com_pop | 8.8 | 4.4 | 12.8 |
| ind_pop | 14.8 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 89.4 | 25.2 | 89.6 |
| tax_fund | 191.0 | 51.5 | 1444.5 |
| road_spend | 99.6 | 8.2 | 647.3 |
| fire_spend | 58.6 | 0.8 | 474.7 |
| police_spend | 95.5 | 6.0 | 604.1 |
| powered_zones | 9.8 | 0.7 | 8.6 |
| unpowered_zones | 5.5 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.3 |
| road_total | 66.3 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 924.7 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 280.2 | 130.7 | 533.4 |
| com_valve | 672.5 | 541.8 | 962.1 |
| ind_valve | 676.6 | 446.9 | 814.5 |
| pop | 4619.3 | 1810.1 | 6881.1 |
| res_pop | 90.6 | 39.6 | 131.0 |
| com_pop | 9.0 | 4.5 | 12.1 |
| ind_pop | 15.1 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 94.9 | 26.2 | 83.7 |
| tax_fund | 178.2 | 47.1 | 1400.1 |
| road_spend | 91.0 | 8.1 | 645.8 |
| fire_spend | 52.8 | 0.8 | 464.7 |
| police_spend | 90.8 | 6.4 | 591.3 |
| powered_zones | 10.5 | 0.9 | 10.7 |
| unpowered_zones | 5.8 | 0.8 | 7.0 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 66.8 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1068.8 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 502.9 | 187.8 | 1348.3 |
| com_valve | 519.5 | 385.4 | 1188.9 |
| ind_valve | 413.1 | 305.2 | 1051.7 |
| pop | 4127.4 | 1548.5 | 9108.7 |
| res_pop | 97.4 | 37.0 | 172.8 |
| com_pop | 8.1 | 4.2 | 15.7 |
| ind_pop | 13.6 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 69.1 | 21.3 | 111.7 |
| tax_fund | 238.6 | 68.0 | 1609.5 |
| road_spend | 131.3 | 8.8 | 653.2 |
| fire_spend | 80.4 | 1.1 | 512.0 |
| police_spend | 113.1 | 4.6 | 651.4 |
| powered_zones | 7.3 | 0.0 | 0.5 |
| unpowered_zones | 4.3 | 0.0 | 6.7 |
| coal_plants | 0.4 | 0.0 | 0.1 |
| nuclear_plants | 0.6 | 0.0 | 0.2 |
| road_total | 64.6 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.265 | 0.838 |
| traffic | 1.158 | 0.772 |
| pollution | 1.698 | 0.706 |
| land_value | 0.763 | 0.325 |
| crime | 1.239 | 0.566 |
| rate_of_growth | 1.248 | 0.819 |
| fire_coverage | 1.429 | 0.123 |
| police_coverage | 1.005 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.404 | 0.286 | 0.335 | 0.313 to 0.356 | 0.278 | 0.157 | 0.201 | 0.167 to 0.239 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.620 | 0.002 | 0.006 |
| all plans | 12 | 0.379 | 0.039 | 0.037 |
| all plans | 24 | 0.504 | 0.067 | 0.073 |
| state-reading plans | 1 | 0.729 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.374 | 0.039 | 0.037 |
| state-reading plans | 24 | 0.513 | 0.079 | 0.074 |
| open-loop plans | 1 | 0.527 | 0.001 | 0.006 |
| open-loop plans | 12 | 0.687 | 0.031 | 0.036 |
| open-loop plans | 24 | 1.068 | 0.042 | 0.071 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -282.50 |
| tile_cat | -38.52 |
| flags | -19.08 |
| power | -5.25 |
| half | -2713.32 |
| eighth | -39.15 |
| scalars_s2 | -5.78 |
| build_cost | -1.18 |
| scalars | -15.50 |
| ledger | -19.11 |
| bk | -28.82 |
| sc_res_pop | -1.75 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.24 |
| sc_powered_zones | -0.09 |
| sc_unpowered_zones | -0.11 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.39 |
| sc_res_valve | -1.12 |
| sc_com_valve | -2.18 |
| sc_ind_valve | -1.88 |
| sc_score | -0.85 |
| sc_funds | -1.34 |
| sc_tax_fund | -0.78 |
| sc_road_spend | -0.97 |
| sc_fire_spend | -0.30 |
| sc_police_spend | -0.30 |
| lg_sprite_cycle | -0.85 |
| lg_total_pop | -2.14 |
| lg_res_hist0 | -1.21 |
| lg_res_hist1 | -0.86 |
| lg_com_hist0 | -0.34 |
| lg_com_hist1 | -0.26 |
| lg_ind_hist0 | -0.40 |
| lg_ind_hist1 | -0.47 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.02 |
| lg_ind_cap | -0.01 |
| lg_need_hospital | -0.14 |
| lg_need_church | -0.11 |
| lg_road_fund | -0.98 |
| lg_police_fund | -0.29 |
| lg_fire_fund | -0.20 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.11 |
| lg_city_center_y | -0.17 |
| lg_pollution_max_x | -3.77 |
| lg_pollution_max_y | -4.00 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.67 |
| terrain | -6.47 |
| com_rate | -6.11 |
| kl | 13.22 |
| elbo | -3159.42 |

## sf_50m_small_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.233 | 0.296 | 0.261 | 0.241 to 0.281 | 0.130 | 0.180 | 0.151 | 0.129 to 0.177 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.241 | 0.304 | 0.269 | 0.248 to 0.289 | 0.140 | 0.193 | 0.162 | 0.137 to 0.191 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.207 | 0.268 | 0.233 | 0.210 to 0.258 | 0.096 | 0.136 | 0.113 | 0.096 to 0.133 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.537 | 0.204 | 0.002 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.355 / 0.402 |
| all plans | 500 | 12 | 0.512 | 0.146 | 0.044 / 0.003 / 0.378 | 0.054 / 0.026 / 0.103 | 0.307 / 0.428 |
| all plans | 500 | 24 | 0.687 | 0.167 | 0.068 / 0.005 / 0.678 | 0.104 / 0.042 / 0.160 | 0.272 / 0.408 |
| state-reading plans | 394 | 1 | 0.552 | 0.208 | 0.002 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.392 / 0.436 |
| state-reading plans | 394 | 12 | 0.507 | 0.151 | 0.048 / 0.003 / 0.465 | 0.056 / 0.025 / 0.103 | 0.325 / 0.442 |
| state-reading plans | 394 | 24 | 0.698 | 0.184 | 0.077 / 0.005 / 0.791 | 0.104 / 0.044 / 0.150 | 0.286 / 0.412 |
| open-loop plans | 106 | 1 | 0.515 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.196 / 0.257 |
| open-loop plans | 106 | 12 | 1.003 | 0.131 | 0.029 / 0.002 / 0.061 | 0.050 / 0.031 / 0.103 | 0.237 / 0.372 |
| open-loop plans | 106 | 24 | 1.560 | 0.122 | 0.042 / 0.005 / 0.140 | 0.104 / 0.036 / 0.203 | 0.222 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1507 | 0.726 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2612 | 0.824 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2525.9850 | 0.504 |
| funds_mae_12m | 5714.0800 | 36.8760 | 806.9277 | 0.864 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 236.0137 | 0.760 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 563.4545 | 0.758 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 357.1332 | 0.850 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0542 | 0.635 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0437 | 0.891 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3068 | 0.717 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3056 | 0.711 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5317.3050 | 0.364 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1012.3452 | 0.870 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 392.4170 | 0.557 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 700.3080 | 0.618 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 684.0475 | 0.403 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1041 | 0.474 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0680 | 0.906 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2721 | 0.668 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2707 | 0.664 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1012.3 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 392.4 | 142.8 | 706.1 |
| com_valve | 700.3 | 508.6 | 1010.2 |
| ind_valve | 684.0 | 416.9 | 864.8 |
| pop | 5317.3 | 1754.6 | 7353.4 |
| res_pop | 101.3 | 39.0 | 139.9 |
| com_pop | 10.3 | 4.4 | 12.8 |
| ind_pop | 17.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 103.0 | 25.2 | 89.6 |
| tax_fund | 209.1 | 51.5 | 1444.5 |
| road_spend | 97.1 | 8.2 | 647.3 |
| fire_spend | 58.1 | 0.8 | 474.7 |
| police_spend | 99.1 | 6.0 | 604.1 |
| powered_zones | 10.6 | 0.7 | 8.6 |
| unpowered_zones | 4.9 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 72.0 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 974.5 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 343.4 | 130.7 | 533.4 |
| com_valve | 738.6 | 541.8 | 962.1 |
| ind_valve | 735.4 | 446.9 | 814.5 |
| pop | 5428.2 | 1810.1 | 6881.1 |
| res_pop | 101.5 | 39.6 | 131.0 |
| com_pop | 10.4 | 4.5 | 12.1 |
| ind_pop | 18.1 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 107.7 | 26.2 | 83.7 |
| tax_fund | 194.4 | 47.1 | 1400.1 |
| road_spend | 88.9 | 8.1 | 645.8 |
| fire_spend | 52.1 | 0.8 | 464.7 |
| police_spend | 95.6 | 6.4 | 591.3 |
| powered_zones | 11.2 | 0.9 | 10.7 |
| unpowered_zones | 5.4 | 0.8 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 72.9 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1153.0 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 574.8 | 187.8 | 1348.3 |
| com_valve | 557.9 | 385.4 | 1188.9 |
| ind_valve | 493.0 | 305.2 | 1051.7 |
| pop | 4905.0 | 1548.5 | 9108.7 |
| res_pop | 100.4 | 37.0 | 172.8 |
| com_pop | 9.9 | 4.2 | 15.7 |
| ind_pop | 15.5 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 85.6 | 21.3 | 111.7 |
| tax_fund | 263.7 | 68.0 | 1609.5 |
| road_spend | 127.4 | 8.8 | 653.2 |
| fire_spend | 80.5 | 1.1 | 512.0 |
| police_spend | 112.1 | 4.6 | 651.4 |
| powered_zones | 8.6 | 0.0 | 0.5 |
| unpowered_zones | 3.4 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.5 | 0.0 | 0.2 |
| road_total | 68.9 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.328 | 0.838 |
| traffic | 1.154 | 0.772 |
| pollution | 1.698 | 0.706 |
| land_value | 0.795 | 0.325 |
| crime | 1.284 | 0.566 |
| rate_of_growth | 1.288 | 0.819 |
| fire_coverage | 1.531 | 0.123 |
| police_coverage | 1.033 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.364 | 0.291 | 0.323 | 0.301 to 0.345 | 0.230 | 0.166 | 0.193 | 0.161 to 0.229 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.413 | 0.001 | 0.006 |
| all plans | 12 | 0.389 | 0.034 | 0.044 |
| all plans | 24 | 0.550 | 0.072 | 0.089 |
| state-reading plans | 1 | 0.434 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.389 | 0.036 | 0.047 |
| state-reading plans | 24 | 0.564 | 0.079 | 0.087 |
| open-loop plans | 1 | 0.376 | 0.001 | 0.007 |
| open-loop plans | 12 | 0.748 | 0.026 | 0.038 |
| open-loop plans | 24 | 1.298 | 0.042 | 0.096 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -309.12 |
| tile_cat | -40.50 |
| flags | -20.17 |
| power | -6.08 |
| half | -2807.16 |
| eighth | -39.54 |
| scalars_s2 | -5.29 |
| build_cost | -0.89 |
| scalars | -28.86 |
| ledger | -36.89 |
| bk | -60.46 |
| sc_res_pop | -1.48 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.22 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.36 |
| sc_res_valve | -1.61 |
| sc_com_valve | -2.82 |
| sc_ind_valve | -2.37 |
| sc_score | -5.22 |
| sc_funds | -3.38 |
| sc_tax_fund | -2.06 |
| sc_road_spend | -3.81 |
| sc_fire_spend | -1.18 |
| sc_police_spend | -1.12 |
| lg_sprite_cycle | -1.33 |
| lg_total_pop | -4.10 |
| lg_res_hist0 | -2.84 |
| lg_res_hist1 | -3.36 |
| lg_com_hist0 | -0.60 |
| lg_com_hist1 | -0.66 |
| lg_ind_hist0 | -0.50 |
| lg_ind_hist1 | -1.21 |
| lg_res_cap | -0.03 |
| lg_com_cap | -0.10 |
| lg_ind_cap | -0.02 |
| lg_need_hospital | -0.25 |
| lg_need_church | -0.18 |
| lg_road_fund | -2.45 |
| lg_police_fund | -0.70 |
| lg_fire_fund | -0.59 |
| lg_auto_budget | -0.02 |
| lg_fire_pop | -0.16 |
| lg_city_center_x | -0.17 |
| lg_city_center_y | -0.51 |
| lg_pollution_max_x | -6.49 |
| lg_pollution_max_y | -6.83 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -3.78 |
| terrain | -6.43 |
| com_rate | -7.21 |
| kl | 13.59 |
| elbo | -3316.43 |
