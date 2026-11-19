# B20, the coverage arm: notes (2026-11-11)

Brief: the specification, then the main round 2 (second store, union of three, launch).
Status: **os_50m_cov is training** (round 2, section R below). Round 1 (sections 1 to 4) stopped before training
because the tagged code could not read a union; the coordinator applied the patch as tag `ladder-v2-cov`.
Sections 1 to 4 are round 1 as written then; where round 2 changed something, section R says so.

## 1. The gap (`coverage_table.md`, `coverage_table.json`, script `coverage_table.py`)

A month *builds* when any of its four macro kinds is non-zero. Shares of building months at tax 0..4:

| source | building months | at tax <= 4 | at tax <= 4 with a funding cut | all three funding lines at 0 |
|---|---|---|---|---|
| train_full, all months | 731,820 | 0.069 | 0.057 | 0.002 |
| train_full, builder trajectories | 258,262 | 0.009 | 0.000 | 0.000 |
| selected plans of the main checkpoint, all methods and budgets (2,559 plans) | 32,139 | 0.105 | 0.087 | 0.000 |
| the same, random search at B = 1,000 (193 plans) | 2,033 | 0.111 | 0.086 | 0.000 |
| frontier plans (e32, 193 instances) | 3,059 | 0.644 | 0.638 | 0.441 |
| coverage store (new) | 154,367 | 0.311 | 0.308 | 0.009 |
| union train_full + coverage | 886,187 | 0.111 (98,700) | 0.101 (89,350) | - |

The premise holds: 0.069 of building months in train_full are at tax <= 4 (0.009 for the scripted builders), far
below the brief's stop line of one fifth. Frontier plans by task (building months at tax <= 4): grow 0.899, solvent
0.892, recover 0.847, power 0.514, treasury 0.203 (the revenue task caps tax at the start rate).

## 2. Coverage data

Code (edits only in the files the brief allows):
- `code/dc/behaviour.py`: new `HeldBudget` (wraps a policy; every month's tax and three funding columns set to one
  setting, forced-disaster column cleared; the builder still plays closed loop), `COVERAGE_STYLES` (the seven
  styles, sorted), `sample_coverage_behaviour(rng)` (style uniform over seven; tax uniform 0..20; road, fire, police
  each uniform on 0..4; draw order style, tax, road, fire, police; label `builder/<style>+held`). Nothing existing
  changed.
