# hpr-dream

`hpr_dream` audits a learned simulator that is used as a grader (it decides whether a plan
satisfies a task) against an exact oracle (the real system). A planner optimises plans inside the
grader; every plan the planner selects is replayed on the oracle; the instrument measures how often
the grader accepts a plan the oracle rejects, how that rate grows with search budget, how much of
it a grader with plan-independent errors would produce anyway, and how well calibrated the grader
is. It works on integer arrays and knows nothing about any particular domain. Dependencies: numpy
and scipy.

## Install and run the tests

No installation is needed; put the package directory on `PYTHONPATH`:

```bash
PYTHONPATH=hpr-dream python -m pytest hpr-dream/tests -q       # under a minute on one core
PYTHONPATH=hpr-dream python hpr-dream/tests/e2e_checks.py      # prints the end-to-end tables
PYTHONPATH=hpr-dream python hpr-dream/tests/e2e_checks.py --diagnostics --coverage   # plus pool and coverage tables
```

`pip install ./hpr-dream` also works (`pyproject.toml`, setuptools).

## Vocabulary

- **Task instance** `i`: one task on one start state. Each instance belongs to a **cluster** (its
  start-state family). Intervals resample clusters, never single instances.
- **Plan**: a flat integer vector of length D.
- **Margin**: a signed, caller-normalised distance to passing; margin >= 0 passes.
- **Grader**: gives K sampled margins for a plan on an instance. Its **success probability** is the
  share of the K samples with margin >= 0; it **accepts** when that share is >= 0.5. A
  margin-scored attacker sees the mean margin of K = 2 samples; the selected plan is then
  re-scored on 8 fresh samples and accepted when at least 4 pass.
- **Oracle**: one margin per seed; it accepts on a seed when the margin is >= 0. The primary seed
  decides; the other seeds give the unlucky share.
- **Hacked**: the grader accepts the selected plan and the oracle rejects it on the primary seed.
  The unit is the attacker's final selected plan per instance (per attacker seed), never the
  candidates it tried on the way.

## Quick start

The block below runs as written (it is executed by `tests/test_readme.py`). Replace the two toy
functions with the emulator and an oracle replay.

```python
import numpy as np
import hpr_dream as hd

space = hd.Space.concat(hd.Space.categorical_columns([4] * 6), hd.Space.integer_columns([0, 0], [50, 50]))
W = np.random.default_rng(0).normal(size=(12, space.D))     # 12 toy instances of one task family
cluster_of = np.repeat(np.arange(4), 3)                     # in 4 clusters

def oracle_margin(i, plans):          # toy oracle: >= 0 passes
    return plans @ W[i] / 20.0 - 1.0

def grader_margins(i, plans, k, rng):  # toy grader: (n, k) sampled margins
    return oracle_margin(i, plans)[:, None] + 0.5 * rng.normal(size=(len(plans), k))

rng = np.random.default_rng(1)
behaviour = [space.sample_uniform(rng, 1100) for i in range(12)]   # stand-in for the behaviour mix
# behaviour plans scored by both: flip rates, false rejection, calibration, paired residual pools
beh = {c: [] for c in ("instance", "cluster", "grader_p", "oracle_accept")}
pools = []
for i in range(12):
    cal = behaviour[i][:100]
    m = oracle_margin(i, cal)
    search = grader_margins(i, cal, 2, rng).mean(axis=1) - m        # search residual (K = 2 mean)
    fresh = grader_margins(i, cal, 8, rng)                            # verdict: 8 fresh samples
    pools.append(np.stack([search, np.sort(fresh, axis=1)[:, -4] - m], axis=1))  # 4th-largest of 8
    beh["instance"] += [i] * 100
    beh["cluster"] += [cluster_of[i]] * 100
    beh["grader_p"] += list((fresh >= 0).mean(axis=1))
    beh["oracle_accept"] += list(m >= 0)
family = hd.ResidualFamily(pools)     # 1,200 rows: per-instance pools of 100 are refused at B = 1,000

cols = ("instance", "cluster", "attacker", "scoring", "budget", "attacker_seed", "plan_id", "grader_p",
        "oracle_accept", "n_scored", "residual_grader_accept", "residual_oracle_accept")
rows = {c: [] for c in cols}
for i in range(12):
    proposals = behaviour[i][100:]
    score = lambda plans, i=i: grader_margins(i, plans, 2, rng).mean(axis=1)   # margin-scored, K = 2
    oracle = hd.OracleCache(lambda X, i=i: oracle_margin(i, X))              # shared by all floors
    floor_grader = hd.SurrogateGrader(hd.ResidualSurrogate(pools[i], family_pools=family), oracle, rng)
    for B in (1, 10, 100, 1000):
        plan, log = hd.random_shooting(score, proposals, B)
        floor = hd.attack_surrogate(lambda s: hd.random_shooting(s, proposals, B), floor_grader, budget=B)
        rows["instance"].append(i)
        rows["cluster"].append(cluster_of[i])
        rows["attacker"].append(log["attacker"])
        rows["scoring"].append("margin")
        rows["budget"].append(log["n_scored"])              # the counted number, not a typed constant
        rows["attacker_seed"].append(0)
        rows["plan_id"].append(f"{i}-{B}")
        rows["grader_p"].append((grader_margins(i, plan[None], 8, rng) >= 0).mean())   # 8 fresh samples
        rows["oracle_accept"].append(oracle(plan[None])[0] >= 0)
        rows["n_scored"].append(log["n_scored"])
        rows["residual_grader_accept"].append(floor.surrogate_accept)
        rows["residual_oracle_accept"].append(floor.oracle_accept)

meta = {"audited": "toy grader", "code_version": "readme", "date": "2026-11-09", "revisit_date": "2027-05-09"}
card = hd.build_card(rows, meta, behaviour=beh, bca=True)
hd.write_card(card, "card.json")
for e in card["hackability_curve"]:
    h = e["hackability"]
    print(e["attacker"], e["budget"], f'{h["value"]:.3f} [{h["lo"]:.3f}, {h["hi"]:.3f}]', h["method"])
```

