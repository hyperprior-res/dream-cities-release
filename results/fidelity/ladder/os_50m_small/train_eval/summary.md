## os_50m_small_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.332 | 0.327 | 0.329 | 0.317 to 0.342 | 0.223 | 0.206 | 0.214 | 0.189 to 0.245 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.337 | 0.331 | 0.334 | 0.322 to 0.348 | 0.233 | 0.215 | 0.224 | 0.195 to 0.258 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.312 | 0.310 | 0.311 | 0.292 to 0.328 | 0.185 | 0.173 | 0.179 | 0.148 to 0.215 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.433 | 0.197 | 0.004 / 0.000 / 0.012 | 0.010 / 0.007 / 0.010 | 0.384 / 0.386 |
| all plans | 500 | 12 | 0.371 | 0.190 | 0.038 / 0.003 / 0.314 | 0.045 / 0.030 / 0.091 | 0.361 / 0.393 |
| all plans | 500 | 24 | 0.416 | 0.188 | 0.060 / 0.006 / 0.521 | 0.080 / 0.045 / 0.163 | 0.342 / 0.389 |
| state-reading plans | 393 | 1 | 0.500 | 0.217 | 0.005 / 0.000 / 0.018 | 0.009 / 0.007 / 0.010 | 0.419 / 0.422 |
| state-reading plans | 393 | 12 | 0.372 | 0.188 | 0.041 / 0.004 / 0.369 | 0.045 / 0.030 / 0.089 | 0.383 / 0.410 |
| state-reading plans | 393 | 24 | 0.431 | 0.191 | 0.068 / 0.006 / 0.714 | 0.079 / 0.046 / 0.154 | 0.357 / 0.399 |
| open-loop plans | 107 | 1 | 0.418 | 0.179 | 0.000 / 0.000 / 0.000 | 0.010 / 0.007 / 0.010 | 0.226 / 0.231 |
| open-loop plans | 107 | 12 | 0.420 | 0.229 | 0.027 / 0.003 / 0.111 | 0.047 / 0.033 / 0.120 | 0.273 / 0.324 |
| open-loop plans | 107 | 24 | 0.443 | 0.222 | 0.034 / 0.005 / 0.164 | 0.088 / 0.044 / 0.212 | 0.280 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.2139 | 0.919 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3292 | 0.964 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 1969.0200 | 0.731 |
| funds_mae_12m | 4895.7120 | 42.3740 | 597.2487 | 0.886 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 254.4445 | 0.840 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 516.5312 | 0.832 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 372.7298 | 0.845 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0454 | 0.748 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0378 | 0.890 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3614 | 0.919 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3683 | 0.913 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 3475.1850 | 0.705 |
| funds_mae_24m | 6681.5280 | 66.8000 | 718.5905 | 0.901 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 329.6298 | 0.793 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 694.5165 | 0.700 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 526.7495 | 0.783 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0800 | 0.705 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0601 | 0.894 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.3418 | 0.879 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.3448 | 0.880 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 718.6 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 329.6 | 218.6 | 754.9 |
| com_valve | 694.5 | 492.3 | 1165.4 |
| ind_valve | 526.7 | 371.1 | 1086.8 |
| pop | 3475.2 | 1875.9 | 7303.8 |
| res_pop | 72.3 | 44.7 | 158.4 |
| com_pop | 7.5 | 5.2 | 13.9 |
| ind_pop | 10.8 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 50.4 | 27.9 | 107.4 |
| tax_fund | 129.6 | 54.7 | 1326.7 |
| road_spend | 60.6 | 11.9 | 835.4 |
| fire_spend | 37.9 | 2.6 | 431.3 |
| police_spend | 68.7 | 3.8 | 545.1 |
| powered_zones | 6.7 | 2.8 | 10.6 |
| unpowered_zones | 5.7 | 2.6 | 8.5 |
| coal_plants | 0.1 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 58.1 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 732.6 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 290.6 | 160.2 | 525.9 |
| com_valve | 735.1 | 495.6 | 1123.2 |
| ind_valve | 587.0 | 397.1 | 1024.3 |
| pop | 3470.0 | 1889.8 | 6800.2 |
| res_pop | 71.6 | 44.3 | 148.6 |
| com_pop | 7.3 | 5.1 | 12.6 |
| ind_pop | 10.8 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 52.2 | 27.1 | 100.2 |
| tax_fund | 124.1 | 50.6 | 1281.6 |
| road_spend | 57.2 | 11.6 | 824.6 |
| fire_spend | 34.8 | 3.0 | 413.3 |
| police_spend | 68.4 | 3.5 | 516.9 |
| powered_zones | 7.2 | 2.5 | 12.5 |
| unpowered_zones | 6.0 | 2.4 | 9.0 |
| coal_plants | 0.1 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 57.4 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 667.0 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 472.9 | 433.2 | 1596.0 |
| com_valve | 545.5 | 480.1 | 1320.4 |
| ind_valve | 305.4 | 275.6 | 1316.6 |
| pop | 3494.3 | 1825.0 | 9153.8 |
| res_pop | 75.0 | 46.2 | 194.5 |
| com_pop | 8.3 | 5.4 | 18.4 |
| ind_pop | 10.4 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.8 | 30.9 | 133.7 |
| tax_fund | 149.5 | 69.9 | 1492.4 |
| road_spend | 73.2 | 13.0 | 875.0 |
| fire_spend | 49.5 | 0.9 | 497.3 |
| police_spend | 69.6 | 4.7 | 648.6 |
| powered_zones | 5.0 | 3.8 | 3.7 |
| unpowered_zones | 4.6 | 3.2 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.1 | 0.0 | 0.2 |
| road_total | 60.9 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 0.983 | 0.858 |
| traffic | 0.916 | 0.787 |
| pollution | 1.457 | 0.738 |
| land_value | 0.645 | 0.398 |
| crime | 0.961 | 0.597 |
| rate_of_growth | 1.025 | 0.852 |
| fire_coverage | 0.755 | 0.146 |
| police_coverage | 0.655 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.462 | 0.319 | 0.377 | 0.362 to 0.392 | 0.309 | 0.190 | 0.235 | 0.205 to 0.271 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.329 | 0.002 | 0.006 |
| all plans | 12 | 0.290 | 0.034 | 0.037 |
| all plans | 24 | 0.334 | 0.060 | 0.073 |
| state-reading plans | 1 | 0.407 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.291 | 0.035 | 0.037 |
| state-reading plans | 24 | 0.347 | 0.062 | 0.070 |
| open-loop plans | 1 | 0.305 | 0.000 | 0.007 |
| open-loop plans | 12 | 0.332 | 0.030 | 0.036 |
| open-loop plans | 24 | 0.351 | 0.046 | 0.082 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -341.80 |
| tile_cat | -42.28 |
| flags | -19.06 |
| power | -6.00 |
| half | -3575.46 |
| eighth | -63.34 |
| scalars_s2 | -5.68 |
| build_cost | -1.04 |
| scalars | -28.16 |
| ledger | -33.19 |
| bk | -55.68 |
| sc_res_pop | -1.63 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.20 |
| sc_powered_zones | -0.04 |
| sc_unpowered_zones | -0.07 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.56 |
| sc_res_valve | -1.46 |
| sc_com_valve | -3.09 |
| sc_ind_valve | -2.15 |
| sc_score | -5.85 |
| sc_funds | -3.12 |
| sc_tax_fund | -1.89 |
| sc_road_spend | -3.31 |
| sc_fire_spend | -0.86 |
| sc_police_spend | -0.77 |
| lg_sprite_cycle | -0.94 |
| lg_total_pop | -4.40 |
| lg_res_hist0 | -2.54 |
| lg_res_hist1 | -2.46 |
| lg_com_hist0 | -1.23 |
| lg_com_hist1 | -0.32 |
| lg_ind_hist0 | -0.88 |
| lg_ind_hist1 | -0.75 |
| lg_res_cap | -0.01 |
| lg_com_cap | -1.94 |
| lg_ind_cap | -0.02 |
| lg_need_hospital | -0.27 |
| lg_need_church | -0.17 |
| lg_road_fund | -1.75 |
| lg_police_fund | -0.29 |
| lg_fire_fund | -0.39 |
| lg_auto_budget | -0.05 |
| lg_fire_pop | -0.26 |
| lg_city_center_x | -0.29 |
| lg_city_center_y | -0.59 |
| lg_pollution_max_x | -4.85 |
| lg_pollution_max_y | -5.13 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -3.66 |
| terrain | -10.80 |
| com_rate | -10.93 |
| kl | 11.98 |
| elbo | -4144.04 |
