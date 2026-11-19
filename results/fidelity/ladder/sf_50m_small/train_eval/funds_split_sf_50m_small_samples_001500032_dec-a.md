# Funds error split: sf_50m_small_samples_001500032_dec-a

Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.

## One month (held-out one-step transitions), by behaviour type and budget month

| group | n | model T=1 | model T=0 | copy | engine floor |
|---|---|---|---|---|---|
| all | budget_month | 165 | 0.0038 (101) | 0.0028 (81) | 0.0391 (759) | 0.0004 (9) |
| all | other_months | 1835 | 0.0000 (34) | 0.0000 (14) | 0.0000 (186) | 0.0000 (0) |
| source: state_reading | budget_month | 125 | 0.0034 (93) | 0.0021 (70) | 0.0348 (670) | 0.0005 (9) |
| source: state_reading | other_months | 1427 | 0.0000 (32) | 0.0000 (9) | 0.0000 (215) | 0.0000 (0) |
| source: open_loop | budget_month | 40 | 0.0044 (123) | 0.0042 (116) | 0.0971 (1039) | 0.0003 (7) |
| source: open_loop | other_months | 408 | 0.0000 (44) | 0.0000 (30) | 0.0000 (86) | 0.0000 (0) |
| budget_sweep | budget_month | 19 | 0.0045 (95) | 0.0026 (83) | 0.0609 (1013) | 0.0004 (10) |
| budget_sweep | other_months | 183 | 0.0000 (5) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| budget_sweep+perturb | budget_month | 13 | 0.0051 (188) | 0.0037 (120) | 0.0210 (659) | 0.0002 (10) |
| budget_sweep+perturb | other_months | 66 | 0.0000 (26) | 0.0000 (9) | 0.0000 (0) | 0.0000 (0) |
| builder/boom | budget_month | 5 | 0.0007 (20) | 0.0014 (17) | 0.0079 (135) | 0.0005 (10) |
| builder/boom | other_months | 92 | 0.0000 (40) | 0.0000 (3) | 0.0000 (445) | 0.0000 (0) |
| builder/boom+perturb | budget_month | 4 | 0.0016 (39) | 0.0037 (61) | 0.0196 (608) | 0.0000 (1) |
| builder/boom+perturb | other_months | 35 | 0.0000 (28) | 0.0000 (3) | 0.0000 (210) | 0.0000 (0) |
| builder/corridor | budget_month | 5 | 0.0023 (43) | 0.0009 (27) | 0.0070 (201) | 0.0004 (11) |
| builder/corridor | other_months | 91 | 0.0000 (19) | 0.0000 (2) | 0.0000 (172) | 0.0000 (0) |
| builder/corridor+perturb | budget_month | 2 | 0.0002 (4) | 0.0006 (8) | 0.0094 (134) | 0.0000 (0) |
| builder/corridor+perturb | other_months | 49 | 0.0000 (19) | 0.0000 (2) | 0.0000 (116) | 0.0000 (0) |
| builder/frugal | budget_month | 10 | 0.0026 (70) | 0.0013 (26) | 0.0143 (614) | 0.0015 (15) |
| builder/frugal | other_months | 79 | 0.0000 (18) | 0.0000 (1) | 0.0000 (109) | 0.0000 (0) |
| builder/frugal+perturb | budget_month | 8 | 0.0105 (519) | 0.0034 (490) | 0.2676 (1697) | 0.0008 (7) |
| builder/frugal+perturb | other_months | 43 | 0.0000 (17) | 0.0000 (2) | 0.0000 (76) | 0.0000 (0) |
| builder/grid | budget_month | 13 | 0.0025 (51) | 0.0006 (28) | 0.0784 (1320) | 0.0002 (9) |
| builder/grid | other_months | 145 | 0.0000 (22) | 0.0000 (1) | 0.0000 (161) | 0.0000 (0) |
| builder/grid+perturb | budget_month | 6 | 0.0070 (57) | 0.0036 (30) | 0.0050 (264) | 0.0024 (14) |
| builder/grid+perturb | other_months | 80 | 0.0000 (44) | 0.0000 (16) | 0.0000 (338) | 0.0000 (0) |
| builder/industry | budget_month | 8 | 0.0084 (26) | 0.0197 (21) | 0.6242 (580) | 0.0003 (5) |
| builder/industry | other_months | 96 | 0.0000 (16) | 0.0000 (2) | 0.0000 (265) | 0.0000 (0) |
| builder/industry+perturb | budget_month | 5 | 0.0132 (136) | 0.0070 (128) | 0.1569 (813) | 0.0004 (5) |
| builder/industry+perturb | other_months | 43 | 0.0000 (8) | 0.0000 (2) | 0.0000 (305) | 0.0000 (0) |
| builder/satellite | budget_month | 11 | 0.0197 (59) | 0.0103 (36) | 0.1995 (749) | 0.0036 (11) |
| builder/satellite | other_months | 68 | 0.0000 (13) | 0.0000 (2) | 0.0000 (288) | 0.0000 (0) |
| builder/satellite+perturb | budget_month | 1 | 0.0136 (19) | 0.0201 (28) | 0.0688 (96) | 0.0050 (7) |
| builder/satellite+perturb | other_months | 45 | 0.0000 (55) | 0.0000 (8) | 0.0000 (326) | 0.0000 (0) |
| builder/transit | budget_month | 7 | 0.0097 (24) | 0.0032 (20) | 0.0447 (281) | 0.0005 (4) |
| builder/transit | other_months | 74 | 0.0000 (27) | 0.0000 (5) | 0.0000 (604) | 0.0000 (0) |
| builder/transit+perturb | budget_month | 1 | 0.0000 (0) | 0.0000 (0) | 304.0000 (304) | 0.0000 (0) |
| builder/transit+perturb | other_months | 48 | 0.0000 (30) | 0.0000 (2) | 0.0000 (289) | 0.0000 (0) |
| noop | budget_month | 8 | 0.0008 (50) | 0.0018 (70) | 0.0156 (1021) | 0.0001 (6) |
| noop | other_months | 109 | 0.0000 (5) | 0.0000 (0) | 0.0000 (0) | 0.0000 (0) |
| noop+perturb | budget_month | 5 | 0.0047 (82) | 0.0005 (25) | 0.0060 (779) | 0.0003 (17) |
| noop+perturb | other_months | 59 | 0.0000 (17) | 0.0000 (2) | 0.0000 (0) | 0.0000 (0) |
| random/sprinkle | budget_month | 20 | 0.0017 (35) | 0.0018 (25) | 0.0138 (446) | 0.0008 (10) |
| random/sprinkle | other_months | 188 | 0.0009 (45) | 0.0001 (8) | 0.0026 (98) | 0.0000 (0) |
| random/sprinkle+perturb | budget_month | 1 | 0.0027 (41) | 0.0013 (20) | 0.0112 (168) | 0.0012 (18) |
| random/sprinkle+perturb | other_months | 80 | 0.0010 (49) | 0.0001 (15) | 0.0011 (79) | 0.0000 (0) |
| random/uniform | budget_month | 13 | 0.0344 (210) | 0.0407 (193) | 0.6237 (1089) | 0.0000 (4) |
| random/uniform | other_months | 116 | 0.0005 (144) | 0.0000 (107) | 0.0000 (302) | 0.0000 (0) |
| random/uniform+perturb | other_months | 46 | 0.0017 (111) | 0.0000 (125) | 0.0000 (393) | 0.0000 (0) |

