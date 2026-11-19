"""Generate the trajectory stores (REBUILD_SPEC.md section 4.2), the train_small index, the summary,
and verify the stores against the oracle.

    python code/scripts/gen_data.py all --workers 28            # everything, resumable
    python code/scripts/gen_data.py gen --splits train_full --workers 28
    python code/scripts/gen_data.py small
    python code/scripts/gen_data.py verify --split train_full --n 500
    python code/scripts/gen_data.py summary
    python code/scripts/gen_data.py backfill --workers 8   # add ledger / terrain / com_rate to dc-store-1 stores
    # the coverage store , its verification and summary
    python code/scripts/gen_data.py gen --splits train_cov --workers 16 --summary-out results/coverage/summary_train_cov.json
    python code/scripts/gen_data.py verify --split train_cov --summary-out results/coverage/summary_train_cov.json
    # the second coverage store: first the per-start settings table, then the store
    python code/scripts/gen_data.py cov2-settings --workers 16
    python code/scripts/gen_data.py gen --splits train_cov2 --workers 16 --summary-out results/coverage/summary_train_cov2.json

Every trajectory j of a split is a function of (split name, master seed, j) only: its months H, its
start (uniform over families, then over the family's start variants), its behaviour (drawn from
``dc.behaviour.BEHAVIOUR_MIX`` via ``sample_behaviour``, or, for a spec with ``"behaviour": "coverage"``,
via ``sample_coverage_behaviour``), its disasters flag, its engine seed and the
policy's random stream. The store is therefore the same whatever the number of workers, and a killed
run resumes where it stopped (rerun the same command).

Engine seeds come from ``dc.seeds.seed_for``. Seeds of every split other than train_full are re-derived
(with an attempt counter) until they are outside train_full's seed set, so they are disjoint from it
by construction.

``--provider FILE.py:ATTR`` replaces the behaviour/families/grammar modules by an object with the same
four functions (``starts``, ``sample_behaviour``, ``rollout_behaviour``, ``compile_plan``); the tests use
it to run this script on a stand-in.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import shlex
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc import data as D  # noqa: E402
from dc.seeds import seed_for  # noqa: E402

MASTER_SEED = 20261109
SPECS: Dict[str, Dict[str, Any]] = {
    "train_full": {"source": "train", "H": [[48, 40000], [120, 9000]], "disaster_rate": 0.15},
    "train_eval": {"source": "train", "H": [[48, 2000]], "disaster_rate": 0.15},
    "heldout_eval": {"source": "heldout", "per_family": [[48, 25], [120, 5]], "disaster_rate": 0.0},
    # the coverage store : the seven scripted builders, each trajectory under one budget setting drawn
    # uniformly from the whole grid and held (dc.behaviour.sample_coverage_behaviour), training starts only,
    # disasters off. Not in SPLIT_ORDER: generated only when named (gen --splits train_cov).
    "train_cov": {"source": "train", "H": [[24, 25000]], "disaster_rate": 0.0, "behaviour": "coverage"},
    # the second coverage store : the seven scripted builders under competent budgets, each
    # trajectory under one setting drawn uniformly from its start's list in ``settings_file`` (``cov2-settings``
    # stage: the best constant settings of the start, by family), every ``quake_every``-th trajectory (j % 5 == 4)
    # with the earthquake forced in month 0 and its setting drawn from the start's ``recover`` list; disasters off;
    # engine seeds also disjoint from the stores in ``avoid_seeds_of``. Not in SPLIT_ORDER.
    "train_cov2": {"source": "train", "H": [[24, 25000]], "disaster_rate": 0.0, "behaviour": "listed",
                   "settings_file": "results/coverage/cov2_settings.json", "quake_every": 5,
                   "avoid_seeds_of": ["train_eval", "heldout_eval", "train_cov"]},
}
SPLIT_ORDER = ("train_full", "heldout_eval", "train_eval")
BEHAVIOURS = ("mix", "coverage", "listed")   # spec["behaviour"]: absent = "mix" (sample_behaviour)
# the cov2-settings stage: every constant plan (dc.frontier.GRID, no macro) of every training start replayed for H
# months on one seed per start, plain and with the recover task's forced earthquake; per family the TOP best settings
# by dc.frontier.J of the family's variant (statistic where its clauses hold), ties by slack then grid order
COV2_CONST = {"H": 24, "seed": "seed_for('b20-cov2-const', start_id, H)", "top": 3, "disasters": False,
              "families": [["grow", "grow", "plain"], ["solvent", "solvent", "plain"],
                           ["treasury", "treasury_rev", "plain"], ["recover", "recover", "quake"]]}
SMALL = {"store": "train_full", "frac": 0.10, "by": ["H", "family", "label"]}
RESULTS = ROOT / "results" / "data"


def _sha(path: Path) -> Optional[str]:
    return D.sha256_file(path) if path.exists() else None


class RealProvider:
    """the modules."""

    name = "dc"

    def starts(self, split):
        from dc.families import starts
        return starts(split)

    def sample_behaviour(self, rng):
        from dc.behaviour import sample_behaviour
        return sample_behaviour(rng)

    def sample_coverage_behaviour(self, rng):
        from dc.behaviour import sample_coverage_behaviour
        return sample_coverage_behaviour(rng)

    def sample_listed_behaviour(self, rng, settings, forced):
        from dc.behaviour import sample_listed_behaviour
        return sample_listed_behaviour(rng, settings, forced)

    def recover_forced(self):
        from dc.tasks import forced_for
        return forced_for("recover")

    def rollout_behaviour(self, eng, cty_path, policy, months, seed, disasters, rng):
        from dc.behaviour import rollout_behaviour
        return rollout_behaviour(eng, cty_path, policy, months, seed, disasters, rng)

    def compile_plan(self, arr):
        from dc.grammar import compile_plan
        return compile_plan(arr)

    def content_files(self) -> List[Path]:
        return [ROOT / "code/dc/grammar.py", ROOT / "code/dc/behaviour.py", ROOT / "code/dc/families.py",
                ROOT / "data/families.json"]


def load_provider(spec: str):
    if spec in ("dc", "", None):
        return RealProvider()
    file, attr = spec.rsplit(":", 1)
    mspec = importlib.util.spec_from_file_location("_gen_provider", file)
    mod = importlib.util.module_from_spec(mspec)
    sys.modules["_gen_provider"] = mod
    mspec.loader.exec_module(mod)
    return getattr(mod, attr)


def train_full_seeds(master: int) -> set:
    n = sum(c for _, c in SPECS["train_full"]["H"])
    return {seed_for("train_full", master, j, "engine") for j in range(n)}


class SplitJob:
    """One split: the per-trajectory draw, as a function of (name, master seed, j)."""

    def __init__(self, name: str, provider, master: int = MASTER_SEED, spec: Optional[Dict[str, Any]] = None):
        self.name, self.provider, self.master = name, provider, int(master)
        self.spec = json.loads(json.dumps(spec if spec is not None else SPECS[name]))
        self.behaviour = self.spec.get("behaviour", "mix")
        if self.behaviour not in BEHAVIOURS:
            raise ValueError(f"{name}: behaviour {self.behaviour!r} not in {BEHAVIOURS}")
        src = self.spec["source"]
        raw = list(provider.starts(src))
        if not raw:
            raise RuntimeError(f"no {src} start states")
        self.starts = [{"start_id": str(s), "family_id": str(f), "split": src, "path": str(p)} for s, f, p in raw]
        fams: List[str] = []
        by_fam: Dict[str, List[int]] = {}
        for i, s in enumerate(self.starts):
            if s["family_id"] not in by_fam:
                fams.append(s["family_id"])
                by_fam[s["family_id"]] = []
            by_fam[s["family_id"]].append(i)
        self.families, self.fam_starts = fams, [by_fam[f] for f in fams]
        self.paths = [str(D.resolve_path(D._rel_or_abs(s["path"]))) for s in self.starts]
        if "per_family" in self.spec:
            pat = np.concatenate([np.full(c, h, dtype=np.int64) for h, c in self.spec["per_family"]])
            self.per_family = len(pat)
            self.Hs = np.tile(pat, len(fams))
        else:
            self.per_family = 0
            Hs = np.concatenate([np.full(c, h, dtype=np.int64) for h, c in self.spec["H"]])
            perm = np.random.default_rng(seed_for(name, self.master, "H")).permutation(len(Hs))
            self.Hs = Hs[perm]          # trajectory j gets months Hs[j]: interleaved, fixed by the seed
        self.n = len(self.Hs)
        if name == "train_full":
            self.seeds = np.array([seed_for(name, self.master, j, "engine") for j in range(self.n)], dtype=np.int64)
        else:
            avoid = train_full_seeds(self.master)
            for other in self.spec.get("avoid_seeds_of", []):
                avoid |= set(SplitJob(other, provider, self.master).seeds.tolist())
            seeds = []
            for j in range(self.n):
                a = 0
                s = seed_for(name, self.master, j, "engine", a)
                while s in avoid:
                    a += 1
                    s = seed_for(name, self.master, j, "engine", a)
                seeds.append(s)
            self.seeds = np.array(seeds, dtype=np.int64)
        self.settings = None
        if self.behaviour == "listed":
            sf = D.resolve_path(self.spec["settings_file"])
            tab = json.loads(sf.read_text())["starts"]
            self.settings_sha256 = D.sha256_file(sf)
            self.settings = [(tab[s["start_id"]]["settings"], tab[s["start_id"]]["recover"]) for s in self.starts]
            self.forced = {int(m): int(k) for m, k in provider.recover_forced().items()}

    def config(self) -> Dict[str, Any]:
        files = getattr(self.provider, "content_files", lambda: [])()
        core = [ROOT / "code/dc/engine.py", ROOT / "code/dc/oracle.py", ROOT / "engine/libmicropolis.so"]
        extra = {"settings_sha256": self.settings_sha256, "forced_quake": {str(m): k for m, k in self.forced.items()}} \
            if self.behaviour == "listed" else {}
        return {
            **extra,
            "name": self.name,
            "spec": self.spec,
            "master_seed": self.master,
            "n_trajectories": int(self.n),
            "city_months": int(self.Hs.sum()),
            "families": len(self.families),
            "starts": len(self.starts),
            "provider": getattr(self.provider, "name", type(self.provider).__name__),
            "content_files": {str(D._rel_or_abs(f)): _sha(f) for f in core + list(files)},
            "seed_derivation": "dc.seeds.seed_for(name, master, j, 'engine'[, attempt]); draw: (name, master, j, 'draw'); "
                               "policy rng: (name, master, j, 'policy'); months: permutation by (name, master, 'H')",
            "provenance": {
                "gen_data.py": _sha(Path(__file__)), "data.py": _sha(ROOT / "code/dc/data.py"),
                "host": platform.node(), "python": sys.version.split()[0], "numpy": np.__version__,
            },
        }

    def run(self, j: int, eng) -> Dict[str, Any]:
        rng = np.random.default_rng(seed_for(self.name, self.master, j, "draw"))
        H = int(self.Hs[j])
        if self.per_family:
            fam = j // self.per_family
        else:
            fam = int(rng.integers(len(self.families)))
        vs = self.fam_starts[fam]
        start_idx = vs[int(rng.integers(len(vs)))]
        if self.behaviour == "coverage":
            policy, label = self.provider.sample_coverage_behaviour(rng)
        elif self.behaviour == "listed":
            quake = j % int(self.spec["quake_every"]) == int(self.spec["quake_every"]) - 1
            plain, recover = self.settings[start_idx]
            policy, label = self.provider.sample_listed_behaviour(rng, recover if quake else plain,
                                                                  self.forced if quake else None)
        else:
            policy, label = self.provider.sample_behaviour(rng)
        disasters = bool(rng.random() < float(self.spec["disaster_rate"]))
        seed = int(self.seeds[j])
        prng = np.random.default_rng(seed_for(self.name, self.master, j, "policy"))
        plan, rep = self.provider.rollout_behaviour(eng, self.paths[start_idx], policy, H, seed, disasters, prng)
        final_hash = int(rep.hashes[-1]) if getattr(rep, "hashes", None) is not None else eng.hash_full()
        return {"start_idx": start_idx, "label": label, "seed": seed, "disasters": disasters, "plan": plan,
                "replay": rep, "final_hash": final_hash}


def remaining_bytes(job: SplitJob, done: int) -> int:
    H = job.Hs[done:]
    return int(((H + 1) * D.OBS_ROW_BYTES + H * D.TRANS_ROW_BYTES).sum())


def committed(path: Path) -> int:
    rec = path / "traj.rec"
    return rec.stat().st_size // D.TRAJ_DTYPE.itemsize if rec.exists() else 0


def cmd_gen(args, provider, splits) -> Dict[str, Any]:
    out = {}
    for name in splits:
        job = SplitJob(name, provider, args.master_seed, spec=override_spec(name, args))
        path = Path(args.root) / name
        need = remaining_bytes(job, committed(path))
        free = shutil.disk_usage(Path(args.root) if Path(args.root).exists() else Path(args.root).parent).free
        print(f"[{name}] {job.n} trajectories, {int(job.Hs.sum())} city-months, {len(job.families)} families, "
              f"{len(job.starts)} starts; still to write {need / 1e9:.1f} GB, free {free / 1e9:.1f} GB", flush=True)
        if free < need + args.min_free_gb * 1e9:
            raise SystemExit(f"[{name}] refusing: free {free / 1e9:.1f} GB < needed {need / 1e9:.1f} GB + margin {args.min_free_gb} GB")
        command = " ".join(shlex.quote(a) for a in [sys.executable, *sys.argv])
        st = D.generate(path, job, workers=args.workers, command=command,
                        log=lambda s: print(s, flush=True), commit_seconds=args.commit_seconds)
        st.pop("manifest", None)
        out[name] = st
        print(f"[{name}] {json.dumps(st)}", flush=True)
    return out


def override_spec(name: str, args) -> Dict[str, Any]:
    spec = json.loads(json.dumps(SPECS[name]))
    parse = lambda v: [[int(h), int(c)] for h, c in (x.split(":") for x in v.split(","))]  # noqa: E731
    if name == "train_full" and getattr(args, "train_h", None):
        spec["H"] = parse(args.train_h)
    if name == "train_eval" and getattr(args, "train_eval_h", None):
        spec["H"] = parse(args.train_eval_h)
    if name == "heldout_eval" and getattr(args, "heldout_per_family", None):
        spec["per_family"] = parse(args.heldout_per_family)
    return spec


def cmd_small(args) -> Dict[str, Any]:
    st = D.TrajStore(Path(args.root) / SMALL["store"])
    if not st.complete:
        raise SystemExit("train_full is not complete; train_small is drawn from the finished store")
    seed = seed_for("train_small", args.master_seed)
    trajs = D.stratified_traj_subset(st, SMALL["frac"], seed, by=SMALL["by"])
    tids = st.transition_ids(trajs)
    meta = {"name": "train_small", "store": SMALL["store"], "frac": SMALL["frac"], "stratified_by": SMALL["by"],
            "seed": seed, "trajectories": int(trajs.size), "transitions": int(tids.size),
            "source_traj_rec_sha256": st.manifest["traj_rec"]["sha256"],
            "by_H": {str(int(h)): int((st.traj["H"][trajs] == h).sum()) for h in np.unique(st.traj["H"][trajs])}}
    D.save_index(Path(args.root) / "train_small.npz", tids, trajs, meta)
    print(f"[train_small] {json.dumps(meta)}", flush=True)
    return meta


def cmd_verify(args, provider, name: str, n: Optional[int]) -> Dict[str, Any]:
    st = D.TrajStore(Path(args.root) / name)
    res = D.verify(st, n=n, seed=seed_for("verify", name, args.master_seed), workers=args.workers,
                   compile_plan=provider.compile_plan)
    res["split"] = name
    res["requested"] = "all" if n is None else int(n)
    print(f"[verify {name}] {json.dumps(res)}", flush=True)
    out = Path(args.summary_out).parent / f"verify_{name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1) + "\n")
    return res


def cmd_backfill(args, provider, splits) -> Dict[str, Any]:
    """Backfill the extended observation into each store (verifying every trajectory), merge the ledger
    statistics into the summary, and write the LEDGER_READY marker when all three stores carry it."""
    command = " ".join(shlex.quote(a) for a in [sys.executable, *sys.argv])
    prov = {str(D._rel_or_abs(f)): _sha(f) for f in [ROOT / "code/dc/engine.py", ROOT / "code/dc/oracle.py",
                                                   ROOT / "engine/libmicropolis.so", ROOT / "code/dc/grammar.py",
                                                   ROOT / "code/dc/data.py"]}
    root = Path(args.root)
    out: Dict[str, Any] = {}
    for name in splits:
        free = shutil.disk_usage(root).free
        st = D.TrajStore(root / name)
        need = st.n_obs * D.LEDGER_ROW_BYTES
        print(f"[backfill {name}] needs {need / 1e9:.2f} GB, free {free / 1e9:.1f} GB", flush=True)
        if free < need + args.min_free_gb * 1e9:
            raise SystemExit(f"[backfill {name}] refusing: not enough free space")
        r = D.backfill_ledger(root / name, workers=args.workers, compile_plan=provider.compile_plan, command=command,
                              provenance=prov, log=lambda m: print(m, flush=True))
        out[name] = r
        if not (r.get("published") or r.get("already_backfilled")):
            _write_json(Path(args.summary_out).parent / "backfill_ledger.json", out)
            raise SystemExit(f"[backfill {name}] stopped: mismatches against the oracle; nothing published")
    _write_json(Path(args.summary_out).parent / "backfill_ledger.json", out)
    # ledger statistics into the summary (the rest of it is unchanged by the backfill)
    sp = Path(args.summary_out)
    summ = json.loads(sp.read_text()) if sp.exists() else {"root": str(root), "splits": {}}
    for name in splits:
        st = D.TrajStore(root / name)
        summ.setdefault("splits", {}).setdefault(name, {})["ledger_change"] = D.ledger_summary(st)
        summ.setdefault("disk_bytes", {})[name] = int(sum(f.stat().st_size for f in (root / name).iterdir() if f.is_file()))
    small = root / "train_small.npz"
    summ["disk_bytes_total"] = int(sum(summ["disk_bytes"].values()) + (small.stat().st_size if small.exists() else 0))
    summ["backfill_ledger"] = {n: {k: v for k, v in r.items() if k != "result"} for n, r in out.items()}
    _write_json(sp, summ)
    print(f"[backfill] ledger statistics merged into {sp}", flush=True)
    stores = [root / n for n in SPLIT_ORDER]
    if all(D.TrajStore(p).has_ledger and all(k in D.TrajStore(p).manifest["arrays"] for k in D.LEDGER_FILES) for p in stores):
        lines = [f"{D.sha256_file(p / 'manifest.json')}  {p / 'manifest.json'}" for p in stores]
        tmp = root / "LEDGER_READY.tmp"
        tmp.write_text("\n".join(lines) + "\n")
        os.replace(tmp, root / "LEDGER_READY")
        print("[backfill] LEDGER_READY:\n" + "\n".join(lines), flush=True)
    return out


# --------------------------------------------------------------------------------------------
# cov2-settings: competent constant budgets per training start 
# --------------------------------------------------------------------------------------------
class _ConstCtx:
    eng = None
    acts = None


def const_seed(start_id: str) -> int:
    return seed_for("b20-cov2-const", str(start_id), int(COV2_CONST["H"]))


def _const_init(provider_spec: str) -> None:
    D._die_with_parent()
    from dc.engine import Engine
    from dc.frontier import constant_plans
    prov = load_provider(provider_spec)
    _ConstCtx.eng = Engine()
    _ConstCtx.acts = [prov.compile_plan(p)[0] for p in constant_plans(int(COV2_CONST["H"]))]


def _const_job(args):
    """(start id, cty, quake, forced) -> every constant plan's scalar trajectory (2625, H+1, 20) on the start's seed."""
    from dc.oracle import replay
    start_id, path, quake, forced = args
    seed = const_seed(start_id)
    f = {int(m): int(k) for m, k in forced.items()} if quake else None
    scal = np.stack([replay(_ConstCtx.eng, path, a, seed, disasters=bool(COV2_CONST["disasters"]), forced=f).scalars
                     for a in _ConstCtx.acts])
    return start_id, bool(quake), scal


def const_family_arrays(scal_plain: np.ndarray, scal_quake: np.ndarray) -> Dict[str, Dict[str, np.ndarray]]:
    """Per family of COV2_CONST: J, slack, statistic and feasibility of every constant plan (dc.frontier)."""
    from dc import frontier as F
    out = {}
    for fam, variant, which in COV2_CONST["families"]:
        sc = scal_quake if which == "quake" else scal_plain
        out[fam] = {"J": F.J(variant, sc), "slack": F.slack(variant, sc), "statistic": F.statistic(variant, sc),
                    "feasible": F.feasible(variant, sc)}
    return out


def cov2_select(arrs: Dict[str, Dict[str, np.ndarray]], top: int) -> Dict[str, Any]:
    """Per family the ``top`` best GRID settings by J (ties: slack, then grid order, as dc.frontier ranks constants);
    ``settings``: their union in family then rank order (at most 4 x top); ``recover``: the recover family's."""
    from dc import frontier as F
    rec: Dict[str, Any] = {"by_family": {}, "settings": [], "recover": []}
    for fam, variant, which in COV2_CONST["families"]:
        a = arrs[fam]
        idx = F.top_k(a["J"], top, tie=a["slack"])
        rows = [[int(v) for v in F.GRID[i]] for i in idx]
        rec["by_family"][fam] = {"variant": variant, "replays": which, "grid_index": [int(i) for i in idx], "settings": rows,
                                 "J": [float(a["J"][i]) for i in idx], "statistic": [float(a["statistic"][i]) for i in idx],
                                 "feasible": [bool(a["feasible"][i]) for i in idx],
                                 "n_feasible_of_grid": int(np.count_nonzero(a["feasible"]))}
        for r in rows:
            if r not in rec["settings"]:
                rec["settings"].append(r)
        if fam == "recover":
            rec["recover"] = rows
    return rec


