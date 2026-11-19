## pilot_50m_samples_000150016

samples consumed: 150016

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.221 | 0.224 | 0.223 | 0.203 to 0.241 | 0.092 | 0.091 | 0.092 | 0.080 to 0.106 |
| model T=0 (mode) | 0.589 | 0.200 | 0.299 | 0.277 to 0.321 | 0.703 | 0.080 | 0.144 | 0.114 to 0.178 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.279 | 0.244 | 0.432 | 0.402 |
| 12 | 0.229 | 0.220 | 0.430 | 0.428 |
| 24 | 0.207 | 0.200 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.0915 | 0.441 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1440 | 0.694 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2228 | 0.703 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.2991 | 0.943 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 3094.9550 | 0.314 |
| funds_mae_12m | 5714.0800 | 36.8760 | 5028.1180 | 0.121 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 664.3380 | -0.051 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 1073.5065 | 0.160 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 930.7060 | -0.017 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0697 | 0.435 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.3402 | 0.102 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.2203 | 0.515 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.2294 | 0.534 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 6453.8050 | 0.161 |
| funds_mae_24m | 7364.5720 | 66.5620 | 6156.4400 | 0.166 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 792.3388 | -0.153 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 1124.5587 | -0.228 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 1060.2845 | -0.437 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1319 | 0.237 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.5214 | 0.232 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2004 | 0.492 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2074 | 0.509 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.869 | 1.675 | 0.204 | 0.017 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 |
| 12 | 0.910 | 0.821 | 0.146 | 0.340 / 0.003 / 0.378 | 0.070 / 0.026 / 0.103 |
| 24 | 0.959 | 0.844 | 0.167 | 0.521 / 0.005 / 0.678 | 0.132 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 6156.4 | 5868.1 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 792.3 | 755.8 | 142.8 | 706.1 |
| com_valve | 1124.6 | 1032.2 | 508.6 | 1010.2 |
| ind_valve | 1060.3 | 969.5 | 416.9 | 864.8 |
| pop | 6453.8 | 6020.0 | 1754.6 | 7353.4 |
| res_pop | 138.4 | 128.0 | 39.0 | 139.9 |
| com_pop | 14.6 | 12.8 | 4.4 | 12.8 |
| ind_pop | 19.2 | 17.8 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 114.2 | 93.7 | 25.2 | 89.6 |
| tax_fund | 833.1 | 536.3 | 51.5 | 1444.5 |
| road_spend | 301.7 | 168.8 | 8.2 | 647.3 |
| fire_spend | 261.8 | 193.2 | 0.8 | 474.7 |
| police_spend | 346.1 | 234.2 | 6.0 | 604.1 |
| powered_zones | 9.2 | 8.5 | 0.7 | 8.6 |
| unpowered_zones | 9.1 | 8.9 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.4 | 0.0 | 0.3 |
| road_total | 76.8 | 50.9 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 1.281 | 0.838 |
| traffic | 1.439 | 0.772 |
| pollution | 1.863 | 0.706 |
| land_value | 1.320 | 0.325 |
| crime | 1.362 | 0.566 |
| rate_of_growth | 1.236 | 0.819 |
| fire_coverage | 1.666 | 0.123 |
| police_coverage | 1.283 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -271.52 |
| tile_cat | -58.23 |
| flags | -33.74 |
| power | -8.90 |
| half | -3270.70 |
| eighth | -68.43 |
| scalars | -26.68 |
| sc_funds | -2.40 |
| sc_res_valve | -2.31 |
| sc_com_valve | -4.41 |
| sc_ind_valve | -4.28 |
| sc_res_pop | -3.51 |
| sc_com_pop | -1.43 |
| sc_ind_pop | -1.53 |
| sc_score | -0.58 |
| sc_tax_fund | -0.63 |
| sc_road_spend | -0.48 |
| sc_fire_spend | -0.25 |
| sc_police_spend | -0.25 |
| sc_powered_zones | -0.28 |
| sc_unpowered_zones | -0.54 |
| sc_coal_plants | -0.06 |
| sc_nuclear_plants | -0.04 |
| sc_road_total | -3.71 |
| n_changed | 99.43 |
| kl | 1.75 |
| elbo | -3739.96 |
| derived_viol | 0.00 |

