## os_50m_full_36m_samples_006000000_dec-a

samples consumed: 6000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "ad75d197abf1cc74", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.298 | 0.282 | 0.290 | 0.270 to 0.308 | 0.191 | 0.171 | 0.180 | 0.152 to 0.211 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.139 | 0.048 | 0.050 | 0.049 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.305 | 0.289 | 0.297 | 0.275 to 0.316 | 0.203 | 0.182 | 0.192 | 0.159 to 0.227 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.131 | 0.131 | 0.131 | 0.120 to 0.141 | 0.050 | 0.052 | 0.051 | 0.045 to 0.056 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.277 | 0.257 | 0.267 | 0.248 to 0.284 | 0.152 | 0.135 | 0.143 | 0.119 to 0.165 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.119 | 0.122 | 0.120 | 0.106 to 0.134 | 0.043 | 0.047 | 0.045 | 0.037 to 0.052 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.844 | 0.203 | 0.009 / 0.000 / 0.013 | 0.010 / 0.006 / 0.007 | 0.376 / 0.393 |
| all plans | 700 | 12 | 0.654 | 0.154 | 0.059 / 0.003 / 0.400 | 0.052 / 0.027 / 0.112 | 0.384 / 0.423 |
| all plans | 700 | 24 | 0.683 | 0.176 | 0.080 / 0.005 / 0.614 | 0.067 / 0.039 / 0.159 | 0.352 / 0.405 |
| state-reading plans | 527 | 1 | 0.796 | 0.201 | 0.012 / 0.000 / 0.018 | 0.010 / 0.006 / 0.008 | 0.420 / 0.431 |
| state-reading plans | 527 | 12 | 0.662 | 0.162 | 0.077 / 0.003 / 0.505 | 0.051 / 0.028 / 0.106 | 0.409 / 0.442 |
| state-reading plans | 527 | 24 | 0.699 | 0.194 | 0.113 / 0.005 / 0.776 | 0.065 / 0.039 / 0.155 | 0.370 / 0.415 |
| open-loop plans | 173 | 1 | 1.202 | 0.226 | 0.000 / 0.000 / 0.000 | 0.009 / 0.005 / 0.007 | 0.164 / 0.208 |
| open-loop plans | 173 | 12 | 0.887 | 0.133 | 0.013 / 0.002 / 0.054 | 0.057 / 0.026 / 0.133 | 0.290 / 0.349 |
| open-loop plans | 173 | 24 | 1.098 | 0.128 | 0.023 / 0.005 / 0.111 | 0.076 / 0.039 / 0.168 | 0.287 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.822 | 0.189 | 0.009 / 0.000 / 0.015 | 0.010 / 0.006 / 0.009 | 0.385 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.665 | 0.152 | 0.063 / 0.002 / 0.433 | 0.053 / 0.030 / 0.105 | 0.386 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.679 | 0.169 | 0.089 / 0.005 / 0.668 | 0.069 / 0.043 / 0.156 | 0.356 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1803 | 0.877 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2900 | 0.908 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2109.6750 | 0.664 |
| funds_mae_12m | 5673.7400 | 40.0829 | 915.4741 | 0.845 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 219.9130 | 0.780 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 573.3046 | 0.822 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 342.1796 | 0.881 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0522 | 0.704 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0589 | 0.859 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3844 | 0.910 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3779 | 0.886 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3152.3893 | 0.735 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1046.5766 | 0.865 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 318.5943 | 0.748 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 849.2798 | 0.312 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 637.5975 | 0.622 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0673 | 0.767 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0801 | 0.877 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3519 | 0.869 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3471 | 0.856 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1046.6 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 318.6 | 160.2 | 787.9 |
| com_valve | 849.3 | 507.1 | 1004.7 |
| ind_valve | 637.6 | 454.2 | 939.2 |
| pop | 3152.4 | 1749.1 | 7044.7 |
| res_pop | 68.1 | 37.1 | 135.5 |
| com_pop | 8.9 | 5.0 | 12.3 |
| ind_pop | 9.9 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 51.3 | 26.8 | 89.0 |
| tax_fund | 154.1 | 53.9 | 1490.0 |
| road_spend | 80.6 | 9.0 | 638.2 |
| fire_spend | 42.8 | 1.3 | 473.1 |
| police_spend | 70.7 | 3.4 | 618.5 |
| powered_zones | 10.9 | 0.9 | 9.0 |
| unpowered_zones | 6.3 | 0.8 | 7.1 |
| coal_plants | 0.7 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.3 |
| road_total | 58.7 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1158.9 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 277.5 | 128.0 | 549.2 |
| com_valve | 913.2 | 545.4 | 967.3 |
| ind_valve | 701.5 | 502.9 | 866.6 |
| pop | 3079.5 | 1820.5 | 6670.1 |
| res_pop | 68.3 | 37.8 | 127.8 |
| com_pop | 8.4 | 5.0 | 11.7 |
| ind_pop | 10.2 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 53.1 | 27.8 | 83.7 |
| tax_fund | 140.6 | 49.4 | 1392.4 |
| road_spend | 76.8 | 8.4 | 639.3 |
| fire_spend | 42.8 | 1.4 | 467.7 |
| police_spend | 69.2 | 4.3 | 609.4 |
| powered_zones | 12.7 | 1.2 | 11.7 |
| unpowered_zones | 7.1 | 1.1 | 7.9 |
| coal_plants | 0.8 | 0.0 | 0.5 |
| nuclear_plants | 1.0 | 0.0 | 0.4 |
| road_total | 59.6 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 704.4 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 443.8 | 258.1 | 1515.1 |
| com_valve | 654.5 | 390.3 | 1118.5 |
| ind_valve | 443.0 | 305.8 | 1160.1 |
| pop | 3374.3 | 1531.7 | 8185.8 |
| res_pop | 67.4 | 35.0 | 158.8 |
| com_pop | 10.5 | 4.9 | 14.2 |
| ind_pop | 8.8 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 46.1 | 23.7 | 105.2 |
| tax_fund | 195.5 | 67.8 | 1787.4 |
| road_spend | 92.0 | 10.5 | 634.9 |
| fire_spend | 43.0 | 0.9 | 489.5 |
| police_spend | 75.4 | 0.8 | 646.2 |
| powered_zones | 5.2 | 0.0 | 0.5 |
| unpowered_zones | 3.6 | 0.0 | 4.8 |
| coal_plants | 0.3 | 0.0 | 0.2 |
| nuclear_plants | 0.3 | 0.0 | 0.1 |
| road_total | 56.0 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.025 | 0.845 |
| traffic | 0.945 | 0.765 |
| pollution | 1.463 | 0.703 |
| land_value | 0.607 | 0.336 |
| crime | 0.936 | 0.580 |
| rate_of_growth | 1.012 | 0.835 |
| fire_coverage | 0.812 | 0.125 |
| police_coverage | 0.772 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.570 | 0.252 | 0.349 | 0.325 to 0.370 | 0.479 | 0.133 | 0.208 | 0.169 to 0.250 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.556 | 0.004 | 0.006 |
| all plans | 12 | 0.429 | 0.040 | 0.048 |
| all plans | 24 | 0.464 | 0.069 | 0.053 |
| state-reading plans | 1 | 0.510 | 0.005 | 0.007 |
| state-reading plans | 12 | 0.437 | 0.056 | 0.048 |
| state-reading plans | 24 | 0.482 | 0.099 | 0.051 |
| open-loop plans | 1 | 0.851 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.529 | 0.011 | 0.049 |
| open-loop plans | 24 | 0.611 | 0.019 | 0.061 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -206.59 |
| tile_cat | -28.52 |
| flags | -13.77 |
| power | -2.18 |
| half | -2310.10 |
| eighth | -32.10 |
| scalars_s2 | -7.47 |
| build_cost | -1.34 |
| scalars | -14.60 |
| ledger | -13.01 |
| bk | -20.14 |
| sc_res_pop | -2.41 |
| sc_com_pop | -0.54 |
| sc_ind_pop | -0.57 |
| sc_powered_zones | -0.17 |
| sc_unpowered_zones | -0.27 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.48 |
| sc_res_valve | -0.99 |
| sc_com_valve | -2.09 |
| sc_ind_valve | -1.37 |
| sc_score | -0.46 |
| sc_funds | -0.96 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.57 |
| sc_fire_spend | -0.11 |
| sc_police_spend | -0.12 |
| lg_sprite_cycle | -0.77 |
| lg_total_pop | -1.44 |
| lg_res_hist0 | -0.41 |
| lg_res_hist1 | -0.35 |
| lg_com_hist0 | -0.09 |
| lg_com_hist1 | -0.09 |
| lg_ind_hist0 | -0.12 |
| lg_ind_hist1 | -0.20 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.04 |
| lg_road_fund | -0.58 |
| lg_police_fund | -0.09 |
| lg_fire_fund | -0.08 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.13 |
| lg_pollution_max_y | -3.15 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -4.94 |
| com_rate | -3.16 |
| kl | 13.51 |
| elbo | -2643.83 |

