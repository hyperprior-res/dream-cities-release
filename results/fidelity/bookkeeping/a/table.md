# Bookkeeping diagnostic, variant a

**Teacher-forced.** Every ratio below except the free-running column is the scalars-only network given the engine's true next census, next-map summary and charged build cost; in the emulator's rollouts the third stage is fed the model's own sampled ones instead.

train: 3,000,000 train_full transitions; held-out: 72,000 heldout_eval transitions (and the 2,000 of the development selection, with the engine re-seeded at month t). Parameters 4,328,993; 201 s on GPU.

Mean absolute error of the rounded one-month prediction as a ratio to copy-last-state (all held-out transitions; the 2,000-transition ratio and the engine's ratio on the same 2,000 beside it).

Free-running column: pilot 6 (censored likelihood, 600,064 samples, development selection): the full emulator's one-month sample (T=1, decoding a) on the same 2,000 transitions, its census, map and cost sampled by the model, as a ratio to copy-last-state.

| entry | 1,003,520 | 10,002,432 | 50,003,968 | 199,999,488 | final, 2,000 | engine other seed, 2,000 | final exact share | free-running T=1, 2,000 |
|---|---|---|---|---|---|---|---|---|
| res_valve | 1.027 | 0.266 | 0.136 | 0.069 | 0.072 | 0.031 | 0.698 | 0.108 |
| com_valve | 0.937 | 0.135 | 0.083 | 0.052 | 0.051 | 0.061 | 0.357 | 0.106 |
| ind_valve | 0.921 | 0.151 | 0.072 | 0.018 | 0.021 | 0.004 | 0.484 | 0.028 |
| score | 1.012 | 0.417 | 0.182 | 0.155 | 0.163 | 0.146 | 0.907 | 0.255 |
| funds | 0.589 | 0.142 | 0.065 | 0.024 | 0.024 | 0.004 | 0.740 | 0.283 |
| tax_fund | 1.155 | 0.413 | 0.138 | 0.069 | 0.066 | 0.011 | 0.906 | 0.115 |
| road_spend | 1.591 | 0.412 | 0.251 | 0.192 | 0.175 | 0.029 | 0.917 | 0.173 |
| fire_spend | 1.224 | 0.441 | 0.214 | 0.065 | 0.051 | 0.004 | 0.968 | 0.072 |
| police_spend | 1.157 | 0.486 | 0.171 | 0.069 | 0.063 | 0.000 | 0.964 | 0.079 |
| sprite_cycle | 0.641 | 0.487 | 0.379 | 0.365 | 0.292 | 0.000 | 0.702 | 0.220 |
| total_pop | 0.617 | 0.241 | 0.159 | 0.125 | 0.125 | 0.167 | 0.417 | 0.519 |
| res_hist0 | 0.833 | 0.633 | 0.308 | 0.046 | 0.044 | 0.810 | 0.947 | 0.860 |
| res_hist1 | 0.822 | 0.604 | 0.498 | 0.010 | 0.010 | 0.000 | 0.992 | 0.056 |
| com_hist0 | 0.790 | 0.350 | 0.236 | 0.002 | 0.002 | 0.766 | 0.998 | 0.803 |
| com_hist1 | 0.785 | 0.321 | 0.136 | 0.006 | 0.004 | 0.000 | 0.995 | 0.007 |
| ind_hist0 | 0.754 | 0.417 | 0.091 | 0.004 | 0.003 | 0.721 | 0.996 | 0.763 |
| ind_hist1 | 0.749 | 0.437 | 0.518 | 0.008 | 0.009 | 0.000 | 0.992 | 0.016 |
| res_cap | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.999 | 1.000 |
| com_cap | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 0.667 |
| ind_cap | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 |
| need_hospital | 1.000 | 0.927 | 0.811 | 0.260 | 0.138 | 0.752 | 0.986 | 1.312 |
| need_church | 1.000 | 0.960 | 0.782 | 0.242 | 0.198 | 0.615 | 0.990 | 1.077 |
| road_fund | 1.293 | 0.433 | 0.225 | 0.186 | 0.163 | 0.031 | 0.917 | 0.154 |
| police_fund | 1.177 | 0.271 | 0.091 | 0.046 | 0.040 | 0.000 | 0.976 | 0.029 |
| fire_fund | 1.233 | 0.261 | 0.102 | 0.041 | 0.037 | 0.000 | 0.978 | 0.030 |
| auto_budget | 1.000 | 1.000 | 0.894 | 0.109 | 0.333 | 0.000 | 1.000 | 0.167 |
| fire_pop | 0.993 | 0.402 | 0.279 | 0.259 | 0.198 | 0.877 | 0.979 | 1.269 |
| city_center_x | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.027 | 0.955 | 0.955 |
| city_center_y | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.049 | 0.955 | 1.184 |
| pollution_max_x | 1.045 | 1.427 | 1.655 | 1.768 | 1.805 | 1.136 | 0.385 | 2.537 |
| pollution_max_y | 1.011 | 1.123 | 1.476 | 1.599 | 1.628 | 1.049 | 0.406 | 2.133 |
| flood_count | 0.608 | 0.514 | 0.508 | 0.507 | 0.500 | 0.000 | 0.999 | 0.019 |
| abs_dist | 0.918 | 0.927 | 0.838 | 0.879 | 0.941 | 1.030 | 0.627 | 1.280 |
