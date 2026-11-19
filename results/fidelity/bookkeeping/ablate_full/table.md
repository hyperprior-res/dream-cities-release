# Bookkeeping diagnostic, variant a

train: 3,000,000 train_full transitions; held-out: 72,000 heldout_eval transitions (and the 2,000 of the fidelity evaluation, with the engine floor re-seeded at month t). Parameters 4,328,993; 100 s on GPU.

Mean absolute error of the rounded one-month prediction as a ratio to copy-last-state (all held-out transitions; the 2,000-transition ratio and the engine floor's ratio on the same 2,000 beside it).

| entry | 99,999,744 | final, 2,000 | engine floor, 2,000 | final exact share |
|---|---|---|---|---|
| res_valve | 0.072 | 0.076 | 0.031 | 0.670 |
| com_valve | 0.056 | 0.053 | 0.061 | 0.296 |
| ind_valve | 0.022 | 0.025 | 0.004 | 0.439 |
| score | 0.152 | 0.158 | 0.146 | 0.907 |
| funds | 0.028 | 0.024 | 0.004 | 0.686 |
| tax_fund | 0.063 | 0.059 | 0.011 | 0.892 |
| road_spend | 0.234 | 0.201 | 0.029 | 0.913 |
| fire_spend | 0.098 | 0.091 | 0.004 | 0.963 |
| police_spend | 0.095 | 0.065 | 0.000 | 0.961 |
| sprite_cycle | 0.365 | 0.293 | 0.000 | 0.551 |
| total_pop | 0.132 | 0.130 | 0.167 | 0.388 |
| res_hist0 | 0.065 | 0.063 | 0.810 | 0.927 |
| res_hist1 | 0.009 | 0.008 | 0.000 | 0.992 |
| com_hist0 | 0.002 | 0.001 | 0.766 | 0.998 |
| com_hist1 | 0.005 | 0.004 | 0.000 | 0.995 |
| ind_hist0 | 0.005 | 0.006 | 0.721 | 0.995 |
| ind_hist1 | 0.006 | 0.008 | 0.000 | 0.994 |
| res_cap | 1.000 | 1.000 | 0.000 | 0.999 |
| com_cap | 1.000 | 1.000 | 0.000 | 1.000 |
| ind_cap | 1.000 | 1.000 | 0.000 | 1.000 |
| need_hospital | 0.825 | 0.817 | 0.752 | 0.955 |
| need_church | 0.809 | 0.780 | 0.615 | 0.967 |
| road_fund | 0.194 | 0.161 | 0.031 | 0.914 |
| police_fund | 0.040 | 0.035 | 0.000 | 0.971 |
| fire_fund | 0.038 | 0.037 | 0.000 | 0.971 |
| auto_budget | 0.803 | 1.000 | 0.000 | 0.997 |
| fire_pop | 0.257 | 0.190 | 0.877 | 0.979 |
| city_center_x | 1.000 | 1.000 | 0.027 | 0.955 |
| city_center_y | 1.000 | 1.000 | 0.049 | 0.955 |
| pollution_max_x | 1.730 | 1.805 | 1.136 | 0.396 |
| pollution_max_y | 1.510 | 1.545 | 1.049 | 0.422 |
| flood_count | 0.508 | 0.500 | 0.000 | 0.999 |
| abs_dist | 0.841 | 0.882 | 1.030 | 0.627 |