## os_50m_full_36m_samples_012000000_dec-a

samples consumed: 12000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "ad75d197abf1cc74", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.300 | 0.287 | 0.293 | 0.273 to 0.312 | 0.189 | 0.173 | 0.181 | 0.153 to 0.211 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.139 | 0.048 | 0.050 | 0.049 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.307 | 0.293 | 0.300 | 0.278 to 0.321 | 0.202 | 0.184 | 0.193 | 0.160 to 0.228 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.131 | 0.131 | 0.131 | 0.120 to 0.141 | 0.050 | 0.052 | 0.051 | 0.045 to 0.056 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.276 | 0.263 | 0.269 | 0.250 to 0.288 | 0.147 | 0.135 | 0.141 | 0.118 to 0.163 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.119 | 0.122 | 0.120 | 0.106 to 0.134 | 0.043 | 0.047 | 0.045 | 0.037 to 0.052 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.786 | 0.203 | 0.008 / 0.000 / 0.013 | 0.009 / 0.006 / 0.007 | 0.375 / 0.393 |
| all plans | 700 | 12 | 0.632 | 0.154 | 0.054 / 0.003 / 0.400 | 0.051 / 0.027 / 0.112 | 0.380 / 0.423 |
| all plans | 700 | 24 | 0.696 | 0.176 | 0.075 / 0.005 / 0.614 | 0.072 / 0.039 / 0.159 | 0.345 / 0.405 |
| state-reading plans | 527 | 1 | 0.750 | 0.201 | 0.012 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.419 / 0.431 |
| state-reading plans | 527 | 12 | 0.632 | 0.162 | 0.073 / 0.003 / 0.505 | 0.051 / 0.028 / 0.106 | 0.404 / 0.442 |
| state-reading plans | 527 | 24 | 0.699 | 0.194 | 0.101 / 0.005 / 0.776 | 0.070 / 0.039 / 0.155 | 0.363 / 0.415 |
| open-loop plans | 173 | 1 | 1.121 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.162 / 0.208 |
| open-loop plans | 173 | 12 | 1.115 | 0.133 | 0.014 / 0.002 / 0.054 | 0.051 / 0.026 / 0.133 | 0.288 / 0.349 |
| open-loop plans | 173 | 24 | 1.601 | 0.128 | 0.020 / 0.005 / 0.111 | 0.079 / 0.039 / 0.168 | 0.280 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.757 | 0.189 | 0.008 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.381 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.634 | 0.152 | 0.059 / 0.002 / 0.433 | 0.053 / 0.030 / 0.105 | 0.383 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.679 | 0.169 | 0.082 / 0.005 / 0.668 | 0.077 / 0.043 / 0.156 | 0.350 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1806 | 0.878 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2933 | 0.919 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2164.4571 | 0.645 |
| funds_mae_12m | 5673.7400 | 40.0829 | 846.8334 | 0.857 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 225.8959 | 0.770 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 548.6662 | 0.855 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 340.1237 | 0.884 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0508 | 0.720 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0543 | 0.871 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3798 | 0.899 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3738 | 0.877 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3532.1429 | 0.663 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1009.3345 | 0.870 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 323.5768 | 0.740 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 803.8002 | 0.404 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 605.7318 | 0.688 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0723 | 0.725 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0750 | 0.885 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3445 | 0.851 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3402 | 0.839 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1009.3 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 323.6 | 160.2 | 787.9 |
| com_valve | 803.8 | 507.1 | 1004.7 |
| ind_valve | 605.7 | 454.2 | 939.2 |
| pop | 3532.1 | 1749.1 | 7044.7 |
| res_pop | 77.4 | 37.1 | 135.5 |
| com_pop | 9.4 | 5.0 | 12.3 |
| ind_pop | 11.0 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 67.8 | 26.8 | 89.0 |
| tax_fund | 158.8 | 53.9 | 1490.0 |
| road_spend | 84.5 | 9.0 | 638.2 |
| fire_spend | 42.7 | 1.3 | 473.1 |
| police_spend | 74.4 | 3.4 | 618.5 |
| powered_zones | 12.7 | 0.9 | 9.0 |
| unpowered_zones | 6.6 | 0.8 | 7.1 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.3 |
| road_total | 54.0 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1120.0 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 288.0 | 128.0 | 549.2 |
| com_valve | 852.4 | 545.4 | 967.3 |
| ind_valve | 667.8 | 502.9 | 866.6 |
| pop | 3440.6 | 1820.5 | 6670.1 |
| res_pop | 76.8 | 37.8 | 127.8 |
| com_pop | 8.8 | 5.0 | 11.7 |
| ind_pop | 11.2 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 68.0 | 27.8 | 83.7 |
| tax_fund | 146.7 | 49.4 | 1392.4 |
| road_spend | 82.6 | 8.4 | 639.3 |
| fire_spend | 40.8 | 1.4 | 467.7 |
| police_spend | 72.4 | 4.3 | 609.4 |
| powered_zones | 13.7 | 1.2 | 11.7 |
| unpowered_zones | 7.4 | 1.1 | 7.9 |
| coal_plants | 0.7 | 0.0 | 0.5 |
| nuclear_plants | 1.0 | 0.0 | 0.4 |
| road_total | 54.8 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 672.1 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 432.0 | 258.1 | 1515.1 |
| com_valve | 655.7 | 390.3 | 1118.5 |
| ind_valve | 416.7 | 305.8 | 1160.1 |
| pop | 3811.0 | 1531.7 | 8185.8 |
| res_pop | 79.0 | 35.0 | 158.8 |
| com_pop | 11.2 | 4.9 | 14.2 |
| ind_pop | 10.4 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 67.3 | 23.7 | 105.2 |
| tax_fund | 195.6 | 67.8 | 1787.4 |
| road_spend | 90.3 | 10.5 | 634.9 |
| fire_spend | 48.7 | 0.9 | 489.5 |
| police_spend | 80.5 | 0.8 | 646.2 |
| powered_zones | 9.6 | 0.0 | 0.5 |
| unpowered_zones | 4.4 | 0.0 | 4.8 |
| coal_plants | 0.3 | 0.0 | 0.2 |
| nuclear_plants | 0.4 | 0.0 | 0.1 |
| road_total | 51.7 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.079 | 0.845 |
| traffic | 0.932 | 0.765 |
| pollution | 1.443 | 0.703 |
| land_value | 0.615 | 0.336 |
| crime | 0.973 | 0.580 |
| rate_of_growth | 1.041 | 0.835 |
| fire_coverage | 0.798 | 0.125 |
| police_coverage | 0.907 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.550 | 0.262 | 0.355 | 0.331 to 0.377 | 0.436 | 0.136 | 0.207 | 0.169 to 0.248 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.505 | 0.003 | 0.005 |
| all plans | 12 | 0.401 | 0.037 | 0.045 |
| all plans | 24 | 0.464 | 0.066 | 0.055 |
| state-reading plans | 1 | 0.479 | 0.004 | 0.005 |
| state-reading plans | 12 | 0.403 | 0.052 | 0.046 |
| state-reading plans | 24 | 0.472 | 0.093 | 0.053 |
| open-loop plans | 1 | 0.828 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.650 | 0.010 | 0.044 |
| open-loop plans | 24 | 0.946 | 0.016 | 0.062 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -199.89 |
| tile_cat | -27.71 |
| flags | -13.72 |
| power | -2.22 |
| half | -2275.56 |
| eighth | -30.80 |
| scalars_s2 | -7.06 |
| build_cost | -1.30 |
| scalars | -14.71 |
| ledger | -14.14 |
| bk | -21.79 |
| sc_res_pop | -2.26 |
| sc_com_pop | -0.44 |
| sc_ind_pop | -0.47 |
| sc_powered_zones | -0.16 |
| sc_unpowered_zones | -0.24 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.45 |
| sc_res_valve | -1.04 |
| sc_com_valve | -2.18 |
| sc_ind_valve | -1.68 |
| sc_score | -0.43 |
| sc_funds | -1.06 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.54 |
| sc_fire_spend | -0.13 |
| sc_police_spend | -0.13 |
| lg_sprite_cycle | -0.94 |
| lg_total_pop | -1.50 |
| lg_res_hist0 | -0.66 |
| lg_res_hist1 | -0.58 |
| lg_com_hist0 | -0.16 |
| lg_com_hist1 | -0.19 |
| lg_ind_hist0 | -0.22 |
| lg_ind_hist1 | -0.28 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.04 |
| lg_road_fund | -0.57 |
| lg_police_fund | -0.10 |
| lg_fire_fund | -0.10 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.17 |
| lg_pollution_max_y | -3.15 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -4.30 |
| com_rate | -2.93 |
| kl | 14.81 |
| elbo | -2602.10 |

