# Funds error split: noledger_50m_full_1step_samples_001200000_dec-b

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 179 | 0.0845 (882) | 0.0228 (289) | 0.0500 (647) | 0.0007 (10) |
| all | other_months | 1821 | 0.0000 (196) | 0.0000 (53) | 0.0000 (153) | 0.0000 (0) |
| budget_sweep | budget_month | 9 | 0.0809 (1147) | 0.0367 (424) | 0.0244 (886) | 0.0010 (17) |
| budget_sweep | other_months | 160 | 0.0000 (12) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 6 | 0.0499 (1086) | 0.0294 (854) | 0.0665 (1559) | 0.0002 (8) |
| budget_sweep+perturb | other_months | 73 | 0.0000 (84) | 0.0000 (20) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 11 | 0.5304 (398) | 0.1264 (135) | 0.4194 (280) | 0.0000 (3) |
| builder/boom | other_months | 86 | 0.0000 (226) | 0.0000 (48) | 0.0000 (318) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 3 | 0.1339 (1168) | 0.0276 (247) | 0.1634 (350) | 0.0006 (8) |
| builder/boom+perturb | other_months | 60 | 0.0000 (155) | 0.0000 (64) | 0.0000 (131) | 0.0000 (0) |
| builder/corridor | budget_month | 10 | 0.0703 (835) | 0.0164 (246) | 0.1044 (930) | 0.0006 (7) |
| builder/corridor | other_months | 105 | 0.0000 (104) | 0.0000 (22) | 0.0000 (40) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 1 | 0.0989 (817) | 0.0087 (72) | 0.0158 (131) | 0.0005 (4) |
| builder/corridor+perturb | other_months | 46 | 0.0000 (205) | 0.0000 (13) | 0.0000 (394) | 0.0000 (0) |
| builder/frugal | budget_month | 13 | 0.0393 (857) | 0.0093 (119) | 0.0309 (355) | 0.0004 (8) |
| builder/frugal | other_months | 95 | 0.0000 (141) | 0.0000 (43) | 0.0000 (132) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 4 | 0.1916 (1032) | 0.0391 (330) | 0.2945 (1474) | 0.0022 (13) |
| builder/frugal+perturb | other_months | 35 | 0.0000 (154) | 0.0000 (27) | 0.0000 (122) | 0.0000 (0) |
| builder/grid | budget_month | 11 | 0.0346 (886) | 0.0297 (190) | 0.0370 (469) | 0.0024 (9) |
| builder/grid | other_months | 131 | 0.0000 (160) | 0.0000 (46) | 0.0000 (300) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 10 | 0.0290 (765) | 0.0103 (250) | 0.0397 (376) | 0.0009 (11) |
| builder/grid+perturb | other_months | 71 | 0.0000 (180) | 0.0000 (54) | 0.0000 (183) | 0.0000 (0) |
| builder/industry | budget_month | 7 | 0.0452 (567) | 0.0239 (360) | 0.0432 (412) | 0.0006 (11) |
| builder/industry | other_months | 84 | 0.0000 (146) | 0.0000 (29) | 0.0000 (192) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 6 | 0.1590 (620) | 0.0215 (108) | 0.0663 (218) | 0.0010 (12) |
| builder/industry+perturb | other_months | 42 | 0.0000 (192) | 0.0000 (34) | 0.0000 (118) | 0.0000 (0) |
| builder/satellite | budget_month | 7 | 0.0758 (878) | 0.0341 (368) | 0.0454 (552) | 0.0006 (9) |
| builder/satellite | other_months | 80 | 0.0000 (155) | 0.0000 (34) | 0.0000 (229) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 5 | 0.0909 (1452) | 0.0159 (353) | 0.0699 (1852) | 0.0010 (21) |
| builder/satellite+perturb | other_months | 55 | 0.0000 (190) | 0.0000 (50) | 0.0000 (252) | 0.0000 (0) |
| builder/transit | budget_month | 11 | 0.1823 (761) | 0.0625 (330) | 0.0765 (726) | 0.0007 (6) |
| builder/transit | other_months | 68 | 0.0000 (138) | 0.0000 (37) | 0.0000 (194) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 4 | 0.2284 (384) | 0.0028 (26) | 0.2732 (1423) | 0.0020 (14) |
| builder/transit+perturb | other_months | 29 | 0.0000 (413) | 0.0000 (207) | 0.0000 (353) | 0.0000 (0) |
| noop | budget_month | 12 | 0.0229 (650) | 0.0057 (228) | 0.0171 (319) | 0.0004 (11) |
| noop | other_months | 140 | 0.0000 (4) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 4 | 0.0497 (991) | 0.0122 (294) | 0.0491 (666) | 0.0006 (12) |
| noop+perturb | other_months | 52 | 0.0000 (44) | 0.0000 (34) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 21 | 0.0982 (1028) | 0.0285 (314) | 0.0433 (526) | 0.0012 (11) |
| random/sprinkle | other_months | 132 | 0.0133 (489) | 0.0023 (118) | 0.0035 (84) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 7 | 0.0450 (804) | 0.0158 (225) | 0.0625 (1052) | 0.0004 (12) |
| random/sprinkle+perturb | other_months | 84 | 0.0025 (435) | 0.0013 (101) | 0.0017 (93) | 0.0000 (0) |
| random/uniform | budget_month | 13 | 0.7252 (1492) | 0.4737 (498) | 0.4583 (663) | 0.0007 (7) |
| random/uniform | other_months | 150 | 0.0000 (443) | 0.0000 (142) | 0.0000 (327) | 0.0000 (0) |
| random/uniform+perturb | budget_month | 4 | 0.2027 (485) | 0.0650 (184) | 0.0000 (247) | 0.0000 (2) |
| random/uniform+perturb | other_months | 43 | 0.0000 (309) | 0.0000 (114) | 0.0000 (186) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 500 | 0.1705 (1989) | 0.3785 (5714) | 0.0026 (37) |
| budget_sweep | 30 | 0.0461 (1275) | 0.0293 (980) | 0.0010 (37) |
| budget_sweep+perturb | 24 | 0.0610 (1310) | 0.0338 (1095) | 0.0009 (45) |
| builder/boom | 23 | 0.5814 (1833) | 6.1942 (9915) | 0.0023 (24) |
| builder/boom+perturb | 15 | 0.6850 (2957) | 4.8241 (12660) | 0.0070 (47) |
| builder/corridor | 24 | 0.2697 (1627) | 0.8689 (5333) | 0.0041 (34) |
| builder/corridor+perturb | 12 | 0.1551 (2322) | 0.2581 (6363) | 0.0049 (65) |
| builder/frugal | 24 | 0.1723 (2227) | 0.3679 (5242) | 0.0033 (45) |
| builder/frugal+perturb | 8 | 0.1880 (2563) | 0.4315 (3823) | 0.0017 (28) |
| builder/grid | 36 | 0.1920 (1854) | 0.6446 (7643) | 0.0041 (41) |
| builder/grid+perturb | 24 | 0.2007 (2075) | 0.5656 (8538) | 0.0032 (36) |
| builder/industry | 27 | 0.1363 (1602) | 0.5414 (4781) | 0.0027 (36) |
| builder/industry+perturb | 9 | 0.3462 (1878) | 1.5478 (6997) | 0.0062 (26) |
| builder/satellite | 33 | 0.4178 (1564) | 3.0552 (8084) | 0.0044 (26) |
| builder/satellite+perturb | 11 | 0.3730 (2296) | 2.9588 (10470) | 0.0029 (29) |
| builder/transit | 24 | 0.1873 (1552) | 0.6405 (7723) | 0.0023 (31) |
| builder/transit+perturb | 8 | 0.8431 (1748) | 3.9967 (9832) | 0.0127 (56) |
| noop | 34 | 0.0544 (1086) | 0.0431 (545) | 0.0016 (32) |
| noop+perturb | 14 | 0.0560 (1333) | 0.0284 (370) | 0.0017 (39) |
| random/sprinkle | 47 | 0.1421 (2148) | 0.1507 (1705) | 0.0018 (35) |
| random/sprinkle+perturb | 23 | 0.1296 (2126) | 0.1561 (1742) | 0.0015 (39) |
| random/uniform | 42 | 1.0000 (3524) | 3.2055 (10422) | 0.0057 (40) |
| random/uniform+perturb | 8 | 0.9184 (4921) | 5.5170 (15375) | 0.0024 (44) |
