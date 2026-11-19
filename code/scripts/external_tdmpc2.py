#!/usr/bin/env python3
"""External check: the hpr_dream instrument on released TD-MPC2 single-task checkpoints.

Grader: the checkpoint's own encoder, latent dynamics and reward head (imagined 50-step return).
Oracle: the same 50 actions (each repeated twice) executed in dm_control from the exactly restored
start state, with the task's own reward. Inference only. Run only with wm2-ext/venv/bin/python.

Commands: ``determinism`` (oracle replay check; must pass before ``audit``), ``audit`` (calibration,
attacks, noise floors, MPPI; resumable), ``report`` (cards and summary from saved results).
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "hpr-dream"))
import numpy as np  # noqa: E402
import hpr_dream as hd  # noqa: E402
from hpr_dream.adaptors import tdmpc2 as td  # noqa: E402

RESULTS = ROOT / "results/external"
CARDS = ROOT / "cards/external"
BUDGETS = (1, 10, 100, 1000)
N_FIT, N_CHECK, N_POOL = 600, 400, 1000
THETA_QUANTILE = 0.65  # target oracle acceptance 0.35 on behaviour plans
ACCEPT_RANGE = (0.2, 0.5)
ATTACKS = (("random_shooting", "margin"), ("cem", "margin"), ("random_shooting", "verdict"))


def dump(path, obj):
    hd.write_card(obj, str(path))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seed_rng(task_index, instance, purpose, seed=0):
    """Behaviour plans (purpose 0) and random-shooting proposals (purpose 1)."""
    return np.random.default_rng(np.random.SeedSequence([951733, task_index, instance, purpose, seed]))


STREAMS = {"cem": 1, "tie": 2, "flip": 3, "residual": 4}


def attack_rng(task_index, instance, stream, attack, budget, seed):
    """One independent stream per (instance, stream, attacker and scoring, budget, attacker seed)."""
    return np.random.default_rng(np.random.SeedSequence(
        [951734, task_index, instance, STREAMS[stream], ATTACKS.index(attack), budget, seed]))


# ------------------------------------------------------------------------------------------------
# oracle determinism


def trace_worker(state_path, plan_path, out_path):
    state = td.StartState.load(state_path)
    env = td.make_env(state.task, state.seed + 123)
    result = td.replay(env, state, np.load(plan_path), trace=True)
    np.savez(out_path, rewards=result[0], physics=result[1], integration=result[2])
    env.close()


def continuation(task, state, plan):
    """Reach the start from its seed and prefix, then step the plan, with no state restoration."""
    env = td.make_env(task, state.seed)
    dim = state.prefix.shape[1]
    for action in td.decode_plans(state.prefix.reshape(1, -1), dim, len(state.prefix))[0]:
        for _ in range(td.ACTION_REPEAT):
            env.step(action.astype(np.float64))
    assert td.integration_state(env).tobytes() == state.integration.tobytes()
    return env, td.replay(env, state, plan, trace=True, restore_start=False)


def determinism(tasks, n_starts):
    folder = RESULTS / "determinism"
    folder.mkdir(parents=True, exist_ok=True)
    rows, starts = [], []
    for task in tasks:
        state = td.capture_start(task, 701)
        state_path = folder / f"{task}-start.npz"
        state.save(state_path)
        dim = state.prefix.shape[1]
        plan = td.behaviour_plans(np.random.default_rng(702), 1, dim)[0]
        plan_path = folder / f"{task}-plan.npy"
        np.save(plan_path, plan)
        env, baseline = continuation(task, state, plan)
        first = td.replay(env, state, plan, trace=True)
        # Dirty the reused environment with another sequence before restoring.
        td.replay(env, state, td.behaviour_plans(np.random.default_rng(703), 1, dim)[0])
        within = td.replay(env, state, plan, trace=True)
        env.close()
        fresh = td.make_env(task, 999)
        td.restore(fresh, state)
        obs_exact = td.observation(fresh).tobytes() == state.obs.tobytes()
        recreated = td.replay(fresh, state, plan, trace=True)
        fresh.close()
        child = folder / f"{task}-child.npz"
        subprocess.run([sys.executable, __file__, "trace", "--state", str(state_path),
                        "--plan", str(plan_path), "--output", str(child)], check=True)
        with np.load(child) as d:
            across = (d["rewards"], d["physics"], d["integration"])
        for mode, result in (("original_continuation", first), ("within_process", within),
                             ("recreated_environment", recreated), ("across_processes", across)):
            equal = [a.tobytes() == b.tobytes() for a, b in zip(baseline, result)]
            deviations = [float(np.max(np.abs(a - b))) for a, b in zip(baseline, result)]
            rows.append(dict(task=task, mode=mode, dmc_steps=len(result[0]),
                             physics_bytes_equal=equal[1], integration_bytes_equal=equal[2],
                             reward_bytes_equal=equal[0], max_physics_deviation=deviations[1],
                             max_integration_deviation=deviations[2], max_reward_deviation=deviations[0],
                             restored_observation_bytes_equal=obs_exact))
        np.savez(folder / f"{task}-reference.npz", rewards=baseline[0], physics=baseline[1], integration=baseline[2])
        # Every audit start: continuation from seed + prefix against a restored replay in a new environment.
        for i in range(n_starts):
            st = td.capture_start(task, 1000 + i)
            p = td.behaviour_plans(np.random.default_rng(704 + i), 1, dim)[0]
            env, ref = continuation(task, st, p)
            env.close()
            env = td.make_env(task, 4242 + i)
            got = td.replay(env, st, p, trace=True)
            td.restore(env, st)
            obs = td.observation(env)
            env.close()
            starts.append(dict(task=task, start=i, state_sha256=st.sha256,
                               trace_bytes_equal=all(a.tobytes() == b.tobytes() for a, b in zip(ref, got)),
                               max_integration_deviation=float(np.max(np.abs(ref[2] - got[2]))),
                               restored_observation_bytes_equal=obs.tobytes() == st.obs.tobytes(),
                               restored_observation_max_deviation=float(np.max(np.abs(obs - st.obs)))))
    tolerance = max([r["max_integration_deviation"] for r in rows] + [s["max_integration_deviation"] for s in starts])
    result = dict(rows=rows, audit_starts=starts, tolerance=tolerance)
    dump(folder / "check.json", result)
    lines = ["task mode steps physics_exact integration_exact rewards_exact max_abs_state max_abs_reward"]
    for r in rows:
        lines.append(f'{r["task"]} {r["mode"]} {r["dmc_steps"]} {int(r["physics_bytes_equal"])} '
                     f'{int(r["integration_bytes_equal"])} {int(r["reward_bytes_equal"])} '
                     f'{r["max_integration_deviation"]:.17g} {r["max_reward_deviation"]:.17g}')
    lines.append(f"restored_observation_bytes_equal={int(all(r['restored_observation_bytes_equal'] for r in rows))}")
    lines.append("audit starts (seed 1000+i, 12-action prefix): continuation vs restored replay in a new environment")
    lines.append("task starts trace_exact max_abs_state restored_obs_exact max_abs_restored_obs")
    for task in tasks:
        s = [x for x in starts if x["task"] == task]
        lines.append(f"{task} {len(s)} {sum(x['trace_bytes_equal'] for x in s)} "
                     f"{max(x['max_integration_deviation'] for x in s):.17g} "
                     f"{sum(x['restored_observation_bytes_equal'] for x in s)} "
                     f"{max(x['restored_observation_max_deviation'] for x in s):.17g}")
    lines.append(f"oracle_tolerance={tolerance:.17g}")
    output = "\n".join(lines) + "\n"
    (folder / "output.txt").write_text(output)
    print(output, end="", flush=True)
    return result


# ------------------------------------------------------------------------------------------------
# calibration, residual pool, attacks


def table(rows):
    return {k: [r[k] for r in rows] for k in rows[0]}


def calibrate(task, task_index, index, pool, workers):
    """Oracle returns of N_FIT + N_CHECK + N_POOL behaviour plans; theta, sd, acceptance check."""
    folder = RESULTS / task
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"calibration-{index:02d}.json"
    if path.exists():
        return json.loads(path.read_text())
    started = time.monotonic()
    state_path = td.EXT_ROOT / "states" / f"{task}-{index:02d}.npz"
    if state_path.exists():
        state = td.StartState.load(state_path)
    else:
        state = td.capture_start(task, 1000 + index)
        state.save(state_path)
    oracle = td.Oracle(state, pool, workers)
    behaviour = td.behaviour_plans(seed_rng(task_index, index, 0), N_FIT + N_CHECK + N_POOL, state.prefix.shape[1])
    real = oracle(behaviour)
    fit, check = real[:N_FIT], real[N_FIT:N_FIT + N_CHECK]
    theta = float(np.quantile(fit, THETA_QUANTILE))
    sd = float(np.std(real[:N_FIT + N_CHECK], ddof=1))
    check_rate = float(np.mean(check >= theta))
    ok = bool(sd > 0 and ACCEPT_RANGE[0] <= check_rate <= ACCEPT_RANGE[1])
    np.savez_compressed(folder / f"behaviour-{index:02d}.npz", plans=behaviour, oracle_returns=real, theta=theta, sd=sd)
    result = dict(instance=index, task=task, state=str(state_path), state_seed=state.seed, state_sha256=state.sha256,
                  theta=theta, sd=sd, fit_rate=float(np.mean(fit >= theta)), check_rate=check_rate, calibrated=ok,
                  n_fit=len(fit), n_check=len(check), n_behaviour_oracle=len(real),
                  oracle_zero_share=float(np.mean(real == 0)), oracle_min=float(real.min()),
                  oracle_median=float(np.median(real)), oracle_max=float(real.max()),
                  oracle_plan_evaluations=oracle.n_evals, elapsed_seconds=time.monotonic() - started)
    dump(path, result)
    print(f"{task} calibration={index} check={check_rate:.4f} calibrated={int(ok)} "
          f"seconds={result['elapsed_seconds']:.2f}", flush=True)
    return result


def residual_pool(task, index, cal, grader):
    """Grader returns on the N_POOL pool plans: residuals, flip-rate verdicts, false rejection."""
    folder = RESULTS / task
    path = folder / f"pool-{index:02d}.json"
    if path.exists():
        return json.loads(path.read_text())
    state = td.StartState.load(cal["state"])
    with np.load(folder / f"behaviour-{index:02d}.npz") as d:
        plans, real = d["plans"][N_FIT + N_CHECK:], d["oracle_returns"][N_FIT + N_CHECK:]
    before = grader.n_evals
    imagined = grader.returns(state, plans)
    theta, sd = cal["theta"], cal["sd"]
    residuals = (imagined - theta) / sd - (real - theta) / sd
    np.savez_compressed(folder / f"pool-{index:02d}.npz", grader_returns=imagined, oracle_returns=real, residuals=residuals)
    result = dict(instance=index, residual_pool_size=len(residuals),
                  behaviour_grader_p=(imagined >= theta).astype(int).tolist(),
                  behaviour_oracle_accept=(real >= theta).tolist(),
                  grader_plan_evaluations=grader.n_evals - before,
                  residual_median=float(np.median(residuals)),
                  residual_q25=float(np.quantile(residuals, 0.25)), residual_q75=float(np.quantile(residuals, 0.75)),
                  spearman_imagined_real=float(_spearman(imagined, real)))
    dump(path, result)
    return result


def _spearman(x, y):
    from scipy.stats import spearmanr
    return spearmanr(x, y)[0]


def run_instance(task, task_index, index, cal, pooled, grader, pool, workers, attacker_seeds, flip_rates):
    folder = RESULTS / task
    saved = folder / f"instance-{index:02d}.json"
    if saved.exists():
        result = json.loads(saved.read_text())
        if len(result["native_records"]) != attacker_seeds or result.get("flip_rates") != list(flip_rates):
            raise ValueError("resume configuration differs from saved run")
        print(f"{task} instance={index} resume=complete", flush=True)
        return result
    started = time.monotonic()
    state = td.StartState.load(cal["state"])
    dim = state.prefix.shape[1]
    theta, sd = cal["theta"], cal["sd"]
    with np.load(folder / f"behaviour-{index:02d}.npz") as d:
        behaviour = d["plans"]
    with np.load(folder / f"pool-{index:02d}.npz") as d:
        residuals = d["residuals"]
    oracle = td.Oracle(state, pool, workers)
    before_g = grader.n_evals
    space = td.plan_space(dim)
    init = hd.fit_marginals(space, behaviour[:N_FIT])
    fp, fn = flip_rates
    records, logs, selected = [], [], []
    cache = hd.OracleCache(lambda x: (oracle(x) - theta) / sd)
    for attack_seed in range(attacker_seeds):
        proposals = td.behaviour_plans(seed_rng(task_index, index, 1, attack_seed), max(BUDGETS), dim)
        for attacker, scoring in ATTACKS:
            for budget in BUDGETS:
                key = (attacker, scoring)

                def attack(score):
                    if attacker == "cem":
                        return hd.cem(score, space, budget, attack_rng(task_index, index, "cem", key, budget, attack_seed), init=init)
                    return hd.random_shooting(score, proposals, budget)

                tie_rng = attack_rng(task_index, index, "tie", key, budget, attack_seed)

                def score(x):
                    m = grader.margins(state, x, theta, sd, k=2).mean(1)
                    return (m >= 0).astype(float) + tie_rng.uniform(0, 1e-6, len(m)) if scoring == "verdict" else m

                plan, log = attack(score)
                selected.append(plan)
                fresh = grader.margins(state, plan[None], theta, sd, k=8)[0]
                m = float((oracle(plan[None])[0] - theta) / sd)
                row = dict(instance=index, cluster=index, attacker=attacker, scoring=scoring,
                           budget=log["n_scored"], n_scored=log["n_scored"], attacker_seed=attack_seed,
                           plan_id=hashlib.sha256(plan.astype(np.int16).tobytes()).hexdigest(),
                           grader_p=float(np.mean(fresh >= 0)), oracle_accept=m >= 0,
                           grader_score=float(np.mean(fresh)), oracle_margin=m)
                floor_evals, floor_logs = 0, {}
                for nm, surrogate in (("flip", hd.FlipSurrogate(fp, fn)), ("residual", hd.ResidualSurrogate(residuals))):
                    floor = hd.attack_surrogate(attack, surrogate, cache,
                                                attack_rng(task_index, index, nm, key, budget, attack_seed),
                                                memo=False, budget=budget)
                    row[nm + "_grader_accept"] = floor.surrogate_accept
                    row[nm + "_oracle_accept"] = floor.oracle_accept
                    floor_evals += floor.log["n_oracle_evals"]
                    floor_logs[nm] = floor.log
                    np.save(folder / f"floor-{index:02d}-{attack_seed}-{attacker}-{scoring}-{budget}-{nm}.npy",
                            floor.plan.astype(np.int16))
                row["n_floor_oracle_evals"] = floor_evals
                records.append(row)
                logs.append(dict(attacker=attacker, scoring=scoring, seed=attack_seed, search=log, floors=floor_logs))
    # TD-MPC2's own planner. Its budget label is the counted number of latent rollouts it scored
    # (horizon-3 rollouts with a terminal Q), not a 50-step plan count. It has no score callback
    # over 50-step plans, so the surrogate noise floors cannot be run against it.
    native_records, native_logs, native_plans = [], [], []
    for attack_seed in range(attacker_seeds):
        plan, log = grader.native_plan(state, 19000 + task_index * 1000 + index * 10 + attack_seed)
        native_plans.append(plan)
        fresh = grader.margins(state, plan[None], theta, sd, k=8)[0]
        real_m = float((oracle(plan[None])[0] - theta) / sd)
        rollouts = int(log["native_trajectories_scored"])
        native_records.append(dict(instance=index, cluster=index, attacker="tdmpc2_mppi", scoring="margin",
                                   budget=rollouts, n_scored=rollouts, attacker_seed=attack_seed,
                                   plan_id=hashlib.sha256(plan.astype(np.int16).tobytes()).hexdigest(),
                                   grader_p=float(np.mean(fresh >= 0)), oracle_accept=real_m >= 0,
                                   grader_score=float(np.mean(fresh)), oracle_margin=real_m))
        native_logs.append(log)
    np.savez_compressed(folder / f"selected-{index:02d}.npz", plans=np.asarray(selected), native_plans=np.asarray(native_plans))
    result = dict(cal)
    result.update(residual_pool_size=pooled["residual_pool_size"], records=records, native_records=native_records,
                  logs=logs, native_logs=native_logs, flip_rates=list(flip_rates),
                  grader_plan_evaluations_pool=pooled["grader_plan_evaluations"],
                  grader_plan_evaluations_attacks=grader.n_evals - before_g,
                  oracle_plan_evaluations_attacks=oracle.n_evals,
                  floor_oracle_unique_evaluations=cache.n_evals,
                  elapsed_seconds_attacks=time.monotonic() - started)
    dump(saved, result)
    print(f"{task} instance={index} grader={result['grader_plan_evaluations_pool'] + result['grader_plan_evaluations_attacks']} "
          f"oracle={cal['oracle_plan_evaluations'] + oracle.n_evals} seconds={result['elapsed_seconds_attacks']:.2f}", flush=True)
    return result


def audit(args):
    check_path = RESULTS / "determinism/check.json"
    if not check_path.exists():
        raise RuntimeError("run the oracle determinism check first")
    check = json.loads(check_path.read_text())
    if check["tolerance"] != 0:
        raise RuntimeError("nonzero oracle tolerance needs an explicit analysis before auditing")
    with mp.get_context("spawn").Pool(args.workers) as pool:
        for task in args.tasks:
            ti = td.TASKS.index(task)
            cals = [calibrate(task, ti, i, pool, args.workers) for i in range(args.instances)]
            failed = [c["instance"] for c in cals if not c["calibrated"]]
            if failed:
                dump(RESULTS / task / "excluded.json", dict(task=task, reason="behaviour-plan oracle acceptance outside "
                     f"{list(ACCEPT_RANGE)} at {len(failed)} of {len(cals)} starts", failed_starts=failed))
                print(f"{task} excluded: {len(failed)}/{len(cals)} starts fail calibration", flush=True)
                continue
            st = td.StartState.load(cals[0]["state"])
            grader = td.Grader(task, td.EXT_ROOT / "checkpoints" / f"{task}-1.pt", len(st.obs), st.prefix.shape[1])
            pooled = [residual_pool(task, i, cals[i], grader) for i in range(args.instances)]
            bp = np.asarray([p for x in pooled for p in x["behaviour_grader_p"]], dtype=bool)
            bo = np.asarray([o for x in pooled for o in x["behaviour_oracle_accept"]], dtype=bool)
            flip_rates = float(np.mean(bp[~bo])), float(np.mean(~bp[bo]))
            for i in range(args.instances):
                run_instance(task, ti, i, cals[i], pooled[i], grader, pool, args.workers, args.attacker_seeds, flip_rates)
            del grader
            import torch
            torch.cuda.empty_cache()
    report(args.tasks)


# ------------------------------------------------------------------------------------------------
# report


def fmt(e):
    if not e or e.get("value") is None:
        return "NA"
    v = e["value"]
    if e.get("method") == hd.stats.ZERO_BOUND_METHOD:
        return f"{v:.3f} [0, {e['hi']:.3f}]e"
    lo, hi = e.get("bca_lo"), e.get("bca_hi")
    if lo is None or hi is None or not np.isfinite(lo + hi):
        lo, hi = e.get("lo"), e.get("hi")
    if lo is None or hi is None or not np.isfinite(lo + hi):
        return f"{v:.3f} [NA, NA]"
    return f"{v:.3f} [{lo:.3f}, {hi:.3f}]"


def key(row):
    return row["attacker"], row["scoring"], row["budget"]


def licence_line(path):
    lines = [line.strip() for line in Path(path).read_text().splitlines() if line.strip()]
    name = lines[0] + (" " + lines[1] if lines[1].startswith("Version") else "")
    return f"{name} (`{Path(path).name}`, sha256 `{sha(path)}`)"


def report(tasks):
    provenance = json.loads((td.EXT_ROOT / "provenance.json").read_text())
    code_version = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    td_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=td.EXT_ROOT / "tdmpc2", text=True).strip()
    det = (RESULTS / "determinism/output.txt").read_text() if (RESULTS / "determinism/output.txt").exists() else "not run"
    summary = [
        "# TD-MPC2 external check", "",
        "Grader: the released TD-MPC2 single-task checkpoint's own encoder, latent dynamics and reward head, loaded "
        "by the authors' code; the imagined return is the sum of 50 predicted rewards along the latent rollout from "
        "the encoded start observation. Oracle: the same 50 actions, each repeated twice (the authors' action repeat), "
        "executed in dm_control from the exactly restored start state; the real return is the sum of the 100 "
        "simulator rewards. Neither is discounted and neither has a terminal value. Margin = (return - theta) / sd.", "",
        f"Behaviour plans: {td.BEHAVIOUR}.", "",
        f"Start states: seed 1000 + i, environment reset, then 12 uniform random actions on the 21-level grid, each "
        f"repeated twice; saved (physics state, MuJoCo integration state, observation, step count) and restored "
        f"exactly. Bootstrap cluster = start state. Theta = the {THETA_QUANTILE} quantile of {N_FIT} behaviour-plan "
        f"oracle returns, checked on {N_CHECK} more (acceptance must lie in {list(ACCEPT_RANGE)}); sd = sample sd of "
        f"those {N_FIT + N_CHECK} returns. A further {N_POOL} behaviour plans per start give the residual pool, the "
        "flip rates (pooled within task) and false rejection.", "",
        "The grader is deterministic (no sampling in the encoder, dynamics or reward head; evaluation mode): K = 2 "
        "and K = 8 samples are copies of one evaluation, so success probabilities are 0 or 1. Each plan's imagined "
        "return is computed in a fixed-shape batch, so it does not depend on the other plans scored with it.", "",
        "Intervals: 95 per cent cluster bootstrap over start states, 2,000 resamples, BCa limits; `e` marks a row "
        "with no hacked unit, whose interval is the instrument's exact one-sided cluster bound. B is the counted "
        "number of plans the attacker scored (for MPPI: the counted latent rollouts). Floors: the residual surrogate "
        "is matched to margin-scored attackers, the flip surrogate (and for random shooting its closed form) to "
        "verdict-scored selection; `*` marks the matched floor.", "",
        "## Oracle determinism (verbatim)", "", "```", det.rstrip(), "```", ""]
    audited = []
    for task in tasks:
        folder = RESULTS / task
        excluded = folder / "excluded.json"
        cals = [json.loads(p.read_text()) for p in sorted(folder.glob("calibration-*.json"))]
        checkpoint = next(c for c in provenance["checkpoints"] if c["task"] == task)
        if excluded.exists():
            ex = json.loads(excluded.read_text())
            summary += [f"## {task}: not audited", "",
                        f"Checkpoint `{checkpoint['file']}` (sha256 `{checkpoint['sha256']}`). "
                        f"{ex['reason'][0].upper() + ex['reason'][1:]}. "
                        f"Starts at which every one of the {cals[0]['n_behaviour_oracle']:,} behaviour-plan returns is "
                        f"exactly 0: {sum(c['oracle_max'] == 0 and c['oracle_min'] == 0 for c in cals)} of {len(cals)}. "
                        f"Across the {len(cals)} starts: share of "
                        f"returns exactly 0 per start {min(c['oracle_zero_share'] for c in cals):.4f} to "
                        f"{max(c['oracle_zero_share'] for c in cals):.4f}; largest return "
                        f"{max(c['oracle_max'] for c in cals):.6g}; checked acceptance at theta = the "
                        f"{THETA_QUANTILE} quantile {min(c['check_rate'] for c in cals):.4f} to "
                        f"{max(c['check_rate'] for c in cals):.4f}. No grader, attack or card is produced for it.", ""]
            continue
        instances = [json.loads(p.read_text()) for p in sorted(folder.glob("instance-*.json"))]
        if not instances:
            continue
        audited.append(task)
        pools = [json.loads(p.read_text()) for p in sorted(folder.glob("pool-*.json"))]
        main = [r for x in instances for r in x["records"]]
        native = [r for x in instances for r in x["native_records"]]
        common = [{k: v for k, v in r.items() if not k.startswith(("flip_", "residual_", "n_floor_"))} for r in main] + native
        beh = [dict(instance=x["instance"], cluster=x["instance"], grader_p=p, oracle_accept=o)
               for x in pools for p, o in zip(x["behaviour_grader_p"], x["behaviour_oracle_accept"])]
        nl = [l for x in instances for l in x["native_logs"]]
        settings = {k: sorted({l[k] for l in nl}) for k in ("native_horizon", "native_iterations", "native_num_samples",
                    "native_num_elites", "native_num_pi_trajs", "native_temperature", "native_min_std",
                    "native_max_std", "native_discount", "native_eval_mode", "native_trajectories_scored")}
        meta = dict(audited=f"TD-MPC2 {task} released single-task checkpoint {checkpoint['file']}",
                    code_version=code_version, date=date.today().isoformat(),
                    revisit_date=(date.today() + timedelta(days=180)).isoformat(),
                    tdmpc2_commit=td_commit, huggingface_revision=provenance["huggingface_revision"],
                    checkpoint=checkpoint, horizon=td.HORIZON, action_repeat=td.ACTION_REPEAT,
                    behaviour=td.BEHAVIOUR, deterministic_grader=True,
                    native_planner="authors' MPPI (_plan, eval_mode=True) called at 50 successive imagined latents; "
                                   "each selected action quantised to the grid before advancing the latent",
                    native_planner_settings=settings,
                    source_sha256={str(p.relative_to(ROOT)): sha(p) for p in
                                   [Path(__file__), ROOT / "hpr-dream/hpr_dream/adaptors/tdmpc2.py"]})
        card = hd.build_card(table(common), meta, behaviour=table(beh), grader_k=8, bca=True, seed=8421)
        floors = hd.build_card(table(main), meta, behaviour=table(beh), grader_k=8, bca=True, seed=8421)
        floor_map = {key(r): r for r in floors["noise_floors"]}
        card["noise_floors"] = [floor_map.get(key(r), r) for r in card["noise_floors"]]
        n_mppi_runs = len(native)
        ex = dict(
            grader_50step_plans_total=sum(x["grader_plan_evaluations_pool"] + x["grader_plan_evaluations_attacks"] for x in instances),
            grader_50step_plans_residual_pool=sum(x["grader_plan_evaluations_pool"] for x in instances),
            grader_50step_plans_attack_search=sum(r["n_scored"] for r in main),
            grader_50step_plans_selected_rescored=len(main) + n_mppi_runs,
            mppi_runs=n_mppi_runs,
            mppi_latent_rollouts=sum(l["native_trajectories_scored"] for l in nl),
            mppi_dynamics_transitions_in_rollouts=sum(l["native_dynamics_transitions"] for l in nl),
            mppi_policy_proposal_transitions=sum(l["native_policy_proposal_transitions"] for l in nl),
            oracle_plans_total=sum(x["oracle_plan_evaluations"] + x["oracle_plan_evaluations_attacks"] for x in instances),
            oracle_plans_calibration=sum(x["n_fit"] + x["n_check"] for x in instances),
            oracle_plans_residual_pool=sum(x["n_behaviour_oracle"] - x["n_fit"] - x["n_check"] for x in instances),
            oracle_plans_selected=len(main) + n_mppi_runs,
            oracle_plans_noise_floors_unique=sum(x["floor_oracle_unique_evaluations"] for x in instances))
        assert ex["grader_50step_plans_total"] == (ex["grader_50step_plans_residual_pool"] + ex["grader_50step_plans_attack_search"]
                                                   + ex["grader_50step_plans_selected_rescored"])
        assert ex["oracle_plans_total"] == (ex["oracle_plans_calibration"] + ex["oracle_plans_residual_pool"]
                                            + ex["oracle_plans_selected"] + ex["oracle_plans_noise_floors_unique"])
        card["execution_counts"] = ex
        card["counts"]["oracle_plan_evaluations"]["noise_floor_attacks"] = ex["oracle_plans_noise_floors_unique"]
        card["counts"]["grader_plan_evaluations"]["attack_search"] = ex["grader_50step_plans_attack_search"]
        card["counts"]["grader_plan_evaluations"]["mppi_latent_rollouts"] = ex["mppi_latent_rollouts"]
        card["calibration_instances"] = [{k: x[k] for k in ("instance", "state_seed", "state_sha256", "theta", "sd", "fit_rate",
                                                            "check_rate", "n_fit", "n_check", "residual_pool_size")} for x in instances]
        card["residual_pool_summary"] = [{k: x[k] for k in ("instance", "residual_median", "residual_q25", "residual_q75",
                                                            "spearman_imagined_real")} for x in pools]
        CARDS.mkdir(parents=True, exist_ok=True)
        dump(CARDS / f"{task}.json", card)
        cond = {key(r): r["conditional_reject"] for r in card["conditional_reject"]}
        fl = {key(r): r for r in card["noise_floors"]}
        fr = card["flip_rates"]
        summary += [f"## {task}", "",
                    f"Checkpoint `{checkpoint['file']}` (sha256 `{checkpoint['sha256']}`). Starts {len(instances)}; attacker "
                    f"seeds per start {len(instances[0]['native_records'])}; theta {min(x['theta'] for x in instances):.4f} to "
                    f"{max(x['theta'] for x in instances):.4f}; sd {min(x['sd'] for x in instances):.4f} to "
                    f"{max(x['sd'] for x in instances):.4f}; checked acceptance {min(x['check_rate'] for x in instances):.4f} to "
                    f"{max(x['check_rate'] for x in instances):.4f}.", "",
                    "| Attacker | Scoring | B | Hackability | Residual floor | Excess over residual | Flip floor | "
                    "Excess over flip | Flip closed form | Conditional rejection |",
                    "|---|---|---:|---|---|---|---|---|---|---|"]
        for r in card["hackability_curve"]:
            f = fl[key(r)]
            res, flip = f.get("residual_surrogate", {}), f.get("flip_surrogate", {})
            cf = f.get("flip_closed_form", {})
            star_r = "*" if r["scoring"] == "margin" and "hackability" in res else ""
            star_f = "*" if r["scoring"] == "verdict" and "hackability" in flip else ""
            summary.append(
                f"| {r['attacker']} | {r['scoring']} | {r['budget']:,} | {fmt(r['hackability'])} | "
                f"{fmt(res.get('hackability'))}{star_r} | {fmt(res.get('excess'))} | {fmt(flip.get('hackability'))}{star_f} | "
                f"{fmt(flip.get('excess'))} | {fmt(cf.get('floor')) if 'floor' in cf else 'NA'} | {fmt(cond[key(r)])} |")
        rp = card["residual_pool_summary"]
        summary += ["",
                    f"False rejection on behaviour plans the oracle accepts: {fmt(card['false_rejection']['false_rejection'])} "
                    f"({card['false_rejection']['n_plans']:,} plans). Flip rates on {card['counts']['behaviour_plans']:,} "
                    f"behaviour plans: fp {fmt(fr['fp'])}, fn {fmt(fr['fn'])}, oracle base rate {fmt(fr['base_rate'])}.", "",
                    f"Behaviour-pool residual (grader margin - oracle margin), median over starts of the per-start median "
                    f"{float(np.median([x['residual_median'] for x in rp])):.3f} (range {min(x['residual_median'] for x in rp):.3f} "
                    f"to {max(x['residual_median'] for x in rp):.3f}); Spearman(imagined, real return) per start "
                    f"{min(x['spearman_imagined_real'] for x in rp):.3f} to {max(x['spearman_imagined_real'] for x in rp):.3f} "
                    f"(median {float(np.median([x['spearman_imagined_real'] for x in rp])):.3f}).", "",
                    "MPPI settings read from the run: " + ", ".join(f"{k.replace('native_', '')}={v if len(v) > 1 else v[0]}"
                                                                     for k, v in settings.items()) + ".", "",
                    "Execution counts:", ""]
        summary += [f"- {k}: {v:,}" for k, v in ex.items()] + [""]
    lic = td.EXT_ROOT / "licences"
    summary += ["## Provenance and limits", "",
                f"TD-MPC2 code: github.com/nicklashansen/tdmpc2 at commit `{td_commit}`. Checkpoints: huggingface.co/"
                f"nicklashansen/tdmpc2 at revision `{provenance['huggingface_revision']}`, files and sha256 in each section "
                f"and in wm2-ext/provenance.json. wm2 commit `{code_version}` plus the source hashes in each card.", "",
                f"Licences: TD-MPC2 {licence_line(lic / 'TD-MPC2-LICENSE')}; dm_control {licence_line(lic / 'dm_control-LICENSE')}.", "",
                "MPPI is the authors' planner with its released settings (above), called at 50 successive imagined "
                "latents from the encoded start observation; each selected action is quantised to the 21-level grid and "
                "advances the latent. This open-loop use differs from the authors' closed-loop evaluation, where each call "
                "starts from a new real observation. Its B is the number of horizon-3 latent rollouts (each with a "
                "terminal Q) it scored, counted during the run; its objective is the authors' discounted return plus "
                "terminal Q, not the 50-step audit score, so no noise floor is run against it (NA).", "",
                f"Audited: {', '.join(audited) if audited else 'none'}."]
    text = "\n".join(summary) + "\n"
    (RESULTS / "summary.md").write_text(text)
    print(text, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("determinism", "trace", "audit", "report"))
    parser.add_argument("--tasks", nargs="+", default=list(td.TASKS))
    parser.add_argument("--instances", type=int, default=20)
    parser.add_argument("--attacker-seeds", type=int, default=3)
    parser.add_argument("--workers", type=int, default=7)
    parser.add_argument("--state")
    parser.add_argument("--plan")
    parser.add_argument("--output")
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    if args.command == "trace":
        return trace_worker(args.state, args.plan, args.output)
    if args.command == "determinism":
        return determinism(args.tasks, args.instances)
    if args.command == "report":
        return report(args.tasks)
    if not 1 <= args.workers <= 7:
        raise ValueError("one coordinator plus at most seven oracle workers")
    audit(args)


if __name__ == "__main__":
    main()
