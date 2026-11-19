## os_50m_full_samples_001200000_dec-a

samples consumed: 1200000; weights loaded: ema; decoding a (T=1.0, overlays sample)

selection: {"name": "dev", "seed": 20261109, "n_trajectories": 1200, "n_onestep": 2000, "n_plans": 500, "H": 24, "plans_by_source": {"state_reading": 394, "open_loop": 106}, "transitions_by_source": {"state_reading": 1516, "open_loop": 484}, "key": "3eed58d3b821a96c", "split": "heldout_eval"}

### Headline: one model sample (T=1) against the stored run

The engine row replays the same month or plan under another seed: a sample-against-sample yardstick for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not comparable with it.

#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=1 (one sample) | 0.279 | 0.277 | 0.278 | 0.256 to 0.298 | 0.174 | 0.164 | 0.169 | 0.143 to 0.201 |
| all (2000) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| all (2000) | nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| all (2000) | engine, other seed (yardstick) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |
| state-reading (1516) | model T=1 (one sample) | 0.289 | 0.285 | 0.287 | 0.265 to 0.307 | 0.190 | 0.177 | 0.183 | 0.152 to 0.219 |
| state-reading (1516) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| state-reading (1516) | nearest neighbour (sampled) | 0.135 | 0.134 | 0.135 | 0.124 to 0.145 | 0.053 | 0.054 | 0.053 | 0.048 to 0.060 |
| state-reading (1516) | engine, other seed (yardstick) | 0.324 | 0.325 | 0.325 | 0.300 to 0.347 | 0.219 | 0.220 | 0.219 | 0.187 to 0.257 |
| open-loop (484) | model T=1 (one sample) | 0.243 | 0.246 | 0.244 | 0.223 to 0.266 | 0.121 | 0.120 | 0.121 | 0.102 to 0.143 |
| open-loop (484) | copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| open-loop (484) | nearest neighbour (sampled) | 0.111 | 0.116 | 0.113 | 0.101 to 0.126 | 0.035 | 0.039 | 0.037 | 0.033 to 0.041 |
| open-loop (484) | engine, other seed (yardstick) | 0.289 | 0.289 | 0.289 | 0.262 to 0.315 | 0.166 | 0.167 | 0.167 | 0.145 to 0.193 |

#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)

| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |
|---|---|---|---|---|---|---|---|
| all plans | 500 | 1 | 1.030 | 0.204 | 0.010 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 | 0.372 / 0.402 |
| all plans | 500 | 12 | 0.604 | 0.146 | 0.063 / 0.003 / 0.378 | 0.041 / 0.026 / 0.103 | 0.371 / 0.428 |
| all plans | 500 | 24 | 0.612 | 0.167 | 0.082 / 0.005 / 0.678 | 0.063 / 0.042 / 0.160 | 0.344 / 0.408 |
| state-reading plans | 394 | 1 | 0.898 | 0.208 | 0.013 / 0.000 / 0.018 | 0.009 / 0.006 / 0.007 | 0.407 / 0.436 |
| state-reading plans | 394 | 12 | 0.608 | 0.151 | 0.076 / 0.003 / 0.465 | 0.041 / 0.025 / 0.103 | 0.392 / 0.442 |
| state-reading plans | 394 | 24 | 0.631 | 0.184 | 0.104 / 0.005 / 0.791 | 0.062 / 0.044 / 0.150 | 0.358 / 0.412 |
| open-loop plans | 106 | 1 | 1.372 | 0.199 | 0.000 / 0.000 / 0.000 | 0.009 / 0.008 / 0.007 | 0.222 / 0.257 |
| open-loop plans | 106 | 12 | 0.897 | 0.131 | 0.016 / 0.002 / 0.061 | 0.040 / 0.031 / 0.103 | 0.291 / 0.372 |
| open-loop plans | 106 | 24 | 0.890 | 0.122 | 0.020 / 0.005 / 0.140 | 0.065 / 0.036 / 0.203 | 0.294 / 0.390 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state has changed-since-start F1 0)

