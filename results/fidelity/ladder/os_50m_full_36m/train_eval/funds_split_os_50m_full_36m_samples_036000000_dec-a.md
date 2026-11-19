# Funds error split: os_50m_full_36m_samples_036000000_dec-a

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 165 | 0.0023 (58) | 0.0017 (44) | 0.0391 (759) | 0.0004 (9) |
| all | other_months | 1835 | 0.0000 (37) | 0.0000 (12) | 0.0000 (186) | 0.0000 (0) |
| source: state_reading | budget_month | 125 | 0.0022 (62) | 0.0017 (34) | 0.0348 (670) | 0.0005 (9) |
| source: state_reading | other_months | 1427 | 0.0000 (40) | 0.0000 (11) | 0.0000 (215) | 0.0000 (0) |
| source: open_loop | budget_month | 40 | 0.0025 (45) | 0.0016 (75) | 0.0971 (1039) | 0.0003 (7) |
| source: open_loop | other_months | 408 | 0.0000 (27) | 0.0000 (13) | 0.0000 (86) | 0.0000 (0) |
| budget_sweep | budget_month | 19 | 0.0018 (30) | 0.0011 (28) | 0.0609 (1013) | 0.0004 (10) |
| budget_sweep | other_months | 183 | 0.0000 (9) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 13 | 0.0018 (45) | 0.0021 (47) | 0.0210 (659) | 0.0002 (10) |
| budget_sweep+perturb | other_months | 66 | 0.0000 (14) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 5 | 0.0009 (23) | 0.0026 (26) | 0.0079 (135) | 0.0005 (10) |
| builder/boom | other_months | 92 | 0.0000 (63) | 0.0000 (16) | 0.0000 (445) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 4 | 0.0004 (231) | 0.0012 (118) | 0.0196 (608) | 0.0000 (1) |
| builder/boom+perturb | other_months | 35 | 0.0000 (38) | 0.0000 (3) | 0.0000 (210) | 0.0000 (0) |
| builder/corridor | budget_month | 5 | 0.0004 (8) | 0.0009 (16) | 0.0070 (201) | 0.0004 (11) |
| builder/corridor | other_months | 91 | 0.0000 (28) | 0.0000 (8) | 0.0000 (172) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 2 | 0.0006 (8) | 0.0002 (2) | 0.0094 (134) | 0.0000 (0) |
| builder/corridor+perturb | other_months | 49 | 0.0000 (24) | 0.0000 (4) | 0.0000 (116) | 0.0000 (0) |
| builder/frugal | budget_month | 10 | 0.0018 (60) | 0.0020 (50) | 0.0143 (614) | 0.0015 (15) |
| builder/frugal | other_months | 79 | 0.0000 (42) | 0.0000 (25) | 0.0000 (109) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 8 | 0.0050 (76) | 0.0014 (48) | 0.2676 (1697) | 0.0008 (7) |
| builder/frugal+perturb | other_months | 43 | 0.0000 (22) | 0.0000 (2) | 0.0000 (76) | 0.0000 (0) |
| builder/grid | budget_month | 13 | 0.0012 (16) | 0.0005 (17) | 0.0784 (1320) | 0.0002 (9) |
| builder/grid | other_months | 145 | 0.0000 (18) | 0.0000 (1) | 0.0000 (161) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 6 | 0.0018 (112) | 0.0051 (31) | 0.0050 (264) | 0.0024 (14) |
| builder/grid+perturb | other_months | 80 | 0.0000 (26) | 0.0000 (6) | 0.0000 (338) | 0.0000 (0) |
| builder/industry | budget_month | 8 | 0.0031 (6) | 0.0046 (8) | 0.6242 (580) | 0.0003 (5) |
| builder/industry | other_months | 96 | 0.0000 (29) | 0.0000 (6) | 0.0000 (265) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 5 | 0.0010 (174) | 0.0030 (24) | 0.1569 (813) | 0.0004 (5) |
| builder/industry+perturb | other_months | 43 | 0.0000 (46) | 0.0000 (19) | 0.0000 (305) | 0.0000 (0) |
| builder/satellite | budget_month | 11 | 0.0157 (68) | 0.0112 (56) | 0.1995 (749) | 0.0036 (11) |
| builder/satellite | other_months | 68 | 0.0000 (29) | 0.0000 (3) | 0.0000 (288) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 1 | 0.0065 (9) | 0.0022 (3) | 0.0688 (96) | 0.0050 (7) |
| builder/satellite+perturb | other_months | 45 | 0.0000 (52) | 0.0000 (15) | 0.0000 (326) | 0.0000 (0) |
| builder/transit | budget_month | 7 | 0.0032 (37) | 0.0034 (9) | 0.0447 (281) | 0.0005 (4) |
| builder/transit | other_months | 74 | 0.0000 (40) | 0.0000 (20) | 0.0000 (604) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 1 | 21.0000 (21) | 0.0000 (0) | 304.0000 (304) | 0.0000 (0) |
| builder/transit+perturb | other_months | 48 | 0.0000 (49) | 0.0000 (17) | 0.0000 (289) | 0.0000 (0) |
| noop | budget_month | 8 | 0.0022 (54) | 0.0013 (34) | 0.0156 (1021) | 0.0001 (6) |
| noop | other_months | 109 | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 5 | 0.0008 (37) | 0.0010 (21) | 0.0060 (779) | 0.0003 (17) |
| noop+perturb | other_months | 59 | 0.0000 (5) | 0.0000 (1) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 20 | 0.0044 (88) | 0.0014 (37) | 0.0138 (446) | 0.0008 (10) |
| random/sprinkle | other_months | 188 | 0.0006 (77) | 0.0000 (18) | 0.0026 (98) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 1 | 0.0044 (66) | 0.0003 (5) | 0.0112 (168) | 0.0012 (18) |
| random/sprinkle+perturb | other_months | 80 | 0.0011 (53) | 0.0001 (18) | 0.0011 (79) | 0.0000 (0) |
| random/uniform | budget_month | 13 | 0.0143 (62) | 0.0058 (169) | 0.6237 (1089) | 0.0000 (4) |
| random/uniform | other_months | 116 | 0.0000 (82) | 0.0000 (45) | 0.0000 (302) | 0.0000 (0) |
| random/uniform+perturb | other_months | 46 | 0.0000 (64) | 0.0000 (27) | 0.0000 (393) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 500 | 0.0320 (562) | 0.3144 (4896) | 0.0035 (42) |
| source: state_reading | 393 | 0.0376 (568) | 0.3691 (5319) | 0.0036 (41) |
| source: open_loop | 107 | 0.0144 (537) | 0.1113 (3340) | 0.0030 (49) |
| budget_sweep | 52 | 0.0077 (282) | 0.0516 (1151) | 0.0028 (51) |
| budget_sweep+perturb | 13 | 0.0147 (560) | 0.0622 (1014) | 0.0037 (75) |
| builder/boom | 22 | 0.0273 (484) | 0.5264 (7698) | 0.0028 (30) |
| builder/boom+perturb | 9 | 0.0755 (569) | 1.9464 (13171) | 0.0048 (34) |
| builder/corridor | 30 | 0.0499 (519) | 1.5593 (6898) | 0.0035 (30) |
| builder/corridor+perturb | 11 | 0.0247 (501) | 0.8501 (7803) | 0.0026 (56) |
| builder/frugal | 19 | 0.0214 (350) | 0.2377 (4058) | 0.0030 (38) |
| builder/frugal+perturb | 12 | 0.0369 (438) | 0.3368 (3605) | 0.0068 (52) |
| builder/grid | 55 | 0.0282 (405) | 0.2887 (5150) | 0.0042 (38) |
| builder/grid+perturb | 18 | 0.0233 (291) | 0.4334 (5471) | 0.0042 (48) |
| builder/industry | 30 | 0.0287 (419) | 1.0808 (5807) | 0.0016 (31) |
| builder/industry+perturb | 8 | 0.0308 (559) | 0.3113 (6407) | 0.0013 (33) |
| builder/satellite | 22 | 0.0923 (281) | 3.5904 (7642) | 0.0106 (29) |
| builder/satellite+perturb | 7 | 0.0981 (809) | 1.2735 (7072) | 0.0055 (68) |
| builder/transit | 13 | 0.0575 (336) | 0.9652 (7019) | 0.0015 (25) |
| builder/transit+perturb | 13 | 0.1004 (845) | 2.4904 (10988) | 0.0037 (32) |
| noop | 26 | 0.0071 (413) | 0.0321 (1220) | 0.0014 (56) |
| noop+perturb | 14 | 0.0044 (308) | 0.0136 (405) | 0.0024 (33) |
| random/sprinkle | 65 | 0.0366 (826) | 0.1177 (2016) | 0.0030 (45) |
| random/sprinkle+perturb | 18 | 0.0812 (1165) | 0.1337 (2152) | 0.0058 (64) |
| random/uniform | 29 | 0.2133 (1107) | 1.8297 (9167) | 0.0091 (40) |
| random/uniform+perturb | 14 | 0.3659 (1191) | 10.8439 (10134) | 0.0081 (45) |
