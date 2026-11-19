# Bookkeeping diagnostic, variant a

train: 3,000,000 train_full transitions; held-out: 72,000 heldout_eval transitions (and the 2,000 of the fidelity evaluation, with the engine floor re-seeded at month t). Parameters 4,328,993; 101 s on GPU.

Mean absolute error of the rounded one-month prediction as a ratio to copy-last-state (all held-out transitions; the 2,000-transition ratio and the engine floor's ratio on the same 2,000 beside it).

| entry | 99,999,744 | final, 2,000 | engine floor, 2,000 | final exact share |
|---|---|---|---|---|
| res_valve | 0.072 | 0.074 | 0.031 | 0.680 |
| com_valve | 0.055 | 0.053 | 0.061 | 0.297 |
| ind_valve | 0.020 | 0.023 | 0.004 | 0.458 |
| score | 0.157 | 0.171 | 0.146 | 0.907 |
| funds | 0.036 | 0.033 | 0.004 | 0.674 |
| tax_fund | 0.071 | 0.066 | 0.011 | 0.893 |
| road_spend | 0.211 | 0.188 | 0.029 | 0.911 |
| fire_spend | 0.207 | 0.175 | 0.004 | 0.960 |
| police_spend | 0.193 | 0.159 | 0.000 | 0.950 |
| sprite_cycle | 0.365 | 0.293 | 0.000 | 0.581 |
| total_pop | 0.129 | 0.123 | 0.167 | 0.387 |
| res_hist0 | 0.058 | 0.060 | 0.810 | 0.933 |
| res_hist1 | 0.009 | 0.007 | 0.000 | 0.992 |
| com_hist0 | 0.002 | 0.003 | 0.766 | 0.997 |
| com_hist1 | 0.004 | 0.004 | 0.000 | 0.996 |
| ind_hist0 | 0.003 | 0.003 | 0.721 | 0.997 |
| ind_hist1 | 0.005 | 0.005 | 0.000 | 0.995 |
| res_cap | 1.000 | 1.000 | 0.000 | 0.999 |
| com_cap | 1.000 | 1.000 | 0.000 | 1.000 |
| ind_cap | 1.000 | 1.000 | 0.000 | 1.000 |
| need_hospital | 0.927 | 0.927 | 0.752 | 0.950 |
| need_church | 0.929 | 0.879 | 0.615 | 0.962 |
| road_fund | 0.179 | 0.145 | 0.031 | 0.914 |
| police_fund | 0.160 | 0.136 | 0.000 | 0.961 |
| fire_fund | 0.166 | 0.129 | 0.000 | 0.967 |
| auto_budget | 0.741 | 0.833 | 0.000 | 0.997 |
| fire_pop | 0.861 | 0.750 | 0.877 | 0.965 |
| city_center_x | 1.000 | 1.000 | 0.027 | 0.955 |
| city_center_y | 1.000 | 1.000 | 0.049 | 0.955 |
| pollution_max_x | 1.727 | 1.763 | 1.136 | 0.396 |
| pollution_max_y | 1.430 | 1.449 | 1.049 | 0.408 |
| flood_count | 0.508 | 0.500 | 0.000 | 0.999 |
| abs_dist | 0.862 | 0.914 | 1.030 | 0.602 |