#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)

| metric | copy | engine yardstick | model T=1 | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1689 | 0.814 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2781 | 0.877 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1760.3400 | 0.758 |
| funds_mae_12m | 5714.0800 | 36.8760 | 907.5638 | 0.847 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 219.5608 | 0.791 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 525.3397 | 0.803 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 336.4418 | 0.882 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0409 | 0.807 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0635 | 0.838 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3712 | 0.868 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3643 | 0.848 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2889.9250 | 0.797 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1053.2375 | 0.865 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 275.4228 | 0.765 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 603.3945 | 0.811 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 622.7408 | 0.540 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0630 | 0.825 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0824 | 0.885 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3444 | 0.845 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3390 | 0.831 |

#### Per scalar at 24 months, all plans (500): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1053.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 1.9 |
| res_valve | 275.4 | 142.8 | 706.1 |
| com_valve | 603.4 | 508.6 | 1010.2 |
| ind_valve | 622.7 | 416.9 | 864.8 |
| pop | 2889.9 | 1754.6 | 7353.4 |
| res_pop | 64.9 | 39.0 | 139.9 |
| com_pop | 6.6 | 4.4 | 12.8 |
| ind_pop | 9.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 42.5 | 25.2 | 89.6 |
| tax_fund | 141.5 | 51.5 | 1444.5 |
| road_spend | 85.2 | 8.2 | 647.3 |
| fire_spend | 55.5 | 0.8 | 474.7 |
| police_spend | 75.3 | 6.0 | 604.1 |
| powered_zones | 8.9 | 0.7 | 8.6 |
| unpowered_zones | 5.4 | 0.6 | 7.0 |
| coal_plants | 0.7 | 0.0 | 0.5 |
| nuclear_plants | 0.8 | 0.0 | 0.3 |
| road_total | 62.0 | 10.9 | 85.5 |

#### Per scalar at 24 months, state-reading plans (394): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1053.5 | 63.0 | 7655.5 |
| tax | 0.0 | 0.0 | 1.3 |
| res_valve | 250.8 | 130.7 | 533.4 |
| com_valve | 630.2 | 541.8 | 962.1 |
| ind_valve | 675.0 | 446.9 | 814.5 |
| pop | 2888.7 | 1810.1 | 6881.1 |
| res_pop | 64.6 | 39.6 | 131.0 |
| com_pop | 6.6 | 4.5 | 12.1 |
| ind_pop | 10.0 | 5.9 | 19.0 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 43.9 | 26.2 | 83.7 |
| tax_fund | 133.4 | 47.1 | 1400.1 |
| road_spend | 79.6 | 8.1 | 645.8 |
| fire_spend | 48.7 | 0.8 | 464.7 |
| police_spend | 68.2 | 6.4 | 591.3 |
| powered_zones | 10.4 | 0.9 | 10.7 |
| unpowered_zones | 5.8 | 0.8 | 7.0 |
| coal_plants | 0.8 | 0.0 | 0.5 |
| nuclear_plants | 0.9 | 0.0 | 0.4 |
| road_total | 62.1 | 11.0 | 96.7 |

#### Per scalar at 24 months, open-loop plans (106): mean absolute error

