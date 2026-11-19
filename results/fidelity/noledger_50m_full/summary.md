## noledger_50m_full_1step_samples_001200000_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 1200000

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.276 | 0.278 | 0.277 | 0.255 to 0.297 | 0.170 | 0.167 | 0.168 | 0.142 to 0.200 |
| model T=0 (mode) | 0.632 | 0.243 | 0.351 | 0.327 to 0.374 | 0.864 | 0.120 | 0.211 | 0.170 to 0.258 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.363 | 0.370 | 0.432 | 0.402 |
| 12 | 0.365 | 0.369 | 0.430 | 0.428 |
| 24 | 0.333 | 0.336 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1685 | 0.812 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.2115 | 1.019 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2768 | 0.873 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3514 | 1.108 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 2299.2000 | 0.579 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1989.4260 | 0.656 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 501.9418 | 0.256 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 696.9495 | 0.602 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 609.2135 | 0.469 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0499 | 0.690 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1705 | 0.553 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3692 | 0.863 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3646 | 0.849 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 4575.5650 | 0.496 |
| funds_mae_24m | 7364.5720 | 66.5620 | 2354.3685 | 0.687 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 537.2943 | 0.300 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 793.5745 | 0.432 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 805.0150 | 0.133 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0881 | 0.611 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.2267 | 0.670 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3364 | 0.825 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3331 | 0.817 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.456 | 0.863 | 0.204 | 0.027 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 |
| 12 | 0.981 | 0.583 | 0.146 | 0.171 / 0.003 / 0.378 | 0.050 / 0.026 / 0.103 |
| 24 | 1.055 | 0.672 | 0.167 | 0.227 / 0.005 / 0.678 | 0.088 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 2354.4 | 1389.7 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 537.3 | 444.4 | 142.8 | 706.1 |
| com_valve | 793.6 | 661.8 | 508.6 | 1010.2 |
| ind_valve | 805.0 | 645.7 | 416.9 | 864.8 |
| pop | 4575.6 | 3967.5 | 1754.6 | 7353.4 |
| res_pop | 101.9 | 83.4 | 39.0 | 139.9 |
| com_pop | 10.1 | 7.0 | 4.4 | 12.8 |
| ind_pop | 14.6 | 12.7 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 159.7 | 88.1 | 25.2 | 89.6 |
| tax_fund | 1296.0 | 693.9 | 51.5 | 1444.5 |
| road_spend | 538.5 | 244.8 | 8.2 | 647.3 |
| fire_spend | 832.3 | 530.9 | 0.8 | 474.7 |
| police_spend | 1001.8 | 623.5 | 6.0 | 604.1 |
| powered_zones | 9.3 | 5.1 | 0.7 | 8.6 |
| unpowered_zones | 6.6 | 5.2 | 0.6 | 7.0 |
| coal_plants | 0.7 | 0.3 | 0.0 | 0.5 |
| nuclear_plants | 0.7 | 0.4 | 0.0 | 0.3 |
| road_total | 62.7 | 27.5 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.921 | 0.838 |
| traffic | 0.876 | 0.772 |
| pollution | 1.067 | 0.706 |
| land_value | 0.592 | 0.325 |
| crime | 0.821 | 0.566 |
| rate_of_growth | 0.879 | 0.819 |
| fire_coverage | 1.422 | 0.123 |
| police_coverage | 1.108 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -249.18 |
| tile_cat | -36.01 |
| flags | -17.27 |
| power | -4.19 |
| half | -2684.43 |
| eighth | -53.67 |
| scalars | -23.07 |
| sc_funds | -2.21 |
| sc_res_valve | -2.08 |
| sc_com_valve | -3.89 |
| sc_ind_valve | -3.92 |
| sc_res_pop | -2.81 |
| sc_com_pop | -0.73 |
| sc_ind_pop | -0.80 |
| sc_score | -0.58 |
| sc_tax_fund | -0.69 |
| sc_road_spend | -0.59 |
| sc_fire_spend | -0.26 |
| sc_police_spend | -0.27 |
| sc_powered_zones | -0.24 |
| sc_unpowered_zones | -0.34 |
| sc_coal_plants | -0.04 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.58 |
| n_changed | 99.43 |
| kl | 4.71 |
| elbo | -3072.53 |
| derived_viol | 0.00 |

