# Depth of the false acceptances 

Main checkpoint (os_50m_full, 6,000,000 samples), 193 instances on the 40 cities, budget 1,000. Counts, no intervals.

| search | judge | instances | false acceptances | median oracle pass share | pass share below 0.1 | pass share 0 | median majority margin |
|---|---|---|---|---|---|---|---|
| random | emulator | 193 | 29 | 0.094 | 15 | 11 | -0.528 |
| random | perfect emulator | 193 | 16 | 0.281 | 3 | 0 | -0.193 |
| cem_seeded | emulator | 193 | 35 | 0.031 | 23 | 14 | -0.717 |
| cem_seeded | perfect emulator | 193 | 13 | 0.344 | 0 | 0 | -0.122 |

False acceptance: the judge accepts the selected plan at 4 or more of its 8 fresh samples and the 32-seed majority oracle rejects it. Pass share: the plan's share of the 32 oracle seeds on which it passes. Sources: random: results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24 and results/audit/engine_reference/tasks_v2_H24/B_economy; cem_seeded: results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded and results/audit/engine_reference/tasks_v2_H24/cem_seeded_B_economy.
