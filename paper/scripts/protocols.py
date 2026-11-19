"""Protocol constants for Appendix B (the reinforcement-learning learner; searches and defences; other protocols) and
the instrument paragraph of Appendix C, generated from the code and from configuration and result files.

``protocols(nm)`` takes the imported ``make_numbers`` module and defines every macro the protocol text uses through
its helpers: ``nm.quote`` for a constant quoted verbatim from a code file (the value is parsed from the quoted text,
never typed beside it), ``nm.add`` for a value read from a JSON or configuration file or computed from quoted
constants. Statements of the prose that carry no number are guarded by ``need`` (a code fragment that must occur
verbatim) or ``expect`` (a condition on a file), so that if the code changes the build stops instead of printing a
stale protocol. Every macro name starts with ``Pr``. The PPO table is written to ``paper/tables/proto_ppo.tex``.
"""
from __future__ import annotations

import ast
import glob
import hashlib
import json
import math
import re
from pathlib import Path

RL = "code/dc/rl.py"
TASKS_PY = "code/dc/tasks.py"
GRAMMAR = "code/dc/grammar.py"
ENGINE = "code/dc/engine.py"
AUDIT = "code/dc/audit.py"
DEFENCES = "code/dc/defences.py"
FIDELITY = "code/dc/fidelity.py"
PATCHING = "code/dc/patching.py"
SEEDS = "code/dc/seeds.py"
BEHAVIOUR = "code/dc/behaviour.py"
RUN_RL = "code/scripts/run_rl.py"
CALIBRATE = "code/scripts/calibrate_tasks.py"
BUILDERS = "code/scripts/gen_builder_pool.py"
GEN_DATA = "code/scripts/gen_data.py"
EVAL_FID = "code/scripts/eval_fidelity.py"
LADDER_PY = "code/scripts/ladder.py"
ATTACK = "hpr-dream/hpr_dream/attack.py"
HPD_INIT = "hpr-dream/hpr_dream/__init__.py"
HPD_CARD = "hpr-dream/hpr_dream/card.py"
HPD_PROJECT = "hpr-dream/pyproject.toml"
TDMPC2 = "hpr-dream/hpr_dream/adaptors/tdmpc2.py"
TASKS_V2 = "data/tasks_v2_H24.json"
TASKS_V2X = "data/tasks_v2x_H24.json"
ENG_TABLE = "results/rl/bc/decision_table_pooled.json"
FRONTIER = "results/defences/frontier.json"
CANON = "results/fidelity/canonical_tiles.json"
BASELINES = "results/fidelity/ladder/os_50m_full/test/baselines.json"
ANIMATE = "engine/src/animate.cpp"

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
         10: "ten"}


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------
def need(nm, source, text):
    """A statement of the prose rests on this code fragment: it must occur verbatim in ``source``."""
    if text not in nm.T(source):
        raise nm.Missing(f"protocols: the text relies on {source} containing {text!r}")


def expect(nm, cond, what):
    if not cond:
        raise nm.Missing(f"protocols: the text states '{what}', and the code or result files no longer support it")


def word(nm, n, what):
    if int(n) not in WORDS:
        raise nm.Missing(f"protocols: {what} = {n} has no word")
    return WORDS[int(n)]


def num(x):
    return f"{x:g}"


def sci(x):
    """3e-4 -> 0.0003; 1e-5 -> 0.00001 (plain decimals: the paper's small tables have no math font for a
    superscript of a superscript)."""
    return f"{x:.10f}".rstrip("0")


def literal(text):
    """The value at the right of the last '=' of a quoted assignment, e.g. ``n_envs: int = 200`` -> 200."""
    raw = text.rsplit("=", 1)[1].strip().rstrip(",")
    return ast.literal_eval(raw)


def qlit(nm, name, text, source, fmt):
    """Quote ``text`` (an assignment) from ``source``; the macro is ``fmt`` of the value parsed from the text."""
    v = literal(text)
    nm.quote(name, text, source, fmt(v))
    return v


def regex(nm, source, pattern, what, flags=0):
    m = re.search(pattern, nm.T(source), flags)
    if not m:
        raise nm.Missing(f"protocols: {what} not found in {source} (pattern {pattern!r})")
    return m


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------------------------
# (a) the reinforcement-learning learner (dc.rl.FROZEN, run_rl.py)
# ---------------------------------------------------------------------------------------------
def _rl_configs(nm):
    """The configuration files of the runs the paper reads: every ladder run (results/rl/<checkpoint>__<family>__<seed>
    __tasks_v2_H24, as make_numbers.rl_runs selects them) and the engine-trained learner's runs
    (decision_table_pooled.json, families.*.scratch_run)."""
    ladder = []
    for p in sorted(glob.glob(str(nm.REPO / "results/rl/*__tasks_v2_H24/config.json"))):
        run = Path(p).parent.name
        if run.startswith("engine"):
            continue
        ck = run.split("__")[0]
        if nm.LADDER_RUN.fullmatch(ck.split("-samples_")[0]):
            ladder.append(p)
    engine = []
    fams = nm.J(ENG_TABLE)["families"]
    for fam in nm.FAMS:
        for r in fams[fam]["scratch_run"].split("+"):
            engine.append((fam, f"results/rl/{r}/config.json"))
    if not ladder or not engine:
        raise nm.Missing("protocols: no RL run configurations found")
    return ladder, engine


