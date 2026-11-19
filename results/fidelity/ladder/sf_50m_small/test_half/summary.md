## sf_50m_small_samples_000750080_dec-a

samples consumed: 750080; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.230 | 0.295 | 0.259 | 0.238 to 0.278 | 0.125 | 0.178 | 0.147 | 0.125 to 0.171 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.239 | 0.304 | 0.267 | 0.245 to 0.289 | 0.136 | 0.192 | 0.159 | 0.133 to 0.187 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.202 | 0.266 | 0.230 | 0.208 to 0.250 | 0.092 | 0.134 | 0.109 | 0.091 to 0.128 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.868 | 0.203 | 0.003 / 0.000 / 0.013 | 0.009 / 0.006 / 0.007 | 0.341 / 0.393 |
| all plans | 700 | 12 | 0.556 | 0.154 | 0.041 / 0.003 / 0.400 | 0.048 / 0.027 / 0.112 | 0.316 / 0.423 |
| all plans | 700 | 24 | 0.684 | 0.176 | 0.070 / 0.005 / 0.614 | 0.087 / 0.039 / 0.159 | 0.279 / 0.405 |
| state-reading plans | 527 | 1 | 0.806 | 0.201 | 0.004 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.385 / 0.431 |
| state-reading plans | 527 | 12 | 0.539 | 0.162 | 0.048 / 0.003 / 0.505 | 0.047 / 0.028 / 0.106 | 0.340 / 0.442 |
| state-reading plans | 527 | 24 | 0.669 | 0.194 | 0.082 / 0.005 / 0.776 | 0.086 / 0.039 / 0.155 | 0.297 / 0.415 |
| open-loop plans | 173 | 1 | 0.704 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.141 / 0.208 |
| open-loop plans | 173 | 12 | 1.108 | 0.133 | 0.025 / 0.002 / 0.054 | 0.050 / 0.026 / 0.133 | 0.229 / 0.349 |
| open-loop plans | 173 | 24 | 1.625 | 0.128 | 0.044 / 0.005 / 0.111 | 0.095 / 0.039 / 0.168 | 0.216 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.775 | 0.189 | 0.003 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.350 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.558 | 0.152 | 0.042 / 0.002 / 0.433 | 0.049 / 0.030 / 0.105 | 0.320 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.662 | 0.169 | 0.078 / 0.005 / 0.668 | 0.088 / 0.043 / 0.156 | 0.285 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1470 | 0.715 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2588 | 0.811 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2158.5250 | 0.647 |
| funds_mae_12m | 5673.7400 | 40.0829 | 810.9632 | 0.863 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 208.8255 | 0.800 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 567.5293 | 0.830 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 346.3534 | 0.875 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0477 | 0.756 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0413 | 0.903 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3161 | 0.748 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3137 | 0.736 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 4520.5536 | 0.477 |
| funds_mae_24m | 7303.4900 | 72.8329 | 945.8173 | 0.879 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 373.3627 | 0.660 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 665.2573 | 0.682 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 590.7793 | 0.718 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0870 | 0.602 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0700 | 0.894 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.2791 | 0.689 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.2769 | 0.683 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 945.8 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 373.4 | 160.2 | 787.9 |
| com_valve | 665.3 | 507.1 | 1004.7 |
| ind_valve | 590.8 | 454.2 | 939.2 |
| pop | 4520.6 | 1749.1 | 7044.7 |
| res_pop | 91.7 | 37.1 | 135.5 |
| com_pop | 9.2 | 5.0 | 12.3 |
| ind_pop | 14.7 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 86.5 | 26.8 | 89.0 |
| tax_fund | 201.6 | 53.9 | 1490.0 |
| road_spend | 102.8 | 9.0 | 638.2 |
| fire_spend | 58.8 | 1.3 | 473.1 |
| police_spend | 97.4 | 3.4 | 618.5 |
| powered_zones | 10.1 | 0.9 | 9.0 |
| unpowered_zones | 6.3 | 0.8 | 7.1 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.3 |
| road_total | 67.9 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 938.8 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 307.0 | 128.0 | 549.2 |
| com_valve | 701.8 | 545.4 | 967.3 |
| ind_valve | 648.7 | 502.9 | 866.6 |
| pop | 4488.2 | 1820.5 | 6670.1 |
| res_pop | 90.0 | 37.8 | 127.8 |
| com_pop | 9.2 | 5.0 | 11.7 |
| ind_pop | 14.7 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 87.9 | 27.8 | 83.7 |
| tax_fund | 183.3 | 49.4 | 1392.4 |
| road_spend | 99.6 | 8.4 | 639.3 |
| fire_spend | 55.5 | 1.4 | 467.7 |
| police_spend | 95.8 | 4.3 | 609.4 |
| powered_zones | 10.8 | 1.2 | 11.7 |
| unpowered_zones | 6.9 | 1.1 | 7.9 |
| coal_plants | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.0 | 0.4 |
| road_total | 67.7 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 967.1 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 575.4 | 258.1 | 1515.1 |
| com_valve | 554.0 | 390.3 | 1118.5 |
| ind_valve | 414.2 | 305.8 | 1160.1 |
| pop | 4619.0 | 1531.7 | 8185.8 |
| res_pop | 96.8 | 35.0 | 158.8 |
| com_pop | 9.1 | 4.9 | 14.2 |
| ind_pop | 14.5 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 82.3 | 23.7 | 105.2 |
| tax_fund | 257.2 | 67.8 | 1787.4 |
| road_spend | 112.4 | 10.5 | 634.9 |
| fire_spend | 68.9 | 0.9 | 489.5 |
| police_spend | 102.1 | 0.8 | 646.2 |
| powered_zones | 8.2 | 0.0 | 0.5 |
| unpowered_zones | 4.4 | 0.0 | 4.8 |
| coal_plants | 0.4 | 0.0 | 0.2 |
| nuclear_plants | 0.6 | 0.0 | 0.1 |
| road_total | 68.4 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.294 | 0.845 |
| traffic | 1.149 | 0.765 |
| pollution | 1.697 | 0.703 |
| land_value | 0.790 | 0.336 |
| crime | 1.263 | 0.580 |
| rate_of_growth | 1.277 | 0.835 |
| fire_coverage | 1.270 | 0.125 |
| police_coverage | 1.032 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.404 | 0.280 | 0.331 | 0.308 to 0.351 | 0.278 | 0.154 | 0.198 | 0.165 to 0.234 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.735 | 0.001 | 0.005 |
| all plans | 12 | 0.400 | 0.033 | 0.035 |
| all plans | 24 | 0.516 | 0.064 | 0.073 |
| state-reading plans | 1 | 0.675 | 0.002 | 0.005 |
| state-reading plans | 12 | 0.388 | 0.038 | 0.034 |
| state-reading plans | 24 | 0.509 | 0.071 | 0.069 |
| open-loop plans | 1 | 0.514 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.753 | 0.024 | 0.040 |
| open-loop plans | 24 | 1.225 | 0.043 | 0.079 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -279.72 |
| tile_cat | -36.89 |
| flags | -18.49 |
| power | -4.51 |
| half | -2671.24 |
| eighth | -37.30 |
| scalars_s2 | -5.69 |
| build_cost | -1.05 |
| scalars | -15.54 |
| ledger | -19.69 |
| bk | -29.54 |
| sc_res_pop | -1.77 |
| sc_com_pop | -0.17 |
| sc_ind_pop | -0.18 |
| sc_powered_zones | -0.07 |
| sc_unpowered_zones | -0.10 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.38 |
| sc_res_valve | -1.21 |
| sc_com_valve | -2.30 |
| sc_ind_valve | -1.80 |
| sc_score | -1.00 |
| sc_funds | -1.34 |
| sc_tax_fund | -0.76 |
| sc_road_spend | -0.93 |
| sc_fire_spend | -0.25 |
| sc_police_spend | -0.26 |
| lg_sprite_cycle | -0.85 |
| lg_total_pop | -2.20 |
| lg_res_hist0 | -1.24 |
| lg_res_hist1 | -0.92 |
| lg_com_hist0 | -0.40 |
| lg_com_hist1 | -0.31 |
| lg_ind_hist0 | -0.47 |
| lg_ind_hist1 | -0.50 |
| lg_res_cap | -0.03 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.12 |
| lg_need_church | -0.12 |
| lg_road_fund | -0.88 |
| lg_police_fund | -0.17 |
| lg_fire_fund | -0.15 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.13 |
| lg_city_center_x | -0.25 |
| lg_city_center_y | -0.15 |
| lg_pollution_max_x | -3.90 |
| lg_pollution_max_y | -4.12 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.74 |
| terrain | -6.60 |
| com_rate | -5.83 |
| kl | 13.32 |
| elbo | -3110.19 |
