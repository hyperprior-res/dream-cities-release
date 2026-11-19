## pilot3_ts_samples_000300032_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 300032

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.252 | 0.256 | 0.254 | 0.232 to 0.274 | 0.137 | 0.135 | 0.136 | 0.114 to 0.162 |
| model T=0 (mode) | 0.606 | 0.233 | 0.337 | 0.313 to 0.358 | 0.805 | 0.106 | 0.187 | 0.148 to 0.230 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.336 | 0.318 | 0.432 | 0.402 |
| 12 | 0.310 | 0.311 | 0.430 | 0.428 |
| 24 | 0.281 | 0.281 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1363 | 0.657 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1872 | 0.903 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2540 | 0.801 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3368 | 1.062 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 3036.9850 | 0.334 |
| funds_mae_12m | 5714.0800 | 36.8760 | 2000.4730 | 0.654 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 696.5287 | -0.112 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 1097.3108 | 0.132 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 964.6608 | -0.068 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0656 | 0.488 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1469 | 0.616 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3113 | 0.728 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3102 | 0.722 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5939.1900 | 0.253 |
| funds_mae_24m | 7364.5720 | 66.5620 | 2444.2280 | 0.674 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 922.8090 | -0.385 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 1164.2675 | -0.307 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 1015.1770 | -0.336 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1145 | 0.386 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.2188 | 0.682 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2815 | 0.691 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2812 | 0.689 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.326 | 0.983 | 0.204 | 0.024 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 |
| 12 | 0.962 | 0.684 | 0.146 | 0.147 / 0.003 / 0.378 | 0.066 / 0.026 / 0.103 |
| 24 | 1.035 | 0.748 | 0.167 | 0.219 / 0.005 / 0.678 | 0.114 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 2444.2 | 1831.5 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 922.8 | 857.7 | 142.8 | 706.1 |
| com_valve | 1164.3 | 1039.4 | 508.6 | 1010.2 |
| ind_valve | 1015.2 | 884.9 | 416.9 | 864.8 |
| pop | 5939.2 | 5515.2 | 1754.6 | 7353.4 |
| res_pop | 117.4 | 105.5 | 39.0 | 139.9 |
| com_pop | 12.2 | 10.8 | 4.4 | 12.8 |
| ind_pop | 17.7 | 16.2 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 162.6 | 100.1 | 25.2 | 89.6 |
| tax_fund | 1116.3 | 575.7 | 51.5 | 1444.5 |
| road_spend | 414.4 | 187.0 | 8.2 | 647.3 |
| fire_spend | 638.8 | 343.3 | 0.8 | 474.7 |
| police_spend | 781.3 | 428.0 | 6.0 | 604.1 |
| powered_zones | 7.4 | 5.0 | 0.7 | 8.6 |
| unpowered_zones | 5.5 | 4.3 | 0.6 | 7.0 |
| coal_plants | 0.6 | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.4 | 0.0 | 0.3 |
| road_total | 55.2 | 26.5 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 1.007 | 0.838 |
| traffic | 0.941 | 0.772 |
| pollution | 1.180 | 0.706 |
| land_value | 0.735 | 0.325 |
| crime | 0.932 | 0.566 |
| rate_of_growth | 0.982 | 0.819 |
| fire_coverage | 1.336 | 0.123 |
| police_coverage | 1.149 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -265.84 |
| tile_cat | -46.31 |
| flags | -24.99 |
| power | -6.68 |
| half | -3118.88 |
| eighth | -60.03 |
| scalars | -24.42 |
| sc_funds | -2.19 |
| sc_res_valve | -2.42 |
| sc_com_valve | -4.45 |
| sc_ind_valve | -4.31 |
| sc_res_pop | -2.74 |
| sc_com_pop | -0.91 |
| sc_ind_pop | -0.87 |
| sc_score | -0.58 |
| sc_tax_fund | -0.69 |
| sc_road_spend | -0.58 |
| sc_fire_spend | -0.26 |
| sc_police_spend | -0.26 |
| sc_powered_zones | -0.23 |
| sc_unpowered_zones | -0.30 |
| sc_coal_plants | -0.04 |
| sc_nuclear_plants | -0.04 |
| sc_road_total | -3.57 |
| n_changed | 99.43 |
| kl | 1.94 |
| elbo | -3549.10 |
| derived_viol | 0.00 |
