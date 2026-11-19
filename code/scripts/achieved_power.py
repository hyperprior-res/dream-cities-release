"""Power of the main claim's test at the achieved intra-checkpoint correlation .

The study protocol (section 1) gives the power at intra-checkpoint correlations 0.3 and 0.5 through the design
effect 1 + (m - 1) rho (m pairs per checkpoint) and asks for the power at the achieved correlation.
``analyse_ladder.py`` computes the first (``power_block``: effective pairs n / (1 + (m - 1) rho), then
``fisher_power(0.4, n_eff)``, two-sided 5 per cent, Fisher z) and writes the achieved correlations to
``main_claim.json`` (``results.power.icc_measured``: ICC(1) by checkpoint of the audit variable and of the RL
variables over the deciding pairs). This script applies the same two steps, imported read-only from
``analyse_ladder.py``, at those measured values. Neither input involves the correlation between the two variables
the claim is decided on. ICC(1) can be negative; the design effect is then below 1, and the power at rho = 0
(independent pairs) is given beside it.

The ICCs are measured on the deciding pairs (all 120 cities), so the value is only final when ``main_claim.json``
is complete; until then it is written as pending and no number is given.

    PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/achieved_power.py

Writes results/analysis/achieved_power.json and achieved_power.md.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "scripts"))
import analyse_ladder as AL  # noqa: E402  (read-only: fisher_power, THRESHOLD, power_block, PRIMARY_X/Y)

MC = ROOT / "results/analysis/main_claim.json"


def power_at(n_pairs: int, n_clusters: int, icc: float) -> dict:
    """``analyse_ladder.power_block``'s computation at one intra-checkpoint correlation."""
    m = n_pairs / n_clusters
    deff = 1 + (m - 1) * icc
    n_eff = n_pairs / deff
    return {"icc": icc, "design_effect": deff, "n_eff": n_eff,
            f"power_spearman_{AL.THRESHOLD}": AL.fisher_power(AL.THRESHOLD, n_eff)}


def compute(mc: dict) -> dict:
    r = mc["results"]
    pw = r["power"]
    x, y = AL.PRIMARY_X, AL.PRIMARY_Y
    out = {"main_claim_status": mc["status"], "n_pairs": pw["n_pairs"], "n_clusters": pw["n_clusters"],
           "primary_x": x, "primary_y": y, "threshold": AL.THRESHOLD,
           "method": "analyse_ladder.power_block's design effect 1 + (m - 1) rho and analyse_ladder.fisher_power "
                     "(two-sided 5 %, Fisher z), at the ICC(1) values main_claim.json gives in results.power.icc_measured"}
    if mc["status"] != "complete" or r.get("status") != "complete":
        out.update(status="pending", reason=f"main_claim.json is {mc['status']} ({pw['n_pairs']} of "
                                            f"{AL.LADDER_SIZE * len(AL.FAMILIES)} deciding pairs): the achieved "
                                            "correlations are measured on the deciding pairs", values=None)
        return out
    icc = pw["icc_measured"]
    vals = {k: power_at(pw["n_pairs"], pw["n_clusters"], icc[k]) for k in (x, y)}
    hi = max(icc[x], icc[y])
    vals["larger of the two"] = power_at(pw["n_pairs"], pw["n_clusters"], hi)
    if min(icc[x], icc[y]) < 0:
        vals["rho = 0 (independent pairs)"] = power_at(pw["n_pairs"], pw["n_clusters"], 0.0)
    out.update(status="complete", values=vals,
               protocol={k: v[f"power_spearman_{AL.THRESHOLD}"] for k, v in pw["at_icc"].items()})
    return out


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--main-claim", default=str(MC))
    ap.add_argument("--out", default=str(ROOT / "results/analysis"))
    a = ap.parse_args(argv)
    res = compute(json.loads(Path(a.main_claim).read_text()))
    res["generated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    res["input"] = a.main_claim
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "achieved_power.json").write_text(json.dumps(res, indent=1))
    L = ["# Power of the main claim's test at the achieved intra-checkpoint correlation", "",
         f"Generated {res['generated']} by `code/scripts/achieved_power.py` from `{a.main_claim}`. Method: "
         f"{res['method']}.", ""]
    if res["status"] == "pending":
        L.append(f"**Pending**: {res['reason']}. No value is given.")
    else:
        L += [f"{res['n_pairs']} pairs in {res['n_clusters']} checkpoints. Protocol: power "
              + ", ".join(f"{v:.2f} at rho {k}" for k, v in res["protocol"].items()) + ".", "",
              "| intra-checkpoint correlation | rho | design effect | effective pairs | power to detect 0.4 |",
              "|---|---|---|---|---|"]
        for k, v in res["values"].items():
            L.append(f"| {k} | {v['icc']:+.3f} | {v['design_effect']:.2f} | {v['n_eff']:.1f} | "
                     f"{v[f'power_spearman_{AL.THRESHOLD}']:.2f} |")
    (out / "achieved_power.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
