# Check: pilot 6 against pilot 5

Selection dev (2000 transitions, 500 plans, key c0a3ceceb9a2a0bf); pilot 5: <cache>/ckpt/pilot5_bk/samples_000600064.pt (600,064 samples, decoding a, weights ema); pilot 6: <cache>/ckpt/pilot6_censored/samples_000600064.pt (600,064 samples, decoding a, weights ema). One model sample at T=1 in every row. Training-seed replicate: <cache>/ckpt/pilot6_censored_s1/samples_000600064.pt.

| metric | pilot 5 | pilot 5, other noise seed | pilot 6 | pilot 6, other noise seed | pilot 6, other training seed | evaluation noise | training noise | verdict |
|---|---|---|---|---|---|---|---|---|
| tile structural F1, one month | 0.1473 | 0.1472 | 0.1466 | 0.1462 | 0.1467 | 0.0001 | 0.0001 | worse |
| tile structural F1 since start, 12 months | 0.3463 | 0.3466 | 0.3433 | 0.3431 | 0.3434 | 0.0003 | 0.0001 | worse |
| tile structural F1 since start, 24 months | 0.3191 | 0.3194 | 0.3165 | 0.3165 | 0.3173 | 0.0003 | 0.0008 | worse |
| funds median rel. error, 12 months | 0.0335 | 0.0353 | 0.0403 | 0.0402 | 0.0442 | 0.0017 | 0.0040 | within noise |
| funds median rel. error, 24 months | 0.0527 | 0.0543 | 0.0598 | 0.0576 | 0.0635 | 0.0016 | 0.0036 | within noise |
| population median rel. error, 12 months | 0.0308 | 0.0306 | 0.0309 | 0.0313 | 0.0295 | 0.0002 | 0.0015 | within noise |
| population median rel. error, 24 months | 0.0575 | 0.0586 | 0.0578 | 0.0570 | 0.0637 | 0.0012 | 0.0059 | within noise |
| res_valve, one month from start (x copy) | 0.1547 | 0.1568 | 0.0955 | 0.0961 | 0.1037 | 0.0021 | 0.0082 | better |
| com_valve, one month from start (x copy) | 0.1177 | 0.1185 | 0.0893 | 0.0919 | 0.1068 | 0.0008 | 0.0175 | better |
| ind_valve, one month from start (x copy) | 0.0750 | 0.0754 | 0.0582 | 0.0584 | 0.0580 | 0.0004 | 0.0002 | better |
| score, one month from start (x copy) | 0.2308 | 0.2317 | 0.2274 | 0.2263 | 0.2745 | 0.0008 | 0.0471 | better |
| res_valve, 12 months (x copy) | 0.2704 | 0.2695 | 0.2771 | 0.2792 | 0.3268 | 0.0009 | 0.0497 | within noise |
| com_valve, 12 months (x copy) | 0.4224 | 0.4157 | 0.4045 | 0.4057 | 0.4071 | 0.0067 | 0.0026 | better |
| ind_valve, 12 months (x copy) | 0.3203 | 0.3201 | 0.3260 | 0.3287 | 0.3409 | 0.0002 | 0.0149 | within noise |
| res_valve, 24 months (x copy) | 0.3401 | 0.3484 | 0.3264 | 0.3187 | 0.3823 | 0.0082 | 0.0560 | better |
| com_valve, 24 months (x copy) | 0.6077 | 0.6106 | 0.5827 | 0.5719 | 0.5826 | 0.0029 | 0.0002 | better |
| ind_valve, 24 months (x copy) | 0.5824 | 0.5762 | 0.5904 | 0.5732 | 0.5965 | 0.0063 | 0.0061 | within noise |
| funds, one month on random transitions (MAE) | 53.6355 | 55.2890 | 55.9535 | 58.9625 | 61.2590 | 1.6535 | 5.3055 | within noise |
| mean ratio over scalars, 24 months | 0.3905 | 0.4265 | 0.4080 | 0.4089 | 0.4343 | 0.0359 | 0.0263 | within noise |

Verdicts: better 7, within noise 9, worse 3

## pilot 6: shares at the engine's bounds, one month (random transitions)

