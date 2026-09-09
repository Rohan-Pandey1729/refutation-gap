#!/usr/bin/env python3
"""Run baseline SLP heuristics over a benchmark suite, verify, and record."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.instance import verify
from slp.tracking import Result, Run


def run_method(inst, method: str, seed: int, node_cap: int, restarts: int):
    """Returns (best_gates, best_program, elapsed, stats)."""
    best = None
    best_prog = None
    agg = {"oracle_calls": 0, "oracle_nodes": 0, "pair_evals": 0, "core_seconds": 0.0}
    t0 = time.time()
    reps = restarts if method in ("paar2", "rnbp") else 1
    for r in range(reps):
        native.seed(seed * 1_000_003 + r)
        native.reset_stats()
        if method == "paar1":
            prog = native.paar(inst.n_inputs, inst.targets, 0)
        elif method == "paar2":
            prog = native.paar(inst.n_inputs, inst.targets, 1)
        elif method == "bp":
            prog = native.boyar_peralta(inst.n_inputs, inst.targets, 0, node_cap)
        elif method == "rnbp":
            prog = native.boyar_peralta(inst.n_inputs, inst.targets, 1, node_cap)
        else:
            raise KeyError(method)
        gates = verify(inst, prog)          # independent ground-truth check
        s = native.get_stats()
        for k in agg:
            agg[k] += s[k]
        if best is None or gates < best:
            best, best_prog = gates, prog
    return best, best_prog, time.time() - t0, agg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", default="small")
    ap.add_argument("--instances", nargs="*", default=None,
                    help="explicit instance names from the cipher registry")
    ap.add_argument("--methods", nargs="+", default=["paar1", "paar2", "bp", "rnbp"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--node-cap", type=int, default=0,
                    help="DFS node budget for the BP distance oracle; 0 = exact")
    ap.add_argument("--name", default="baselines")
    ap.add_argument("--notes", default="")
    args = ap.parse_args()

    insts = ([registry.get(n) for n in args.instances] if args.instances
             else registry.suite(args.suite))

    print(f"{'instance':28s} {'n':>4s} {'m':>4s} {'naive':>6s} " +
          " ".join(f"{m:>8s}" for m in args.methods))
    with Run(args.name, notes=args.notes, suite=args.suite, methods=args.methods,
             seed=args.seed, restarts=args.restarts, node_cap=args.node_cap) as run:
        for inst in insts:
            cells = []
            for method in args.methods:
                try:
                    gates, prog, secs, stats = run_method(
                        inst, method, args.seed, args.node_cap, args.restarts)
                except Exception as exc:  # keep going; record nothing unverified
                    cells.append("ERR")
                    print(f"  !! {inst.name}/{method}: {exc}", file=sys.stderr)
                    continue
                run.add(Result(
                    instance=inst.name, fingerprint=inst.fingerprint(),
                    n_inputs=inst.n_inputs, n_outputs=inst.n_outputs,
                    method=method,
                    config={"seed": args.seed, "restarts": args.restarts,
                            "node_cap": args.node_cap},
                    gates=gates, naive=inst.naive_cost, seconds=secs,
                    stats=stats, program=prog,
                ))
                cells.append(f"{gates:>8d}")
            print(f"{inst.name:28s} {inst.n_inputs:4d} {inst.n_outputs:4d} "
                  f"{inst.naive_cost:6d} " + " ".join(cells), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