def cmd_cov2_settings(args, provider) -> Dict[str, Any]:
    """Replay the constant plans of every training start (resumable per start under <root>/cov2_const/) and write the
    settings table ``SPECS['train_cov2']['settings_file']``."""
    import multiprocessing as mp
    from dc import frontier as F
    t0 = time.time()
    starts = [(str(s), str(f), str(D.resolve_path(D._rel_or_abs(p)))) for s, f, p in provider.starts("train")]
    forced = {int(m): int(k) for m, k in provider.recover_forced().items()}
    cdir = Path(args.root) / "cov2_const"
    cdir.mkdir(parents=True, exist_ok=True)
    todo = [x for x in starts if not (cdir / f"{x[0]}.npz").exists()]
    print(f"[cov2-settings] {len(starts)} training starts, {len(todo)} to replay ({len(F.GRID)} constant plans x "
          f"{COV2_CONST['H']} months, plain and with {forced}) on {args.workers} worker(s)", flush=True)
    if todo:
        jobs = [(s, p, q, forced) for s, _, p in todo for q in (False, True)]
        got: Dict[str, Dict[bool, np.ndarray]] = {}
        with mp.get_context("fork").Pool(args.workers, initializer=_const_init, initargs=(args.provider,)) as pool:
            for k, (sid, quake, scal) in enumerate(pool.imap_unordered(_const_job, jobs, chunksize=1)):
                got.setdefault(sid, {})[quake] = scal
                if len(got[sid]) == 2:
                    arrs = const_family_arrays(got[sid][False], got[sid][True])
                    tmp = cdir / f"{sid}.tmp.npz"
                    np.savez(tmp, seed=np.int64(const_seed(sid)), grid=F.GRID,
                             **{f"{fam}__{k2}": v for fam, a in arrs.items() for k2, v in a.items()})
                    os.replace(tmp, cdir / f"{sid}.npz")
                    del got[sid]
                if (k + 1) % 40 == 0:
                    print(f"[cov2-settings] {k + 1}/{len(jobs)} start-variants replayed, {time.time() - t0:.0f} s", flush=True)
    table: Dict[str, Any] = {}
    for sid, fam_id, _ in starts:
        with np.load(cdir / f"{sid}.npz") as z:
            if int(z["seed"]) != const_seed(sid) or not np.array_equal(z["grid"], F.GRID):
                raise RuntimeError(f"{cdir / sid}.npz was made under another seed or grid")
            arrs = {fam: {k2: z[f"{fam}__{k2}"] for k2 in ("J", "slack", "statistic", "feasible")}
                    for fam, _, _ in COV2_CONST["families"]}
        table[sid] = {"family_id": fam_id, "seed": const_seed(sid), **cov2_select(arrs, int(COV2_CONST["top"]))}
    n_set = [len(v["settings"]) for v in table.values()]
    meta = {"what": "per training start, the best constant budget settings by task family ",
            "rule": COV2_CONST, "grid": "dc.frontier.GRID: tax 0..20 x road, fire, police levels 0..4 (2,625 settings)",
            "forced_quake": {str(m): k for m, k in forced.items()}, "starts": len(table),
            "settings_per_start": {"min": int(min(n_set)), "max": int(max(n_set)), "mean": float(np.mean(n_set))},
            "engine_city_months": int(len(starts) * 2 * len(F.GRID) * int(COV2_CONST["H"])),
            "uses": "training starts only; no held-out start, threshold or frontier plan",
            "code": {str(D._rel_or_abs(f)): _sha(f) for f in (ROOT / "code/dc/frontier.py", ROOT / "code/dc/tasks.py",
                                                               ROOT / "code/dc/oracle.py", ROOT / "code/dc/engine.py",
                                                               ROOT / "engine/libmicropolis.so", Path(__file__))},
            "seconds_this_call": round(time.time() - t0, 1)}
    out = D.resolve_path(SPECS["train_cov2"]["settings_file"])
    _write_json(out, {"meta": meta, "starts": table})
    print(f"[cov2-settings] {json.dumps(meta)} -> {out}", flush=True)
    return meta


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1) + "\n")
    os.replace(tmp, path)