## os_50m_full_36m_samples_018000000_dec-a

samples consumed: 18000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "ad75d197abf1cc74", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.301 | 0.288 | 0.295 | 0.274 to 0.312 | 0.189 | 0.173 | 0.181 | 0.154 to 0.210 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.139 | 0.048 | 0.050 | 0.049 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.309 | 0.295 | 0.302 | 0.281 to 0.322 | 0.202 | 0.186 | 0.194 | 0.162 to 0.228 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.131 | 0.131 | 0.131 | 0.120 to 0.141 | 0.050 | 0.052 | 0.051 | 0.045 to 0.056 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.275 | 0.262 | 0.268 | 0.248 to 0.288 | 0.147 | 0.134 | 0.141 | 0.118 to 0.162 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.119 | 0.122 | 0.120 | 0.106 to 0.134 | 0.043 | 0.047 | 0.045 | 0.037 to 0.052 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.717 | 0.203 | 0.006 / 0.000 / 0.013 | 0.009 / 0.006 / 0.007 | 0.380 / 0.393 |
| all plans | 700 | 12 | 0.592 | 0.154 | 0.046 / 0.003 / 0.400 | 0.056 / 0.027 / 0.112 | 0.378 / 0.423 |
| all plans | 700 | 24 | 0.678 | 0.176 | 0.062 / 0.005 / 0.614 | 0.078 / 0.039 / 0.159 | 0.340 / 0.405 |
| state-reading plans | 527 | 1 | 0.682 | 0.201 | 0.010 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.424 / 0.431 |
| state-reading plans | 527 | 12 | 0.589 | 0.162 | 0.061 / 0.003 / 0.505 | 0.056 / 0.028 / 0.106 | 0.403 / 0.442 |
| state-reading plans | 527 | 24 | 0.678 | 0.194 | 0.084 / 0.005 / 0.776 | 0.074 / 0.039 / 0.155 | 0.358 / 0.415 |
| open-loop plans | 173 | 1 | 0.973 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.167 / 0.208 |
| open-loop plans | 173 | 12 | 1.066 | 0.133 | 0.012 / 0.002 / 0.054 | 0.055 / 0.026 / 0.133 | 0.287 / 0.349 |
| open-loop plans | 173 | 24 | 1.517 | 0.128 | 0.020 / 0.005 / 0.111 | 0.089 / 0.039 / 0.168 | 0.277 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.699 | 0.189 | 0.007 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.388 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.602 | 0.152 | 0.047 / 0.002 / 0.433 | 0.056 / 0.030 / 0.105 | 0.381 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.671 | 0.169 | 0.065 / 0.005 / 0.668 | 0.084 / 0.043 / 0.156 | 0.346 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1811 | 0.880 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2945 | 0.922 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2307.7643 | 0.597 |
| funds_mae_12m | 5673.7400 | 40.0829 | 769.9291 | 0.870 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 233.3970 | 0.757 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 548.9118 | 0.855 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 344.2273 | 0.878 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0557 | 0.662 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0461 | 0.891 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3784 | 0.895 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3724 | 0.873 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3977.3643 | 0.579 |
| funds_mae_24m | 7303.4900 | 72.8329 | 920.9182 | 0.883 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 337.7896 | 0.717 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 804.6039 | 0.402 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 612.7411 | 0.673 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0783 | 0.675 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0616 | 0.907 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3405 | 0.841 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3358 | 0.828 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 920.9 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 337.8 | 160.2 | 787.9 |
| com_valve | 804.6 | 507.1 | 1004.7 |
| ind_valve | 612.7 | 454.2 | 939.2 |
| pop | 3977.4 | 1749.1 | 7044.7 |
| res_pop | 83.8 | 37.1 | 135.5 |
| com_pop | 9.7 | 5.0 | 12.3 |
| ind_pop | 12.4 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 71.6 | 26.8 | 89.0 |
| tax_fund | 161.5 | 53.9 | 1490.0 |
| road_spend | 93.1 | 9.0 | 638.2 |
| fire_spend | 44.2 | 1.3 | 473.1 |
| police_spend | 76.5 | 3.4 | 618.5 |
| powered_zones | 11.4 | 0.9 | 9.0 |
| unpowered_zones | 5.8 | 0.8 | 7.1 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.3 |
| road_total | 50.8 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 969.9 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 292.5 | 128.0 | 549.2 |
| com_valve | 863.7 | 545.4 | 967.3 |
| ind_valve | 672.0 | 502.9 | 866.6 |
| pop | 3824.7 | 1820.5 | 6670.1 |
| res_pop | 82.3 | 37.8 | 127.8 |
| com_pop | 9.0 | 5.0 | 11.7 |
| ind_pop | 12.3 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 71.0 | 27.8 | 83.7 |
| tax_fund | 148.0 | 49.4 | 1392.4 |
| road_spend | 88.9 | 8.4 | 639.3 |
| fire_spend | 43.3 | 1.4 | 467.7 |
| police_spend | 74.6 | 4.3 | 609.4 |
| powered_zones | 12.2 | 1.2 | 11.7 |
| unpowered_zones | 6.5 | 1.1 | 7.9 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.4 |
| road_total | 51.0 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 771.7 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 475.8 | 258.1 | 1515.1 |
| com_valve | 624.5 | 390.3 | 1118.5 |
| ind_valve | 432.4 | 305.8 | 1160.1 |
| pop | 4442.3 | 1531.7 | 8185.8 |
| res_pop | 88.2 | 35.0 | 158.8 |
| com_pop | 11.5 | 4.9 | 14.2 |
| ind_pop | 12.7 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 73.3 | 23.7 | 105.2 |
| tax_fund | 202.7 | 67.8 | 1787.4 |
| road_spend | 105.7 | 10.5 | 634.9 |
| fire_spend | 46.8 | 0.9 | 489.5 |
| police_spend | 82.2 | 0.8 | 646.2 |
| powered_zones | 8.6 | 0.0 | 0.5 |
| unpowered_zones | 3.6 | 0.0 | 4.8 |
| coal_plants | 0.3 | 0.0 | 0.2 |
| nuclear_plants | 0.4 | 0.0 | 0.1 |
| road_total | 50.2 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.111 | 0.845 |
| traffic | 0.935 | 0.765 |
| pollution | 1.434 | 0.703 |
| land_value | 0.618 | 0.336 |
| crime | 0.982 | 0.580 |
| rate_of_growth | 1.068 | 0.835 |
| fire_coverage | 0.957 | 0.125 |
| police_coverage | 0.884 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.534 | 0.264 | 0.353 | 0.330 to 0.374 | 0.405 | 0.136 | 0.204 | 0.166 to 0.244 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.499 | 0.002 | 0.006 |
| all plans | 12 | 0.395 | 0.031 | 0.047 |
| all plans | 24 | 0.475 | 0.062 | 0.069 |
| state-reading plans | 1 | 0.464 | 0.004 | 0.006 |
| state-reading plans | 12 | 0.392 | 0.043 | 0.046 |
| state-reading plans | 24 | 0.478 | 0.082 | 0.066 |
| open-loop plans | 1 | 0.695 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.664 | 0.011 | 0.050 |
| open-loop plans | 24 | 1.023 | 0.018 | 0.077 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -195.80 |
| tile_cat | -27.26 |
| flags | -13.69 |
| power | -2.15 |
| half | -2207.25 |
| eighth | -29.66 |
| scalars_s2 | -6.37 |
| build_cost | -1.23 |
| scalars | -13.86 |
| ledger | -14.55 |
| bk | -22.04 |
| sc_res_pop | -2.00 |
| sc_com_pop | -0.30 |
| sc_ind_pop | -0.31 |
| sc_powered_zones | -0.14 |
| sc_unpowered_zones | -0.20 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.40 |
| sc_res_valve | -1.02 |
| sc_com_valve | -2.09 |
| sc_ind_valve | -1.34 |
| sc_score | -0.51 |
| sc_funds | -0.98 |
| sc_tax_fund | -0.49 |
| sc_road_spend | -0.73 |
| sc_fire_spend | -0.17 |
| sc_police_spend | -0.17 |
| lg_sprite_cycle | -1.74 |
| lg_total_pop | -1.39 |
| lg_res_hist0 | -0.36 |
| lg_res_hist1 | -0.35 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.09 |
| lg_ind_hist0 | -0.09 |
| lg_ind_hist1 | -0.19 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.06 |
| lg_need_church | -0.04 |
| lg_road_fund | -0.75 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.13 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.01 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.35 |
| lg_pollution_max_y | -3.39 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.35 |
| terrain | -3.94 |
| com_rate | -2.39 |
| kl | 15.79 |
| elbo | -2527.58 |