## noledger_50m_full_1step_samples_002400000_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 2400000

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.286 | 0.284 | 0.285 | 0.265 to 0.304 | 0.181 | 0.172 | 0.176 | 0.151 to 0.206 |
| model T=0 (mode) | 0.636 | 0.249 | 0.358 | 0.334 to 0.379 | 0.840 | 0.127 | 0.220 | 0.178 to 0.266 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.359 | 0.380 | 0.432 | 0.402 |
| 12 | 0.375 | 0.381 | 0.430 | 0.428 |
| 24 | 0.347 | 0.352 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1764 | 0.851 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.2203 | 1.062 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2850 | 0.899 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3579 | 1.129 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1882.8550 | 0.717 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1520.7485 | 0.739 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 300.6155 | 0.637 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 506.5865 | 0.825 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 394.3408 | 0.794 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0439 | 0.768 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1283 | 0.666 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3812 | 0.891 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3748 | 0.872 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3198.9050 | 0.742 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1770.5605 | 0.767 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 313.7610 | 0.697 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 547.3468 | 0.923 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 576.8035 | 0.643 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0680 | 0.782 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1746 | 0.748 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3521 | 0.864 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3474 | 0.852 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.174 | 0.659 | 0.204 | 0.022 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 |
| 12 | 0.797 | 0.455 | 0.146 | 0.128 / 0.003 / 0.378 | 0.044 / 0.026 / 0.103 |
| 24 | 0.836 | 0.503 | 0.167 | 0.175 / 0.005 / 0.678 | 0.068 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 1770.6 | 987.4 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 313.8 | 241.1 | 142.8 | 706.1 |
| com_valve | 547.3 | 445.6 | 508.6 | 1010.2 |
| ind_valve | 576.8 | 458.6 | 416.9 | 864.8 |
| pop | 3198.9 | 2706.3 | 1754.6 | 7353.4 |
| res_pop | 74.2 | 58.0 | 39.0 | 139.9 |
| com_pop | 7.2 | 5.2 | 4.4 | 12.8 |
| ind_pop | 10.9 | 9.2 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 134.7 | 71.4 | 25.2 | 89.6 |
| tax_fund | 1131.7 | 596.0 | 51.5 | 1444.5 |
| road_spend | 448.4 | 200.9 | 8.2 | 647.3 |
| fire_spend | 650.2 | 365.6 | 0.8 | 474.7 |
| police_spend | 847.3 | 485.1 | 6.0 | 604.1 |
| powered_zones | 8.3 | 4.7 | 0.7 | 8.6 |
| unpowered_zones | 5.8 | 4.4 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.6 | 0.3 | 0.0 | 0.3 |
| road_total | 58.4 | 25.6 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.848 | 0.838 |
| traffic | 0.857 | 0.772 |
| pollution | 1.028 | 0.706 |
| land_value | 0.564 | 0.325 |
| crime | 0.739 | 0.566 |
| rate_of_growth | 0.780 | 0.819 |
| fire_coverage | 1.291 | 0.123 |
| police_coverage | 0.946 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -231.96 |
| tile_cat | -32.62 |
| flags | -16.01 |
| power | -3.67 |
| half | -2529.73 |
| eighth | -49.78 |
| scalars | -21.39 |
| sc_funds | -2.11 |
| sc_res_valve | -1.92 |
| sc_com_valve | -3.55 |
| sc_ind_valve | -3.60 |
| sc_res_pop | -2.54 |
| sc_com_pop | -0.60 |
| sc_ind_pop | -0.66 |
| sc_score | -0.55 |
| sc_tax_fund | -0.67 |
| sc_road_spend | -0.57 |
| sc_fire_spend | -0.25 |
| sc_police_spend | -0.26 |
| sc_powered_zones | -0.21 |
| sc_unpowered_zones | -0.30 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.03 |
| sc_road_total | -3.53 |
| n_changed | 99.43 |
| kl | 8.81 |
| elbo | -2893.97 |
| derived_viol | 0.00 |

