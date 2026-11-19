## os_100m_small_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.348 | 0.329 | 0.339 | 0.326 to 0.352 | 0.243 | 0.204 | 0.222 | 0.195 to 0.254 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.354 | 0.333 | 0.343 | 0.330 to 0.357 | 0.254 | 0.213 | 0.232 | 0.202 to 0.267 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.329 | 0.313 | 0.321 | 0.301 to 0.339 | 0.201 | 0.172 | 0.185 | 0.155 to 0.221 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.403 | 0.197 | 0.003 / 0.000 / 0.012 | 0.009 / 0.007 / 0.010 | 0.394 / 0.386 |
| all plans | 500 | 12 | 0.373 | 0.190 | 0.036 / 0.003 / 0.314 | 0.050 / 0.030 / 0.091 | 0.366 / 0.393 |
| all plans | 500 | 24 | 0.432 | 0.188 | 0.051 / 0.006 / 0.521 | 0.084 / 0.045 / 0.163 | 0.344 / 0.389 |
| state-reading plans | 393 | 1 | 0.418 | 0.217 | 0.005 / 0.000 / 0.018 | 0.009 / 0.007 / 0.010 | 0.430 / 0.422 |
| state-reading plans | 393 | 12 | 0.371 | 0.188 | 0.039 / 0.004 / 0.369 | 0.049 / 0.030 / 0.089 | 0.389 / 0.410 |
| state-reading plans | 393 | 24 | 0.443 | 0.191 | 0.058 / 0.006 / 0.714 | 0.080 / 0.046 / 0.154 | 0.361 / 0.399 |
| open-loop plans | 107 | 1 | 0.418 | 0.179 | 0.000 / 0.000 / 0.000 | 0.011 / 0.007 / 0.010 | 0.227 / 0.231 |
| open-loop plans | 107 | 12 | 0.428 | 0.229 | 0.022 / 0.003 / 0.111 | 0.055 / 0.033 / 0.120 | 0.271 / 0.324 |
| open-loop plans | 107 | 24 | 0.481 | 0.222 | 0.028 / 0.005 / 0.164 | 0.106 / 0.044 / 0.212 | 0.277 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.2217 | 0.952 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3385 | 0.991 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2184.9750 | 0.655 |
| funds_mae_12m | 4895.7120 | 42.3740 | 578.8220 | 0.889 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 254.6258 | 0.840 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 522.1100 | 0.826 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 379.0370 | 0.837 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0496 | 0.679 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0358 | 0.896 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3660 | 0.931 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3723 | 0.923 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 3788.6900 | 0.648 |
| funds_mae_24m | 6681.5280 | 66.8000 | 674.6605 | 0.908 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 346.3350 | 0.762 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 712.9977 | 0.672 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 572.5852 | 0.718 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0844 | 0.667 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0507 | 0.913 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.3442 | 0.886 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.3465 | 0.884 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 674.7 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 346.3 | 218.6 | 754.9 |
| com_valve | 713.0 | 492.3 | 1165.4 |
| ind_valve | 572.6 | 371.1 | 1086.8 |
| pop | 3788.7 | 1875.9 | 7303.8 |
| res_pop | 76.5 | 44.7 | 158.4 |
| com_pop | 7.8 | 5.2 | 13.9 |
| ind_pop | 11.9 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 55.5 | 27.9 | 107.4 |
| tax_fund | 137.6 | 54.7 | 1326.7 |
| road_spend | 57.2 | 11.9 | 835.4 |
| fire_spend | 34.5 | 2.6 | 431.3 |
| police_spend | 59.9 | 3.8 | 545.1 |
| powered_zones | 6.9 | 2.8 | 10.6 |
| unpowered_zones | 5.9 | 2.6 | 8.5 |
| coal_plants | 0.1 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 57.7 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 672.7 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 300.7 | 160.2 | 525.9 |
| com_valve | 756.6 | 495.6 | 1123.2 |
| ind_valve | 641.0 | 397.1 | 1024.3 |
| pop | 3722.9 | 1889.8 | 6800.2 |
| res_pop | 75.2 | 44.3 | 148.6 |
| com_pop | 7.4 | 5.1 | 12.6 |
| ind_pop | 11.9 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 56.8 | 27.1 | 100.2 |
| tax_fund | 123.5 | 50.6 | 1281.6 |
| road_spend | 52.1 | 11.6 | 824.6 |
| fire_spend | 31.9 | 3.0 | 413.3 |
| police_spend | 60.0 | 3.5 | 516.9 |
| powered_zones | 7.2 | 2.5 | 12.5 |
| unpowered_zones | 6.1 | 2.4 | 9.0 |
| coal_plants | 0.1 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 56.3 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 681.7 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 513.8 | 433.2 | 1596.0 |
| com_valve | 552.8 | 480.1 | 1320.4 |
| ind_valve | 321.4 | 275.6 | 1316.6 |
| pop | 4030.2 | 1825.0 | 9153.8 |
| res_pop | 81.3 | 46.2 | 194.5 |
| com_pop | 9.1 | 5.4 | 18.4 |
| ind_pop | 12.0 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 50.6 | 30.9 | 133.7 |
| tax_fund | 189.3 | 69.9 | 1492.4 |
| road_spend | 75.8 | 13.0 | 875.0 |
| fire_spend | 44.3 | 0.9 | 497.3 |
| police_spend | 59.3 | 4.7 | 648.6 |
| powered_zones | 5.6 | 3.8 | 3.7 |
| unpowered_zones | 4.9 | 3.2 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.1 | 0.0 | 0.2 |
| road_total | 62.7 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 0.984 | 0.858 |
| traffic | 0.875 | 0.787 |
| pollution | 1.460 | 0.738 |
| land_value | 0.631 | 0.398 |
| crime | 1.000 | 0.597 |
| rate_of_growth | 1.024 | 0.852 |
| fire_coverage | 0.700 | 0.146 |
| police_coverage | 0.716 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.441 | 0.322 | 0.372 | 0.358 to 0.386 | 0.298 | 0.186 | 0.229 | 0.198 to 0.265 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.321 | 0.002 | 0.007 |
| all plans | 12 | 0.299 | 0.028 | 0.042 |
| all plans | 24 | 0.352 | 0.048 | 0.074 |
| state-reading plans | 1 | 0.332 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.296 | 0.029 | 0.041 |
| state-reading plans | 24 | 0.361 | 0.050 | 0.069 |
| open-loop plans | 1 | 0.345 | 0.000 | 0.008 |
| open-loop plans | 12 | 0.350 | 0.022 | 0.045 |
| open-loop plans | 24 | 0.390 | 0.040 | 0.109 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -389.56 |
| tile_cat | -46.05 |
| flags | -20.48 |
| power | -6.68 |
| half | -3729.56 |
| eighth | -75.18 |
| scalars_s2 | -5.67 |
| build_cost | -1.04 |
| scalars | -28.04 |
| ledger | -36.22 |
| bk | -58.59 |
| sc_res_pop | -1.65 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.20 |
| sc_powered_zones | -0.04 |
| sc_unpowered_zones | -0.09 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.52 |
| sc_res_valve | -1.62 |
| sc_com_valve | -3.05 |
| sc_ind_valve | -2.27 |
| sc_score | -5.49 |
| sc_funds | -2.80 |
| sc_tax_fund | -2.86 |
| sc_road_spend | -3.27 |
| sc_fire_spend | -0.58 |
| sc_police_spend | -0.44 |
| lg_sprite_cycle | -1.05 |
| lg_total_pop | -2.84 |
| lg_res_hist0 | -2.71 |
| lg_res_hist1 | -3.32 |
| lg_com_hist0 | -1.52 |
| lg_com_hist1 | -0.55 |
| lg_ind_hist0 | -2.16 |
| lg_ind_hist1 | -1.05 |
| lg_res_cap | -0.05 |
| lg_com_cap | -0.07 |
| lg_ind_cap | -0.02 |
| lg_need_hospital | -0.79 |
| lg_need_church | -0.70 |
| lg_road_fund | -1.67 |
| lg_police_fund | -0.30 |
| lg_fire_fund | -0.50 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.47 |
| lg_city_center_x | -0.63 |
| lg_city_center_y | -1.40 |
| lg_pollution_max_x | -5.19 |
| lg_pollution_max_y | -5.29 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -3.88 |
| terrain | -10.78 |
| com_rate | -13.50 |
| kl | 13.67 |
| elbo | -4370.77 |
