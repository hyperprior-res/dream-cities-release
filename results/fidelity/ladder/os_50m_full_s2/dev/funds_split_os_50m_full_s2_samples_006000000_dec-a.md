# Funds error split: os_50m_full_s2_samples_006000000_dec-a

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 179 | 0.0044 (58) | 0.0028 (48) | 0.0500 (647) | 0.0007 (10) |
| all | other_months | 1821 | 0.0000 (43) | 0.0000 (16) | 0.0000 (153) | 0.0000 (0) |
| source: state_reading | budget_month | 145 | 0.0046 (61) | 0.0032 (50) | 0.0504 (658) | 0.0007 (9) |
| source: state_reading | other_months | 1371 | 0.0000 (41) | 0.0000 (14) | 0.0000 (168) | 0.0000 (0) |
| source: open_loop | budget_month | 34 | 0.0030 (47) | 0.0020 (37) | 0.0482 (601) | 0.0006 (11) |
| source: open_loop | other_months | 450 | 0.0000 (48) | 0.0000 (21) | 0.0000 (109) | 0.0000 (0) |
| budget_sweep | budget_month | 9 | 0.0010 (33) | 0.0012 (36) | 0.0244 (886) | 0.0010 (17) |
| budget_sweep | other_months | 160 | 0.0000 (14) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 6 | 0.0005 (23) | 0.0007 (27) | 0.0665 (1559) | 0.0002 (8) |
| budget_sweep+perturb | other_months | 73 | 0.0000 (19) | 0.0000 (3) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 11 | 0.0155 (51) | 0.0045 (35) | 0.4194 (280) | 0.0000 (3) |
| builder/boom | other_months | 86 | 0.0000 (41) | 0.0000 (10) | 0.0000 (318) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 3 | 0.0020 (57) | 0.0012 (48) | 0.1634 (350) | 0.0006 (8) |
| builder/boom+perturb | other_months | 60 | 0.0000 (23) | 0.0000 (4) | 0.0000 (131) | 0.0000 (0) |
| builder/corridor | budget_month | 10 | 0.0089 (92) | 0.0032 (47) | 0.1044 (930) | 0.0006 (7) |
| builder/corridor | other_months | 105 | 0.0000 (18) | 0.0000 (4) | 0.0000 (40) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 1 | 0.0059 (49) | 0.0006 (5) | 0.0158 (131) | 0.0005 (4) |
| builder/corridor+perturb | other_months | 46 | 0.0000 (31) | 0.0000 (13) | 0.0000 (394) | 0.0000 (0) |
| builder/frugal | budget_month | 13 | 0.0041 (62) | 0.0021 (25) | 0.0309 (355) | 0.0004 (8) |
| builder/frugal | other_months | 95 | 0.0000 (36) | 0.0000 (8) | 0.0000 (132) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 4 | 0.0139 (62) | 0.0078 (62) | 0.2945 (1474) | 0.0022 (13) |
| builder/frugal+perturb | other_months | 35 | 0.0000 (27) | 0.0000 (14) | 0.0000 (122) | 0.0000 (0) |
| builder/grid | budget_month | 11 | 0.0065 (53) | 0.0069 (54) | 0.0370 (469) | 0.0024 (9) |
| builder/grid | other_months | 131 | 0.0000 (37) | 0.0000 (16) | 0.0000 (300) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 10 | 0.0027 (85) | 0.0011 (29) | 0.0397 (376) | 0.0009 (11) |
| builder/grid+perturb | other_months | 71 | 0.0000 (20) | 0.0000 (14) | 0.0000 (183) | 0.0000 (0) |
| builder/industry | budget_month | 7 | 0.0027 (29) | 0.0011 (19) | 0.0432 (412) | 0.0006 (11) |
| builder/industry | other_months | 84 | 0.0000 (21) | 0.0000 (14) | 0.0000 (192) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 6 | 0.0037 (18) | 0.0025 (16) | 0.0663 (218) | 0.0010 (12) |
| builder/industry+perturb | other_months | 42 | 0.0000 (14) | 0.0000 (13) | 0.0000 (118) | 0.0000 (0) |
| builder/satellite | budget_month | 7 | 0.0028 (34) | 0.0044 (63) | 0.0454 (552) | 0.0006 (9) |
| builder/satellite | other_months | 80 | 0.0000 (26) | 0.0000 (7) | 0.0000 (229) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 5 | 0.0012 (122) | 0.0016 (96) | 0.0699 (1852) | 0.0010 (21) |
| builder/satellite+perturb | other_months | 55 | 0.0000 (58) | 0.0000 (5) | 0.0000 (252) | 0.0000 (0) |
| builder/transit | budget_month | 11 | 0.0153 (62) | 0.0151 (58) | 0.0765 (726) | 0.0007 (6) |
| builder/transit | other_months | 68 | 0.0000 (36) | 0.0000 (12) | 0.0000 (194) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 4 | 0.0002 (5) | 0.0036 (20) | 0.2732 (1423) | 0.0020 (14) |
| builder/transit+perturb | other_months | 29 | 0.0000 (70) | 0.0000 (12) | 0.0000 (353) | 0.0000 (0) |
| noop | budget_month | 12 | 0.0011 (26) | 0.0010 (18) | 0.0171 (319) | 0.0004 (11) |
| noop | other_months | 140 | 0.0000 (6) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 4 | 0.0125 (166) | 0.0117 (179) | 0.0491 (666) | 0.0006 (12) |
| noop+perturb | other_months | 52 | 0.0000 (18) | 0.0000 (1) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 21 | 0.0046 (66) | 0.0052 (67) | 0.0433 (526) | 0.0012 (11) |
| random/sprinkle | other_months | 132 | 0.0020 (79) | 0.0004 (27) | 0.0035 (84) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 7 | 0.0059 (89) | 0.0044 (72) | 0.0625 (1052) | 0.0004 (12) |
| random/sprinkle+perturb | other_months | 84 | 0.0017 (109) | 0.0001 (33) | 0.0017 (93) | 0.0000 (0) |
| random/uniform | budget_month | 13 | 0.0526 (75) | 0.0556 (54) | 0.4583 (663) | 0.0007 (7) |
| random/uniform | other_months | 150 | 0.0000 (124) | 0.0000 (64) | 0.0000 (327) | 0.0000 (0) |
| random/uniform+perturb | budget_month | 4 | 0.0000 (5) | 0.0000 (39) | 0.0000 (247) | 0.0000 (2) |
| random/uniform+perturb | other_months | 43 | 0.0000 (96) | 0.0000 (56) | 0.0000 (186) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 500 | 0.0392 (538) | 0.3785 (5714) | 0.0026 (37) |
| source: state_reading | 394 | 0.0425 (498) | 0.4654 (6019) | 0.0028 (37) |
| source: open_loop | 106 | 0.0243 (685) | 0.0615 (4581) | 0.0019 (36) |
| budget_sweep | 30 | 0.0086 (320) | 0.0293 (980) | 0.0010 (37) |
| budget_sweep+perturb | 24 | 0.0146 (339) | 0.0338 (1095) | 0.0009 (45) |
| builder/boom | 23 | 0.1157 (444) | 6.1942 (9915) | 0.0023 (24) |
| builder/boom+perturb | 15 | 0.1427 (667) | 4.8241 (12660) | 0.0070 (47) |
| builder/corridor | 24 | 0.0561 (403) | 0.8689 (5333) | 0.0041 (34) |
| builder/corridor+perturb | 12 | 0.0308 (558) | 0.2581 (6363) | 0.0049 (65) |
| builder/frugal | 24 | 0.0523 (598) | 0.3679 (5242) | 0.0033 (45) |
| builder/frugal+perturb | 8 | 0.0267 (439) | 0.4315 (3823) | 0.0017 (28) |
| builder/grid | 36 | 0.0440 (543) | 0.6446 (7643) | 0.0041 (41) |
| builder/grid+perturb | 24 | 0.0480 (479) | 0.5656 (8538) | 0.0032 (36) |
| builder/industry | 27 | 0.0311 (354) | 0.5414 (4781) | 0.0027 (36) |
| builder/industry+perturb | 9 | 0.0454 (307) | 1.5478 (6997) | 0.0062 (26) |
| builder/satellite | 33 | 0.0672 (298) | 3.0552 (8084) | 0.0044 (26) |
| builder/satellite+perturb | 11 | 0.0454 (522) | 2.9588 (10470) | 0.0029 (29) |
| builder/transit | 24 | 0.0359 (512) | 0.6405 (7723) | 0.0023 (31) |
| builder/transit+perturb | 8 | 0.1926 (365) | 3.9967 (9832) | 0.0127 (56) |
| noop | 34 | 0.0099 (282) | 0.0431 (545) | 0.0016 (32) |
| noop+perturb | 14 | 0.0113 (322) | 0.0284 (370) | 0.0017 (39) |
| random/sprinkle | 47 | 0.0352 (619) | 0.1507 (1705) | 0.0018 (35) |
| random/sprinkle+perturb | 23 | 0.0420 (678) | 0.1561 (1742) | 0.0015 (39) |
| random/uniform | 42 | 0.3426 (1272) | 3.2055 (10422) | 0.0057 (40) |
| random/uniform+perturb | 8 | 0.3568 (1298) | 5.5170 (15375) | 0.0024 (44) |