## os_50m_full_36m_samples_024000000_dec-a

samples consumed: 24000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "ad75d197abf1cc74", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.301 | 0.285 | 0.293 | 0.273 to 0.310 | 0.188 | 0.172 | 0.180 | 0.152 to 0.209 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.139 | 0.048 | 0.050 | 0.049 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.308 | 0.292 | 0.300 | 0.279 to 0.320 | 0.200 | 0.184 | 0.192 | 0.160 to 0.225 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.131 | 0.131 | 0.131 | 0.120 to 0.141 | 0.050 | 0.052 | 0.051 | 0.045 to 0.056 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.275 | 0.257 | 0.266 | 0.248 to 0.284 | 0.148 | 0.132 | 0.140 | 0.116 to 0.163 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.119 | 0.122 | 0.120 | 0.106 to 0.134 | 0.043 | 0.047 | 0.045 | 0.037 to 0.052 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.677 | 0.203 | 0.005 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.380 / 0.393 |
| all plans | 700 | 12 | 0.542 | 0.154 | 0.040 / 0.003 / 0.400 | 0.058 / 0.027 / 0.112 | 0.373 / 0.423 |
| all plans | 700 | 24 | 0.670 | 0.176 | 0.056 / 0.005 / 0.614 | 0.096 / 0.039 / 0.159 | 0.332 / 0.405 |
| state-reading plans | 527 | 1 | 0.664 | 0.201 | 0.007 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.424 / 0.431 |
| state-reading plans | 527 | 12 | 0.540 | 0.162 | 0.050 / 0.003 / 0.505 | 0.057 / 0.028 / 0.106 | 0.397 / 0.442 |
| state-reading plans | 527 | 24 | 0.674 | 0.194 | 0.072 / 0.005 / 0.776 | 0.093 / 0.039 / 0.155 | 0.350 / 0.415 |
| open-loop plans | 173 | 1 | 0.956 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.167 / 0.208 |
| open-loop plans | 173 | 12 | 0.949 | 0.133 | 0.015 / 0.002 / 0.054 | 0.062 / 0.026 / 0.133 | 0.280 / 0.349 |
| open-loop plans | 173 | 24 | 1.511 | 0.128 | 0.022 / 0.005 / 0.111 | 0.103 / 0.039 / 0.168 | 0.268 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.665 | 0.189 | 0.005 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.388 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.540 | 0.152 | 0.043 / 0.002 / 0.433 | 0.056 / 0.030 / 0.105 | 0.377 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.658 | 0.169 | 0.063 / 0.005 / 0.668 | 0.101 / 0.043 / 0.156 | 0.338 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1796 | 0.873 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2925 | 0.916 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2563.4357 | 0.510 |
| funds_mae_12m | 5673.7400 | 40.0829 | 675.4025 | 0.887 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 248.3646 | 0.731 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 565.4252 | 0.833 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 361.4779 | 0.851 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0581 | 0.634 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0397 | 0.907 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3726 | 0.882 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3661 | 0.859 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 4967.8536 | 0.392 |
| funds_mae_24m | 7303.4900 | 72.8329 | 844.6275 | 0.893 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 420.3520 | 0.586 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 807.5005 | 0.396 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 636.6104 | 0.624 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0957 | 0.530 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0565 | 0.916 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3317 | 0.819 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3266 | 0.806 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 844.6 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 420.4 | 160.2 | 787.9 |
| com_valve | 807.5 | 507.1 | 1004.7 |
| ind_valve | 636.6 | 454.2 | 939.2 |
| pop | 4967.9 | 1749.1 | 7044.7 |
| res_pop | 107.0 | 37.1 | 135.5 |
| com_pop | 10.6 | 5.0 | 12.3 |
| ind_pop | 14.3 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 100.4 | 26.8 | 89.0 |
| tax_fund | 183.3 | 53.9 | 1490.0 |
| road_spend | 92.8 | 9.0 | 638.2 |
| fire_spend | 46.1 | 1.3 | 473.1 |
| police_spend | 84.0 | 3.4 | 618.5 |
| powered_zones | 10.3 | 0.9 | 9.0 |
| unpowered_zones | 5.5 | 0.8 | 7.1 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 36.9 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 875.9 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 384.9 | 128.0 | 549.2 |
| com_valve | 851.3 | 545.4 | 967.3 |
| ind_valve | 686.0 | 502.9 | 866.6 |
| pop | 4820.2 | 1820.5 | 6670.1 |
| res_pop | 101.9 | 37.8 | 127.8 |
| com_pop | 10.0 | 5.0 | 11.7 |
| ind_pop | 14.4 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 99.7 | 27.8 | 83.7 |
| tax_fund | 164.5 | 49.4 | 1392.4 |
| road_spend | 88.7 | 8.4 | 639.3 |
| fire_spend | 43.3 | 1.4 | 467.7 |
| police_spend | 78.3 | 4.3 | 609.4 |
| powered_zones | 10.8 | 1.2 | 11.7 |
| unpowered_zones | 6.2 | 1.1 | 7.9 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 36.6 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 749.5 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 528.3 | 258.1 | 1515.1 |
| com_valve | 673.9 | 390.3 | 1118.5 |
| ind_valve | 486.3 | 305.8 | 1160.1 |
| pop | 5417.5 | 1531.7 | 8185.8 |
| res_pop | 122.5 | 35.0 | 158.8 |
| com_pop | 12.2 | 4.9 | 14.2 |
| ind_pop | 14.1 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 102.6 | 23.7 | 105.2 |
| tax_fund | 240.5 | 67.8 | 1787.4 |
| road_spend | 105.4 | 10.5 | 634.9 |
| fire_spend | 54.6 | 0.9 | 489.5 |
| police_spend | 101.2 | 0.8 | 646.2 |
| powered_zones | 8.7 | 0.0 | 0.5 |
| unpowered_zones | 3.3 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.4 | 0.0 | 0.1 |
| road_total | 37.8 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.150 | 0.845 |
| traffic | 0.950 | 0.765 |
| pollution | 1.466 | 0.703 |
| land_value | 0.654 | 0.336 |
| crime | 1.012 | 0.580 |
| rate_of_growth | 1.097 | 0.835 |
| fire_coverage | 1.028 | 0.125 |
| police_coverage | 1.003 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.523 | 0.260 | 0.348 | 0.325 to 0.368 | 0.383 | 0.135 | 0.200 | 0.163 to 0.239 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.471 | 0.002 | 0.005 |
| all plans | 12 | 0.387 | 0.029 | 0.047 |
| all plans | 24 | 0.505 | 0.052 | 0.086 |
| state-reading plans | 1 | 0.464 | 0.003 | 0.005 |
| state-reading plans | 12 | 0.385 | 0.036 | 0.046 |
| state-reading plans | 24 | 0.509 | 0.067 | 0.085 |
| open-loop plans | 1 | 0.701 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.632 | 0.011 | 0.049 |
| open-loop plans | 24 | 1.138 | 0.016 | 0.095 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -190.03 |
| tile_cat | -26.49 |
| flags | -13.32 |
| power | -1.62 |
| half | -2121.87 |
| eighth | -28.47 |
| scalars_s2 | -5.64 |
| build_cost | -1.13 |
| scalars | -13.61 |
| ledger | -15.68 |
| bk | -23.64 |
| sc_res_pop | -1.70 |
| sc_com_pop | -0.17 |
| sc_ind_pop | -0.17 |
| sc_powered_zones | -0.10 |
| sc_unpowered_zones | -0.14 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.34 |
| sc_res_valve | -1.03 |
| sc_com_valve | -2.08 |
| sc_ind_valve | -1.03 |
| sc_score | -0.72 |
| sc_funds | -1.02 |
| sc_tax_fund | -0.62 |
| sc_road_spend | -1.03 |
| sc_fire_spend | -0.20 |
| sc_police_spend | -0.24 |
| lg_sprite_cycle | -2.45 |
| lg_total_pop | -1.32 |
| lg_res_hist0 | -0.20 |
| lg_res_hist1 | -0.32 |
| lg_com_hist0 | -0.05 |
| lg_com_hist1 | -0.18 |
| lg_ind_hist0 | -0.03 |
| lg_ind_hist1 | -0.23 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.08 |
| lg_need_church | -0.05 |
| lg_road_fund | -0.94 |
| lg_police_fund | -0.16 |
| lg_fire_fund | -0.13 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.01 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.48 |
| lg_pollution_max_y | -3.58 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.39 |
| terrain | -3.67 |
| com_rate | -1.87 |
| kl | 18.13 |
| elbo | -2435.88 |

