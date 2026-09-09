#!/usr/bin/env python3
"""Re-establish every closed optimality result with a checked DRAT refutation.

Our earlier sweeps recorded 121 proven optima resting on bare solver UNSAT
answers. This re-runs them so each result carries a certificate an independent
third-party checker accepted, and measures what that costs.

Recorded per instance: solve time with and without proof logging, proof size,
independent check time, and the checker's verdict. A result counts as certified
only when drat-trim returns VERIFIED.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.certified import SOLVERS, certified_minimum, prove_unsat
from slp.instance import verify
from slp.optimal import exists_program


def best_heuristic(inst, restarts=300):
    best, prog = None, None
    for mode in (0, 1):
        for r in range(restarts if mode else 1):
            native.seed(1000 + r)
            p = native.paar(inst.n_inputs, inst.targets, mode)
            g = verify(inst, p)
            if best is None or g < best:
                best, prog = g, p
    for mode in (0, 1):
        for r in range(min(restarts, 50) if mode else 1):
            native.seed(3000 + r)
            p = native.boyar_peralta(inst.n_inputs, inst.targets, mode, 0)
            g = verify(inst, p)
            if g < best:
                best, prog = g, p
    return best, prog


def load_closed(paths):
    """Instances previously closed, deduplicated by fingerprint."""
    seen, out = set(), []
    for p in paths:
        f = Path(p)
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if not r.get("proved") or r["fingerprint"] in seen:
                continue
            seen.add(r["fingerprint"])
            out.append(r)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="+",
                    default=["runs/optimal_results.jsonl", "runs/optimal_broad.jsonl",
                             "runs/optimal_more.jsonl"])
    ap.add_argument("--out", default="runs/certified.jsonl")
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--keep-proofs", type=int, default=3,
                    help="keep the DRAT files for this many instances, as artifacts")
    ap.add_argument("--baseline-solver", default="cadical153",
                    help="solver timed WITHOUT proof logging, for the overhead comparison")
    args = ap.parse_args()

    closed = [r for r in load_closed(args.sources) if r["n"] <= args.max_n]
    closed.sort(key=lambda r: (r["n"], r["instance"]))
    if args.limit:
        closed = closed[:args.limit]
    out = Path(args.out)
    print(f"{len(closed)} previously-closed instances to certify (n <= {args.max_n})\n")
    print(f"{'instance':26s} {'opt':>4s} {'agree':>6s} {'solve_s':>8s} {'base_s':>8s} "
          f"{'proof_lines':>12s} {'proof_MB':>9s} {'check_s':>8s} {'verdict':>14s}")

    n_cert = n_disagree = n_fail = 0
    kept = 0
    for row in closed:
        inst = registry.random_matrix(row["n"], row["n"], row["density"], row["seed"])
        assert inst.fingerprint() == row["fingerprint"], inst.name
        ub, prog = best_heuristic(inst)
        keep = kept < args.keep_proofs
        t0 = time.time()
        res = certified_minimum(inst, ub, prog, keep_proof=keep)
        wall = time.time() - t0
        if keep:
            kept += 1

        dec = [h for h in res["history"] if not h.sat]
        d = dec[-1] if dec else None

        # baseline: same decisive query, no proof logging, faster solver
        base_s = None
        if d is not None:
            t0 = time.time()
            exists_program(inst, d.k)
            base_s = time.time() - t0

        agree = (res["optimal"] == row["optimal"])
        if not agree:
            n_disagree += 1
        if res["proved"]:
            n_cert += 1
        else:
            n_fail += 1

        rec = {
            "instance": inst.name, "fingerprint": inst.fingerprint(), "n": row["n"],
            "density": row["density"], "seed": row["seed"],
            "previous_optimal": row["optimal"], "optimal": res["optimal"],
            "agrees_with_previous": agree,
            "heuristic_ub": ub, "certified": res["proved"],
            "certificate": res["certificate"], "wall_seconds": wall,
            "baseline_solve_seconds": base_s,
            "decisive": (asdict(d) | {"program": None}) if d is not None else None,
            "history": [asdict(h) | {"program": None} for h in res["history"]],
            "proof_kept": keep,
        }
        with out.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")

        if d is not None:
            print(f"{inst.name:26s} {res['optimal']:4d} {str(agree):>6s} "
                  f"{d.solve_seconds:8.2f} {base_s:8.2f} {d.proof_lines:12,d} "
                  f"{d.proof_bytes/1e6:9.2f} {d.check_seconds:8.2f} {d.verdict:>14s}",
                  flush=True)
        else:
            print(f"{inst.name:26s} {res['optimal']:4d} {str(agree):>6s} "
                  f"{'-':>8s} {'-':>8s} {'-':>12s} {'-':>9s} {'-':>8s} "
                  f"{'no refutation':>14s}", flush=True)

    print(f"\ncertified: {n_cert}   uncertified: {n_fail}   "
          f"disagreements with earlier runs: {n_disagree}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
