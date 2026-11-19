## sf_15m_small_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.229 | 0.291 | 0.257 | 0.237 to 0.276 | 0.128 | 0.177 | 0.148 | 0.127 to 0.172 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.237 | 0.299 | 0.265 | 0.244 to 0.285 | 0.138 | 0.190 | 0.160 | 0.135 to 0.188 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.203 | 0.263 | 0.229 | 0.208 to 0.249 | 0.094 | 0.133 | 0.110 | 0.092 to 0.128 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.737 | 0.203 | 0.003 / 0.000 / 0.013 | 0.009 / 0.006 / 0.007 | 0.340 / 0.393 |
| all plans | 700 | 12 | 0.576 | 0.154 | 0.056 / 0.003 / 0.400 | 0.047 / 0.027 / 0.112 | 0.313 / 0.423 |
| all plans | 700 | 24 | 0.711 | 0.176 | 0.111 / 0.005 / 0.614 | 0.084 / 0.039 / 0.159 | 0.274 / 0.405 |
| state-reading plans | 527 | 1 | 0.723 | 0.201 | 0.005 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.382 / 0.431 |
| state-reading plans | 527 | 12 | 0.561 | 0.162 | 0.064 / 0.003 / 0.505 | 0.046 / 0.028 / 0.106 | 0.335 / 0.442 |
| state-reading plans | 527 | 24 | 0.693 | 0.194 | 0.124 / 0.005 / 0.776 | 0.080 / 0.039 / 0.155 | 0.291 / 0.415 |
| open-loop plans | 173 | 1 | 0.819 | 0.226 | 0.000 / 0.000 / 0.000 | 0.009 / 0.005 / 0.007 | 0.144 / 0.208 |
| open-loop plans | 173 | 12 | 1.091 | 0.133 | 0.037 / 0.002 / 0.054 | 0.051 / 0.026 / 0.133 | 0.232 / 0.349 |
| open-loop plans | 173 | 24 | 1.562 | 0.128 | 0.074 / 0.005 / 0.111 | 0.094 / 0.039 / 0.168 | 0.216 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.670 | 0.189 | 0.004 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.350 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.575 | 0.152 | 0.058 / 0.002 / 0.433 | 0.048 / 0.030 / 0.105 | 0.316 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.691 | 0.169 | 0.124 / 0.005 / 0.668 | 0.084 / 0.043 / 0.156 | 0.279 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1482 | 0.721 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2566 | 0.804 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2068.4393 | 0.678 |
| funds_mae_12m | 5673.7400 | 40.0829 | 928.9057 | 0.842 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 228.4955 | 0.765 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 582.2034 | 0.810 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 367.2030 | 0.842 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0470 | 0.764 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0561 | 0.866 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3129 | 0.740 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3110 | 0.729 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3950.9143 | 0.584 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1328.6121 | 0.826 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 377.7639 | 0.653 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 655.7995 | 0.701 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 653.5598 | 0.589 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0839 | 0.628 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.1112 | 0.826 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.2738 | 0.676 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.2722 | 0.671 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1328.6 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 377.8 | 160.2 | 787.9 |
| com_valve | 655.8 | 507.1 | 1004.7 |
| ind_valve | 653.6 | 454.2 | 939.2 |
| pop | 3950.9 | 1749.1 | 7044.7 |
| res_pop | 92.2 | 37.1 | 135.5 |
| com_pop | 8.7 | 5.0 | 12.3 |
| ind_pop | 13.1 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 77.2 | 26.8 | 89.0 |
| tax_fund | 186.4 | 53.9 | 1490.0 |
| road_spend | 101.3 | 9.0 | 638.2 |
| fire_spend | 57.1 | 1.3 | 473.1 |
| police_spend | 96.6 | 3.4 | 618.5 |
| powered_zones | 9.2 | 0.9 | 9.0 |
| unpowered_zones | 6.5 | 0.8 | 7.1 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.3 |
| road_total | 69.7 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1269.0 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 308.6 | 128.0 | 549.2 |
| com_valve | 693.9 | 545.4 | 967.3 |
| ind_valve | 718.4 | 502.9 | 866.6 |
| pop | 3837.3 | 1820.5 | 6670.1 |
| res_pop | 87.3 | 37.8 | 127.8 |
| com_pop | 8.7 | 5.0 | 11.7 |
| ind_pop | 13.1 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 79.2 | 27.8 | 83.7 |
| tax_fund | 173.9 | 49.4 | 1392.4 |
| road_spend | 99.7 | 8.4 | 639.3 |
| fire_spend | 54.8 | 1.4 | 467.7 |
| police_spend | 95.0 | 4.3 | 609.4 |
| powered_zones | 10.0 | 1.2 | 11.7 |
| unpowered_zones | 7.2 | 1.1 | 7.9 |
| coal_plants | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.4 |
| road_total | 70.4 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1510.2 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 588.4 | 258.1 | 1515.1 |
| com_valve | 539.8 | 390.3 | 1118.5 |
| ind_valve | 456.0 | 305.8 | 1160.1 |
| pop | 4297.0 | 1531.7 | 8185.8 |
| res_pop | 107.0 | 35.0 | 158.8 |
| com_pop | 8.6 | 4.9 | 14.2 |
| ind_pop | 12.8 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 70.9 | 23.7 | 105.2 |
| tax_fund | 224.3 | 67.8 | 1787.4 |
| road_spend | 106.4 | 10.5 | 634.9 |
| fire_spend | 64.2 | 0.9 | 489.5 |
| police_spend | 101.5 | 0.8 | 646.2 |
| powered_zones | 7.0 | 0.0 | 0.5 |
| unpowered_zones | 4.7 | 0.0 | 4.8 |
| coal_plants | 0.5 | 0.0 | 0.2 |
| nuclear_plants | 0.7 | 0.0 | 0.1 |
| road_total | 67.7 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.279 | 0.845 |
| traffic | 1.122 | 0.765 |
| pollution | 1.641 | 0.703 |
| land_value | 0.765 | 0.336 |
| crime | 1.281 | 0.580 |
| rate_of_growth | 1.295 | 0.835 |
| fire_coverage | 1.399 | 0.125 |
| police_coverage | 1.115 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.502 | 0.268 | 0.350 | 0.327 to 0.370 | 0.446 | 0.140 | 0.213 | 0.179 to 0.252 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.562 | 0.002 | 0.006 |
| all plans | 12 | 0.398 | 0.053 | 0.035 |
| all plans | 24 | 0.518 | 0.125 | 0.071 |
| state-reading plans | 1 | 0.545 | 0.002 | 0.007 |
| state-reading plans | 12 | 0.388 | 0.059 | 0.035 |
| state-reading plans | 24 | 0.507 | 0.142 | 0.066 |
| open-loop plans | 1 | 0.640 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.689 | 0.041 | 0.035 |
| open-loop plans | 24 | 1.092 | 0.084 | 0.087 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -242.28 |
| tile_cat | -34.29 |
| flags | -21.00 |
| power | -3.17 |
| half | -2541.15 |
| eighth | -36.66 |
| scalars_s2 | -5.66 |
| build_cost | -1.06 |
| scalars | -15.42 |
| ledger | -17.85 |
| bk | -27.61 |
| sc_res_pop | -1.75 |
| sc_com_pop | -0.17 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.07 |
| sc_unpowered_zones | -0.09 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.38 |
| sc_res_valve | -1.16 |
| sc_com_valve | -2.28 |
| sc_ind_valve | -1.66 |
| sc_score | -0.98 |
| sc_funds | -1.34 |
| sc_tax_fund | -0.77 |
| sc_road_spend | -1.06 |
| sc_fire_spend | -0.21 |
| sc_police_spend | -0.29 |
| lg_sprite_cycle | -0.88 |
| lg_total_pop | -2.24 |
| lg_res_hist0 | -1.01 |
| lg_res_hist1 | -0.51 |
| lg_com_hist0 | -0.21 |
| lg_com_hist1 | -0.12 |
| lg_ind_hist0 | -0.32 |
| lg_ind_hist1 | -0.21 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.13 |
| lg_need_church | -0.08 |
| lg_road_fund | -1.03 |
| lg_police_fund | -0.18 |
| lg_fire_fund | -0.13 |
| lg_auto_budget | -0.04 |
| lg_fire_pop | -0.14 |
| lg_city_center_x | -0.17 |
| lg_city_center_y | -0.15 |
| lg_pollution_max_x | -3.77 |
| lg_pollution_max_y | -3.78 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.74 |
| terrain | -6.76 |
| com_rate | -6.39 |
| kl | 12.95 |
| elbo | -2938.98 |