| scalar | model sample | engine yardstick | copy |
|---|---|---|---|
| funds | 1052.3 | 79.7 | 6283.1 |
| tax | 0.0 | 0.0 | 4.2 |
| res_valve | 366.8 | 187.8 | 1348.3 |
| com_valve | 503.8 | 385.4 | 1188.9 |
| ind_valve | 428.6 | 305.2 | 1051.7 |
| pop | 2894.5 | 1548.5 | 9108.7 |
| res_pop | 65.9 | 37.0 | 172.8 |
| com_pop | 6.7 | 4.2 | 15.7 |
| ind_pop | 9.7 | 5.6 | 22.3 |
| city_time | 0.0 | 0.0 | 96.0 |
| score | 36.9 | 21.3 | 111.7 |
| tax_fund | 171.6 | 68.0 | 1609.5 |
| road_spend | 105.9 | 8.8 | 653.2 |
| fire_spend | 80.9 | 1.1 | 512.0 |
| police_spend | 101.8 | 4.6 | 651.4 |
| powered_zones | 3.5 | 0.0 | 0.5 |
| unpowered_zones | 4.1 | 0.0 | 6.7 |
| coal_plants | 0.3 | 0.0 | 0.1 |
| nuclear_plants | 0.4 | 0.0 | 0.2 |
| road_total | 61.8 | 10.5 | 43.7 |

#### Overlays at 24 months, all plans: error ratio to copy-last-state

| overlay | model sample | engine yardstick |
|---|---|---|
| pop_density | 1.025 | 0.838 |
| traffic | 1.100 | 0.772 |
| pollution | 1.557 | 0.706 |
| land_value | 0.677 | 0.325 |
| crime | 1.034 | 0.566 |
| rate_of_growth | 1.003 | 0.819 |
| fire_coverage | 1.616 | 0.123 |
| police_coverage | 1.025 | 0.114 |

### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)

| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|---|
| all (2000) | model T=0 (mode) | 0.628 | 0.249 | 0.357 | 0.332 to 0.379 | 0.835 | 0.123 | 0.214 | 0.171 to 0.261 |
| all (2000) | nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |

| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |
|---|---|---|---|---|
| all plans | 1 | 0.702 | 0.005 | 0.006 |
| all plans | 12 | 0.373 | 0.041 | 0.031 |
| all plans | 24 | 0.397 | 0.067 | 0.052 |
| state-reading plans | 1 | 0.559 | 0.005 | 0.006 |
| state-reading plans | 12 | 0.375 | 0.047 | 0.030 |
| state-reading plans | 24 | 0.417 | 0.085 | 0.053 |
| open-loop plans | 1 | 0.957 | 0.000 | 0.006 |
| open-loop plans | 12 | 0.558 | 0.015 | 0.034 |
| open-loop plans | 24 | 0.511 | 0.018 | 0.051 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -243.17 |
| tile_cat | -35.07 |
| flags | -17.60 |
| power | -4.25 |
| half | -2638.50 |
| eighth | -41.68 |
| scalars_s2 | -7.90 |
| build_cost | -1.54 |
| scalars | -15.48 |
| ledger | -13.70 |
| bk | -21.29 |
| sc_res_pop | -2.55 |
| sc_com_pop | -0.58 |
| sc_ind_pop | -0.66 |
| sc_powered_zones | -0.22 |
| sc_unpowered_zones | -0.29 |
| sc_coal_plants | -0.04 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.52 |
| sc_res_valve | -1.01 |
| sc_com_valve | -2.08 |
| sc_ind_valve | -1.79 |
| sc_score | -0.37 |
| sc_funds | -1.14 |
| sc_tax_fund | -0.44 |
| sc_road_spend | -0.45 |
| sc_fire_spend | -0.17 |
| sc_police_spend | -0.14 |
| lg_sprite_cycle | -1.09 |
| lg_total_pop | -1.58 |
| lg_res_hist0 | -0.70 |
| lg_res_hist1 | -0.55 |
| lg_com_hist0 | -0.17 |
| lg_com_hist1 | -0.20 |
| lg_ind_hist0 | -0.25 |
| lg_ind_hist1 | -0.32 |
| lg_res_cap | -0.00 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.46 |
| lg_police_fund | -0.13 |
| lg_fire_fund | -0.15 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.13 |
| lg_city_center_y | -0.08 |
| lg_pollution_max_x | -2.74 |
| lg_pollution_max_y | -2.67 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -7.48 |
| com_rate | -6.45 |
| kl | 7.59 |
| elbo | -3032.52 |
