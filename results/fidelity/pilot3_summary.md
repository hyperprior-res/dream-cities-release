# Pilot 3: the scalar pathway, spatial first and scalars second

## What changed (code/dc/model.py `ScalarStage`, `ModelConfig.scalar_stage = "twostage"`)

The step is factorised as p(next tiles, flags, power, overlays | state, action, z), unchanged, times
p(next scalars | next spatial state, current state, action). The second stage is trained teacher-forced
on the engine's next spatial state and, in `sample_next` and every rollout, is fed the model's own
sampled next spatial state, so the dreamed scalars follow the dreamed map. Its inputs:

* changed-tile key tables: per tile a key = code x 16 + (zone, burnable, powered flag, power map) bits;
  for every tile whose key differs between the current and the next map, the sum of e[key_next] -
  e[key_cur]. Unchanged tiles contribute exactly zero, so a change in any per-tile count is
  representable exactly (sum-pooled, not mean-pooled) and the sum runs over the changed tiles only.
  One table has one column per learned scalar and is added directly to the location of that scalar's
  change distribution (in units of its delta scale); a second feeds the network;
* a changed-tile network on (current code, next code, action raster at the tile, listed price per tile,
  key bits), sum-pooled, with the same two outputs (location and features): the month's spend is
  visible as the map change inside the action footprint, priced by the listed price;
* the next and current overlays through a per-cell network, pooled; the trunk's pooled features, which
  carry the conditioning vector (normalised scalars, month of year, action scalars, listed price, z);
* variant pilot3_lv adds an absolute histogram of the next map's keys (sum over all tiles of a learned
  32-vector per key); variant pilot3_dc instead feeds the raw conditioning inputs to the second stage.

