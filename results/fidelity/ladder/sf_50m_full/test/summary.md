## sf_50m_full_samples_001500032_dec-a

samples consumed: 1500032; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "test", "seed": 20261123, "n_trajectories": 1200, "eligible_plans": 700, "development_plans_excluded": 500, "development_transitions_excluded": 2000, "plans_shared_with_development": 0, "transitions_shared_with_development": 0, "development_transitions_inside_test_plan_windows": 502, "n_onestep": 2000, "n_plans": 700, "H": 24, "plans_by_source": {"state_reading": 527, "open_loop": 173}, "transitions_by_source": {"state_reading": 1481, "open_loop": 519}, "plans_with_no_development_transition_in_window": 325, "key": "a57bd947882a5d0e", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.277 | 0.288 | 0.282 | 0.262 to 0.301 | 0.164 | 0.173 | 0.168 | 0.143 to 0.195 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.129 | 0.129 | 0.129 | 0.118 to 0.138 | 0.049 | 0.051 | 0.050 | 0.045 to 0.055 |
| all (2000) | engine, other seed (yardstick) | 0.319 | 0.320 | 0.319 | 0.297 to 0.340 | 0.205 | 0.206 | 0.206 | 0.178 to 0.236 |
| state-reading (1481) | model T=1 (one sample) | 0.287 | 0.296 | 0.292 | 0.270 to 0.312 | 0.178 | 0.187 | 0.182 | 0.154 to 0.214 |
| state-reading (1481) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1481) | nearest neighbour (sampled) | 0.132 | 0.132 | 0.132 | 0.121 to 0.142 | 0.051 | 0.053 | 0.052 | 0.047 to 0.057 |
| state-reading (1481) | engine, other seed (yardstick) | 0.328 | 0.328 | 0.328 | 0.304 to 0.351 | 0.218 | 0.218 | 0.218 | 0.187 to 0.253 |
| open-loop (519) | model T=1 (one sample) | 0.243 | 0.258 | 0.250 | 0.229 to 0.271 | 0.119 | 0.129 | 0.124 | 0.103 to 0.143 |
| open-loop (519) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (519) | nearest neighbour (sampled) | 0.116 | 0.119 | 0.117 | 0.105 to 0.130 | 0.042 | 0.045 | 0.044 | 0.036 to 0.050 |
| open-loop (519) | engine, other seed (yardstick) | 0.289 | 0.292 | 0.290 | 0.269 to 0.309 | 0.165 | 0.169 | 0.167 | 0.141 to 0.191 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 700 | 1 | 0.510 | 0.203 | 0.001 / 0.000 / 0.013 | 0.008 / 0.006 / 0.007 | 0.366 / 0.393 |
| all plans | 700 | 12 | 0.474 | 0.154 | 0.034 / 0.003 / 0.400 | 0.050 / 0.027 / 0.112 | 0.319 / 0.423 |
| all plans | 700 | 24 | 0.634 | 0.176 | 0.067 / 0.005 / 0.614 | 0.081 / 0.039 / 0.159 | 0.279 / 0.405 |
| state-reading plans | 527 | 1 | 0.500 | 0.201 | 0.002 / 0.000 / 0.018 | 0.009 / 0.006 / 0.008 | 0.410 / 0.431 |
| state-reading plans | 527 | 12 | 0.467 | 0.162 | 0.039 / 0.003 / 0.505 | 0.050 / 0.028 / 0.106 | 0.344 / 0.442 |
| state-reading plans | 527 | 24 | 0.627 | 0.194 | 0.077 / 0.005 / 0.776 | 0.078 / 0.039 / 0.155 | 0.298 / 0.415 |
| open-loop plans | 173 | 1 | 0.503 | 0.226 | 0.000 / 0.000 / 0.000 | 0.008 / 0.005 / 0.007 | 0.157 / 0.208 |
| open-loop plans | 173 | 12 | 0.906 | 0.133 | 0.025 / 0.002 / 0.054 | 0.050 / 0.026 / 0.133 | 0.230 / 0.349 |
| open-loop plans | 173 | 24 | 1.556 | 0.128 | 0.048 / 0.005 / 0.111 | 0.090 / 0.039 / 0.168 | 0.214 / 0.369 |
| plans with no development transition in months 0..H-1 | 325 | 1 | 0.517 | 0.189 | 0.001 / 0.000 / 0.015 | 0.009 / 0.006 / 0.009 | 0.375 / 0.406 |
| plans with no development transition in months 0..H-1 | 325 | 12 | 0.466 | 0.152 | 0.035 / 0.002 / 0.433 | 0.049 / 0.030 / 0.105 | 0.324 / 0.422 |
| plans with no development transition in months 0..H-1 | 325 | 24 | 0.614 | 0.169 | 0.076 / 0.005 / 0.668 | 0.081 / 0.043 / 0.156 | 0.285 / 0.412 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2057 | 0.1683 | 0.818 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3193 | 0.2823 | 0.884 |
| pop_mae_12m | 4074.3429 | 1113.8857 | 2215.9536 | 0.628 |
| funds_mae_12m | 5673.7400 | 40.0829 | 654.8882 | 0.891 |
| res_valve_mae_12m | 665.7029 | 94.4943 | 226.6705 | 0.769 |
| com_valve_mae_12m | 1186.7643 | 440.5900 | 569.2463 | 0.828 |
| ind_valve_mae_12m | 907.8200 | 265.8071 | 352.2271 | 0.865 |
| pop_median_rel_12m | 0.1120 | 0.0270 | 0.0503 | 0.726 |
| funds_median_rel_12m | 0.4004 | 0.0028 | 0.0344 | 0.921 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4227 | 0.3190 | 0.755 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4264 | 0.3190 | 0.748 |
| pop_mae_24m | 7044.7143 | 1749.1429 | 4040.0857 | 0.567 |
| funds_mae_24m | 7303.4900 | 72.8329 | 899.9641 | 0.886 |
| res_valve_mae_24m | 787.9029 | 160.1886 | 358.7502 | 0.684 |
| com_valve_mae_24m | 1004.6614 | 507.1057 | 744.3679 | 0.523 |
| ind_valve_mae_24m | 939.1571 | 454.1971 | 653.1305 | 0.590 |
| pop_median_rel_24m | 0.1591 | 0.0394 | 0.0814 | 0.650 |
| funds_median_rel_24m | 0.6142 | 0.0052 | 0.0667 | 0.899 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4050 | 0.2787 | 0.688 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4054 | 0.2779 | 0.685 |

