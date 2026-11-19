## sf_50m_small_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.230 | 0.295 | 0.259 | 0.238 to 0.278 | 0.126 | 0.178 | 0.148 | 0.126 to 0.172 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.239 | 0.303 | 0.267 | 0.246 to 0.288 | 0.137 | 0.191 | 0.159 | 0.133 to 0.188 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.203 | 0.268 | 0.231 | 0.208 to 0.252 | 0.093 | 0.137 | 0.111 | 0.094 to 0.129 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.590 | 0.203 | 0.002 / 0.000 / 0.013 | 0.009 / 0.006 / 0.007 | 0.340 / 0.393 |
| all plans | 700 | 12 | 0.532 | 0.154 | 0.038 / 0.003 / 0.400 | 0.056 / 0.027 / 0.112 | 0.304 / 0.423 |
| all plans | 700 | 24 | 0.706 | 0.176 | 0.063 / 0.005 / 0.614 | 0.106 / 0.039 / 0.159 | 0.266 / 0.405 |
| state-reading plans | 527 | 1 | 0.560 | 0.201 | 0.002 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.383 / 0.431 |
| state-reading plans | 527 | 12 | 0.523 | 0.162 | 0.043 / 0.003 / 0.505 | 0.056 / 0.028 / 0.106 | 0.328 / 0.442 |
| state-reading plans | 527 | 24 | 0.700 | 0.194 | 0.074 / 0.005 / 0.776 | 0.104 / 0.039 / 0.155 | 0.285 / 0.415 |
| open-loop plans | 173 | 1 | 0.599 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.140 / 0.208 |
| open-loop plans | 173 | 12 | 0.996 | 0.133 | 0.025 / 0.002 / 0.054 | 0.060 / 0.026 / 0.133 | 0.216 / 0.349 |
| open-loop plans | 173 | 24 | 1.750 | 0.128 | 0.042 / 0.005 / 0.111 | 0.113 / 0.039 / 0.168 | 0.200 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.564 | 0.189 | 0.002 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.348 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.536 | 0.152 | 0.040 / 0.002 / 0.433 | 0.057 / 0.030 / 0.105 | 0.308 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.687 | 0.169 | 0.069 / 0.005 / 0.668 | 0.108 / 0.043 / 0.156 | 0.272 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1475 | 0.717 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2587 | 0.810 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2609.0643 | 0.495 |
| funds_mae_12m | 5673.7400 | 40.0829 | 893.2966 | 0.849 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 221.7779 | 0.777 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 578.0625 | 0.816 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 349.5743 | 0.870 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0563 | 0.655 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0385 | 0.910 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3039 | 0.719 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3028 | 0.710 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 5442.1000 | 0.303 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1007.7912 | 0.871 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 423.5688 | 0.580 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 714.6645 | 0.583 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 649.3545 | 0.598 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.1061 | 0.443 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0633 | 0.905 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.2661 | 0.657 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.2647 | 0.653 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1007.8 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 423.6 | 160.2 | 787.9 |
| com_valve | 714.7 | 507.1 | 1004.7 |
| ind_valve | 649.4 | 454.2 | 939.2 |
| pop | 5442.1 | 1749.1 | 7044.7 |
| res_pop | 103.9 | 37.1 | 135.5 |
| com_pop | 10.9 | 5.0 | 12.3 |
| ind_pop | 17.6 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 104.5 | 26.8 | 89.0 |
| tax_fund | 227.2 | 53.9 | 1490.0 |
| road_spend | 100.5 | 9.0 | 638.2 |
| fire_spend | 59.6 | 1.3 | 473.1 |
| police_spend | 95.4 | 3.4 | 618.5 |
| powered_zones | 11.3 | 0.9 | 9.0 |
| unpowered_zones | 5.7 | 0.8 | 7.1 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.3 |
| road_total | 74.4 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 984.8 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 352.5 | 128.0 | 549.2 |
| com_valve | 766.2 | 545.4 | 967.3 |
| ind_valve | 716.2 | 502.9 | 866.6 |
| pop | 5436.6 | 1820.5 | 6670.1 |
| res_pop | 101.9 | 37.8 | 127.8 |
| com_pop | 10.9 | 5.0 | 11.7 |
| ind_pop | 17.9 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 105.8 | 27.8 | 83.7 |
| tax_fund | 202.5 | 49.4 | 1392.4 |
| road_spend | 97.8 | 8.4 | 639.3 |
| fire_spend | 55.9 | 1.4 | 467.7 |
| police_spend | 92.7 | 4.3 | 609.4 |
| powered_zones | 11.8 | 1.2 | 11.7 |
| unpowered_zones | 6.3 | 1.1 | 7.9 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.0 | 0.4 |
| road_total | 74.9 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1077.9 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 640.0 | 258.1 | 1515.1 |
| com_valve | 557.6 | 390.3 | 1118.5 |
| ind_valve | 445.8 | 305.8 | 1160.1 |
| pop | 5458.9 | 1531.7 | 8185.8 |
| res_pop | 109.7 | 35.0 | 158.8 |
| com_pop | 10.8 | 4.9 | 14.2 |
| ind_pop | 16.8 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 100.4 | 23.7 | 105.2 |
| tax_fund | 302.3 | 67.8 | 1787.4 |
| road_spend | 108.5 | 10.5 | 634.9 |
| fire_spend | 71.1 | 0.9 | 489.5 |
| police_spend | 103.7 | 0.8 | 646.2 |
| powered_zones | 9.8 | 0.0 | 0.5 |
| unpowered_zones | 3.8 | 0.0 | 4.8 |
| coal_plants | 0.3 | 0.0 | 0.2 |
| nuclear_plants | 0.5 | 0.0 | 0.1 |
| road_total | 72.8 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.364 | 0.845 |
| traffic | 1.144 | 0.765 |
| pollution | 1.704 | 0.703 |
| land_value | 0.830 | 0.336 |
| crime | 1.314 | 0.580 |
| rate_of_growth | 1.320 | 0.835 |
| fire_coverage | 1.277 | 0.125 |
| police_coverage | 1.041 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.363 | 0.287 | 0.321 | 0.298 to 0.341 | 0.227 | 0.163 | 0.190 | 0.159 to 0.223 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.464 | 0.001 | 0.006 |
| all plans | 12 | 0.412 | 0.034 | 0.047 |
| all plans | 24 | 0.575 | 0.070 | 0.094 |
| state-reading plans | 1 | 0.434 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.404 | 0.036 | 0.046 |
| state-reading plans | 24 | 0.573 | 0.078 | 0.089 |
| open-loop plans | 1 | 0.490 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.776 | 0.026 | 0.049 |
| open-loop plans | 24 | 1.495 | 0.048 | 0.101 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -306.82 |
| tile_cat | -38.81 |
| flags | -20.39 |
| power | -5.96 |
| half | -2765.14 |
| eighth | -37.59 |
| scalars_s2 | -5.22 |
| build_cost | -0.79 |
| scalars | -29.46 |
| ledger | -39.83 |
| bk | -64.07 |
| sc_res_pop | -1.50 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.15 |
| sc_powered_zones | -0.01 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.37 |
| sc_res_valve | -1.71 |
| sc_com_valve | -2.98 |
| sc_ind_valve | -2.25 |
| sc_score | -6.25 |
| sc_funds | -3.59 |
| sc_tax_fund | -1.87 |
| sc_road_spend | -3.47 |
| sc_fire_spend | -1.06 |
| sc_police_spend | -1.07 |
| lg_sprite_cycle | -1.34 |
| lg_total_pop | -4.31 |
| lg_res_hist0 | -3.22 |
| lg_res_hist1 | -3.78 |
| lg_com_hist0 | -0.96 |
| lg_com_hist1 | -1.00 |
| lg_ind_hist0 | -0.81 |
| lg_ind_hist1 | -1.45 |
| lg_res_cap | -0.04 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.28 |
| lg_need_church | -0.23 |
| lg_road_fund | -2.12 |
| lg_police_fund | -0.46 |
| lg_fire_fund | -0.43 |
| lg_auto_budget | -0.03 |
| lg_fire_pop | -0.34 |
| lg_city_center_x | -0.66 |
| lg_city_center_y | -0.19 |
| lg_pollution_max_x | -6.61 |
| lg_pollution_max_y | -7.13 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -4.44 |
| terrain | -6.57 |
| com_rate | -7.08 |
| kl | 13.69 |
| elbo | -3272.12 |