## noledger_50m_full_1step_samples_003000064_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 3000064

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.292 | 0.284 | 0.288 | 0.268 to 0.307 | 0.187 | 0.172 | 0.179 | 0.153 to 0.210 |
| model T=0 (mode) | 0.622 | 0.251 | 0.357 | 0.333 to 0.379 | 0.754 | 0.127 | 0.218 | 0.177 to 0.262 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.363 | 0.385 | 0.432 | 0.402 |
| 12 | 0.378 | 0.384 | 0.430 | 0.428 |
| 24 | 0.350 | 0.355 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1791 | 0.863 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.2180 | 1.051 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2880 | 0.908 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3574 | 1.127 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1821.0950 | 0.738 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1275.2225 | 0.782 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 281.8788 | 0.673 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 463.3143 | 0.875 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 363.0250 | 0.842 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0421 | 0.791 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.1068 | 0.723 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3843 | 0.899 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3778 | 0.879 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3193.5600 | 0.743 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1508.2240 | 0.802 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 311.3832 | 0.701 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 539.2315 | 0.939 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 564.5675 | 0.670 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0687 | 0.776 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1459 | 0.790 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3548 | 0.870 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3497 | 0.858 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 1.081 | 0.599 | 0.204 | 0.017 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 |
| 12 | 0.719 | 0.415 | 0.146 | 0.107 / 0.003 / 0.378 | 0.042 / 0.026 / 0.103 |
| 24 | 0.764 | 0.471 | 0.167 | 0.146 / 0.005 / 0.678 | 0.069 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 1508.2 | 873.3 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 311.4 | 259.2 | 142.8 | 706.1 |
| com_valve | 539.2 | 451.8 | 508.6 | 1010.2 |
| ind_valve | 564.6 | 452.9 | 416.9 | 864.8 |
| pop | 3193.6 | 2763.5 | 1754.6 | 7353.4 |
| res_pop | 73.1 | 58.9 | 39.0 | 139.9 |
| com_pop | 7.0 | 5.4 | 4.4 | 12.8 |
| ind_pop | 10.3 | 8.9 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 121.9 | 71.1 | 25.2 | 89.6 |
| tax_fund | 976.9 | 496.9 | 51.5 | 1444.5 |
| road_spend | 390.2 | 168.5 | 8.2 | 647.3 |
| fire_spend | 583.5 | 312.8 | 0.8 | 474.7 |
| police_spend | 711.1 | 378.2 | 6.0 | 604.1 |
| powered_zones | 7.4 | 4.4 | 0.7 | 8.6 |
| unpowered_zones | 5.3 | 3.9 | 0.6 | 7.0 |
| coal_plants | 0.5 | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.5 | 0.3 | 0.0 | 0.3 |
| road_total | 54.2 | 25.2 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.840 | 0.838 |
| traffic | 0.853 | 0.772 |
| pollution | 1.032 | 0.706 |
| land_value | 0.563 | 0.325 |
| crime | 0.731 | 0.566 |
| rate_of_growth | 0.773 | 0.819 |
| fire_coverage | 1.108 | 0.123 |
| police_coverage | 0.883 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -226.92 |
| tile_cat | -31.91 |
| flags | -15.42 |
| power | -3.29 |
| half | -2472.17 |
| eighth | -48.83 |
| scalars | -20.50 |
| sc_funds | -2.05 |
| sc_res_valve | -1.85 |
| sc_com_valve | -3.43 |
| sc_ind_valve | -3.50 |
| sc_res_pop | -2.38 |
| sc_com_pop | -0.48 |
| sc_ind_pop | -0.54 |
| sc_score | -0.54 |
| sc_tax_fund | -0.65 |
| sc_road_spend | -0.56 |
| sc_fire_spend | -0.24 |
| sc_police_spend | -0.25 |
| sc_powered_zones | -0.20 |
| sc_unpowered_zones | -0.27 |
| sc_coal_plants | -0.03 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.50 |
| n_changed | 99.43 |
| kl | 9.81 |
| elbo | -2828.84 |
| derived_viol | 0.00 |

