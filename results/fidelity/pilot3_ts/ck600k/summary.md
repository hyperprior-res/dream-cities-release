## pilot3_ts_samples_000600064_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 600064

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.264 | 0.267 | 0.265 | 0.243 to 0.286 | 0.150 | 0.148 | 0.149 | 0.125 to 0.178 |
| model T=0 (mode) | 0.610 | 0.242 | 0.347 | 0.322 to 0.369 | 0.823 | 0.111 | 0.195 | 0.155 to 0.240 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.349 | 0.345 | 0.432 | 0.402 |
| 12 | 0.332 | 0.337 | 0.430 | 0.428 |
| 24 | 0.302 | 0.305 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1490 | 0.718 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1954 | 0.942 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2655 | 0.837 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3468 | 1.094 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2950.3050 | 0.362 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1138.4462 | 0.806 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 531.7428 | 0.200 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 904.4505 | 0.358 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 811.2540 | 0.164 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0660 | 0.482 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0727 | 0.814 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3366 | 0.787 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3320 | 0.773 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5657.6650 | 0.303 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1409.1128 | 0.816 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 661.6640 | 0.079 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 981.4140 | 0.057 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 942.3755 | -0.173 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1097 | 0.426 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1210 | 0.827 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3050 | 0.748 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3022 | 0.741 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 0.845 | 0.665 | 0.204 | 0.009 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 |
| 12 | 0.627 | 0.511 | 0.146 | 0.073 / 0.003 / 0.378 | 0.066 / 0.026 / 0.103 |
| 24 | 0.693 | 0.562 | 0.167 | 0.121 / 0.005 / 0.678 | 0.110 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 1409.1 | 1116.5 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 661.7 | 608.7 | 142.8 | 706.1 |
| com_valve | 981.4 | 876.6 | 508.6 | 1010.2 |
| ind_valve | 942.4 | 833.6 | 416.9 | 864.8 |
| pop | 5657.7 | 5372.2 | 1754.6 | 7353.4 |
| res_pop | 104.4 | 94.2 | 39.0 | 139.9 |
| com_pop | 10.7 | 9.7 | 4.4 | 12.8 |
| ind_pop | 18.1 | 17.0 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 110.9 | 87.0 | 25.2 | 89.6 |
| tax_fund | 684.0 | 442.6 | 51.5 | 1444.5 |
| road_spend | 207.5 | 125.5 | 8.2 | 647.3 |
| fire_spend | 255.5 | 117.0 | 0.8 | 474.7 |
| police_spend | 323.8 | 164.6 | 6.0 | 604.1 |
| powered_zones | 4.4 | 3.6 | 0.7 | 8.6 |
| unpowered_zones | 4.0 | 3.6 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.2 | 0.0 | 0.3 |
| road_total | 45.7 | 24.4 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.985 | 0.838 |
| traffic | 0.933 | 0.772 |
| pollution | 1.143 | 0.706 |
| land_value | 0.681 | 0.325 |
| crime | 0.990 | 0.566 |
| rate_of_growth | 0.958 | 0.819 |
| fire_coverage | 1.219 | 0.123 |
| police_coverage | 1.041 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -260.67 |
| tile_cat | -41.22 |
| flags | -23.12 |
| power | -5.65 |
| half | -2987.53 |
| eighth | -56.46 |
| scalars | -20.76 |
| sc_funds | -1.86 |
| sc_res_valve | -2.17 |
| sc_com_valve | -4.35 |
| sc_ind_valve | -3.99 |
| sc_res_pop | -1.95 |
| sc_com_pop | -0.33 |
| sc_ind_pop | -0.34 |
| sc_score | -0.53 |
| sc_tax_fund | -0.61 |
| sc_road_spend | -0.48 |
| sc_fire_spend | -0.22 |
| sc_police_spend | -0.23 |
| sc_powered_zones | -0.11 |
| sc_unpowered_zones | -0.09 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.47 |
| n_changed | 99.43 |
| kl | 2.94 |
| elbo | -3398.34 |
| derived_viol | 0.00 |
