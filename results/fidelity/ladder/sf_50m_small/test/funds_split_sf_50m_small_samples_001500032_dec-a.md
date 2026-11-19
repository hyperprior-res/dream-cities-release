# Funds error split: sf_50m_small_samples_001500032_dec-a

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 182 | 0.0039 (96) | 0.0041 (92) | 0.0559 (713) | 0.0006 (10) |
| all | other_months | 1818 | 0.0000 (42) | 0.0000 (17) | 0.0000 (156) | 0.0000 (0) |
| source: state_reading | budget_month | 132 | 0.0040 (85) | 0.0040 (73) | 0.0583 (665) | 0.0006 (9) |
| source: state_reading | other_months | 1349 | 0.0000 (32) | 0.0000 (10) | 0.0000 (173) | 0.0000 (0) |
| source: open_loop | budget_month | 50 | 0.0035 (124) | 0.0047 (141) | 0.0422 (838) | 0.0007 (13) |
| source: open_loop | other_months | 469 | 0.0000 (72) | 0.0000 (37) | 0.0000 (106) | 0.0000 (0) |
| budget_sweep | budget_month | 19 | 0.0021 (93) | 0.0026 (94) | 0.0243 (873) | 0.0007 (14) |
| budget_sweep | other_months | 177 | 0.0000 (2) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 7 | 0.0034 (153) | 0.0024 (87) | 0.0462 (1452) | 0.0000 (13) |
| budget_sweep+perturb | other_months | 67 | 0.0000 (2) | 0.0000 (1) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 9 | 0.0262 (94) | 0.0122 (63) | 0.5485 (1546) | 0.0037 (9) |
| builder/boom | other_months | 92 | 0.0000 (15) | 0.0000 (3) | 0.0000 (181) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 8 | 0.0000 (18) | 0.0000 (20) | 0.5590 (328) | 0.0000 (2) |
| builder/boom+perturb | other_months | 47 | 0.0000 (23) | 0.0000 (3) | 0.0000 (181) | 0.0000 (0) |
| builder/corridor | budget_month | 8 | 0.0042 (83) | 0.0039 (74) | 0.0482 (708) | 0.0006 (17) |
| builder/corridor | other_months | 99 | 0.0000 (33) | 0.0000 (5) | 0.0000 (170) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 6 | 0.0040 (76) | 0.0034 (72) | 0.0625 (320) | 0.0009 (8) |
| builder/corridor+perturb | other_months | 27 | 0.0000 (29) | 0.0000 (1) | 0.0000 (208) | 0.0000 (0) |
| builder/frugal | budget_month | 13 | 0.0059 (79) | 0.0059 (83) | 0.0696 (714) | 0.0007 (9) |
| builder/frugal | other_months | 114 | 0.0000 (17) | 0.0000 (3) | 0.0000 (157) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 8 | 0.0098 (74) | 0.0102 (78) | 0.0783 (718) | 0.0024 (12) |
| builder/frugal+perturb | other_months | 46 | 0.0000 (14) | 0.0000 (7) | 0.0000 (93) | 0.0000 (0) |
| builder/grid | budget_month | 12 | 0.0062 (59) | 0.0068 (70) | 0.0799 (1094) | 0.0017 (16) |
| builder/grid | other_months | 135 | 0.0000 (30) | 0.0000 (3) | 0.0000 (247) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 9 | 0.0026 (132) | 0.0028 (107) | 0.0739 (380) | 0.0007 (7) |
| builder/grid+perturb | other_months | 63 | 0.0000 (16) | 0.0000 (8) | 0.0000 (287) | 0.0000 (0) |
| builder/industry | budget_month | 4 | 0.0090 (125) | 0.0142 (126) | 0.2742 (371) | 0.0006 (2) |
| builder/industry | other_months | 67 | 0.0000 (23) | 0.0000 (1) | 0.0000 (96) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 1 | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| builder/industry+perturb | other_months | 43 | 0.0000 (12) | 0.0000 (3) | 0.0000 (23) | 0.0000 (0) |
| builder/satellite | budget_month | 8 | 0.0045 (112) | 0.0040 (111) | 0.0566 (481) | 0.0008 (8) |
| builder/satellite | other_months | 90 | 0.0000 (22) | 0.0000 (3) | 0.0000 (287) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 2 | 0.0011 (28) | 0.0012 (32) | 716.5037 (814) | 0.0001 (3) |
| builder/satellite+perturb | other_months | 63 | 0.0000 (24) | 0.0000 (9) | 0.0000 (363) | 0.0000 (0) |
| builder/transit | budget_month | 6 | 0.0020 (36) | 0.0000 (40) | 0.0149 (244) | 0.0000 (2) |
| builder/transit | other_months | 73 | 0.0000 (18) | 0.0000 (3) | 0.0000 (235) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 6 | 0.0070 (28) | 0.0052 (44) | 0.1119 (604) | 0.0014 (7) |
| builder/transit+perturb | other_months | 29 | 0.0000 (7) | 0.0000 (3) | 0.0000 (90) | 0.0000 (0) |
| noop | budget_month | 19 | 0.0061 (92) | 0.0043 (93) | 0.0350 (530) | 0.0006 (10) |
| noop | other_months | 161 | 0.0000 (5) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 1 | 0.0006 (23) | 0.0010 (39) | 0.0053 (214) | 0.0007 (29) |
| noop+perturb | other_months | 28 | 0.0000 (29) | 0.0000 (8) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 15 | 0.0019 (86) | 0.0013 (61) | 0.0128 (439) | 0.0003 (8) |
| random/sprinkle | other_months | 135 | 0.0005 (38) | 0.0001 (9) | 0.0029 (85) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 6 | 0.0122 (224) | 0.0071 (133) | 0.0797 (519) | 0.0025 (16) |
| random/sprinkle+perturb | other_months | 73 | 0.0014 (84) | 0.0001 (32) | 0.0029 (99) | 0.0000 (0) |
| random/uniform | budget_month | 12 | 0.0910 (225) | 0.0852 (293) | 0.4844 (1270) | 0.0032 (15) |
| random/uniform | other_months | 131 | 0.0000 (248) | 0.0000 (133) | 0.0000 (381) | 0.0000 (0) |
| random/uniform+perturb | budget_month | 3 | 0.0000 (5) | 0.0000 (4) | 0.0000 (0) | 0.0000 (0) |
| random/uniform+perturb | other_months | 58 | 0.0006 (164) | 0.0000 (89) | 0.0000 (311) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 700 | 0.0385 (893) | 0.4004 (5674) | 0.0028 (40) |
| source: state_reading | 527 | 0.0435 (841) | 0.5051 (6388) | 0.0031 (40) |
| source: open_loop | 173 | 0.0251 (1052) | 0.0542 (3497) | 0.0021 (40) |
| budget_sweep | 62 | 0.0132 (444) | 0.0302 (887) | 0.0017 (50) |
| budget_sweep+perturb | 28 | 0.0180 (603) | 0.0461 (1299) | 0.0026 (77) |
| builder/boom | 38 | 0.2196 (1272) | 5.4171 (11517) | 0.0045 (26) |
| builder/boom+perturb | 17 | 0.1220 (849) | 3.6674 (10249) | 0.0048 (23) |
| builder/corridor | 36 | 0.0450 (815) | 0.4189 (5789) | 0.0016 (26) |
| builder/corridor+perturb | 13 | 0.0886 (944) | 0.8232 (5926) | 0.0052 (63) |
| builder/frugal | 38 | 0.0173 (355) | 0.2851 (4161) | 0.0025 (53) |
| builder/frugal+perturb | 18 | 0.0233 (434) | 0.3811 (4542) | 0.0031 (43) |
| builder/grid | 55 | 0.0597 (922) | 0.7606 (7655) | 0.0037 (32) |
| builder/grid+perturb | 24 | 0.0345 (1022) | 0.4278 (7612) | 0.0031 (50) |
| builder/industry | 22 | 0.0330 (581) | 0.6838 (4918) | 0.0027 (38) |
| builder/industry+perturb | 16 | 0.0550 (846) | 1.0517 (6811) | 0.0043 (34) |
| builder/satellite | 34 | 0.0864 (738) | 2.8567 (9029) | 0.0072 (41) |
| builder/satellite+perturb | 19 | 0.0753 (962) | 1.4111 (10297) | 0.0031 (30) |
| builder/transit | 29 | 0.0916 (888) | 2.4141 (10186) | 0.0103 (46) |
| builder/transit+perturb | 16 | 0.0906 (1172) | 1.1264 (9196) | 0.0035 (38) |
| noop | 59 | 0.0125 (332) | 0.0283 (485) | 0.0011 (29) |
| noop+perturb | 15 | 0.0110 (311) | 0.0258 (343) | 0.0017 (46) |
| random/sprinkle | 56 | 0.0249 (504) | 0.1359 (1905) | 0.0018 (35) |
| random/sprinkle+perturb | 28 | 0.0206 (423) | 0.1483 (1787) | 0.0020 (34) |
| random/uniform | 52 | 0.4236 (2596) | 1.9492 (10026) | 0.0057 (42) |
| random/uniform+perturb | 25 | 0.7282 (2659) | 2.6450 (10605) | 0.0067 (46) |
