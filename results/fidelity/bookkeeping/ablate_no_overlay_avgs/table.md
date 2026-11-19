# Bookkeeping diagnostic, variant a

train: 3,000,000 train_full transitions; held-out: 72,000 heldout_eval transitions (and the 2,000 of the fidelity evaluation, with the engine floor re-seeded at month t). Parameters 4,328,993; 101 s on GPU.

Mean absolute error of the rounded one-month prediction as a ratio to copy-last-state (all held-out transitions; the 2,000-transition ratio and the engine floor's ratio on the same 2,000 beside it).

| entry | 99,999,744 | final, 2,000 | engine floor, 2,000 | final exact share |
|---|---|---|---|---|
| res_valve | 0.073 | 0.076 | 0.031 | 0.683 |
| com_valve | 0.056 | 0.052 | 0.061 | 0.295 |
| ind_valve | 0.026 | 0.027 | 0.004 | 0.400 |
| score | 0.212 | 0.224 | 0.146 | 0.904 |
| funds | 0.065 | 0.062 | 0.004 | 0.662 |
| tax_fund | 0.224 | 0.201 | 0.011 | 0.891 |
| road_spend | 0.260 | 0.230 | 0.029 | 0.911 |
| fire_spend | 0.118 | 0.114 | 0.004 | 0.962 |
| police_spend | 0.112 | 0.063 | 0.000 | 0.959 |
| sprite_cycle | 0.365 | 0.293 | 0.000 | 0.544 |
| total_pop | 0.129 | 0.127 | 0.167 | 0.394 |
| res_hist0 | 0.061 | 0.059 | 0.810 | 0.931 |
| res_hist1 | 0.010 | 0.013 | 0.000 | 0.991 |
| com_hist0 | 0.002 | 0.001 | 0.766 | 0.998 |
| com_hist1 | 0.004 | 0.003 | 0.000 | 0.997 |
| ind_hist0 | 0.004 | 0.004 | 0.721 | 0.996 |
| ind_hist1 | 0.006 | 0.006 | 0.000 | 0.994 |
| res_cap | 1.000 | 1.000 | 0.000 | 0.999 |
| com_cap | 1.000 | 1.000 | 0.000 | 1.000 |
| ind_cap | 1.000 | 1.000 | 0.000 | 1.000 |
| need_hospital | 0.647 | 0.569 | 0.752 | 0.965 |
| need_church | 0.606 | 0.549 | 0.615 | 0.975 |
| road_fund | 0.227 | 0.191 | 0.031 | 0.914 |
| police_fund | 0.041 | 0.033 | 0.000 | 0.969 |
| fire_fund | 0.037 | 0.031 | 0.000 | 0.971 |
| auto_budget | 0.847 | 0.833 | 0.000 | 0.997 |
| fire_pop | 0.261 | 0.205 | 0.877 | 0.979 |
| city_center_x | 1.000 | 1.000 | 0.027 | 0.955 |
| city_center_y | 1.000 | 1.000 | 0.049 | 0.955 |
| pollution_max_x | 1.740 | 1.843 | 1.136 | 0.358 |
| pollution_max_y | 1.596 | 1.625 | 1.049 | 0.394 |
| flood_count | 0.508 | 0.500 | 0.000 | 0.999 |
| abs_dist | 0.840 | 0.887 | 1.030 | 0.617 |
