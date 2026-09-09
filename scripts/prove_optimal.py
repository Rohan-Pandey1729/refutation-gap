#!/usr/bin/env python3
"""Prove exact optimal SLP sizes for small instances via SAT.

For each instance: take the best circuit our heuristics can find (a verified
upper bound), then descend k = best-1, best-2, ... asking SAT whether a k-gate
program exists. The first UNSAT proves optimality.

Nothing is recorded as proved unless the solver actually returned UNSAT --
a conflict-budget exhaustion is recorded as inconclusive.
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
from slp.optimal import minimum_size
from slp.tracking import Result, Run


def best_heuristic(inst, restarts=200):
    best, best_prog, which = None, None, None
    for name, mode, fn in [("paar1", 0, native.paar), ("paar2", 1, native.paar),
                           ("bp", 0, native.boyar_peralta), ("rnbp", 1, native.boyar_peralta)]:
        reps = restarts if name in ("paar2", "rnbp") else 1
        for r in range(reps):
            native.seed(1000 + r)
            prog = fn(inst.n_inputs, inst.targets, mode) if fn is native.paar \
                else fn(inst.n_inputs, inst.targets, mode, 0)
            g = verify(inst, prog)
            if best is None or g < best:
                best, best_prog, which = g, prog, name
    return best, best_prog, which


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[6, 7, 8, 9, 10])
    ap.add_argument("--densities", type=float, nargs="+", default=[0.3, 0.5, 0.7])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--conf-budget", type=int, default=20_000_000)
    ap.add_argument("--restarts", type=int, default=200)
    ap.add_argument("--out", default="runs/optimal_results.jsonl")
    ap.add_argument("--name", default="prove_optimal")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    proved = inconclusive = 0

    print(f"{'instance':26s} {'naive':>6s} {'heur':>5s} {'via':>6s} {'OPT':>5s} {'gap':>4s} {'sec':>9s}")
    with Run(args.name, notes="SAT optimality proofs for small random instances",
             sizes=args.sizes, densities=args.densities, seeds=args.seeds,
             conf_budget=args.conf_budget) as run:
        for n in args.sizes:
            for d in args.densities:
                for s in args.seeds:
                    inst = registry.random_matrix(n, n, d, s)
                    ub, ub_prog, which = best_heuristic(inst, args.restarts)
                    t0 = time.time()
                    res = minimum_size(inst, lower=1, upper=ub, verbose=False,
                                       conf_budget=args.conf_budget)
                    secs = time.time() - t0
                    if res["proved"]:
                        opt = res["optimal"]
                        prog = res["program"] if res["program"] is not None else ub_prog
                        gates = verify(inst, prog)
                        assert gates == opt or gates == ub, (gates, opt, ub)
                        proved += 1
                        run.add(Result(
                            instance=inst.name, fingerprint=inst.fingerprint(),
                            n_inputs=inst.n_inputs, n_outputs=inst.n_outputs,
                            method="sat_optimal",
                            config={"conf_budget": args.conf_budget,
                                    "heuristic_ub": ub, "heuristic": which},
                            gates=opt, naive=inst.naive_cost, seconds=secs,
                            stats={"history": res["history"], "proved": True},
                            program=prog if gates == opt else [],
                        ))
                        print(f"{inst.name:26s} {inst.naive_cost:6d} {ub:5d} {which:>6s} "
                              f"{opt:5d} {ub-opt:+4d} {secs:9.2f}", flush=True)
                    else:
                        inconclusive += 1
                        print(f"{inst.name:26s} {inst.naive_cost:6d} {ub:5d} {which:>6s} "
                              f"{'?':>5s} {'':>4s} {secs:9.2f}  inconclusive at "
                              f"k={res.get('inconclusive_at')}", flush=True)
                    with out.open("a") as fh:
                        fh.write(json.dumps({
                            "instance": inst.name, "fingerprint": inst.fingerprint(),
                            "n": n, "density": d, "seed": s, "naive": inst.naive_cost,
                            "heuristic_ub": ub, "heuristic": which,
                            "optimal": res.get("optimal"), "proved": res["proved"],
                            "inconclusive_at": res.get("inconclusive_at"),
                            "seconds": secs, "history": res["history"],
                        }) + "\n")
    print(f"\nproved optimal: {proved}   inconclusive: {inconclusive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
