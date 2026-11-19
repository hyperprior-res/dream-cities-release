# Pilot 4: the sufficient observation (ledger + carried maps)

50M, one-step, 600,000 samples (600,064 consumed) on train_full; pilot3_lv flags plus the ledger; GPU 1
(gpu-b), batch 128 as 2 x 64 accumulated micro-batches; evaluation as pilot 3 (same held-out selection,
decoding b). Engine floor recomputed with the ledger (results/fidelity/pilot4_ledger/floor_*.json).

## Headline

| run | 1-month scalar ratio, sampled | mean of K | funds med. rel. 12 m | pop med. rel. 12 m | structural F1 1 m T=1 | 24-month scalar ratio |
|---|---|---|---|---|---|---|
| pilot3_lv 600k | 0.840 | 0.682 | 0.0724 | 0.0574 | 0.1508 | 0.658 |
| pilot4_ledger 300k | 1.459 | 1.062 | 0.1934 | 0.0487 | 0.1373 | 1.035 |
| pilot4_ledger 600k | 0.848 | 0.667 | 0.1092 | 0.0400 | 0.1474 | 0.645 |

Engine floor: 1-month scalar ratio 0.204, funds 12 m 0.0026, pop 12 m 0.0259, structural F1 0.2074.

## Valves and score at one month (mean absolute error; ratio to copy-last-state)

| entry | run | start: sample | start: mean of K | start: floor | start: copy | start ratio | random: T=1 | random: floor | random: copy | random ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| res_valve | pilot3_lv 600k | 70.14 | 53.15 | 2.02 | 55.45 | 1.265 | 73.73 | 1.76 | 56.63 | 1.302 |
| res_valve | pilot4_ledger 300k | 116.59 | 86.36 | 2.02 | 55.45 | 2.103 | 96.41 | 1.76 | 56.63 | 1.702 |
| res_valve | pilot4_ledger 600k | 70.26 | 51.09 | 2.02 | 55.45 | 1.267 | 73.97 | 1.76 | 56.63 | 1.306 |
| com_valve | pilot3_lv 600k | 125.53 | 100.49 | 5.08 | 112.98 | 1.111 | 137.39 | 7.66 | 125.67 | 1.093 |
| com_valve | pilot4_ledger 300k | 160.53 | 108.74 | 5.08 | 112.98 | 1.421 | 156.31 | 7.66 | 125.67 | 1.244 |
| com_valve | pilot4_ledger 600k | 111.01 | 86.46 | 5.08 | 112.98 | 0.983 | 122.30 | 7.66 | 125.67 | 0.973 |
| ind_valve | pilot3_lv 600k | 124.83 | 102.26 | 0.00 | 126.05 | 0.990 | 106.90 | 0.37 | 101.15 | 1.057 |
| ind_valve | pilot4_ledger 300k | 163.88 | 108.46 | 0.00 | 126.05 | 1.300 | 133.05 | 0.37 | 101.15 | 1.315 |
| ind_valve | pilot4_ledger 600k | 118.31 | 90.15 | 0.00 | 126.05 | 0.939 | 94.07 | 0.37 | 101.15 | 0.930 |
| score | pilot3_lv 600k | 60.17 | 45.16 | 0.71 | 46.63 | 1.290 | 5.35 | 0.72 | 4.95 | 1.080 |
| score | pilot4_ledger 300k | 88.64 | 50.52 | 0.71 | 46.63 | 1.901 | 8.50 | 0.72 | 4.95 | 1.718 |
| score | pilot4_ledger 600k | 53.66 | 36.57 | 0.71 | 46.63 | 1.151 | 4.59 | 0.72 | 4.95 | 0.928 |

Per learned ledger entry: results/fidelity/pilot4_ledger/ck600k/one_month_*.md (and ck300k/).


## What was built (code/dc/model.py, ModelConfig.ledger; SIZES now default to lv + ledger)

* Inputs: the 27-entry ledger (standardised; symmetric log for wide entries; plus a one-hot of
  (sim_cycle / 4) mod 5, the rate-of-growth decay gate) in the conditioning vector and directly into the
  second stage; the terrain map (30 x 25) enters the trunk at its 30 x 25 level, com_rate (15 x 13) at the
  bottleneck.
* Outputs: terrain and com_rate predicted by the spatial stage as gated discretised logistics (like the
  overlays; decoding b takes their mean); 24 ledger entries learned in the second stage (same family as
  the scalars, integer change), with a learned linear path from the current scalars and ledger and the
  budget-month weight; per-entry log-likelihoods `lg_<name>`, plus `ledger`, `terrain`, `com_rate`.
* Set by definition : `sim_cycle` (+4 a month mod 1024; 1,728 of 1,728),
  `initial_eval` (0 at every boundary after the first), `disasters` (the trajectory's switch, constant).
  `sprite_cycle` is a pure tick count but its increment (319 or 320) is not a function of its own value,
  so it is learned. Everything else is learned. Nothing is restored from the engine in a rollout.
* Derived definitions hold on the store: 0 violations in 3,072 sampled train_full transitions.
* Trained on GPU 1 (gpu-b, the GPU free now; GPU 0 is busy until 02:20Z with noledger_50m_full_1step):
  600,064 samples in 1,541 s, median 411.5 samples/s, peak 12.3 GB (GPU 0 would have started at 02:20Z).

## Valves and score: not clearly below copy, and why (measured)

At 600k the valves and the score are at copy-last-state level at one month (start states: res 1.27, com
0.98, ind 0.94, score 1.15 times copy; random transitions res 1.31, com 0.97, ind 0.93, score 0.93), with
the engine floor at 0.00 to 0.07 of copy. Their held-out likelihood did not change with the ledger
(res/com/ind valve NLL 2.098 / 4.170 / 3.936 nats against pilot3_lv's 2.119 / 4.261 / 3.964).

The inputs are now there: the restore is exact with them and the floor is small. What fails is learning
exact arithmetic on large raw values in the second stage. The clearest case is `res_hist1`, whose next
value is the current `res_hist0` in every transition (engine floor 0.00): the model's error is 1.34 against
copy's 1.18 on random transitions (com_hist1 1.14 / 1.13, ind_hist1 1.33 / 1.33). The learned linear path
takes the current values in units of their delta scale (hist values up to about 22,000 with a delta scale
of 4), so an exact copy needs weights of exactly +1 / -1, and Adam moves each weight by about the learning
rate per step: a weight error of 1e-3 is already several units of error. The valve update is a clamped
ratio of census values times 600, applied twice a month, which is harder still for the same reason. The
ledger likelihood is still falling fast (-8.1% per 100k samples over the last tenth; scalars -2.4%), so
part of this is training length.

Next design step I would take: a copy (pointer) pathway in the second stage, a learned softmax over
current entries whose saturated choice gives "next = current value of entry j" exactly (learned, no rule
written in), and ratio features (differences of the standardised log values of census and history
entries) for the valves.
