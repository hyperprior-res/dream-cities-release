## sf_100m_full_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.309 | 0.320 | 0.314 | 0.301 to 0.328 | 0.197 | 0.209 | 0.203 | 0.179 to 0.232 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.314 | 0.325 | 0.319 | 0.306 to 0.334 | 0.207 | 0.218 | 0.213 | 0.185 to 0.247 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.287 | 0.304 | 0.295 | 0.276 to 0.312 | 0.160 | 0.175 | 0.167 | 0.139 to 0.199 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.404 | 0.197 | 0.001 / 0.000 / 0.012 | 0.010 / 0.007 / 0.010 | 0.380 / 0.386 |
| all plans | 500 | 12 | 0.392 | 0.190 | 0.028 / 0.003 / 0.314 | 0.049 / 0.030 / 0.091 | 0.326 / 0.393 |
| all plans | 500 | 24 | 0.483 | 0.188 | 0.063 / 0.006 / 0.521 | 0.086 / 0.045 / 0.163 | 0.301 / 0.389 |
| state-reading plans | 393 | 1 | 0.460 | 0.217 | 0.002 / 0.000 / 0.018 | 0.010 / 0.007 / 0.010 | 0.414 / 0.422 |
| state-reading plans | 393 | 12 | 0.387 | 0.188 | 0.028 / 0.004 / 0.369 | 0.048 / 0.030 / 0.089 | 0.345 / 0.410 |
| state-reading plans | 393 | 24 | 0.484 | 0.191 | 0.066 / 0.006 / 0.714 | 0.084 / 0.046 / 0.154 | 0.316 / 0.399 |
| open-loop plans | 107 | 1 | 0.392 | 0.179 | 0.000 / 0.000 / 0.000 | 0.009 / 0.007 / 0.010 | 0.224 / 0.231 |
| open-loop plans | 107 | 12 | 0.479 | 0.229 | 0.024 / 0.003 / 0.111 | 0.051 / 0.033 / 0.120 | 0.250 / 0.324 |
| open-loop plans | 107 | 24 | 0.589 | 0.222 | 0.052 / 0.005 / 0.164 | 0.098 / 0.044 / 0.212 | 0.242 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.2029 | 0.872 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3144 | 0.920 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2015.4300 | 0.714 |
| funds_mae_12m | 4895.7120 | 42.3740 | 525.5440 | 0.900 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 230.3918 | 0.883 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 527.9100 | 0.819 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 368.5433 | 0.851 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0489 | 0.692 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0277 | 0.922 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3257 | 0.828 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3388 | 0.840 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 3809.6900 | 0.644 |
| funds_mae_24m | 6681.5280 | 66.8000 | 782.2002 | 0.892 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 344.3168 | 0.766 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 670.3523 | 0.735 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 502.5057 | 0.816 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0863 | 0.651 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0629 | 0.889 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.3007 | 0.773 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.3077 | 0.785 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 782.2 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 344.3 | 218.6 | 754.9 |
| com_valve | 670.4 | 492.3 | 1165.4 |
| ind_valve | 502.5 | 371.1 | 1086.8 |
| pop | 3809.7 | 1875.9 | 7303.8 |
| res_pop | 93.0 | 44.7 | 158.4 |
| com_pop | 7.8 | 5.2 | 13.9 |
| ind_pop | 10.6 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 58.3 | 27.9 | 107.4 |
| tax_fund | 105.3 | 54.7 | 1326.7 |
| road_spend | 56.7 | 11.9 | 835.4 |
| fire_spend | 30.2 | 2.6 | 431.3 |
| police_spend | 40.7 | 3.8 | 545.1 |
| powered_zones | 7.8 | 2.8 | 10.6 |
| unpowered_zones | 6.5 | 2.6 | 8.5 |
| coal_plants | 0.2 | 0.0 | 0.4 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 61.4 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 751.6 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 269.3 | 160.2 | 525.9 |
| com_valve | 696.1 | 495.6 | 1123.2 |
| ind_valve | 546.9 | 397.1 | 1024.3 |
| pop | 3803.1 | 1889.8 | 6800.2 |
| res_pop | 90.6 | 44.3 | 148.6 |
| com_pop | 7.7 | 5.1 | 12.6 |
| ind_pop | 10.6 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 59.9 | 27.1 | 100.2 |
| tax_fund | 102.7 | 50.6 | 1281.6 |
| road_spend | 54.7 | 11.6 | 824.6 |
| fire_spend | 29.1 | 3.0 | 413.3 |
| police_spend | 39.7 | 3.5 | 516.9 |
| powered_zones | 8.1 | 2.5 | 12.5 |
| unpowered_zones | 6.7 | 2.4 | 9.0 |
| coal_plants | 0.3 | 0.0 | 0.4 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 60.0 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 894.6 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 619.7 | 433.2 | 1596.0 |
| com_valve | 575.9 | 480.1 | 1320.4 |
| ind_valve | 339.6 | 275.6 | 1316.6 |
| pop | 3834.0 | 1825.0 | 9153.8 |
| res_pop | 102.0 | 46.2 | 194.5 |
| com_pop | 8.3 | 5.4 | 18.4 |
| ind_pop | 10.3 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 52.2 | 30.9 | 133.7 |
| tax_fund | 115.1 | 69.9 | 1492.4 |
| road_spend | 64.0 | 13.0 | 875.0 |
| fire_spend | 34.3 | 0.9 | 497.3 |
| police_spend | 44.4 | 4.7 | 648.6 |
| powered_zones | 6.6 | 3.8 | 3.7 |
| unpowered_zones | 5.8 | 3.2 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 66.5 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.180 | 0.858 |
| traffic | 0.885 | 0.787 |
| pollution | 1.761 | 0.738 |
| land_value | 0.679 | 0.398 |
| crime | 1.118 | 0.597 |
| rate_of_growth | 1.139 | 0.852 |
| fire_coverage | 0.868 | 0.146 |
| police_coverage | 0.739 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.593 | 0.300 | 0.398 | 0.384 to 0.412 | 0.498 | 0.177 | 0.261 | 0.226 to 0.299 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.302 | 0.001 | 0.007 |
| all plans | 12 | 0.293 | 0.027 | 0.037 |
| all plans | 24 | 0.367 | 0.071 | 0.078 |
| state-reading plans | 1 | 0.321 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.287 | 0.028 | 0.034 |
| state-reading plans | 24 | 0.369 | 0.077 | 0.074 |
| open-loop plans | 1 | 0.313 | 0.000 | 0.008 |
| open-loop plans | 12 | 0.366 | 0.023 | 0.043 |
| open-loop plans | 24 | 0.446 | 0.065 | 0.092 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -253.81 |
| tile_cat | -35.56 |
| flags | -16.66 |
| power | -3.48 |
| half | -3076.47 |
| eighth | -42.17 |
| scalars_s2 | -5.53 |
| build_cost | -0.92 |
| scalars | -11.52 |
| ledger | -9.05 |
| bk | -15.04 |
| sc_res_pop | -1.59 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.04 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.55 |
| sc_res_valve | -1.06 |
| sc_com_valve | -2.07 |
| sc_ind_valve | -0.98 |
| sc_score | -0.28 |
| sc_funds | -0.78 |
| sc_tax_fund | -0.38 |
| sc_road_spend | -0.26 |
| sc_fire_spend | -0.09 |
| sc_police_spend | -0.08 |
| lg_sprite_cycle | -0.40 |
| lg_total_pop | -1.34 |
| lg_res_hist0 | -0.44 |
| lg_res_hist1 | -0.04 |
| lg_com_hist0 | -0.30 |
| lg_com_hist1 | -0.00 |
| lg_ind_hist0 | -0.29 |
| lg_ind_hist1 | -0.01 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.05 |
| lg_road_fund | -0.25 |
| lg_police_fund | -0.05 |
| lg_fire_fund | -0.05 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -1.84 |
| lg_pollution_max_y | -1.56 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.25 |
| terrain | -8.30 |
| com_rate | -2.13 |
| kl | 16.32 |
| elbo | -3476.41 |
