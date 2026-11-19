## os_50m_cov_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "03e254f7493d9a36", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.337 | 0.315 | 0.326 | 0.313 to 0.339 | 0.233 | 0.202 | 0.217 | 0.190 to 0.248 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.342 | 0.320 | 0.331 | 0.318 to 0.345 | 0.245 | 0.211 | 0.227 | 0.197 to 0.263 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.315 | 0.298 | 0.306 | 0.288 to 0.325 | 0.190 | 0.168 | 0.178 | 0.149 to 0.213 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.424 | 0.197 | 0.006 / 0.000 / 0.012 | 0.010 / 0.007 / 0.010 | 0.388 / 0.386 |
| all plans | 500 | 12 | 0.365 | 0.190 | 0.067 / 0.003 / 0.314 | 0.049 / 0.030 / 0.091 | 0.356 / 0.393 |
| all plans | 500 | 24 | 0.434 | 0.188 | 0.121 / 0.006 / 0.521 | 0.086 / 0.045 / 0.163 | 0.332 / 0.389 |
| state-reading plans | 393 | 1 | 0.445 | 0.217 | 0.009 / 0.000 / 0.018 | 0.010 / 0.007 / 0.010 | 0.423 / 0.422 |
| state-reading plans | 393 | 12 | 0.367 | 0.188 | 0.074 / 0.004 / 0.369 | 0.048 / 0.030 / 0.089 | 0.376 / 0.410 |
| state-reading plans | 393 | 24 | 0.446 | 0.191 | 0.138 / 0.006 / 0.714 | 0.085 / 0.046 / 0.154 | 0.346 / 0.399 |
| open-loop plans | 107 | 1 | 0.423 | 0.179 | 0.000 / 0.000 / 0.000 | 0.010 / 0.007 / 0.010 | 0.230 / 0.231 |
| open-loop plans | 107 | 12 | 0.414 | 0.229 | 0.041 / 0.003 / 0.111 | 0.049 / 0.033 / 0.120 | 0.271 / 0.324 |
| open-loop plans | 107 | 24 | 0.480 | 0.222 | 0.069 / 0.005 / 0.164 | 0.093 / 0.044 / 0.212 | 0.276 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.2165 | 0.930 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3257 | 0.953 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2128.3600 | 0.675 |
| funds_mae_12m | 4895.7120 | 42.3740 | 897.1975 | 0.824 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 247.4565 | 0.852 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 515.2215 | 0.834 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 379.2618 | 0.837 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0489 | 0.692 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0669 | 0.796 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3557 | 0.905 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3623 | 0.898 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 3750.8250 | 0.655 |
| funds_mae_24m | 6681.5280 | 66.8000 | 1297.0418 | 0.814 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 329.2715 | 0.794 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 690.2565 | 0.706 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 534.0507 | 0.772 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0862 | 0.651 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.1210 | 0.776 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.3320 | 0.854 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.3347 | 0.854 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1297.0 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 329.3 | 218.6 | 754.9 |
| com_valve | 690.3 | 492.3 | 1165.4 |
| ind_valve | 534.1 | 371.1 | 1086.8 |
| pop | 3750.8 | 1875.9 | 7303.8 |
| res_pop | 80.6 | 44.7 | 158.4 |
| com_pop | 8.0 | 5.2 | 13.9 |
| ind_pop | 10.5 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 65.7 | 27.9 | 107.4 |
| tax_fund | 115.7 | 54.7 | 1326.7 |
| road_spend | 58.2 | 11.9 | 835.4 |
| fire_spend | 40.9 | 2.6 | 431.3 |
| police_spend | 55.4 | 3.8 | 545.1 |
| powered_zones | 7.5 | 2.8 | 10.6 |
| unpowered_zones | 6.0 | 2.6 | 8.5 |
| coal_plants | 0.1 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 57.8 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1322.5 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 273.5 | 160.2 | 525.9 |
| com_valve | 722.7 | 495.6 | 1123.2 |
| ind_valve | 588.8 | 397.1 | 1024.3 |
| pop | 3752.6 | 1889.8 | 6800.2 |
| res_pop | 80.7 | 44.3 | 148.6 |
| com_pop | 7.9 | 5.1 | 12.6 |
| ind_pop | 10.5 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 67.2 | 27.1 | 100.2 |
| tax_fund | 111.1 | 50.6 | 1281.6 |
| road_spend | 56.8 | 11.6 | 824.6 |
| fire_spend | 37.6 | 3.0 | 413.3 |
| police_spend | 56.2 | 3.5 | 516.9 |
| powered_zones | 7.9 | 2.5 | 12.5 |
| unpowered_zones | 6.3 | 2.4 | 9.0 |
| coal_plants | 0.1 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 57.0 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1203.6 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 534.1 | 433.2 | 1596.0 |
| com_valve | 571.2 | 480.1 | 1320.4 |
| ind_valve | 332.8 | 275.6 | 1316.6 |
| pop | 3744.4 | 1825.0 | 9153.8 |
| res_pop | 80.1 | 46.2 | 194.5 |
| com_pop | 8.4 | 5.4 | 18.4 |
| ind_pop | 10.4 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 60.3 | 30.9 | 133.7 |
| tax_fund | 132.7 | 69.9 | 1492.4 |
| road_spend | 63.5 | 13.0 | 875.0 |
| fire_spend | 53.0 | 0.9 | 497.3 |
| police_spend | 52.1 | 4.7 | 648.6 |
| powered_zones | 6.2 | 3.8 | 3.7 |
| unpowered_zones | 4.9 | 3.2 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.1 | 0.0 | 0.2 |
| road_total | 60.4 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.038 | 0.858 |
| traffic | 0.952 | 0.787 |
| pollution | 1.665 | 0.738 |
| land_value | 0.638 | 0.398 |
| crime | 1.048 | 0.597 |
| rate_of_growth | 0.985 | 0.852 |
| fire_coverage | 1.167 | 0.146 |
| police_coverage | 0.925 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.595 | 0.298 | 0.397 | 0.383 to 0.410 | 0.505 | 0.175 | 0.260 | 0.224 to 0.299 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.327 | 0.004 | 0.006 |
| all plans | 12 | 0.288 | 0.074 | 0.041 |
| all plans | 24 | 0.352 | 0.131 | 0.074 |
| state-reading plans | 1 | 0.341 | 0.005 | 0.006 |
| state-reading plans | 12 | 0.288 | 0.082 | 0.041 |
| state-reading plans | 24 | 0.363 | 0.151 | 0.072 |
| open-loop plans | 1 | 0.339 | 0.000 | 0.007 |
| open-loop plans | 12 | 0.330 | 0.047 | 0.043 |
| open-loop plans | 24 | 0.386 | 0.090 | 0.082 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -258.90 |
| tile_cat | -35.55 |
| flags | -16.36 |
| power | -2.75 |
| half | -3135.88 |
| eighth | -43.76 |
| scalars_s2 | -5.54 |
| build_cost | -1.27 |
| scalars | -11.43 |
| ledger | -9.16 |
| bk | -15.04 |
| sc_res_pop | -1.60 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.54 |
| sc_res_valve | -1.07 |
| sc_com_valve | -2.08 |
| sc_ind_valve | -0.99 |
| sc_score | -0.28 |
| sc_funds | -0.73 |
| sc_tax_fund | -0.37 |
| sc_road_spend | -0.23 |
| sc_fire_spend | -0.07 |
| sc_police_spend | -0.07 |
| lg_sprite_cycle | -0.37 |
| lg_total_pop | -1.46 |
| lg_res_hist0 | -0.46 |
| lg_res_hist1 | -0.05 |
| lg_com_hist0 | -0.31 |
| lg_com_hist1 | -0.01 |
| lg_ind_hist0 | -0.29 |
| lg_ind_hist1 | -0.05 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.05 |
| lg_road_fund | -0.22 |
| lg_police_fund | -0.03 |
| lg_fire_fund | -0.04 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.01 |
| lg_pollution_max_x | -1.87 |
| lg_pollution_max_y | -1.55 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.24 |
| terrain | -7.88 |
| com_rate | -1.73 |
| kl | 14.52 |
| elbo | -3539.17 |