## os_50m_full_36m_samples_030000000_dec-a

samples consumed: 30000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "ad75d197abf1cc74", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.309 | 0.282 | 0.295 | 0.276 to 0.313 | 0.198 | 0.169 | 0.182 | 0.154 to 0.212 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.139 | 0.048 | 0.050 | 0.049 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.316 | 0.290 | 0.302 | 0.282 to 0.322 | 0.210 | 0.182 | 0.195 | 0.163 to 0.229 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.131 | 0.131 | 0.131 | 0.120 to 0.141 | 0.050 | 0.052 | 0.051 | 0.045 to 0.056 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.283 | 0.256 | 0.269 | 0.248 to 0.288 | 0.156 | 0.129 | 0.141 | 0.116 to 0.165 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.119 | 0.122 | 0.120 | 0.106 to 0.134 | 0.043 | 0.047 | 0.045 | 0.037 to 0.052 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.621 | 0.203 | 0.003 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.384 / 0.393 |
| all plans | 700 | 12 | 0.521 | 0.154 | 0.035 / 0.003 / 0.400 | 0.059 / 0.027 / 0.112 | 0.371 / 0.423 |
| all plans | 700 | 24 | 0.730 | 0.176 | 0.053 / 0.005 / 0.614 | 0.132 / 0.039 / 0.159 | 0.323 / 0.405 |
| state-reading plans | 527 | 1 | 0.598 | 0.201 | 0.005 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.428 / 0.431 |
| state-reading plans | 527 | 12 | 0.522 | 0.162 | 0.042 / 0.003 / 0.505 | 0.059 / 0.028 / 0.106 | 0.396 / 0.442 |
| state-reading plans | 527 | 24 | 0.739 | 0.194 | 0.063 / 0.005 / 0.776 | 0.132 / 0.039 / 0.155 | 0.341 / 0.415 |
| open-loop plans | 173 | 1 | 0.663 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.170 / 0.208 |
| open-loop plans | 173 | 12 | 0.926 | 0.133 | 0.015 / 0.002 / 0.054 | 0.060 / 0.026 / 0.133 | 0.278 / 0.349 |
| open-loop plans | 173 | 24 | 1.842 | 0.128 | 0.026 / 0.005 / 0.111 | 0.133 / 0.039 / 0.168 | 0.260 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.612 | 0.189 | 0.004 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.393 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.522 | 0.152 | 0.035 / 0.002 / 0.433 | 0.057 / 0.030 / 0.105 | 0.375 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.713 | 0.169 | 0.056 / 0.005 / 0.668 | 0.136 / 0.043 / 0.156 | 0.330 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1824 | 0.887 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2949 | 0.924 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2648.9750 | 0.481 |
| funds_mae_12m | 5673.7400 | 40.0829 | 636.1363 | 0.894 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 274.8637 | 0.684 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 598.8282 | 0.788 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 381.9225 | 0.819 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0591 | 0.622 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0354 | 0.918 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3708 | 0.877 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3630 | 0.851 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 6318.2893 | 0.137 |
| funds_mae_24m | 7303.4900 | 72.8329 | 802.9380 | 0.899 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 504.9257 | 0.451 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 800.3925 | 0.411 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 687.7334 | 0.518 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.1320 | 0.227 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0530 | 0.922 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3234 | 0.798 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3175 | 0.783 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 802.9 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 504.9 | 160.2 | 787.9 |
| com_valve | 800.4 | 507.1 | 1004.7 |
| ind_valve | 687.7 | 454.2 | 939.2 |
| pop | 6318.3 | 1749.1 | 7044.7 |
| res_pop | 129.3 | 37.1 | 135.5 |
| com_pop | 12.0 | 5.0 | 12.3 |
| ind_pop | 17.6 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 124.9 | 26.8 | 89.0 |
| tax_fund | 197.2 | 53.9 | 1490.0 |
| road_spend | 94.3 | 9.0 | 638.2 |
| fire_spend | 54.1 | 1.3 | 473.1 |
| police_spend | 88.8 | 3.4 | 618.5 |
| powered_zones | 12.0 | 0.9 | 9.0 |
| unpowered_zones | 5.5 | 0.8 | 7.1 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 38.3 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 813.5 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 485.4 | 128.0 | 549.2 |
| com_valve | 846.1 | 545.4 | 967.3 |
| ind_valve | 742.8 | 502.9 | 866.6 |
| pop | 6379.9 | 1820.5 | 6670.1 |
| res_pop | 128.8 | 37.8 | 127.8 |
| com_pop | 11.7 | 5.0 | 11.7 |
| ind_pop | 18.0 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 124.0 | 27.8 | 83.7 |
| tax_fund | 182.6 | 49.4 | 1392.4 |
| road_spend | 90.4 | 8.4 | 639.3 |
| fire_spend | 51.3 | 1.4 | 467.7 |
| police_spend | 82.9 | 4.3 | 609.4 |
| powered_zones | 12.2 | 1.2 | 11.7 |
| unpowered_zones | 6.1 | 1.1 | 7.9 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 38.0 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 770.7 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 564.4 | 258.1 | 1515.1 |
| com_valve | 661.1 | 390.3 | 1118.5 |
| ind_valve | 520.1 | 305.8 | 1160.1 |
| pop | 6130.7 | 1531.7 | 8185.8 |
| res_pop | 130.5 | 35.0 | 158.8 |
| com_pop | 12.9 | 4.9 | 14.2 |
| ind_pop | 16.6 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 127.8 | 23.7 | 105.2 |
| tax_fund | 241.6 | 67.8 | 1787.4 |
| road_spend | 106.2 | 10.5 | 634.9 |
| fire_spend | 62.3 | 0.9 | 489.5 |
| police_spend | 106.9 | 0.8 | 646.2 |
| powered_zones | 11.4 | 0.0 | 0.5 |
| unpowered_zones | 3.8 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.4 | 0.0 | 0.1 |
| road_total | 39.0 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.168 | 0.845 |
| traffic | 0.966 | 0.765 |
| pollution | 1.489 | 0.703 |
| land_value | 0.677 | 0.336 |
| crime | 1.021 | 0.580 |
| rate_of_growth | 1.108 | 0.835 |
| fire_coverage | 1.260 | 0.125 |
| police_coverage | 1.015 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.517 | 0.263 | 0.348 | 0.325 to 0.369 | 0.387 | 0.136 | 0.202 | 0.165 to 0.241 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.450 | 0.002 | 0.006 |
| all plans | 12 | 0.388 | 0.027 | 0.046 |
| all plans | 24 | 0.587 | 0.047 | 0.130 |
| state-reading plans | 1 | 0.421 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.389 | 0.030 | 0.047 |
| state-reading plans | 24 | 0.597 | 0.059 | 0.134 |
| open-loop plans | 1 | 0.489 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.702 | 0.014 | 0.044 |
| open-loop plans | 24 | 1.623 | 0.022 | 0.127 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -186.28 |
| tile_cat | -26.13 |
| flags | -12.75 |
| power | -1.04 |
| half | -2078.84 |
| eighth | -27.37 |
| scalars_s2 | -5.01 |
| build_cost | -0.97 |
| scalars | -14.15 |
| ledger | -17.47 |
| bk | -26.60 |
| sc_res_pop | -1.45 |
| sc_com_pop | -0.10 |
| sc_ind_pop | -0.10 |
| sc_powered_zones | -0.05 |
| sc_unpowered_zones | -0.06 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.24 |
| sc_res_valve | -1.05 |
| sc_com_valve | -2.10 |
| sc_ind_valve | -1.00 |
| sc_score | -1.02 |
| sc_funds | -1.20 |
| sc_tax_fund | -0.78 |
| sc_road_spend | -1.41 |
| sc_fire_spend | -0.24 |
| sc_police_spend | -0.35 |
| lg_sprite_cycle | -2.65 |
| lg_total_pop | -1.33 |
| lg_res_hist0 | -0.17 |
| lg_res_hist1 | -0.83 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.39 |
| lg_ind_hist0 | -0.04 |
| lg_ind_hist1 | -0.34 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.13 |
| lg_need_church | -0.06 |
| lg_road_fund | -1.29 |
| lg_police_fund | -0.21 |
| lg_fire_fund | -0.17 |
| lg_auto_budget | -0.02 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.01 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.54 |
| lg_pollution_max_y | -3.74 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.42 |
| terrain | -3.54 |
| com_rate | -1.70 |
| kl | 19.34 |
| elbo | -2389.55 |

