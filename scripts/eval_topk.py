#!/usr/bin/env python3
"""Does the free candidate prefilter preserve Boyar-Peralta's output, and what does it save?

For each instance: run full BP, then BP restricted each step to the ~K candidates
surviving the free prefilter. Report gates (quality) and oracle calls / wall time
(cost). Every circuit is verified.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.instance import verify


def run(inst, topk):
    native.seed(1)
    native.reset_stats()
    t0 = time.time()
    prog = (native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0) if topk == 0
            else native.boyar_peralta_topk(inst.n_inputs, inst.targets, 0, 0, topk))
    wall = time.time() - t0
    gates = verify(inst, prog)
    s = native.get_stats()
    return {"topk": topk, "gates": gates, "wall": wall,
            "oracle_calls": s["oracle_calls"], "oracle_nodes": s["oracle_nodes"],
            "pair_evals": s["pair_evals"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instances", nargs="*",
                    default=["aes_mixcolumns", "anubis", "clefia_m1", "aes_inv_mixcolumns"])
    ap.add_argument("--sizes", type=int, nargs="*", default=[16, 18, 20])
    ap.add_argument("--ks", type=int, nargs="+", default=[0, 500, 200, 100, 50, 20, 10, 5])
    ap.add_argument("--out", default="runs/topk_results.jsonl")
    args = ap.parse_args()

    jobs = [(registry.random_matrix(n, n, 0.5, 0), f"rand_n{n}_d0.5") for n in args.sizes]
    jobs += [(registry.get(name), name) for name in args.instances]

    out = Path(args.out)
    for inst, label in jobs:
        print(f"\n=== {label}  (n={inst.n_inputs}, naive={inst.naive_cost})")
        print(f"{'topk':>6s} {'gates':>6s} {'d_gates':>8s} {'wall_s':>9s} {'speedup':>8s} "
              f"{'oracle_calls':>13s} {'call_ratio':>11s}")
        base = None
        for k in args.ks:
            r = run(inst, k)
            r.update({"instance": label, "n": inst.n_inputs})
            if base is None:
                base = r
            dg = r["gates"] - base["gates"]
            sp = base["wall"] / max(1e-9, r["wall"])
            cr = r["oracle_calls"] / max(1, base["oracle_calls"])
            print(f"{k if k else 'full':>6} {r['gates']:6d} {dg:+8d} {r['wall']:9.3f} "
                  f"{sp:8.2f} {r['oracle_calls']:13,d} {cr:11.3f}", flush=True)
            with out.open("a") as fh:
                fh.write(json.dumps(r) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
