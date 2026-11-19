#!/usr/bin/env python
"""Speed and equivalence benches for ``dc.fast``.

  bench_fast.py speed --path audit --size 50m --chunk 256 --variants tag,raster,fused,graphs,fast
  bench_fast.py speed --path rl --size 50m --envs 200 --variants tag-eager,tag,fast
  bench_fast.py equiv --size 50m --n 2000
  bench_fast.py fidelity --out results/perf/fidelity_dev_fast

Model code comes from a git tag through ``dc.audit.load_emulator(ckpt, device, model_src)`` (default
ladder-v2). 50m uses the trained checkpoint; 15m and 100m have none, so a freshly initialised model of the
tag's size is written to a scratch checkpoint and loaded the same way (the trunk's cost does not depend on
the weights; the sampling tail's does, through the number of changed tiles). Every result is printed and
appended as one JSON line to ``--log`` with the command that produced it.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "hpr-dream"))

from dc import audit as A  # noqa: E402
from dc import fast  # noqa: E402

CKPT_50M = "<cache>/ckpt/pilot6_censored/samples_000600064.pt"
SCRATCH = Path(os.environ.get("BENCH_FAST_SCRATCH", "<cache>/perf"))


def log_line(args, rec: dict) -> None:
    rec = dict(rec, cmd=" ".join(sys.argv), gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
               torch=torch.__version__, at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print(json.dumps(rec), flush=True)
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        with open(args.log, "a") as f:
            f.write(json.dumps(rec) + "\n")


def ckpt_for(size: str, model_src: str) -> str:
    if os.environ.get("BENCH_FAST_CKPT"):          # a trained checkpoint of that size 
        return os.environ["BENCH_FAST_CKPT"]
    if size == "50m":
        return CKPT_50M
    p = SCRATCH / f"fresh_{size}_{model_src}.pt"
    if not p.exists():
        pkg, _ = A.code_package(model_src)
        M = importlib.import_module(f"{pkg.__name__}.model")
        torch.manual_seed(0)
        m = M.Emulator(size)
        p.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"model_config": m.cfg.to_dict(), "model": m.state_dict(), "ema": None, "samples": 0}, p)
    return str(p)


def workload(n_plans: int):
    inst = sorted(A.load_instances(A.TASKS_JSON, horizon=24), key=lambda i: (i.start_id, i.task))[0]
    plans = A.Pools(24).behaviour(inst.start_id)
    plans = np.concatenate([plans] * (n_plans // len(plans) + 1))[:n_plans]
    return inst, A.effective(plans, inst.task, 24)


def make_judge(args, chunk: int, buckets, variant: str):
    """The audit's own judge; variants switch exactly what the one-line changes would switch."""
    J = A.EmulatorJudge(ckpt_for(args.size, args.model_src), device="cuda:0", chunk=chunk, buckets=buckets,
                        compile_trunk=variant in ("tag", "raster", "tag-graphs"), model_src=args.model_src)
    m = J.model
    if variant in ("fused", "fast", "fused-eager", "graphs-eager", "tag-graphs", "fast-tail"):
        fast.accelerate(m, fused=variant in ("fused", "fast", "fused-eager", "fast-tail"),
                        compile=variant in ("fused", "fast", "tag-graphs", "fast-tail"),
                        graphs=variant in ("fast", "graphs-eager", "tag-graphs", "fast-tail"))
        if variant == "fast-tail":                       # the refused lever, for its measurement only
            fast.experimental_compiled_tail(m)
    return J