#### Per scalar at 24 months, all plans (700): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 900.0 | 72.8 | 7303.5 |
| tax | 0.0 | 0.0 | 2.0 |
| res_valve | 358.8 | 160.2 | 787.9 |
| com_valve | 744.4 | 507.1 | 1004.7 |
| ind_valve | 653.1 | 454.2 | 939.2 |
| pop | 4040.1 | 1749.1 | 7044.7 |
| res_pop | 89.3 | 37.1 | 135.5 |
| com_pop | 10.2 | 5.0 | 12.3 |
| ind_pop | 12.3 | 5.8 | 19.4 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 100.8 | 26.8 | 89.0 |
| tax_fund | 226.8 | 53.9 | 1490.0 |
| road_spend | 84.5 | 9.0 | 638.2 |
| fire_spend | 52.2 | 1.3 | 473.1 |
| police_spend | 90.5 | 3.4 | 618.5 |
| powered_zones | 10.2 | 0.9 | 9.0 |
| unpowered_zones | 6.3 | 0.8 | 7.1 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.3 |
| road_total | 60.7 | 11.8 | 86.1 |

#### Per scalar at 24 months, state-reading plans (527): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 884.8 | 71.1 | 8109.3 |
| tax | 0.0 | 0.0 | 1.4 |
| res_valve | 294.0 | 128.0 | 549.2 |
| com_valve | 798.8 | 545.4 | 967.3 |
| ind_valve | 717.5 | 502.9 | 866.6 |
| pop | 3972.0 | 1820.5 | 6670.1 |
| res_pop | 86.7 | 37.8 | 127.8 |
| com_pop | 9.9 | 5.0 | 11.7 |
| ind_pop | 12.4 | 6.1 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 102.4 | 27.8 | 83.7 |
| tax_fund | 210.7 | 49.4 | 1392.4 |
| road_spend | 80.8 | 8.4 | 639.3 |
| fire_spend | 49.3 | 1.4 | 467.7 |
| police_spend | 86.0 | 4.3 | 609.4 |
| powered_zones | 10.7 | 1.2 | 11.7 |
| unpowered_zones | 7.0 | 1.1 | 7.9 |
| coal_plants | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.0 | 0.4 |
| road_total | 60.9 | 12.3 | 99.0 |