## pilot_50m_samples_000300032

samples consumed: 300032

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.248 | 0.253 | 0.250 | 0.229 to 0.270 | 0.131 | 0.130 | 0.130 | 0.110 to 0.155 |
| model T=0 (mode) | 0.606 | 0.229 | 0.333 | 0.309 to 0.354 | 0.802 | 0.099 | 0.177 | 0.141 to 0.220 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.333 | 0.314 | 0.432 | 0.402 |
| 12 | 0.303 | 0.303 | 0.430 | 0.428 |
| 24 | 0.271 | 0.270 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1303 | 0.628 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1769 | 0.853 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2504 | 0.790 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3325 | 1.049 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2915.2000 | 0.374 |
| funds_mae_12m | 5714.0800 | 36.8760 | 4280.7317 | 0.252 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 610.4250 | 0.051 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 948.3903 | 0.307 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 888.2240 | 0.047 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0629 | 0.522 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.2839 | 0.252 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3030 | 0.708 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3027 | 0.705 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 6681.9350 | 0.120 |
| funds_mae_24m | 7364.5720 | 66.5620 | 5229.5392 | 0.293 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 732.1380 | -0.046 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 1054.4108 | -0.088 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 1046.1735 | -0.405 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1361 | 0.201 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.4442 | 0.347 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2701 | 0.663 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2715 | 0.666 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.338 | 1.175 | 0.204 | 0.012 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 |
| 12 | 0.821 | 0.723 | 0.146 | 0.284 / 0.003 / 0.378 | 0.063 / 0.026 / 0.103 |
| 24 | 0.897 | 0.791 | 0.167 | 0.444 / 0.005 / 0.678 | 0.136 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 5229.5 | 4956.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 732.1 | 679.4 | 142.8 | 706.1 |
| com_valve | 1054.4 | 957.7 | 508.6 | 1010.2 |
| ind_valve | 1046.2 | 966.7 | 416.9 | 864.8 |
| pop | 6681.9 | 6165.3 | 1754.6 | 7353.4 |
| res_pop | 131.6 | 117.0 | 39.0 | 139.9 |
| com_pop | 13.9 | 11.8 | 4.4 | 12.8 |
| ind_pop | 19.9 | 18.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 110.7 | 87.2 | 25.2 | 89.6 |
| tax_fund | 782.4 | 549.0 | 51.5 | 1444.5 |
| road_spend | 214.9 | 137.7 | 8.2 | 647.3 |
| fire_spend | 199.8 | 133.6 | 0.8 | 474.7 |
| police_spend | 277.1 | 205.6 | 6.0 | 604.1 |
| powered_zones | 8.4 | 8.2 | 0.7 | 8.6 |
| unpowered_zones | 8.2 | 8.0 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.3 | 0.0 | 0.3 |
| road_total | 78.0 | 50.1 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 1.236 | 0.838 |
| traffic | 1.266 | 0.772 |
| pollution | 1.799 | 0.706 |
| land_value | 1.026 | 0.325 |
| crime | 1.243 | 0.566 |
| rate_of_growth | 1.239 | 0.819 |
| fire_coverage | 1.202 | 0.123 |
| police_coverage | 1.110 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -264.11 |
| tile_cat | -45.37 |
| flags | -22.92 |
| power | -6.49 |
| half | -3094.51 |
| eighth | -59.57 |
| scalars | -25.22 |
| sc_funds | -2.18 |
| sc_res_valve | -2.16 |
| sc_com_valve | -4.30 |
| sc_ind_valve | -4.13 |
| sc_res_pop | -3.41 |
| sc_com_pop | -1.32 |
| sc_ind_pop | -1.45 |
| sc_score | -0.54 |
| sc_tax_fund | -0.61 |
| sc_road_spend | -0.45 |
| sc_fire_spend | -0.21 |
| sc_police_spend | -0.23 |
| sc_powered_zones | -0.19 |
| sc_unpowered_zones | -0.36 |
| sc_coal_plants | -0.05 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.62 |
| n_changed | 99.43 |
| kl | 2.73 |
| elbo | -3520.92 |
| derived_viol | 0.00 |

