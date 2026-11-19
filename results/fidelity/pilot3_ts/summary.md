## pilot2_50m_samples_000600064_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 600064

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.266 | 0.267 | 0.267 | 0.245 to 0.286 | 0.151 | 0.148 | 0.150 | 0.126 to 0.177 |
| model T=0 (mode) | 0.611 | 0.242 | 0.346 | 0.322 to 0.369 | 0.809 | 0.113 | 0.198 | 0.157 to 0.242 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.339 | 0.344 | 0.432 | 0.402 |
| 12 | 0.326 | 0.330 | 0.430 | 0.428 |
| 24 | 0.292 | 0.294 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1497 | 0.722 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1979 | 0.954 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2667 | 0.841 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3464 | 1.092 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 3057.8100 | 0.327 |
| funds_mae_12m | 5714.0800 | 36.8760 | 3560.8890 | 0.379 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 533.1280 | 0.197 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 951.1247 | 0.304 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 838.8487 | 0.122 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0674 | 0.464 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.2908 | 0.233 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3298 | 0.771 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3258 | 0.758 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 6389.5000 | 0.172 |
| funds_mae_24m | 7364.5720 | 66.5620 | 3940.9685 | 0.469 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 660.2970 | 0.081 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 897.0310 | 0.226 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 968.4878 | -0.232 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1303 | 0.251 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.3761 | 0.448 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2935 | 0.720 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2915 | 0.715 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.694 | 1.529 | 0.204 | 0.004 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 |
| 12 | 0.806 | 0.710 | 0.146 | 0.291 / 0.003 / 0.378 | 0.067 / 0.026 / 0.103 |
| 24 | 0.858 | 0.746 | 0.167 | 0.376 / 0.005 / 0.678 | 0.130 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 3941.0 | 3482.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 660.3 | 596.5 | 142.8 | 706.1 |
| com_valve | 897.0 | 812.9 | 508.6 | 1010.2 |
| ind_valve | 968.5 | 883.2 | 416.9 | 864.8 |
| pop | 6389.5 | 5883.5 | 1754.6 | 7353.4 |
| res_pop | 123.6 | 107.4 | 39.0 | 139.9 |
| com_pop | 12.8 | 11.1 | 4.4 | 12.8 |
| ind_pop | 20.4 | 18.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 102.5 | 79.4 | 25.2 | 89.6 |
| tax_fund | 745.4 | 478.6 | 51.5 | 1444.5 |
| road_spend | 246.1 | 185.7 | 8.2 | 647.3 |
| fire_spend | 176.6 | 101.9 | 0.8 | 474.7 |
| police_spend | 216.4 | 158.1 | 6.0 | 604.1 |
| powered_zones | 8.1 | 7.8 | 0.7 | 8.6 |
| unpowered_zones | 7.2 | 6.9 | 0.6 | 7.0 |
| coal_plants | 0.6 | 0.6 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.4 | 0.0 | 0.3 |
| road_total | 64.5 | 42.9 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 1.026 | 0.838 |
| traffic | 0.947 | 0.772 |
| pollution | 1.127 | 0.706 |
| land_value | 0.680 | 0.325 |
| crime | 0.911 | 0.566 |
| rate_of_growth | 1.023 | 0.819 |
| fire_coverage | 1.189 | 0.123 |
| police_coverage | 1.142 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -259.24 |
| tile_cat | -40.89 |
| flags | -20.43 |
| power | -5.39 |
| half | -2972.79 |
| eighth | -55.94 |
| scalars | -23.85 |
| sc_funds | -1.90 |
| sc_res_valve | -2.01 |
| sc_com_valve | -4.23 |
| sc_ind_valve | -3.98 |
| sc_res_pop | -3.39 |
| sc_com_pop | -0.93 |
| sc_ind_pop | -1.41 |
| sc_score | -0.52 |
| sc_tax_fund | -0.59 |
| sc_road_spend | -0.44 |
| sc_fire_spend | -0.21 |
| sc_police_spend | -0.22 |
| sc_powered_zones | -0.16 |
| sc_unpowered_zones | -0.24 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.56 |
| n_changed | 99.43 |
| kl | 3.43 |
| elbo | -3381.97 |
| derived_viol | 0.00 |