def rl_learner(nm):
    # -- the frozen learner and its run configurations -----------------------------------------------------------
    need(nm, RL, "FROZEN = replace(STAB_SPATIAL, mask_treasury_tax=True)")
    need(nm, RUN_RL, 'cfg = rl.FROZEN if args.variant == "frozen" else rl.VARIANTS[args.variant]')
    ladder, engine = _rl_configs(nm)
    cfgs = [nm.J(p) for p in ladder]
    ref = cfgs[0]["cfg"]
    for p, c in zip(ladder, cfgs):
        expect(nm, c["cfg"] == ref, f"every ladder RL run has one configuration ({p} differs)")
        expect(nm, c["meta"].get("variant") == "frozen", f"every ladder RL run uses the frozen learner ({p})")
        expect(nm, c["meta"]["emulator"]["environment_decoding"] == {"temperature": 1.0, "overlay": "sample"},
               f"the emulator environment samples every head at temperature one ({p})")
    def default(key):
        """RLConfig's default of a field (a configuration written before the field existed reads it as this,
        RLConfig.from_dict)."""
        m = re.search(rf"^    {key}: [^=\n]+ = ([^#\n]+?)\s*(#.*)?$", nm.T(RL), re.M)
        if not m:
            raise nm.Missing(f"protocols: RLConfig.{key} has no default in {RL}")
        return ast.literal_eval(m.group(1).replace("_", "") if m.group(1)[:1].isdigit() else m.group(1))

    for fam, p in engine:
        c = nm.J(p)
        keys = set(c["cfg"]) | set(ref)
        get = lambda d, k: d[k] if k in d else default(k)
        diff = {k for k in keys if get(c["cfg"], k) != get(ref, k)}
        # the s0 engine runs of four families are "stab_spatial", FROZEN without the treasury tax mask, which
        # changes nothing outside treasury
        expect(nm, diff <= {"mask_treasury_tax"} and (not diff or fam != "treasury"),
               f"the engine-trained learner has the emulator learner's settings ({p}: {sorted(diff)})")
        expect(nm, c["meta"]["environment"] == "engine", f"{p} is trained on the engine")
    expect(nm, ref["mask_treasury_tax"] is True, "the treasury tax mask is on")
    need(nm, RL, 'MASKED_TAX_TASKS = ("treasury",)')

    # -- PPO constants: quoted from the dataclass defaults and the frozen variant's line; checked against the runs
    q = {}
    for key, name, text, fmt in (
            ("n_envs", "PrEnvs", "n_envs: int = 200", nm.ints),
            ("rollout_len", "PrRollout", "rollout_len: int = 25", nm.ints),
            ("budget", "PrBudget", "budget: int = 1_000_000", nm.ints),
            ("lr", "PrLr", "lr: float = 3e-4", sci),
            ("adam_eps", "PrAdamEps", "adam_eps: float = 1e-5", sci),
            ("epochs", "PrEpochs", "epochs: int = 4", nm.ints),
            ("minibatch", "PrMinibatch", "minibatch: int = 1000", nm.ints),
            ("clip", "PrClip", "clip: float = 0.2", num),
            ("gamma", "PrGamma", "gamma: float = 1.0", num),
            ("gae_lambda", "PrGae", "gae_lambda: float = 0.95", num),
            ("ent_coef", "PrEnt", "ent_coef: float = 0.003", num),
            ("vf_coef", "PrVf", "vf_coef: float = 0.5", num),
            ("max_grad_norm", "PrGradNorm", "max_grad_norm: float = 0.5", num),
            ("init_mix", "PrInitMix", "init_mix: float = 0.9", num),
            ("init_plans", "PrInitPlans", "init_plans: int = 200", nm.ints)):
        v = qlit(nm, name, text, RL, fmt)
        expect(nm, ref[key] == v, f"the runs' {key} is the code's {v}")
        q[key] = v
    line = ('"stab_spatial": replace(B8_LEARNER, target_kl=0.02, lr_schedule="linear", ent_schedule="linear",\n'
            '                            policy=PolicyConfig(readout="spatial")),')
    need(nm, RL, line)
    m = re.search(r"target_kl=([0-9.]+)", line)
    nm.add("PrTargetKl", num(float(m.group(1))), RL, 'VARIANTS["stab_spatial"]: target_kl=0.02 (FROZEN = stab_spatial + mask)')
    expect(nm, ref["target_kl"] == float(m.group(1)), "the runs' KL target is the frozen variant's")
    for k in ("lr_schedule", "ent_schedule"):
        expect(nm, ref[k] == "linear", f"the runs' {k} is linear (decay to zero over the updates)")
    need(nm, RL, 'return self.lr * (1.0 - k / self.n_iter) if self.lr_schedule == "linear" else self.lr')
    need(nm, RL, 'return self.ent_coef * (1.0 - k / self.n_iter) if self.ent_schedule == "linear" else self.ent_coef')
    v = float(regex(nm, RL, r'acc\["approx_kl"\] > ([0-9.]+) \* cfg\.target_kl', "the KL early stop").group(1))
    nm.add("PrKlStop", num(v), RL, 'Trainer.iterate: acc["approx_kl"] > 1.5 * cfg.target_kl')
    expect(nm, ref["policy"]["readout"] == "spatial", "the runs use the spatial read-out")
    snaps = tuple(literal("s = " + regex(nm, RL, r"snapshots: Tuple\[int, \.\.\.\] = (\([0-9_, ]+\))",
                                         "RLConfig.snapshots").group(1)))
    expect(nm, list(snaps) == ref["snapshots"], "the runs' snapshots are the code's")
    expect(nm, sorted(snaps) == sorted(nm.RL_SNAPS.values()), "the snapshots are those make_numbers reads")
    nm.add("PrSnapshots", nm.words_list([nm.ints(s) for s in sorted(snaps)]), RL, "RLConfig.snapshots")
    per = q["n_envs"] * q["rollout_len"]
    nm.add("PrMonthsPerUpdate", nm.ints(per), RL, "n_envs x rollout_len (RLConfig.months_per_iter)")
    expect(nm, q["budget"] % per == 0 and per % q["minibatch"] == 0, "the budget is whole updates of whole minibatches")
    nm.add("PrUpdates", nm.ints(q["budget"] // per), RL, "budget / (n_envs x rollout_len) (RLConfig.n_iter)")
    H = int(regex(nm, RL, r"^H = (\d+)$", "the episode length H", re.M).group(1))
    expect(nm, H == int(nm.J(TASKS_V2)["meta"]["horizon"]), "an episode lasts the task horizon (\\Horizon)")
    nm.add("PrEpisodesPerUpdate", nm.ints(round(per / H)), RL, f"n_envs x rollout_len / H = {per}/{H}, rounded")
    need(nm, RL, 'raise RuntimeError(f"iteration {k}: {n_steps} month-steps taken, {E * L} expected")')
    need(nm, RL, "assert self.months == cfg.budget, (self.months, cfg.budget)")
    need(nm, RL, "nv = v_last if t == L - 1 else V[t + 1]")                         # bootstrap at the cut
    need(nm, RL, "mu, sd = ad_all.mean(), ad_all.std()             # advantages normalised over the whole minibatch")
    need(nm, RL, "rew = m - self.margin")                                             # potential-based reward
    need(nm, RL, "self.slot_inst[slots] = (slots + self.episode[slots] * self.E) % self.n_inst")

    # -- policy network ----------------------------------------------------------------------------------------------
    pol = ref["policy"]
    for key, name, text in (("tile_emb", "PrTileEmb", "tile_emb: int = 8"), ("c1", "PrConvA", "c1: int = 32"),
                            ("c2", "PrConvB", "c2: int = 48"), ("hidden", "PrHidden", "hidden: int = 256")):
        v = qlit(nm, name, text, RL, nm.ints)
        expect(nm, pol[key] == v, f"the runs' policy {key} is {v}")
    expect(nm, pol["spatial_out"] == pol["vec_hidden"] == pol["hidden"], "the encoder, vector and trunk layers are equally wide")
    v = qlit(nm, "PrReadCell", "READ_CELL = 4", RL, nm.ints)
    need(nm, RL, "nn.init.zeros_(self.pos_out.weight)")
    pp = {c["meta"]["policy_parameters"] for c in cfgs} | {nm.J(p)["meta"]["policy_parameters"] for _, p in engine}
    expect(nm, len(pp) == 1, "every run's policy has the same parameter count")
    nm.add_multi("PrPolicyParams", nm.ints(pp.pop()), ladder[:1] + [p for _, p in engine],
                 "meta.policy_parameters (equal in every ladder and engine-trained run)")
    # environment features: task one-hot, month one-hot, start scalars, change since the start, five threshold columns
    need(nm, RL, "N_ENV_VEC = len(T.TASKS) + H + NUM_SCALARS + NUM_SCALARS + 5")
    n_tasks = len(ast.literal_eval(regex(nm, TASKS_PY, r"TASKS: Tuple\[str, \.\.\.\] = (\([^)]*\))", "TASKS").group(1)))
    n_sc = int(regex(nm, ENGINE, r"^NUM_SCALARS = (\d+)$", "NUM_SCALARS", re.M).group(1))
    nm.add("PrEnvFeatures", nm.ints(n_tasks + H + 2 * n_sc + 5), RL,
           f"N_ENV_VEC = len(TASKS) ({n_tasks}, tasks.py) + H ({H}) + 2 NUM_SCALARS ({n_sc}, engine.py) + 5")
    nm.src(TASKS_PY), nm.src(ENGINE)
    # action heads: every plan column but the forced disaster; sizes from the grammar
    need(nm, RL, "HEAD_COLS: List[int] = [0, 1, 2, 3] + [5 + 5 * j + k for j in range(G.M) for k in range(5)]")
    g = nm.T(GRAMMAR)
    M = int(regex(nm, GRAMMAR, r"^M = (\d+) ", "M", re.M).group(1))
    names = ast.literal_eval(regex(nm, GRAMMAR, r"MACRO_NAMES = (\[.*?\])", "MACRO_NAMES", re.S).group(1))
    tax_hi = int(regex(nm, GRAMMAR, r'\("tax", 0, (\d+)\)', "the tax column").group(1))
    lvl_hi = [int(regex(nm, GRAMMAR, rf'\("{c}", 0, (\d+)\)', f"the {c} column").group(1)) for c in ("road", "fire", "police")]
    line_max = int(regex(nm, GRAMMAR, r"^LINE_MAX = (\d+)$", "LINE_MAX", re.M).group(1))
    b_hi = int(regex(nm, GRAMMAR, r'\(f"m\{_i\}_b", 0, (\d+)\)', "the b column").group(1))
    need(nm, GRAMMAR, '(f"m{_i}_x", 0, WORLD_W - 1),')
    need(nm, GRAMMAR, '(f"m{_i}_y", 0, WORLD_H - 1),')
    ww, wh = (int(x) for x in regex(nm, ENGINE, r"^WORLD_W, WORLD_H = (\d+), (\d+)$", "the map size", re.M).groups())
    heads = 4 + 5 * M
    logits = (tax_hi + 1) + sum(h + 1 for h in lvl_hi) + M * (len(names) + ww + wh + (line_max + 1) + (b_hi + 1))
    need(nm, RL, f"{heads} heads, {logits:,} logits")            # the module docstring agrees with the grammar
    nm.add("PrHeads", nm.ints(heads), GRAMMAR, "4 budget columns + 5 columns x M macros (rl.HEAD_COLS)")
    nm.add("PrLogits", nm.ints(logits), GRAMMAR, "sum of the head sizes (rl.HEAD_SIZES) from PLAN_COLUMNS, MACRO_NAMES, "
           "WORLD_W/H (engine.py)")
    # initial head biases: the first init_plans logged plans of every start of the family
    need(nm, RUN_RL, "plans = np.concatenate([RA.behaviour_plans(i.start_id, cfg.init_plans).reshape(-1, rl.N_COLS)")
    need(nm, RL, 'out[HEAD_OFF[i]:HEAD_OFF[i + 1]] = np.log(mix * p + (1.0 - mix) / size)')
    for c in cfgs[:40] + [nm.J(p) for _, p in engine]:
        starts = {k.split("|")[0] for k in c["meta"]["instances"]}
        expect(nm, c["meta"]["init_rows"] == len(starts) * q["init_plans"] * H, "the biases read init_plans plans per start")
    need(nm, RL, 'torch.manual_seed(seed_for("rl-init", init_key or run_key))')
    need(nm, RUN_RL, 'init_key=f"{args.task}|s{args.seed}"')
    # reward units (dc.tasks.margin)
    need(nm, TASKS_PY, "terms = [(statistic(task, s) - theta) / max(float(stat_sd), 1e-9)]")
    need(nm, TASKS_PY, "terms.append((s[..., 0, SC_TAX] - s[..., 1:, SC_TAX].max(axis=-1, initial=-np.inf)) / 20.0)")
    expect(nm, tax_hi == 20, "the tax slack is a share of the rate's range (the divisor 20 is the tax column's maximum)")
    pu = float(regex(nm, TASKS_PY, r"terms\.append\(\(frac - POWER_FRACTION\) / ([0-9.]+)\)", "the power slack unit").group(1))
    nm.add("PrPowerUnit", num(round(pu * 100, 6)), TASKS_PY, "margin: (frac - POWER_FRACTION) / 0.05, in percentage points")
    need(nm, TASKS_PY, "return np.minimum.reduce(terms)")
    need(nm, CALIBRATE, "sd = float(np.std(st[ok])) if ok.sum() > 1 else float(np.std(st))")
    # the tax mask
    need(nm, RL, "out[:, :n] = out[:, :n].masked_fill(over, -1e9)")
    # open-loop and closed-loop PPO evaluation protocol
    need(nm, RL, '"dream_accepts": [bool(x >= 0) for x in dm]')
    need(nm, RL, 'out["inflation_open"] = float((dm - om).mean())')
    need(nm, RL, 'r.update({"engine_open_margins": [float(x) for x in om.mean(axis=1)],')
    need(nm, RL, 'seeds = [fresh(("rl-eval-closed-seed", run_key, months, inst[e % n].key, e // n), inst[e % n].start_id)')
    need(nm, RL, "P = D[\"plans\"] if emu is not None else C[\"plans\"]")    # engine learner: open = closed-loop logs
    need(nm, RL, "eq[sl] = [np.array_equal(rep[j], traj[e]) for j, e in enumerate(sl)]")


def table_ppo(nm):
    """paper/tables/proto_ppo.tex: the learner's settings, two pairs of columns; every value cell a Pr macro and every
    qualifier generated from the runs' configuration."""
    ladder, _ = _rl_configs(nm)
    cfg = nm.J(ladder[0])["cfg"]
    lin = lambda k: ", linear to zero" if cfg[k] == "linear" else ""
    rows = [("Environments per run", r"\PrEnvs"),
            ("Months per environment and update", r"\PrRollout"),
            ("Months per update", r"\PrMonthsPerUpdate"),
            (r"Updates in \PrBudget{} months", r"\PrUpdates"),
            ("Adam learning rate", r"\PrLr{}" + lin("lr_schedule")),
            (r"Adam $\epsilon$", r"\PrAdamEps"),
            ("Epochs per update", r"\PrEpochs"),
            ("Minibatch (months)", r"\PrMinibatch"),
            ("Clipping range", r"\PrClip"),
            (r"Discount $\gamma$", r"\PrGamma"),
            (r"GAE $\lambda$", r"\PrGae"),
            ("Entropy coefficient", r"\PrEnt{}" + lin("ent_schedule")),
            ("Value-loss coefficient", r"\PrVf"),
            ("Gradient-norm clip", r"\PrGradNorm"),
            ("KL target", r"\PrTargetKl"),
            ("KL early stop (multiple of the target)", r"\PrKlStop"),
            ("Logged-marginal weight in the first logits", r"\PrInitMix"),
            ("Policy parameters", r"\PrPolicyParams")]
    half = (len(rows) + 1) // 2
    left, right = rows[:half], rows[half:] + [("", "")] * (2 * half - len(rows))
    body = [f"{a} & {b} & {c} & {d} \\\\" for (a, b), (c, d) in zip(left, right)]
    (nm.PAPER / "tables" / "proto_ppo.tex").write_text(
        "% Generated by paper/scripts/protocols.py (protocols(nm), called from make_numbers.py): every value is a macro\n"
        "% quoted from code/dc/rl.py and checked against every RL run's config.json\n"
        r"\begin{tabular}{@{}lrlr@{}}" "\n" r"\toprule" "\n"
        r"Setting & Value & Setting & Value \\" "\n" r"\midrule" "\n" + "\n".join(body) + "\n"
        r"\bottomrule" "\n" r"\end{tabular}" "\n")


# ---------------------------------------------------------------------------------------------
# (b) searches and defences
# ---------------------------------------------------------------------------------------------
def searches(nm):
    # logged plans: the calibration plans of every held-out start (calibrate_tasks.py), original and further cities
    n = {}
    for f in (TASKS_V2, TASKS_V2X):
        m = nm.J(f)["meta"]
        n[f] = int(m["n_fit"]) + int(m["n_val"])
    expect(nm, len(set(n.values())) == 1, "the original and the further cities have the same number of logged plans per start")
    nm.add("PrLoggedPerStart", nm.ints(n[TASKS_V2]), TASKS_V2, "meta.n_fit + meta.n_val (equal in tasks_v2x_H24.json)")
    nm.src(TASKS_V2X)
    need(nm, CALIBRATE, "H, n = a.horizon, a.n_fit + a.n_val")
    need(nm, CALIBRATE, "policy, label = sample_behaviour(rng)")
    need(nm, CALIBRATE, 'plan, _ = rollout_behaviour(eng, cty, policy, H, seed_for("cal-gen", start_id, H, j), False, rng)')
    need(nm, CALIBRATE, "plan[:, 4] = 0                                         # task plans carry no forced disasters of their own")
    regex(nm, AUDIT, r'CAL_DIR = Path\("[^"]+/calibration"\)', "CAL_DIR")
    need(nm, AUDIT, "p[..., FORCED_COL] = 0")
    qlit(nm, "PrPerturb", "P_PERTURB = 0.30", BEHAVIOUR, num)
    # random search and best-of-N (hpr_dream.random_shooting / best_of_n over the first B rows, argmax, first on ties)
    need(nm, ATTACK, "s = counter(P[:B])\n    j = int(np.argmax(s))")
    need(nm, AUDIT, "sel = hd.random_shooting(_Lookup(flat_beh, prop_score[s]), flat_beh[:n_prop], B)")
    need(nm, AUDIT, "prop_score[s] = self._smargin(inst, tr).mean(axis=1)[:n_prop]")
    need(nm, BUILDERS, "style = STYLES[int(rng.integers(len(STYLES)))]")
    need(nm, BUILDERS, 'plan, _ = rollout_behaviour(eng, cty, make_policy(label), H, seed_for("bon-gen", start_id, H, j), False, rng,')
    # the adaptive search (hpr_dream.cem_seeded as dc.audit calls it)
    block = regex(nm, ATTACK, r"def cem_seeded\((.*?)\) -> Selected:", "the cem_seeded signature", re.S).group(1)
    d = {}
    for key in ("elite_frac", "min_elite", "p_replace", "smoothing", "prob_floor", "std_floor", "std_floor_frac"):
        m = re.search(rf"\b{key}: \w+ = ([0-9.]+)", block)
        if not m:
            raise nm.Missing(f"protocols: cem_seeded default {key} not found")
        d[key] = ast.literal_eval(m.group(1))
    for key, name in (("min_elite", "PrMinElite"), ("smoothing", "PrSmooth"), ("prob_floor", "PrProbFloor"),
                      ("std_floor", "PrSdFloor"), ("std_floor_frac", "PrSdFloorFrac")):
        nm.add(name, num(d[key]), ATTACK, f"cem_seeded({key}=...) default")
    fm = regex(nm, ATTACK, r"def fit_marginals\(space: Space, behaviour_plans, \*, prob_floor: float = ([0-9.]+), "
                           r"std_floor: float = ([0-9.]+),\s+std_floor_frac: float = ([0-9.]+)\)", "fit_marginals").groups()
    expect(nm, tuple(float(x) for x in fm) == (d["prob_floor"], d["std_floor"], d["std_floor_frac"]),
           "the initial marginals carry the same floors as the updates")
    need(nm, AUDIT, 'init = hd.fit_marginals(self.space, flat_beh) if ("cem" in plan or "cem_seeded" in plan) else None')
    need(nm, AUDIT, "flat_beh[:n_prop], init, block=N_COLS, repair=self._repair)")
    need(nm, AUDIT, "return sp.freeze([FORCED_COL + N_COLS * m for m in range(H)], 0)")
    need(nm, ATTACK, "n_elite = max(int(min_elite), math.ceil(elite_frac * N))")
    need(nm, ATTACK, "elite = P[np.argsort(-s_all, kind=\"stable\")[:min(n_elite, P.shape[0])]]")
    need(nm, ATTACK, "mask = rng.random((N, n_blocks)) < float(p_replace)")
    need(nm, ATTACK, "f_col = np.minimum(float(prob_floor), 0.5 / L.cat_n)")
    need(nm, ATTACK, "sf = np.maximum(float(std_floor), float(std_floor_frac) * (L.int_high - L.int_low))")
    n_kinds = len(ast.literal_eval(regex(nm, GRAMMAR, r"MACRO_NAMES = (\[.*?\])", "MACRO_NAMES", re.S).group(1)))
    expect(nm, min(d["prob_floor"], 0.5 / n_kinds) == d["prob_floor"],
           "the probability floor is prob_floor itself (the only categorical column is the macro kind)")
    sched = regex(nm, ATTACK, r"1000: \((\d+), (\d+)\),", "CEM_SCHEDULE[1000]")
    N = int(sched.group(2))
    nm.add("PrEliteThou", nm.ints(max(d["min_elite"], math.ceil(d["elite_frac"] * N))), ATTACK,
           f"max(min_elite, ceil(elite_frac x {N})), the population at B = 1,000 (CEM_SCHEDULE)")


def defences(nm):
    de = nm.J(FRONTIER)["design"]
    nm.add("PrDetPlans", nm.ints(de["detector_plans"]), FRONTIER, "design.detector_plans")
    need(nm, DEFENCES, "DETECTOR_PLANS = 125")
    expect(nm, de["detector_plans"] == 125, "the detector and the shrinkage read DETECTOR_PLANS logged plans")
    feats = list(de["detector_features"])
    expect(nm, feats == ["mean_margin", "pass_share", "disagreement", "monthly_spread", "macro_share"],
           "the detector's features are mean margin, pass share, disagreement, monthly spread and macro share")
    nm.add("PrDetFeatures", word(nm, len(feats), "detector features"), FRONTIER, "len(design.detector_features)")
    M = len(de["members"])
    nm.add("PrEnsSearchK", nm.ints(M * de["k_search_per_member"]), FRONTIER, "len(design.members) x k_search_per_member")
    nm.add("PrEnsVerdictK", nm.ints(M * de["k_verdict_per_member"]), FRONTIER, "len(design.members) x k_verdict_per_member")
    expect(nm, de["disagreement_ddof"] == 1, "the disagreement is a sample standard deviation (ddof 1)")
    expect(nm, int(de["budget"]) <= nm.J(TASKS_V2)["meta"]["n_fit"] + nm.J(TASKS_V2)["meta"]["n_val"],
           "the halt thresholds read the instance's first DefBudget logged plans")
    # the rules, verbatim
    need(nm, DEFENCES, 'return mean - st.param * np.asarray(S["disagreement"])')
    need(nm, DEFENCES, 'return base & (am >= 0), {"acceptance_margin": am}')
    need(nm, DEFENCES, 'Setting("penalty0", "ensemble", "penalty", 0.0, derived_from="ensemble", neutral=True),')
    need(nm, DEFENCES, 'halt = {q: float(np.percentile(prop["ensemble"]["disagreement"], q)) for q in HALT_PERCENTILES}')
    need(nm, DEFENCES, 'return np.where(np.asarray(S["disagreement"]) > ctx["halt"][st.param], -np.inf, mean)')
    need(nm, DEFENCES, 'return base & ~(np.asarray(S["disagreement"]) > thr), {"halt_threshold": np.full(p.shape, thr)}')
    need(nm, DEFENCES, 'label = (dv["pass_share"] >= ACCEPT_P) & ~oj["accept"]')
    need(nm, DEFENCES, 'return {f: k % 2 for k, f in enumerate(sorted(set(families)))}')
    need(nm, DEFENCES, 'spread = sm.std(axis=1, ddof=DDOF).mean(axis=-1) / max(float(inst.stat_sd), 1e-9)')
    need(nm, DEFENCES, 'return (k != 0).any(axis=-1).mean(axis=-1).astype(np.float64)')
    need(nm, DEFENCES, '"det_search_X": feature_matrix(prop["ensemble"])[:nd], "det_verdict_X": feature_matrix(dv),')
    need(nm, DEFENCES, "alpha = var_mu / (var_mu + var_v) if var_mu > 0 else 0.0")
    need(nm, DEFENCES, "var_v = float(np.mean((v - q) ** 2))")
    need(nm, DEFENCES, "return float(alpha) * np.asarray(p, dtype=np.float64) + (1.0 - float(alpha)) * float(mu_bar)")
    need(nm, DEFENCES, 'return s >= ACCEPT_P, {"shrunk_share": s,')
    # the count of defended settings the main text reports includes the neutral lambda = 0 point
    rows = nm.J(FRONTIER)["frontier"]["random"]["rows"]
    tested = [r["setting"] for r in rows if "hackability_minus_ensemble" in r and r.get("complete") and r["setting"] != "member0"]
    expect(nm, "penalty0" in tested, "the lambda = 0 point is among the defended settings counted in \\DefTestedN")


# ---------------------------------------------------------------------------------------------
# (c) other protocols
# ---------------------------------------------------------------------------------------------
def other(nm):
    # structural changed-tile F1
    need(nm, FIDELITY, "tp = (pch & tch & (pred == true)).sum(dim=(1, 2))")
    need(nm, FIDELITY, "for c in range(1024):\n        union(c, int(nxt[c]))")
    need(nm, FIDELITY, 'for t in range(k["LTRFBASE"], k["HTRFBASE"] + 64):\n        union(t, k["ROADBASE"] + ((t - k["ROADBASE"]) & 15))')
    c = nm.J(CANON)
    expect(nm, c["canonical"]["animate_cpp_sha256"] == sha256(nm.REPO / ANIMATE), "the class table is the engine source's")
    nm.src(ANIMATE)
    for key, name in (("classes", "PrTileClasses"), ("codes_merged_into_another", "PrTilesMerged"),
                      ("multi_member_classes", "PrMultiClasses")):
        nm.add(name, nm.ints(c["canonical"][key]), CANON, f"canonical.{key}")
    ch = c["heldout_eval_changes"]
    nm.add("PrNonStructShare", nm.f3(ch["share_becoming_unchanged"]), CANON, "heldout_eval_changes.share_becoming_unchanged")
    nm.add("PrHeldTransitions", nm.ints(ch["transitions"]), CANON, "heldout_eval_changes.transitions")
    # the held-out store and the test selection
    text = '"heldout_eval": {"source": "heldout", "per_family": [[48, 25], [120, 5]], "disaster_rate": 0.0},'
    need(nm, GEN_DATA, text)
    (hs, ns), (hl, nl) = ast.literal_eval(re.search(r'"per_family": (\[\[.*?\]\])', text).group(1))
    for name, v in (("PrHeldShortH", hs), ("PrHeldShortN", ns), ("PrHeldLongH", hl), ("PrHeldLongN", nl)):
        nm.add(name, nm.ints(v), GEN_DATA, f'SPECS["heldout_eval"]["per_family"] = {[[hs, ns], [hl, nl]]}')
    need(nm, GEN_DATA, '"heldout_eval": {"source": "heldout"')
    n_cities = len({i["family_id"] for i in nm.J(TASKS_V2)["instances"]})
    expect(nm, ch["transitions"] == n_cities * (ns * hs + nl * hl), "the held-out store's transitions are the spec's")
    mt = nm.test_json("os_50m_full")
    sel = nm.J(mt)["selection"]
    expect(nm, sel["n_trajectories"] == n_cities * (ns + nl), "the held-out store holds the spec's trajectories")
    nm.add("PrHeldTraj", nm.ints(sel["n_trajectories"]), mt, "selection.n_trajectories")
    line = "DEV_SEED, TEST_SEED, TRAIN_EVAL_SEED = 20261109, 20261123, 20261147"
    need(nm, FIDELITY, line)
    dev_seed, test_seed, _ = ast.literal_eval("(" + line.split("=", 1)[1] + ")")
    nm.quote("PrDevSeed", line, FIDELITY, str(dev_seed))
    nm.add("PrTestSeed", str(test_seed), FIDELITY, f'text "{line}"')
    expect(nm, sel["name"] == "test" and sel["seed"] == test_seed, "the paper's selection is the test selection")
    for key, name in (("development_plans_excluded", "PrDevPlans"), ("development_transitions_excluded", "PrDevTransitions"),
                      ("development_transitions_inside_test_plan_windows", "PrDevInWindows")):
        nm.add(name, nm.ints(sel[key]), mt, f"selection.{key}")
    expect(nm, sel["plans_shared_with_development"] == 0 and sel["transitions_shared_with_development"] == 0,
           "the test selection shares no plan and no transition with the development selection")
    expect(nm, sel["eligible_plans"] == sel["n_plans"] == sel["n_trajectories"] - sel["development_plans_excluded"],
           "the test plans are every trajectory that is not a development plan")
    need(nm, FIDELITY, "pool = [(i, t) for i in rest for t in range(trajs[i].H) if (i, t) not in dev_pairs]")
    need(nm, FIDELITY, "s = _stack_states([trajs[i].state([0], device) for i in ids])")
    # the nearest-neighbour emulator
    need(nm, FIDELITY, "Context = (current code, attempted tool at the tile or none, powered flag).")
    need(nm, FIDELITY, "p = torch.where(seen, self.p_change[ctx], self.p_change_c[cur])")
    need(nm, EVAL_FID, 'ap.add_argument("--train-index", default="train_full", help="training split for the nearest-neighbour fit")')
    expect(nm, "--train-index" not in nm.T(LADDER_PY), "the ladder's evaluations fit the nearest neighbour on train_full")
    b = nm.J(BASELINES)
    nm.add("PrNNFit", nm.ints(b["nn_fit_transitions"]), BASELINES, "nn_fit_transitions")
    expect(nm, "nn_sample" in b, "the reported nearest neighbour is the sampled one")
    # oracle patching: the nine subsystems' masks, verbatim
    for t in ('"power": Mask("power", (Part("flags", (4,)), Part("power"), Part("scalars", _sc(SC_POWERED, SC_UNPOWERED)))),',
              '"treasury": Mask("treasury", (Part("scalars", _sc(SC_FUNDS, SC_TAX_FUND, SC_ROAD_SPEND, SC_FIRE_SPEND,',
              '"valves": Mask("valves", (Part("scalars", _sc(SC_RES_VALVE, SC_COM_VALVE, SC_IND_VALVE)),)),',
              '"zone_growth": Mask("zone_growth", (Part("tile_index", cells="zone"),)),',
              '"pollution": Mask("pollution", (Part("half", (2,)),)),',
              '"traffic": Mask("traffic", (Part("half", (1,)), Part("tile_index", cells="road"))),',
              '"land_value": Mask("land_value", (Part("half", (3,)),)),',
              '"crime": Mask("crime", (Part("half", (4,)),)),',
              '"fire": Mask("fire", (Part("eighth", (1,)), Part("tile_index", cells="fire"))),'):
        need(nm, PATCHING, t)
    need(nm, FIDELITY, 'HALF_NAMES = ["pop_density", "traffic", "pollution", "land_value", "crime"]')
    need(nm, FIDELITY, 'EIGHTH_NAMES = ["rate_of_growth", "fire_coverage", "police_coverage"]')
    glob_ = ast.literal_eval(regex(nm, PATCHING, r"^GLOBAL = (\([^)]*\))", "GLOBAL", re.M).group(1))
    loc = ast.literal_eval(regex(nm, PATCHING, r"^LOCAL = (\([^)]*\))", "LOCAL", re.M).group(1))
    nm.add("PrNSubsystems", word(nm, len(glob_) + len(loc), "subsystems"), PATCHING, "len(GLOBAL) + len(LOCAL)")
    nm.add("PrNGlobal", word(nm, len(glob_), "global subsystems"), PATCHING, "len(GLOBAL)")
    nm.add("PrNLocal", word(nm, len(loc), "local subsystems"), PATCHING, "len(LOCAL)")
    # seeds
    need(nm, SEEDS, 'h = hashlib.sha256("\\x1f".join(str(k) for k in keys).encode()).digest()')
    m = regex(nm, SEEDS, r"return int\.from_bytes\(h\[:4\], \"big\"\) & (0x[0-9A-Fa-f]+)", "the seed mask")
    bits = int(m.group(1), 16).bit_length()
    nm.quote("PrSeedBits", f"A {bits}-bit seed from a tuple of keys", SEEDS, str(bits))
    ns_ = int(regex(nm, AUDIT, r"^N_SECONDARY = (\d+)$", "N_SECONDARY", re.M).group(1))
    nm.add("PrResidualSeeds", word(nm, 1 + ns_, "residual seeds"), AUDIT, "primary seed + N_SECONDARY")
    need(nm, AUDIT, 'return seed_for("task", inst.start_id, inst.task, inst.horizon)')
    need(nm, TASKS_PY, 'return [seed_for(ORACLE_SEED_NAME, start_id, task, int(horizon), k) for k in range(n)]')
    need(nm, AUDIT, 'raise ValueError(f"{inst.key}: oracle seeds {sorted(both)} are also residual seeds")')
    need(nm, AUDIT, 's = seed_for(*keys, "redraw", r)')
    need(nm, AUDIT, '``seed_for("audit-seedcheck", start, *S, i, k)``')
    need(nm, AUDIT, 'torch.manual_seed(seed_for("audit-emu", inst.start_id, *stream))')
    need(nm, AUDIT, 'np.random.default_rng(seed_for("audit-cem-seeded", inst.key, B, s))')
    need(nm, RL, 's, _ = RA.fresh_seed(("rl-engine-train", self.run_key, int(e), int(self.episode[e])), self._reserved[sid])')
    need(nm, GEN_DATA, "Seeds of every split other than train_full are re-derived\n(with an attempt counter) until they are outside train_full's seed set")


# ---------------------------------------------------------------------------------------------
# (d) the instrument (Appendix C)
# ---------------------------------------------------------------------------------------------
def instrument(nm):
    need(nm, HPD_PROJECT, 'dependencies = ["numpy>=1.24", "scipy>=1.10"]')
    need(nm, HPD_PROJECT, 'name = "hpr-dream"')
    for f in ("random_shooting", "best_of_n", "cem,", "cem_seeded", "build_card", "write_card", "hackability",
              "false_rejection", "conditional_reject", "excess", "brier_decomposition", "log_score", "auc",
              "clustered_spearman", "clustered_kendall", "ResidualSurrogate", "FlipSurrogate", "OracleCache"):
        need(nm, HPD_INIT, f)
    need(nm, ATTACK, 'raise BudgetError(f"{name}: scored {self.n_plans} plans, budget {B}")')
    need(nm, ATTACK, 'ScoreFn = Callable[[np.ndarray], np.ndarray]')
    need(nm, HPD_CARD, 'REQUIRED = ("instance", "cluster", "attacker", "budget", "attacker_seed", "plan_id", "grader_p", "oracle_accept")')
    need(nm, HPD_INIT, "zero_count_upper_bound")
    for f in ('"hackability_curve": curve,', '"noise_floors": floors,', '"calibration": {"selected": selected_cal},',
              '"conditional_reject": cond,', '"excess": _est(S.excess(',
              '"false_rejection"', '"flip_rates"', '"dream_overfit_probability"', '"detector_auc"', '"counts"'):
        need(nm, HPD_CARD, f)
    # the TD-MPC2 adaptor: start capture and restore, behaviour plans, the model's margins, the simulator oracle
    for f in ("def capture_start(task, seed, prefix_steps=12):", "def restore(env, state):", "def behaviour_plans(rng, n, action_dim, horizon=HORIZON):",
              "class Oracle:", "class Grader:", "def margins(self, state, plans, theta, sd, k=1):", "def plan_space(action_dim, horizon=HORIZON):"):
        need(nm, TDMPC2, f)
    # the city adaptor: the perfect emulator is a sampling judge that replays the engine on fresh seeds
    need(nm, AUDIT, "class EngineSeedJudge(SamplingJudge):")


def protocols(nm):
    rl_learner(nm)
    table_ppo(nm)
    searches(nm)
    defences(nm)
    other(nm)
    instrument(nm)