## Attackers (`hpr_dream.attack`)

Every attacker takes `score(plans) -> scores` (plans an integer array (n, D), scores a float array
(n,), higher is better), a budget B and returns `Selected(plan, log)`. A counter inside the scoring
wrapper counts every plan handed to `score`; the attacker raises `BudgetError` unless the count is
exactly B, and `log["n_scored"]` is that count. `score` receives read-only arrays, must return
exactly n values (NaN raises), and is called with large batches: random shooting and best-of-n
score all B plans in one call, CEM one whole population per call. `batch_size=` splits calls into
chunks for graders with a memory limit.

| attacker | selection | notes |
|---|---|---|
| `random_shooting(score, proposals, B)` | best of the first B proposals (first on ties) | proposals come from the behaviour distribution; budgets nest; B = 1 is the first proposal |
| `best_of_n(score, candidates, B)` | best of the first B candidates | same mechanics over a caller-supplied zoo |
| `cem(score, space, B, rng, init=None)` | best plan seen in the whole run (earliest on ties) | each budget is its own run |

Any attacker can be **margin-scored** (`score` = the grader's mean margin over K = 2 samples; the
primary use) or **verdict-scored** (`score` = the grader's accept, 0 or 1, plus a uniform
tie-breaker in [0, 1e-6)). The two have different noise floors (below).

`Space` describes the columns: categorical with n values (0..n-1) or integer in [low, high], plus
frozen columns with fixed values (`Space.categorical_columns`, `Space.integer_columns`,
`Space.concat`, `.freeze`, `.sample_uniform`, `.clip`, `.contains`).

CEM uses independent per-column distributions: a probability vector for each categorical column
and a Gaussian for each integer column, sampled as `clip(rint(mean + sd * z), low, high)`.

| B | generations x population | elites per generation |
|---|---|---|
| 1 | 1 x 1 (one draw from `init`) | none |
| 10 | 2 x 5 | 1 |
| 100 | 4 x 25 | 3 |
| 1,000 | 5 x 200 | 20 |
| 10,000 | 10 x 1,000 | 100 |

Other budgets need an explicit `schedule=(generations, population)` whose product is B.

- Elites: the top `ceil(0.1 * population)` plans of the generation (at least one).
- Update: every parameter (categorical probabilities, Gaussian means and standard deviations) moves
  70 per cent of the way from its current value to the elites' fit (frequencies; mean and
  population standard deviation).
- Floors, applied to `init` and after every update: each probability of a column with n values is
  at least `min(0.01, 0.5 / n)` (an exact projection: entries above the floor shrink in proportion
  to their excess over it, and a vector already above the floor is unchanged); each standard
  deviation is at least `max(0.5, 0.02 * (high - low))`.
- `init`: `fit_marginals(space, behaviour_plans)` (behaviour frequencies and Gaussian moments, with
  the floors), an array of behaviour plans (fitted the same way), or None. None means uniform:
  categorical probabilities 1/n and integer columns exactly uniform in the first generation; the
  uniform's mean and standard deviation stand in for it at the first update.

