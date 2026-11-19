## sf_15m_full_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.233 | 0.284 | 0.256 | 0.237 to 0.273 | 0.131 | 0.173 | 0.149 | 0.126 to 0.173 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.241 | 0.293 | 0.265 | 0.244 to 0.284 | 0.142 | 0.186 | 0.161 | 0.135 to 0.188 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.203 | 0.256 | 0.227 | 0.209 to 0.244 | 0.096 | 0.131 | 0.111 | 0.094 to 0.128 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.638 | 0.203 | 0.003 / 0.000 / 0.013 | 0.009 / 0.006 / 0.007 | 0.333 / 0.393 |
| all plans | 700 | 12 | 0.536 | 0.154 | 0.057 / 0.003 / 0.400 | 0.053 / 0.027 / 0.112 | 0.318 / 0.423 |
| all plans | 700 | 24 | 0.639 | 0.176 | 0.105 / 0.005 / 0.614 | 0.079 / 0.039 / 0.159 | 0.283 / 0.405 |
| state-reading plans | 527 | 1 | 0.592 | 0.201 | 0.005 / 0.000 / 0.018 | 0.010 / 0.006 / 0.008 | 0.375 / 0.431 |
| state-reading plans | 527 | 12 | 0.523 | 0.162 | 0.062 / 0.003 / 0.505 | 0.054 / 0.028 / 0.106 | 0.340 / 0.442 |
| state-reading plans | 527 | 24 | 0.631 | 0.194 | 0.112 / 0.005 / 0.776 | 0.078 / 0.039 / 0.155 | 0.300 / 0.415 |
| open-loop plans | 173 | 1 | 0.865 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.140 / 0.208 |
| open-loop plans | 173 | 12 | 1.069 | 0.133 | 0.046 / 0.002 / 0.054 | 0.051 / 0.026 / 0.133 | 0.239 / 0.349 |
| open-loop plans | 173 | 24 | 1.456 | 0.128 | 0.084 / 0.005 / 0.111 | 0.080 / 0.039 / 0.168 | 0.224 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.603 | 0.189 | 0.004 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.341 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.543 | 0.152 | 0.062 / 0.002 / 0.433 | 0.056 / 0.030 / 0.105 | 0.319 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.628 | 0.169 | 0.116 / 0.005 / 0.668 | 0.080 / 0.043 / 0.156 | 0.286 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1488 | 0.724 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2559 | 0.802 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2217.4929 | 0.627 |
| funds_mae_12m | 5673.7400 | 40.0829 | 908.5820 | 0.846 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 219.6457 | 0.781 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 594.2580 | 0.794 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 367.3520 | 0.842 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0532 | 0.692 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0571 | 0.863 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3176 | 0.752 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3171 | 0.744 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3611.2500 | 0.648 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1226.5363 | 0.840 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 340.0052 | 0.714 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 659.0362 | 0.695 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 554.9346 | 0.792 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0790 | 0.669 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.1048 | 0.836 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.2826 | 0.698 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.2813 | 0.694 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1226.5 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 340.0 | 160.2 | 787.9 |
| com_valve | 659.0 | 507.1 | 1004.7 |
| ind_valve | 554.9 | 454.2 | 939.2 |
| pop | 3611.2 | 1749.1 | 7044.7 |
| res_pop | 88.1 | 37.1 | 135.5 |
| com_pop | 9.1 | 5.0 | 12.3 |
| ind_pop | 10.5 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 77.2 | 26.8 | 89.0 |
| tax_fund | 167.4 | 53.9 | 1490.0 |
| road_spend | 84.8 | 9.0 | 638.2 |
| fire_spend | 41.4 | 1.3 | 473.1 |
| police_spend | 53.8 | 3.4 | 618.5 |
| powered_zones | 9.1 | 0.9 | 9.0 |
| unpowered_zones | 6.4 | 0.8 | 7.1 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.3 |
| road_total | 58.5 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1135.8 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 308.8 | 128.0 | 549.2 |
| com_valve | 697.6 | 545.4 | 967.3 |
| ind_valve | 604.9 | 502.9 | 866.6 |
| pop | 3638.4 | 1820.5 | 6670.1 |
| res_pop | 88.9 | 37.8 | 127.8 |
| com_pop | 9.1 | 5.0 | 11.7 |
| ind_pop | 10.8 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 78.2 | 27.8 | 83.7 |
| tax_fund | 160.6 | 49.4 | 1392.4 |
| road_spend | 83.2 | 8.4 | 639.3 |
| fire_spend | 39.1 | 1.4 | 467.7 |
| police_spend | 52.4 | 4.3 | 609.4 |
| powered_zones | 9.7 | 1.2 | 11.7 |
| unpowered_zones | 7.0 | 1.1 | 7.9 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.4 |
| road_total | 58.8 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1503.0 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 435.2 | 258.1 | 1515.1 |
| com_valve | 541.4 | 390.3 | 1118.5 |
| ind_valve | 402.7 | 305.8 | 1160.1 |
| pop | 3528.6 | 1531.7 | 8185.8 |
| res_pop | 85.7 | 35.0 | 158.8 |
| com_pop | 9.2 | 4.9 | 14.2 |
| ind_pop | 9.9 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 74.3 | 23.7 | 105.2 |
| tax_fund | 188.2 | 67.8 | 1787.4 |
| road_spend | 89.9 | 10.5 | 634.9 |
| fire_spend | 48.4 | 0.9 | 489.5 |
| police_spend | 58.3 | 0.8 | 646.2 |
| powered_zones | 7.1 | 0.0 | 0.5 |
| unpowered_zones | 4.6 | 0.0 | 4.8 |
| coal_plants | 0.4 | 0.0 | 0.2 |
| nuclear_plants | 0.6 | 0.0 | 0.1 |
| road_total | 57.7 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.257 | 0.845 |
| traffic | 1.101 | 0.765 |
| pollution | 1.647 | 0.703 |
| land_value | 0.706 | 0.336 |
| crime | 1.221 | 0.580 |
| rate_of_growth | 1.237 | 0.835 |
| fire_coverage | 1.246 | 0.125 |
| police_coverage | 0.920 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.602 | 0.258 | 0.361 | 0.337 to 0.383 | 0.664 | 0.133 | 0.221 | 0.181 to 0.263 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.478 | 0.002 | 0.005 |
| all plans | 12 | 0.373 | 0.058 | 0.046 |
| all plans | 24 | 0.453 | 0.122 | 0.055 |
| state-reading plans | 1 | 0.437 | 0.002 | 0.006 |
| state-reading plans | 12 | 0.367 | 0.058 | 0.047 |
| state-reading plans | 24 | 0.452 | 0.128 | 0.055 |
| open-loop plans | 1 | 0.652 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.673 | 0.058 | 0.042 |
| open-loop plans | 24 | 1.017 | 0.101 | 0.058 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -221.27 |
| tile_cat | -30.70 |
| flags | -15.68 |
| power | -2.05 |
| half | -2426.30 |
| eighth | -35.54 |
| scalars_s2 | -5.60 |
| build_cost | -1.05 |
| scalars | -12.83 |
| ledger | -13.23 |
| bk | -20.47 |
| sc_res_pop | -1.71 |
| sc_com_pop | -0.17 |
| sc_ind_pop | -0.16 |
| sc_powered_zones | -0.07 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.38 |
| sc_res_valve | -1.02 |
| sc_com_valve | -2.14 |
| sc_ind_valve | -1.55 |
| sc_score | -0.41 |
| sc_funds | -0.99 |
| sc_tax_fund | -0.45 |
| sc_road_spend | -0.46 |
| sc_fire_spend | -0.10 |
| sc_police_spend | -0.12 |
| lg_sprite_cycle | -0.78 |
| lg_total_pop | -1.59 |
| lg_res_hist0 | -0.61 |
| lg_res_hist1 | -0.43 |
| lg_com_hist0 | -0.18 |
| lg_com_hist1 | -0.11 |
| lg_ind_hist0 | -0.24 |
| lg_ind_hist1 | -0.21 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.05 |
| lg_need_church | -0.04 |
| lg_road_fund | -0.48 |
| lg_police_fund | -0.09 |
| lg_fire_fund | -0.06 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.03 |
| lg_city_center_y | -0.04 |
| lg_pollution_max_x | -3.01 |
| lg_pollution_max_y | -2.92 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -5.78 |
| com_rate | -4.43 |
| kl | 12.39 |
| elbo | -2781.27 |
