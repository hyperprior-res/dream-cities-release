## pilot3_dc_samples_000600064_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 600064

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.262 | 0.263 | 0.262 | 0.240 to 0.283 | 0.148 | 0.143 | 0.146 | 0.120 to 0.175 |
| model T=0 (mode) | 0.613 | 0.237 | 0.341 | 0.316 to 0.364 | 0.836 | 0.107 | 0.190 | 0.149 to 0.238 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.337 | 0.340 | 0.432 | 0.402 |
| 12 | 0.326 | 0.332 | 0.430 | 0.428 |
| 24 | 0.299 | 0.303 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1458 | 0.703 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1904 | 0.918 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2623 | 0.827 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3415 | 1.077 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2788.3950 | 0.416 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1687.7217 | 0.709 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 481.7335 | 0.295 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 841.7245 | 0.432 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 718.6078 | 0.304 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0650 | 0.495 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0991 | 0.743 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3318 | 0.776 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3259 | 0.758 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 5382.0000 | 0.352 |
| funds_mae_24m | 7364.5720 | 66.5620 | 2040.7628 | 0.729 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 584.6712 | 0.216 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 884.7750 | 0.250 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 826.9997 | 0.084 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.1098 | 0.426 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1559 | 0.775 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3033 | 0.744 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2993 | 0.734 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 0.831 | 0.668 | 0.204 | 0.008 / 0.000 / 0.017 | 0.007 / 0.006 / 0.007 |
| 12 | 0.636 | 0.524 | 0.146 | 0.099 / 0.003 / 0.378 | 0.065 / 0.026 / 0.103 |
| 24 | 0.687 | 0.565 | 0.167 | 0.156 / 0.005 / 0.678 | 0.110 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 2040.8 | 1799.6 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 584.7 | 531.1 | 142.8 | 706.1 |
| com_valve | 884.8 | 787.4 | 508.6 | 1010.2 |
| ind_valve | 827.0 | 733.6 | 416.9 | 864.8 |
| pop | 5382.0 | 5106.3 | 1754.6 | 7353.4 |
| res_pop | 109.4 | 96.3 | 39.0 | 139.9 |
| com_pop | 10.2 | 9.5 | 4.4 | 12.8 |
| ind_pop | 16.0 | 15.4 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 100.7 | 77.2 | 25.2 | 89.6 |
| tax_fund | 732.2 | 461.9 | 51.5 | 1444.5 |
| road_spend | 227.2 | 148.1 | 8.2 | 647.3 |
| fire_spend | 273.5 | 135.0 | 0.8 | 474.7 |
| police_spend | 338.0 | 178.9 | 6.0 | 604.1 |
| powered_zones | 5.2 | 4.5 | 0.7 | 8.6 |
| unpowered_zones | 4.3 | 3.9 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.3 | 0.3 | 0.0 | 0.3 |
| road_total | 46.9 | 27.7 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.963 | 0.838 |
| traffic | 0.969 | 0.772 |
| pollution | 1.103 | 0.706 |
| land_value | 0.683 | 0.325 |
| crime | 0.942 | 0.566 |
| rate_of_growth | 0.926 | 0.819 |
| fire_coverage | 1.100 | 0.123 |
| police_coverage | 1.026 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -259.95 |
| tile_cat | -41.61 |
| flags | -20.95 |
| power | -5.43 |
| half | -2972.78 |
| eighth | -56.24 |
| scalars | -20.61 |
| sc_funds | -1.84 |
| sc_res_valve | -2.11 |
| sc_com_valve | -4.28 |
| sc_ind_valve | -4.01 |
| sc_res_pop | -2.01 |
| sc_com_pop | -0.28 |
| sc_ind_pop | -0.35 |
| sc_score | -0.52 |
| sc_tax_fund | -0.61 |
| sc_road_spend | -0.48 |
| sc_fire_spend | -0.22 |
| sc_police_spend | -0.23 |
| sc_powered_zones | -0.10 |
| sc_unpowered_zones | -0.08 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.46 |
| n_changed | 99.43 |
| kl | 3.14 |
| elbo | -3380.71 |
| derived_viol | 0.00 |
