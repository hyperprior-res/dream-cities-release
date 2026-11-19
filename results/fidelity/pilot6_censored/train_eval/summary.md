## pilot6_censored_samples_000600064_dec-a

samples consumed: 600064; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "c2c2ecc0bf1a26f8", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.302 | 0.301 | 0.301 | 0.288 to 0.315 | 0.190 | 0.187 | 0.188 | 0.165 to 0.218 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.136 | 0.135 | 0.135 | 0.125 to 0.145 | 0.055 | 0.054 | 0.055 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.307 | 0.305 | 0.306 | 0.293 to 0.320 | 0.201 | 0.196 | 0.199 | 0.172 to 0.232 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.147 | 0.057 | 0.055 | 0.056 | 0.049 to 0.063 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.280 | 0.283 | 0.281 | 0.263 to 0.298 | 0.151 | 0.151 | 0.151 | 0.125 to 0.184 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.128 | 0.131 | 0.130 | 0.119 to 0.140 | 0.050 | 0.051 | 0.051 | 0.042 to 0.060 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.479 | 0.197 | 0.003 / 0.000 / 0.012 | 0.008 / 0.007 / 0.010 | 0.335 / 0.386 |
| all plans | 500 | 12 | 0.361 | 0.190 | 0.034 / 0.003 / 0.314 | 0.035 / 0.030 / 0.091 | 0.326 / 0.393 |
| all plans | 500 | 24 | 0.470 | 0.188 | 0.050 / 0.006 / 0.521 | 0.061 / 0.045 / 0.163 | 0.311 / 0.389 |
| state-reading plans | 393 | 1 | 0.547 | 0.217 | 0.004 / 0.000 / 0.018 | 0.008 / 0.007 / 0.010 | 0.369 / 0.422 |
| state-reading plans | 393 | 12 | 0.360 | 0.188 | 0.041 / 0.004 / 0.369 | 0.035 / 0.030 / 0.089 | 0.346 / 0.410 |
| state-reading plans | 393 | 24 | 0.413 | 0.191 | 0.060 / 0.006 / 0.714 | 0.061 / 0.046 / 0.154 | 0.324 / 0.399 |
| open-loop plans | 107 | 1 | 0.426 | 0.179 | 0.000 / 0.000 / 0.000 | 0.008 / 0.007 / 0.010 | 0.183 / 0.231 |
| open-loop plans | 107 | 12 | 0.415 | 0.229 | 0.014 / 0.003 / 0.111 | 0.036 / 0.033 / 0.120 | 0.246 / 0.324 |
| open-loop plans | 107 | 24 | 0.701 | 0.222 | 0.019 / 0.005 / 0.164 | 0.060 / 0.044 / 0.212 | 0.260 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.1884 | 0.810 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3011 | 0.881 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 1463.6950 | 0.909 |
| funds_mae_12m | 4895.7120 | 42.3740 | 811.6922 | 0.841 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 182.7883 | 0.967 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 445.4792 | 0.916 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 281.9700 | 0.965 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0355 | 0.911 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0342 | 0.901 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3260 | 0.829 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3379 | 0.837 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 2571.3400 | 0.872 |
| funds_mae_24m | 6681.5280 | 66.8000 | 967.2950 | 0.864 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 246.1753 | 0.949 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 649.7893 | 0.766 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 454.3695 | 0.884 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0606 | 0.870 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0499 | 0.914 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.3110 | 0.800 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.3170 | 0.809 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 967.3 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 246.2 | 218.6 | 754.9 |
| com_valve | 649.8 | 492.3 | 1165.4 |
| ind_valve | 454.4 | 371.1 | 1086.8 |
| pop | 2571.3 | 1875.9 | 7303.8 |
| res_pop | 57.9 | 44.7 | 158.4 |
| com_pop | 6.4 | 5.2 | 13.9 |
| ind_pop | 7.3 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.1 | 27.9 | 107.4 |
| tax_fund | 96.3 | 54.7 | 1326.7 |
| road_spend | 49.9 | 11.9 | 835.4 |
| fire_spend | 32.9 | 2.6 | 431.3 |
| police_spend | 696.8 | 3.8 | 545.1 |
| powered_zones | 6.7 | 2.8 | 10.6 |
| unpowered_zones | 6.2 | 2.6 | 8.5 |
| coal_plants | 0.2 | 0.0 | 0.4 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 61.1 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 935.6 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 196.2 | 160.2 | 525.9 |
| com_valve | 689.5 | 495.6 | 1123.2 |
| ind_valve | 498.3 | 397.1 | 1024.3 |
| pop | 2611.1 | 1889.8 | 6800.2 |
| res_pop | 58.4 | 44.3 | 148.6 |
| com_pop | 6.2 | 5.1 | 12.6 |
| ind_pop | 7.5 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 44.5 | 27.1 | 100.2 |
| tax_fund | 91.3 | 50.6 | 1281.6 |
| road_spend | 47.9 | 11.6 | 824.6 |
| fire_spend | 29.1 | 3.0 | 413.3 |
| police_spend | 46.9 | 3.5 | 516.9 |
| powered_zones | 7.5 | 2.5 | 12.5 |
| unpowered_zones | 6.6 | 2.4 | 9.0 |
| coal_plants | 0.2 | 0.0 | 0.4 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 60.2 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1083.7 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 429.7 | 433.2 | 1596.0 |
| com_valve | 504.1 | 480.1 | 1320.4 |
| ind_valve | 293.2 | 275.6 | 1316.6 |
| pop | 2425.3 | 1825.0 | 9153.8 |
| res_pop | 56.1 | 46.2 | 194.5 |
| com_pop | 6.9 | 5.4 | 18.4 |
| ind_pop | 6.8 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 38.0 | 30.9 | 133.7 |
| tax_fund | 114.7 | 69.9 | 1492.4 |
| road_spend | 57.1 | 13.0 | 875.0 |
| fire_spend | 46.6 | 0.9 | 497.3 |
| police_spend | 3084.2 | 4.7 | 648.6 |
| powered_zones | 4.1 | 3.8 | 3.7 |
| unpowered_zones | 4.7 | 3.2 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 64.5 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.079 | 0.858 |
| traffic | 0.935 | 0.787 |
| pollution | 1.667 | 0.738 |
| land_value | 0.801 | 0.398 |
| crime | 1.158 | 0.597 |
| rate_of_growth | 1.027 | 0.852 |
| fire_coverage | 0.978 | 0.146 |
| police_coverage | 0.671 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.670 | 0.273 | 0.388 | 0.373 to 0.402 | 0.849 | 0.142 | 0.243 | 0.206 to 0.288 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.426 | 0.002 | 0.007 |
| all plans | 12 | 0.298 | 0.030 | 0.030 |
| all plans | 24 | 0.406 | 0.044 | 0.057 |
| state-reading plans | 1 | 0.494 | 0.002 | 0.007 |
| state-reading plans | 12 | 0.294 | 0.035 | 0.030 |
| state-reading plans | 24 | 0.346 | 0.056 | 0.056 |
| open-loop plans | 1 | 0.372 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.368 | 0.019 | 0.030 |
| open-loop plans | 24 | 0.640 | 0.019 | 0.060 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -305.05 |
| tile_cat | -46.10 |
| flags | -20.69 |
| power | -5.23 |
| half | -3873.78 |
| eighth | -54.16 |
| scalars_s2 | -6.21 |
| build_cost | -1.24 |
| scalars | -12.46 |
| ledger | -10.08 |
| bk | -16.32 |
| sc_res_pop | -1.88 |
| sc_com_pop | -0.25 |
| sc_ind_pop | -0.25 |
| sc_powered_zones | -0.10 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.61 |
| sc_res_valve | -1.08 |
| sc_com_valve | -2.09 |
| sc_ind_valve | -1.16 |
| sc_score | -0.29 |
| sc_funds | -0.83 |
| sc_tax_fund | -0.37 |
| sc_road_spend | -0.25 |
| sc_fire_spend | -0.09 |
| sc_police_spend | -0.08 |
| lg_sprite_cycle | -0.59 |
| lg_total_pop | -1.51 |
| lg_res_hist0 | -0.53 |
| lg_res_hist1 | -0.12 |
| lg_com_hist0 | -0.31 |
| lg_com_hist1 | -0.03 |
| lg_ind_hist0 | -0.30 |
| lg_ind_hist1 | -0.09 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.06 |
| lg_need_church | -0.05 |
| lg_road_fund | -0.24 |
| lg_police_fund | -0.05 |
| lg_fire_fund | -0.05 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.12 |
| lg_city_center_y | -0.08 |
| lg_pollution_max_x | -1.94 |
| lg_pollution_max_y | -1.67 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.24 |
| terrain | -15.09 |
| com_rate | -14.91 |
| kl | 3.80 |
| elbo | -4362.59 |
