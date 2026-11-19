## os_15m_small_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.335 | 0.318 | 0.326 | 0.314 to 0.340 | 0.232 | 0.198 | 0.214 | 0.187 to 0.245 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.340 | 0.323 | 0.331 | 0.319 to 0.345 | 0.243 | 0.207 | 0.224 | 0.195 to 0.260 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.317 | 0.300 | 0.308 | 0.290 to 0.325 | 0.190 | 0.163 | 0.175 | 0.144 to 0.213 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.450 | 0.197 | 0.004 / 0.000 / 0.012 | 0.010 / 0.007 / 0.010 | 0.382 / 0.386 |
| all plans | 500 | 12 | 0.404 | 0.190 | 0.053 / 0.003 / 0.314 | 0.054 / 0.030 / 0.091 | 0.352 / 0.393 |
| all plans | 500 | 24 | 0.466 | 0.188 | 0.096 / 0.006 / 0.521 | 0.092 / 0.045 / 0.163 | 0.332 / 0.389 |
| state-reading plans | 393 | 1 | 0.482 | 0.217 | 0.006 / 0.000 / 0.018 | 0.010 / 0.007 / 0.010 | 0.417 / 0.422 |
| state-reading plans | 393 | 12 | 0.405 | 0.188 | 0.056 / 0.004 / 0.369 | 0.053 / 0.030 / 0.089 | 0.373 / 0.410 |
| state-reading plans | 393 | 24 | 0.475 | 0.191 | 0.103 / 0.006 / 0.714 | 0.086 / 0.046 / 0.154 | 0.347 / 0.399 |
| open-loop plans | 107 | 1 | 0.432 | 0.179 | 0.000 / 0.000 / 0.000 | 0.011 / 0.007 / 0.010 | 0.225 / 0.231 |
| open-loop plans | 107 | 12 | 0.461 | 0.229 | 0.035 / 0.003 / 0.111 | 0.057 / 0.033 / 0.120 | 0.266 / 0.324 |
| open-loop plans | 107 | 24 | 0.526 | 0.222 | 0.073 / 0.005 / 0.164 | 0.114 / 0.044 / 0.212 | 0.273 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.2136 | 0.918 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3264 | 0.955 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2248.1950 | 0.632 |
| funds_mae_12m | 4895.7120 | 42.3740 | 742.8083 | 0.856 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 273.7980 | 0.806 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 543.4850 | 0.800 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 407.0093 | 0.800 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0541 | 0.607 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0525 | 0.842 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3522 | 0.896 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3631 | 0.900 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 3878.8450 | 0.631 |
| funds_mae_24m | 6681.5280 | 66.8000 | 1029.9690 | 0.854 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 359.7258 | 0.737 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 760.1520 | 0.602 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 623.0220 | 0.648 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0917 | 0.605 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0958 | 0.825 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.3322 | 0.855 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.3371 | 0.860 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1030.0 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 359.7 | 218.6 | 754.9 |
| com_valve | 760.2 | 492.3 | 1165.4 |
| ind_valve | 623.0 | 371.1 | 1086.8 |
| pop | 3878.8 | 1875.9 | 7303.8 |
| res_pop | 83.1 | 44.7 | 158.4 |
| com_pop | 8.0 | 5.2 | 13.9 |
| ind_pop | 13.0 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 55.3 | 27.9 | 107.4 |
| tax_fund | 125.9 | 54.7 | 1326.7 |
| road_spend | 56.5 | 11.9 | 835.4 |
| fire_spend | 44.0 | 2.6 | 431.3 |
| police_spend | 73.8 | 3.8 | 545.1 |
| powered_zones | 7.1 | 2.8 | 10.6 |
| unpowered_zones | 6.1 | 2.6 | 8.5 |
| coal_plants | 0.2 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 66.2 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 998.6 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 293.2 | 160.2 | 525.9 |
| com_valve | 807.3 | 495.6 | 1123.2 |
| ind_valve | 702.4 | 397.1 | 1024.3 |
| pop | 3796.8 | 1889.8 | 6800.2 |
| res_pop | 83.1 | 44.3 | 148.6 |
| com_pop | 7.8 | 5.1 | 12.6 |
| ind_pop | 12.8 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 56.9 | 27.1 | 100.2 |
| tax_fund | 118.5 | 50.6 | 1281.6 |
| road_spend | 54.0 | 11.6 | 824.6 |
| fire_spend | 41.6 | 3.0 | 413.3 |
| police_spend | 71.9 | 3.5 | 516.9 |
| powered_zones | 7.5 | 2.5 | 12.5 |
| unpowered_zones | 6.4 | 2.4 | 9.0 |
| coal_plants | 0.2 | 0.0 | 0.4 |
| nuclear_plants | 0.2 | 0.0 | 0.3 |
| road_total | 65.1 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1145.1 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 604.2 | 433.2 | 1596.0 |
| com_valve | 587.0 | 480.1 | 1320.4 |
| ind_valve | 331.6 | 275.6 | 1316.6 |
| pop | 4180.3 | 1825.0 | 9153.8 |
| res_pop | 83.2 | 46.2 | 194.5 |
| com_pop | 8.6 | 5.4 | 18.4 |
| ind_pop | 13.8 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 49.7 | 30.9 | 133.7 |
| tax_fund | 153.0 | 69.9 | 1492.4 |
| road_spend | 65.6 | 13.0 | 875.0 |
| fire_spend | 52.8 | 0.9 | 497.3 |
| police_spend | 80.9 | 4.7 | 648.6 |
| powered_zones | 5.7 | 3.8 | 3.7 |
| unpowered_zones | 5.1 | 3.2 | 6.7 |
| coal_plants | 0.1 | 0.0 | 0.1 |
| nuclear_plants | 0.2 | 0.0 | 0.2 |
| road_total | 70.3 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.012 | 0.858 |
| traffic | 0.929 | 0.787 |
| pollution | 1.578 | 0.738 |
| land_value | 0.648 | 0.398 |
| crime | 1.009 | 0.597 |
| rate_of_growth | 1.039 | 0.852 |
| fire_coverage | 0.904 | 0.146 |
| police_coverage | 0.737 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.571 | 0.298 | 0.391 | 0.377 to 0.405 | 0.481 | 0.164 | 0.245 | 0.212 to 0.284 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.359 | 0.003 | 0.008 |
| all plans | 12 | 0.322 | 0.051 | 0.044 |
| all plans | 24 | 0.382 | 0.113 | 0.085 |
| state-reading plans | 1 | 0.390 | 0.003 | 0.007 |
| state-reading plans | 12 | 0.321 | 0.053 | 0.044 |
| state-reading plans | 24 | 0.391 | 0.114 | 0.083 |
| open-loop plans | 1 | 0.346 | 0.000 | 0.008 |
| open-loop plans | 12 | 0.381 | 0.039 | 0.047 |
| open-loop plans | 24 | 0.431 | 0.097 | 0.102 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -284.35 |
| tile_cat | -39.43 |
| flags | -18.54 |
| power | -5.10 |
| half | -3384.65 |
| eighth | -49.34 |
| scalars_s2 | -5.66 |
| build_cost | -1.05 |
| scalars | -26.03 |
| ledger | -26.31 |
| bk | -46.67 |
| sc_res_pop | -1.63 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.20 |
| sc_powered_zones | -0.04 |
| sc_unpowered_zones | -0.09 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.54 |
| sc_res_valve | -1.45 |
| sc_com_valve | -2.79 |
| sc_ind_valve | -1.73 |
| sc_score | -5.26 |
| sc_funds | -2.83 |
| sc_tax_fund | -2.30 |
| sc_road_spend | -2.59 |
| sc_fire_spend | -0.70 |
| sc_police_spend | -0.70 |
| lg_sprite_cycle | -0.94 |
| lg_total_pop | -3.42 |
| lg_res_hist0 | -2.70 |
| lg_res_hist1 | -1.22 |
| lg_com_hist0 | -0.60 |
| lg_com_hist1 | -0.10 |
| lg_ind_hist0 | -0.80 |
| lg_ind_hist1 | -0.22 |
| lg_res_cap | -0.02 |
| lg_com_cap | -0.05 |
| lg_ind_cap | -0.13 |
| lg_need_hospital | -0.23 |
| lg_need_church | -0.10 |
| lg_road_fund | -1.82 |
| lg_police_fund | -0.43 |
| lg_fire_fund | -0.31 |
| lg_auto_budget | -0.06 |
| lg_fire_pop | -0.20 |
| lg_city_center_x | -0.59 |
| lg_city_center_y | -0.55 |
| lg_pollution_max_x | -3.90 |
| lg_pollution_max_y | -4.49 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -3.41 |
| terrain | -11.10 |
| com_rate | -10.51 |
| kl | 12.98 |
| elbo | -3869.39 |
