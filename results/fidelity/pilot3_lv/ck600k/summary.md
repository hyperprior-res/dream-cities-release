## pilot3_lv_samples_000600064_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 600064

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.266 | 0.265 | 0.266 | 0.243 to 0.286 | 0.153 | 0.148 | 0.151 | 0.125 to 0.180 |
| model T=0 (mode) | 0.615 | 0.239 | 0.344 | 0.319 to 0.368 | 0.831 | 0.112 | 0.197 | 0.156 to 0.244 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.343 | 0.339 | 0.432 | 0.402 |
| 12 | 0.337 | 0.341 | 0.430 | 0.428 |
| 24 | 0.308 | 0.311 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1508 | 0.727 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1970 | 0.950 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2655 | 0.837 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3440 | 1.085 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2544.1600 | 0.497 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1103.5050 | 0.812 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 482.9360 | 0.292 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 863.4285 | 0.406 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 744.8033 | 0.264 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0574 | 0.594 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0724 | 0.814 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3412 | 0.798 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3365 | 0.783 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5073.3350 | 0.407 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1294.9752 | 0.832 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 601.7675 | 0.185 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 896.1275 | 0.227 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 907.6545 | -0.096 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1000 | 0.509 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1067 | 0.849 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3112 | 0.764 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3083 | 0.756 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 0.840 | 0.682 | 0.204 | 0.008 / 0.000 / 0.017 | 0.007 / 0.006 / 0.007 |
| 12 | 0.593 | 0.482 | 0.146 | 0.072 / 0.003 / 0.378 | 0.057 / 0.026 / 0.103 |
| 24 | 0.658 | 0.534 | 0.167 | 0.107 / 0.005 / 0.678 | 0.100 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 1295.0 | 970.3 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 601.8 | 555.6 | 142.8 | 706.1 |
| com_valve | 896.1 | 814.0 | 508.6 | 1010.2 |
| ind_valve | 907.7 | 815.8 | 416.9 | 864.8 |
| pop | 5073.3 | 4834.3 | 1754.6 | 7353.4 |
| res_pop | 93.7 | 85.3 | 39.0 | 139.9 |
| com_pop | 10.3 | 9.6 | 4.4 | 12.8 |
| ind_pop | 15.4 | 14.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 107.8 | 84.4 | 25.2 | 89.6 |
| tax_fund | 704.8 | 422.9 | 51.5 | 1444.5 |
| road_spend | 210.6 | 134.0 | 8.2 | 647.3 |
| fire_spend | 262.8 | 125.7 | 0.8 | 474.7 |
| police_spend | 336.9 | 176.0 | 6.0 | 604.1 |
| powered_zones | 4.2 | 3.4 | 0.7 | 8.6 |
| unpowered_zones | 3.7 | 3.3 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.2 | 0.0 | 0.3 |
| road_total | 44.7 | 22.8 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.940 | 0.838 |
| traffic | 0.926 | 0.772 |
| pollution | 1.173 | 0.706 |
| land_value | 0.688 | 0.325 |
| crime | 0.938 | 0.566 |
| rate_of_growth | 0.902 | 0.819 |
| fire_coverage | 1.154 | 0.123 |
| police_coverage | 0.998 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -261.63 |
| tile_cat | -41.76 |
| flags | -21.74 |
| power | -5.72 |
| half | -2979.88 |
| eighth | -56.20 |
| scalars | -20.68 |
| sc_funds | -1.85 |
| sc_res_valve | -2.12 |
| sc_com_valve | -4.26 |
| sc_ind_valve | -3.96 |
| sc_res_pop | -2.01 |
| sc_com_pop | -0.38 |
| sc_ind_pop | -0.36 |
| sc_score | -0.52 |
| sc_tax_fund | -0.61 |
| sc_road_spend | -0.48 |
| sc_fire_spend | -0.22 |
| sc_police_spend | -0.23 |
| sc_powered_zones | -0.11 |
| sc_unpowered_zones | -0.09 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.45 |
| n_changed | 99.43 |
| kl | 3.04 |
| elbo | -3390.66 |
| derived_viol | 0.00 |
