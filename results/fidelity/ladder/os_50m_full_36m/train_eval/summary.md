## os_50m_full_36m_samples_036000000_dec-a

samples consumed: 36000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "047a3eb9a326995f", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.344 | 0.314 | 0.328 | 0.316 to 0.342 | 0.242 | 0.203 | 0.221 | 0.194 to 0.252 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.134 | 0.133 | 0.134 | 0.124 to 0.143 | 0.055 | 0.054 | 0.054 | 0.048 to 0.061 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.348 | 0.318 | 0.332 | 0.320 to 0.346 | 0.251 | 0.213 | 0.230 | 0.200 to 0.266 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.137 | 0.134 | 0.135 | 0.125 to 0.145 | 0.057 | 0.055 | 0.056 | 0.049 to 0.063 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.332 | 0.298 | 0.314 | 0.296 to 0.332 | 0.207 | 0.168 | 0.185 | 0.153 to 0.223 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.127 | 0.130 | 0.128 | 0.118 to 0.139 | 0.049 | 0.050 | 0.050 | 0.042 to 0.058 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.414 | 0.197 | 0.002 / 0.000 / 0.012 | 0.010 / 0.007 / 0.010 | 0.401 / 0.386 |
| all plans | 500 | 12 | 0.512 | 0.190 | 0.032 / 0.003 / 0.314 | 0.082 / 0.030 / 0.091 | 0.350 / 0.393 |
| all plans | 500 | 24 | 0.708 | 0.188 | 0.057 / 0.006 / 0.521 | 0.197 / 0.045 / 0.163 | 0.314 / 0.389 |
| state-reading plans | 393 | 1 | 0.405 | 0.217 | 0.004 / 0.000 / 0.018 | 0.010 / 0.007 / 0.010 | 0.435 / 0.422 |
| state-reading plans | 393 | 12 | 0.521 | 0.188 | 0.038 / 0.004 / 0.369 | 0.082 / 0.030 / 0.089 | 0.370 / 0.410 |
| state-reading plans | 393 | 24 | 0.745 | 0.191 | 0.072 / 0.006 / 0.714 | 0.197 / 0.046 / 0.154 | 0.328 / 0.399 |
| open-loop plans | 107 | 1 | 0.434 | 0.179 | 0.000 / 0.000 / 0.000 | 0.009 / 0.007 / 0.010 | 0.247 / 0.231 |
| open-loop plans | 107 | 12 | 0.538 | 0.229 | 0.014 / 0.003 / 0.111 | 0.077 / 0.033 / 0.120 | 0.268 / 0.324 |
| open-loop plans | 107 | 24 | 0.746 | 0.222 | 0.027 / 0.005 / 0.164 | 0.198 / 0.044 / 0.212 | 0.257 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.2208 | 0.949 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3285 | 0.962 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 3409.7050 | 0.223 |
| funds_mae_12m | 4895.7120 | 42.3740 | 561.8335 | 0.893 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 313.1095 | 0.736 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 572.7458 | 0.766 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 406.8963 | 0.800 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0817 | 0.154 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0320 | 0.908 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3501 | 0.890 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3564 | 0.883 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 8178.7750 | -0.161 |
| funds_mae_24m | 6681.5280 | 66.8000 | 791.0005 | 0.891 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 611.2682 | 0.268 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 863.3718 | 0.449 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 688.8687 | 0.556 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.1970 | -0.293 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0572 | 0.900 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.3136 | 0.807 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.3163 | 0.807 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 791.0 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 611.3 | 218.6 | 754.9 |
| com_valve | 863.4 | 492.3 | 1165.4 |
| ind_valve | 688.9 | 371.1 | 1086.8 |
| pop | 8178.8 | 1875.9 | 7303.8 |
| res_pop | 171.4 | 44.7 | 158.4 |
| com_pop | 13.3 | 5.2 | 13.9 |
| ind_pop | 20.6 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 126.9 | 27.9 | 107.4 |
| tax_fund | 203.4 | 54.7 | 1326.7 |
| road_spend | 65.3 | 11.9 | 835.4 |
| fire_spend | 56.1 | 2.6 | 431.3 |
| police_spend | 68.0 | 3.8 | 545.1 |
| powered_zones | 12.4 | 2.8 | 10.6 |
| unpowered_zones | 6.1 | 2.6 | 8.5 |
| coal_plants | 0.3 | 0.0 | 0.4 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 41.8 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 813.2 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 586.2 | 160.2 | 525.9 |
| com_valve | 915.7 | 495.6 | 1123.2 |
| ind_valve | 743.5 | 397.1 | 1024.3 |
| pop | 8325.2 | 1889.8 | 6800.2 |
| res_pop | 174.7 | 44.3 | 148.6 |
| com_pop | 13.5 | 5.1 | 12.6 |
| ind_pop | 20.9 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 129.2 | 27.1 | 100.2 |
| tax_fund | 194.7 | 50.6 | 1281.6 |
| road_spend | 61.4 | 11.6 | 824.6 |
| fire_spend | 54.1 | 3.0 | 413.3 |
| police_spend | 68.7 | 3.5 | 516.9 |
| powered_zones | 12.3 | 2.5 | 12.5 |
| unpowered_zones | 6.3 | 2.4 | 9.0 |
| coal_plants | 0.4 | 0.0 | 0.4 |
| nuclear_plants | 0.4 | 0.0 | 0.3 |
| road_total | 42.0 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 709.6 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 703.3 | 433.2 | 1596.0 |
| com_valve | 671.2 | 480.1 | 1320.4 |
| ind_valve | 488.0 | 275.6 | 1316.6 |
| pop | 7641.0 | 1825.0 | 9153.8 |
| res_pop | 159.4 | 46.2 | 194.5 |
| com_pop | 12.6 | 5.4 | 18.4 |
| ind_pop | 19.6 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 118.3 | 30.9 | 133.7 |
| tax_fund | 235.4 | 69.9 | 1492.4 |
| road_spend | 79.9 | 13.0 | 875.0 |
| fire_spend | 63.2 | 0.9 | 497.3 |
| police_spend | 65.2 | 4.7 | 648.6 |
| powered_zones | 12.7 | 3.8 | 3.7 |
| unpowered_zones | 5.5 | 3.2 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 40.9 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.122 | 0.858 |
| traffic | 0.917 | 0.787 |
| pollution | 1.571 | 0.738 |
| land_value | 0.669 | 0.398 |
| crime | 1.016 | 0.597 |
| rate_of_growth | 1.079 | 0.852 |
| fire_coverage | 1.167 | 0.146 |
| police_coverage | 0.852 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.571 | 0.298 | 0.392 | 0.378 to 0.406 | 0.465 | 0.174 | 0.253 | 0.217 to 0.294 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.293 | 0.001 | 0.006 |
| all plans | 12 | 0.397 | 0.029 | 0.075 |
| all plans | 24 | 0.589 | 0.067 | 0.207 |
| state-reading plans | 1 | 0.304 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.404 | 0.032 | 0.076 |
| state-reading plans | 24 | 0.622 | 0.082 | 0.206 |
| open-loop plans | 1 | 0.288 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.419 | 0.018 | 0.071 |
| open-loop plans | 24 | 0.629 | 0.030 | 0.210 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -229.56 |
| tile_cat | -32.99 |
| flags | -15.85 |
| power | -2.54 |
| half | -2877.19 |
| eighth | -36.46 |
| scalars_s2 | -5.06 |
| build_cost | -0.99 |
| scalars | -11.40 |
| ledger | -9.19 |
| bk | -15.53 |
| sc_res_pop | -1.43 |
| sc_com_pop | -0.09 |
| sc_ind_pop | -0.12 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.36 |
| sc_res_valve | -1.05 |
| sc_com_valve | -2.06 |
| sc_ind_valve | -0.79 |
| sc_score | -0.42 |
| sc_funds | -0.66 |
| sc_tax_fund | -0.54 |
| sc_road_spend | -0.57 |
| sc_fire_spend | -0.11 |
| sc_police_spend | -0.14 |
| lg_sprite_cycle | -0.11 |
| lg_total_pop | -1.26 |
| lg_res_hist0 | -0.37 |
| lg_res_hist1 | -0.01 |
| lg_com_hist0 | -0.29 |
| lg_com_hist1 | -0.00 |
| lg_ind_hist0 | -0.27 |
| lg_ind_hist1 | -0.00 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.07 |
| lg_need_church | -0.05 |
| lg_road_fund | -0.60 |
| lg_police_fund | -0.06 |
| lg_fire_fund | -0.07 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.10 |
| lg_city_center_x | -0.01 |
| lg_city_center_y | -0.01 |
| lg_pollution_max_x | -1.93 |
| lg_pollution_max_y | -1.63 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.32 |
| terrain | -6.41 |
| com_rate | -1.36 |
| kl | 20.84 |
| elbo | -3244.79 |
