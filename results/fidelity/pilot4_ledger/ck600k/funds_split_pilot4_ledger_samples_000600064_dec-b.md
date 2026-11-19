# Funds error split: pilot4_ledger_samples_000600064_dec-b

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 179 | 0.0344 (494) | 0.0203 (308) | 0.0500 (647) | 0.0007 (10) |
| all | other_months | 1821 | 0.0000 (103) | 0.0000 (55) | 0.0000 (153) | 0.0000 (0) |
| budget_sweep | budget_month | 9 | 0.0219 (394) | 0.0263 (523) | 0.0244 (886) | 0.0010 (17) |
| budget_sweep | other_months | 160 | 0.0000 (5) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 6 | 0.0354 (899) | 0.0472 (1262) | 0.0665 (1559) | 0.0002 (8) |
| budget_sweep+perturb | other_months | 73 | 0.0000 (48) | 0.0000 (6) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 11 | 0.1449 (534) | 0.0276 (168) | 0.4194 (280) | 0.0000 (3) |
| builder/boom | other_months | 86 | 0.0000 (99) | 0.0000 (42) | 0.0000 (318) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 3 | 0.1275 (494) | 0.0039 (272) | 0.1634 (350) | 0.0006 (8) |
| builder/boom+perturb | other_months | 60 | 0.0000 (98) | 0.0000 (32) | 0.0000 (131) | 0.0000 (0) |
| builder/corridor | budget_month | 10 | 0.0486 (593) | 0.0356 (274) | 0.1044 (930) | 0.0006 (7) |
| builder/corridor | other_months | 105 | 0.0000 (36) | 0.0000 (10) | 0.0000 (40) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 1 | 0.0063 (52) | 0.0025 (21) | 0.0158 (131) | 0.0005 (4) |
| builder/corridor+perturb | other_months | 46 | 0.0000 (79) | 0.0000 (10) | 0.0000 (394) | 0.0000 (0) |
| builder/frugal | budget_month | 13 | 0.0139 (227) | 0.0109 (165) | 0.0309 (355) | 0.0004 (8) |
| builder/frugal | other_months | 95 | 0.0000 (78) | 0.0000 (25) | 0.0000 (132) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 4 | 0.1582 (1890) | 0.0679 (342) | 0.2945 (1474) | 0.0022 (13) |
| builder/frugal+perturb | other_months | 35 | 0.0000 (63) | 0.0000 (35) | 0.0000 (122) | 0.0000 (0) |
| builder/grid | budget_month | 11 | 0.0829 (419) | 0.0585 (292) | 0.0370 (469) | 0.0024 (9) |
| builder/grid | other_months | 131 | 0.0000 (138) | 0.0000 (58) | 0.0000 (300) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 10 | 0.0232 (509) | 0.0021 (224) | 0.0397 (376) | 0.0009 (11) |
| builder/grid+perturb | other_months | 71 | 0.0000 (90) | 0.0000 (45) | 0.0000 (183) | 0.0000 (0) |
| builder/industry | budget_month | 7 | 0.0421 (332) | 0.0079 (84) | 0.0432 (412) | 0.0006 (11) |
| builder/industry | other_months | 84 | 0.0000 (40) | 0.0000 (24) | 0.0000 (192) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 6 | 0.0300 (273) | 0.0210 (143) | 0.0663 (218) | 0.0010 (12) |
| builder/industry+perturb | other_months | 42 | 0.0000 (31) | 0.0000 (27) | 0.0000 (118) | 0.0000 (0) |
| builder/satellite | budget_month | 7 | 0.0138 (379) | 0.0083 (143) | 0.0454 (552) | 0.0006 (9) |
| builder/satellite | other_months | 80 | 0.0000 (61) | 0.0000 (27) | 0.0000 (229) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 5 | 0.0366 (810) | 0.0260 (638) | 0.0699 (1852) | 0.0010 (21) |
| builder/satellite+perturb | other_months | 55 | 0.0000 (87) | 0.0000 (59) | 0.0000 (252) | 0.0000 (0) |
| builder/transit | budget_month | 11 | 0.0817 (443) | 0.0668 (309) | 0.0765 (726) | 0.0007 (6) |
| builder/transit | other_months | 68 | 0.0000 (55) | 0.0000 (26) | 0.0000 (194) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 4 | 0.0175 (69) | 0.0407 (358) | 0.2732 (1423) | 0.0020 (14) |
| builder/transit+perturb | other_months | 29 | 0.0000 (101) | 0.0000 (95) | 0.0000 (353) | 0.0000 (0) |
| noop | budget_month | 12 | 0.0101 (228) | 0.0038 (89) | 0.0171 (319) | 0.0004 (11) |
| noop | other_months | 140 | 0.0000 (12) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 4 | 0.0212 (345) | 0.0127 (454) | 0.0491 (666) | 0.0006 (12) |
| noop+perturb | other_months | 52 | 0.0000 (33) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 21 | 0.0257 (523) | 0.0147 (261) | 0.0433 (526) | 0.0012 (11) |
| random/sprinkle | other_months | 132 | 0.0116 (246) | 0.0022 (130) | 0.0035 (84) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 7 | 0.0078 (390) | 0.0215 (385) | 0.0625 (1052) | 0.0004 (12) |
| random/sprinkle+perturb | other_months | 84 | 0.0034 (165) | 0.0020 (84) | 0.0017 (93) | 0.0000 (0) |
| random/uniform | budget_month | 13 | 0.8655 (864) | 0.0890 (494) | 0.4583 (663) | 0.0007 (7) |
| random/uniform | other_months | 150 | 0.0000 (328) | 0.0000 (227) | 0.0000 (327) | 0.0000 (0) |
| random/uniform+perturb | budget_month | 4 | 0.0378 (266) | 0.0471 (134) | 0.0000 (247) | 0.0000 (2) |
| random/uniform+perturb | other_months | 43 | 0.0000 (171) | 0.0000 (152) | 0.0000 (186) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 500 | 0.1092 (1817) | 0.3785 (5714) | 0.0026 (37) |
| budget_sweep | 30 | 0.0287 (1069) | 0.0293 (980) | 0.0010 (37) |
| budget_sweep+perturb | 24 | 0.0331 (1160) | 0.0338 (1095) | 0.0009 (45) |
| builder/boom | 23 | 0.6153 (1954) | 6.1942 (9915) | 0.0023 (24) |
| builder/boom+perturb | 15 | 0.9056 (3242) | 4.8241 (12660) | 0.0070 (47) |
| builder/corridor | 24 | 0.2589 (1441) | 0.8689 (5333) | 0.0041 (34) |
| builder/corridor+perturb | 12 | 0.0620 (1756) | 0.2581 (6363) | 0.0049 (65) |
| builder/frugal | 24 | 0.1500 (2433) | 0.3679 (5242) | 0.0033 (45) |
| builder/frugal+perturb | 8 | 0.1089 (1650) | 0.4315 (3823) | 0.0017 (28) |
| builder/grid | 36 | 0.1294 (2046) | 0.6446 (7643) | 0.0041 (41) |
| builder/grid+perturb | 24 | 0.1733 (1925) | 0.5656 (8538) | 0.0032 (36) |
| builder/industry | 27 | 0.0786 (1057) | 0.5414 (4781) | 0.0027 (36) |
| builder/industry+perturb | 9 | 0.2225 (1468) | 1.5478 (6997) | 0.0062 (26) |
| builder/satellite | 33 | 0.2781 (1210) | 3.0552 (8084) | 0.0044 (26) |
| builder/satellite+perturb | 11 | 0.4287 (1940) | 2.9588 (10470) | 0.0029 (29) |
| builder/transit | 24 | 0.1112 (1501) | 0.6405 (7723) | 0.0023 (31) |
| builder/transit+perturb | 8 | 0.6655 (1887) | 3.9967 (9832) | 0.0127 (56) |
| noop | 34 | 0.0237 (496) | 0.0431 (545) | 0.0016 (32) |
| noop+perturb | 14 | 0.0215 (465) | 0.0284 (370) | 0.0017 (39) |
| random/sprinkle | 47 | 0.0933 (1425) | 0.1507 (1705) | 0.0018 (35) |
| random/sprinkle+perturb | 23 | 0.0938 (1301) | 0.1561 (1742) | 0.0015 (39) |
| random/uniform | 42 | 1.0000 (4342) | 3.2055 (10422) | 0.0057 (40) |
| random/uniform+perturb | 8 | 1.0815 (6367) | 5.5170 (15375) | 0.0024 (44) |
