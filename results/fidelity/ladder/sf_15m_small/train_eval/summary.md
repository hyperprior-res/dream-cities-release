## sf_15m_small_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.273 | 0.324 | 0.297 | 0.284 to 0.310 | 0.165 | 0.214 | 0.186 | 0.165 to 0.212 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.280 | 0.329 | 0.302 | 0.290 to 0.316 | 0.174 | 0.224 | 0.196 | 0.172 to 0.224 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.251 | 0.306 | 0.276 | 0.258 to 0.293 | 0.133 | 0.179 | 0.153 | 0.128 to 0.182 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.487 | 0.197 | 0.002 / 0.000 / 0.012 | 0.011 / 0.007 / 0.010 | 0.356 / 0.386 |
| all plans | 500 | 12 | 0.538 | 0.190 | 0.060 / 0.003 / 0.314 | 0.062 / 0.030 / 0.091 | 0.292 / 0.393 |
| all plans | 500 | 24 | 0.707 | 0.188 | 0.137 / 0.006 / 0.521 | 0.123 / 0.045 / 0.163 | 0.262 / 0.389 |
| state-reading plans | 393 | 1 | 0.548 | 0.217 | 0.003 / 0.000 / 0.018 | 0.011 / 0.007 / 0.010 | 0.388 / 0.422 |
| state-reading plans | 393 | 12 | 0.525 | 0.188 | 0.064 / 0.004 / 0.369 | 0.060 / 0.030 / 0.089 | 0.308 / 0.410 |
| state-reading plans | 393 | 24 | 0.701 | 0.191 | 0.146 / 0.006 / 0.714 | 0.119 / 0.046 / 0.154 | 0.274 / 0.399 |
| open-loop plans | 107 | 1 | 0.445 | 0.179 | 0.000 / 0.000 / 0.000 | 0.010 / 0.007 / 0.010 | 0.212 / 0.231 |
| open-loop plans | 107 | 12 | 0.699 | 0.229 | 0.049 / 0.003 / 0.111 | 0.067 / 0.033 / 0.120 | 0.227 / 0.324 |
| open-loop plans | 107 | 24 | 0.948 | 0.222 | 0.107 / 0.005 / 0.164 | 0.142 / 0.044 / 0.212 | 0.215 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.1863 | 0.800 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.2965 | 0.868 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2637.5450 | 0.495 |
| funds_mae_12m | 4895.7120 | 42.3740 | 888.1075 | 0.826 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 269.7110 | 0.813 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 552.8982 | 0.789 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 392.7220 | 0.819 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0620 | 0.477 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0601 | 0.818 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.2917 | 0.742 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3063 | 0.759 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 5459.1700 | 0.340 |
| funds_mae_24m | 6681.5280 | 66.8000 | 1446.6650 | 0.791 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 405.0163 | 0.652 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 699.9620 | 0.691 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 572.1453 | 0.719 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.1233 | 0.336 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.1366 | 0.746 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.2616 | 0.673 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.2687 | 0.686 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1446.7 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 405.0 | 218.6 | 754.9 |
| com_valve | 700.0 | 492.3 | 1165.4 |
| ind_valve | 572.1 | 371.1 | 1086.8 |
| pop | 5459.2 | 1875.9 | 7303.8 |
| res_pop | 117.6 | 44.7 | 158.4 |
| com_pop | 9.4 | 5.2 | 13.9 |
| ind_pop | 16.3 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 95.1 | 27.9 | 107.4 |
| tax_fund | 147.9 | 54.7 | 1326.7 |
| road_spend | 71.0 | 11.9 | 835.4 |
| fire_spend | 52.7 | 2.6 | 431.3 |
| police_spend | 87.7 | 3.8 | 545.1 |
| powered_zones | 11.0 | 2.8 | 10.6 |
| unpowered_zones | 7.6 | 2.6 | 8.5 |
| coal_plants | 0.5 | 0.0 | 0.4 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 83.5 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1370.9 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 337.1 | 160.2 | 525.9 |
| com_valve | 720.5 | 495.6 | 1123.2 |
| ind_valve | 629.3 | 397.1 | 1024.3 |
| pop | 5396.5 | 1889.8 | 6800.2 |
| res_pop | 114.3 | 44.3 | 148.6 |
| com_pop | 9.4 | 5.1 | 12.6 |
| ind_pop | 16.3 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 97.5 | 27.1 | 100.2 |
| tax_fund | 139.7 | 50.6 | 1281.6 |
| road_spend | 68.7 | 11.6 | 824.6 |
| fire_spend | 48.9 | 3.0 | 413.3 |
| police_spend | 90.4 | 3.5 | 516.9 |
| powered_zones | 11.1 | 2.5 | 12.5 |
| unpowered_zones | 7.8 | 2.4 | 9.0 |
| coal_plants | 0.5 | 0.0 | 0.4 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 82.7 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1724.9 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 654.5 | 433.2 | 1596.0 |
| com_valve | 624.4 | 480.1 | 1320.4 |
| ind_valve | 362.1 | 275.6 | 1316.6 |
| pop | 5689.2 | 1825.0 | 9153.8 |
| res_pop | 129.3 | 46.2 | 194.5 |
| com_pop | 9.5 | 5.4 | 18.4 |
| ind_pop | 16.1 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 86.3 | 30.9 | 133.7 |
| tax_fund | 177.7 | 69.9 | 1492.4 |
| road_spend | 79.4 | 13.0 | 875.0 |
| fire_spend | 66.5 | 0.9 | 497.3 |
| police_spend | 77.8 | 4.7 | 648.6 |
| powered_zones | 10.6 | 3.8 | 3.7 |
| unpowered_zones | 6.9 | 3.2 | 6.7 |
| coal_plants | 0.4 | 0.0 | 0.1 |
| nuclear_plants | 0.6 | 0.0 | 0.2 |
| road_total | 86.1 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.304 | 0.858 |
| traffic | 0.961 | 0.787 |
| pollution | 1.614 | 0.738 |
| land_value | 0.732 | 0.398 |
| crime | 1.334 | 0.597 |
| rate_of_growth | 1.333 | 0.852 |
| fire_coverage | 1.204 | 0.146 |
| police_coverage | 1.002 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.569 | 0.305 | 0.397 | 0.384 to 0.411 | 0.488 | 0.181 | 0.264 | 0.230 to 0.303 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.373 | 0.001 | 0.007 |
| all plans | 12 | 0.403 | 0.063 | 0.051 |
| all plans | 24 | 0.555 | 0.167 | 0.117 |
| state-reading plans | 1 | 0.425 | 0.002 | 0.007 |
| state-reading plans | 12 | 0.392 | 0.064 | 0.048 |
| state-reading plans | 24 | 0.551 | 0.176 | 0.107 |
| open-loop plans | 1 | 0.333 | 0.000 | 0.007 |
| open-loop plans | 12 | 0.539 | 0.050 | 0.063 |
| open-loop plans | 24 | 0.732 | 0.130 | 0.131 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -286.36 |
| tile_cat | -40.41 |
| flags | -18.57 |
| power | -4.88 |
| half | -3425.87 |
| eighth | -48.76 |
| scalars_s2 | -5.66 |
| build_cost | -0.96 |
| scalars | -21.87 |
| ledger | -21.07 |
| bk | -37.28 |
| sc_res_pop | -1.62 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.20 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.09 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.55 |
| sc_res_valve | -1.38 |
| sc_com_valve | -2.66 |
| sc_ind_valve | -1.61 |
| sc_score | -3.62 |
| sc_funds | -2.41 |
| sc_tax_fund | -1.86 |
| sc_road_spend | -1.60 |
| sc_fire_spend | -0.55 |
| sc_police_spend | -0.54 |
| lg_sprite_cycle | -0.92 |
| lg_total_pop | -2.98 |
| lg_res_hist0 | -1.59 |
| lg_res_hist1 | -0.77 |
| lg_com_hist0 | -0.49 |
| lg_com_hist1 | -0.04 |
| lg_ind_hist0 | -0.53 |
| lg_ind_hist1 | -0.15 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.02 |
| lg_ind_cap | -0.14 |
| lg_need_hospital | -0.18 |
| lg_need_church | -0.09 |
| lg_road_fund | -1.58 |
| lg_police_fund | -0.32 |
| lg_fire_fund | -0.24 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.14 |
| lg_city_center_x | -0.45 |
| lg_city_center_y | -0.36 |
| lg_pollution_max_x | -3.38 |
| lg_pollution_max_y | -3.51 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -3.13 |
| terrain | -12.56 |
| com_rate | -8.78 |
| kl | 13.24 |
| elbo | -3903.35 |
