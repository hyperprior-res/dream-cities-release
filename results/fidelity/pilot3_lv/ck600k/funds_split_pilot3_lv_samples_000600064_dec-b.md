# Funds error split: pilot3_lv_samples_000600064_dec-b

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 179 | 0.0387 (485) | 0.0187 (297) | 0.0500 (647) | 0.0007 (10) |
| all | other_months | 1821 | 0.0000 (72) | 0.0000 (30) | 0.0000 (153) | 0.0000 (0) |
| budget_sweep | budget_month | 9 | 0.0384 (688) | 0.0098 (453) | 0.0244 (886) | 0.0010 (17) |
| budget_sweep | other_months | 160 | 0.0000 (4) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 6 | 0.0546 (1403) | 0.0341 (1022) | 0.0665 (1559) | 0.0002 (8) |
| budget_sweep+perturb | other_months | 73 | 0.0000 (23) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 11 | 0.3627 (322) | 0.1307 (166) | 0.4194 (280) | 0.0000 (3) |
| builder/boom | other_months | 86 | 0.0000 (82) | 0.0000 (23) | 0.0000 (318) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 3 | 0.0114 (103) | 0.0325 (302) | 0.1634 (350) | 0.0006 (8) |
| builder/boom+perturb | other_months | 60 | 0.0000 (67) | 0.0000 (10) | 0.0000 (131) | 0.0000 (0) |
| builder/corridor | budget_month | 10 | 0.0417 (493) | 0.0145 (137) | 0.1044 (930) | 0.0006 (7) |
| builder/corridor | other_months | 105 | 0.0000 (28) | 0.0000 (4) | 0.0000 (40) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 1 | 0.0220 (182) | 0.0167 (138) | 0.0158 (131) | 0.0005 (4) |
| builder/corridor+perturb | other_months | 46 | 0.0000 (51) | 0.0000 (12) | 0.0000 (394) | 0.0000 (0) |
| builder/frugal | budget_month | 13 | 0.0323 (416) | 0.0167 (186) | 0.0309 (355) | 0.0004 (8) |
| builder/frugal | other_months | 95 | 0.0000 (62) | 0.0000 (15) | 0.0000 (132) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 4 | 0.0985 (725) | 0.0306 (495) | 0.2945 (1474) | 0.0022 (13) |
| builder/frugal+perturb | other_months | 35 | 0.0000 (53) | 0.0000 (13) | 0.0000 (122) | 0.0000 (0) |
| builder/grid | budget_month | 11 | 0.0484 (369) | 0.0356 (160) | 0.0370 (469) | 0.0024 (9) |
| builder/grid | other_months | 131 | 0.0000 (72) | 0.0000 (20) | 0.0000 (300) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 10 | 0.0133 (447) | 0.0140 (362) | 0.0397 (376) | 0.0009 (11) |
| builder/grid+perturb | other_months | 71 | 0.0000 (36) | 0.0000 (23) | 0.0000 (183) | 0.0000 (0) |
| builder/industry | budget_month | 7 | 0.0234 (220) | 0.0182 (224) | 0.0432 (412) | 0.0006 (11) |
| builder/industry | other_months | 84 | 0.0000 (43) | 0.0000 (11) | 0.0000 (192) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 6 | 0.0424 (164) | 0.0224 (146) | 0.0663 (218) | 0.0010 (12) |
| builder/industry+perturb | other_months | 42 | 0.0000 (33) | 0.0000 (8) | 0.0000 (118) | 0.0000 (0) |
| builder/satellite | budget_month | 7 | 0.0275 (331) | 0.0119 (206) | 0.0454 (552) | 0.0006 (9) |
| builder/satellite | other_months | 80 | 0.0000 (54) | 0.0000 (14) | 0.0000 (229) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 5 | 0.0490 (1210) | 0.0067 (670) | 0.0699 (1852) | 0.0010 (21) |
| builder/satellite+perturb | other_months | 55 | 0.0000 (74) | 0.0000 (15) | 0.0000 (252) | 0.0000 (0) |
| builder/transit | budget_month | 11 | 0.1040 (613) | 0.0643 (341) | 0.0765 (726) | 0.0007 (6) |
| builder/transit | other_months | 68 | 0.0000 (60) | 0.0000 (11) | 0.0000 (194) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 4 | 0.0884 (600) | 0.0106 (117) | 0.2732 (1423) | 0.0020 (14) |
| builder/transit+perturb | other_months | 29 | 0.0000 (84) | 0.0000 (35) | 0.0000 (353) | 0.0000 (0) |
| noop | budget_month | 12 | 0.0152 (284) | 0.0066 (201) | 0.0171 (319) | 0.0004 (11) |
| noop | other_months | 140 | 0.0000 (3) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 4 | 0.0253 (393) | 0.0106 (154) | 0.0491 (666) | 0.0006 (12) |
| noop+perturb | other_months | 52 | 0.0000 (29) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 21 | 0.0284 (390) | 0.0142 (263) | 0.0433 (526) | 0.0012 (11) |
| random/sprinkle | other_months | 132 | 0.0044 (134) | 0.0013 (33) | 0.0035 (84) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 7 | 0.0045 (600) | 0.0121 (247) | 0.0625 (1052) | 0.0004 (12) |
| random/sprinkle+perturb | other_months | 84 | 0.0024 (127) | 0.0015 (58) | 0.0017 (93) | 0.0000 (0) |
| random/uniform | budget_month | 13 | 0.2180 (683) | 0.1698 (533) | 0.4583 (663) | 0.0007 (7) |
| random/uniform | other_months | 150 | 0.0000 (248) | 0.0000 (164) | 0.0000 (327) | 0.0000 (0) |
| random/uniform+perturb | budget_month | 4 | 0.0000 (29) | 0.0298 (74) | 0.0000 (247) | 0.0000 (2) |
| random/uniform+perturb | other_months | 43 | 0.0000 (133) | 0.0000 (156) | 0.0000 (186) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 500 | 0.0724 (1104) | 0.3785 (5714) | 0.0026 (37) |
| budget_sweep | 30 | 0.0302 (1105) | 0.0293 (980) | 0.0010 (37) |
| budget_sweep+perturb | 24 | 0.0436 (1153) | 0.0338 (1095) | 0.0009 (45) |
| builder/boom | 23 | 0.3047 (912) | 6.1942 (9915) | 0.0023 (24) |
| builder/boom+perturb | 15 | 0.2818 (1509) | 4.8241 (12660) | 0.0070 (47) |
| builder/corridor | 24 | 0.0784 (616) | 0.8689 (5333) | 0.0041 (34) |
| builder/corridor+perturb | 12 | 0.0422 (962) | 0.2581 (6363) | 0.0049 (65) |
| builder/frugal | 24 | 0.0733 (1263) | 0.3679 (5242) | 0.0033 (45) |
| builder/frugal+perturb | 8 | 0.0678 (853) | 0.4315 (3823) | 0.0017 (28) |
| builder/grid | 36 | 0.0839 (818) | 0.6446 (7643) | 0.0041 (41) |
| builder/grid+perturb | 24 | 0.0873 (1056) | 0.5656 (8538) | 0.0032 (36) |
| builder/industry | 27 | 0.0516 (627) | 0.5414 (4781) | 0.0027 (36) |
| builder/industry+perturb | 9 | 0.0747 (501) | 1.5478 (6997) | 0.0062 (26) |
| builder/satellite | 33 | 0.1442 (531) | 3.0552 (8084) | 0.0044 (26) |
| builder/satellite+perturb | 11 | 0.2346 (977) | 2.9588 (10470) | 0.0029 (29) |
| builder/transit | 24 | 0.0878 (887) | 0.6405 (7723) | 0.0023 (31) |
| builder/transit+perturb | 8 | 0.3370 (1008) | 3.9967 (9832) | 0.0127 (56) |
| noop | 34 | 0.0196 (465) | 0.0431 (545) | 0.0016 (32) |
| noop+perturb | 14 | 0.0197 (500) | 0.0284 (370) | 0.0017 (39) |
| random/sprinkle | 47 | 0.0550 (809) | 0.1507 (1705) | 0.0018 (35) |
| random/sprinkle+perturb | 23 | 0.0561 (872) | 0.1561 (1742) | 0.0015 (39) |
| random/uniform | 42 | 0.8327 (3010) | 3.2055 (10422) | 0.0057 (40) |
| random/uniform+perturb | 8 | 1.0000 (5338) | 5.5170 (15375) | 0.0024 (44) |
