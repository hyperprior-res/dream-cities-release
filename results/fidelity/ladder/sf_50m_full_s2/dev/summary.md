## sf_50m_full_s2_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.285 | 0.287 | 0.286 | 0.265 to 0.305 | 0.173 | 0.171 | 0.172 | 0.147 to 0.200 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.294 | 0.295 | 0.294 | 0.273 to 0.314 | 0.188 | 0.183 | 0.185 | 0.156 to 0.218 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.250 | 0.259 | 0.255 | 0.231 to 0.278 | 0.126 | 0.129 | 0.128 | 0.111 to 0.147 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.633 | 0.204 | 0.004 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.386 / 0.402 |
| all plans | 500 | 12 | 0.438 | 0.146 | 0.044 / 0.003 / 0.378 | 0.040 / 0.026 / 0.103 | 0.353 / 0.428 |
| all plans | 500 | 24 | 0.527 | 0.167 | 0.082 / 0.005 / 0.678 | 0.067 / 0.042 / 0.160 | 0.316 / 0.408 |
| state-reading plans | 394 | 1 | 0.679 | 0.208 | 0.005 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.421 / 0.436 |
| state-reading plans | 394 | 12 | 0.431 | 0.151 | 0.048 / 0.003 / 0.465 | 0.040 / 0.025 / 0.103 | 0.372 / 0.442 |
| state-reading plans | 394 | 24 | 0.533 | 0.184 | 0.091 / 0.005 / 0.791 | 0.067 / 0.044 / 0.150 | 0.330 / 0.412 |
| open-loop plans | 106 | 1 | 0.597 | 0.199 | 0.000 / 0.000 / 0.000 | 0.007 / 0.008 / 0.007 | 0.232 / 0.257 |
| open-loop plans | 106 | 12 | 0.869 | 0.131 | 0.028 / 0.002 / 0.061 | 0.041 / 0.031 / 0.103 | 0.280 / 0.372 |
| open-loop plans | 106 | 24 | 1.073 | 0.122 | 0.056 / 0.005 / 0.140 | 0.065 / 0.036 / 0.203 | 0.268 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1719 | 0.829 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2859 | 0.901 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1714.8300 | 0.773 |
| funds_mae_12m | 5714.0800 | 36.8760 | 593.3107 | 0.902 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 204.9060 | 0.818 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 522.3220 | 0.806 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 351.5470 | 0.859 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0402 | 0.816 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0438 | 0.890 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3528 | 0.825 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3503 | 0.815 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3018.6250 | 0.774 |
| funds_mae_24m | 7364.5720 | 66.5620 | 906.7815 | 0.885 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 264.2160 | 0.784 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 612.8900 | 0.792 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 605.8043 | 0.578 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0667 | 0.793 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0818 | 0.886 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3164 | 0.776 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3143 | 0.771 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 906.8 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 264.2 | 142.8 | 706.1 |
| com_valve | 612.9 | 508.6 | 1010.2 |
| ind_valve | 605.8 | 416.9 | 864.8 |
| pop | 3018.6 | 1754.6 | 7353.4 |
| res_pop | 67.0 | 39.0 | 139.9 |
| com_pop | 6.9 | 4.4 | 12.8 |
| ind_pop | 10.2 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 55.3 | 25.2 | 89.6 |
| tax_fund | 122.4 | 51.5 | 1444.5 |
| road_spend | 83.8 | 8.2 | 647.3 |
| fire_spend | 34.4 | 0.8 | 474.7 |
| police_spend | 57.1 | 6.0 | 604.1 |
| powered_zones | 7.3 | 0.7 | 8.6 |
| unpowered_zones | 5.4 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 48.5 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 903.1 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 244.7 | 130.7 | 533.4 |
| com_valve | 649.1 | 541.8 | 962.1 |
| ind_valve | 662.0 | 446.9 | 814.5 |
| pop | 3052.8 | 1810.1 | 6881.1 |
| res_pop | 65.9 | 39.6 | 131.0 |
| com_pop | 6.9 | 4.5 | 12.1 |
| ind_pop | 10.3 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 58.1 | 26.2 | 83.7 |
| tax_fund | 116.5 | 47.1 | 1400.1 |
| road_spend | 78.1 | 8.1 | 645.8 |
| fire_spend | 30.9 | 0.8 | 464.7 |
| police_spend | 57.3 | 6.4 | 591.3 |
| powered_zones | 7.9 | 0.9 | 10.7 |
| unpowered_zones | 5.7 | 0.8 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 48.5 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 920.3 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 336.9 | 187.8 | 1348.3 |
| com_valve | 478.4 | 385.4 | 1188.9 |
| ind_valve | 396.9 | 305.2 | 1051.7 |
| pop | 2891.7 | 1548.5 | 9108.7 |
| res_pop | 71.1 | 37.0 | 172.8 |
| com_pop | 6.6 | 4.2 | 15.7 |
| ind_pop | 10.0 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 45.2 | 21.3 | 111.7 |
| tax_fund | 144.5 | 68.0 | 1609.5 |
| road_spend | 104.9 | 8.8 | 653.2 |
| fire_spend | 47.4 | 1.1 | 512.0 |
| police_spend | 56.4 | 4.6 | 651.4 |
| powered_zones | 5.1 | 0.0 | 0.5 |
| unpowered_zones | 4.0 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.6 | 0.0 | 0.2 |
| road_total | 48.6 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.134 | 0.838 |
| traffic | 1.072 | 0.772 |
| pollution | 1.639 | 0.706 |
| land_value | 0.632 | 0.325 |
| crime | 1.084 | 0.566 |
| rate_of_growth | 1.074 | 0.819 |
| fire_coverage | 2.692 | 0.123 |
| police_coverage | 1.239 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.584 | 0.263 | 0.362 | 0.339 to 0.382 | 0.574 | 0.133 | 0.217 | 0.178 to 0.257 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.465 | 0.002 | 0.006 |
| all plans | 12 | 0.300 | 0.040 | 0.031 |
| all plans | 24 | 0.372 | 0.086 | 0.052 |
| state-reading plans | 1 | 0.521 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.299 | 0.041 | 0.031 |
| state-reading plans | 24 | 0.387 | 0.099 | 0.051 |
| open-loop plans | 1 | 0.393 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.501 | 0.027 | 0.032 |
| open-loop plans | 24 | 0.652 | 0.064 | 0.054 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -215.41 |
| tile_cat | -30.87 |
| flags | -15.00 |
| power | -2.80 |
| half | -2376.68 |
| eighth | -36.39 |
| scalars_s2 | -5.75 |
| build_cost | -1.18 |
| scalars | -12.86 |
| ledger | -12.94 |
| bk | -20.04 |
| sc_res_pop | -1.79 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.23 |
| sc_powered_zones | -0.08 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.38 |
| sc_res_valve | -0.96 |
| sc_com_valve | -1.99 |
| sc_ind_valve | -1.54 |
| sc_score | -0.39 |
| sc_funds | -1.00 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.47 |
| sc_fire_spend | -0.16 |
| sc_police_spend | -0.15 |
| lg_sprite_cycle | -0.72 |
| lg_total_pop | -1.52 |
| lg_res_hist0 | -0.53 |
| lg_res_hist1 | -0.35 |
| lg_com_hist0 | -0.13 |
| lg_com_hist1 | -0.09 |
| lg_ind_hist0 | -0.20 |
| lg_ind_hist1 | -0.21 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.53 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.13 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -2.95 |
| lg_pollution_max_y | -2.92 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.34 |
| terrain | -4.80 |
| com_rate | -3.02 |
| kl | 13.47 |
| elbo | -2725.42 |

