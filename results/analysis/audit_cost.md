# Cost of the audit in engine terms 

A replay is one 24-month engine run of one plan on one seed (24 city-months).

## Random-search audit, emulator side, per checkpoint (budgets 1, 10, 100, 1,000)

| city set | checkpoints | instances | replays per selected plan | engine city-months per checkpoint (all four budgets) | per instance (replays) | at B = 1,000 only, per checkpoint | distinct selected plans per instance |
|---|---|---|---|---|---|---|---|
| c40 | 24 | 193 | 41 | 759,648 | 3,936 (164) | 189,912 | 3.53 |
| c80 | 12 | 381 | 41 | 1,499,616 | 3,936 (164) | 374,904 | 3.49 |

All 120 cities (574 instances), on the 12 checkpoints with both city sets complete: 2,259,264 engine city-months per checkpoint (94,136 replays) over the four budgets, 564,816 (23,534 replays) at B = 1,000 alone; with a replay cache (a plan selected at several budgets replayed once) 83,107 replays. Each selected plan: 32 oracle seeds (needed for false acceptance) and 9 residual seeds (floors and decision fidelity); the oracle seeds alone at B = 1,000: 18,368 replays (440,832 city-months) per checkpoint.

## Perfect-emulator reference (shared by every checkpoint, once per city set)

| city set | instances | engine city-months per instance at B = 1,000 (search samples + verdict samples + oracle and residual) | replays per instance | whole run: engine-seeds judge city-months |
|---|---|---|---|---|
| c40 | 193 | 48,000 + 192 + 984 = 49,176 | 2,049 | 46,684,176 |
| c80 | 381 | 48,000 + 192 + 984 = 49,176 | 2,049 | 36,172,608 |

## RL as the paper evaluates it

| scope | runs | instance rows | open-loop oracle | closed loop | closed-loop check | greedy | total engine city-months |
|---|---|---|---|---|---|---|---|
| main checkpoint | 15 | 579 | 3,557,376 | 111,168 | 111,168 | 472,464 | 4,252,176 |
| ladder | 360 | 13896 | 85,377,024 | 2,668,032 | 2,668,032 | 11,339,136 | 102,052,224 |

The engine-trained learner (the RL arm's perfect-emulator reference): 11 runs, 11,000,000 engine months of training and 3,106,512 of evaluation. Per instance and run the RL evaluation replays each of its 8 action logs on the 32 oracle seeds (256 replays, 6,144 city-months); plan 0's false acceptance alone needs 32 replays (768 city-months), the same as one selected plan of the audit.

Per-instance figures of the reference are the records' design counts at B = 1,000 (the 1,000 candidates' K = 2 samples are shared by the tasks of a start with the same forced events, and budgets nest); the whole-run figure is the measured count of the engine-seeds judge, including the behaviour plans' verdicts.
