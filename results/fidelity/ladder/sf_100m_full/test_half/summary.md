## sf_100m_full_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.269 | 0.287 | 0.277 | 0.256 to 0.298 | 0.159 | 0.176 | 0.167 | 0.141 to 0.194 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.277 | 0.295 | 0.286 | 0.263 to 0.309 | 0.171 | 0.188 | 0.179 | 0.149 to 0.210 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.240 | 0.259 | 0.249 | 0.229 to 0.269 | 0.121 | 0.137 | 0.129 | 0.107 to 0.148 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.588 | 0.203 | 0.003 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.364 / 0.393 |
| all plans | 700 | 12 | 0.429 | 0.154 | 0.032 / 0.003 / 0.400 | 0.041 / 0.027 / 0.112 | 0.350 / 0.423 |
| all plans | 700 | 24 | 0.506 | 0.176 | 0.059 / 0.005 / 0.614 | 0.067 / 0.039 / 0.159 | 0.316 / 0.405 |
| state-reading plans | 527 | 1 | 0.568 | 0.201 | 0.004 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.408 / 0.431 |
| state-reading plans | 527 | 12 | 0.424 | 0.162 | 0.036 / 0.003 / 0.505 | 0.041 / 0.028 / 0.106 | 0.374 / 0.442 |
| state-reading plans | 527 | 24 | 0.508 | 0.194 | 0.065 / 0.005 / 0.776 | 0.066 / 0.039 / 0.155 | 0.335 / 0.415 |
| open-loop plans | 173 | 1 | 0.619 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.158 / 0.208 |
| open-loop plans | 173 | 12 | 0.702 | 0.133 | 0.021 / 0.002 / 0.054 | 0.040 / 0.026 / 0.133 | 0.263 / 0.349 |
| open-loop plans | 173 | 24 | 0.965 | 0.128 | 0.043 / 0.005 / 0.111 | 0.070 / 0.039 / 0.168 | 0.251 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.536 | 0.189 | 0.003 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.374 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.428 | 0.152 | 0.034 / 0.002 / 0.433 | 0.041 / 0.030 / 0.105 | 0.352 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.497 | 0.169 | 0.069 / 0.005 / 0.668 | 0.066 / 0.043 / 0.156 | 0.321 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1668 | 0.811 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2774 | 0.869 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 1747.6214 | 0.786 |
| funds_mae_12m | 5673.7400 | 40.0829 | 606.5100 | 0.899 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 212.5452 | 0.793 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 542.1900 | 0.864 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 349.5596 | 0.870 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0410 | 0.836 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0320 | 0.927 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3498 | 0.828 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3495 | 0.820 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3144.8571 | 0.736 |
| funds_mae_24m | 7303.4900 | 72.8329 | 770.6113 | 0.903 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 315.7570 | 0.752 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 654.5345 | 0.704 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 549.4814 | 0.804 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0673 | 0.767 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0587 | 0.912 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3159 | 0.780 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3152 | 0.777 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 770.6 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 315.8 | 160.2 | 787.9 |
| com_valve | 654.5 | 507.1 | 1004.7 |
| ind_valve | 549.5 | 454.2 | 939.2 |
| pop | 3144.9 | 1749.1 | 7044.7 |
| res_pop | 71.1 | 37.1 | 135.5 |
| com_pop | 7.2 | 5.0 | 12.3 |
| ind_pop | 10.3 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 55.5 | 26.8 | 89.0 |
| tax_fund | 145.5 | 53.9 | 1490.0 |
| road_spend | 80.9 | 9.0 | 638.2 |
| fire_spend | 39.0 | 1.3 | 473.1 |
| police_spend | 54.0 | 3.4 | 618.5 |
| powered_zones | 6.6 | 0.9 | 9.0 |
| unpowered_zones | 5.0 | 0.8 | 7.1 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 52.6 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 729.6 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 270.8 | 128.0 | 549.2 |
| com_valve | 697.3 | 545.4 | 967.3 |
| ind_valve | 610.7 | 502.9 | 866.6 |
| pop | 3170.1 | 1820.5 | 6670.1 |
| res_pop | 69.2 | 37.8 | 127.8 |
| com_pop | 7.2 | 5.0 | 11.7 |
| ind_pop | 10.4 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 57.8 | 27.8 | 83.7 |
| tax_fund | 133.4 | 49.4 | 1392.4 |
| road_spend | 77.0 | 8.4 | 639.3 |
| fire_spend | 36.3 | 1.4 | 467.7 |
| police_spend | 53.7 | 4.3 | 609.4 |
| powered_zones | 7.5 | 1.2 | 11.7 |
| unpowered_zones | 5.7 | 1.1 | 7.9 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 52.8 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 895.5 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 452.8 | 258.1 | 1515.1 |
| com_valve | 524.3 | 390.3 | 1118.5 |
| ind_valve | 363.0 | 305.8 | 1160.1 |
| pop | 3068.0 | 1531.7 | 8185.8 |
| res_pop | 77.0 | 35.0 | 158.8 |
| com_pop | 7.3 | 4.9 | 14.2 |
| ind_pop | 9.8 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 48.3 | 23.7 | 105.2 |
| tax_fund | 182.1 | 67.8 | 1787.4 |
| road_spend | 92.8 | 10.5 | 634.9 |
| fire_spend | 47.2 | 0.9 | 489.5 |
| police_spend | 54.9 | 0.8 | 646.2 |
| powered_zones | 4.1 | 0.0 | 0.5 |
| unpowered_zones | 3.0 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.4 | 0.0 | 0.1 |
| road_total | 51.7 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.171 | 0.845 |
| traffic | 0.965 | 0.765 |
| pollution | 1.679 | 0.703 |
| land_value | 0.649 | 0.336 |
| crime | 1.082 | 0.580 |
| rate_of_growth | 1.105 | 0.835 |
| fire_coverage | 0.828 | 0.125 |
| police_coverage | 0.790 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.567 | 0.263 | 0.359 | 0.337 to 0.379 | 0.493 | 0.141 | 0.220 | 0.181 to 0.260 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.460 | 0.001 | 0.005 |
| all plans | 12 | 0.297 | 0.025 | 0.030 |
| all plans | 24 | 0.361 | 0.062 | 0.051 |
| state-reading plans | 1 | 0.444 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.296 | 0.025 | 0.030 |
| state-reading plans | 24 | 0.368 | 0.066 | 0.051 |
| open-loop plans | 1 | 0.446 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.454 | 0.023 | 0.030 |
| open-loop plans | 24 | 0.617 | 0.047 | 0.052 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -206.62 |
| tile_cat | -28.68 |
| flags | -13.81 |
| power | -1.92 |
| half | -2241.54 |
| eighth | -32.24 |
| scalars_s2 | -5.65 |
| build_cost | -1.05 |
| scalars | -12.82 |
| ledger | -12.90 |
| bk | -20.07 |
| sc_res_pop | -1.77 |
| sc_com_pop | -0.16 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.07 |
| sc_unpowered_zones | -0.09 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.38 |
| sc_res_valve | -0.99 |
| sc_com_valve | -2.07 |
| sc_ind_valve | -1.32 |
| sc_score | -0.49 |
| sc_funds | -1.02 |
| sc_tax_fund | -0.45 |
| sc_road_spend | -0.59 |
| sc_fire_spend | -0.11 |
| sc_police_spend | -0.13 |
| lg_sprite_cycle | -0.75 |
| lg_total_pop | -1.50 |
| lg_res_hist0 | -0.38 |
| lg_res_hist1 | -0.38 |
| lg_com_hist0 | -0.07 |
| lg_com_hist1 | -0.15 |
| lg_ind_hist0 | -0.09 |
| lg_ind_hist1 | -0.15 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.60 |
| lg_police_fund | -0.10 |
| lg_fire_fund | -0.08 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.08 |
| lg_pollution_max_y | -3.09 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -4.61 |
| com_rate | -1.93 |
| kl | 15.22 |
| elbo | -2573.36 |