Its output is the same family as before (per learned scalar: point mass on "no change" plus a
3-component discretised logistic over the integer change; the log-scale floor is e^-9 of the delta
scale, so it can be very narrow). Everything is learned; no engine formula, rule or identity is
written into the second stage. The three bookkeeping identities derived since pilot 1 (tax = the
action's tax, city_time + 4, pop = 20 x (res + 8 x (com + ind))) are still derived, as confirmed after
the first report; if rule 3 of the brief is meant to cover them they can be turned back into heads.

Training: the scalar terms of transitions whose month contains the yearly budget (city_time mod 48 >= 44;
measured: every budget landing in heldout_eval follows city_time mod 48 = 44, 6,000 of 72,000
transitions) are weighted 6 (`--budget-weight 6`); the two changed-tile tables use 10 times the
learning rate (`--table-lr-mult 10`), because each entry is updated only when its key changes.
Spend features (listed price) kept. Same schedule as pilot 2 (AdamW 8e-4, warm-up 3%, cosine to 5%,
batch 128, 600,000 samples).

## Diagnostics (held-out, from the runs)

* Changed-tile tables help: pilot3_ts at 150k, held-out scalar NLL 26.34 nats; the same checkpoint
  with the tables zeroed 28.65; pilot 2 at 150k 26.36.
* z is not a scalar shortcut: pilot3_ts at 600k, held-out scalar NLL with posterior z 19.94, prior
  sample 20.16, prior mean 20.02 (pilot 2 at 600k: 23.59).
* Teacher-forced, pilot3_ts at 150k gets the funds change exactly in 78.5% of non-budget months
  (mean |error| 67.5); budget months median |error| 236.
* Funds outside the budget month are exactly minus the charged cost (60,000 of 60,000 held-out months),
  and the second stage now follows the map: funds median relative error at 12 months went from 0.29
  (pilot 2) to about 0.07.
* Training scalar NLL keeps falling at the end (last-tenth slope -1.7% per 100k samples for
  pilot3_ts, -1.2% for pilot3_lv; pilot 2 was flat at +0.01%); tile terms fall about 2.3% per 100k
  in all runs (results/fidelity/pilot3_ts/last_tenth_slopes.json).

## What limits the 1-month scalar ratio (target 0.6, missed)

The 1-month figure is the mean over 18 scalars of (model error / copy-last-state error) for one sampled
month from the 500 plans' start states. With the second stage it fell from 1.69 to about 0.84; the mean
of the K = 8 samples is about 0.67 and the engine floor 0.20. On 2,000 random held-out transitions the
same ratio is 0.87 sampled, 0.64 at the mode, 0.26 for the engine. Two groups keep it above 0.6:

* valves and score: deterministic in the engine at one month (floor 0.00 to 0.04), the model 1.0 to 1.3
  sampled and 0.8 to 1.0 at the mean of K. Neither the absolute map histogram (pilot3_lv) nor feeding
  the raw scalars directly (pilot3_dc) changed them at 300k (valve ratios 2.08/1.56/1.34,
  2.11/1.56/1.35, 2.17/1.56/1.32; held-out valve NLL 11.17, 11.05, 11.05 nats), so the limit is how
  fast the network learns the valve update (a clamped function of census ratios and tax applied twice a
  month), not missing inputs; their NLL is still falling;
* map counts whose copy error at one month is near zero (powered zones copy MAE 0.06, coal plants
  0.004, nuclear 0.01): the count follows the dreamed map exactly as designed, so any spatial error
  (a plant the engine refused, a power change) shows as a ratio above 1. That is now a spatial-stage
  error.

Sampling noise is the rest: the mean of K is 0.15 to 0.2 below one sample, because the second stage's
distributions are still broader than the engine's near-deterministic scalars.
# Pilot 3: the scalar pathway (two-stage factorisation)

All runs: 50M, one-step, 600,000 samples (600,064 consumed) on train_full, batch 128, the pilot-2 schedule;
evaluation as pilot 2 (2,000 held-out transitions, 500 held-out 24-month plans, K = 8, decoding b, same
selection key). Pilot 2 was re-evaluated with the current evaluation code for the reference column.

## Targets at 600k samples

| run | samples | 1-month scalar ratio, sampled (<= 0.6) | mean of K | funds med. rel. 12 m (<= 0.15, falling) | pop med. rel. 12 m (<= 0.066) | structural F1 1 m, T=1 (>= 0.15) | 24-month scalar ratio |
|---|---|---|---|---|---|---|---|
| pilot2 (pooled scalar head) | 600,064 | 1.694 | 1.529 | 0.2908 | 0.0674 | 0.1497 | 0.858 |
| pilot3_ts (two-stage) | 300,032 | 1.326 | 0.983 | 0.1469 | 0.0656 | 0.1363 | 1.035 |
| pilot3_ts (two-stage) | 600,064 | 0.845 | 0.665 | 0.0727 | 0.0660 | 0.1490 | 0.693 |
| pilot3_lv (+ next-map level histograms) | 300,032 | 1.360 | 0.982 | 0.1531 | 0.0593 | 0.1363 | 1.015 |
| pilot3_lv (+ next-map level histograms) | 600,064 | 0.840 | 0.682 | 0.0724 | 0.0574 | 0.1508 | 0.658 |
| pilot3_dc (+ direct conditioning inputs) | 300,032 | 1.306 | 0.930 | 0.1600 | 0.0710 | 0.1370 | 1.030 |
| pilot3_dc (+ direct conditioning inputs) | 600,064 | 0.831 | 0.668 | 0.0991 | 0.0650 | 0.1458 | 0.687 |

Engine floor (other seed): 1-month scalar ratio 0.204, funds 12 m 0.0026, pop 12 m 0.0259; structural F1 0.2074.

## 1-month error ratio to copy-last-state per scalar at 600k (sampled; engine floor beside)

| scalar | floor | copy MAE | pilot2 | pilot3_ts | pilot3_lv | pilot3_dc |
|---|---|---|---|---|---|---|
| funds | 0.00 | 439.344 | 1.63 | 0.69 | 0.66 | 0.69 |
| res_valve | 0.04 | 55.448 | 1.31 | 1.37 | 1.26 | 1.33 |
| com_valve | 0.04 | 112.980 | 1.03 | 1.23 | 1.11 | 1.10 |
| ind_valve | 0.00 | 126.048 | 0.94 | 1.04 | 0.99 | 0.96 |
| pop | 0.81 | 346.520 | 1.04 | 0.88 | 0.86 | 0.87 |
| res_pop | 0.77 | 9.458 | 0.96 | 0.73 | 0.74 | 0.74 |
| com_pop | 0.87 | 0.964 | 1.14 | 1.08 | 1.11 | 1.09 |
| ind_pop | 0.90 | 1.162 | 1.13 | 0.84 | 0.82 | 0.84 |
| score | 0.02 | 46.632 | 1.04 | 1.34 | 1.29 | 1.24 |
| tax_fund | 0.00 | 128.294 | 0.47 | 0.31 | 0.40 | 0.37 |
| road_spend | 0.01 | 45.186 | 0.27 | 0.26 | 0.29 | 0.26 |
| fire_spend | 0.00 | 30.800 | 0.41 | 0.58 | 0.64 | 0.83 |
| police_spend | 0.00 | 39.200 | 0.30 | 0.58 | 0.52 | 0.56 |
| powered_zones | 0.00 | 0.062 | 2.81 | 1.25 | 1.51 | 1.12 |
| unpowered_zones | 0.00 | 0.354 | 1.10 | 0.51 | 0.50 | 0.55 |
| coal_plants | 0.00 | 0.004 | 11.31 | 1.25 | 1.19 | 1.06 |
| nuclear_plants | 0.00 | 0.012 | 3.10 | 0.96 | 0.88 | 0.98 |
| road_total | 0.22 | 37.286 | 0.51 | 0.33 | 0.35 | 0.37 |

## Verdict

pilot3_lv (two-stage plus absolute next-map histograms) meets three of the four targets at 600k: funds
median relative error at 12 months 0.0724 (bar 0.15; falling from 0.1531 at 300k), population 0.0574
(bar 0.066), structural changed-tile F1 0.1508 sampled (bar 0.15). It misses the 1-month scalar ratio:
0.840 against 0.6, by 0.24 (pilot 2: 1.694; engine floor 0.204). pilot3_dc has the lowest 1-month ratio
(0.831) but misses F1 (0.1458) and is worse on funds (0.0991); pilot3_ts sits between. The structural F1
of the three runs (0.1458 to 0.1508) varies with an unchanged spatial stage, by less than the family
bootstrap interval (about +-0.02). Recommended configuration for the ladder: pilot3_lv
(`--budget-weight 6 --table-lr-mult 10 --model-overrides '{"ss_level_dim": 32}'`).

## Files

* per variant: results/fidelity/pilot3_<ts|lv|dc>/comparison.md (against pilot 2, same table format),
  ck300k/ and ck600k/ (evaluation JSON, summary.md, funds_split_*.md / .json by behaviour type and budget
  month, training_curves.png at 600k); funds_split of pilot 2 copied beside;
* results/fidelity/pilot3_ts/last_tenth_slopes.json (pilot 2 and the three variants);
* checkpoints <cache>/ckpt/pilot3_<ts|lv|dc>/ (150k, 300k, 600k, sha256 sidecars).
