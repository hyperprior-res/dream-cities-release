#!/usr/bin/env python
"""Step-1 diagnostic: can a small network learn the engine's bookkeeping from scalars alone?

    bookkeeping_diag.py build                      # feature cache of train_full and heldout_eval
    bookkeeping_diag.py fit --variant a --samples 200000000 --out results/fidelity/bookkeeping/a

Inputs per transition (all of month t, plus true quantities of month t+1 that the next map carries):
* this month's 20 scalars and 27 ledger entries; the action scalars (11); the listed price per tool
  channel (calls x engine unit cost, from the plan's macro geometry) and its total; month of year;
* next-map census (true): res/com/ind pop, pop, powered and unpowered zones, coal and nuclear plants,
  road total (the scalars at t+1 that are read off the map); next overlays' averages (land value over
  cells > 0, pollution over cells > 0, crime over cells with land value > 0, traffic over cells > 0,
  population density over cells > 0, and the number of cells with land value > 0); next tiles' counts of
  fire-station, police-station, hospital, church, stadium, seaport and airport centres and of fire tiles,
  and the zone tiles' centre of mass; and the month's charged build cost (what the second stage sees as
  the map change inside the action footprint, priced).
Targets: next month's valves, score, funds, tax fund, three spends, and the 24 learned ledger entries, as
the one-month change scaled per entry by the standard deviation of its change.
Variants: (a) residual MLP on symmetric-log and linearly scaled inputs; (b) (a) plus a learned copy
pathway (per target a softmax over current entries and next-map quantities and a gate, exact once
sharp); (c) (b) plus product units (exp of a learned linear map of log inputs), so ratios and products
are linear for the network. Loss: L1 on the scaled change (median prediction). Metric: mean absolute
error of the rounded prediction, per entry, as a ratio to copy-last-state, on all heldout_eval
transitions and on the 2,000 held-out transitions of the fidelity evaluation, beside the engine floor.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from multiprocessing import get_context
from pathlib import Path
from typing import Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

CACHE = Path("<cache>/ckpt/bookkeeping_cache")
CENTRES = {1: [765], 2: [774], 3: [409], 4: [418] + [960 + 9 * k for k in range(7)], 5: [784, 800], 6: [698], 7: [716]}
COUNT_NAMES = ["fire_stations", "police_stations", "hospitals", "churches", "stadiums", "seaports", "airports", "fire_tiles"]
CENSUS_NEXT = ["res_pop", "com_pop", "ind_pop", "pop", "powered_zones", "unpowered_zones", "coal_plants", "nuclear_plants", "road_total"]
OVERLAY_NAMES = ["lv_avg", "poll_avg", "crime_avg", "traffic_avg", "popden_avg", "lv_cells"]
SC_TARGETS = ["res_valve", "com_valve", "ind_valve", "score", "funds", "tax_fund", "road_spend", "fire_spend", "police_spend"]


def _lut():
    lut = np.zeros(1024, dtype=np.int64)
    for c, codes in CENTRES.items():
        lut[codes] = c
    lut[56:64] = 8
    return lut


_ST = None


def _init(path):
    global _ST
    from dc import data
    _ST = data.TrajStore(path)


def _chunk(args):
    """Next-map features for the observation rows ``rows`` (sorted)."""
    rows = args
    from dc.engine import ZONEBIT
    st = _ST
    lo, hi = int(rows[0]), int(rows[-1]) + 1
    tiles = np.asarray(st.tiles[lo:hi]).view(np.uint16)[rows - lo]
    half = np.asarray(st.half[lo:hi])[rows - lo].astype(np.float64)
    n = len(rows)
    codes = (tiles & 0x3FF).astype(np.int64)
    zone = (tiles & ZONEBIT) > 0
    cat = _lut()[codes]
    cat = np.where((cat >= 1) & (cat <= 7) & ~zone, 0, cat)
    rr = np.broadcast_to(np.arange(n)[:, None, None], cat.shape)
    nz = cat > 0
    cnt = np.bincount(rr[nz] * 9 + cat[nz], minlength=n * 9).reshape(n, 9)[:, 1:]
    zc = zone.sum(axis=(1, 2)).astype(np.float64)
    cx = (zone.sum(axis=2) * np.arange(zone.shape[1])).sum(axis=1) / np.maximum(zc, 1)
    cy = (zone.sum(axis=1) * np.arange(zone.shape[2])).sum(axis=1) / np.maximum(zc, 1)
    pd, tr, po, lv, cr = (half[:, i] for i in range(5))

    def avg(v, m):
        k = m.sum(axis=(1, 2))
        return np.where(k > 0, (v * m).sum(axis=(1, 2)) / np.maximum(k, 1), 0.0)

    ov = np.stack([avg(lv, lv > 0), avg(po, po > 0), avg(cr, lv > 0), avg(tr, tr > 0), avg(pd, pd > 0),
                   (lv > 0).sum(axis=(1, 2)).astype(np.float64)], axis=1)
    return np.concatenate([cnt.astype(np.float64), cx[:, None], cy[:, None], ov], axis=1)


def listed_price(plan: np.ndarray) -> np.ndarray:
    from dc import grammar
    r = grammar.clip_plan(plan.astype(np.int64))
    ch, _, _, _, _, n, tool = grammar._macro_geometry(r)
    cost = np.where(tool >= 0, grammar._KIND_COST[r[:, 5::5].astype(np.int64)], 0) * n
    out = np.zeros((plan.shape[0], 15), dtype=np.float64)
    ok = (ch >= 0) & (n > 0)
    np.add.at(out, (np.broadcast_to(np.arange(plan.shape[0])[:, None], ch.shape)[ok], ch[ok]), cost[ok])
    return out


def build(split: str, workers: int) -> None:
    from dc import data, grammar
    st, idx = data.open_split(split)
    k = np.arange(st.n_trans, dtype=np.int64)
    r = st.obs_row_of(k)
    t0 = time.time()
    sc0, sc1 = np.asarray(st.scalars[:]), None
    sc1 = sc0[r + 1]
    sc0 = sc0[r]
    lg = np.asarray(st.ledger[:])
    lg0, lg1 = lg[r], lg[r + 1]
    plan = np.asarray(st.plan[:])
    act = grammar.action_scalars_batch(plan).astype(np.float32)
    price = listed_price(plan)
    cost = np.asarray(st.build_cost[:]).astype(np.float64)
    rows1 = r + 1
    chunks = [rows1[a:a + 20000] for a in range(0, len(rows1), 20000)]
    with get_context("spawn").Pool(workers, initializer=_init, initargs=(str(st.path),)) as pool:
        nxt = np.concatenate(pool.map(_chunk, chunks))
    traj = st.traj_of(k)
    month = st.month_of(k)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(CACHE / f"{split}.npz", sc0=sc0, sc1=sc1, lg0=lg0, lg1=lg1, act=act, price=price, cost=cost, nxt=nxt,
             traj=traj, month=month)
    print(f"{split}: {len(k)} transitions, built in {time.time() - t0:.0f}s -> {CACHE / (split + '.npz')}", flush=True)


# ----------------------------------------------------------------------------------------------
def load(split: str):
    from dc.engine import LG, LEDGER_NAMES, SCALAR_NAMES
    from dc.model import LEARNED_LEDGER, month_features
    import torch
    z = np.load(CACHE / f"{split}.npz")
    SN = {n: i for i, n in enumerate(SCALAR_NAMES)}
    census = z["sc1"][:, [SN[n] for n in CENSUS_NEXT]]
    raw = np.concatenate([z["sc0"], z["lg0"], census, z["nxt"], z["cost"][:, None], z["price"],
                          z["price"].sum(1, keepdims=True)], axis=1).astype(np.float64)
    raw_names = (["cur_" + n for n in SCALAR_NAMES] + ["cur_" + n for n in LEDGER_NAMES] + ["next_" + n for n in CENSUS_NEXT]
                 + ["next_" + n for n in COUNT_NAMES + ["zone_cx", "zone_cy"] + OVERLAY_NAMES] + ["charged_cost"]
                 + [f"price_{c}" for c in range(15)] + ["price_total"])
    tgt_idx_sc = [SN[n] for n in SC_TARGETS]
    cur_t = np.concatenate([z["sc0"][:, tgt_idx_sc], z["lg0"][:, list(LEARNED_LEDGER)]], axis=1).astype(np.float64)
    nxt_t = np.concatenate([z["sc1"][:, tgt_idx_sc], z["lg1"][:, list(LEARNED_LEDGER)]], axis=1).astype(np.float64)
    tgt_names = SC_TARGETS + [LEDGER_NAMES[i] for i in LEARNED_LEDGER]
    mf = month_features(torch.from_numpy(z["sc0"][:, SN["city_time"]].astype(np.float64))).numpy()
    return {"raw": raw, "raw_names": raw_names, "act": z["act"].astype(np.float64), "month": mf, "cur": cur_t,
            "nxt": nxt_t, "tgt_names": tgt_names, "traj": z["traj"], "tmonth": z["month"]}


def symlog(x):
    return np.sign(x) * np.log1p(np.abs(x))


def fit(args) -> None:
    import torch
    import torch.nn as nn
    torch.manual_seed(args.seed)
    dev = torch.device("cuda")
    tr, he = load("train_full"), load("heldout_eval")
    # input normalisation from train
    sl = symlog(tr["raw"])
    mu_l, sd_l = sl.mean(0), sl.std(0) + 1e-6
    mu_r, sd_r = tr["raw"].mean(0), tr["raw"].std(0) + 1e-6
    d_tr = tr["nxt"] - tr["cur"]
    scale = np.maximum(d_tr.std(0), 1.0)

    drop = [i for i, n in enumerate(tr["raw_names"]) if any(n.startswith(p) for p in args.drop.split(",") if p)]

    def feats(d):
        f = np.concatenate([(symlog(d["raw"]) - mu_l) / sd_l, np.clip((d["raw"] - mu_r) / sd_r, -50, 50)], 1)
        if drop:      # ablation: the dropped raw inputs carry no information (both encodings zeroed)
            nr = d["raw"].shape[1]
            f[:, drop] = 0.0
            f[:, [nr + i for i in drop]] = 0.0
        return np.concatenate([f, d["act"], d["month"]], 1)

    X = torch.tensor(feats(tr), dtype=torch.float32, device=dev)
    Y = torch.tensor(d_tr / scale, dtype=torch.float32, device=dev)
    Xh = torch.tensor(feats(he), dtype=torch.float32, device=dev)
    Rtr = torch.tensor(tr["raw"], dtype=torch.float64, device=dev)
    Rhe = torch.tensor(he["raw"], dtype=torch.float64, device=dev)
    Ctr = torch.tensor(tr["cur"], dtype=torch.float64, device=dev)
    Che = torch.tensor(he["cur"], dtype=torch.float64, device=dev)
    S = torch.tensor(scale, dtype=torch.float64, device=dev)
    nT, nI, nR = Y.shape[1], X.shape[1], Rtr.shape[1]

    class Res(nn.Module):
        def __init__(self, w):
            super().__init__()
            self.n = nn.LayerNorm(w)
            self.f = nn.Sequential(nn.Linear(w, 2 * w), nn.GELU(), nn.Linear(2 * w, w))

        def forward(self, x):
            return x + self.f(self.n(x))

    class Net(nn.Module):
        def __init__(self, variant):
            super().__init__()
            self.variant = variant
            w = args.width
            extra = 0
            if variant == "c":
                self.prod = nn.Linear(nR, args.n_prod)          # exponents on log(|raw| + 1)
                nn.init.normal_(self.prod.weight, std=0.05)
                nn.init.zeros_(self.prod.bias)
                extra = args.n_prod
            self.inp = nn.Linear(nI + extra, w)
            self.blocks = nn.Sequential(*[Res(w) for _ in range(args.depth)])
            self.out = nn.Sequential(nn.LayerNorm(w), nn.Linear(w, nT))
            if variant in ("b", "c"):
                # copy pathway over the raw sources (current entries, next-map quantities, cost, prices)
                self.sel = nn.Linear(w, nT * (nR + 1))           # per-sample selection logits (+ "keep")
                nn.init.zeros_(self.sel.weight)
                with torch.no_grad():
                    self.sel.bias.zero_()
                    self.sel.bias.view(nT, nR + 1)[:, -1] = 4.0   # start at "keep current"

        def forward(self, x, raw, cur):
            if self.variant == "c":
                lp = torch.log1p(raw.abs().float()).clamp(max=20)
                pu = torch.exp(self.prod(lp).clamp(-20, 20))
                x = torch.cat([x, torch.log1p(pu)], dim=1)
            h = self.blocks(self.inp(x))
            d = self.out(h).double()                             # scaled change
            if self.variant in ("b", "c"):
                logits = self.sel(h).view(-1, nT, nR + 1).double()
                p = torch.softmax(logits, dim=-1)
                src = torch.cat([raw.unsqueeze(1).expand(-1, nT, -1), cur.unsqueeze(-1)], dim=-1)   # (B, nT, nR+1)
                copy = (p * src).sum(-1)                         # raw next value by selection
                d = d + (copy - cur) / S                         # added to the change, in scaled units
            return d

    net = Net(args.variant).to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=args.lr, weight_decay=0.0)
    steps = args.samples // args.batch
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=args.lr, total_steps=steps, pct_start=0.02, final_div_factor=100)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    # matched 2,000 held-out transitions of the fidelity evaluation, and the engine floor on them
    from dc import data, fidelity as fd
    st, _ = data.open_split("heldout_eval")
    trajs = fd.trajectories_from_store(st, st.traj_ids().tolist())
    pairs = fd.pick_transitions(trajs, 2000, 20261109)
    first = st.traj["first_trans"].astype(np.int64)
    sel2k = torch.tensor([first[trajs[i].traj_id] + t for i, t in pairs], device=dev)
    floor = json.loads((ROOT / "results/fidelity/pilot4_ledger/floor_onestep.json").read_text())
    floor_mae = {**floor["scalar_mae_1m"], **floor.get("ledger_mae_1m", {})}
    checkpoints = sorted(set(int(x) for x in args.eval_at.split(",")) | {steps * args.batch})
    reports = []

    def evaluate(samples_done):
        net.eval()
        with torch.no_grad():
            preds = []
            for a in range(0, Xh.shape[0], 65536):
                sl_ = slice(a, a + 65536)
                preds.append(net(Xh[sl_], Rhe[sl_], Che[sl_]))
            dpred = torch.cat(preds) * S
            nxt_pred = torch.round(Che + dpred)
            true = torch.tensor(he["nxt"], device=dev)
            e_m = (nxt_pred - true).abs()
            e_c = (Che - true).abs()
        net.train()
        rep = {"samples": samples_done, "entries": {}}
        for j, n in enumerate(he["tgt_names"]):
            m_all, c_all = float(e_m[:, j].mean()), float(e_c[:, j].mean())
            m2, c2 = float(e_m[sel2k, j].mean()), float(e_c[sel2k, j].mean())
            f2 = floor_mae.get(n)
            rep["entries"][n] = {"model_all": m_all, "copy_all": c_all, "ratio_all": m_all / c_all if c_all > 0 else float("nan"),
                                 "model_2k": m2, "copy_2k": c2, "ratio_2k": m2 / c2 if c2 > 0 else float("nan"),
                                 "floor_2k": f2, "floor_ratio_2k": (f2 / c2) if (f2 is not None and c2 > 0) else float("nan"),
                                 "exact_share_all": float((e_m[:, j] == 0).float().mean())}
        reports.append(rep)
        key = ["res_valve", "com_valve", "ind_valve", "score", "res_hist1", "com_hist0", "funds", "tax_fund", "road_fund"]
        print(f"[{args.variant}] {samples_done:>11,} samples: " + "  ".join(
            f"{n} {rep['entries'][n]['ratio_all']:.3f}" for n in key if n in rep["entries"]), flush=True)

    n_tr = X.shape[0]
    g = torch.Generator(device=dev).manual_seed(args.seed)
    t0 = time.time()
    done = 0
    ci = 0
    for step in range(steps):
        ix = torch.randint(n_tr, (args.batch,), device=dev, generator=g)
        pred = net(X[ix], Rtr[ix], Ctr[ix])
        loss = (pred - Y[ix].double()).abs().mean()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step()
        sched.step()
        done += args.batch
        while ci < len(checkpoints) and done >= checkpoints[ci]:
            evaluate(done)
            ci += 1
    res = {"variant": args.variant, "args": vars(args), "dropped_inputs": [tr["raw_names"][i] for i in drop], "train_transitions": int(n_tr), "heldout_transitions": int(Xh.shape[0]),
           "inputs": tr["raw_names"] + ["act_" + str(i) for i in range(11)] + ["month_" + str(i) for i in range(18)],
           "targets": tr["tgt_names"], "change_scale": dict(zip(tr["tgt_names"], scale.tolist())),
           "params": sum(p.numel() for p in net.parameters()), "seconds": time.time() - t0, "reports": reports}
    (out / "result.json").write_text(json.dumps(res, indent=1))
    (out / "table.md").write_text(render_table(res))
    print("wrote", out / "table.md", flush=True)


def render_table(res: dict, free: Optional[dict] = None, free_label: str = "") -> str:
    """table.md from a fit's result.json. Every ratio of the fit is teacher-forced: the scalars-only
    network is given the engine's true next census, next-map summary and charged build cost. ``free``:
    an evaluation JSON of the full emulator (eval_fidelity.py) on the same 2,000 transitions, whose
    one-month T=1 sample feeds the third stage the model's own sampled census, map summary and cost
    (free-running), added as a column beside the teacher-forced ratio on those transitions."""
    reports = res["reports"]
    L = [f"# Bookkeeping diagnostic, variant {res['variant']}", "",
         "**Teacher-forced.** Every ratio below" + (" except the free-running column" if free is not None else "") +
         " is the scalars-only network given the engine's true next census, next-map summary and charged build cost; "
         "in the emulator's rollouts the third stage is fed the model's own sampled ones instead.", "",
         f"train: {res['train_transitions']:,} train_full transitions; held-out: {res['heldout_transitions']:,} heldout_eval "
         "transitions (and the 2,000 of the development selection, with the engine re-seeded at month t). "
         f"Parameters {res['params']:,}; {res['seconds']:.0f} s on GPU.", "",
         "Mean absolute error of the rounded one-month prediction as a ratio to copy-last-state (all held-out transitions;"
         " the 2,000-transition ratio and the engine's ratio on the same 2,000 beside it).", ""]
    if free is not None:
        L += [f"Free-running column: {free_label}: the full emulator's one-month sample (T=1, decoding "
              f"{free.get('decoding', {}).get('name')}) on the same 2,000 transitions, its census, map and cost sampled "
              "by the model, as a ratio to copy-last-state.", ""]
    head = "| entry | " + " | ".join(f"{r['samples']:,}" for r in reports) + " | final, 2,000 | engine other seed, 2,000 | final exact share |"
    L += [head + (" free-running T=1, 2,000 |" if free is not None else ""),
          "|---|" + "---|" * (len(reports) + 3 + (1 if free is not None else 0))]
    for n in res["targets"]:
        cells = [f"{r['entries'][n]['ratio_all']:.3f}" for r in reports]
        e = reports[-1]["entries"][n]
        row = f"| {n} | " + " | ".join(cells) + f" | {e['ratio_2k']:.3f} | {e['floor_ratio_2k']:.3f} | {e['exact_share_all']:.3f} |"
        if free is not None:
            on = free["onestep"]
            v = on["scalar_mae_1m"].get(n) or on.get("ledger_mae_1m", {}).get(n)
            row += f" {v['T1'] / v['copy']:.3f} |" if v and v["copy"] > 0 else " n/a |"
        L.append(row)
    return "\n".join(L) + "\n"


def table(args) -> None:
    out = Path(args.out)
    res = json.loads((out / "result.json").read_text())
    free = json.loads(Path(args.free_json).read_text()) if args.free_json else None
    (out / "table.md").write_text(render_table(res, free, args.free_label))
    print("wrote", out / "table.md", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["build", "fit", "table"])
    ap.add_argument("--free-json", default="", help="table: evaluation JSON of the full emulator (free-running column)")
    ap.add_argument("--free-label", default="", help="table: label of the free-running column's checkpoint")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--variant", default="a", choices=["a", "b", "c"])
    ap.add_argument("--samples", type=int, default=200_000_000)
    ap.add_argument("--batch", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--width", type=int, default=512)
    ap.add_argument("--depth", type=int, default=4)
    ap.add_argument("--n-prod", type=int, default=64)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--eval-at", default="1000000,10000000,50000000")
    ap.add_argument("--out", default=str(ROOT / "results/fidelity/bookkeeping/a"))
    ap.add_argument("--drop", default="", help="comma-separated raw input name prefixes to remove (ablation)")
    args = ap.parse_args()
    if args.stage == "build":
        for split in ("heldout_eval", "train_full"):
            build(split, args.workers)
    elif args.stage == "table":
        table(args)
    else:
        fit(args)


if __name__ == "__main__":
    main()
