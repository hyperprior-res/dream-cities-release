# Funds error split: os_15m_small_samples_006000000_dec-a

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 182 | 0.0043 (108) | 0.0041 (79) | 0.0559 (713) | 0.0006 (10) |
| all | other_months | 1818 | 0.0000 (61) | 0.0000 (26) | 0.0000 (156) | 0.0000 (0) |
| source: state_reading | budget_month | 132 | 0.0039 (86) | 0.0037 (65) | 0.0583 (665) | 0.0006 (9) |
| source: state_reading | other_months | 1349 | 0.0000 (53) | 0.0000 (15) | 0.0000 (173) | 0.0000 (0) |
| source: open_loop | budget_month | 50 | 0.0083 (164) | 0.0060 (115) | 0.0422 (838) | 0.0007 (13) |
| source: open_loop | other_months | 469 | 0.0000 (82) | 0.0000 (56) | 0.0000 (106) | 0.0000 (0) |
| budget_sweep | budget_month | 19 | 0.0064 (143) | 0.0024 (122) | 0.0243 (873) | 0.0007 (14) |
| budget_sweep | other_months | 177 | 0.0000 (14) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 7 | 0.0046 (112) | 0.0042 (109) | 0.0462 (1452) | 0.0000 (13) |
| budget_sweep+perturb | other_months | 67 | 0.0000 (11) | 0.0000 (2) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 9 | 0.0242 (166) | 0.0087 (57) | 0.5485 (1546) | 0.0037 (9) |
| builder/boom | other_months | 92 | 0.0000 (26) | 0.0000 (7) | 0.0000 (181) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 8 | 0.0000 (21) | 0.0000 (15) | 0.5590 (328) | 0.0000 (2) |
| builder/boom+perturb | other_months | 47 | 0.0000 (29) | 0.0000 (10) | 0.0000 (181) | 0.0000 (0) |
| builder/corridor | budget_month | 8 | 0.0032 (88) | 0.0026 (43) | 0.0482 (708) | 0.0006 (17) |
| builder/corridor | other_months | 99 | 0.0000 (40) | 0.0000 (16) | 0.0000 (170) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 6 | 0.0020 (30) | 0.0025 (43) | 0.0625 (320) | 0.0009 (8) |
| builder/corridor+perturb | other_months | 27 | 0.0000 (49) | 0.0000 (2) | 0.0000 (208) | 0.0000 (0) |
| builder/frugal | budget_month | 13 | 0.0047 (70) | 0.0037 (78) | 0.0696 (714) | 0.0007 (9) |
| builder/frugal | other_months | 114 | 0.0000 (41) | 0.0000 (8) | 0.0000 (157) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 8 | 0.0111 (125) | 0.0054 (53) | 0.0783 (718) | 0.0024 (12) |
| builder/frugal+perturb | other_months | 46 | 0.0000 (17) | 0.0000 (7) | 0.0000 (93) | 0.0000 (0) |
| builder/grid | budget_month | 12 | 0.0121 (156) | 0.0184 (151) | 0.0799 (1094) | 0.0017 (16) |
| builder/grid | other_months | 135 | 0.0000 (49) | 0.0000 (13) | 0.0000 (247) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 9 | 0.0069 (88) | 0.0069 (78) | 0.0739 (380) | 0.0007 (7) |
| builder/grid+perturb | other_months | 63 | 0.0000 (26) | 0.0000 (13) | 0.0000 (287) | 0.0000 (0) |
| builder/industry | budget_month | 4 | 0.0101 (67) | 0.0119 (61) | 0.2742 (371) | 0.0006 (2) |
| builder/industry | other_months | 67 | 0.0000 (31) | 0.0000 (5) | 0.0000 (96) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 1 | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| builder/industry+perturb | other_months | 43 | 0.0000 (8) | 0.0000 (1) | 0.0000 (23) | 0.0000 (0) |
| builder/satellite | budget_month | 8 | 0.0014 (41) | 0.0014 (32) | 0.0566 (481) | 0.0008 (8) |
| builder/satellite | other_months | 90 | 0.0000 (40) | 0.0000 (4) | 0.0000 (287) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 2 | 0.0006 (16) | 0.0008 (20) | 716.5037 (814) | 0.0001 (3) |
| builder/satellite+perturb | other_months | 63 | 0.0000 (117) | 0.0000 (25) | 0.0000 (363) | 0.0000 (0) |
| builder/transit | budget_month | 6 | 0.0010 (18) | 0.0005 (23) | 0.0149 (244) | 0.0000 (2) |
| builder/transit | other_months | 73 | 0.0000 (61) | 0.0000 (15) | 0.0000 (235) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 6 | 0.0031 (54) | 0.0068 (58) | 0.1119 (604) | 0.0014 (7) |
| builder/transit+perturb | other_months | 29 | 0.0000 (68) | 0.0000 (7) | 0.0000 (90) | 0.0000 (0) |
| noop | budget_month | 19 | 0.0103 (116) | 0.0027 (79) | 0.0350 (530) | 0.0006 (10) |
| noop | other_months | 161 | 0.0000 (8) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 1 | 0.0027 (108) | 0.0030 (121) | 0.0053 (214) | 0.0007 (29) |
| noop+perturb | other_months | 28 | 0.0000 (21) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 15 | 0.0033 (91) | 0.0023 (53) | 0.0128 (439) | 0.0003 (8) |
| random/sprinkle | other_months | 135 | 0.0035 (101) | 0.0001 (24) | 0.0029 (85) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 6 | 0.0104 (157) | 0.0099 (116) | 0.0797 (519) | 0.0025 (16) |
| random/sprinkle+perturb | other_months | 73 | 0.0007 (71) | 0.0001 (27) | 0.0029 (99) | 0.0000 (0) |
| random/uniform | budget_month | 12 | 0.0195 (275) | 0.0219 (162) | 0.4844 (1270) | 0.0032 (15) |
| random/uniform | other_months | 131 | 0.0000 (265) | 0.0000 (202) | 0.0000 (381) | 0.0000 (0) |
| random/uniform+perturb | budget_month | 3 | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| random/uniform+perturb | other_months | 58 | 0.0000 (155) | 0.0000 (90) | 0.0000 (311) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 700 | 0.0457 (807) | 0.4004 (5674) | 0.0028 (40) |
| source: state_reading | 527 | 0.0523 (726) | 0.5051 (6388) | 0.0031 (40) |
| source: open_loop | 173 | 0.0295 (1054) | 0.0542 (3497) | 0.0021 (40) |
| budget_sweep | 62 | 0.0158 (566) | 0.0302 (887) | 0.0017 (50) |
| budget_sweep+perturb | 28 | 0.0218 (672) | 0.0461 (1299) | 0.0026 (77) |
| builder/boom | 38 | 0.1686 (582) | 5.4171 (11517) | 0.0045 (26) |
| builder/boom+perturb | 17 | 0.1028 (698) | 3.6674 (10249) | 0.0048 (23) |
| builder/corridor | 36 | 0.0406 (597) | 0.4189 (5789) | 0.0016 (26) |
| builder/corridor+perturb | 13 | 0.0661 (522) | 0.8232 (5926) | 0.0052 (63) |
| builder/frugal | 38 | 0.0307 (632) | 0.2851 (4161) | 0.0025 (53) |
| builder/frugal+perturb | 18 | 0.0356 (508) | 0.3811 (4542) | 0.0031 (43) |
| builder/grid | 55 | 0.0585 (611) | 0.7606 (7655) | 0.0037 (32) |
| builder/grid+perturb | 24 | 0.0453 (670) | 0.4278 (7612) | 0.0031 (50) |
| builder/industry | 22 | 0.0326 (356) | 0.6838 (4918) | 0.0027 (38) |
| builder/industry+perturb | 16 | 0.0466 (674) | 1.0517 (6811) | 0.0043 (34) |
| builder/satellite | 34 | 0.0974 (561) | 2.8567 (9029) | 0.0072 (41) |
| builder/satellite+perturb | 19 | 0.0675 (790) | 1.4111 (10297) | 0.0031 (30) |
| builder/transit | 29 | 0.1103 (695) | 2.4141 (10186) | 0.0103 (46) |
| builder/transit+perturb | 16 | 0.1031 (834) | 1.1264 (9196) | 0.0035 (38) |
| noop | 59 | 0.0163 (342) | 0.0283 (485) | 0.0011 (29) |
| noop+perturb | 15 | 0.0133 (363) | 0.0258 (343) | 0.0017 (46) |
| random/sprinkle | 56 | 0.0433 (737) | 0.1359 (1905) | 0.0018 (35) |
| random/sprinkle+perturb | 28 | 0.0428 (685) | 0.1483 (1787) | 0.0020 (34) |
| random/uniform | 52 | 0.3639 (2442) | 1.9492 (10026) | 0.0057 (42) |
| random/uniform+perturb | 25 | 0.5495 (2664) | 2.6450 (10605) | 0.0067 (46) |