## Twelve months (open-loop from the plans' start states; every window holds one budget month)

| behaviour | n plans | model sample | copy | engine floor |
|---|---|---|---|---|
| all | 500 | 0.0346 (686) | 0.3144 (4896) | 0.0035 (42) |
| source: state_reading | 393 | 0.0364 (661) | 0.3691 (5319) | 0.0036 (41) |
| source: open_loop | 107 | 0.0246 (774) | 0.1113 (3340) | 0.0030 (49) |
| budget_sweep | 52 | 0.0175 (391) | 0.0516 (1151) | 0.0028 (51) |
| budget_sweep+perturb | 13 | 0.0166 (533) | 0.0622 (1014) | 0.0037 (75) |
| builder/boom | 22 | 0.0373 (700) | 0.5264 (7698) | 0.0028 (30) |
| builder/boom+perturb | 9 | 0.1324 (943) | 1.9464 (13171) | 0.0048 (34) |
| builder/corridor | 30 | 0.0418 (621) | 1.5593 (6898) | 0.0035 (30) |
| builder/corridor+perturb | 11 | 0.0222 (471) | 0.8501 (7803) | 0.0026 (56) |
| builder/frugal | 19 | 0.0218 (408) | 0.2377 (4058) | 0.0030 (38) |
| builder/frugal+perturb | 12 | 0.0306 (361) | 0.3368 (3605) | 0.0068 (52) |
| builder/grid | 55 | 0.0370 (695) | 0.2887 (5150) | 0.0042 (38) |
| builder/grid+perturb | 18 | 0.0510 (667) | 0.4334 (5471) | 0.0042 (48) |
| builder/industry | 30 | 0.0368 (730) | 1.0808 (5807) | 0.0016 (31) |
| builder/industry+perturb | 8 | 0.0316 (754) | 0.3113 (6407) | 0.0013 (33) |
| builder/satellite | 22 | 0.0763 (408) | 3.5904 (7642) | 0.0106 (29) |
| builder/satellite+perturb | 7 | 0.0789 (698) | 1.2735 (7072) | 0.0055 (68) |
| builder/transit | 13 | 0.0594 (619) | 0.9652 (7019) | 0.0015 (25) |
| builder/transit+perturb | 13 | 0.1120 (880) | 2.4904 (10988) | 0.0037 (32) |
| noop | 26 | 0.0087 (386) | 0.0321 (1220) | 0.0014 (56) |
| noop+perturb | 14 | 0.0089 (250) | 0.0136 (405) | 0.0024 (33) |
| random/sprinkle | 65 | 0.0209 (516) | 0.1177 (2016) | 0.0030 (45) |
| random/sprinkle+perturb | 18 | 0.0387 (745) | 0.1337 (2152) | 0.0058 (64) |
| random/uniform | 29 | 0.4136 (1809) | 1.8297 (9167) | 0.0091 (40) |
| random/uniform+perturb | 14 | 0.8983 (2232) | 10.8439 (10134) | 0.0081 (45) |