## os_50m_full_36m_samples_036000000_dec-a

samples consumed: 36000000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "ad75d197abf1cc74", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.314 | 0.285 | 0.299 | 0.279 to 0.317 | 0.201 | 0.168 | 0.183 | 0.155 to 0.213 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.139 | 0.048 | 0.050 | 0.049 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.321 | 0.293 | 0.306 | 0.286 to 0.325 | 0.214 | 0.180 | 0.195 | 0.164 to 0.228 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.131 | 0.131 | 0.131 | 0.120 to 0.141 | 0.050 | 0.052 | 0.051 | 0.045 to 0.056 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.288 | 0.258 | 0.272 | 0.252 to 0.291 | 0.158 | 0.129 | 0.142 | 0.117 to 0.166 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.119 | 0.122 | 0.120 | 0.106 to 0.134 | 0.043 | 0.047 | 0.045 | 0.037 to 0.052 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.589 | 0.203 | 0.003 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.388 / 0.393 |
| all plans | 700 | 12 | 0.526 | 0.154 | 0.028 / 0.003 / 0.400 | 0.065 / 0.027 / 0.112 | 0.369 / 0.423 |
| all plans | 700 | 24 | 0.773 | 0.176 | 0.044 / 0.005 / 0.614 | 0.174 / 0.039 / 0.159 | 0.320 / 0.405 |
| state-reading plans | 527 | 1 | 0.585 | 0.201 | 0.004 / 0.000 / 0.018 | 0.008 / 0.006 / 0.008 | 0.433 / 0.431 |
| state-reading plans | 527 | 12 | 0.528 | 0.162 | 0.034 / 0.003 / 0.505 | 0.065 / 0.028 / 0.106 | 0.394 / 0.442 |
| state-reading plans | 527 | 24 | 0.792 | 0.194 | 0.052 / 0.005 / 0.776 | 0.175 / 0.039 / 0.155 | 0.339 / 0.415 |
| open-loop plans | 173 | 1 | 0.689 | 0.226 | 0.000 / 0.000 / 0.000 | 0.007 / 0.005 / 0.007 | 0.170 / 0.208 |
| open-loop plans | 173 | 12 | 0.897 | 0.133 | 0.014 / 0.002 / 0.054 | 0.065 / 0.026 / 0.133 | 0.276 / 0.349 |
| open-loop plans | 173 | 24 | 1.860 | 0.128 | 0.022 / 0.005 / 0.111 | 0.167 / 0.039 / 0.168 | 0.256 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.587 | 0.189 | 0.003 / 0.000 / 0.015 | 0.008 / 0.006 / 0.009 | 0.394 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.524 | 0.152 | 0.027 / 0.002 / 0.433 | 0.067 / 0.030 / 0.105 | 0.373 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.764 | 0.169 | 0.049 / 0.005 / 0.668 | 0.181 / 0.043 / 0.156 | 0.327 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1829 | 0.889 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2988 | 0.936 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2991.4464 | 0.366 |
| funds_mae_12m | 5673.7400 | 40.0829 | 562.4211 | 0.907 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 283.7763 | 0.669 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 602.2645 | 0.783 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 382.7127 | 0.818 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0650 | 0.553 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0278 | 0.937 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3693 | 0.874 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3617 | 0.848 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 7929.8393 | -0.167 |
| funds_mae_24m | 7303.4900 | 72.8329 | 706.3007 | 0.912 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 589.5468 | 0.316 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 816.8798 | 0.377 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 745.5611 | 0.399 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.1736 | -0.121 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0435 | 0.937 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.3204 | 0.791 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.3153 | 0.778 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 706.3 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 589.5 | 160.2 | 787.9 |
| com_valve | 816.9 | 507.1 | 1004.7 |
| ind_valve | 745.6 | 454.2 | 939.2 |
| pop | 7929.8 | 1749.1 | 7044.7 |
| res_pop | 159.7 | 37.1 | 135.5 |
| com_pop | 13.9 | 5.0 | 12.3 |
| ind_pop | 20.3 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 135.4 | 26.8 | 89.0 |
| tax_fund | 215.2 | 53.9 | 1490.0 |
| road_spend | 92.3 | 9.0 | 638.2 |
| fire_spend | 60.0 | 1.3 | 473.1 |
| police_spend | 92.0 | 3.4 | 618.5 |
| powered_zones | 12.1 | 0.9 | 9.0 |
| unpowered_zones | 4.7 | 0.8 | 7.1 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 40.8 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 701.5 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 567.7 | 128.0 | 549.2 |
| com_valve | 845.0 | 545.4 | 967.3 |
| ind_valve | 787.2 | 502.9 | 866.6 |
| pop | 8091.8 | 1820.5 | 6670.1 |
| res_pop | 161.4 | 37.8 | 127.8 |
| com_pop | 13.8 | 5.0 | 11.7 |
| ind_pop | 20.9 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 135.4 | 27.8 | 83.7 |
| tax_fund | 202.6 | 49.4 | 1392.4 |
| road_spend | 87.0 | 8.4 | 639.3 |
| fire_spend | 56.6 | 1.4 | 467.7 |
| police_spend | 85.7 | 4.3 | 609.4 |
| powered_zones | 12.3 | 1.2 | 11.7 |
| unpowered_zones | 5.4 | 1.1 | 7.9 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 40.7 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 721.1 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 656.2 | 258.1 | 1515.1 |
| com_valve | 731.2 | 390.3 | 1118.5 |
| ind_valve | 618.6 | 305.8 | 1160.1 |
| pop | 7436.4 | 1531.7 | 8185.8 |
| res_pop | 154.6 | 35.0 | 158.8 |
| com_pop | 14.1 | 4.9 | 14.2 |
| ind_pop | 18.6 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 135.7 | 23.7 | 105.2 |
| tax_fund | 253.3 | 67.8 | 1787.4 |
| road_spend | 108.4 | 10.5 | 634.9 |
| fire_spend | 70.2 | 0.9 | 489.5 |
| police_spend | 111.1 | 0.8 | 646.2 |
| powered_zones | 11.5 | 0.0 | 0.5 |
| unpowered_zones | 2.8 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.3 | 0.0 | 0.1 |
| road_total | 41.2 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.172 | 0.845 |
| traffic | 0.975 | 0.765 |
| pollution | 1.501 | 0.703 |
| land_value | 0.681 | 0.336 |
| crime | 1.018 | 0.580 |
| rate_of_growth | 1.106 | 0.835 |
| fire_coverage | 1.650 | 0.125 |
| police_coverage | 1.006 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.518 | 0.263 | 0.349 | 0.326 to 0.370 | 0.395 | 0.136 | 0.203 | 0.166 to 0.242 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.460 | 0.002 | 0.005 |
| all plans | 12 | 0.398 | 0.019 | 0.057 |
| all plans | 24 | 0.642 | 0.038 | 0.187 |
| state-reading plans | 1 | 0.461 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.398 | 0.024 | 0.056 |
| state-reading plans | 24 | 0.658 | 0.047 | 0.188 |
| open-loop plans | 1 | 0.529 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.719 | 0.014 | 0.059 |
| open-loop plans | 24 | 1.701 | 0.018 | 0.186 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -185.45 |
| tile_cat | -26.11 |
| flags | -12.81 |
| power | -1.16 |
| half | -2062.05 |
| eighth | -26.86 |
| scalars_s2 | -4.73 |
| build_cost | -0.83 |
| scalars | -15.26 |
| ledger | -19.23 |
| bk | -29.76 |
| sc_res_pop | -1.31 |
| sc_com_pop | -0.10 |
| sc_ind_pop | -0.09 |
| sc_powered_zones | -0.02 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.19 |
| sc_res_valve | -1.07 |
| sc_com_valve | -2.11 |
| sc_ind_valve | -1.01 |
| sc_score | -1.39 |
| sc_funds | -1.43 |
| sc_tax_fund | -0.93 |
| sc_road_spend | -1.84 |
| sc_fire_spend | -0.31 |
| sc_police_spend | -0.44 |
| lg_sprite_cycle | -2.66 |
| lg_total_pop | -1.34 |
| lg_res_hist0 | -0.17 |
| lg_res_hist1 | -1.24 |
| lg_com_hist0 | -0.07 |
| lg_com_hist1 | -0.57 |
| lg_ind_hist0 | -0.04 |
| lg_ind_hist1 | -0.50 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.17 |
| lg_need_church | -0.06 |
| lg_road_fund | -1.94 |
| lg_police_fund | -0.27 |
| lg_fire_fund | -0.23 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.01 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.56 |
| lg_pollution_max_y | -3.83 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.45 |
| terrain | -3.42 |
| com_rate | -1.92 |
| kl | 20.28 |
| elbo | -2375.38 |
