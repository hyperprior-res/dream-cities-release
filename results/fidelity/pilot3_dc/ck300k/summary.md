## pilot3_dc_samples_000300032_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 300032

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.250 | 0.255 | 0.253 | 0.231 to 0.273 | 0.137 | 0.137 | 0.137 | 0.114 to 0.163 |
| model T=0 (mode) | 0.616 | 0.231 | 0.336 | 0.311 to 0.358 | 0.829 | 0.106 | 0.188 | 0.148 to 0.232 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.334 | 0.318 | 0.432 | 0.402 |
| 12 | 0.308 | 0.309 | 0.430 | 0.428 |
| 24 | 0.279 | 0.279 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1370 | 0.660 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1876 | 0.904 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2528 | 0.797 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3358 | 1.059 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 3086.9450 | 0.317 |
| funds_mae_12m | 5714.0800 | 36.8760 | 2210.2503 | 0.617 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 671.3985 | -0.064 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 1022.5805 | 0.220 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 951.7932 | -0.049 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0710 | 0.418 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1600 | 0.581 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3087 | 0.722 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3080 | 0.717 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5968.4550 | 0.247 |
| funds_mae_24m | 7364.5720 | 66.5620 | 2651.9420 | 0.646 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 881.8837 | -0.312 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 1100.1495 | -0.179 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 1005.4963 | -0.314 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1175 | 0.360 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.2397 | 0.651 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2786 | 0.684 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2785 | 0.683 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.306 | 0.930 | 0.204 | 0.021 / 0.000 / 0.017 | 0.007 / 0.006 / 0.007 |
| 12 | 0.968 | 0.670 | 0.146 | 0.160 / 0.003 / 0.378 | 0.071 / 0.026 / 0.103 |
| 24 | 1.030 | 0.725 | 0.167 | 0.240 / 0.005 / 0.678 | 0.117 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 2651.9 | 2018.0 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 881.9 | 809.5 | 142.8 | 706.1 |
| com_valve | 1100.1 | 979.3 | 508.6 | 1010.2 |
| ind_valve | 1005.5 | 878.5 | 416.9 | 864.8 |
| pop | 5968.5 | 5473.6 | 1754.6 | 7353.4 |
| res_pop | 124.0 | 108.3 | 39.0 | 139.9 |
| com_pop | 11.8 | 10.2 | 4.4 | 12.8 |
| ind_pop | 17.4 | 16.1 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 153.7 | 89.6 | 25.2 | 89.6 |
| tax_fund | 1120.3 | 623.7 | 51.5 | 1444.5 |
| road_spend | 447.8 | 226.9 | 8.2 | 647.3 |
| fire_spend | 583.1 | 285.5 | 0.8 | 474.7 |
| police_spend | 744.7 | 373.8 | 6.0 | 604.1 |
| powered_zones | 7.6 | 5.0 | 0.7 | 8.6 |
| unpowered_zones | 5.9 | 4.7 | 0.6 | 7.0 |
| coal_plants | 0.6 | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.4 | 0.0 | 0.3 |
| road_total | 59.0 | 26.8 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 1.000 | 0.838 |
| traffic | 0.938 | 0.772 |
| pollution | 1.170 | 0.706 |
| land_value | 0.716 | 0.325 |
| crime | 0.912 | 0.566 |
| rate_of_growth | 0.968 | 0.819 |
| fire_coverage | 1.266 | 0.123 |
| police_coverage | 1.108 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -264.87 |
| tile_cat | -46.17 |
| flags | -23.89 |
| power | -6.75 |
| half | -3106.38 |
| eighth | -59.53 |
| scalars | -24.28 |
| sc_funds | -2.17 |
| sc_res_valve | -2.34 |
| sc_com_valve | -4.41 |
| sc_ind_valve | -4.29 |
| sc_res_pop | -2.80 |
| sc_com_pop | -0.89 |
| sc_ind_pop | -0.83 |
| sc_score | -0.58 |
| sc_tax_fund | -0.68 |
| sc_road_spend | -0.58 |
| sc_fire_spend | -0.25 |
| sc_police_spend | -0.26 |
| sc_powered_zones | -0.23 |
| sc_unpowered_zones | -0.31 |
| sc_coal_plants | -0.04 |
| sc_nuclear_plants | -0.04 |
| sc_road_total | -3.56 |
| n_changed | 99.43 |
| kl | 1.99 |
| elbo | -3533.87 |
| derived_viol | 0.00 |