## pilot_50m_samples_000600064

samples consumed: 600064

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.258 | 0.261 | 0.259 | 0.239 to 0.279 | 0.140 | 0.134 | 0.137 | 0.117 to 0.161 |
| model T=0 (mode) | 0.598 | 0.234 | 0.336 | 0.313 to 0.358 | 0.794 | 0.098 | 0.175 | 0.138 to 0.218 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.338 | 0.334 | 0.432 | 0.402 |
| 12 | 0.316 | 0.317 | 0.430 | 0.428 |
| 24 | 0.284 | 0.283 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1371 | 0.661 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1750 | 0.844 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2595 | 0.818 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3364 | 1.061 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2769.9850 | 0.422 |
| funds_mae_12m | 5714.0800 | 36.8760 | 3909.5712 | 0.318 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 507.9680 | 0.245 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 883.8715 | 0.382 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 832.2877 | 0.132 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0594 | 0.568 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.2708 | 0.286 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3168 | 0.741 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3155 | 0.734 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 6176.7300 | 0.210 |
| funds_mae_24m | 7364.5720 | 66.5620 | 4464.5360 | 0.397 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 547.3715 | 0.282 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 917.3300 | 0.185 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 984.0650 | -0.266 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1243 | 0.302 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.3816 | 0.440 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2833 | 0.695 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2838 | 0.696 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.308 | 1.178 | 0.204 | 0.004 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 |
| 12 | 0.793 | 0.705 | 0.146 | 0.271 / 0.003 / 0.378 | 0.059 / 0.026 / 0.103 |
| 24 | 0.859 | 0.760 | 0.167 | 0.382 / 0.005 / 0.678 | 0.124 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 4464.5 | 4056.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 547.4 | 486.7 | 142.8 | 706.1 |
| com_valve | 917.3 | 829.1 | 508.6 | 1010.2 |
| ind_valve | 984.1 | 897.3 | 416.9 | 864.8 |
| pop | 6176.7 | 5757.8 | 1754.6 | 7353.4 |
| res_pop | 118.6 | 105.3 | 39.0 | 139.9 |
| com_pop | 12.5 | 10.7 | 4.4 | 12.8 |
| ind_pop | 19.2 | 17.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 97.5 | 76.6 | 25.2 | 89.6 |
| tax_fund | 746.4 | 512.7 | 51.5 | 1444.5 |
| road_spend | 180.6 | 117.8 | 8.2 | 647.3 |
| fire_spend | 167.8 | 111.9 | 0.8 | 474.7 |
| police_spend | 233.8 | 170.3 | 6.0 | 604.1 |
| powered_zones | 8.8 | 8.4 | 0.7 | 8.6 |
| unpowered_zones | 8.0 | 7.8 | 0.6 | 7.0 |
| coal_plants | 0.6 | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.4 | 0.0 | 0.3 |
| road_total | 102.7 | 82.0 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 1.198 | 0.838 |
| traffic | 1.179 | 0.772 |
| pollution | 1.702 | 0.706 |
| land_value | 0.903 | 0.325 |
| crime | 1.274 | 0.566 |
| rate_of_growth | 1.202 | 0.819 |
| fire_coverage | 1.221 | 0.123 |
| police_coverage | 1.169 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -258.68 |
| tile_cat | -40.65 |
| flags | -20.39 |
| power | -5.41 |
| half | -2954.28 |
| eighth | -55.91 |
| scalars | -23.59 |
| sc_funds | -1.95 |
| sc_res_valve | -2.04 |
| sc_com_valve | -4.11 |
| sc_ind_valve | -4.01 |
| sc_res_pop | -3.36 |
| sc_com_pop | -1.01 |
| sc_ind_pop | -1.07 |
| sc_score | -0.53 |
| sc_tax_fund | -0.60 |
| sc_road_spend | -0.44 |
| sc_fire_spend | -0.21 |
| sc_police_spend | -0.22 |
| sc_powered_zones | -0.14 |
| sc_unpowered_zones | -0.27 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.04 |
| sc_road_total | -3.56 |
| n_changed | 99.43 |
| kl | 4.90 |
| elbo | -3363.81 |
| derived_viol | 0.00 |
