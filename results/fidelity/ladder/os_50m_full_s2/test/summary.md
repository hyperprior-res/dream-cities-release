## os_50m_full_s2_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.305 | 0.286 | 0.295 | 0.275 to 0.314 | 0.193 | 0.165 | 0.178 | 0.150 to 0.208 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.314 | 0.295 | 0.304 | 0.284 to 0.323 | 0.210 | 0.179 | 0.193 | 0.161 to 0.228 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.274 | 0.256 | 0.265 | 0.245 to 0.282 | 0.139 | 0.120 | 0.129 | 0.105 to 0.152 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.498 | 0.203 | 0.003 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.373 / 0.393 |
| all plans | 700 | 12 | 0.397 | 0.154 | 0.036 / 0.003 / 0.400 | 0.050 / 0.027 / 0.112 | 0.376 / 0.423 |
| all plans | 700 | 24 | 0.506 | 0.176 | 0.060 / 0.005 / 0.614 | 0.075 / 0.039 / 0.159 | 0.340 / 0.405 |
| state-reading plans | 527 | 1 | 0.490 | 0.201 | 0.005 / 0.000 / 0.018 | 0.008 / 0.006 / 0.008 | 0.418 / 0.431 |
| state-reading plans | 527 | 12 | 0.398 | 0.162 | 0.040 / 0.003 / 0.505 | 0.050 / 0.028 / 0.106 | 0.401 / 0.442 |
| state-reading plans | 527 | 24 | 0.519 | 0.194 | 0.067 / 0.005 / 0.776 | 0.075 / 0.039 / 0.155 | 0.358 / 0.415 |
| open-loop plans | 173 | 1 | 0.592 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.156 / 0.208 |
| open-loop plans | 173 | 12 | 0.670 | 0.133 | 0.024 / 0.002 / 0.054 | 0.050 / 0.026 / 0.133 | 0.283 / 0.349 |
| open-loop plans | 173 | 24 | 1.127 | 0.128 | 0.040 / 0.005 / 0.111 | 0.075 / 0.039 / 0.168 | 0.275 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.495 | 0.189 | 0.003 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.380 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.405 | 0.152 | 0.038 / 0.002 / 0.433 | 0.051 / 0.030 / 0.105 | 0.380 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.519 | 0.169 | 0.066 / 0.005 / 0.668 | 0.083 / 0.043 / 0.156 | 0.346 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1778 | 0.865 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2953 | 0.925 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2143.0107 | 0.652 |
| funds_mae_12m | 5673.7400 | 40.0829 | 566.2330 | 0.907 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 193.7455 | 0.826 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 530.3896 | 0.880 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 344.0377 | 0.878 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0499 | 0.730 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0362 | 0.916 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3763 | 0.890 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3688 | 0.865 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3654.3464 | 0.640 |
| funds_mae_24m | 7303.4900 | 72.8329 | 731.0229 | 0.909 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 308.5345 | 0.764 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 719.5275 | 0.573 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 637.4852 | 0.622 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0751 | 0.702 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0601 | 0.910 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3397 | 0.839 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3338 | 0.823 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 731.0 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 308.5 | 160.2 | 787.9 |
| com_valve | 719.5 | 507.1 | 1004.7 |
| ind_valve | 637.5 | 454.2 | 939.2 |
| pop | 3654.3 | 1749.1 | 7044.7 |
| res_pop | 71.7 | 37.1 | 135.5 |
| com_pop | 8.2 | 5.0 | 12.3 |
| ind_pop | 12.3 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 82.1 | 26.8 | 89.0 |
| tax_fund | 132.5 | 53.9 | 1490.0 |
| road_spend | 73.5 | 9.0 | 638.2 |
| fire_spend | 28.9 | 1.3 | 473.1 |
| police_spend | 190.8 | 3.4 | 618.5 |
| powered_zones | 7.8 | 0.9 | 9.0 |
| unpowered_zones | 4.8 | 0.8 | 7.1 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.3 |
| road_total | 48.3 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 739.5 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 268.6 | 128.0 | 549.2 |
| com_valve | 775.5 | 545.4 | 967.3 |
| ind_valve | 701.1 | 502.9 | 866.6 |
| pop | 3693.3 | 1820.5 | 6670.1 |
| res_pop | 72.0 | 37.8 | 127.8 |
| com_pop | 8.1 | 5.0 | 11.7 |
| ind_pop | 12.6 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 81.9 | 27.8 | 83.7 |
| tax_fund | 124.6 | 49.4 | 1392.4 |
| road_spend | 69.6 | 8.4 | 639.3 |
| fire_spend | 26.5 | 1.4 | 467.7 |
| police_spend | 234.9 | 4.3 | 609.4 |
| powered_zones | 8.1 | 1.2 | 11.7 |
| unpowered_zones | 5.5 | 1.1 | 7.9 |
| coal_plants | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.0 | 0.4 |
| road_total | 48.3 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 705.1 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 430.1 | 258.1 | 1515.1 |
| com_valve | 548.9 | 390.3 | 1118.5 |
| ind_valve | 443.7 | 305.8 | 1160.1 |
| pop | 3535.6 | 1531.7 | 8185.8 |
| res_pop | 70.7 | 35.0 | 158.8 |
| com_pop | 8.4 | 4.9 | 14.2 |
| ind_pop | 11.5 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 82.7 | 23.7 | 105.2 |
| tax_fund | 156.3 | 67.8 | 1787.4 |
| road_spend | 85.1 | 10.5 | 634.9 |
| fire_spend | 35.9 | 0.9 | 489.5 |
| police_spend | 56.4 | 0.8 | 646.2 |
| powered_zones | 6.6 | 0.0 | 0.5 |
| unpowered_zones | 2.6 | 0.0 | 4.8 |
| coal_plants | 0.1 | 0.0 | 0.2 |
| nuclear_plants | 0.2 | 0.0 | 0.1 |
| road_total | 48.3 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.073 | 0.845 |
| traffic | 0.991 | 0.765 |
| pollution | 1.577 | 0.703 |
| land_value | 0.624 | 0.336 |
| crime | 1.007 | 0.580 |
| rate_of_growth | 1.011 | 0.835 |
| fire_coverage | 1.088 | 0.125 |
| police_coverage | 1.052 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.530 | 0.261 | 0.350 | 0.328 to 0.369 | 0.398 | 0.131 | 0.198 | 0.163 to 0.235 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.394 | 0.002 | 0.006 |
| all plans | 12 | 0.310 | 0.029 | 0.044 |
| all plans | 24 | 0.412 | 0.063 | 0.063 |
| state-reading plans | 1 | 0.389 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.310 | 0.030 | 0.044 |
| state-reading plans | 24 | 0.426 | 0.073 | 0.063 |
| open-loop plans | 1 | 0.460 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.539 | 0.025 | 0.043 |
| open-loop plans | 24 | 0.967 | 0.044 | 0.062 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -208.36 |
| tile_cat | -28.71 |
| flags | -14.49 |
| power | -2.64 |
| half | -2283.47 |
| eighth | -33.07 |
| scalars_s2 | -5.15 |
| build_cost | -0.86 |
| scalars | -12.15 |
| ledger | -13.54 |
| bk | -20.53 |
| sc_res_pop | -1.45 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.14 |
| sc_powered_zones | -0.03 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.36 |
| sc_res_valve | -1.07 |
| sc_com_valve | -2.04 |
| sc_ind_valve | -1.06 |
| sc_score | -0.54 |
| sc_funds | -0.86 |
| sc_tax_fund | -0.47 |
| sc_road_spend | -0.62 |
| sc_fire_spend | -0.15 |
| sc_police_spend | -0.19 |
| lg_sprite_cycle | -0.77 |
| lg_total_pop | -1.55 |
| lg_res_hist0 | -0.29 |
| lg_res_hist1 | -0.63 |
| lg_com_hist0 | -0.09 |
| lg_com_hist1 | -0.20 |
| lg_ind_hist0 | -0.08 |
| lg_ind_hist1 | -0.24 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.65 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.11 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.17 |
| lg_pollution_max_y | -3.10 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -4.69 |
| com_rate | -3.24 |
| kl | 14.09 |
| elbo | -2619.30 |
