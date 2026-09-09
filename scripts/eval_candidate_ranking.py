#!/usr/bin/env python3
"""Can candidate pairs be ranked cheaply enough to skip most oracle calls?

Boyar-Peralta scores every candidate pair against every unsolved target, which
on AES MixColumns is ~4M exact-oracle calls. If a cheap ranker reliably puts an
OPTIMAL candidate in its top K, the search only has to evaluate K candidates
exactly per step, and the result is identical whenever the top-K contains one.

Before reaching for a model, establish the free baseline. Since
    g(x) <= popcount(x)
always holds, the condition
    popcount(t XOR u) <= dist[t] - 1
is a SUFFICIENT condition for adding u to reduce target t's distance. Counting
the targets satisfying it is a guaranteed lower bound on u's reduction count,
costs O(#targets) integer ops, and needs no training data at all.

This script measures recall@K for that free heuristic against ground truth.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.instance import apply_program, verify

_PC = np.array([bin(i).count("1") for i in range(1 << 16)], dtype=np.int16)


def pc(v):
    v = np.asarray(v, dtype=np.uint64)
    return (_PC[(v & np.uint64(0xFFFF)).astype(np.int64)]
            + _PC[((v >> np.uint64(16)) & np.uint64(0xFFFF)).astype(np.int64)]
            + _PC[((v >> np.uint64(32)) & np.uint64(0xFFFF)).astype(np.int64)]
            + _PC[((v >> np.uint64(48)) & np.uint64(0xFFFF)).astype(np.int64)]).astype(np.int32)


def replay(inst, program):
    """Re-derive the (targets, dist) state at each step, as the C search saw it."""
    n = inst.n_inputs
    targets = [t for t in inst.distinct_targets if bin(t).count("1") > 1]
    dist = [bin(t).count("1") - 1 for t in targets]
    sigs = apply_program(n, program)
    states = []
    for k in range(len(program)):
        states.append((list(dist), sigs[n + k]))
        # recompute distances exactly the way the search does: via the oracle
        added = sigs[n:n + k + 1]
        for r, t in enumerate(targets):
            if dist[r] > 0:
                g = native.gval(n, t ^ sigs[n + k], [int(a) for a in added[:-1]] or [], dist[r] - 1)
                if g <= dist[r] - 1:
                    dist[r] -= 1
    return targets, states


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instances", nargs="*", default=["anubis", "clefia_m1"])
    ap.add_argument("--sizes", type=int, nargs="*", default=[12, 14, 16])
    ap.add_argument("--ks", type=int, nargs="+", default=[1, 2, 3, 5, 10, 20, 50, 100])
    ap.add_argument("--out", default="runs/candidate_ranking.jsonl")
    args = ap.parse_args()

    jobs = [(registry.random_matrix(n, n, 0.5, 0), f"rand_n{n}") for n in args.sizes]
    jobs += [(registry.get(name), name) for name in args.instances]

    print(f"{'instance':20s} {'steps':>6s} {'cands/step':>11s} " +
          " ".join(f"{'r@'+str(k):>7s}" for k in args.ks) + f" {'frac@best':>10s}")
    allrows = []
    for inst, label in jobs:
        prog, recs = native.boyar_peralta_candidates(inst.n_inputs, inst.targets, 0)
        verify(inst, prog)
        bystep = defaultdict(list)
        for (st, u, tot, base) in recs:
            bystep[st].append((int(u), int(tot)))
        targets, states = replay(inst, prog)
        tarr = np.array(targets, dtype=np.uint64)

        hits = {k: 0 for k in args.ks}
        steps = 0
        cands_total = 0
        frac_optimal = []
        for st in sorted(bystep):
            if st >= len(states):
                break
            dist, _chosen = states[st]
            cands = bystep[st]
            if not cands:
                continue
            us = np.array([c[0] for c in cands], dtype=np.uint64)
            totals = np.array([c[1] for c in cands], dtype=np.int32)
            best_total = totals.min()
            frac_optimal.append(float((totals == best_total).mean()))

            active = [r for r, d in enumerate(dist) if d > 0]
            if not active:
                continue
            # free heuristic: count targets where popcount(t^u) <= dist-1
            score = np.zeros(len(us), dtype=np.int32)
            for r in active:
                score += (pc(tarr[r] ^ us) <= (dist[r] - 1)).astype(np.int32)
            order = np.argsort(-score, kind="stable")
            ranked_totals = totals[order]
            steps += 1
            cands_total += len(us)
            for k in args.ks:
                if ranked_totals[:k].min() == best_total:
                    hits[k] += 1

        row = {"instance": label, "n": inst.n_inputs, "steps": steps,
               "cands_per_step": cands_total / max(1, steps),
               "recall_at_k": {str(k): hits[k] / max(1, steps) for k in args.ks},
               "mean_frac_optimal": float(np.mean(frac_optimal)) if frac_optimal else 0.0}
        allrows.append(row)
        print(f"{label:20s} {steps:6d} {row['cands_per_step']:11.1f} " +
              " ".join(f"{hits[k]/max(1,steps):7.3f}" for k in args.ks) +
              f" {row['mean_frac_optimal']:10.4f}", flush=True)

    Path(args.out).write_text("\n".join(json.dumps(r) for r in allrows) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