def cmd_speed(args) -> None:
    variants = [v for v in args.variants.split(",") if v]
    orig_rollout = A.emulator_rollout
    for variant in variants:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        if args.path == "audit":
            chunk, K = args.chunk, args.K
            buckets = tuple(int(b) for b in args.buckets.split(",")) if args.buckets else (16, 64, chunk)
            J = make_judge(args, chunk, buckets, variant)
            # "default": the audit's own adaptor (the model's default decoding, a) against fast.emulator_rollout;
            # another --overlay: both with that decoding (the tag with the host raster, as the audit builds it)
            dec = {} if args.overlay == "default" else {"overlay": args.overlay, "temperature": 1.0}
            if variant in ("tag", "tag-eager"):
                A.emulator_rollout = orig_rollout if not dec else \
                    (lambda m, s0, P, K_, dev, max_batch: _host_rollout(m, s0, P, K_, dev, max_batch, args.overlay))
            else:
                A.emulator_rollout = lambda m, s0, P, K_, dev, max_batch: fast.emulator_rollout(m, s0, P, K_, dev,
                                                                                                 max_batch, **dec)
            n = args.plans or (chunk // K) * args.calls_chunks
            inst, eff = workload(max(n, chunk // K))
            t = time.time()
            J.samples(inst, eff[: chunk // K], K, ("warm",))
            if variant not in ("tag", "raster"):
                J.samples(inst, eff[: chunk // K], K, ("warm2",))
            torch.cuda.synchronize()
            warm = time.time() - t
            rates = []
            for rep in range(args.reps):
                torch.cuda.synchronize()
                t = time.time()
                J.samples(inst, eff[:n], K, ("bench", rep))
                torch.cuda.synchronize()
                rates.append(n * K * 24 / (time.time() - t))
            log_line(args, {"bench": "speed", "path": "audit", "size": args.size, "variant": variant, "chunk": chunk,
                            "K": K, "buckets": list(J.buckets), "overlay": args.overlay, "month_steps_per_call": n * K * 24,
                            "padded_month_steps": J.padded_month_steps,
                            "rates": [round(r, 1) for r in rates], "median_rate": round(float(np.median(rates)), 1),
                            "warmup_s": round(warm, 1), "peak_mem_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2),
                            "fast": fast.describe(J.model)})
            del J
        else:
            from dc import rl as R
            J = make_judge(args, 128, (16, 64, 128), "tag" if variant == "tag" else
                           ("tag-eager" if variant == "tag-eager" else variant))
            m = J.model
            inst, eff = workload(512)
            s0 = J.state0(inst)
            B = args.envs
            st = {k: v.repeat(B, *([1] * (v.dim() - 1))).clone() for k, v in s0.items()}
            idx = np.arange(B) % len(eff)
            raster_fn = R.raster_torch if variant in ("tag", "tag-eager") else (lambda rows, dev: fast.raster_rows(rows, dev))

            def step(st, h):
                rows = eff[idx, h % 24]
                r = raster_fn(rows, J.device)
                a = R.act_scalars_torch(rows, J.device)
                dec = {} if args.overlay == "default" else {"overlay": args.overlay, "temperature": 1.0}
                return m.sample_next(st, r.to(st["flags"].dtype), a.float(), max_batch=B, **dec)

            torch.manual_seed(0)
            t = time.time()
            for h in range(4):
                st = step(st, h)
            torch.cuda.synchronize()
            warm = time.time() - t
            rates = []
            for rep in range(args.reps):
                torch.cuda.synchronize()
                t = time.time()
                for h in range(24):
                    st = step(st, h)
                torch.cuda.synchronize()
                rates.append(B * 24 / (time.time() - t))
            log_line(args, {"bench": "speed", "path": "rl", "size": args.size, "variant": variant, "envs": B,
                            "overlay": args.overlay, "raster": "rl.raster_torch" if variant in ("tag", "tag-eager") else "fast.raster_rows",
                            "rates": [round(r, 1) for r in rates], "median_rate": round(float(np.median(rates)), 1),
                            "warmup_s": round(warm, 1), "peak_mem_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2),
                            "fast": fast.describe(m)})
            del J, m, st
    A.emulator_rollout = orig_rollout


# ----------------------------------------------------------------------------------------------
# Equivalence (a): every head's distribution parameters on held-out transitions, same inputs and z
# ----------------------------------------------------------------------------------------------
def heldout_dev(n: int):
    from dc import data
    from dc import fidelity as fd
    store, _ = data.open_split("heldout_eval")
    trajs = fd.trajectories_from_store(store, store.traj_ids().tolist())
    pairs, plans, desc = fd.selection(trajs, "dev", n, fd.DEV_N_PLANS, fd.DEV_H)
    return fd, trajs, pairs, plans, desc


def head_params(model, dense, s0, s1, act, raster) -> dict:
    """Every head's distribution parameters given the trunk's output ``dense`` (teacher-forced on the engine's
    next state s1 where a head needs the next state, as in ``log_prob``)."""
    mod = sys.modules[type(model).__module__]
    feat, dl, half_par, eighth_par, pooled, terrain_par, com_par, cond_in = dense
    dl = dl.float()
    out = {"tile_gate_logit": dl[..., 0], "flag_power_logit_dense": dl[..., 1:]}
    i0, i1 = s0["tile_index"], s1["tile_index"]
    bi, xi, yi = (i1 != i0).nonzero(as_tuple=True)
    if bi.numel():
        f = feat[bi, xi, yi]
        lg = model._cat_logits(f, i0[bi, xi, yi])
        lp = torch.log_softmax(lg, dim=-1)
        out["tile_cat_logp"] = torch.where(torch.isfinite(lp), lp, torch.zeros_like(lp))
        out["new_flag_logit"] = model._new_flag_logits(f, i1[bi, xi, yi])
    for name, par, nch in (("half", half_par, mod.N_HALF), ("eighth", eighth_par, mod.N_EIGHTH),
                           ("terrain", terrain_par, 1), ("com_rate", com_par, 1)):
        g, lpi, dmu, ls = model._split_overlay(par, nch)
        out.update({f"{name}.gate": g, f"{name}.logit_pi": lpi, f"{name}.mu": dmu, f"{name}.log_s": ls})
    g, lpi, mu, ls = model._scalar_dist(pooled, s0, s1, raster, cond_in)
    D = model.target_delta_scale()
    out.update({"stage2.gate": g, "stage2.logit_pi": lpi, "stage2.mu_over_scale": mu / D[:, None], "stage2.log_s": ls})
    raw = mod.bk_raw(s0, s1, s1["build_cost"], model.listed_spend(raster))
    g, lpi, mu, ls = model.bk_dist_from_raw(raw, act, s0["scalars"][:, mod.SC_TIME])
    D3 = model.bk_delta_scale()
    out.update({"stage3.gate": g, "stage3.logit_pi": lpi, "stage3.mu_over_scale": mu / D3[:, None], "stage3.log_s": ls})
    terms = model._terms(dense, s0, s1, act, raster)
    for k in model.recon_terms:
        out[f"loglik.{k}"] = terms[k]
    return {k: v.float() for k, v in out.items()}


def cmd_equiv(args) -> None:
    dev = torch.device("cuda:0")
    model, ck, desc, _ = A.load_emulator(ckpt_for(args.size, args.model_src), dev, args.model_src)
    fd, trajs, pairs, plans, sel = heldout_dev(args.n)
    trunks = {"eager": model.trunk, "compiled": torch.compile(model.trunk, dynamic=False),
              "fast": fast.GraphedTrunk(torch.compile(fast.make_fused_trunk(model), dynamic=False))}
    pairs_cmp = (("compiled", "eager"), ("fast", "eager"), ("fast", "compiled"))
    gmax = {}
    sub = {}
    scale = {}
    samp_diff = {p: {} for p in pairs_cmp}
    rng = torch.Generator(device=dev).manual_seed(1234)
    t0 = time.time()
    n_states = 0
    for a in range(0, len(pairs), args.batch):
        s0, r, act, s1 = fd.onestep_batch(trajs, pairs[a:a + args.batch], dev)
        B = s0["tile_index"].shape[0]
        n_states += B
        z = torch.randn(B, model.cfg.z_dim, device=dev, generator=torch.Generator(device=dev).manual_seed(a))
        with torch.no_grad():
            with torch.autocast("cuda", dtype=torch.bfloat16):
                cond_in = model.cond_input(s0, act, r)
            res, smp = {}, {}
            for name, fn in trunks.items():
                object.__setattr__(model, "_trunk_fn", fn)
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    dense = model._dense(s0, r, cond_in, z)
                res[name] = head_params(model, dense, s0, s1, act, r)
                torch.manual_seed(10_000 + a)
                smp[name] = model.sample_next(s0, r, act, z=z, temperature=1.0, overlay="sample")
            for k, v in res["eager"].items():
                scale.setdefault(k, []).append(v.abs().mean().item())
            for p in pairs_cmp:
                for k in res["eager"]:
                    d = (res[p[0]][k] - res[p[1]][k]).abs().flatten()
                    key = (p, k)
                    gmax[key] = max(gmax.get(key, 0.0), d.max().item())
                    idx = torch.randint(0, d.numel(), (min(d.numel(), 20000),), device=dev, generator=rng)
                    sub.setdefault(key, []).append(d[idx].cpu())
                for k in smp["eager"]:
                    x, y = smp[p[0]][k], smp[p[1]][k]
                    c = samp_diff[p].setdefault(k, [0, 0])
                    c[0] += int((x != y).sum().item())
                    c[1] += x.numel()
    object.__setattr__(model, "_trunk_fn", model.trunk)
    rows = []
    for k in res["eager"]:
        row = {"head": k, "mean_abs_value": float(np.mean(scale[k]))}
        for p in pairs_cmp:
            q = torch.cat(sub[(p, k)]).double()
            tag = f"{p[0]}_vs_{p[1]}"
            row[tag] = {"max": gmax[(p, k)], "p999": float(torch.quantile(q, 0.999)), "p99": float(torch.quantile(q, 0.99)),
                        "mean": float(q.mean())}
        ref = row["compiled_vs_eager"]
        f = row["fast_vs_eager"]
        row["pass"] = bool(f["max"] <= max(2 * ref["max"], 1e-5) and f["p999"] <= max(2 * ref["p999"], 1e-5))
        rows.append(row)
    samples = {f"{p[0]}_vs_{p[1]}": {k: {"differ": c[0], "of": c[1], "share": c[0] / max(c[1], 1)}
                                     for k, c in samp_diff[p].items()} for p in pairs_cmp}
    out = {"bench": "equiv", "size": args.size, "model": desc, "selection": {k: sel[k] for k in sel if k != "pairs"} if isinstance(sel, dict) else None,
           "n_states": n_states, "seconds": round(time.time() - t0, 1), "all_pass": all(r["pass"] for r in rows),
           "criterion": "fast-vs-eager max and p99.9 |difference| each <= max(2 x compiled-vs-eager, 1e-5), per head",
           "heads": rows, "samples_same_seed": samples, "fast_graphs": trunks["fast"].n_replays}
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(out, indent=1, default=str))
    print(f"equiv {args.size}: {n_states} held-out states, all pass: {out['all_pass']}")
    print(f"{'head':28s} {'mean|v|':>9s} | {'cmp-eager max':>13s} {'p99.9':>9s} | {'fast-eager max':>14s} {'p99.9':>9s} | {'fast-cmp max':>12s} | pass")
    for r in rows:
        c, f, fc = r["compiled_vs_eager"], r["fast_vs_eager"], r["fast_vs_compiled"]
        print(f"{r['head']:28s} {r['mean_abs_value']:9.3g} | {c['max']:13.3g} {c['p999']:9.3g} | {f['max']:14.3g} {f['p999']:9.3g} | "
              f"{fc['max']:12.3g} | {r['pass']}")
    print("samples under the same seed and z, share of elements that differ:")
    for p, d in samples.items():
        print(" ", p, {k: f"{v['share']:.2e}" for k, v in d.items()})
    log_line(args, {k: v for k, v in out.items() if k not in ("heads",)} | {"n_heads": len(rows),
                                                                          "n_pass": sum(r["pass"] for r in rows)})


# ----------------------------------------------------------------------------------------------
# Equivalence (b): fidelity on the development selection, decoding a, tag against fast on the same card
# ----------------------------------------------------------------------------------------------
B3_DEV = ROOT / "results" / "fidelity" / "pilot6_censored"


def cmd_fidelity(args) -> None:
    sys.path.insert(0, str(ROOT / "code" / "scripts"))
    from pilot_check import ROWS, get
    dev = torch.device("cuda:0")
    fd, trajs, pairs, plans, sel = heldout_dev(fd_n := 2000)
    out_dir = Path(args.out or ROOT / "results" / "perf" / "fidelity_dev")
    out_dir.mkdir(parents=True, exist_ok=True)
    res = {}
    if args.tag_json:              # the tag's result from another run (e.g. another batch layout)
        res["tag"] = json.loads(Path(args.tag_json).read_text())
    variants = [v for v in args.variants.split(",") if v]
    fv = [v for v in variants if v != "tag"][0]
    if "tag" not in variants and "tag" not in res:
        raise SystemExit("fidelity: give --tag-json or include tag in --variants")
    for variant in ["tag"] + [v for v in variants if v != "tag"]:
        p = out_dir / f"{variant}_seed{args.eval_seed}.json"
        if variant in res:
            continue
        if p.exists():
            res[variant] = json.loads(p.read_text())
            continue
        model, ck, desc, _ = A.load_emulator(CKPT_50M, dev, args.model_src)
        if variant == "tagc":                            # the tag with its own compiled trunk (training's mode)
            model.compile_trunk(dynamic=False)
        if variant in ("fast", "fasttail"):
            fast.accelerate(model)
            if variant == "fasttail":                    # the refused lever, for its measurement only
                fast.experimental_compiled_tail(model)
        t = time.time()
        one = fd.eval_model_onestep(model, trajs, pairs, dev, seed=args.eval_seed)
        ro = fd.eval_model_rollouts(model, trajs, plans, dev, H=fd.DEV_H, K=8, temperature=1.0, overlay="sample",
                                    batch_plans=args.batch, seed=args.eval_seed)
        r = {"variant": variant, "model": desc, "fast": fast.describe(model), "eval_seed": args.eval_seed,
             "batch_plans": args.batch, "decoding": {"name": "a", "temperature": 1.0, "overlay": "sample"},
             "seconds": round(time.time() - t, 1), "onestep": one, "rollouts": ro}
        fd.to_json(r, p)
        res[variant] = json.loads(p.read_text())
        del model
        torch.cuda.empty_cache()
    b3 = {s: json.loads((B3_DEV / d / f"pilot6_censored_samples_000600064_dec-a{suf}.json").read_text())
          for s, d, suf in (("s0", "dev", ""), ("s1", "dev_noise_seed1", "_seed1"))}
    lines = [f"Fidelity on the development selection (decoding a, K = 8, {len(pairs)} transitions, {len(plans)} plans), "
             f"pilot6_censored at 600,064 samples, model code {args.model_src}. tag and fast: GPU 1, eval seed "
             f"{args.eval_seed}; plans per rollout batch: tag {res['tag'].get('batch_plans')}, {fv} "
             f"{res[fv].get('batch_plans')} (equal: the same random stream; different: another batch layout, so "
             "other draws). B3: results/fidelity/pilot6_censored (GPU 0, seeds 0 and 1); evaluation noise = "
             "|B3 seed 0 - B3 seed 1|.", "",
             "| metric | tag (GPU 1) | fast (GPU 1) | abs(fast - tag) | B3 seed 0 | B3 seed 1 | evaluation noise | fast - tag within noise |",
             "|---|---|---|---|---|---|---|---|"]
    n_ok = 0
    for label, path, _hib in ROWS:
        vt, vf, v0, v1 = (get(res["tag"], path), get(res[fv], path), get(b3["s0"], path), get(b3["s1"], path))
        noise = abs(v0 - v1)
        ok = abs(vf - vt) <= noise
        n_ok += ok
        lines.append(f"| {label} | {vt:.4f} | {vf:.4f} | {abs(vf - vt):.4f} | {v0:.4f} | {v1:.4f} | {noise:.4f} | {'yes' if ok else 'NO'} |")
    lines += ["", f"{n_ok} of {len(ROWS)} rows: abs({fv} - tag) <= evaluation noise. Seconds: tag {res['tag']['seconds']}, "
              f"{fv} {res[fv]['seconds']} (one-step evaluation + rollouts)."]
    (out_dir / f"fidelity_check_seed{args.eval_seed}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    log_line(args, {"bench": "fidelity", "rows_within_noise": n_ok, "rows": len(ROWS),
                    "seconds": {k: res[k]["seconds"] for k in res}})


# ----------------------------------------------------------------------------------------------
# The tail lever: identical trunk output in, samples out of the tag's tail and of the compiled tail
# ----------------------------------------------------------------------------------------------
def cmd_tailcheck(args) -> None:
    dev = torch.device("cuda:0")
    ck = ckpt_for(args.size, args.model_src)
    mA, _, desc, _ = A.load_emulator(ck, dev, args.model_src)
    mB, _, _, _ = A.load_emulator(ck, dev, args.model_src)
    fast.experimental_compiled_tail(mB)
    fd, trajs, pairs, plans, sel = heldout_dev(args.n)
    diff, tot = {}, {}
    rng_equal = 0
    times = {"tag": 0.0, "tail": 0.0}
    n_states = 0
    for rep, a in enumerate(range(0, len(pairs), args.batch)):
        s0, r, act, s1 = fd.onestep_batch(trajs, pairs[a:a + args.batch], dev)
        B = s0["tile_index"].shape[0]
        n_states += B
        with torch.no_grad():
            z = torch.randn(B, mA.cfg.z_dim, device=dev, generator=torch.Generator(device=dev).manual_seed(a))
            with torch.autocast("cuda", dtype=torch.bfloat16):
                dense = mA._dense(s0, r, mA.cond_input(s0, act, r), z)
            outs, states = {}, {}
            for name, m in (("tag", mA), ("tail", mB), ("tag", mA), ("tail", mB)):   # second pass timed
                torch.manual_seed(20_000 + a)
                torch.cuda.synchronize()
                t = time.perf_counter()
                outs[name] = m._sample_from_dense(dense, s0, act, 1.0, "sample", r)
                torch.cuda.synchronize()
                if rep > 0:
                    times[name] += (time.perf_counter() - t) / 2
                states[name] = torch.cuda.get_rng_state()
        rng_equal += int(torch.equal(states["tag"], states["tail"]))
        for k in outs["tag"]:
            x, y = outs["tag"][k], outs["tail"][k]
            diff[k] = diff.get(k, 0) + int((x != y).sum().item())
            tot[k] = tot.get(k, 0) + x.numel()
    n_b = len(range(0, len(pairs), args.batch))
    rec = {"bench": "tailcheck", "size": args.size, "n_states": n_states, "batches": n_b,
           "rng_state_equal_after_tail": f"{rng_equal} of {n_b}",
           "share_differing": {k: diff[k] / tot[k] for k in diff}, "differing": diff,
           "tail_ms_per_batch": {k: round(1000 * v / max(n_b - 1, 1), 2) for k, v in times.items()}, "batch": args.batch}
    log_line(args, rec)


def cmd_fidelity_seeds(args) -> None:
    """Every evaluation JSON of the tag and of the fast path under results/perf/fidelity_dev*/ (several noise seeds
    and batch layouts) and the two: per metric, mean and standard deviation over evaluations, and the
    difference of means against twice its standard error (Welch). Criterion fixed before the extra seeds ran:
    abs(mean fast - mean tag) <= 2 x sqrt(sd_fast^2 / n_fast + sd_tag^2 / n_tag) on each row."""
    sys.path.insert(0, str(ROOT / "code" / "scripts"))
    from pilot_check import ROWS, get
    ev = {"tag": [], "fast": []}
    fname, tname = args.fast_name, args.tag_name
    for d in sorted((ROOT / "results" / "perf").glob("fidelity_dev*")):
        for p in sorted(d.glob("*_seed*.json")):
            v = p.name.split("_seed")[0]
            v = "fast" if v == fname else ("tag" if v == tname else None)
            if v in ev:
                r = json.loads(p.read_text())
                ev[v].append((f"{d.name}/{p.name} (batch {r.get('batch_plans')})", r))
    b3 = [(f"B3 {d}", json.loads((B3_DEV / d / f"pilot6_censored_samples_000600064_dec-a{suf}.json").read_text()))
          for d, suf in (("dev", ""), ("dev_noise_seed1", "_seed1"))]
    if args.with_b3:
        ev["tag"] += b3
    lines = [f"Fidelity on the development selection, decoding a, pilot6_censored at 600,064 samples (model code ladder-v2).",
             f"Columns 'tag' = variant {tname}{' and B3' if args.with_b3 else ''}, columns 'fast' = variant {fname} "
             "(tag: the eager trunk, as eval_fidelity.py runs it; tagc: the tag's compiled trunk; fast: dc.fast).",
             "", "Evaluations, tag: " + "; ".join(n for n, _ in ev["tag"]),
             "", "Evaluations, fast: " + "; ".join(n for n, _ in ev["fast"]), "",
             "| metric | tag mean | tag sd | n | fast mean | fast sd | n | fast - tag | 2 x SE | within |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    n_ok = 0
    for label, path, _ in ROWS:
        t = np.array([get(r, path) for _, r in ev["tag"]], dtype=float)
        f = np.array([get(r, path) for _, r in ev["fast"]], dtype=float)
        se = math.sqrt(t.var(ddof=1) / len(t) + f.var(ddof=1) / len(f))
        d = f.mean() - t.mean()
        ok = abs(d) <= 2 * se
        n_ok += ok
        lines.append(f"| {label} | {t.mean():.4f} | {t.std(ddof=1):.4f} | {len(t)} | {f.mean():.4f} | {f.std(ddof=1):.4f} | "
                     f"{len(f)} | {d:+.4f} | {2 * se:.4f} | {'yes' if ok else 'NO'} |")
    lines += ["", f"{n_ok} of {len(ROWS)} rows within 2 standard errors (at 95 per cent per row about 1 of 19 falls "
              "outside by chance when the two are the same model)."]
    out = Path(args.out or ROOT / "results" / "perf" / "fidelity_seeds.md")
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def cmd_table(args) -> None:
    """speed.jsonl -> a markdown table (the last record of each configuration), with gains against the tag."""
    recs = [json.loads(l) for l in Path(args.log).read_text().splitlines() if l.strip()]
    last = {}
    for r in recs:
        if r.get("bench") != "speed":
            continue
        cfg = (r["path"], r["size"], r.get("chunk", r.get("envs")), r.get("K"), tuple(r.get("buckets") or ()),
               r.get("month_steps_per_call"), r["overlay"])
        last[(cfg, r["variant"])] = r
    cfgs = sorted({c for c, _ in last}, key=lambda c: (c[0], ["15m", "50m", "100m"].index(c[1]) if c[1] in ("15m", "50m", "100m") else 9,
                                                     c[2], c[4], c[5] or 0))
    L = ["| path | size | rows (chunk or envs) | K | buckets | month-steps per call | variant | month-steps/s (median of reps) | x tag (compiled) | peak GB |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for c in cfgs:
        base = last.get((c, "tag"))
        for (c2, v), r in sorted(last.items(), key=lambda kv: kv[1]["at"]):
            if c2 != c:
                continue
            g = f"{r['median_rate'] / base['median_rate']:.3f}" if base else ""
            L.append(f"| {c[0]} | {c[1]} | {c[2]} | {c[3] or ''} | {','.join(map(str, c[4]))} | {c[5] or ''} | {v} | "
                     f"{r['median_rate']:,.0f} | {g} | {r['peak_mem_gb']} |")
    out = Path(args.out or Path(args.log).with_name("speed_table.md"))
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


def _host_rollout(model, state0, plans, K, device, max_batch, overlay):
    """``dc.audit.emulator_rollout`` with another overlay decoding (host raster, as the audit builds it)."""
    from dc.grammar import N_COLS, action_scalars_batch, raster_batch
    B, H = plans.shape[0], plans.shape[1]
    act = torch.from_numpy(action_scalars_batch(plans.reshape(-1, N_COLS)).reshape(B, H, -1)).to(device)
    s0 = {k: v.expand(B, *v.shape[1:]) for k, v in state0.items()}
    traj, _ = model.rollout(s0, lambda h: torch.from_numpy(raster_batch(plans[:, h])).to(device, non_blocking=True),
                            act, K=K, temperature=1.0, max_batch=max_batch, overlay=overlay)
    return traj.double().cpu().numpy()


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("speed")
    sp.add_argument("--path", choices=("audit", "rl"), default="audit")
    sp.add_argument("--size", default="50m")
    sp.add_argument("--model-src", default="ladder-v2")
    sp.add_argument("--chunk", type=int, default=256)
    sp.add_argument("--buckets", default="")
    sp.add_argument("--K", type=int, default=2)
    sp.add_argument("--calls-chunks", type=int, default=2, help="plans per timed call, in chunks")
    sp.add_argument("--plans", type=int, default=0, help="plans per timed call (overrides --calls-chunks)")
    sp.add_argument("--envs", type=int, default=200)
    sp.add_argument("--overlay", default="default", help="default: the model's own decoding (a), which the audit uses; mean / sample: explicit")
    sp.add_argument("--variants", default="tag,fast")
    sp.add_argument("--reps", type=int, default=3)
    sp.add_argument("--log", default=str(ROOT / "results" / "perf" / "bench" / "speed.jsonl"))
    for name in ("equiv", "fidelity", "tailcheck"):
        p = sub.add_parser(name)
        p.add_argument("--size", default="50m")
        p.add_argument("--model-src", default="ladder-v2")
        p.add_argument("--n", type=int, default=2000)
        p.add_argument("--batch", type=int, default=128)
        p.add_argument("--out", default="")
        p.add_argument("--eval-seed", type=int, default=0)
        p.add_argument("--tag-json", default="", help="fidelity: the tag's result JSON from another run")
        p.add_argument("--variants", default="tag,fast", help="fidelity: tag and one of fast, fasttail, tagc")
        p.add_argument("--log", default=str(ROOT / "results" / "perf" / "bench" / f"{name}.jsonl"))
    fs = sub.add_parser("fidelity-seeds")
    fs.add_argument("--with-b3", action="store_true", help="count the two GPU 0 evaluations as tag evaluations")
    fs.add_argument("--fast-name", default="fast", help="the variant compared with the reference: fast, fasttail, tagc")
    fs.add_argument("--tag-name", default="tag", help="the reference variant: tag (eager trunk) or tagc (compiled)")
    fs.add_argument("--out", default="")
    tp = sub.add_parser("table")
    tp.add_argument("--log", default=str(ROOT / "results" / "perf" / "bench" / "speed.jsonl"))
    tp.add_argument("--out", default="")
    args = ap.parse_args()
    if args.cmd == "speed":
        cmd_speed(args)
    elif args.cmd == "equiv":
        cmd_equiv(args)
    elif args.cmd == "fidelity":
        cmd_fidelity(args)
    elif args.cmd == "tailcheck":
        cmd_tailcheck(args)
    elif args.cmd == "table":
        cmd_table(args)
    elif args.cmd == "fidelity-seeds":
        cmd_fidelity_seeds(args)


if __name__ == "__main__":
    main()
