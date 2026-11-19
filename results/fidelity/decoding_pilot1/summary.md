## pilot_50m_samples_000600064_dec-a (decoding a: T=1.0, overlays sample)

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

## pilot_50m_samples_000600064_dec-b (decoding b: T=1.0, overlays mean)

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
| 1 | 0.337 | 0.335 | 0.432 | 0.402 |
| 12 | 0.314 | 0.316 | 0.430 | 0.428 |
| 24 | 0.282 | 0.283 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1371 | 0.661 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1750 | 0.844 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2595 | 0.818 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3364 | 1.061 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2890.1150 | 0.382 |
| funds_mae_12m | 5714.0800 | 36.8760 | 4042.2370 | 0.294 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 502.4555 | 0.255 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 914.9832 | 0.346 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 863.7205 | 0.084 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0644 | 0.503 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.2894 | 0.237 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3160 | 0.739 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3135 | 0.730 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 6299.4150 | 0.188 |
| funds_mae_24m | 7364.5720 | 66.5620 | 4637.0697 | 0.374 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 585.8940 | 0.213 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 872.7875 | 0.274 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 931.2005 | -0.148 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1230 | 0.313 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.4262 | 0.374 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2831 | 0.695 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2822 | 0.692 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.301 | 1.177 | 0.204 | 0.004 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 |
| 12 | 0.800 | 0.716 | 0.146 | 0.289 / 0.003 / 0.378 | 0.064 / 0.026 / 0.103 |
| 24 | 0.859 | 0.764 | 0.167 | 0.426 / 0.005 / 0.678 | 0.123 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 4637.1 | 4202.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 585.9 | 515.2 | 142.8 | 706.1 |
| com_valve | 872.8 | 798.1 | 508.6 | 1010.2 |
| ind_valve | 931.2 | 852.1 | 416.9 | 864.8 |
| pop | 6299.4 | 5878.1 | 1754.6 | 7353.4 |
| res_pop | 120.6 | 105.7 | 39.0 | 139.9 |
| com_pop | 12.6 | 10.9 | 4.4 | 12.8 |
| ind_pop | 19.8 | 18.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 98.9 | 79.5 | 25.2 | 89.6 |
| tax_fund | 774.3 | 501.3 | 51.5 | 1444.5 |
| road_spend | 182.4 | 122.0 | 8.2 | 647.3 |
| fire_spend | 158.4 | 103.1 | 0.8 | 474.7 |
| police_spend | 228.4 | 159.8 | 6.0 | 604.1 |
| powered_zones | 8.7 | 8.4 | 0.7 | 8.6 |
| unpowered_zones | 7.9 | 7.7 | 0.6 | 7.0 |
| coal_plants | 0.6 | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.4 | 0.0 | 0.3 |
| road_total | 95.7 | 82.0 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 1.016 | 0.838 |
| traffic | 0.945 | 0.772 |
| pollution | 1.130 | 0.706 |
| land_value | 0.735 | 0.325 |
| crime | 1.027 | 0.566 |
| rate_of_growth | 0.999 | 0.819 |
| fire_coverage | 1.123 | 0.123 |
| police_coverage | 1.166 | 0.114 |

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

## pilot_50m_samples_000600064_dec-c (decoding c: T=0.0, overlays sample)

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
| 1 | 0.417 | 0.472 | 0.432 | 0.402 |
| 12 | 0.353 | 0.360 | 0.430 | 0.428 |
| 24 | 0.309 | 0.311 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1371 | 0.661 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1750 | 0.844 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2595 | 0.818 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3364 | 1.061 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2912.8000 | 0.375 |
| funds_mae_12m | 5714.0800 | 36.8760 | 4271.8740 | 0.254 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 507.3600 | 0.246 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 943.4460 | 0.313 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 704.5780 | 0.325 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0711 | 0.416 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.2065 | 0.457 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3601 | 0.842 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3531 | 0.822 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 6586.2400 | 0.137 |
| funds_mae_24m | 7364.5720 | 66.5620 | 5220.5640 | 0.294 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 626.7260 | 0.141 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 1396.8760 | -0.771 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 1104.9800 | -0.536 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1396 | 0.171 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.4102 | 0.398 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3113 | 0.764 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3088 | 0.757 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 0.684 | 0.684 | 0.204 | 0.001 / 0.000 / 0.017 | 0.006 / 0.006 / 0.007 |
| 12 | 0.759 | 0.759 | 0.146 | 0.207 / 0.003 / 0.378 | 0.071 / 0.026 / 0.103 |
| 24 | 0.907 | 0.907 | 0.167 | 0.410 / 0.005 / 0.678 | 0.140 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 5220.6 | 5220.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 626.7 | 626.7 | 142.8 | 706.1 |
| com_valve | 1396.9 | 1396.9 | 508.6 | 1010.2 |
| ind_valve | 1105.0 | 1105.0 | 416.9 | 864.8 |
| pop | 6586.2 | 6586.2 | 1754.6 | 7353.4 |
| res_pop | 152.9 | 152.9 | 39.0 | 139.9 |
| com_pop | 19.5 | 19.5 | 4.4 | 12.8 |
| ind_pop | 18.5 | 18.5 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 97.5 | 97.5 | 25.2 | 89.6 |
| tax_fund | 484.2 | 484.2 | 51.5 | 1444.5 |
| road_spend | 130.7 | 130.7 | 8.2 | 647.3 |
| fire_spend | 85.3 | 85.3 | 0.8 | 474.7 |
| police_spend | 152.6 | 152.6 | 6.0 | 604.1 |
| powered_zones | 8.6 | 8.6 | 0.7 | 8.6 |
| unpowered_zones | 6.3 | 6.3 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.5 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.3 | 0.0 | 0.3 |
| road_total | 142.8 | 142.8 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 1.050 | 0.838 |
| traffic | 0.916 | 0.772 |
| pollution | 1.809 | 0.706 |
| land_value | 0.726 | 0.325 |
| crime | 0.958 | 0.566 |
| rate_of_growth | 1.069 | 0.819 |
| fire_coverage | 1.000 | 0.123 |
| police_coverage | 0.996 | 0.114 |

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