## noledger_50m_full_1step_samples_003600000_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 3600000

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.293 | 0.286 | 0.289 | 0.269 to 0.308 | 0.188 | 0.174 | 0.180 | 0.154 to 0.210 |
| model T=0 (mode) | 0.608 | 0.253 | 0.358 | 0.335 to 0.378 | 0.670 | 0.130 | 0.218 | 0.178 to 0.260 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.367 | 0.387 | 0.432 | 0.402 |
| 12 | 0.380 | 0.387 | 0.430 | 0.428 |
| 24 | 0.352 | 0.357 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1804 | 0.870 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.2178 | 1.050 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2895 | 0.913 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3576 | 1.128 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1763.8200 | 0.757 |
| funds_mae_12m | 5714.0800 | 36.8760 | 1113.5847 | 0.810 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 271.8300 | 0.692 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 481.5690 | 0.854 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 358.7550 | 0.848 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0427 | 0.784 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0873 | 0.775 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3866 | 0.904 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3796 | 0.884 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3039.4700 | 0.771 |
| funds_mae_24m | 7364.5720 | 66.5620 | 1337.5580 | 0.826 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 284.4973 | 0.748 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 529.4842 | 0.958 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 577.4230 | 0.642 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0639 | 0.817 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.1302 | 0.814 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3575 | 0.877 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3524 | 0.864 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 0.937 | 0.578 | 0.204 | 0.014 / 0.000 / 0.017 | 0.009 / 0.006 / 0.007 |
| 12 | 0.624 | 0.369 | 0.146 | 0.087 / 0.003 / 0.378 | 0.043 / 0.026 / 0.103 |
| 24 | 0.660 | 0.409 | 0.167 | 0.130 / 0.005 / 0.678 | 0.064 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 1337.6 | 790.3 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 284.5 | 230.1 | 142.8 | 706.1 |
| com_valve | 529.5 | 445.7 | 508.6 | 1010.2 |
| ind_valve | 577.4 | 471.2 | 416.9 | 864.8 |
| pop | 3039.5 | 2640.8 | 1754.6 | 7353.4 |
| res_pop | 69.5 | 56.3 | 39.0 | 139.9 |
| com_pop | 6.8 | 5.6 | 4.4 | 12.8 |
| ind_pop | 10.1 | 8.8 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 94.3 | 53.6 | 25.2 | 89.6 |
| tax_fund | 878.1 | 450.7 | 51.5 | 1444.5 |
| road_spend | 338.1 | 150.8 | 8.2 | 647.3 |
| fire_spend | 462.4 | 228.9 | 0.8 | 474.7 |
| police_spend | 582.3 | 280.3 | 6.0 | 604.1 |
| powered_zones | 6.6 | 4.1 | 0.7 | 8.6 |
| unpowered_zones | 4.7 | 3.6 | 0.6 | 7.0 |
| coal_plants | 0.3 | 0.2 | 0.0 | 0.5 |
| nuclear_plants | 0.4 | 0.2 | 0.0 | 0.3 |
| road_total | 50.0 | 25.0 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.838 | 0.838 |
| traffic | 0.850 | 0.772 |
| pollution | 1.031 | 0.706 |
| land_value | 0.554 | 0.325 |
| crime | 0.723 | 0.566 |
| rate_of_growth | 0.770 | 0.819 |
| fire_coverage | 1.042 | 0.123 |
| police_coverage | 0.886 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -222.86 |
| tile_cat | -31.47 |
| flags | -15.28 |
| power | -3.04 |
| half | -2440.63 |
| eighth | -48.19 |
| scalars | -19.54 |
| sc_funds | -1.98 |
| sc_res_valve | -1.79 |
| sc_com_valve | -3.31 |
| sc_ind_valve | -3.39 |
| sc_res_pop | -2.17 |
| sc_com_pop | -0.38 |
| sc_ind_pop | -0.44 |
| sc_score | -0.51 |
| sc_tax_fund | -0.64 |
| sc_road_spend | -0.54 |
| sc_fire_spend | -0.24 |
| sc_police_spend | -0.25 |
| sc_powered_zones | -0.17 |
| sc_unpowered_zones | -0.23 |
| sc_coal_plants | -0.02 |
| sc_nuclear_plants | -0.02 |
| sc_road_total | -3.47 |
| n_changed | 99.43 |
| kl | 10.55 |
| elbo | -2791.55 |
| derived_viol | 0.00 |

