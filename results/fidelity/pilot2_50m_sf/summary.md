## pilot2_50m_sf_samples_000150016_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 150016

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.204 | 0.282 | 0.237 | 0.218 to 0.254 | 0.108 | 0.174 | 0.133 | 0.116 to 0.153 |
| model T=0 (mode) | 0.579 | 0.260 | 0.359 | 0.335 to 0.379 | 0.698 | 0.130 | 0.219 | 0.179 to 0.261 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.335 | 0.310 | 0.432 | 0.402 |
| 12 | 0.296 | 0.296 | 0.430 | 0.428 |
| 24 | 0.257 | 0.256 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1335 | 0.644 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.2187 | 1.054 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2366 | 0.746 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3588 | 1.132 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 3208.7900 | 0.276 |
| funds_mae_12m | 5714.0800 | 36.8760 | 3945.9320 | 0.311 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 595.9443 | 0.078 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 989.0285 | 0.259 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 905.3362 | 0.021 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0733 | 0.388 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.3697 | 0.023 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.2957 | 0.691 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.2960 | 0.689 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 6517.2000 | 0.149 |
| funds_mae_24m | 7364.5720 | 66.5620 | 4201.5685 | 0.433 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 796.3022 | -0.160 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 1032.3550 | -0.044 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 960.9697 | -0.215 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1334 | 0.224 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.4836 | 0.288 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2560 | 0.628 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2569 | 0.630 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 2.370 | 2.099 | 0.204 | 0.008 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 |
| 12 | 0.921 | 0.745 | 0.146 | 0.370 / 0.003 / 0.378 | 0.073 / 0.026 / 0.103 |
| 24 | 0.997 | 0.804 | 0.167 | 0.484 / 0.005 / 0.678 | 0.133 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 4201.6 | 3299.1 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 796.3 | 703.7 | 142.8 | 706.1 |
| com_valve | 1032.4 | 921.4 | 508.6 | 1010.2 |
| ind_valve | 961.0 | 825.8 | 416.9 | 864.8 |
| pop | 6517.2 | 5901.4 | 1754.6 | 7353.4 |
| res_pop | 134.9 | 110.7 | 39.0 | 139.9 |
| com_pop | 13.7 | 11.5 | 4.4 | 12.8 |
| ind_pop | 21.1 | 18.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 126.9 | 83.5 | 25.2 | 89.6 |
| tax_fund | 1035.2 | 570.4 | 51.5 | 1444.5 |
| road_spend | 365.3 | 257.5 | 8.2 | 647.3 |
| fire_spend | 233.7 | 132.5 | 0.8 | 474.7 |
| police_spend | 295.4 | 198.9 | 6.0 | 604.1 |
| powered_zones | 8.3 | 7.6 | 0.7 | 8.6 |
| unpowered_zones | 7.7 | 7.3 | 0.6 | 7.0 |
| coal_plants | 0.8 | 0.7 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.5 | 0.0 | 0.3 |
| road_total | 72.4 | 45.8 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 1.086 | 0.838 |
| traffic | 0.957 | 0.772 |
| pollution | 1.182 | 0.706 |
| land_value | 0.741 | 0.325 |
| crime | 0.947 | 0.566 |
| rate_of_growth | 1.123 | 0.819 |
| fire_coverage | 1.271 | 0.123 |
| police_coverage | 1.153 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -260.67 |
| tile_cat | -42.98 |
| flags | -20.89 |
| power | -5.29 |
| half | -3022.04 |
| eighth | -57.66 |
| scalars | -24.37 |
| sc_funds | -2.03 |
| sc_res_valve | -2.03 |
| sc_com_valve | -4.22 |
| sc_ind_valve | -4.03 |
| sc_res_pop | -3.40 |
| sc_com_pop | -0.89 |
| sc_ind_pop | -1.44 |
| sc_score | -0.59 |
| sc_tax_fund | -0.65 |
| sc_road_spend | -0.48 |
| sc_fire_spend | -0.22 |
| sc_police_spend | -0.24 |
| sc_powered_zones | -0.18 |
| sc_unpowered_zones | -0.27 |
| sc_coal_plants | -0.04 |
| sc_nuclear_plants | -0.04 |
| sc_road_total | -3.61 |
| n_changed | 99.43 |
| kl | 4.92 |
| elbo | -3438.83 |
| derived_viol | 0.00 |
