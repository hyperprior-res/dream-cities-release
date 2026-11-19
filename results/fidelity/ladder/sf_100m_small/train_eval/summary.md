## sf_100m_small_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.297 | 0.332 | 0.314 | 0.300 to 0.328 | 0.183 | 0.213 | 0.197 | 0.174 to 0.225 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.302 | 0.336 | 0.318 | 0.305 to 0.332 | 0.192 | 0.223 | 0.206 | 0.180 to 0.238 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.280 | 0.315 | 0.296 | 0.276 to 0.315 | 0.149 | 0.179 | 0.163 | 0.136 to 0.193 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.492 | 0.197 | 0.001 / 0.000 / 0.012 | 0.010 / 0.007 / 0.010 | 0.376 / 0.386 |
| all plans | 500 | 12 | 0.536 | 0.190 | 0.040 / 0.003 / 0.314 | 0.061 / 0.030 / 0.091 | 0.289 / 0.393 |
| all plans | 500 | 24 | 0.733 | 0.188 | 0.085 / 0.006 / 0.521 | 0.124 / 0.045 / 0.163 | 0.255 / 0.389 |
| state-reading plans | 393 | 1 | 0.681 | 0.217 | 0.002 / 0.000 / 0.018 | 0.010 / 0.007 / 0.010 | 0.411 / 0.422 |
| state-reading plans | 393 | 12 | 0.526 | 0.188 | 0.043 / 0.004 / 0.369 | 0.060 / 0.030 / 0.089 | 0.307 / 0.410 |
| state-reading plans | 393 | 24 | 0.729 | 0.191 | 0.099 / 0.006 / 0.714 | 0.120 / 0.046 / 0.154 | 0.270 / 0.399 |
| open-loop plans | 107 | 1 | 0.423 | 0.179 | 0.000 / 0.000 / 0.000 | 0.010 / 0.007 / 0.010 | 0.216 / 0.231 |
| open-loop plans | 107 | 12 | 0.701 | 0.229 | 0.031 / 0.003 / 0.111 | 0.069 / 0.033 / 0.120 | 0.217 / 0.324 |
| open-loop plans | 107 | 24 | 0.956 | 0.222 | 0.051 / 0.005 / 0.164 | 0.139 / 0.044 / 0.212 | 0.198 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.1970 | 0.846 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3136 | 0.918 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 2689.8100 | 0.477 |
| funds_mae_12m | 4895.7120 | 42.3740 | 702.6880 | 0.864 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 243.6565 | 0.859 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 560.3573 | 0.780 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 389.9565 | 0.823 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0611 | 0.492 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0396 | 0.884 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.2892 | 0.735 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3039 | 0.753 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 5824.1700 | 0.273 |
| funds_mae_24m | 6681.5280 | 66.8000 | 1064.3390 | 0.849 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 413.7350 | 0.636 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 738.3390 | 0.634 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 609.2843 | 0.667 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.1243 | 0.327 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.0854 | 0.845 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.2551 | 0.656 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.2628 | 0.671 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1064.3 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 413.7 | 218.6 | 754.9 |
| com_valve | 738.3 | 492.3 | 1165.4 |
| ind_valve | 609.3 | 371.1 | 1086.8 |
| pop | 5824.2 | 1875.9 | 7303.8 |
| res_pop | 131.9 | 44.7 | 158.4 |
| com_pop | 10.5 | 5.2 | 13.9 |
| ind_pop | 16.8 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 92.9 | 27.9 | 107.4 |
| tax_fund | 159.7 | 54.7 | 1326.7 |
| road_spend | 72.1 | 11.9 | 835.4 |
| fire_spend | 41.5 | 2.6 | 431.3 |
| police_spend | 80.6 | 3.8 | 545.1 |
| powered_zones | 11.6 | 2.8 | 10.6 |
| unpowered_zones | 7.8 | 2.6 | 8.5 |
| coal_plants | 0.5 | 0.0 | 0.4 |
| nuclear_plants | 0.7 | 0.0 | 0.3 |
| road_total | 69.4 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1064.9 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 322.1 | 160.2 | 525.9 |
| com_valve | 775.6 | 495.6 | 1123.2 |
| ind_valve | 669.9 | 397.1 | 1024.3 |
| pop | 5834.7 | 1889.8 | 6800.2 |
| res_pop | 130.2 | 44.3 | 148.6 |
| com_pop | 10.6 | 5.1 | 12.6 |
| ind_pop | 16.7 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 95.2 | 27.1 | 100.2 |
| tax_fund | 145.3 | 50.6 | 1281.6 |
| road_spend | 69.2 | 11.6 | 824.6 |
| fire_spend | 42.0 | 3.0 | 413.3 |
| police_spend | 83.1 | 3.5 | 516.9 |
| powered_zones | 11.9 | 2.5 | 12.5 |
| unpowered_zones | 8.1 | 2.4 | 9.0 |
| coal_plants | 0.5 | 0.0 | 0.4 |
| nuclear_plants | 0.7 | 0.0 | 0.3 |
| road_total | 67.3 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1062.1 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 750.3 | 433.2 | 1596.0 |
| com_valve | 601.6 | 480.1 | 1320.4 |
| ind_valve | 386.7 | 275.6 | 1316.6 |
| pop | 5785.4 | 1825.0 | 9153.8 |
| res_pop | 138.3 | 46.2 | 194.5 |
| com_pop | 10.4 | 5.4 | 18.4 |
| ind_pop | 17.2 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 84.7 | 30.9 | 133.7 |
| tax_fund | 212.7 | 69.9 | 1492.4 |
| road_spend | 82.5 | 13.0 | 875.0 |
| fire_spend | 39.8 | 0.9 | 497.3 |
| police_spend | 71.1 | 4.7 | 648.6 |
| powered_zones | 10.6 | 3.8 | 3.7 |
| unpowered_zones | 6.9 | 3.2 | 6.7 |
| coal_plants | 0.4 | 0.0 | 0.1 |
| nuclear_plants | 0.6 | 0.0 | 0.2 |
| road_total | 77.1 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.401 | 0.858 |
| traffic | 0.961 | 0.787 |
| pollution | 1.649 | 0.738 |
| land_value | 0.813 | 0.398 |
| crime | 1.395 | 0.597 |
| rate_of_growth | 1.295 | 0.852 |
| fire_coverage | 0.948 | 0.146 |
| police_coverage | 0.960 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.438 | 0.327 | 0.375 | 0.360 to 0.389 | 0.287 | 0.203 | 0.237 | 0.207 to 0.274 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.409 | 0.001 | 0.007 |
| all plans | 12 | 0.410 | 0.040 | 0.052 |
| all plans | 24 | 0.563 | 0.107 | 0.111 |
| state-reading plans | 1 | 0.595 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.405 | 0.044 | 0.049 |
| state-reading plans | 24 | 0.566 | 0.116 | 0.109 |
| open-loop plans | 1 | 0.345 | 0.000 | 0.008 |
| open-loop plans | 12 | 0.510 | 0.028 | 0.063 |
| open-loop plans | 24 | 0.695 | 0.069 | 0.133 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -366.26 |
| tile_cat | -46.29 |
| flags | -20.18 |
| power | -7.05 |
| half | -3665.91 |
| eighth | -53.98 |
| scalars_s2 | -5.66 |
| build_cost | -0.95 |
| scalars | -24.50 |
| ledger | -29.76 |
| bk | -48.60 |
| sc_res_pop | -1.62 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.19 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.09 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.56 |
| sc_res_valve | -1.61 |
| sc_com_valve | -2.97 |
| sc_ind_valve | -2.10 |
| sc_score | -3.84 |
| sc_funds | -2.30 |
| sc_tax_fund | -2.33 |
| sc_road_spend | -2.65 |
| sc_fire_spend | -0.48 |
| sc_police_spend | -0.57 |
| lg_sprite_cycle | -1.02 |
| lg_total_pop | -2.63 |
| lg_res_hist0 | -1.96 |
| lg_res_hist1 | -1.98 |
| lg_com_hist0 | -0.90 |
| lg_com_hist1 | -0.34 |
| lg_ind_hist0 | -1.19 |
| lg_ind_hist1 | -0.55 |
| lg_res_cap | -0.03 |
| lg_com_cap | -0.06 |
| lg_ind_cap | -0.02 |
| lg_need_hospital | -0.68 |
| lg_need_church | -0.43 |
| lg_road_fund | -1.58 |
| lg_police_fund | -0.35 |
| lg_fire_fund | -0.36 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.31 |
| lg_city_center_x | -0.55 |
| lg_city_center_y | -1.17 |
| lg_pollution_max_x | -4.91 |
| lg_pollution_max_y | -5.03 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -3.68 |
| terrain | -12.53 |
| com_rate | -8.65 |
| kl | 13.96 |
| elbo | -4250.02 |
