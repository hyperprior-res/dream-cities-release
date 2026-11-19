## sf_50m_full_s2_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "train_eval", "seed": 20261147, "n_trajectories": 2000, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 393, "open_loop": 107}, "transitions_by_source": {"state_reading": 1552, "open_loop": 448}, "key": "86f90caf2eb79469", "split": "train_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.325 | 0.318 | 0.321 | 0.309 to 0.334 | 0.218 | 0.206 | 0.212 | 0.186 to 0.242 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.135 | 0.135 | 0.135 | 0.125 to 0.144 | 0.055 | 0.054 | 0.054 | 0.048 to 0.062 |
| all (2000) | engine, other seed (yardstick) | 0.341 | 0.342 | 0.342 | 0.328 to 0.356 | 0.234 | 0.232 | 0.233 | 0.205 to 0.265 |
| state-reading (1552) | model T=1 (one sample) | 0.330 | 0.321 | 0.326 | 0.313 to 0.339 | 0.230 | 0.214 | 0.222 | 0.194 to 0.256 |
| state-reading (1552) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1552) | nearest neighbour (sampled) | 0.138 | 0.136 | 0.137 | 0.127 to 0.146 | 0.058 | 0.056 | 0.057 | 0.050 to 0.065 |
| state-reading (1552) | engine, other seed (yardstick) | 0.345 | 0.346 | 0.346 | 0.332 to 0.361 | 0.241 | 0.239 | 0.240 | 0.210 to 0.275 |
| open-loop (448) | model T=1 (one sample) | 0.304 | 0.304 | 0.304 | 0.285 to 0.322 | 0.179 | 0.173 | 0.176 | 0.145 to 0.209 |
| open-loop (448) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (448) | nearest neighbour (sampled) | 0.126 | 0.128 | 0.127 | 0.117 to 0.137 | 0.046 | 0.046 | 0.046 | 0.038 to 0.055 |
| open-loop (448) | engine, other seed (yardstick) | 0.324 | 0.327 | 0.325 | 0.305 to 0.346 | 0.208 | 0.206 | 0.207 | 0.173 to 0.243 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 0.414 | 0.197 | 0.001 / 0.000 / 0.012 | 0.010 / 0.007 / 0.010 | 0.387 / 0.386 |
| all plans | 500 | 12 | 0.440 | 0.190 | 0.052 / 0.003 / 0.314 | 0.047 / 0.030 / 0.091 | 0.317 / 0.393 |
| all plans | 500 | 24 | 0.613 | 0.188 | 0.165 / 0.006 / 0.521 | 0.095 / 0.045 / 0.163 | 0.273 / 0.389 |
| state-reading plans | 393 | 1 | 0.464 | 0.217 | 0.002 / 0.000 / 0.018 | 0.010 / 0.007 / 0.010 | 0.420 / 0.422 |
| state-reading plans | 393 | 12 | 0.434 | 0.188 | 0.055 / 0.004 / 0.369 | 0.046 / 0.030 / 0.089 | 0.336 / 0.410 |
| state-reading plans | 393 | 24 | 0.616 | 0.191 | 0.184 / 0.006 / 0.714 | 0.094 / 0.046 / 0.154 | 0.288 / 0.399 |
| open-loop plans | 107 | 1 | 0.403 | 0.179 | 0.000 / 0.000 / 0.000 | 0.010 / 0.007 / 0.010 | 0.237 / 0.231 |
| open-loop plans | 107 | 12 | 0.563 | 0.229 | 0.042 / 0.003 / 0.111 | 0.050 / 0.033 / 0.120 | 0.240 / 0.324 |
| open-loop plans | 107 | 24 | 0.776 | 0.222 | 0.104 / 0.005 / 0.164 | 0.097 / 0.044 / 0.212 | 0.219 / 0.349 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2327 | 0.2118 | 0.910 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3416 | 0.3212 | 0.940 |
| pop_mae_12m | 4042.1200 | 1205.2800 | 1965.3100 | 0.732 |
| funds_mae_12m | 4895.7120 | 42.3740 | 699.5280 | 0.865 |
| res_valve_mae_12m | 727.9660 | 164.2480 | 248.9878 | 0.850 |
| com_valve_mae_12m | 1218.4420 | 375.0420 | 531.6888 | 0.814 |
| ind_valve_mae_12m | 1013.6780 | 255.3760 | 372.7790 | 0.845 |
| pop_median_rel_12m | 0.0912 | 0.0300 | 0.0468 | 0.726 |
| funds_median_rel_12m | 0.3144 | 0.0035 | 0.0518 | 0.845 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.3932 | 0.3166 | 0.805 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4035 | 0.3288 | 0.815 |
| pop_mae_24m | 7303.8400 | 1875.9200 | 4131.4650 | 0.584 |
| funds_mae_24m | 6681.5280 | 66.8000 | 1543.7410 | 0.777 |
| res_valve_mae_24m | 754.9140 | 218.6320 | 386.1298 | 0.688 |
| com_valve_mae_24m | 1165.3700 | 492.2540 | 729.9680 | 0.647 |
| ind_valve_mae_24m | 1086.8340 | 371.0880 | 578.6955 | 0.710 |
| pop_median_rel_24m | 0.1626 | 0.0454 | 0.0954 | 0.573 |
| funds_median_rel_24m | 0.5206 | 0.0057 | 0.1649 | 0.691 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.3888 | 0.2733 | 0.703 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.3918 | 0.2807 | 0.716 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1543.7 | 66.8 | 6681.5 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 386.1 | 218.6 | 754.9 |
| com_valve | 730.0 | 492.3 | 1165.4 |
| ind_valve | 578.7 | 371.1 | 1086.8 |
| pop | 4131.5 | 1875.9 | 7303.8 |
| res_pop | 93.1 | 44.7 | 158.4 |
| com_pop | 8.8 | 5.2 | 13.9 |
| ind_pop | 12.2 | 5.6 | 18.8 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 68.7 | 27.9 | 107.4 |
| tax_fund | 109.6 | 54.7 | 1326.7 |
| road_spend | 69.6 | 11.9 | 835.4 |
| fire_spend | 41.3 | 2.6 | 431.3 |
| police_spend | 59.4 | 3.8 | 545.1 |
| powered_zones | 10.1 | 2.8 | 10.6 |
| unpowered_zones | 8.4 | 2.6 | 8.5 |
| coal_plants | 0.4 | 0.0 | 0.4 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 67.2 | 15.2 | 90.0 |

