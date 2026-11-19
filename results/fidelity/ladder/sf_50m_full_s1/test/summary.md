## sf_50m_full_s1_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.277 | 0.287 | 0.282 | 0.262 to 0.302 | 0.166 | 0.170 | 0.168 | 0.144 to 0.195 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.286 | 0.296 | 0.291 | 0.269 to 0.312 | 0.179 | 0.184 | 0.182 | 0.153 to 0.214 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.247 | 0.255 | 0.251 | 0.229 to 0.272 | 0.123 | 0.126 | 0.125 | 0.105 to 0.144 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.516 | 0.203 | 0.002 / 0.000 / 0.013 | 0.009 / 0.006 / 0.007 | 0.365 / 0.393 |
| all plans | 700 | 12 | 0.429 | 0.154 | 0.038 / 0.003 / 0.400 | 0.044 / 0.027 / 0.112 | 0.329 / 0.423 |
| all plans | 700 | 24 | 0.626 | 0.176 | 0.092 / 0.005 / 0.614 | 0.079 / 0.039 / 0.159 | 0.278 / 0.405 |
| state-reading plans | 527 | 1 | 0.514 | 0.201 | 0.002 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.408 / 0.431 |
| state-reading plans | 527 | 12 | 0.424 | 0.162 | 0.041 / 0.003 / 0.505 | 0.045 / 0.028 / 0.106 | 0.357 / 0.442 |
| state-reading plans | 527 | 24 | 0.622 | 0.194 | 0.099 / 0.005 / 0.776 | 0.078 / 0.039 / 0.155 | 0.300 / 0.415 |
| open-loop plans | 173 | 1 | 0.486 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.159 / 0.208 |
| open-loop plans | 173 | 12 | 0.810 | 0.133 | 0.029 / 0.002 / 0.054 | 0.043 / 0.026 / 0.133 | 0.230 / 0.349 |
| open-loop plans | 173 | 24 | 1.595 | 0.128 | 0.069 / 0.005 / 0.111 | 0.080 / 0.039 / 0.168 | 0.203 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.489 | 0.189 | 0.002 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.376 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.431 | 0.152 | 0.040 / 0.002 / 0.433 | 0.045 / 0.030 / 0.105 | 0.333 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.614 | 0.169 | 0.105 / 0.005 / 0.668 | 0.082 / 0.043 / 0.156 | 0.282 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1682 | 0.818 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2821 | 0.884 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 1877.2929 | 0.742 |
| funds_mae_12m | 5673.7400 | 40.0829 | 681.3320 | 0.886 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 196.3943 | 0.822 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 569.0327 | 0.828 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 348.6055 | 0.871 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0445 | 0.794 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0381 | 0.911 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3295 | 0.780 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3298 | 0.774 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 3569.1750 | 0.656 |
| funds_mae_24m | 7303.4900 | 72.8329 | 1085.2732 | 0.860 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 405.4025 | 0.609 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 646.1659 | 0.721 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 600.2098 | 0.699 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0786 | 0.672 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0920 | 0.857 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.2777 | 0.686 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.2783 | 0.687 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1085.3 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 405.4 | 160.2 | 787.9 |
| com_valve | 646.2 | 507.1 | 1004.7 |
| ind_valve | 600.2 | 454.2 | 939.2 |
| pop | 3569.2 | 1749.1 | 7044.7 |
| res_pop | 71.8 | 37.1 | 135.5 |
| com_pop | 7.8 | 5.0 | 12.3 |
| ind_pop | 14.5 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 126.0 | 26.8 | 89.0 |
| tax_fund | 136.3 | 53.9 | 1490.0 |
| road_spend | 75.2 | 9.0 | 638.2 |
| fire_spend | 41.7 | 1.3 | 473.1 |
| police_spend | 59.2 | 3.4 | 618.5 |
| powered_zones | 10.7 | 0.9 | 9.0 |
| unpowered_zones | 6.4 | 0.8 | 7.1 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 59.9 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1074.0 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 379.1 | 128.0 | 549.2 |
| com_valve | 687.2 | 545.4 | 967.3 |
| ind_valve | 652.3 | 502.9 | 866.6 |
| pop | 3649.5 | 1820.5 | 6670.1 |
| res_pop | 72.5 | 37.8 | 127.8 |
| com_pop | 7.8 | 5.0 | 11.7 |
| ind_pop | 15.1 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 128.4 | 27.8 | 83.7 |
| tax_fund | 124.5 | 49.4 | 1392.4 |
| road_spend | 71.6 | 8.4 | 639.3 |
| fire_spend | 37.8 | 1.4 | 467.7 |
| police_spend | 54.8 | 4.3 | 609.4 |
| powered_zones | 11.3 | 1.2 | 11.7 |
| unpowered_zones | 7.0 | 1.1 | 7.9 |
| coal_plants | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 60.8 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1119.7 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 485.6 | 258.1 | 1515.1 |
| com_valve | 521.0 | 390.3 | 1118.5 |
| ind_valve | 441.6 | 305.8 | 1160.1 |
| pop | 3324.5 | 1531.7 | 8185.8 |
| res_pop | 70.0 | 35.0 | 158.8 |
| com_pop | 7.7 | 4.9 | 14.2 |
| ind_pop | 12.7 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 118.9 | 23.7 | 105.2 |
| tax_fund | 172.4 | 67.8 | 1787.4 |
| road_spend | 86.3 | 10.5 | 634.9 |
| fire_spend | 53.7 | 0.9 | 489.5 |
| police_spend | 72.7 | 0.8 | 646.2 |
| powered_zones | 8.9 | 0.0 | 0.5 |
| unpowered_zones | 4.7 | 0.0 | 4.8 |
| coal_plants | 0.3 | 0.0 | 0.2 |
| nuclear_plants | 0.5 | 0.0 | 0.1 |
| road_total | 57.2 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.275 | 0.845 |
| traffic | 1.044 | 0.765 |
| pollution | 1.745 | 0.703 |
| land_value | 0.751 | 0.336 |
| crime | 1.189 | 0.580 |
| rate_of_growth | 1.132 | 0.835 |
| fire_coverage | 3.591 | 0.125 |
| police_coverage | 1.557 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.572 | 0.262 | 0.359 | 0.337 to 0.380 | 0.552 | 0.132 | 0.213 | 0.175 to 0.254 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.412 | 0.001 | 0.005 |
| all plans | 12 | 0.313 | 0.034 | 0.035 |
| all plans | 24 | 0.491 | 0.115 | 0.062 |
| state-reading plans | 1 | 0.408 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.311 | 0.038 | 0.034 |
| state-reading plans | 24 | 0.494 | 0.124 | 0.064 |
| open-loop plans | 1 | 0.372 | 0.000 | 0.004 |
| open-loop plans | 12 | 0.554 | 0.030 | 0.037 |
| open-loop plans | 24 | 1.326 | 0.097 | 0.057 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -209.25 |
| tile_cat | -28.89 |
| flags | -13.75 |
| power | -1.85 |
| half | -2307.30 |
| eighth | -33.83 |
| scalars_s2 | -5.14 |
| build_cost | -0.78 |
| scalars | -12.10 |
| ledger | -13.02 |
| bk | -19.98 |
| sc_res_pop | -1.46 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.14 |
| sc_powered_zones | -0.01 |
| sc_unpowered_zones | -0.02 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.36 |
| sc_res_valve | -0.95 |
| sc_com_valve | -2.06 |
| sc_ind_valve | -1.07 |
| sc_score | -0.53 |
| sc_funds | -0.98 |
| sc_tax_fund | -0.46 |
| sc_road_spend | -0.61 |
| sc_fire_spend | -0.13 |
| sc_police_spend | -0.18 |
| lg_sprite_cycle | -0.85 |
| lg_total_pop | -1.49 |
| lg_res_hist0 | -0.24 |
| lg_res_hist1 | -0.48 |
| lg_com_hist0 | -0.06 |
| lg_com_hist1 | -0.27 |
| lg_ind_hist0 | -0.07 |
| lg_ind_hist1 | -0.15 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.64 |
| lg_police_fund | -0.14 |
| lg_fire_fund | -0.11 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.02 |
| lg_pollution_max_x | -3.05 |
| lg_pollution_max_y | -2.97 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -4.85 |
| com_rate | -2.84 |
| kl | 15.35 |
| elbo | -2643.80 |