- `code/scripts/gen_data.py`: spec `train_cov` = `{"source": "train", "H": [[24, 25000]], "disaster_rate": 0.0,
  "behaviour": "coverage"}`; `SplitJob` reads `spec["behaviour"]` (absent = the mix, as before);
  `RealProvider.sample_coverage_behaviour`. `train_cov` is not in `SPLIT_ORDER`, so `all` does not generate it.
  Starts, seed derivation (`seed_for("train_cov", master, j, ...)`, re-derived until outside train_full's seeds),
  policy stream, layout, writer, crash safety: the original generator's.
- Tests: `code/tests/test_behaviour.py` (+2: the coverage draw's marginals and determinism, bad settings refused; a
  held builder holds the setting, the engine's tax scalar follows it, it builds, its log replays exactly, month 0's
  macros equal the unwrapped builder's), `code/tests/test_data.py` (+2 and a stand-in coverage behaviour: the three
  original specs and `SPLIT_ORDER` pinned, no `behaviour` key in their configs; a coverage split generated with 1
  and 3 workers is byte-identical, held budgets, no disasters, training starts only, seeds disjoint from
  train_full's, verify 0 mismatches). `pytest code/tests/test_data.py code/tests/test_behaviour.py`: 25 passed in
  5.2 s.

The existing stores are still what the generator produces (`regen_check.py`, `regen_check.json`): 1,000 random
trajectories of each of train_full, heldout_eval and train_eval generated again from scratch with the edited code:
action log, final full-state hash, label, engine seed, start and disasters flag equal in 1,000 of 1,000 for each.
The job configs equal the stored ones except `store_format` (stored `dc-store-1` at generation, now `dc-store-2`
after the ledger backfill; this predates B20, and means `gen_data.py gen` on a finished original store would refuse
on that key).

The store `<cache>/data/train_cov` (beside train_full, which was not touched):
- 25,000 trajectories x 24 months = 600,000 transitions, 625,000 observations, 27,038,985,592 bytes (27.0 GB;
  free before: 198.2 GB). Generated in 89.5 s on 16 local workers (6,705 city-months a second); host-b not used.
  Log `wm2-cache/logs/gen_train_cov_20261111T1442Z.log`.
- Verify by re-replay of **every** trajectory (`dc.data.verify`, every stored array and the final hash): 25,000
  checked, 0 mismatched, 625,000 observations compared (`verify_train_cov.json`). Manifest sha256 check: 16 files,
  0 mismatched.
- 60 families, 228 start variants, 0 held-out starts in the start table; split `train` only; disasters on in 0
  trajectories; budget columns constant within every trajectory and the forced column 0 everywhere.
- Draws: styles boom 3,580, grid 3,560, frugal 3,634, industry 3,579, satellite 3,561, corridor 3,486, transit
  3,600; tax 0..20 each 1,109 to 1,257 trajectories; each funding level 4,888 to 5,130.
- Engine seeds: 0 shared with train_full, train_eval or heldout_eval; 24,999 distinct of 25,000 (one repeat inside
  the store, as a 31-bit `seed_for` allows; the original generator has the same property); 0 (start, seed) pairs
  shared with train_eval.
- Under the coverage mix 0.257 of months build (train_full's builder trajectories: 0.158); building months at tax
  <= 4: 48,017 (train_full: 50,683), so the union about doubles them. Summary: `summary_train_cov.json`.

Known limit of the design as written: funding is uniform per line, so the frontier's commonest budget (all three
lines at 0: 0.441 of frontier building months) gets 1/125 of the trajectories; building months at tax <= 4 with all
funding at 0 are 420 in the coverage store and 314 in train_full.

## 3. Training: blocked, smallest change

Why the tagged code (`ladder-v2`, identical to the main tree in `dc/data.py` and `dc/train.py`) cannot read a union:
1. `train_run.py` takes one store from `dc.data.open_split(name)`: `TrajStore(root / name)`, or for `train_small`
   an index into one named store; the loader workers reopen `TrajStore(path)` by path.
2. The third stage reads `BookData.from_cache`: hard-coded `<cache>/ckpt/
   bookkeeping_cache/train_full.npz`, refused unless its length equals the store's transition count. So even a
   physically concatenated store fails; and that copy would be 150 GB on 198 GB free.

Smallest change, `B20_union_loader.patch` (applies cleanly to `ladder-v2`; `patch -p1 --dry-run` checked):
- `code/dc/data.py` (+115 / -2 lines): `open_store(path)` (a union directory holds `union.json`), `_Concat` (row-wise
  concatenation of the parts' memory maps, read by index, slice or index array), `UnionStore(TrajStore)` (parts'
  records concatenated with row offsets, starts / families / labels merged with remapped indices; refuses a part
  whose manifest sha256 changed since the union was made), `make_union(path, parts)`; `open_split` and the loader's
  `_BatchSource` open through `open_store`. A single store opens exactly as before.
- `code/dc/train.py` (+8 / -2): `BookData.from_cache` concatenates the parts' caches (`<part>.npz`, in part
  order) when the store is a union; otherwise unchanged.
- `dc/model.py`, `train_run.py`, `ladder.py`, the optimiser, schedule and loss: untouched.

Checked in a scratch copy of the tag (not in any checkout): the tag's own `test_data.py` 15 of 15 passed with and
without the patch; `BookData.from_cache` on train_small (20,000 rows) gives identical tensors, statistics and info
with and without the patch; on the real stores (`union_check.py` here, run against the patched scratch copy): union of 74,000
trajectories, 3,600,000 transitions, 3,674,000 observations; 300 records equal their part's; 400 loader rows
(tiles, half, power, eighth, scalars, ledger, terrain, com_rate, plan raster, action scalars) and build costs equal
the part stores'; `OneStepBatches` with 2 worker processes returns the stored states; 41 batches of 64 drew 0.172 of
transitions from the coverage part (expected 1/6); `BookData` over the union equals the per-part caches. The
coverage store's bookkeeping cache was built with `bookkeeping_diag.build` (same code as `train_full.npz`) into the
working directory only (71 s, 641 MB): it still has to be built (or copied) into `wm2-cache/ckpt/bookkeeping_cache/`.

Prepared, not launched: `<cache>/ckpt/queue_cov_gpu0.json` (os_50m_full's entry and
defaults copied, name `os_50m_cov`, index `train_full_cov`). Its `train_run.py` argv differs from os_50m_full's in
`--run` and `--index` only (checked through `ladder.train_cmd`). os_50m_full trained in 2 h 50 min on an unshared
GPU 0 (04:46 to 07:36Z, 10 November) plus 17 min of fidelity evaluation; GPU 0 is now shared with an evaluation
queue, so longer (not measured).

## 4. After approval

`B20_after_training.sh` (not run): A, the cache, the union directory and the launch from a clean checkout of
`ladder-v2` + the patch; B, the audit exactly as `queue3_gpu0_20261111.sh` does it (`random,best_of_n,
random_verdict --subset-n 0`, then `cem_seeded` in its own work directory sharing the samples, then
`--compare-reference` for both); C, the 15 RL runs (`rl_queue.py --make ... --seeds 0,1,2`, default learner
`frozen` = `dc.rl.FROZEN`, the committed one; queue and checkpoint list under `wm2-cache/rl/`, not in the fleet
checkout), then `--queue ... --gpu 0`.

Nothing of B20 is running. No `test` selection result was read. No git commits.

## R. Round 2 

### R1. Second coverage store `train_cov2`: builders under competent budgets
- Settings table (`gen_data.py cov2-settings`, output `cov2_settings.json`; per-start arrays in
  `wm2-cache/data/cov2_const/`): for each of the 228 training starts, the 2,625 constant plans (`dc.frontier.GRID`, no
  macro) replayed for 24 months on one seed per start, `seed_for('b20-cov2-const', start_id, 24)`, disasters off,
  plain and with the recover task's earthquake (kind 3) forced in month 0: 1,197,000 replays, 28,728,000 engine
  city-months, 2,471 s on 16 local workers. Per family the 3 best settings by `dc.frontier.J` of the family's variant
  (grow, solvent, treasury_rev on the plain replays; recover on the earthquake replays), ties by slack then grid
  order (the frontier's own ranking of constants); union per start, deduplicated: 3 to 12 settings (mean 8.42),
  1,920 in all, of which 0.571 at tax <= 4, 0.322 with all three funding lines at 0, 0.180 both. Recover lists: 684
  settings, 0.832 at tax <= 4. Every start's best setting is feasible in every family. No held-out start,
  threshold or frontier plan enters (statistic and clauses only).
- Generator: spec `train_cov2` (`behaviour: listed`, `settings_file`, `quake_every: 5`, `avoid_seeds_of:
  [train_eval, heldout_eval, train_cov]`); `dc.behaviour.sample_listed_behaviour` (style uniform over seven, then
  a setting uniform over the start's list) and `HeldBudget(..., forced=)` (writes the forced event; default none,
  so `train_cov` is unchanged); trajectory j with j % 5 == 4 gets the earthquake in month 0 and a setting from
  the start's recover list. The settings file's sha256 and the forced event are in the store's generation config.
- Existing outputs unchanged: `regen_check.json` (rerun after the round-2 edits) 500 of 500 trajectories of each of
  train_full, heldout_eval, train_eval and train_cov regenerated identical (plan, final hash, label, seed, start,
  disasters flag); train_cov's job config equal to its stored one. Tests: 28 passed (`test_data.py`,
  `test_behaviour.py`; new: the listed split with a stand-in, the selection rule on constructed scalars, the
  listed behaviour with the forced earthquake in the engine).
- Store `<cache>/data/train_cov2`: 25,000 trajectories, 600,000 transitions, 625,000
  observations, 27,039,694,654 bytes; 199 s on 16 workers (3,017 city-months a second). Verify by re-replay of all
  25,000 trajectories: 0 mismatched (`verify_train_cov2.json`); manifest 16 files, 0 mismatched.
  `store_checks_train_cov2.json`: engine seeds 25,000 distinct, 0 shared with train_full, train_eval,
  heldout_eval or train_cov (and train_cov 0 shared with train_cov2); 60 families, 228 starts, 0 held-out starts,
  disasters flag off everywhere, budget held in every trajectory, every setting in its start's list (0 outside),
  5,000 trajectories with the earthquake in month 0 and no other forced event (0 wrong); styles 3,513 to 3,630
  each; setting positions uniform within lists (for example lists of 3: 1,749 / 1,679 / 1,652).
- Bookkeeping caches (same function as `train_full.npz`): `bookkeeping_cache/train_cov.npz` (copied from the
  scratch build of round 1, sha256 262d3530...) and `train_cov2.npz` (built in 122 s).

### R2. The union and its coverage (`coverage_table.md`)
Union `wm2-cache/data/train_full_cov12` (`dc.data.make_union` of tag ladder-v2-cov; parts train_full, train_cov,
train_cov2): 99,000 trajectories, 4,200,000 transitions, 4,299,000 observations.

| | train_full | train_cov | train_cov2 | union | frontier plans |
|---|---|---|---|---|---|
| building months | 731,820 | 154,367 | 204,582 | 1,090,769 | 3,059 |
| share at tax <= 4 | 0.069 | 0.311 | 0.603 | **0.204** | 0.644 |
| share with all funding at 0 | 0.002 | 0.009 | 0.336 | **0.066** | 0.441 |
| tax <= 4 and all funding at 0 (count) | 314 | 420 | 41,519 | **42,253** | 1,126 |
| the same, share | 0.000 | 0.003 | 0.203 | 0.039 | 0.368 |
| transitions at or after a forced earthquake | 72,864 (1,858 traj., 35 in month 0) | 0 | 120,000 (5,000 traj., all month 0) | 192,864 | - |

### R3. Launch
- `cd <home>/development/wm2-ladder-v2-cov && nohup .../python code/scripts/ladder.py --queue
  <cache>/ckpt/queue_cov_gpu0.json --gpu 0 --ckpt-root
  <cache>/ckpt/ladder_v2 >> <cache>/ckpt/cov_gpu0.out` at
  2026-11-11T15:46:21Z. PIDs: ladder.py 1597473 (its shell 1597470, in `cov_gpu0.pid`), train_run.py 1597490.
  Logs: `ckpt/cov_gpu0.out`, `ckpt/ladder_v2/ladder_gpu0.log`, `ckpt/ladder_v2/os_50m_cov.out`,
  `ckpt/ladder_v2/os_50m_cov/log.jsonl`. Resume: the same command.
- First lines: normalisation statistics from 51,200 transitions; third-stage data 4,200,000 rows; 52,880,043
  parameters (as os_50m_full); argv equal to os_50m_full's but for `--run` and `--index`. `config.json`: store
  `train_full_cov12`, index 4,200,000, bookkeeping sources the three caches. Losses at 2,560 / 5,120 / 7,680 / 10,240
  samples: 0.716 / 0.682 / 0.636 / 0.596 (os_50m_full: 0.706 / 0.682 / 0.646 / 0.595). GPU memory 25.1 GB.
- Both new stores are sampled: all six loader workers map the files of train_full, train_cov and train_cov2; the
  run's own index stream (seed 0, batch 128) draws 0.714 / 0.143 / 0.143 from the three parts over its first 2,000
  batches (expected 0.714 / 0.143 / 0.143).
- Rate: 404 to 494 samples a second in the first steps on the shared card (os_50m_full: about 690 unshared; 590 on
  average over its whole run). Projected end of training about 20:00 to 20:30Z (4.2 to 4.7 h at the os_50m_full
  ratio of whole-run to early rate), then the ladder's fidelity evaluation (dev, test, train_eval; about 17 min
  unshared). Not a measurement of the end; check `log.jsonl`.

### R4. After training
`B20_after_training.sh` updated: audit (B) and RL (C) for `os_50m_cov/samples_006000000`. The audit's
`--model-src auto` resolves to the checkpoint's commit (ladder-v2-cov); `fast_check_cov.json` shows `dc.fast` accepts
it (tiny checkpoint written by the cov checkout's Trainer, git record 0b822c4 with no dirty files; loaded with
`dc.audit.load_emulator(..., "auto")`; Trunk/Block and ScalarStage sources equal the ladder-v2 reference; `model.py`
byte-identical between the tags; on CPU the accelerated trunk equals the fused one and the fused one equals the
tag's trunk with maximum absolute difference 0.0). RL runs pass `--model-src ladder-v2-cov`; the RL queue's
construction was dry-checked into the working directory (15 runs, learner `frozen` = `dc.rl.FROZEN`).

Side effect: the check extracted the ladder-v2-cov `dc` package into the audit cache
(`wm2-cache/audit/model_src/0b822c419081`), as any audit of this checkpoint would.
