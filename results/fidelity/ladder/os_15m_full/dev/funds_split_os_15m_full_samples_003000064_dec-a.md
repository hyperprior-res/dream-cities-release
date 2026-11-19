# Funds error split: os_15m_full_samples_003000064_dec-a

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 179 | 0.0058 (104) | 0.0033 (54) | 0.0500 (647) | 0.0007 (10) |
| all | other_months | 1821 | 0.0000 (58) | 0.0000 (15) | 0.0000 (153) | 0.0000 (0) |
| source: state_reading | budget_month | 145 | 0.0064 (109) | 0.0036 (57) | 0.0504 (658) | 0.0007 (9) |
| source: state_reading | other_months | 1371 | 0.0000 (60) | 0.0000 (9) | 0.0000 (168) | 0.0000 (0) |
| source: open_loop | budget_month | 34 | 0.0046 (82) | 0.0018 (44) | 0.0482 (601) | 0.0006 (11) |
| source: open_loop | other_months | 450 | 0.0000 (51) | 0.0000 (32) | 0.0000 (109) | 0.0000 (0) |
| budget_sweep | budget_month | 9 | 0.0045 (80) | 0.0017 (34) | 0.0244 (886) | 0.0010 (17) |
| budget_sweep | other_months | 160 | 0.0000 (2) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 6 | 0.0025 (105) | 0.0036 (73) | 0.0665 (1559) | 0.0002 (8) |
| budget_sweep+perturb | other_months | 73 | 0.0000 (24) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 11 | 0.0263 (61) | 0.0222 (35) | 0.4194 (280) | 0.0000 (3) |
| builder/boom | other_months | 86 | 0.0000 (86) | 0.0000 (10) | 0.0000 (318) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 3 | 0.0030 (59) | 0.0043 (56) | 0.1634 (350) | 0.0006 (8) |
| builder/boom+perturb | other_months | 60 | 0.0000 (46) | 0.0000 (2) | 0.0000 (131) | 0.0000 (0) |
| builder/corridor | budget_month | 10 | 0.0098 (129) | 0.0032 (30) | 0.1044 (930) | 0.0006 (7) |
| builder/corridor | other_months | 105 | 0.0000 (24) | 0.0000 (2) | 0.0000 (40) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 1 | 0.0040 (33) | 0.0008 (7) | 0.0158 (131) | 0.0005 (4) |
| builder/corridor+perturb | other_months | 46 | 0.0000 (49) | 0.0000 (3) | 0.0000 (394) | 0.0000 (0) |
| builder/frugal | budget_month | 13 | 0.0064 (76) | 0.0027 (28) | 0.0309 (355) | 0.0004 (8) |
| builder/frugal | other_months | 95 | 0.0000 (33) | 0.0000 (5) | 0.0000 (132) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 4 | 0.0128 (73) | 0.0151 (64) | 0.2945 (1474) | 0.0022 (13) |
| builder/frugal+perturb | other_months | 35 | 0.0000 (70) | 0.0000 (5) | 0.0000 (122) | 0.0000 (0) |
| builder/grid | budget_month | 11 | 0.0119 (188) | 0.0079 (89) | 0.0370 (469) | 0.0024 (9) |
| builder/grid | other_months | 131 | 0.0000 (64) | 0.0000 (8) | 0.0000 (300) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 10 | 0.0025 (65) | 0.0022 (30) | 0.0397 (376) | 0.0009 (11) |
| builder/grid+perturb | other_months | 71 | 0.0000 (31) | 0.0000 (6) | 0.0000 (183) | 0.0000 (0) |
| builder/industry | budget_month | 7 | 0.0054 (29) | 0.0032 (27) | 0.0432 (412) | 0.0006 (11) |
| builder/industry | other_months | 84 | 0.0000 (38) | 0.0000 (3) | 0.0000 (192) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 6 | 0.0020 (9) | 0.0046 (15) | 0.0663 (218) | 0.0010 (12) |
| builder/industry+perturb | other_months | 42 | 0.0000 (43) | 0.0000 (4) | 0.0000 (118) | 0.0000 (0) |
| builder/satellite | budget_month | 7 | 0.0015 (28) | 0.0024 (25) | 0.0454 (552) | 0.0006 (9) |
| builder/satellite | other_months | 80 | 0.0000 (64) | 0.0000 (4) | 0.0000 (229) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 5 | 0.0020 (129) | 0.0030 (143) | 0.0699 (1852) | 0.0010 (21) |
| builder/satellite+perturb | other_months | 55 | 0.0000 (46) | 0.0000 (6) | 0.0000 (252) | 0.0000 (0) |
| builder/transit | budget_month | 11 | 0.0113 (117) | 0.0119 (63) | 0.0765 (726) | 0.0007 (6) |
| builder/transit | other_months | 68 | 0.0000 (58) | 0.0000 (5) | 0.0000 (194) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 4 | 0.0107 (61) | 0.0015 (12) | 0.2732 (1423) | 0.0020 (14) |
| builder/transit+perturb | other_months | 29 | 0.0000 (81) | 0.0000 (65) | 0.0000 (353) | 0.0000 (0) |
| noop | budget_month | 12 | 0.0009 (28) | 0.0007 (16) | 0.0171 (319) | 0.0004 (11) |
| noop | other_months | 140 | 0.0000 (8) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 4 | 0.0168 (330) | 0.0125 (268) | 0.0491 (666) | 0.0006 (12) |
| noop+perturb | other_months | 52 | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 21 | 0.0071 (160) | 0.0036 (66) | 0.0433 (526) | 0.0012 (11) |
| random/sprinkle | other_months | 132 | 0.0032 (124) | 0.0004 (17) | 0.0035 (84) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 7 | 0.0147 (199) | 0.0040 (85) | 0.0625 (1052) | 0.0004 (12) |
| random/sprinkle+perturb | other_months | 84 | 0.0015 (109) | 0.0005 (26) | 0.0017 (93) | 0.0000 (0) |
| random/uniform | budget_month | 13 | 0.0707 (133) | 0.0433 (78) | 0.4583 (663) | 0.0007 (7) |
| random/uniform | other_months | 150 | 0.0000 (143) | 0.0000 (95) | 0.0000 (327) | 0.0000 (0) |
| random/uniform+perturb | budget_month | 4 | 0.0000 (92) | 0.0000 (17) | 0.0000 (247) | 0.0000 (2) |
| random/uniform+perturb | other_months | 43 | 0.0000 (105) | 0.0000 (33) | 0.0000 (186) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 500 | 0.0560 (821) | 0.3785 (5714) | 0.0026 (37) |
| source: state_reading | 394 | 0.0646 (727) | 0.4654 (6019) | 0.0028 (37) |
| source: open_loop | 106 | 0.0184 (1169) | 0.0615 (4581) | 0.0019 (36) |
| budget_sweep | 30 | 0.0067 (297) | 0.0293 (980) | 0.0010 (37) |
| budget_sweep+perturb | 24 | 0.0142 (421) | 0.0338 (1095) | 0.0009 (45) |
| builder/boom | 23 | 0.1508 (594) | 6.1942 (9915) | 0.0023 (24) |
| builder/boom+perturb | 15 | 0.2102 (951) | 4.8241 (12660) | 0.0070 (47) |
| builder/corridor | 24 | 0.0750 (506) | 0.8689 (5333) | 0.0041 (34) |
| builder/corridor+perturb | 12 | 0.0389 (634) | 0.2581 (6363) | 0.0049 (65) |
| builder/frugal | 24 | 0.0556 (859) | 0.3679 (5242) | 0.0033 (45) |
| builder/frugal+perturb | 8 | 0.0611 (768) | 0.4315 (3823) | 0.0017 (28) |
| builder/grid | 36 | 0.0607 (637) | 0.6446 (7643) | 0.0041 (41) |
| builder/grid+perturb | 24 | 0.0839 (782) | 0.5656 (8538) | 0.0032 (36) |
| builder/industry | 27 | 0.0442 (566) | 0.5414 (4781) | 0.0027 (36) |
| builder/industry+perturb | 9 | 0.0624 (468) | 1.5478 (6997) | 0.0062 (26) |
| builder/satellite | 33 | 0.1325 (480) | 3.0552 (8084) | 0.0044 (26) |
| builder/satellite+perturb | 11 | 0.0818 (696) | 2.9588 (10470) | 0.0029 (29) |
| builder/transit | 24 | 0.0643 (558) | 0.6405 (7723) | 0.0023 (31) |
| builder/transit+perturb | 8 | 0.2943 (713) | 3.9967 (9832) | 0.0127 (56) |
| noop | 34 | 0.0054 (203) | 0.0431 (545) | 0.0016 (32) |
| noop+perturb | 14 | 0.0088 (245) | 0.0284 (370) | 0.0017 (39) |
| random/sprinkle | 47 | 0.0796 (997) | 0.1507 (1705) | 0.0018 (35) |
| random/sprinkle+perturb | 23 | 0.0722 (972) | 0.1561 (1742) | 0.0015 (39) |
| random/uniform | 42 | 0.7318 (2574) | 3.2055 (10422) | 0.0057 (40) |
| random/uniform+perturb | 8 | 0.8772 (3194) | 5.5170 (15375) | 0.0024 (44) |