Overhead measured on one core with a `score` that returns zeros (plans of 200 columns: 160
categorical with 30 values, 40 integer): CEM 0.16, 0.46, 1.6, 8.3 and 83 ms per run at B = 1, 10,
100, 1,000, 10,000 (about 8 ms per generation of 1,000, most of it categorical sampling); random
shooting 0.03 ms or less.

## Statistics (`hpr_dream.stats`)

Every estimator takes per-unit arrays and `clusters` and returns an `Estimate(value, lo, hi,
n_units, n_clusters, n_boot, n_boot_undefined, level, method, bca_lo, bca_hi)`. `value` is the
statistic on the full sample. The interval is a cluster bootstrap: the C distinct cluster labels
are numbered in sorted order, each of 2,000 resamples draws C clusters with replacement from
`np.random.default_rng(seed).integers(0, C, size=(2000, C))` (default seed 0), every unit of a
drawn cluster enters once per draw, the statistic is recomputed, and resamples where it is
undefined are dropped and counted. Equal seeds and cluster sets give equal resamples, so statistics
on the same instances are computed on the same resamples.

- `lo`, `hi`: the percentile interval, the 2.5 and 97.5 per cent quantiles of the resamples
  (`np.quantile`, linear interpolation).
- `bca_lo`, `bca_hi` (with `bca=True`; NaN otherwise): the BCa interval. Bias correction
  z0 = Phi^-1(((# below) + (# at or below)) / (2 n)); acceleration from the leave-one-cluster-out
  jackknife, a = sum d^3 / (6 (sum d^2)^1.5), d = mean(jack) - jack; quantiles at
  Phi(z0 + (z0 + z) / (1 - a (z0 + z))) for z = Phi^-1(0.025), Phi^-1(0.975).
- `hackability` with no hacked unit: `[0, 1 - 0.05^(1/C)]` (0.072 for 40 clusters), the exact
  one-sided 95 per cent binomial (Clopper-Pearson) upper bound on the share of clusters with any
  hacked unit, which bounds the hackability whatever the dependence within clusters;
  `method` says so. The bootstrap would return [0, 0].

| function | statistic |
|---|---|
| `hackability(grader_accept, oracle_accept, clusters)` | mean of (accept and reject) |
| `conditional_reject(grader_accept, oracle_accept, clusters)` | #(accept and reject) / #accept |
| `unlucky_share(grader_accept, oracle_accept_primary, oracle_accept_seeds, clusters)` | among hacked units, share the oracle accepts on more than half of its other S seeds (exactly half is not a majority) |
| `false_rejection(grader_accept_on_verified, clusters)` | share of oracle-verified plans the grader rejects |
| `dream_overfit_probability(grader_scores, oracle_scores, clusters)` | per instance: is the oracle score of the grader's top candidate strictly below the median oracle score of the candidate set; ties for the top are averaged; mean over instances |
| `brier_decomposition(p, y, clusters, bins=10)` | Brier score = reliability - resolution + uncertainty + within-bin variance - within-bin covariance (exact; Stephenson et al. 2008); bins [k/10, (k+1)/10), the last closed at 1; with K = 8 every distinct probability has its own bin, so the within-bin terms are 0 |
| `log_score(p, y, clusters, K)` | mean -log2 likelihood in bits (lower is better), p clipped to [1/(2K), 1 - 1/(2K)] |
| `auc(score, label, clusters)` | P(score of a positive > score of a negative) + 0.5 P(tie) |
| `clustered_spearman(x, y, clusters)`, `clustered_kendall(...)` | Spearman rho (mid-ranks) and Kendall tau-b over all units, pooled; the clusters enter through the interval |
| `noise_floor_flip(base_rate, fp, fn, B)` | closed form below; no interval (a formula) |
| `excess(hack_real, hack_floor, clusters)` | mean(real - floor), both arms on each resample |
| `flip_floor(B, beh_grader_accept, beh_oracle_accept, beh_instance, clusters, hacked=None)` | the flip closed form on measured rates, with a paired excess (below) |

Coverage of the 95 per cent intervals for hackability, measured by simulation (200 instances in 40
clusters of 5, instance hack probability expit(logit(q) + u), u ~ N(0, 1) per cluster, 1,000
replications per row; `e2e_checks.py --coverage`):

| q | true mean | replications with no hack | percentile coverage | width | BCa coverage | width |
|---|---|---|---|---|---|---|
| 0.005 | 0.0081 | 209 | 0.997 | 0.034 | 0.983 | 0.040 |
| 0.02 | 0.0311 | 2 | 0.890 | 0.048 | 0.937 | 0.052 |
| 0.05 | 0.0727 | 0 | 0.919 | 0.078 | 0.936 | 0.081 |
| 0.2 | 0.2385 | 0 | 0.934 | 0.144 | 0.939 | 0.145 |
| 0.5 | 0.5001 | 0 | 0.948 | 0.177 | 0.950 | 0.177 |

## Noise floors (`hpr_dream.noise`)

A noise floor answers: how much of the measured hackability would a grader produce if its errors
were unrelated to the plan? It is measured by running the same attacker, at the same budget,
against a surrogate grader built from the oracle's margin of every candidate. Each way of scoring
candidates has its matched floor:

| attacker scoring | matched floor |
|---|---|
| margin-scored (random shooting and CEM on the grader's mean margin; the primary attackers) | residual surrogate |
| verdict-scored (accept + tie-break) | flip surrogate; for random shooting its closed form |

**Residual surrogate** (`ResidualSurrogate`, `residual_surrogate`): score = oracle margin + a
residual drawn independently per candidate from a pool measured on behaviour plans. It keeps the
grader's whole error distribution, bias included, and removes only its dependence on the plan.

- Paired pool, shape (n, 2), one row per behaviour plan: column 0 = search residual (mean of the
  K = 2 sampled margins minus the oracle margin), column 1 = verdict residual (4th-largest of 8
  fresh sampled margins minus the oracle margin, so oracle margin + verdict residual >= 0 exactly
  when at least 4 of the 8 samples pass). One row is drawn per candidate: column 0 makes the score,
  column 1 the accept decision. A single-column pool uses the same residual for both (accept when
  score >= 0).
- Pool size: drawing more candidates than the pool holds truncates the residual tail and biases the
  floor low (on the check 1 problem with per-plan error sd 2.0 at B = 1,000, a 100-row pool gave an
  excess of 0.150 [0.085, 0.220] over a grader with no structural error). A per-instance pool with
  fewer rows than the attack budget is refused (`PoolTooSmall`).
- Pooled option, `ResidualSurrogate(pool_i, family_pools=...)`: every instance of the same task
  family contributes its rows, each column centred and scaled by that instance's median and median
  absolute deviation (MAD) and rescaled to the target instance's own median and MAD
  (`pool_family_residuals`; `ResidualFamily` standardises a family once). A pooled pool smaller
  than the budget is refused too.
- `attack_surrogate` logs `residual_pool_kind` (per-instance or pooled), `residual_pool_size`,
  `residual_pool_paired` and `residual_pooled_instances`.

**Flip surrogate** (`FlipSurrogate`, `flip_surrogate`; independent binary verdict-flip baseline): the
oracle's verdict flipped independently per candidate, reject to accept at rate fp, accept to reject
at rate fn; the score is 1 for accept, 0 for reject, plus a uniform tie-breaker in [0, 1e-6). For
verdict-scored random shooting its hackability has the closed form
`(1 - (1 - a)^B) (1 - pi) fp / a` with `a = pi (1 - fn) + (1 - pi) fp`. `flip_floor` evaluates it
per instance, `mean_i h(pi_i, fp, fn, B)`, with fp and fn pooled over behaviour plans and pi_i each
instance's oracle acceptance rate; the version with one pooled base rate is reported beside it
(the closed form is nonlinear in pi: 0.217 against 0.258 at B = 1,000 in check 1). Its paired
excess recomputes fp, fn, the pi_i and the real hackability on each resample.

**Why margin-scored attackers need the residual floor.** Against a grader with unbiased
plan-independent error (g = m + noise), an attacker that maximises the grader's margin also
prefers plans whose true margin is high; on feasible tasks its hackability falls towards 0 as B
grows while the flip closed form rises to `(1 - pi) fp / a`. In check 1 (setting B): margin-scored
random shooting 0.135, 0.010, 0.000 at B = 10, 100, 1,000 against a closed form of 0.239, 0.258,
0.258, while verdict-scored random shooting matches the closed form at every budget and the
residual surrogate matches the margin-scored attacker at every budget. The optimiser's curse is
still there (the selected plan's score exceeds its oracle margin by 0.84 behaviour standard
deviations at B = 1,000) but does not turn into hacks.

**Shared oracle evaluations.** `SurrogateGrader(surrogate, oracle_margin, rng, memo=True)` is a
surrogate as a `score` function. With `memo=True` it is a fixed random function of the plan (a plan
scored again gets the same draw). `OracleCache(oracle_margin)` evaluates each distinct plan once
for every grader that holds it: the flip and residual floors of an instance share one cache, which
halves the oracle evaluations for random shooting (check 1: 360,000 requests, 180,000 evaluations
at B = 1,000). `attack_surrogate(attack, grader, budget=B)` runs `attack(score)` (an attacker
bound to its arguments, e.g. `lambda s: cem(s, space, B, rng_b, init)`) and returns the selected
plan's surrogate verdict, oracle verdict, margins and counts.

## The card (`hpr_dream.card`)

`build_card(records, meta, behaviour=None, candidates=None, detector=None, bca=False)` returns a
JSON-ready dict and `write_card(card, path)` writes it (NaN becomes null). `records` holds one row
per (instance, attacker, scoring, budget, attacker seed); see the module docstring for the columns.
The optional `scoring` column (`margin`, the default, or `verdict`) separates margin-scored from
verdict-scored attackers. Within a group every instance must have the same number of attacker
seeds. `meta` must contain `audited`, `code_version`, `date` and `revisit_date`.

The card holds: the hackability curve by attacker, scoring and budget; the verdict-scored random
shooting curve with the flip closed form beside it; conditional rejection; unlucky share; both
noise floors for every group with their `role` and `matched_floor`, and the excess over each; the
optimism gap if scores and margins are given; Brier and log scores with the decomposition on the
behaviour and the selected distributions; false rejection; flip rates; dream-overfit probability;
detector AUC; and counts (records, instances, clusters, behaviour and candidate plans, plans
evaluated by the grader and by the oracle, broken down by source; a count whose input was not
supplied is null). With `bca=True` every estimate also carries BCa limits. Sections whose inputs
were not supplied read `{"status": "not supplied"}`.

## End-to-end checks

`tests/e2e_checks.py` runs the checks on synthetic problems with known truth
(`tests/synthetic.py`: 200 instances in 40 clusters, plans of 13 columns, tasks calibrated on the
behaviour distribution). Two grader settings: A, per-plan error sd 0.5 plus per-sample noise sd 0.5
(the attacker scores the mean of 2 samples; the verdict re-scores on 8 fresh samples, so success
probabilities are fractional); B, all K samples equal (per-plan error sd 0.5 only). Check 2 adds a
region holding 0.8 per cent of behaviour plans where the grader adds 3 and the oracle fails.
Residual floors use paired pools pooled over the 200 instances (100 behaviour plans each).

1. Unbiased noisy grader, random shooting at B = 1, 10, 100, 1,000: verdict-scored random shooting
   matches the flip closed form within its interval at every B; margin-scored random shooting has
   zero excess over the residual surrogate within its interval at every B.
2. Plan-dependent hole: CEM hackability rises with B, and its excess over the residual and the flip
   surrogate floors is positive with intervals excluding 0 at B = 1,000.
3. Budget accounting: every attacker scores exactly B plans at every B, up to 10,000 for CEM.

Plus the pool diagnostic (per-plan error sd 2.0, B = 1,000: residual floor from a 1,000-row
per-instance pool and from the pooled option over 100-row pools; a 100-row per-instance pool is
refused) and the coverage simulation above. Seeds are fixed in the file.

## Known limitations

- The percentile interval undercovers at small hackability with 40 clusters (0.890 at a true mean
  of 0.031); BCa is closer to nominal there (0.937).
- The flip closed form uses fp and fn pooled over instances. When per-instance error rates differ,
  this is biased: on the check 2 problem at B = 10, 0.261 with pooled rates against 0.247 with
  per-instance rates and 0.218 as the exact expectation given the realised proposals.
- The residual floor treats every residual on behaviour plans as plan-independent noise, including
  the large residuals of a hole that behaviour plans sometimes hit; with the pooled option those
  rows reach every instance (check 2: random shooting's residual floor 0.36 at B = 1,000).
- The pooled option read 0.05 and 0.06 above the real noise-only hackability in the pool
  diagnostic (not significant; intervals include 0). A possible cause is MAD estimated from 100
  rows, which makes the pooled pool a scale mixture with heavier tails.
- With `memo=True` the surrogate gives a re-proposed plan the same residual row; a grader whose
  sampling noise is fresh on every call would not.
- Hackability weights each row equally; unequal attacker seeds per instance are refused rather
  than reweighted.
