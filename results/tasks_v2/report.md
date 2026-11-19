# Task difficulty and thresholds v2, H = 24 

Saved by the coordinator from the builder's hand-back (the builder could not write this file). Engine only; no emulator involved. Generated tables: `tables_H24.md`; per-instance records: `instances_H24.json`. Adopted file: `data/tasks_v2_H24.json` (treasury in its revenue form, called `treasury_rev` below; seven instances with no headroom left out; see study protocol).

I've finished the H = 24 study, including your 32-seed majority stage. I did not start H = 12, 60 or 120. Nothing of mine is still running on either machine. The harness would not let me write `results/tasks_v2/report.md` (it blocks report files from assistant), so the report text is below the hand-back. All tables are generated in `results/tasks_v2/tables_H24.md`.

**Majority rule at theta32(0.5).** m32 is the 16th largest of the 32 feasible statistics, so a plan passes when at least 16 of 32 seeds pass; an exact 16 passes. Entries are pass shares of 100-plan seeded subsets. "Well posed" counts instances; CE runs are selected on the primary seed as before.

| family | well posed | majority: beh / bld / b / c | CE majority, B = 10 / 100 / 1k / 10k (beh init; bld init) | oracle seed 0 alone: beh / bld / b / c; 20 constants; CE 10k beh / bld |
|---|---|---|---|---|
| grow | 36/40 | .051 / .101 / .206 / .327 | .025 / .025 / .150 / .200; .000 / .075 / .175 / .200 | .057 / .105 / .243 / .349; .050; .275 / .350 |
| solvent | 20/40 | .009 / .014 / .089 / .113 | .075 / .075 / .200 / .250; .025 / .075 / .150 / .325 | .030 / .039 / .134 / .143; .150; .350 / .350 |
| treasury_v2 | 24/40 | .001 / .000 / .010 / .000 | .026 / .053 / .368 / .579; .026 / .026 / .079 / .132 | .000 / .000 / .008 / .000; .104; .526 / .132 |
| recover | 13/40 | .055 / .102 / .262 / .436 | .025 / .125 / .150 / .150; .125 / .175 / .150 / .200 | .101 / .149 / .296 / .380; .250; .300 / .325 |
| power | 40/40 | .125 / .230 / .176 / .338 | .000 / .100 / .200 / .400; .000 / .125 / .225 / .450 | identical to majority (the statistic doesn't vary by seed); constants .000 |
| treasury_rev | 39/40 | .041 / .043 / .092 / .108 | .000 / .000 / .125 / .600; .000 / .075 / .075 / .425 | in the tables |

- **Constants:** wherever e32 > c32, the 20 constants pass the majority rule 0 times at every lambda (verified).
- **Where the majority rule fails: 18 of 240.** Not patched.
  - e32 ≤ c32 (ties included): solvent ho-g-05, 32; treasury_v2 ho-g-03, 05, 06, 08, 12, 14, 20, 26, 32; recover ho-g-28, 31, 36, 37, 39.
  - treasury_v2 ho-g-16: c32 = −inf, because no constant keeps the population on 16 of 32 seeds.
  - treasury_v2 ho-g-21: no frontier plan from the nine-seed rule. theta is null for ho-g-16 and ho-g-21.
- **The nine-seed rule as briefed breaks.** It is well posed in only 73 of 200 instances, and e ≤ c in 47 of 200. The reason: c is a maximum over 2,785 single replays, and 119 of 200 times it came from a secondary seed, while e is a nine-seed mean. At that rule's theta(0.5), the CE plan picked at B = 10,000 passes its own primary seed in 75 to 98 per cent of grow, solvent and recover instances, but the other eight seeds only 7 to 11 per cent of the time.
- **The current thresholds are too easy, confirmed.** Some constant plan passes on some seed (full grid, all nine seeds): grow .900, solvent 1.000, treasury 1.000, recover 1.000, power .100. On the 567-plan grid and the primary seed I get exactly your table.
- **Treasury:**
  - v1 has no headroom: well posed 0 of 40, and the best plan is tax 20 with no funding.
  - v2 is degenerate in small cities: 1 of 12 under 15,000 people is well posed. In large cities its headroom (up to 13,584 dollars) comes from raising the tax to 19–20 in the month before the yearly collection, not from building.
  - The alternative I tested is `treasury_rev`: tax collected at the last yearly budget ≥ theta, funds never negative, tax never above the starting rate. Its frontier plans build in 40 of 40 instances; it is well posed in 18 of 40 (nine seeds) and 39 of 40 (majority).
- **Cross-check against `dc.tasks`:** your `oracle_value` equals my `majority_value` on all 160 constant-and-frontier sets for grow, solvent, recover and power. treasury_v2 can't be checked yet because `dc.tasks` has no population clause as of 08:05Z; that test skips until it does.
- **Files:**
  - `code/dc/frontier.py`, `code/scripts/task_frontier.py`, `code/tests/test_frontier.py` (22 passed, 1 skipped, 1.3 s).
  - `data/tasks_v2_H24.json`: theta = theta32(0.5), the nine-seed fields under their present names plus `theta_l50` (the nine-seed theta(0.5), since `theta` now holds theta32), and `meta.oracle`.
  - `results/tasks_v2/tables_H24.md` and `instances_H24.json`.
  - `wm2-cache/tasks_v2/H24/<start_id>.npz`, 40 files.
- **Counts:** 8,637,968 replays run (207.3 M city-months, 6.13 M of them on host-b) and 166,000 closed-loop rollouts. The oracle stage was about 65 M city-months.

---

**Report**

**1. Majority rule, more detail**

| family | e32 > c32 | (e32 − c32) / SE, quartiles | (e32 − c32) / stat_sd, quartiles | seed_sd32 / stat_sd, median | frontier plan feasible on all 32 seeds |
|---|---|---|---|---|---|
| grow | 40/40 | 8.00, 13.61, 19.49 | 0.36, 0.78, 1.60 | 0.340 | 40/40 |
| solvent | 38/40 | 3.29, 6.02, 10.17 | 0.15, 0.35, 0.83 | 0.299 | 40/40 |
| treasury_v2 | 29/40 | 2.62, 27.39, 93.84 | 0.00, 0.10, 0.70 | 0.015 | 14/40 |
| recover | 35/40 | 1.57, 4.28, 7.83 | 0.16, 0.85, 1.46 | 0.767 | 40/40 |
| power | 40/40 | inf (seed sd 0) | 3.37, 4.29, 5.07 | 0.000 | 39/40 |
| treasury_rev | 40/40 | 17.54, 20.96, 31.52 | 0.82, 1.35, 1.95 | 0.306 | 40/40 |

- The standard error is 1.2533 × seed_sd32 / √32. Where seed_sd32 = 0, well posed means e32 − c32 > 0.
- The 100-plan subsets use `seed_for("tv2-oracle-subset", start, H, source)` for the two pools and `(start, variant, H, source)` for sources b and c.
- The lambda = 0.25 and 0.75 tables are in `tables_H24.md`.

**2. The nine-seed rule as briefed** (pass rates at theta(0.5): pools on the primary seed; CE on the eight secondary seeds)

| family | e > c | well posed | (e − c) / seed sd | (e − c) / stat_sd | seed sd / stat_sd | beh / bld / b / c | CE beh init, B = 10 / 100 / 1k / 10k |
|---|---|---|---|---|---|---|---|
| grow | 39/40 | 10/40 | 0.85, 2.85, 4.03 | 0.14, 0.55, 1.38 | 0.33 | .023 / .047 / .124 / .187 | .037 / .028 / .091 / .109 |
| solvent | 24/40 | 2/40 | −0.18, 0.51, 1.79 | −0.06, 0.10, 0.29 | 0.25 | .005 / .006 / .082 / .082 | .037 / .041 / .056 / .069 |
| treasury_v2 | 27/40 | 20/40 | −0.55, 5.28, 19.44 | −0.01, 0.08, 0.63 | 0.01 | .000 / .000 / .031 / .004 | .016 / .051 / .279 / .564 |
| recover | 23/40 | 1/40 | −0.31, 0.33, 0.94 | −0.18, 0.17, 0.61 | 0.60 | .022 / .041 / .133 / .184 | .028 / .103 / .100 / .081 |
| power | 40/40 | 40/40 | inf (seed sd 0) | 3.37, 4.29, 5.07 | 0 | .121 / .224 / .172 / .332 | .000 / .100 / .200 / .391 |

Where it breaks, in plain terms:
1. **c and e are not like for like.** c exceeds the best constant's own nine-seed mean by a median 1.3 to 1.6 seed sd. For comparison, the expected maximum of nine normal draws is 1.49 sd.
2. **e ≤ c in 47 of 200 instances:** grow 1, solvent 16, treasury_v2 12 plus 1 undefined, recover 17, power 0. In those instances constant plans pass at theta(0.5); over all 200 that is 0.3 per cent of constant plans on the primary seed. Where e > c it is exactly 0 on the primary seed. On the full grid across the eight secondary seeds, 0.6 per cent still pass.
3. **The engine's own seed noise is large.** Over 24 months it is 0.25 to 0.60 stat_sd for grow, solvent and recover, against a median headroom of 0.10 to 0.55 stat_sd.
4. **In power, "4 seed sd" means nothing.** The zone count doesn't vary by seed, but the headroom is real: 25 to 46 zones at the quartiles.

**3. Frontier plans**
- **Source:** the frontier plan came from closed-loop builders (c) in 36 per cent of instances, cross-entropy search (d) 27 per cent, budget-overwritten pools (b) 21 per cent, raw pools (a) 16 per cent.
- **Grow, solvent, recover, power:** the frontier plans build, 1.5 to 2.0 macros a month (roads, wires, all three zone types; power adds a plant and stations), with tax 0 to 4 and funding cut. Two-thirds keep one budget all 24 months.
- **Best constant setting:** funding at 0 on all three lines in 198 of 200 instances; ties go to the larger feasibility slack, which picks the cheapest setting.

**4. Treasury**

**v2 split by city size and the tax calendar.**
- Funds change only at the engine's yearly budget, twice in 24 months.
- In small cities yearly tax income is 35 to 1,000 dollars, and building cannot pay for itself within 24 months.
- ho-g-23 shows the large-city mechanism: tax 20 in months 7 and 19, with collections at boundaries 8 and 20, gives +8,460 dollars over the best constant.

**Why `treasury_rev`.** Any statistic that is funds at H is maximised by spending nothing and is set by the budget columns: maximum tax for v1, the population-safe tax plus a collection-month spike for v2. A treasury task with real headroom has to reward the tax base instead.
- `treasury_rev`'s statistic is the engine's `tax_fund`, a treasury scalar.
- The tax cap removes both the maximum-tax corner and the collection-month spike.
- Its stat_sd is recomputed from the calibration trajectories (same definition as v1). It has no v1 threshold.
- Its frontier plans build in every instance, with tax 4 to 7.

**5. Method**
- **Engine access:** every replay goes through `EngineJudge` (shared cache, local pools, host-b's `serve`). The only exception is source c's closed-loop rollouts, which follow the `gen_builder_pool.py` pattern.
- **host-b check:** at every driver start, the start file's sha256 was compared and 12 check plans were replayed on both machines; they were byte-identical every time. I copied no files to host-b.
- **Choices where the brief was silent** (all in the JSON `meta`):
  - J of an infeasible trajectory is −1e9 plus the violated clause's slack.
  - The best constant settings are ranked by J on the primary seed, ties broken by slack then grid order. Without the slack tie-break, the three "best" settings differed only in a funding line that doesn't move the statistic.
  - Source c uses its own closed-loop seed and applies the task's forced events during the closed loop.
  - CE is initialised from the pool's per-column fit, with every month's tax and funding means moved to the best constant (sds as fitted).
  - Seed sd uses ddof = 1.
