## os_50m_full_s1_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.336 | 0.316 | 0.326 | 0.313 to 0.339 | 0.231 | 0.202 | 0.216 | 0.190 to 0.247 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.339 | 0.320 | 0.329 | 0.316 to 0.343 | 0.240 | 0.212 | 0.225 | 0.195 to 0.260 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.324 | 0.299 | 0.311 | 0.292 to 0.328 | 0.200 | 0.168 | 0.182 | 0.151 to 0.219 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.378 | 0.197 | 0.003 / 0.000 / 0.012 | 0.010 / 0.007 / 0.010 | 0.388 / 0.386 |
| all plans | 500 | 12 | 0.393 | 0.190 | 0.034 / 0.003 / 0.314 | 0.047 / 0.030 / 0.091 | 0.360 / 0.393 |
| all plans | 500 | 24 | 0.460 | 0.188 | 0.061 / 0.006 / 0.521 | 0.078 / 0.045 / 0.163 | 0.341 / 0.389 |
| state-reading plans | 393 | 1 | 0.403 | 0.217 | 0.005 / 0.000 / 0.018 | 0.010 / 0.007 / 0.010 | 0.422 / 0.422 |
| state-reading plans | 393 | 12 | 0.402 | 0.188 | 0.037 / 0.004 / 0.369 | 0.045 / 0.030 / 0.089 | 0.382 / 0.410 |
| state-reading plans | 393 | 24 | 0.490 | 0.191 | 0.065 / 0.006 / 0.714 | 0.075 / 0.046 / 0.154 | 0.356 / 0.399 |
| open-loop plans | 107 | 1 | 0.379 | 0.179 | 0.000 / 0.000 / 0.000 | 0.010 / 0.007 / 0.010 | 0.233 / 0.231 |
| open-loop plans | 107 | 12 | 0.416 | 0.229 | 0.023 / 0.003 / 0.111 | 0.053 / 0.033 / 0.120 | 0.272 / 0.324 |
| open-loop plans | 107 | 24 | 0.447 | 0.222 | 0.043 / 0.005 / 0.164 | 0.091 / 0.044 / 0.212 | 0.281 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.2158 | 0.927 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3255 | 0.953 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2015.5050 | 0.714 |
| funds_mae_12m | 4895.7120 | 42.3740 | 500.4505 | 0.906 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 253.4485 | 0.842 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 531.9797 | 0.814 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 389.1355 | 0.824 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0470 | 0.722 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0337 | 0.903 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3604 | 0.917 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3685 | 0.913 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 3460.5900 | 0.708 |
| funds_mae_24m | 6681.5280 | 66.8000 | 704.3570 | 0.904 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 328.0133 | 0.796 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 689.4322 | 0.707 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 555.1377 | 0.743 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0780 | 0.721 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0607 | 0.893 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.3410 | 0.877 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.3445 | 0.879 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 704.4 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 328.0 | 218.6 | 754.9 |
| com_valve | 689.4 | 492.3 | 1165.4 |
| ind_valve | 555.1 | 371.1 | 1086.8 |
| pop | 3460.6 | 1875.9 | 7303.8 |
| res_pop | 71.4 | 44.7 | 158.4 |
| com_pop | 7.6 | 5.2 | 13.9 |
| ind_pop | 10.5 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 51.1 | 27.9 | 107.4 |
| tax_fund | 117.2 | 54.7 | 1326.7 |
| road_spend | 49.2 | 11.9 | 835.4 |
| fire_spend | 44.5 | 2.6 | 431.3 |
| police_spend | 528.5 | 3.8 | 545.1 |
| powered_zones | 6.6 | 2.8 | 10.6 |
| unpowered_zones | 5.7 | 2.6 | 8.5 |
| coal_plants | 0.1 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 55.8 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 699.3 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 277.3 | 160.2 | 525.9 |
| com_valve | 726.5 | 495.6 | 1123.2 |
| ind_valve | 618.6 | 397.1 | 1024.3 |
| pop | 3418.0 | 1889.8 | 6800.2 |
| res_pop | 71.2 | 44.3 | 148.6 |
| com_pop | 7.5 | 5.1 | 12.6 |
| ind_pop | 10.5 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 52.6 | 27.1 | 100.2 |
| tax_fund | 109.1 | 50.6 | 1281.6 |
| road_spend | 47.9 | 11.6 | 824.6 |
| fire_spend | 46.0 | 3.0 | 413.3 |
| police_spend | 660.5 | 3.5 | 516.9 |
| powered_zones | 7.0 | 2.5 | 12.5 |
| unpowered_zones | 5.9 | 2.4 | 9.0 |
| coal_plants | 0.2 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 55.8 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 723.0 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 514.1 | 433.2 | 1596.0 |
| com_valve | 553.2 | 480.1 | 1320.4 |
| ind_valve | 322.2 | 275.6 | 1316.6 |
| pop | 3616.8 | 1825.0 | 9153.8 |
| res_pop | 71.9 | 46.2 | 194.5 |
| com_pop | 8.0 | 5.4 | 18.4 |
| ind_pop | 10.9 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 45.3 | 30.9 | 133.7 |
| tax_fund | 146.8 | 69.9 | 1492.4 |
| road_spend | 53.9 | 13.0 | 875.0 |
| fire_spend | 38.8 | 0.9 | 497.3 |
| police_spend | 43.3 | 4.7 | 648.6 |
| powered_zones | 5.2 | 3.8 | 3.7 |
| unpowered_zones | 4.7 | 3.2 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.1 | 0.0 | 0.2 |
| road_total | 55.8 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.005 | 0.858 |
| traffic | 0.886 | 0.787 |
| pollution | 1.447 | 0.738 |
| land_value | 0.589 | 0.398 |
| crime | 0.964 | 0.597 |
| rate_of_growth | 0.981 | 0.852 |
| fire_coverage | 0.780 | 0.146 |
| police_coverage | 0.604 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.579 | 0.296 | 0.392 | 0.377 to 0.406 | 0.460 | 0.174 | 0.252 | 0.217 to 0.290 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.288 | 0.002 | 0.006 |
| all plans | 12 | 0.311 | 0.028 | 0.036 |
| all plans | 24 | 0.374 | 0.062 | 0.069 |
| state-reading plans | 1 | 0.306 | 0.003 | 0.006 |
| state-reading plans | 12 | 0.317 | 0.029 | 0.034 |
| state-reading plans | 24 | 0.402 | 0.071 | 0.065 |
| open-loop plans | 1 | 0.302 | 0.000 | 0.008 |
| open-loop plans | 12 | 0.337 | 0.027 | 0.044 |
| open-loop plans | 24 | 0.353 | 0.054 | 0.079 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -255.56 |
| tile_cat | -35.13 |
| flags | -16.96 |
| power | -3.66 |
| half | -3143.90 |
| eighth | -43.10 |
| scalars_s2 | -5.53 |
| build_cost | -1.03 |
| scalars | -11.34 |
| ledger | -9.24 |
| bk | -15.05 |
| sc_res_pop | -1.59 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.04 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.55 |
| sc_res_valve | -1.06 |
| sc_com_valve | -2.07 |
| sc_ind_valve | -0.96 |
| sc_score | -0.27 |
| sc_funds | -0.69 |
| sc_tax_fund | -0.37 |
| sc_road_spend | -0.23 |
| sc_fire_spend | -0.07 |
| sc_police_spend | -0.08 |
| lg_sprite_cycle | -0.45 |
| lg_total_pop | -1.41 |
| lg_res_hist0 | -0.45 |
| lg_res_hist1 | -0.05 |
| lg_com_hist0 | -0.31 |
| lg_com_hist1 | -0.00 |
| lg_ind_hist0 | -0.29 |
| lg_ind_hist1 | -0.03 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.05 |
| lg_road_fund | -0.23 |
| lg_police_fund | -0.04 |
| lg_fire_fund | -0.03 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -1.84 |
| lg_pollution_max_y | -1.62 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.24 |
| terrain | -8.28 |
| com_rate | -3.88 |
| kl | 15.66 |
| elbo | -3547.73 |
