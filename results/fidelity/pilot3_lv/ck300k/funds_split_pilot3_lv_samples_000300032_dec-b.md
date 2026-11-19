# Funds error split: pilot3_lv_samples_000300032_dec-b

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 179 | 0.0816 (822) | 0.0272 (386) | 0.0500 (647) | 0.0007 (10) |
| all | other_months | 1821 | 0.0000 (156) | 0.0000 (47) | 0.0000 (153) | 0.0000 (0) |
| budget_sweep | budget_month | 9 | 0.0590 (978) | 0.0272 (570) | 0.0244 (886) | 0.0010 (17) |
| budget_sweep | other_months | 160 | 0.0000 (13) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 6 | 0.0428 (1526) | 0.0739 (1360) | 0.0665 (1559) | 0.0002 (8) |
| budget_sweep+perturb | other_months | 73 | 0.0000 (15) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 11 | 0.1286 (235) | 0.0979 (160) | 0.4194 (280) | 0.0000 (3) |
| builder/boom | other_months | 86 | 0.0000 (166) | 0.0000 (47) | 0.0000 (318) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 3 | 0.1080 (566) | 0.0330 (336) | 0.1634 (350) | 0.0006 (8) |
| builder/boom+perturb | other_months | 60 | 0.0000 (78) | 0.0000 (24) | 0.0000 (131) | 0.0000 (0) |
| builder/corridor | budget_month | 10 | 0.0935 (1031) | 0.0269 (203) | 0.1044 (930) | 0.0006 (7) |
| builder/corridor | other_months | 105 | 0.0000 (59) | 0.0000 (8) | 0.0000 (40) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 1 | 0.0399 (330) | 0.0181 (150) | 0.0158 (131) | 0.0005 (4) |
| builder/corridor+perturb | other_months | 46 | 0.0000 (137) | 0.0000 (20) | 0.0000 (394) | 0.0000 (0) |
| builder/frugal | budget_month | 13 | 0.1554 (1006) | 0.0152 (222) | 0.0309 (355) | 0.0004 (8) |
| builder/frugal | other_months | 95 | 0.0000 (148) | 0.0000 (39) | 0.0000 (132) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 4 | 0.2855 (1490) | 0.0475 (752) | 0.2945 (1474) | 0.0022 (13) |
| builder/frugal+perturb | other_months | 35 | 0.0000 (193) | 0.0000 (18) | 0.0000 (122) | 0.0000 (0) |
| builder/grid | budget_month | 11 | 0.0935 (628) | 0.0831 (247) | 0.0370 (469) | 0.0024 (9) |
| builder/grid | other_months | 131 | 0.0000 (191) | 0.0000 (70) | 0.0000 (300) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 10 | 0.0560 (639) | 0.0219 (308) | 0.0397 (376) | 0.0009 (11) |
| builder/grid+perturb | other_months | 71 | 0.0000 (128) | 0.0000 (31) | 0.0000 (183) | 0.0000 (0) |
| builder/industry | budget_month | 7 | 0.0536 (586) | 0.0274 (299) | 0.0432 (412) | 0.0006 (11) |
| builder/industry | other_months | 84 | 0.0000 (80) | 0.0000 (20) | 0.0000 (192) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 6 | 0.0686 (258) | 0.0379 (224) | 0.0663 (218) | 0.0010 (12) |
| builder/industry+perturb | other_months | 42 | 0.0000 (85) | 0.0000 (13) | 0.0000 (118) | 0.0000 (0) |
| builder/satellite | budget_month | 7 | 0.0521 (677) | 0.0146 (272) | 0.0454 (552) | 0.0006 (9) |
| builder/satellite | other_months | 80 | 0.0000 (142) | 0.0000 (22) | 0.0000 (229) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 5 | 0.0617 (1179) | 0.0067 (1007) | 0.0699 (1852) | 0.0010 (21) |
| builder/satellite+perturb | other_months | 55 | 0.0000 (124) | 0.0000 (40) | 0.0000 (252) | 0.0000 (0) |
| builder/transit | budget_month | 11 | 0.2786 (904) | 0.0666 (564) | 0.0765 (726) | 0.0007 (6) |
| builder/transit | other_months | 68 | 0.0000 (108) | 0.0000 (41) | 0.0000 (194) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 4 | 0.1144 (532) | 0.0112 (82) | 0.2732 (1423) | 0.0020 (14) |
| builder/transit+perturb | other_months | 29 | 0.0000 (157) | 0.0000 (44) | 0.0000 (353) | 0.0000 (0) |
| noop | budget_month | 12 | 0.0205 (848) | 0.0191 (259) | 0.0171 (319) | 0.0004 (11) |
| noop | other_months | 140 | 0.0000 (33) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 4 | 0.1120 (2124) | 0.0211 (406) | 0.0491 (666) | 0.0006 (12) |
| noop+perturb | other_months | 52 | 0.0000 (34) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 21 | 0.0601 (821) | 0.0230 (299) | 0.0433 (526) | 0.0012 (11) |
| random/sprinkle | other_months | 132 | 0.0174 (375) | 0.0024 (63) | 0.0035 (84) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 7 | 0.0788 (611) | 0.0135 (387) | 0.0625 (1052) | 0.0004 (12) |
| random/sprinkle+perturb | other_months | 84 | 0.0032 (249) | 0.0013 (69) | 0.0017 (93) | 0.0000 (0) |
| random/uniform | budget_month | 13 | 0.5799 (769) | 0.4928 (627) | 0.4583 (663) | 0.0007 (7) |
| random/uniform | other_months | 150 | 0.0000 (438) | 0.0000 (201) | 0.0000 (327) | 0.0000 (0) |
| random/uniform+perturb | budget_month | 4 | 447.0000 (867) | 0.0366 (114) | 0.0000 (247) | 0.0000 (2) |
| random/uniform+perturb | other_months | 43 | 0.0000 (286) | 0.0000 (207) | 0.0000 (186) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 500 | 0.1531 (2064) | 0.3785 (5714) | 0.0026 (37) |
| budget_sweep | 30 | 0.0507 (1566) | 0.0293 (980) | 0.0010 (37) |
| budget_sweep+perturb | 24 | 0.0631 (1484) | 0.0338 (1095) | 0.0009 (45) |
| builder/boom | 23 | 0.8031 (2284) | 6.1942 (9915) | 0.0023 (24) |
| builder/boom+perturb | 15 | 0.9261 (3290) | 4.8241 (12660) | 0.0070 (47) |
| builder/corridor | 24 | 0.2591 (1428) | 0.8689 (5333) | 0.0041 (34) |
| builder/corridor+perturb | 12 | 0.0989 (2140) | 0.2581 (6363) | 0.0049 (65) |
| builder/frugal | 24 | 0.1769 (2421) | 0.3679 (5242) | 0.0033 (45) |
| builder/frugal+perturb | 8 | 0.1267 (2024) | 0.4315 (3823) | 0.0017 (28) |
| builder/grid | 36 | 0.2404 (2119) | 0.6446 (7643) | 0.0041 (41) |
| builder/grid+perturb | 24 | 0.2201 (2063) | 0.5656 (8538) | 0.0032 (36) |
| builder/industry | 27 | 0.1189 (1547) | 0.5414 (4781) | 0.0027 (36) |
| builder/industry+perturb | 9 | 0.3057 (1632) | 1.5478 (6997) | 0.0062 (26) |
| builder/satellite | 33 | 0.3739 (1338) | 3.0552 (8084) | 0.0044 (26) |
| builder/satellite+perturb | 11 | 0.2089 (1653) | 2.9588 (10470) | 0.0029 (29) |
| builder/transit | 24 | 0.2028 (2148) | 0.6405 (7723) | 0.0023 (31) |
| builder/transit+perturb | 8 | 0.6922 (2365) | 3.9967 (9832) | 0.0127 (56) |
| noop | 34 | 0.0443 (1007) | 0.0431 (545) | 0.0016 (32) |
| noop+perturb | 14 | 0.0351 (935) | 0.0284 (370) | 0.0017 (39) |
| random/sprinkle | 47 | 0.1071 (1739) | 0.1507 (1705) | 0.0018 (35) |
| random/sprinkle+perturb | 23 | 0.1006 (1664) | 0.1561 (1742) | 0.0015 (39) |
| random/uniform | 42 | 0.9781 (4151) | 3.2055 (10422) | 0.0057 (40) |
| random/uniform+perturb | 8 | 1.0000 (7062) | 5.5170 (15375) | 0.0024 (44) |
