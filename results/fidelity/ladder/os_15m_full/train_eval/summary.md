## os_15m_full_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.329 | 0.312 | 0.320 | 0.308 to 0.333 | 0.221 | 0.194 | 0.207 | 0.182 to 0.236 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.334 | 0.317 | 0.325 | 0.313 to 0.338 | 0.232 | 0.203 | 0.217 | 0.188 to 0.249 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.311 | 0.295 | 0.303 | 0.284 to 0.320 | 0.182 | 0.158 | 0.169 | 0.141 to 0.201 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.411 | 0.197 | 0.004 / 0.000 / 0.012 | 0.010 / 0.007 / 0.010 | 0.368 / 0.386 |
| all plans | 500 | 12 | 0.387 | 0.190 | 0.047 / 0.003 / 0.314 | 0.048 / 0.030 / 0.091 | 0.349 / 0.393 |
| all plans | 500 | 24 | 0.545 | 0.188 | 0.088 / 0.006 / 0.521 | 0.080 / 0.045 / 0.163 | 0.333 / 0.389 |
| state-reading plans | 393 | 1 | 0.417 | 0.217 | 0.006 / 0.000 / 0.018 | 0.010 / 0.007 / 0.010 | 0.404 / 0.422 |
| state-reading plans | 393 | 12 | 0.385 | 0.188 | 0.049 / 0.004 / 0.369 | 0.046 / 0.030 / 0.089 | 0.370 / 0.410 |
| state-reading plans | 393 | 24 | 0.585 | 0.191 | 0.092 / 0.006 / 0.714 | 0.076 / 0.046 / 0.154 | 0.348 / 0.399 |
| open-loop plans | 107 | 1 | 0.427 | 0.179 | 0.000 / 0.000 / 0.000 | 0.010 / 0.007 / 0.010 | 0.206 / 0.231 |
| open-loop plans | 107 | 12 | 0.453 | 0.229 | 0.038 / 0.003 / 0.111 | 0.054 / 0.033 / 0.120 | 0.260 / 0.324 |
| open-loop plans | 107 | 24 | 0.523 | 0.222 | 0.071 / 0.005 / 0.164 | 0.102 / 0.044 / 0.212 | 0.271 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.2065 | 0.887 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3203 | 0.938 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2054.4000 | 0.701 |
| funds_mae_12m | 4895.7120 | 42.3740 | 679.8388 | 0.869 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 251.3377 | 0.846 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 565.7575 | 0.774 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 380.1530 | 0.835 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0478 | 0.710 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0474 | 0.859 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3489 | 0.887 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3605 | 0.893 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 3478.3100 | 0.705 |
| funds_mae_24m | 6681.5280 | 66.8000 | 1008.8755 | 0.858 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 311.3320 | 0.827 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 808.4480 | 0.530 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 561.6890 | 0.734 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0803 | 0.702 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0884 | 0.839 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.3329 | 0.856 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.3381 | 0.863 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1008.9 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 311.3 | 218.6 | 754.9 |
| com_valve | 808.4 | 492.3 | 1165.4 |
| ind_valve | 561.7 | 371.1 | 1086.8 |
| pop | 3478.3 | 1875.9 | 7303.8 |
| res_pop | 70.2 | 44.7 | 158.4 |
| com_pop | 8.8 | 5.2 | 13.9 |
| ind_pop | 10.9 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 53.8 | 27.9 | 107.4 |
| tax_fund | 130.4 | 54.7 | 1326.7 |
| road_spend | 59.1 | 11.9 | 835.4 |
| fire_spend | 31.4 | 2.6 | 431.3 |
| police_spend | 1020.6 | 3.8 | 545.1 |
| powered_zones | 7.5 | 2.8 | 10.6 |
| unpowered_zones | 6.5 | 2.6 | 8.5 |
| coal_plants | 0.2 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 62.2 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 950.3 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 254.8 | 160.2 | 525.9 |
| com_valve | 869.7 | 495.6 | 1123.2 |
| ind_valve | 622.9 | 397.1 | 1024.3 |
| pop | 3349.2 | 1889.8 | 6800.2 |
| res_pop | 68.5 | 44.3 | 148.6 |
| com_pop | 8.4 | 5.1 | 12.6 |
| ind_pop | 10.8 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 54.6 | 27.1 | 100.2 |
| tax_fund | 134.2 | 50.6 | 1281.6 |
| road_spend | 55.8 | 11.6 | 824.6 |
| fire_spend | 31.6 | 3.0 | 413.3 |
| police_spend | 1286.8 | 3.5 | 516.9 |
| powered_zones | 7.7 | 2.5 | 12.5 |
| unpowered_zones | 6.6 | 2.4 | 9.0 |
| coal_plants | 0.2 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 61.6 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1224.1 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 519.0 | 433.2 | 1596.0 |
| com_valve | 583.5 | 480.1 | 1320.4 |
| ind_valve | 336.8 | 275.6 | 1316.6 |
| pop | 3952.7 | 1825.0 | 9153.8 |
| res_pop | 76.4 | 46.2 | 194.5 |
| com_pop | 10.4 | 5.4 | 18.4 |
| ind_pop | 11.1 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 50.9 | 30.9 | 133.7 |
| tax_fund | 116.7 | 69.9 | 1492.4 |
| road_spend | 71.6 | 13.0 | 875.0 |
| fire_spend | 30.5 | 0.9 | 497.3 |
| police_spend | 43.1 | 4.7 | 648.6 |
| powered_zones | 6.7 | 3.8 | 3.7 |
| unpowered_zones | 6.0 | 3.2 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.1 | 0.0 | 0.2 |
| road_total | 64.6 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.009 | 0.858 |
| traffic | 0.927 | 0.787 |
| pollution | 1.619 | 0.738 |
| land_value | 0.599 | 0.398 |
| crime | 1.013 | 0.597 |
| rate_of_growth | 1.014 | 0.852 |
| fire_coverage | 0.898 | 0.146 |
| police_coverage | 0.640 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.641 | 0.290 | 0.399 | 0.385 to 0.414 | 0.656 | 0.154 | 0.250 | 0.213 to 0.292 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.313 | 0.002 | 0.007 |
| all plans | 12 | 0.299 | 0.052 | 0.039 |
| all plans | 24 | 0.455 | 0.107 | 0.070 |
| state-reading plans | 1 | 0.304 | 0.003 | 0.007 |
| state-reading plans | 12 | 0.294 | 0.052 | 0.037 |
| state-reading plans | 24 | 0.491 | 0.115 | 0.066 |
| open-loop plans | 1 | 0.344 | 0.001 | 0.007 |
| open-loop plans | 12 | 0.374 | 0.050 | 0.053 |
| open-loop plans | 24 | 0.433 | 0.091 | 0.101 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -266.46 |
| tile_cat | -37.28 |
| flags | -16.99 |
| power | -3.61 |
| half | -3269.62 |
| eighth | -45.95 |
| scalars_s2 | -5.55 |
| build_cost | -1.03 |
| scalars | -11.38 |
| ledger | -9.62 |
| bk | -15.45 |
| sc_res_pop | -1.59 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.04 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.54 |
| sc_res_valve | -1.08 |
| sc_com_valve | -2.07 |
| sc_ind_valve | -0.98 |
| sc_score | -0.28 |
| sc_funds | -0.69 |
| sc_tax_fund | -0.37 |
| sc_road_spend | -0.23 |
| sc_fire_spend | -0.07 |
| sc_police_spend | -0.07 |
| lg_sprite_cycle | -0.57 |
| lg_total_pop | -1.49 |
| lg_res_hist0 | -0.47 |
| lg_res_hist1 | -0.05 |
| lg_com_hist0 | -0.31 |
| lg_com_hist1 | -0.01 |
| lg_ind_hist0 | -0.29 |
| lg_ind_hist1 | -0.04 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.05 |
| lg_road_fund | -0.22 |
| lg_police_fund | -0.04 |
| lg_fire_fund | -0.03 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -1.93 |
| lg_pollution_max_y | -1.69 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.24 |
| terrain | -9.35 |
| com_rate | -5.21 |
| kl | 12.17 |
| elbo | -3688.67 |
