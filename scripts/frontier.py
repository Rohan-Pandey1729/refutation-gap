#!/usr/bin/env python3
"""How far can a modern SAT solver push exact g-XOR optimality?

Fuhs & Schneider-Kamp (SAT 2010) established the method and hit a wall: they
proved a 13-gate 8-input instance optimal, but could not settle a 21x8 instance
at k=22 after 40+ days of solver time. As far as an independent literature check
could determine, nobody has revisited that wall with a modern solver.

This measures the frontier with CaDiCaL: for increasing n, how long does the
decisive UNSAT proof take, and where does it become infeasible?

The interesting number is the time for the UNSAT call at k = opt-1. SAT calls are
easy; it is the UNSAT proof that establishes the lower bound.
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
from slp.optimal import exists_program, trivial_lower_bound


def best_heuristic(inst, restarts=400):
    best, prog = None, None
    for mode in (0, 1):
        for r in range(restarts if mode else 1):
            native.seed(5000 + r)
            p1 = native.paar(inst.n_inputs, inst.targets, mode)
            g = verify(inst, p1)
            if best is None or g < best:
                best, prog = g, p1
    for mode in (0, 1):
        for r in range(min(restarts, 40) if mode else 1):
            native.seed(7000 + r)
            p2 = native.boyar_peralta(inst.n_inputs, inst.targets, mode, 0)
            g = verify(inst, p2)
            if g < best:
                best, prog = g, p2
    return best, prog


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[9, 10, 11, 12, 13])
    ap.add_argument("--density", type=float, default=0.4)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1])
    ap.add_argument("--conf-budget", type=int, default=8_000_000)
    ap.add_argument("--out", default="runs/frontier.jsonl")
    args = ap.parse_args()

    out = Path(args.out)
    print(f"{'instance':24s} {'lb':>4s} {'ub':>4s} {'k':>4s} {'result':>9s} "
          f"{'sec':>10s} {'vars':>10s} {'clauses':>12s}")
    for n in args.sizes:
        for s in args.seeds:
            inst = registry.random_matrix(n, n, args.density, s)
            ub, prog = best_heuristic(inst)
            lb = trivial_lower_bound(inst)
            k = ub - 1
            if k < lb:
                print(f"{inst.name:24s} {lb:4d} {ub:4d} {'-':>4s} "
                      f"{'lb=ub':>9s} {'':>10s}")
                continue
            t0 = time.time()
            res = exists_program(inst, k, conf_budget=args.conf_budget)
            secs = time.time() - t0
            label = "TIMEOUT" if res.timed_out else ("SAT" if res.sat else "UNSAT")
            print(f"{inst.name:24s} {lb:4d} {ub:4d} {k:4d} {label:>9s} "
                  f"{secs:10.2f} {res.n_vars:10,d} {res.n_clauses:12,d}", flush=True)
            with out.open("a") as fh:
                fh.write(json.dumps({
                    "instance": inst.name, "n": n, "density": args.density, "seed": s,
                    "heuristic_ub": ub, "trivial_lb": lb, "k": k, "result": label,
                    "seconds": secs, "vars": res.n_vars, "clauses": res.n_clauses,
                    "conf_budget": args.conf_budget}) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