| entry | bounds | model at lower | engine at lower | model at upper | engine at upper | model beyond | engine beyond |
|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 12.15% | 11.25% | n/a | n/a | 0 | 0 |
| res_valve | [-2000, 2000] | 6.90% | 6.90% | 64.20% | 63.90% | 0 | 0 |
| com_valve | [-1500, 1500] | 18.40% | 18.20% | 27.95% | 27.80% | 0 | 0 |
| ind_valve | [-1500, 1500] | 16.70% | 16.60% | 25.75% | 25.65% | 0 | 0 |
| res_pop | [0, inf] | 0.00% | 0.05% | n/a | n/a | 0 | 0 |
| com_pop | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0 | 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| tax_fund | [0, inf] | 11.55% | 11.55% | n/a | n/a | 0 | 0 |
| road_spend | [0, inf] | 11.40% | 11.40% | n/a | n/a | 0 | 0 |
| fire_spend | [0, inf] | 13.45% | 13.40% | n/a | n/a | 0 | 0 |
| police_spend | [0, inf] | 17.65% | 17.75% | n/a | n/a | 0 | 0 |
| powered_zones | [0, inf] | 1.05% | 1.10% | n/a | n/a | 0 | 0 |
| unpowered_zones | [0, inf] | 46.85% | 46.90% | n/a | n/a | 0 | 0 |
| coal_plants | [0, inf] | 39.50% | 39.35% | n/a | n/a | 0 | 0 |
| nuclear_plants | [0, inf] | 23.20% | 23.10% | n/a | n/a | 0 | 0 |
| road_total | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| total_pop | [0, inf] | 0.15% | 0.00% | n/a | n/a | 0 | 0 |
| res_hist0 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0 | 0 |
| res_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0 | 0 |
| com_hist0 | [0, inf] | 0.05% | 0.10% | n/a | n/a | 0 | 0 |
| com_hist1 | [0, inf] | 0.05% | 0.05% | n/a | n/a | 0 | 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| res_cap | [0, 1] | 96.75% | 96.65% | 3.25% | 3.35% | 0 | 0 |
| com_cap | [0, 1] | 99.45% | 99.55% | 0.55% | 0.45% | 0 | 0 |
| ind_cap | [0, 1] | 99.80% | 99.75% | 0.20% | 0.25% | 0 | 0 |
| need_hospital | [-1, 1] | 4.15% | 2.45% | 24.40% | 22.85% | 0 | 0 |
| need_church | [-1, 1] | 2.35% | 1.45% | 38.30% | 37.90% | 0 | 0 |
| road_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 0 | 0 |
| police_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 0 | 0 |
| fire_fund | [0, inf] | 10.65% | 10.65% | n/a | n/a | 0 | 0 |
| auto_budget | [0, 1] | 12.60% | 12.65% | 87.40% | 87.35% | 0 | 0 |
| fire_pop | [0, inf] | 94.20% | 95.25% | n/a | n/a | 0 | 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| pollution_max_x | [0, 118] | 0.25% | 0.00% | 0.70% | 0.00% | 0 | 0 |
| pollution_max_y | [0, 98] | 1.25% | 0.00% | 0.95% | 0.00% | 0 | 0 |
| flood_count | [0, 30] | 99.65% | 99.65% | 0.00% | 0.00% | 0 | 0 |
| abs_dist | [0, inf] | 64.90% | 63.95% | n/a | n/a | 0 | 0 |
| build_cost | [0, inf] | 79.50% | 78.60% | n/a | n/a | 0 | 0 |

## pilot 6: shares at the engine's bounds, rollouts (months 1..H of the plans)

| entry | bounds | model at lower | engine at lower | model at upper | engine at upper | model beyond | engine beyond |
|---|---|---|---|---|---|---|---|
| funds | [0, inf] | 3.62% | 3.27% | n/a | n/a | 0 | 0 |
| res_valve | [-2000, 2000] | 2.97% | 3.19% | 70.08% | 65.26% | 0 | 0 |
| com_valve | [-1500, 1500] | 19.40% | 14.96% | 26.93% | 28.68% | 0 | 0 |
| ind_valve | [-1500, 1500] | 16.43% | 14.17% | 24.37% | 24.52% | 0 | 0 |
| res_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| com_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| ind_pop | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| score | [0, 1000] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| tax_fund | [0, inf] | 26.50% | 26.63% | n/a | n/a | 0 | 0 |
| road_spend | [0, inf] | 25.86% | 25.73% | n/a | n/a | 0 | 0 |
| fire_spend | [0, inf] | 26.38% | 25.96% | n/a | n/a | 0 | 0 |
| police_spend | [0, inf] | 26.53% | 26.40% | n/a | n/a | 0 | 0 |
| powered_zones | [0, inf] | 0.00% | 0.27% | n/a | n/a | 0 | 0 |
| unpowered_zones | [0, inf] | 47.48% | 50.18% | n/a | n/a | 0 | 0 |
| coal_plants | [0, inf] | 41.58% | 39.12% | n/a | n/a | 0 | 0 |
| nuclear_plants | [0, inf] | 27.84% | 23.54% | n/a | n/a | 0 | 0 |
| road_total | [0, inf] | 0.04% | 0.00% | n/a | n/a | 0 | 0 |
| total_pop | [0, inf] | 0.31% | 0.00% | n/a | n/a | 0 | 0 |
| res_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| res_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| com_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| com_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| ind_hist0 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| ind_hist1 | [0, inf] | 0.00% | 0.00% | n/a | n/a | 0 | 0 |
| res_cap | [0, 1] | 95.72% | 96.87% | 4.28% | 3.13% | 0 | 0 |
| com_cap | [0, 1] | 98.56% | 99.58% | 1.44% | 0.42% | 0 | 0 |
| ind_cap | [0, 1] | 99.64% | 100.00% | 0.36% | 0.00% | 0 | 0 |
| need_hospital | [-1, 1] | 11.66% | 1.28% | 36.43% | 24.30% | 0 | 0 |
| need_church | [-1, 1] | 7.16% | 0.94% | 45.70% | 39.90% | 0 | 0 |
| road_fund | [0, inf] | 25.76% | 25.69% | n/a | n/a | 0 | 0 |
| police_fund | [0, inf] | 25.43% | 25.69% | n/a | n/a | 0 | 0 |
| fire_fund | [0, inf] | 25.55% | 25.69% | n/a | n/a | 0 | 0 |
| auto_budget | [0, 1] | 1.88% | 2.82% | 98.12% | 97.18% | 0 | 0 |
| fire_pop | [0, inf] | 83.13% | 97.75% | n/a | n/a | 0 | 0 |
| city_center_x | [0, 119] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| city_center_y | [0, 99] | 0.00% | 0.00% | 0.00% | 0.00% | 0 | 0 |
| pollution_max_x | [0, 118] | 0.79% | 0.00% | 1.01% | 0.00% | 0 | 0 |
| pollution_max_y | [0, 98] | 1.11% | 0.00% | 1.52% | 0.00% | 0 | 0 |
| flood_count | [0, 30] | 99.38% | 99.64% | 0.00% | 0.00% | 0 | 0 |
| abs_dist | [0, inf] | 70.11% | 67.43% | n/a | n/a | 0 | 0 |
| build_cost | [0, inf] | 68.50% | 67.62% | n/a | n/a | 0 | 0 |
