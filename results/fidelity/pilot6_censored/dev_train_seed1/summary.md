## pilot6_censored_s1_samples_000600064_dec-a

samples consumed: 600064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "c0a3ceceb9a2a0bf", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.261 | 0.268 | 0.264 | 0.242 to 0.284 | 0.147 | 0.146 | 0.147 | 0.123 to 0.173 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.269 | 0.275 | 0.272 | 0.250 to 0.292 | 0.161 | 0.159 | 0.160 | 0.132 to 0.191 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.229 | 0.239 | 0.234 | 0.211 to 0.257 | 0.102 | 0.103 | 0.103 | 0.091 to 0.116 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.573 | 0.204 | 0.004 / 0.000 / 0.017 | 0.007 / 0.006 / 0.007 | 0.342 / 0.402 |
| all plans | 500 | 12 | 0.389 | 0.146 | 0.044 / 0.003 / 0.378 | 0.029 / 0.026 / 0.103 | 0.343 / 0.428 |
| all plans | 500 | 24 | 0.434 | 0.167 | 0.063 / 0.005 / 0.678 | 0.064 / 0.042 / 0.160 | 0.317 / 0.408 |
| state-reading plans | 394 | 1 | 0.558 | 0.208 | 0.005 / 0.000 / 0.018 | 0.007 / 0.006 / 0.007 | 0.378 / 0.436 |
| state-reading plans | 394 | 12 | 0.389 | 0.151 | 0.051 / 0.003 / 0.465 | 0.030 / 0.025 / 0.103 | 0.365 / 0.442 |
| state-reading plans | 394 | 24 | 0.450 | 0.184 | 0.076 / 0.005 / 0.791 | 0.066 / 0.044 / 0.150 | 0.331 / 0.412 |
| open-loop plans | 106 | 1 | 0.604 | 0.199 | 0.000 / 0.000 / 0.000 | 0.007 / 0.008 / 0.007 | 0.186 / 0.257 |
| open-loop plans | 106 | 12 | 0.504 | 0.131 | 0.019 / 0.002 / 0.061 | 0.028 / 0.031 / 0.103 | 0.262 / 0.372 |
| open-loop plans | 106 | 24 | 0.533 | 0.122 | 0.026 / 0.005 / 0.140 | 0.058 / 0.036 / 0.203 | 0.266 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1467 | 0.707 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2642 | 0.833 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1355.1750 | 0.893 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1117.4127 | 0.810 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 208.2610 | 0.812 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 492.6832 | 0.841 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 313.4452 | 0.916 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0295 | 0.954 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0442 | 0.889 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3434 | 0.803 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3388 | 0.788 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2876.3750 | 0.800 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1304.3502 | 0.830 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 269.9853 | 0.774 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 588.5335 | 0.841 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 515.8362 | 0.779 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0637 | 0.818 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0635 | 0.913 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3173 | 0.779 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3142 | 0.770 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1304.4 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 270.0 | 142.8 | 706.1 |
| com_valve | 588.5 | 508.6 | 1010.2 |
| ind_valve | 515.8 | 416.9 | 864.8 |
| pop | 2876.4 | 1754.6 | 7353.4 |
| res_pop | 62.7 | 39.0 | 139.9 |
| com_pop | 5.9 | 4.4 | 12.8 |
| ind_pop | 8.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 48.6 | 25.2 | 89.6 |
| tax_fund | 158.4 | 51.5 | 1444.5 |
| road_spend | 81.4 | 8.2 | 647.3 |
| fire_spend | 29.3 | 0.8 | 474.7 |
| police_spend | 54.8 | 6.0 | 604.1 |
| powered_zones | 5.3 | 0.7 | 8.6 |
| unpowered_zones | 4.8 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 49.7 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1156.7 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 252.4 | 130.7 | 533.4 |
| com_valve | 615.0 | 541.8 | 962.1 |
| ind_valve | 555.0 | 446.9 | 814.5 |
| pop | 2915.2 | 1810.1 | 6881.1 |
| res_pop | 62.8 | 39.6 | 131.0 |
| com_pop | 5.9 | 4.5 | 12.1 |
| ind_pop | 8.6 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 50.7 | 26.2 | 83.7 |
| tax_fund | 150.0 | 47.1 | 1400.1 |
| road_spend | 76.1 | 8.1 | 645.8 |
| fire_spend | 24.4 | 0.8 | 464.7 |
| police_spend | 48.2 | 6.4 | 591.3 |
| powered_zones | 6.3 | 0.9 | 10.7 |
| unpowered_zones | 5.2 | 0.8 | 7.0 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.0 | 0.4 |
| road_total | 49.6 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1853.3 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 335.3 | 187.8 | 1348.3 |
| com_valve | 490.0 | 385.4 | 1188.9 |
| ind_valve | 370.2 | 305.2 | 1051.7 |
| pop | 2731.9 | 1548.5 | 9108.7 |
| res_pop | 62.5 | 37.0 | 172.8 |
| com_pop | 6.1 | 4.2 | 15.7 |
| ind_pop | 8.4 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 40.6 | 21.3 | 111.7 |
| tax_fund | 189.9 | 68.0 | 1609.5 |
| road_spend | 101.2 | 8.8 | 653.2 |
| fire_spend | 47.5 | 1.1 | 512.0 |
| police_spend | 79.3 | 4.6 | 651.4 |
| powered_zones | 1.3 | 0.0 | 0.5 |
| unpowered_zones | 3.2 | 0.0 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 50.0 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.117 | 0.838 |
| traffic | 1.217 | 0.772 |
| pollution | 1.727 | 0.706 |
| land_value | 0.844 | 0.325 |
| crime | 1.222 | 0.566 |
| rate_of_growth | 1.058 | 0.819 |
| fire_coverage | 1.292 | 0.123 |
| police_coverage | 0.976 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.604 | 0.242 | 0.345 | 0.321 to 0.368 | 0.801 | 0.110 | 0.193 | 0.153 to 0.236 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.506 | 0.002 | 0.005 |
| all plans | 12 | 0.314 | 0.036 | 0.024 |
| all plans | 24 | 0.358 | 0.063 | 0.053 |
| state-reading plans | 1 | 0.489 | 0.002 | 0.005 |
| state-reading plans | 12 | 0.313 | 0.046 | 0.024 |
| state-reading plans | 24 | 0.373 | 0.078 | 0.057 |
| open-loop plans | 1 | 0.530 | 0.001 | 0.004 |
| open-loop plans | 12 | 0.392 | 0.014 | 0.024 |
| open-loop plans | 24 | 0.403 | 0.030 | 0.046 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -260.14 |
| tile_cat | -40.79 |
| flags | -20.76 |
| power | -5.42 |
| half | -2938.49 |
| eighth | -45.04 |
| scalars_s2 | -6.00 |
| build_cost | -1.19 |
| scalars | -12.86 |
| ledger | -12.80 |
| bk | -19.66 |
| sc_res_pop | -1.82 |
| sc_com_pop | -0.23 |
| sc_ind_pop | -0.31 |
| sc_powered_zones | -0.09 |
| sc_unpowered_zones | -0.08 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.43 |
| sc_res_valve | -0.98 |
| sc_com_valve | -1.94 |
| sc_ind_valve | -1.17 |
| sc_score | -0.45 |
| sc_funds | -0.96 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.51 |
| sc_fire_spend | -0.20 |
| sc_police_spend | -0.20 |
| lg_sprite_cycle | -0.70 |
| lg_total_pop | -1.54 |
| lg_res_hist0 | -0.32 |
| lg_res_hist1 | -0.26 |
| lg_com_hist0 | -0.05 |
| lg_com_hist1 | -0.20 |
| lg_ind_hist0 | -0.08 |
| lg_ind_hist1 | -0.33 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.03 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.53 |
| lg_police_fund | -0.21 |
| lg_fire_fund | -0.18 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.11 |
| lg_city_center_y | -0.09 |
| lg_pollution_max_x | -2.81 |
| lg_pollution_max_y | -2.92 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -9.18 |
| com_rate | -12.73 |
| kl | 3.68 |
| elbo | -3363.07 |
