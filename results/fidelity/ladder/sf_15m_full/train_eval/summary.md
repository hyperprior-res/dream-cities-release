## sf_15m_full_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.290 | 0.315 | 0.302 | 0.289 to 0.316 | 0.180 | 0.202 | 0.190 | 0.167 to 0.218 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.295 | 0.320 | 0.307 | 0.294 to 0.321 | 0.190 | 0.212 | 0.201 | 0.174 to 0.231 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.270 | 0.297 | 0.283 | 0.264 to 0.300 | 0.144 | 0.162 | 0.152 | 0.129 to 0.178 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.430 | 0.197 | 0.002 / 0.000 / 0.012 | 0.011 / 0.007 / 0.010 | 0.349 / 0.386 |
| all plans | 500 | 12 | 0.451 | 0.190 | 0.052 / 0.003 / 0.314 | 0.049 / 0.030 / 0.091 | 0.302 / 0.393 |
| all plans | 500 | 24 | 0.552 | 0.188 | 0.116 / 0.006 / 0.521 | 0.081 / 0.045 / 0.163 | 0.278 / 0.389 |
| state-reading plans | 393 | 1 | 0.501 | 0.217 | 0.003 / 0.000 / 0.018 | 0.011 / 0.007 / 0.010 | 0.383 / 0.422 |
| state-reading plans | 393 | 12 | 0.443 | 0.188 | 0.055 / 0.004 / 0.369 | 0.046 / 0.030 / 0.089 | 0.320 / 0.410 |
| state-reading plans | 393 | 24 | 0.551 | 0.191 | 0.122 / 0.006 / 0.714 | 0.078 / 0.046 / 0.154 | 0.292 / 0.399 |
| open-loop plans | 107 | 1 | 0.401 | 0.179 | 0.000 / 0.000 / 0.000 | 0.011 / 0.007 / 0.010 | 0.195 / 0.231 |
| open-loop plans | 107 | 12 | 0.574 | 0.229 | 0.042 / 0.003 / 0.111 | 0.059 / 0.033 / 0.120 | 0.230 / 0.324 |
| open-loop plans | 107 | 24 | 0.723 | 0.222 | 0.092 / 0.005 / 0.164 | 0.090 / 0.044 / 0.212 | 0.225 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.1903 | 0.818 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3023 | 0.885 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2151.9800 | 0.666 |
| funds_mae_12m | 4895.7120 | 42.3740 | 764.9088 | 0.851 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 241.7425 | 0.863 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 577.0935 | 0.760 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 371.2697 | 0.847 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0493 | 0.686 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0515 | 0.846 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3020 | 0.768 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3155 | 0.782 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 3521.2050 | 0.697 |
| funds_mae_24m | 6681.5280 | 66.8000 | 1233.5300 | 0.824 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 350.8715 | 0.753 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 737.6840 | 0.635 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 527.1740 | 0.782 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0809 | 0.697 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.1156 | 0.787 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.2782 | 0.715 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.2845 | 0.726 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1233.5 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 350.9 | 218.6 | 754.9 |
| com_valve | 737.7 | 492.3 | 1165.4 |
| ind_valve | 527.2 | 371.1 | 1086.8 |
| pop | 3521.2 | 1875.9 | 7303.8 |
| res_pop | 83.1 | 44.7 | 158.4 |
| com_pop | 8.7 | 5.2 | 13.9 |
| ind_pop | 10.4 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 73.8 | 27.9 | 107.4 |
| tax_fund | 117.9 | 54.7 | 1326.7 |
| road_spend | 65.3 | 11.9 | 835.4 |
| fire_spend | 39.4 | 2.6 | 431.3 |
| police_spend | 51.8 | 3.8 | 545.1 |
| powered_zones | 10.0 | 2.8 | 10.6 |
| unpowered_zones | 7.9 | 2.6 | 8.5 |
| coal_plants | 0.3 | 0.0 | 0.4 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 67.2 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1168.8 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 301.5 | 160.2 | 525.9 |
| com_valve | 778.4 | 495.6 | 1123.2 |
| ind_valve | 577.9 | 397.1 | 1024.3 |
| pop | 3506.2 | 1889.8 | 6800.2 |
| res_pop | 80.9 | 44.3 | 148.6 |
| com_pop | 8.6 | 5.1 | 12.6 |
| ind_pop | 10.4 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 74.9 | 27.1 | 100.2 |
| tax_fund | 114.1 | 50.6 | 1281.6 |
| road_spend | 63.2 | 11.6 | 824.6 |
| fire_spend | 36.7 | 3.0 | 413.3 |
| police_spend | 52.5 | 3.5 | 516.9 |
| powered_zones | 10.0 | 2.5 | 12.5 |
| unpowered_zones | 7.9 | 2.4 | 9.0 |
| coal_plants | 0.3 | 0.0 | 0.4 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 65.5 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1471.3 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 532.2 | 433.2 | 1596.0 |
| com_valve | 588.1 | 480.1 | 1320.4 |
| ind_valve | 341.0 | 275.6 | 1316.6 |
| pop | 3576.2 | 1825.0 | 9153.8 |
| res_pop | 91.1 | 46.2 | 194.5 |
| com_pop | 9.1 | 5.4 | 18.4 |
| ind_pop | 10.1 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 69.5 | 30.9 | 133.7 |
| tax_fund | 131.9 | 69.9 | 1492.4 |
| road_spend | 73.2 | 13.0 | 875.0 |
| fire_spend | 49.0 | 0.9 | 497.3 |
| police_spend | 49.1 | 4.7 | 648.6 |
| powered_zones | 9.9 | 3.8 | 3.7 |
| unpowered_zones | 7.9 | 3.2 | 6.7 |
| coal_plants | 0.2 | 0.0 | 0.1 |
| nuclear_plants | 0.3 | 0.0 | 0.2 |
| road_total | 73.4 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.236 | 0.858 |
| traffic | 0.985 | 0.787 |
| pollution | 1.576 | 0.738 |
| land_value | 0.688 | 0.398 |
| crime | 1.213 | 0.597 |
| rate_of_growth | 1.230 | 0.852 |
| fire_coverage | 1.307 | 0.146 |
| police_coverage | 0.900 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.634 | 0.295 | 0.403 | 0.388 to 0.417 | 0.652 | 0.164 | 0.262 | 0.226 to 0.304 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.322 | 0.001 | 0.007 |
| all plans | 12 | 0.329 | 0.054 | 0.039 |
| all plans | 24 | 0.414 | 0.145 | 0.064 |
| state-reading plans | 1 | 0.360 | 0.001 | 0.007 |
| state-reading plans | 12 | 0.322 | 0.055 | 0.037 |
| state-reading plans | 24 | 0.412 | 0.151 | 0.064 |
| open-loop plans | 1 | 0.312 | 0.000 | 0.008 |
| open-loop plans | 12 | 0.428 | 0.051 | 0.045 |
| open-loop plans | 24 | 0.547 | 0.106 | 0.076 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -269.62 |
| tile_cat | -38.43 |
| flags | -17.52 |
| power | -3.85 |
| half | -3320.71 |
| eighth | -47.50 |
| scalars_s2 | -5.58 |
| build_cost | -0.93 |
| scalars | -11.53 |
| ledger | -9.59 |
| bk | -15.54 |
| sc_res_pop | -1.59 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.07 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.56 |
| sc_res_valve | -1.09 |
| sc_com_valve | -2.07 |
| sc_ind_valve | -1.03 |
| sc_score | -0.28 |
| sc_funds | -0.73 |
| sc_tax_fund | -0.37 |
| sc_road_spend | -0.23 |
| sc_fire_spend | -0.08 |
| sc_police_spend | -0.07 |
| lg_sprite_cycle | -0.57 |
| lg_total_pop | -1.48 |
| lg_res_hist0 | -0.47 |
| lg_res_hist1 | -0.05 |
| lg_com_hist0 | -0.31 |
| lg_com_hist1 | -0.00 |
| lg_ind_hist0 | -0.30 |
| lg_ind_hist1 | -0.03 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.06 |
| lg_need_church | -0.05 |
| lg_road_fund | -0.22 |
| lg_police_fund | -0.04 |
| lg_fire_fund | -0.04 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -1.91 |
| lg_pollution_max_y | -1.67 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.24 |
| terrain | -10.27 |
| com_rate | -5.02 |
| kl | 12.66 |
| elbo | -3747.62 |