#### Per scalar at 24 months, open-loop plans (173): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 946.1 | 78.1 | 4848.9 |
| tax | 0.0 | 0.0 | 4.1 |
| res_valve | 555.9 | 258.1 | 1515.1 |
| com_valve | 578.6 | 390.3 | 1118.5 |
| ind_valve | 457.0 | 305.8 | 1160.1 |
| pop | 4247.5 | 1531.7 | 8185.8 |
| res_pop | 97.0 | 35.0 | 158.8 |
| com_pop | 11.0 | 4.9 | 14.2 |
| ind_pop | 12.2 | 4.7 | 20.6 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 96.1 | 23.7 | 105.2 |
| tax_fund | 276.0 | 67.8 | 1787.4 |
| road_spend | 95.8 | 10.5 | 634.9 |
| fire_spend | 61.1 | 0.9 | 489.5 |
| police_spend | 104.1 | 0.8 | 646.2 |
| powered_zones | 8.7 | 0.0 | 0.5 |
| unpowered_zones | 4.3 | 0.0 | 4.8 |
| coal_plants | 0.2 | 0.0 | 0.2 |
| nuclear_plants | 0.4 | 0.0 | 0.1 |
| road_total | 59.9 | 10.3 | 46.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.323 | 0.845 |
| traffic | 1.067 | 0.765 |
| pollution | 1.807 | 0.703 |
| land_value | 0.743 | 0.336 |
| crime | 1.229 | 0.580 |
| rate_of_growth | 1.228 | 0.835 |
| fire_coverage | 1.594 | 0.125 |
| police_coverage | 1.462 | 0.126 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.558 | 0.264 | 0.358 | 0.336 to 0.379 | 0.479 | 0.136 | 0.212 | 0.174 to 0.253 |
| all (2000) | nearest neighbour (mode) | 0.277 | 0.017 | 0.032 | 0.026 to 0.040 | 0.279 | 0.035 | 0.062 | 0.051 to 0.074 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.392 | 0.001 | 0.006 |
| all plans | 12 | 0.355 | 0.031 | 0.043 |
| all plans | 24 | 0.499 | 0.076 | 0.068 |
| state-reading plans | 1 | 0.385 | 0.001 | 0.006 |
| state-reading plans | 12 | 0.350 | 0.032 | 0.043 |
| state-reading plans | 24 | 0.498 | 0.089 | 0.065 |
| open-loop plans | 1 | 0.371 | 0.000 | 0.005 |
| open-loop plans | 12 | 0.668 | 0.028 | 0.043 |
| open-loop plans | 24 | 1.282 | 0.057 | 0.084 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -209.71 |
| tile_cat | -29.14 |
| flags | -14.28 |
| power | -2.24 |
| half | -2310.67 |
| eighth | -33.94 |
| scalars_s2 | -5.15 |
| build_cost | -0.78 |
| scalars | -12.26 |
| ledger | -13.50 |
| bk | -20.62 |
| sc_res_pop | -1.47 |
| sc_com_pop | -0.14 |
| sc_ind_pop | -0.14 |
| sc_powered_zones | -0.01 |
| sc_unpowered_zones | -0.01 |
| sc_coal_plants | -0.00 |
| sc_nuclear_plants | -0.00 |
| sc_road_total | -3.36 |
| sc_res_valve | -0.99 |
| sc_com_valve | -2.06 |
| sc_ind_valve | -1.08 |
| sc_score | -0.51 |
| sc_funds | -0.96 |
| sc_tax_fund | -0.48 |
| sc_road_spend | -0.69 |
| sc_fire_spend | -0.18 |
| sc_police_spend | -0.18 |
| lg_sprite_cycle | -1.11 |
| lg_total_pop | -1.40 |
| lg_res_hist0 | -0.24 |
| lg_res_hist1 | -0.40 |
| lg_com_hist0 | -0.05 |
| lg_com_hist1 | -0.20 |
| lg_ind_hist0 | -0.06 |
| lg_ind_hist1 | -0.17 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.06 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.69 |
| lg_police_fund | -0.14 |
| lg_fire_fund | -0.21 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.06 |
| lg_city_center_x | -0.02 |
| lg_city_center_y | -0.03 |
| lg_pollution_max_x | -3.08 |
| lg_pollution_max_y | -3.23 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.32 |
| terrain | -4.74 |
| com_rate | -2.95 |
| kl | 14.26 |
| elbo | -2648.47 |
