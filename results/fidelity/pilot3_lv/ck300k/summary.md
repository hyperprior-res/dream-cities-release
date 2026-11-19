## pilot3_lv_samples_000300032_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 300032

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.250 | 0.254 | 0.252 | 0.229 to 0.272 | 0.137 | 0.136 | 0.136 | 0.113 to 0.163 |
| model T=0 (mode) | 0.617 | 0.228 | 0.332 | 0.308 to 0.355 | 0.824 | 0.107 | 0.189 | 0.149 to 0.235 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.335 | 0.315 | 0.432 | 0.402 |
| 12 | 0.315 | 0.316 | 0.430 | 0.428 |
| 24 | 0.285 | 0.285 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1363 | 0.657 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1894 | 0.913 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2519 | 0.794 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3324 | 1.048 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2808.6650 | 0.410 |
| funds_mae_12m | 5714.0800 | 36.8760 | 2063.8815 | 0.643 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 671.3452 | -0.064 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 992.6297 | 0.255 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 874.2525 | 0.068 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0593 | 0.569 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1531 | 0.600 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3160 | 0.739 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3153 | 0.734 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5643.2750 | 0.305 |
| funds_mae_24m | 7364.5720 | 66.5620 | 2443.6703 | 0.674 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 856.7695 | -0.267 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 1099.0967 | -0.177 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 1009.8742 | -0.324 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1067 | 0.452 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.2308 | 0.664 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2853 | 0.700 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2854 | 0.700 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.360 | 0.982 | 0.204 | 0.023 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 |
| 12 | 0.946 | 0.648 | 0.146 | 0.153 / 0.003 / 0.378 | 0.059 / 0.026 / 0.103 |
| 24 | 1.015 | 0.722 | 0.167 | 0.231 / 0.005 / 0.678 | 0.107 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 2443.7 | 1711.0 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 856.8 | 791.0 | 142.8 | 706.1 |
| com_valve | 1099.1 | 990.9 | 508.6 | 1010.2 |
| ind_valve | 1009.9 | 895.7 | 416.9 | 864.8 |
| pop | 5643.3 | 5165.7 | 1754.6 | 7353.4 |
| res_pop | 114.0 | 101.4 | 39.0 | 139.9 |
| com_pop | 11.6 | 10.1 | 4.4 | 12.8 |
| ind_pop | 16.8 | 15.2 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 155.9 | 97.4 | 25.2 | 89.6 |
| tax_fund | 1171.0 | 649.5 | 51.5 | 1444.5 |
| road_spend | 445.7 | 235.0 | 8.2 | 647.3 |
| fire_spend | 641.7 | 342.2 | 0.8 | 474.7 |
| police_spend | 745.8 | 365.7 | 6.0 | 604.1 |
| powered_zones | 7.8 | 4.5 | 0.7 | 8.6 |
| unpowered_zones | 5.8 | 4.7 | 0.6 | 7.0 |
| coal_plants | 0.6 | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.4 | 0.0 | 0.3 |
| road_total | 57.4 | 26.3 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.980 | 0.838 |
| traffic | 0.921 | 0.772 |
| pollution | 1.169 | 0.706 |
| land_value | 0.720 | 0.325 |
| crime | 0.909 | 0.566 |
| rate_of_growth | 0.945 | 0.819 |
| fire_coverage | 1.238 | 0.123 |
| police_coverage | 1.109 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -265.82 |
| tile_cat | -46.46 |
| flags | -23.89 |
| power | -6.67 |
| half | -3106.47 |
| eighth | -59.53 |
| scalars | -24.40 |
| sc_funds | -2.19 |
| sc_res_valve | -2.36 |
| sc_com_valve | -4.41 |
| sc_ind_valve | -4.27 |
| sc_res_pop | -2.77 |
| sc_com_pop | -0.90 |
| sc_ind_pop | -0.94 |
| sc_score | -0.58 |
| sc_tax_fund | -0.69 |
| sc_road_spend | -0.58 |
| sc_fire_spend | -0.25 |
| sc_police_spend | -0.26 |
| sc_powered_zones | -0.24 |
| sc_unpowered_zones | -0.30 |
| sc_coal_plants | -0.04 |
| sc_nuclear_plants | -0.04 |
| sc_road_total | -3.56 |
| n_changed | 99.43 |
| kl | 1.86 |
| elbo | -3535.10 |
| derived_viol | 0.00 |