def cmd_summary(args, splits, verify_results: Optional[Dict] = None, provider=None) -> Dict[str, Any]:
    out: Dict[str, Any] = {"root": str(args.root), "splits": {}, "generation": {}}
    g = getattr(provider, "grammar", None)
    rf = g()[0] if g else None
    for name in splits:
        p = Path(args.root) / name
        if (p / "traj.rec").exists():
            st = D.TrajStore(p)
            out["splits"][name] = D.summarise(st, workers=min(args.workers, 16), raster_fn=rf)
            if st.manifest and "generation" in st.manifest:
                out["generation"][name] = st.manifest["generation"]
    if verify_results is None:
        verify_results = {}
        for name in splits:
            f = Path(args.summary_out).parent / f"verify_{name}.json"
            if f.exists():
                verify_results[name] = json.loads(f.read_text())
    small = Path(args.root) / "train_small.npz"
    if small.exists():
        out["train_small"] = D.load_index(small)[1]
    if verify_results:
        out["verify"] = verify_results
    disk = {}
    for name in splits:
        p = Path(args.root) / name
        if p.exists():
            disk[name] = int(sum(f.stat().st_size for f in p.iterdir() if f.is_file()))
    out["disk_bytes"] = disk
    out["disk_bytes_total"] = int(sum(disk.values()) + (small.stat().st_size if small.exists() else 0))
    return out


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["all", "gen", "small", "verify", "summary", "bench", "backfill", "cov2-settings"])
    ap.add_argument("--splits", default=",".join(SPLIT_ORDER))
    ap.add_argument("--split", default="train_full", help="verify: which store")
    ap.add_argument("--n", type=int, default=None, help="verify: trajectories (default all)")
    ap.add_argument("--workers", type=int, default=28)
    ap.add_argument("--root", default=str(D.DATA_ROOT))
    ap.add_argument("--master-seed", type=int, default=MASTER_SEED)
    ap.add_argument("--provider", default="dc")
    ap.add_argument("--min-free-gb", type=float, default=50.0, help="free space to keep beyond what the run writes")
    ap.add_argument("--commit-seconds", type=float, default=10.0)
    ap.add_argument("--summary-out", default=str(RESULTS / "summary.json"))
    ap.add_argument("--train-h", default=None, help="smoke runs only: train_full months:count list, e.g. 48:50,120:5")
    ap.add_argument("--train-eval-h", default=None, help="smoke runs only: train_eval months:count list, e.g. 48:10")
    ap.add_argument("--heldout-per-family", default=None, help="smoke runs only: e.g. 48:2,120:1")
    ap.add_argument("--device", default="cuda:0", help="bench: loader device")
    ap.add_argument("--seconds", type=float, default=60.0, help="bench: measuring time")
    ap.add_argument("--batch-size", type=int, default=256, help="bench: batch size")
    ap.add_argument("--loader-workers", type=int, default=8, help="bench: loader worker processes")
    ap.add_argument("--k", type=int, default=1, help="bench: 1 = OneStepBatches, k > 1 = MultiStepBatches")
    ap.add_argument("--verify-train-n", type=int, default=500)
    args = ap.parse_args(argv)
    provider = load_provider(args.provider)
    splits = [s for s in args.splits.split(",") if s]
    Path(args.root).mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if args.stage == "gen":
        cmd_gen(args, provider, splits)
    elif args.stage == "small":
        cmd_small(args)
    elif args.stage == "verify":
        cmd_verify(args, provider, args.split, args.n)
    elif args.stage == "summary":
        s = cmd_summary(args, splits, provider=provider)
        _save_summary(args, s)
    elif args.stage == "backfill":
        cmd_backfill(args, provider, splits)
    elif args.stage == "cov2-settings":
        cmd_cov2_settings(args, provider)
    elif args.stage == "bench":
        st, idx = D.open_split(args.split, args.root)
        g = getattr(provider, "grammar", None)
        rf, sf = (g() if g else (None, None))
        res = D.bench_loader(st, idx, args.batch_size, args.device, seconds=args.seconds, num_workers=args.loader_workers,
                             k=args.k, raster_fn=rf, scalars_fn=sf)
        res["split"] = args.split
        print(f"[bench] {json.dumps(res)}", flush=True)
    else:
        gen = cmd_gen(args, provider, splits)
        small = cmd_small(args) if "train_full" in splits else None
        ver = {}
        if "train_full" in splits:
            ver["train_full"] = cmd_verify(args, provider, "train_full", args.verify_train_n)
        if "heldout_eval" in splits:
            ver["heldout_eval"] = cmd_verify(args, provider, "heldout_eval", None)
        s = cmd_summary(args, splits, ver, provider=provider)
        s["generation_this_call"] = gen
        s["wall_clock_s_all_stages"] = round(time.time() - t0, 1)
        _save_summary(args, s)


def _save_summary(args, s: Dict[str, Any]) -> None:
    out = Path(args.summary_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(s, f, indent=1)
        f.write("\n")
    print(f"[summary] written to {out}", flush=True)
    print(json.dumps(s, indent=1), flush=True)


if __name__ == "__main__":
    main()