#### Per scalar at 24 months, state-reading plans (393): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1552.9 | 62.1 | 7190.6 |
| tax | 0.0 | 0.0 | 1.1 |
| res_valve | 339.0 | 160.2 | 525.9 |
| com_valve | 762.9 | 495.6 | 1123.2 |
| ind_valve | 632.8 | 397.1 | 1024.3 |
| pop | 4177.9 | 1889.8 | 6800.2 |
| res_pop | 92.2 | 44.3 | 148.6 |
| com_pop | 8.8 | 5.1 | 12.6 |
| ind_pop | 12.4 | 5.6 | 18.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 70.6 | 27.1 | 100.2 |
| tax_fund | 106.0 | 50.6 | 1281.6 |
| road_spend | 67.7 | 11.6 | 824.6 |
| fire_spend | 43.2 | 3.0 | 413.3 |
| police_spend | 60.3 | 3.5 | 516.9 |
| powered_zones | 10.5 | 2.5 | 12.5 |
| unpowered_zones | 8.6 | 2.4 | 9.0 |
| coal_plants | 0.4 | 0.0 | 0.4 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 67.4 | 14.7 | 101.0 |

#### Per scalar at 24 months, open-loop plans (107): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1510.2 | 84.1 | 4811.7 |
| tax | 0.0 | 0.0 | 4.5 |
| res_valve | 559.2 | 433.2 | 1596.0 |
| com_valve | 609.1 | 480.1 | 1320.4 |
| ind_valve | 380.1 | 275.6 | 1316.6 |
| pop | 3960.8 | 1825.0 | 9153.8 |
| res_pop | 96.2 | 46.2 | 194.5 |
| com_pop | 9.1 | 5.4 | 18.4 |
| ind_pop | 11.4 | 5.4 | 20.9 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 61.9 | 30.9 | 133.7 |
| tax_fund | 123.1 | 69.9 | 1492.4 |
| road_spend | 76.8 | 13.0 | 875.0 |
| fire_spend | 34.0 | 0.9 | 497.3 |
| police_spend | 56.1 | 4.7 | 648.6 |
| powered_zones | 8.8 | 3.8 | 3.7 |
| unpowered_zones | 7.5 | 3.2 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 66.7 | 17.0 | 49.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.254 | 0.858 |
| traffic | 1.013 | 0.787 |
| pollution | 1.776 | 0.738 |
| land_value | 0.766 | 0.398 |
| crime | 1.295 | 0.597 |
| rate_of_growth | 1.161 | 0.852 |
| fire_coverage | 5.788 | 0.146 |
| police_coverage | 2.182 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.616 | 0.295 | 0.399 | 0.384 to 0.412 | 0.564 | 0.165 | 0.256 | 0.220 to 0.295 |
| all (2000) | nearest neighbour (mode) | 0.284 | 0.017 | 0.032 | 0.026 to 0.039 | 0.289 | 0.036 | 0.065 | 0.056 to 0.075 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.317 | 0.001 | 0.007 |
| all plans | 12 | 0.330 | 0.059 | 0.038 |
| all plans | 24 | 0.478 | 0.200 | 0.088 |
| state-reading plans | 1 | 0.347 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.324 | 0.059 | 0.037 |
| state-reading plans | 24 | 0.484 | 0.215 | 0.090 |
| open-loop plans | 1 | 0.312 | 0.000 | 0.007 |
| open-loop plans | 12 | 0.435 | 0.066 | 0.043 |
| open-loop plans | 24 | 0.580 | 0.121 | 0.088 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -259.53 |
| tile_cat | -36.30 |
| flags | -16.94 |
| power | -3.99 |
| half | -3186.35 |
| eighth | -45.17 |
| scalars_s2 | -5.53 |
| build_cost | -0.92 |
| scalars | -11.43 |
| ledger | -9.24 |
| bk | -15.13 |
| sc_res_pop | -1.59 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.55 |
| sc_res_valve | -1.06 |
| sc_com_valve | -2.07 |
| sc_ind_valve | -1.00 |
| sc_score | -0.28 |
| sc_funds | -0.70 |
| sc_tax_fund | -0.37 |
| sc_road_spend | -0.25 |
| sc_fire_spend | -0.08 |
| sc_police_spend | -0.09 |
| lg_sprite_cycle | -0.37 |
| lg_total_pop | -1.42 |
| lg_res_hist0 | -0.46 |
| lg_res_hist1 | -0.05 |
| lg_com_hist0 | -0.31 |
| lg_com_hist1 | -0.00 |
| lg_ind_hist0 | -0.28 |
| lg_ind_hist1 | -0.02 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.05 |
| lg_road_fund | -0.24 |
| lg_police_fund | -0.05 |
| lg_fire_fund | -0.04 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.08 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.01 |
| lg_pollution_max_x | -1.91 |
| lg_pollution_max_y | -1.62 |
| lg_flood_count | -0.01 |
| lg_abs_dist | -2.24 |
| terrain | -8.74 |
| com_rate | -3.62 |
| kl | 14.16 |
| elbo | -3596.38 |