## noledger_50m_full_1step_samples_004800000_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 4800000

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.296 | 0.286 | 0.291 | 0.271 to 0.309 | 0.190 | 0.174 | 0.181 | 0.155 to 0.211 |
| model T=0 (mode) | 0.560 | 0.255 | 0.350 | 0.328 to 0.369 | 0.487 | 0.133 | 0.209 | 0.173 to 0.247 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.369 | 0.392 | 0.432 | 0.402 |
| 12 | 0.379 | 0.387 | 0.430 | 0.428 |
| 24 | 0.354 | 0.360 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1814 | 0.875 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.2092 | 1.008 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2906 | 0.916 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3499 | 1.103 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1775.6050 | 0.753 |
| funds_mae_12m | 5714.0800 | 36.8760 | 771.5385 | 0.871 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 240.3168 | 0.751 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 472.9650 | 0.864 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 339.1250 | 0.878 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0428 | 0.782 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0604 | 0.846 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3873 | 0.906 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3787 | 0.881 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3013.2400 | 0.775 |
| funds_mae_24m | 7364.5720 | 66.5620 | 935.8590 | 0.881 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 271.5602 | 0.771 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 540.9025 | 0.936 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 587.3958 | 0.619 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0655 | 0.803 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0873 | 0.877 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3599 | 0.883 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3537 | 0.867 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 0.716 | 0.458 | 0.204 | 0.009 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 |
| 12 | 0.474 | 0.314 | 0.146 | 0.060 / 0.003 / 0.378 | 0.043 / 0.026 / 0.103 |
| 24 | 0.516 | 0.351 | 0.167 | 0.087 / 0.005 / 0.678 | 0.065 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 935.9 | 621.5 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 271.6 | 233.1 | 142.8 | 706.1 |
| com_valve | 540.9 | 470.9 | 508.6 | 1010.2 |
| ind_valve | 587.4 | 496.4 | 416.9 | 864.8 |
| pop | 3013.2 | 2702.9 | 1754.6 | 7353.4 |
| res_pop | 69.4 | 59.2 | 39.0 | 139.9 |
| com_pop | 6.4 | 5.5 | 4.4 | 12.8 |
| ind_pop | 9.7 | 8.6 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 68.6 | 43.1 | 25.2 | 89.6 |
| tax_fund | 676.9 | 406.2 | 51.5 | 1444.5 |
| road_spend | 232.0 | 109.5 | 8.2 | 647.3 |
| fire_spend | 305.8 | 137.3 | 0.8 | 474.7 |
| police_spend | 414.2 | 192.6 | 6.0 | 604.1 |
| powered_zones | 4.9 | 3.3 | 0.7 | 8.6 |
| unpowered_zones | 3.8 | 3.1 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.1 | 0.0 | 0.3 |
| road_total | 42.4 | 22.6 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.838 | 0.838 |
| traffic | 0.869 | 0.772 |
| pollution | 1.015 | 0.706 |
| land_value | 0.541 | 0.325 |
| crime | 0.714 | 0.566 |
| rate_of_growth | 0.755 | 0.819 |
| fire_coverage | 1.035 | 0.123 |
| police_coverage | 0.842 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -218.87 |
| tile_cat | -31.07 |
| flags | -15.49 |
| power | -2.77 |
| half | -2391.43 |
| eighth | -47.05 |
| scalars | -17.59 |
| sc_funds | -1.78 |
| sc_res_valve | -1.65 |
| sc_com_valve | -3.10 |
| sc_ind_valve | -3.18 |
| sc_res_pop | -1.77 |
| sc_com_pop | -0.20 |
| sc_ind_pop | -0.27 |
| sc_score | -0.47 |
| sc_tax_fund | -0.59 |
| sc_road_spend | -0.49 |
| sc_fire_spend | -0.21 |
| sc_police_spend | -0.22 |
| sc_powered_zones | -0.10 |
| sc_unpowered_zones | -0.11 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.41 |
| n_changed | 99.43 |
| kl | 11.59 |
| elbo | -2735.85 |
| derived_viol | 0.00 |

