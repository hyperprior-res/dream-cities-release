## sf_50m_small_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.279 | 0.329 | 0.302 | 0.288 to 0.315 | 0.168 | 0.219 | 0.190 | 0.169 to 0.217 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.284 | 0.333 | 0.306 | 0.293 to 0.321 | 0.176 | 0.230 | 0.200 | 0.174 to 0.229 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.261 | 0.310 | 0.283 | 0.266 to 0.301 | 0.137 | 0.180 | 0.156 | 0.131 to 0.184 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.520 | 0.197 | 0.002 / 0.000 / 0.012 | 0.011 / 0.007 / 0.010 | 0.354 / 0.386 |
| all plans | 500 | 12 | 0.475 | 0.190 | 0.035 / 0.003 / 0.314 | 0.057 / 0.030 / 0.091 | 0.303 / 0.393 |
| all plans | 500 | 24 | 0.599 | 0.188 | 0.057 / 0.006 / 0.521 | 0.108 / 0.045 / 0.163 | 0.278 / 0.389 |
| state-reading plans | 393 | 1 | 0.709 | 0.217 | 0.002 / 0.000 / 0.018 | 0.011 / 0.007 / 0.010 | 0.388 / 0.422 |
| state-reading plans | 393 | 12 | 0.472 | 0.188 | 0.036 / 0.004 / 0.369 | 0.056 / 0.030 / 0.089 | 0.322 / 0.410 |
| state-reading plans | 393 | 24 | 0.606 | 0.191 | 0.063 / 0.006 / 0.714 | 0.106 / 0.046 / 0.154 | 0.293 / 0.399 |
| open-loop plans | 107 | 1 | 0.447 | 0.179 | 0.000 / 0.000 / 0.000 | 0.011 / 0.007 / 0.010 | 0.200 / 0.231 |
| open-loop plans | 107 | 12 | 0.567 | 0.229 | 0.025 / 0.003 / 0.111 | 0.062 / 0.033 / 0.120 | 0.227 / 0.324 |
| open-loop plans | 107 | 24 | 0.722 | 0.222 | 0.036 / 0.005 / 0.164 | 0.118 / 0.044 / 0.212 | 0.219 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.1902 | 0.817 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3016 | 0.883 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2387.4350 | 0.583 |
| funds_mae_12m | 4895.7120 | 42.3740 | 685.5282 | 0.867 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 232.9547 | 0.878 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 567.6783 | 0.772 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 371.8232 | 0.846 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0571 | 0.557 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0346 | 0.900 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3026 | 0.769 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3170 | 0.786 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 4758.7150 | 0.469 |
| funds_mae_24m | 6681.5280 | 66.8000 | 840.0477 | 0.883 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 418.8018 | 0.627 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 712.0565 | 0.673 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 565.5710 | 0.728 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.1085 | 0.462 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0565 | 0.901 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.2779 | 0.715 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.2857 | 0.729 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 840.0 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 418.8 | 218.6 | 754.9 |
| com_valve | 712.1 | 492.3 | 1165.4 |
| ind_valve | 565.6 | 371.1 | 1086.8 |
| pop | 4758.7 | 1875.9 | 7303.8 |
| res_pop | 100.4 | 44.7 | 158.4 |
| com_pop | 10.1 | 5.2 | 13.9 |
| ind_pop | 14.5 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 83.8 | 27.9 | 107.4 |
| tax_fund | 155.3 | 54.7 | 1326.7 |
| road_spend | 68.6 | 11.9 | 835.4 |
| fire_spend | 42.5 | 2.6 | 431.3 |
| police_spend | 75.7 | 3.8 | 545.1 |
| powered_zones | 9.9 | 2.8 | 10.6 |
| unpowered_zones | 6.6 | 2.6 | 8.5 |
| coal_plants | 0.3 | 0.0 | 0.4 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 77.8 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 838.6 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 336.3 | 160.2 | 525.9 |
| com_valve | 736.1 | 495.6 | 1123.2 |
| ind_valve | 619.1 | 397.1 | 1024.3 |
| pop | 4820.9 | 1889.8 | 6800.2 |
| res_pop | 99.7 | 44.3 | 148.6 |
| com_pop | 10.1 | 5.1 | 12.6 |
| ind_pop | 14.6 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 87.5 | 27.1 | 100.2 |
| tax_fund | 146.9 | 50.6 | 1281.6 |
| road_spend | 63.0 | 11.6 | 824.6 |
| fire_spend | 40.7 | 3.0 | 413.3 |
| police_spend | 76.3 | 3.5 | 516.9 |
| powered_zones | 10.3 | 2.5 | 12.5 |
| unpowered_zones | 6.8 | 2.4 | 9.0 |
| coal_plants | 0.4 | 0.0 | 0.4 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 75.8 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 845.4 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 721.8 | 433.2 | 1596.0 |
| com_valve | 623.8 | 480.1 | 1320.4 |
| ind_valve | 369.1 | 275.6 | 1316.6 |
| pop | 4530.2 | 1825.0 | 9153.8 |
| res_pop | 103.1 | 46.2 | 194.5 |
| com_pop | 9.8 | 5.4 | 18.4 |
| ind_pop | 13.9 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 70.1 | 30.9 | 133.7 |
| tax_fund | 186.4 | 69.9 | 1492.4 |
| road_spend | 89.0 | 13.0 | 875.0 |
| fire_spend | 49.0 | 0.9 | 497.3 |
| police_spend | 73.7 | 4.7 | 648.6 |
| powered_zones | 8.4 | 3.8 | 3.7 |
| unpowered_zones | 5.6 | 3.2 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 85.1 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.292 | 0.858 |
| traffic | 0.993 | 0.787 |
| pollution | 1.615 | 0.738 |
| land_value | 0.741 | 0.398 |
| crime | 1.258 | 0.597 |
| rate_of_growth | 1.281 | 0.852 |
| fire_coverage | 0.908 | 0.146 |
| police_coverage | 0.779 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.475 | 0.319 | 0.382 | 0.367 to 0.397 | 0.328 | 0.201 | 0.249 | 0.218 to 0.285 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.411 | 0.001 | 0.008 |
| all plans | 12 | 0.359 | 0.030 | 0.047 |
| all plans | 24 | 0.481 | 0.057 | 0.102 |
| state-reading plans | 1 | 0.603 | 0.001 | 0.008 |
| state-reading plans | 12 | 0.356 | 0.032 | 0.044 |
| state-reading plans | 24 | 0.488 | 0.062 | 0.098 |
| open-loop plans | 1 | 0.330 | 0.000 | 0.008 |
| open-loop plans | 12 | 0.439 | 0.020 | 0.050 |
| open-loop plans | 24 | 0.577 | 0.042 | 0.111 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -329.19 |
| tile_cat | -43.01 |
| flags | -18.74 |
| power | -6.39 |
| half | -3560.18 |
| eighth | -49.27 |
| scalars_s2 | -5.67 |
| build_cost | -0.94 |
| scalars | -24.39 |
| ledger | -26.65 |
| bk | -45.38 |
| sc_res_pop | -1.63 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.19 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.09 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.56 |
| sc_res_valve | -1.44 |
| sc_com_valve | -2.91 |
| sc_ind_valve | -1.98 |
| sc_score | -4.22 |
| sc_funds | -2.67 |
| sc_tax_fund | -1.64 |
| sc_road_spend | -2.54 |
| sc_fire_spend | -0.70 |
| sc_police_spend | -0.63 |
| lg_sprite_cycle | -0.94 |
| lg_total_pop | -3.50 |
| lg_res_hist0 | -1.78 |
| lg_res_hist1 | -1.58 |
| lg_com_hist0 | -0.82 |
| lg_com_hist1 | -0.26 |
| lg_ind_hist0 | -0.60 |
| lg_ind_hist1 | -0.39 |
| lg_res_cap | -0.01 |
| lg_com_cap | -1.33 |
| lg_ind_cap | -0.02 |
| lg_need_hospital | -0.22 |
| lg_need_church | -0.14 |
| lg_road_fund | -1.81 |
| lg_police_fund | -0.27 |
| lg_fire_fund | -0.32 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.18 |
| lg_city_center_x | -0.26 |
| lg_city_center_y | -0.45 |
| lg_pollution_max_x | -4.18 |
| lg_pollution_max_y | -4.17 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -3.40 |
| terrain | -12.45 |
| com_rate | -8.92 |
| kl | 13.87 |
| elbo | -4093.98 |
