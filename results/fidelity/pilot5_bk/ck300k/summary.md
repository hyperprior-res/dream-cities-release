## pilot5_bk_samples_000300032_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 300032

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.253 | 0.256 | 0.254 | 0.233 to 0.274 | 0.140 | 0.138 | 0.139 | 0.117 to 0.165 |
| model T=0 (mode) | 0.612 | 0.233 | 0.338 | 0.313 to 0.360 | 0.831 | 0.106 | 0.188 | 0.148 to 0.232 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.344 | 0.321 | 0.432 | 0.402 |
| 12 | 0.328 | 0.330 | 0.430 | 0.428 |
| 24 | 0.303 | 0.305 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1391 | 0.670 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.1883 | 0.908 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2544 | 0.802 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3376 | 1.065 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1357.5850 | 0.892 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1248.0670 | 0.787 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 217.7392 | 0.794 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 532.1610 | 0.795 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 299.1755 | 0.938 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0311 | 0.933 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0692 | 0.823 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3302 | 0.772 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3277 | 0.763 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 2468.0650 | 0.873 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1432.3818 | 0.813 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 363.8958 | 0.608 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 614.5398 | 0.789 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 507.3843 | 0.798 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0547 | 0.895 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0929 | 0.869 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3049 | 0.748 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3033 | 0.744 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 0.686 | 0.547 | 0.204 | 0.008 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 |
| 12 | 0.526 | 0.373 | 0.146 | 0.069 / 0.003 / 0.378 | 0.031 / 0.026 / 0.103 |
| 24 | 0.551 | 0.402 | 0.167 | 0.093 / 0.005 / 0.678 | 0.055 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 1432.4 | 1167.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 363.9 | 331.1 | 142.8 | 706.1 |
| com_valve | 614.5 | 530.2 | 508.6 | 1010.2 |
| ind_valve | 507.4 | 423.1 | 416.9 | 864.8 |
| pop | 2468.1 | 2137.7 | 1754.6 | 7353.4 |
| res_pop | 62.4 | 53.5 | 39.0 | 139.9 |
| com_pop | 6.5 | 5.9 | 4.4 | 12.8 |
| ind_pop | 7.7 | 6.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 46.4 | 39.2 | 25.2 | 89.6 |
| tax_fund | 124.7 | 104.5 | 51.5 | 1444.5 |
| road_spend | 86.3 | 74.3 | 8.2 | 647.3 |
| fire_spend | 40.5 | 31.0 | 0.8 | 474.7 |
| police_spend | 66.3 | 48.0 | 6.0 | 604.1 |
| powered_zones | 7.0 | 4.6 | 0.7 | 8.6 |
| unpowered_zones | 5.3 | 4.3 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.4 | 0.0 | 0.3 |
| road_total | 59.0 | 31.0 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.854 | 0.838 |
| traffic | 0.914 | 0.772 |
| pollution | 1.087 | 0.706 |
| land_value | 0.681 | 0.325 |
| crime | 0.831 | 0.566 |
| rate_of_growth | 0.762 | 0.819 |
| fire_coverage | 1.369 | 0.123 |
| police_coverage | 0.984 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -264.57 |
| tile_cat | -45.66 |
| flags | -23.07 |
| power | -6.50 |
| half | -3099.01 |
| eighth | -48.49 |
| scalars_s2 | -7.81 |
| build_cost | -1.52 |
| scalars | -15.55 |
| ledger | -13.43 |
| bk | -21.17 |
| sc_res_pop | -2.56 |
| sc_com_pop | -0.58 |
| sc_ind_pop | -0.60 |
| sc_powered_zones | -0.21 |
| sc_unpowered_zones | -0.28 |
| sc_coal_plants | -0.04 |
| sc_nuclear_plants | -0.04 |
| sc_road_total | -3.51 |
| sc_res_valve | -1.08 |
| sc_com_valve | -2.18 |
| sc_ind_valve | -1.74 |
| sc_score | -0.39 |
| sc_funds | -1.10 |
| sc_tax_fund | -0.45 |
| sc_road_spend | -0.47 |
| sc_fire_spend | -0.17 |
| sc_police_spend | -0.16 |
| lg_sprite_cycle | -0.80 |
| lg_total_pop | -1.55 |
| lg_res_hist0 | -0.59 |
| lg_res_hist1 | -0.43 |
| lg_com_hist0 | -0.10 |
| lg_com_hist1 | -0.14 |
| lg_ind_hist0 | -0.18 |
| lg_ind_hist1 | -0.26 |
| lg_res_cap | -0.01 |
| lg_com_cap | -0.00 |
| lg_ind_cap | -0.00 |
| lg_need_hospital | -0.04 |
| lg_need_church | -0.03 |
| lg_road_fund | -0.51 |
| lg_police_fund | -0.14 |
| lg_fire_fund | -0.14 |
| lg_auto_budget | -0.00 |
| lg_fire_pop | -0.05 |
| lg_city_center_x | -0.13 |
| lg_city_center_y | -0.12 |
| lg_pollution_max_x | -2.82 |
| lg_pollution_max_y | -3.06 |
| lg_flood_count | -0.00 |
| lg_abs_dist | -2.33 |
| terrain | -9.86 |
| com_rate | -13.77 |
| n_changed | 99.43 |
| kl | 2.36 |
| elbo | -3543.81 |
| derived_viol | 0.00 |