## noledger_50m_full_1step_samples_006000000_dec-b (decoding b: T=1.0, overlays mean)

samples consumed: 6000000

### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)

| predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |
|---|---|---|---|---|---|---|---|---|
| model T=1 (sampled) | 0.302 | 0.289 | 0.295 | 0.276 to 0.313 | 0.196 | 0.173 | 0.184 | 0.157 to 0.213 |
| model T=0 (mode) | 0.540 | 0.259 | 0.350 | 0.329 to 0.369 | 0.440 | 0.136 | 0.207 | 0.173 to 0.244 |
| copy-last-state | n/a | 0.000 | 0.000 | 0.000 to 0.000 | n/a | 0.000 | 0.000 | 0.000 to 0.000 |
| nearest neighbour (mode) | 0.283 | 0.019 | 0.035 | 0.029 to 0.042 | 0.287 | 0.038 | 0.067 | 0.056 to 0.078 |
| nearest neighbour (sampled) | 0.130 | 0.130 | 0.130 | 0.119 to 0.140 | 0.049 | 0.050 | 0.050 | 0.045 to 0.054 |
| engine, other seed (floor) | 0.317 | 0.317 | 0.317 | 0.293 to 0.339 | 0.207 | 0.208 | 0.207 | 0.179 to 0.240 |

### Tile agreement along rollouts: changed-since-start F1 at month h (copy-last-state 0)

| horizon | model raw | model structural | engine floor raw | engine floor structural |
|---|---|---|---|---|
| 1 | 0.368 | 0.393 | 0.432 | 0.402 |
| 12 | 0.379 | 0.388 | 0.430 | 0.428 |
| 24 | 0.353 | 0.360 | 0.408 | 0.408 |

### Share of the copy-to-floor gap closed by the model

| metric | copy | engine floor | model | share closed |
|---|---|---|---|---|
| tile_F1_1m_structural_T1 | 0.0000 | 0.2074 | 0.1838 | 0.886 |
| tile_F1_1m_structural_T0 | 0.0000 | 0.2074 | 0.2074 | 1.000 |
| tile_F1_1m_raw_T1 | 0.0000 | 0.3171 | 0.2953 | 0.931 |
| tile_F1_1m_raw_T0 | 0.0000 | 0.3171 | 0.3502 | 1.104 |
| pop_mae_12m | 4040.1600 | 1032.8800 | 1867.0950 | 0.723 |
| funds_mae_12m | 5714.0800 | 36.8760 | 679.0345 | 0.887 |
| res_valve_mae_12m | 637.3420 | 108.9680 | 230.8265 | 0.769 |
| com_valve_mae_12m | 1210.2460 | 356.8940 | 471.4407 | 0.866 |
| ind_valve_mae_12m | 919.5300 | 258.2060 | 322.0548 | 0.903 |
| pop_median_rel_12m | 0.1033 | 0.0259 | 0.0460 | 0.740 |
| funds_median_rel_12m | 0.3785 | 0.0026 | 0.0496 | 0.875 |
| tile_F1_since_start_12m_structural | 0.0000 | 0.4277 | 0.3884 | 0.908 |
| tile_F1_since_start_12m_raw | 0.0000 | 0.4297 | 0.3787 | 0.881 |
| pop_mae_24m | 7353.3600 | 1754.6000 | 3123.6850 | 0.755 |
| funds_mae_24m | 7364.5720 | 66.5620 | 847.1910 | 0.893 |
| res_valve_mae_24m | 706.1500 | 142.7880 | 272.8780 | 0.769 |
| com_valve_mae_24m | 1010.2040 | 508.6500 | 551.9895 | 0.914 |
| ind_valve_mae_24m | 864.7700 | 416.8580 | 582.8140 | 0.629 |
| pop_median_rel_24m | 0.1597 | 0.0424 | 0.0685 | 0.778 |
| funds_median_rel_24m | 0.6777 | 0.0047 | 0.0732 | 0.898 |
| tile_F1_since_start_24m_structural | 0.0000 | 0.4075 | 0.3599 | 0.883 |
| tile_F1_since_start_24m_raw | 0.0000 | 0.4078 | 0.3528 | 0.865 |

