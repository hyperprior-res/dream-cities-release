## pilot4_ledger_samples_000300032_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 300032

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.251 | 0.256 | 0.253 | 0.232 to 0.273 | 0.137 | 0.138 | 0.137 | 0.115 to 0.163 |
| model T=0 (mode) | 0.612 | 0.232 | 0.337 | 0.312 to 0.359 | 0.825 | 0.105 | 0.187 | 0.147 to 0.230 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.343 | 0.321 | 0.432 | 0.402 |
| 12 | 0.315 | 0.317 | 0.430 | 0.428 |
| 24 | 0.287 | 0.288 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1373 | 0.662 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1868 | 0.900 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2533 | 0.799 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3366 | 1.061 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2409.7450 | 0.542 |
| funds_mae_12m | 5714.0800 | 36.8760 | 2625.3445 | 0.544 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 563.4512 | 0.140 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 837.4955 | 0.437 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 691.5400 | 0.345 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0487 | 0.705 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1934 | 0.492 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3174 | 0.742 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3149 | 0.733 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 4505.2950 | 0.509 |
| funds_mae_24m | 7364.5720 | 66.5620 | 3276.5080 | 0.560 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 722.8395 | -0.030 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 912.4188 | 0.195 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 872.0730 | -0.016 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0897 | 0.597 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.2789 | 0.593 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.2879 | 0.707 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.2868 | 0.703 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.459 | 1.062 | 0.204 | 0.027 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 |
| 12 | 0.972 | 0.647 | 0.146 | 0.193 / 0.003 / 0.378 | 0.049 / 0.026 / 0.103 |
| 24 | 1.035 | 0.704 | 0.167 | 0.279 / 0.005 / 0.678 | 0.090 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 3276.5 | 2505.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 722.8 | 663.3 | 142.8 | 706.1 |
| com_valve | 912.4 | 824.3 | 508.6 | 1010.2 |
| ind_valve | 872.1 | 782.5 | 416.9 | 864.8 |
| pop | 4505.3 | 3976.4 | 1754.6 | 7353.4 |
| res_pop | 115.9 | 103.5 | 39.0 | 139.9 |
| com_pop | 9.5 | 7.9 | 4.4 | 12.8 |
| ind_pop | 12.5 | 10.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 145.0 | 84.2 | 25.2 | 89.6 |
| tax_fund | 1075.8 | 565.7 | 51.5 | 1444.5 |
| road_spend | 450.8 | 188.1 | 8.2 | 647.3 |
| fire_spend | 633.7 | 316.1 | 0.8 | 474.7 |
| police_spend | 837.4 | 440.8 | 6.0 | 604.1 |
| powered_zones | 8.5 | 5.6 | 0.7 | 8.6 |
| unpowered_zones | 6.7 | 5.4 | 0.6 | 7.0 |
| coal_plants | 0.7 | 0.4 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.4 | 0.0 | 0.3 |
| road_total | 94.6 | 53.4 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.943 | 0.838 |
| traffic | 0.946 | 0.772 |
| pollution | 1.142 | 0.706 |
| land_value | 0.688 | 0.325 |
| crime | 0.888 | 0.566 |
| rate_of_growth | 0.883 | 0.819 |
| fire_coverage | 1.158 | 0.123 |
| police_coverage | 1.038 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -265.80 |
| tile_cat | -46.31 |
| flags | -23.42 |
| power | -6.55 |
| half | -3094.94 |
| eighth | -48.78 |
| scalars | -24.42 |
| sc_funds | -2.23 |
| sc_res_valve | -2.32 |
| sc_com_valve | -4.34 |
| sc_ind_valve | -4.20 |
| sc_res_pop | -2.83 |
| sc_com_pop | -0.95 |
| sc_ind_pop | -0.92 |
| sc_score | -0.57 |
| sc_tax_fund | -0.69 |
| sc_road_spend | -0.59 |
| sc_fire_spend | -0.26 |
| sc_police_spend | -0.27 |
| sc_powered_zones | -0.24 |
| sc_unpowered_zones | -0.34 |
| sc_coal_plants | -0.05 |
| sc_nuclear_plants | -0.05 |
| sc_road_total | -3.60 |
| ledger | -24.38 |
| lg_sprite_cycle | -4.83 |
| lg_total_pop | -2.00 |
| lg_res_hist0 | -1.23 |
| lg_res_hist1 | -1.61 |
| lg_com_hist0 | -1.02 |
| lg_com_hist1 | -1.43 |
| lg_ind_hist0 | -0.99 |
| lg_ind_hist1 | -1.54 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.01 |
| lg_ind_cap | -0.01 |
| lg_need_hospital | -0.22 |
| lg_need_church | -0.18 |
| lg_road_fund | -0.56 |
| lg_police_fund | -0.23 |
| lg_fire_fund | -0.21 |
| lg_auto_budget | -0.01 |
| lg_fire_pop | -0.14 |
| lg_city_center_x | -0.17 |
| lg_city_center_y | -0.16 |
| lg_pollution_max_x | -2.66 |
| lg_pollution_max_y | -2.54 |
| lg_flood_count | -0.04 |
| lg_abs_dist | -2.59 |
| terrain | -9.95 |
| com_rate | -13.14 |
| n_changed | 99.43 |
| kl | 1.93 |
| elbo | -3559.64 |
| derived_viol | 0.00 |