## sf_50m_full_s2_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "f5d737081dd2e7ae", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.291 | 0.285 | 0.288 | 0.267 to 0.308 | 0.181 | 0.169 | 0.175 | 0.149 to 0.205 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.300 | 0.294 | 0.297 | 0.275 to 0.317 | 0.196 | 0.182 | 0.189 | 0.158 to 0.223 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.255 | 0.254 | 0.255 | 0.231 to 0.277 | 0.129 | 0.125 | 0.127 | 0.109 to 0.149 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.452 | 0.204 | 0.002 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 | 0.388 / 0.402 |
| all plans | 500 | 12 | 0.458 | 0.146 | 0.062 / 0.003 / 0.378 | 0.043 / 0.026 / 0.103 | 0.325 / 0.428 |
| all plans | 500 | 24 | 0.659 | 0.167 | 0.171 / 0.005 / 0.678 | 0.085 / 0.042 / 0.160 | 0.269 / 0.408 |
| state-reading plans | 394 | 1 | 0.444 | 0.208 | 0.002 / 0.000 / 0.018 | 0.008 / 0.006 / 0.007 | 0.424 / 0.436 |
| state-reading plans | 394 | 12 | 0.450 | 0.151 | 0.065 / 0.003 / 0.465 | 0.043 / 0.025 / 0.103 | 0.344 / 0.442 |
| state-reading plans | 394 | 24 | 0.662 | 0.184 | 0.192 / 0.005 / 0.791 | 0.085 / 0.044 / 0.150 | 0.283 / 0.412 |
| open-loop plans | 106 | 1 | 0.458 | 0.199 | 0.000 / 0.000 / 0.000 | 0.008 / 0.008 / 0.007 | 0.232 / 0.257 |
| open-loop plans | 106 | 12 | 0.928 | 0.131 | 0.046 / 0.002 / 0.061 | 0.042 / 0.031 / 0.103 | 0.251 / 0.372 |
| open-loop plans | 106 | 24 | 1.381 | 0.122 | 0.124 / 0.005 / 0.140 | 0.088 / 0.036 / 0.203 | 0.220 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1746 | 0.842 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2880 | 0.908 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1889.3400 | 0.715 |
| funds_mae_12m | 5714.0800 | 36.8760 | 784.2455 | 0.868 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 204.2463 | 0.820 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 560.8392 | 0.761 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 364.6250 | 0.839 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0427 | 0.784 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0616 | 0.843 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3248 | 0.760 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3237 | 0.753 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 4108.8000 | 0.580 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1703.6085 | 0.776 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 339.1215 | 0.651 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 693.6310 | 0.631 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 665.9728 | 0.444 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0848 | 0.639 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1711 | 0.753 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2693 | 0.661 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2691 | 0.660 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1703.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 339.1 | 142.8 | 706.1 |
| com_valve | 693.6 | 508.6 | 1010.2 |
| ind_valve | 666.0 | 416.9 | 864.8 |
| pop | 4108.8 | 1754.6 | 7353.4 |
| res_pop | 84.3 | 39.0 | 139.9 |
| com_pop | 8.4 | 4.4 | 12.8 |
| ind_pop | 13.1 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 79.7 | 25.2 | 89.6 |
| tax_fund | 132.0 | 51.5 | 1444.5 |
| road_spend | 86.8 | 8.2 | 647.3 |
| fire_spend | 49.1 | 0.8 | 474.7 |
| police_spend | 73.9 | 6.0 | 604.1 |
| powered_zones | 8.7 | 0.7 | 8.6 |
| unpowered_zones | 6.6 | 0.6 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.3 |
| road_total | 59.1 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1676.7 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 307.9 | 130.7 | 533.4 |
| com_valve | 726.7 | 541.8 | 962.1 |
| ind_valve | 724.4 | 446.9 | 814.5 |
| pop | 4154.2 | 1810.1 | 6881.1 |
| res_pop | 83.3 | 39.6 | 131.0 |
| com_pop | 8.5 | 4.5 | 12.1 |
| ind_pop | 13.2 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 83.3 | 26.2 | 83.7 |
| tax_fund | 126.0 | 47.1 | 1400.1 |
| road_spend | 81.9 | 8.1 | 645.8 |
| fire_spend | 44.2 | 0.8 | 464.7 |
| police_spend | 71.2 | 6.4 | 591.3 |
| powered_zones | 9.3 | 0.9 | 10.7 |
| unpowered_zones | 6.9 | 0.8 | 7.0 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.4 |
| road_total | 60.0 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1803.5 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 455.0 | 187.8 | 1348.3 |
| com_valve | 570.7 | 385.4 | 1188.9 |
| ind_valve | 448.8 | 305.2 | 1051.7 |
| pop | 3940.2 | 1548.5 | 9108.7 |
| res_pop | 88.1 | 37.0 | 172.8 |
| com_pop | 7.8 | 4.2 | 15.7 |
| ind_pop | 12.6 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 66.5 | 21.3 | 111.7 |
| tax_fund | 154.4 | 68.0 | 1609.5 |
| road_spend | 105.3 | 8.8 | 653.2 |
| fire_spend | 67.2 | 1.1 | 512.0 |
| police_spend | 84.0 | 4.6 | 651.4 |
| powered_zones | 6.6 | 0.0 | 0.5 |
| unpowered_zones | 5.4 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.8 | 0.0 | 0.2 |
| road_total | 56.0 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.257 | 0.838 |
| traffic | 1.147 | 0.772 |
| pollution | 1.898 | 0.706 |
| land_value | 0.808 | 0.325 |
| crime | 1.373 | 0.566 |
| rate_of_growth | 1.176 | 0.819 |
| fire_coverage | 10.873 | 0.123 |
| police_coverage | 2.810 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.569 | 0.263 | 0.359 | 0.337 to 0.378 | 0.523 | 0.133 | 0.212 | 0.175 to 0.252 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.355 | 0.001 | 0.006 |
| all plans | 12 | 0.326 | 0.062 | 0.031 |
| all plans | 24 | 0.503 | 0.216 | 0.072 |
| state-reading plans | 1 | 0.354 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.324 | 0.065 | 0.031 |
| state-reading plans | 24 | 0.512 | 0.230 | 0.072 |
| open-loop plans | 1 | 0.345 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.606 | 0.049 | 0.033 |
| open-loop plans | 24 | 1.033 | 0.125 | 0.071 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -214.09 |
| tile_cat | -30.70 |
| flags | -14.78 |
| power | -2.60 |
| half | -2358.67 |
| eighth | -35.98 |
| scalars_s2 | -5.20 |
| build_cost | -0.88 |
| scalars | -12.15 |
| ledger | -13.09 |
| bk | -20.04 |
| sc_res_pop | -1.46 |
| sc_com_pop | -0.12 |
| sc_ind_pop | -0.21 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.36 |
| sc_res_valve | -0.99 |
| sc_com_valve | -1.93 |
| sc_ind_valve | -1.10 |
| sc_score | -0.49 |
| sc_funds | -0.89 |
| sc_tax_fund | -0.48 |
| sc_road_spend | -0.57 |
| sc_fire_spend | -0.25 |
| sc_police_spend | -0.25 |
| lg_sprite_cycle | -0.85 |
| lg_total_pop | -1.48 |
| lg_res_hist0 | -0.29 |
| lg_res_hist1 | -0.34 |
| lg_com_hist0 | -0.05 |
| lg_com_hist1 | -0.07 |
| lg_ind_hist0 | -0.06 |
| lg_ind_hist1 | -0.19 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.02 |
| lg_road_fund | -0.76 |
| lg_police_fund | -0.24 |
| lg_fire_fund | -0.18 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.01 |
| lg_pollution_max_y | -3.03 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.35 |
| terrain | -4.71 |
| com_rate | -2.83 |
| kl | 13.89 |
| elbo | -2704.38 |
