# Funds error split: pilot2_50m_samples_000600064_dec-b

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 179 | 0.0463 (641) | 0.0267 (414) | 0.0500 (647) | 0.0007 (10) |
| all | other_months | 1821 | 0.0000 (165) | 0.0000 (110) | 0.0000 (153) | 0.0000 (0) |
| budget_sweep | budget_month | 9 | 0.0404 (993) | 0.0287 (758) | 0.0244 (886) | 0.0010 (17) |
| budget_sweep | other_months | 160 | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 6 | 0.0452 (1194) | 0.0507 (982) | 0.0665 (1559) | 0.0002 (8) |
| budget_sweep+perturb | other_months | 73 | 0.0000 (1) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 11 | 0.0118 (77) | 0.0494 (65) | 0.4194 (280) | 0.0000 (3) |
| builder/boom | other_months | 86 | 0.0000 (246) | 0.0000 (160) | 0.0000 (318) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 3 | 0.0043 (108) | 0.0035 (106) | 0.1634 (350) | 0.0006 (8) |
| builder/boom+perturb | other_months | 60 | 0.0000 (51) | 0.0000 (91) | 0.0000 (131) | 0.0000 (0) |
| builder/corridor | budget_month | 10 | 0.0734 (569) | 0.0393 (275) | 0.1044 (930) | 0.0006 (7) |
| builder/corridor | other_months | 105 | 0.0000 (65) | 0.0000 (6) | 0.0000 (40) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 1 | 0.0134 (111) | 0.0073 (60) | 0.0158 (131) | 0.0005 (4) |
| builder/corridor+perturb | other_months | 46 | 0.0000 (436) | 0.0000 (245) | 0.0000 (394) | 0.0000 (0) |
| builder/frugal | budget_month | 13 | 0.0497 (476) | 0.0144 (224) | 0.0309 (355) | 0.0004 (8) |
| builder/frugal | other_months | 95 | 0.0000 (136) | 0.0000 (67) | 0.0000 (132) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 4 | 0.2694 (1551) | 0.1932 (1260) | 0.2945 (1474) | 0.0022 (13) |
| builder/frugal+perturb | other_months | 35 | 0.0000 (47) | 0.0000 (83) | 0.0000 (122) | 0.0000 (0) |
| builder/grid | budget_month | 11 | 0.0681 (528) | 0.0422 (321) | 0.0370 (469) | 0.0024 (9) |
| builder/grid | other_months | 131 | 0.0000 (307) | 0.0000 (245) | 0.0000 (300) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 10 | 0.0230 (477) | 0.0106 (152) | 0.0397 (376) | 0.0009 (11) |
| builder/grid+perturb | other_months | 71 | 0.0000 (215) | 0.0000 (143) | 0.0000 (183) | 0.0000 (0) |
| builder/industry | budget_month | 7 | 0.0367 (627) | 0.0218 (207) | 0.0432 (412) | 0.0006 (11) |
| builder/industry | other_months | 84 | 0.0000 (152) | 0.0000 (129) | 0.0000 (192) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 6 | 0.1622 (433) | 0.0186 (148) | 0.0663 (218) | 0.0010 (12) |
| builder/industry+perturb | other_months | 42 | 0.0000 (81) | 0.0000 (24) | 0.0000 (118) | 0.0000 (0) |
| builder/satellite | budget_month | 7 | 0.0384 (386) | 0.0409 (357) | 0.0454 (552) | 0.0006 (9) |
| builder/satellite | other_months | 80 | 0.0000 (106) | 0.0000 (43) | 0.0000 (229) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 5 | 0.0346 (1401) | 0.0287 (1048) | 0.0699 (1852) | 0.0010 (21) |
| builder/satellite+perturb | other_months | 55 | 0.0000 (305) | 0.0000 (176) | 0.0000 (252) | 0.0000 (0) |
| builder/transit | budget_month | 11 | 0.1175 (518) | 0.0787 (419) | 0.0765 (726) | 0.0007 (6) |
| builder/transit | other_months | 68 | 0.0000 (149) | 0.0000 (141) | 0.0000 (194) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 4 | 0.2355 (1394) | 0.0874 (685) | 0.2732 (1423) | 0.0020 (14) |
| builder/transit+perturb | other_months | 29 | 0.0000 (383) | 0.0000 (245) | 0.0000 (353) | 0.0000 (0) |
| noop | budget_month | 12 | 0.0070 (173) | 0.0064 (236) | 0.0171 (319) | 0.0004 (11) |
| noop | other_months | 140 | 0.0000 (1) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 4 | 0.1504 (2152) | 0.0477 (590) | 0.0491 (666) | 0.0006 (12) |
| noop+perturb | other_months | 52 | 0.0000 (1) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 21 | 0.0448 (399) | 0.0271 (390) | 0.0433 (526) | 0.0012 (11) |
| random/sprinkle | other_months | 132 | 0.0013 (226) | 0.0008 (109) | 0.0035 (84) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 7 | 0.0161 (864) | 0.0072 (823) | 0.0625 (1052) | 0.0004 (12) |
| random/sprinkle+perturb | other_months | 84 | 0.0009 (133) | 0.0008 (119) | 0.0017 (93) | 0.0000 (0) |
| random/uniform | budget_month | 13 | 0.5038 (1104) | 0.0823 (549) | 0.4583 (663) | 0.0007 (7) |
| random/uniform | other_months | 150 | 0.0000 (432) | 0.0000 (271) | 0.0000 (327) | 0.0000 (0) |
| random/uniform+perturb | budget_month | 4 | 0.0986 (330) | 0.0611 (218) | 0.0000 (247) | 0.0000 (2) |
| random/uniform+perturb | other_months | 43 | 0.0000 (241) | 0.0000 (250) | 0.0000 (186) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 500 | 0.2908 (3561) | 0.3785 (5714) | 0.0026 (37) |
| budget_sweep | 30 | 0.0413 (1418) | 0.0293 (980) | 0.0010 (37) |
| budget_sweep+perturb | 24 | 0.0307 (1258) | 0.0338 (1095) | 0.0009 (45) |
| builder/boom | 23 | 1.0000 (4318) | 6.1942 (9915) | 0.0023 (24) |
| builder/boom+perturb | 15 | 1.4338 (6277) | 4.8241 (12660) | 0.0070 (47) |
| builder/corridor | 24 | 0.4126 (2431) | 0.8689 (5333) | 0.0041 (34) |
| builder/corridor+perturb | 12 | 0.1854 (3273) | 0.2581 (6363) | 0.0049 (65) |
| builder/frugal | 24 | 0.2576 (3508) | 0.3679 (5242) | 0.0033 (45) |
| builder/frugal+perturb | 8 | 0.2224 (2745) | 0.4315 (3823) | 0.0017 (28) |
| builder/grid | 36 | 0.3279 (3552) | 0.6446 (7643) | 0.0041 (41) |
| builder/grid+perturb | 24 | 0.3660 (4638) | 0.5656 (8538) | 0.0032 (36) |
| builder/industry | 27 | 0.1995 (2196) | 0.5414 (4781) | 0.0027 (36) |
| builder/industry+perturb | 9 | 0.6215 (3433) | 1.5478 (6997) | 0.0062 (26) |
| builder/satellite | 33 | 0.9798 (3438) | 3.0552 (8084) | 0.0044 (26) |
| builder/satellite+perturb | 11 | 0.6427 (3625) | 2.9588 (10470) | 0.0029 (29) |
| builder/transit | 24 | 0.3968 (3725) | 0.6405 (7723) | 0.0023 (31) |
| builder/transit+perturb | 8 | 1.6205 (5997) | 3.9967 (9832) | 0.0127 (56) |
| noop | 34 | 0.0208 (675) | 0.0431 (545) | 0.0016 (32) |
| noop+perturb | 14 | 0.0274 (730) | 0.0284 (370) | 0.0017 (39) |
| random/sprinkle | 47 | 0.3490 (4639) | 0.1507 (1705) | 0.0018 (35) |
| random/sprinkle+perturb | 23 | 0.3169 (4979) | 0.1561 (1742) | 0.0015 (39) |
| random/uniform | 42 | 1.0000 (5898) | 3.2055 (10422) | 0.0057 (40) |
| random/uniform+perturb | 8 | 1.1716 (9611) | 5.5170 (15375) | 0.0024 (44) |