### Open-loop rollouts: error relative to copy-last-state (mean over scalars; <1 beats copy)

| horizon | model (sample) | model (mean of K) | engine other seed | funds med. rel. model / floor / copy | pop med. rel. model / floor / copy |
|---|---|---|---|---|---|
| 1 | 0.593 | 0.401 | 0.204 | 0.007 / 0.000 / 0.017 | 0.008 / 0.006 / 0.007 |
| 12 | 0.423 | 0.295 | 0.146 | 0.050 / 0.003 / 0.378 | 0.046 / 0.026 / 0.103 |
| 24 | 0.475 | 0.341 | 0.167 | 0.073 / 0.005 / 0.678 | 0.068 / 0.042 / 0.160 |

(means over the 18 scalars other than tax and city_time, which are bookkeeping identities)

### Per scalar at 24 months: mean absolute error, model sample / model mean of K / engine other seed / copy

| scalar | model sample | model mean | engine floor | copy |
|---|---|---|---|---|
| funds | 847.2 | 582.2 | 66.6 | 7364.6 |
| tax | 0.0 | 0.0 | 0.0 | 1.9 |
| res_valve | 272.9 | 238.7 | 142.8 | 706.1 |
| com_valve | 552.0 | 489.8 | 508.6 | 1010.2 |
| ind_valve | 582.8 | 502.1 | 416.9 | 864.8 |
| pop | 3123.7 | 2814.9 | 1754.6 | 7353.4 |
| res_pop | 71.6 | 60.5 | 39.0 | 139.9 |
| com_pop | 6.6 | 5.7 | 4.4 | 12.8 |
| ind_pop | 10.1 | 9.0 | 5.8 | 19.7 |
| city_time | 0.0 | 0.0 | 0.0 | 96.0 |
| score | 62.7 | 44.2 | 25.2 | 89.6 |
| tax_fund | 614.4 | 397.1 | 51.5 | 1444.5 |
| road_spend | 191.8 | 98.3 | 8.2 | 647.3 |
| fire_spend | 250.5 | 115.9 | 0.8 | 474.7 |
| police_spend | 341.3 | 161.2 | 6.0 | 604.1 |
| powered_zones | 4.6 | 3.2 | 0.7 | 8.6 |
| unpowered_zones | 3.6 | 3.0 | 0.6 | 7.0 |
| coal_plants | 0.2 | 0.1 | 0.0 | 0.5 |
| nuclear_plants | 0.2 | 0.1 | 0.0 | 0.3 |
| road_total | 38.7 | 21.7 | 10.9 | 85.5 |

### Overlays at 24 months: error ratio to copy-last-state, model sample / engine floor

| overlay | model | floor |
|---|---|---|
| pop_density | 0.845 | 0.838 |
| traffic | 0.885 | 0.772 |
| pollution | 1.018 | 0.706 |
| land_value | 0.543 | 0.325 |
| crime | 0.721 | 0.566 |
| rate_of_growth | 0.762 | 0.819 |
| fire_coverage | 1.116 | 0.123 |
| police_coverage | 0.858 | 0.114 |

### Held-out log-likelihood (nats per transition)

| term | value |
|---|---|
| tile_gate | -217.16 |
| tile_cat | -30.94 |
| flags | -15.72 |
| power | -2.94 |
| half | -2373.09 |
| eighth | -46.89 |
| scalars | -16.46 |
| sc_funds | -1.59 |
| sc_res_valve | -1.56 |
| sc_com_valve | -2.98 |
| sc_ind_valve | -3.08 |
| sc_res_pop | -1.53 |
| sc_com_pop | -0.15 |
| sc_ind_pop | -0.23 |
| sc_score | -0.45 |
| sc_tax_fund | -0.56 |
| sc_road_spend | -0.45 |
| sc_fire_spend | -0.19 |
| sc_police_spend | -0.20 |
| sc_powered_zones | -0.04 |
| sc_unpowered_zones | -0.03 |
| sc_coal_plants | -0.01 |
| sc_nuclear_plants | -0.01 |
| sc_road_total | -3.39 |
| n_changed | 99.43 |
| kl | 12.09 |
| elbo | -2715.30 |
| derived_viol | 0.00 |
