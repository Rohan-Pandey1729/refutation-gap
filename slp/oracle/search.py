"""Boyar-Peralta with a pluggable distance oracle.

The C implementation in slp/core.c hardcodes the exact DFS oracle. This Python
version takes the oracle as an argument so that exact, budgeted and learned
oracles can be compared inside an otherwise identical search.

It is slower than the C version per step, but that is not what is being measured:
the comparison is between oracles inside the same outer loop, and the learned
oracle's queries are answered in one batched call per step, which the exact DFS
cannot do.

Any circuit this produces still goes through slp.instance.verify.
"""
from __future__ import annotations

import time
from typing import Callable, Optional

import numpy as np

from ..instance import SLPInstance

# An oracle answers a BATCH of queries: given the current added-set and arrays
# of (x, budget), return a boolean array "is g(x) <= budget".
OracleFn = Callable[[int, np.ndarray, np.ndarray, np.ndarray], np.ndarray]


def exact_oracle_factory():
    """Reference oracle: exact, via the C DFS. Used to validate the Python loop."""
    from ..native import gval

    def fn(n, added, xs, budgets):
        added_list = [int(a) for a in added]
        out = np.zeros(len(xs), dtype=bool)
        for i, (x, b) in enumerate(zip(xs, budgets)):
            if b < 0:
                continue
            out[i] = gval(n, int(x), added_list, int(b)) <= int(b)
        return out
    return fn


def boyar_peralta(inst: SLPInstance, oracle: OracleFn, max_steps: int = 100000,
                  collect_timing: bool = True) -> dict:
    n = inst.n_inputs
    S: list[int] = [1 << i for i in range(n)]
    added: list[int] = []
    targets = [t for t in inst.distinct_targets if bin(t).count("1") > 1]
    dist = [bin(t).count("1") - 1 for t in targets]
    program: list[tuple[int, int]] = []
    oracle_seconds = 0.0
    n_queries = 0
    steps = 0

    while any(d > 0 for d in dist) and steps < max_steps:
        steps += 1
        sig = np.array(S, dtype=np.uint64)
        ns = len(S)
        iu, ju = np.triu_indices(ns, k=1)
        cand = sig[iu] ^ sig[ju]
        # drop candidates equal to an existing signal or zero
        keep = (cand != 0) & ~np.isin(cand, sig)
        iu, ju, cand = iu[keep], ju[keep], cand[keep]
        if len(cand) == 0:
            break

        active = [r for r, d in enumerate(dist) if d > 0]
        xs = np.concatenate([np.uint64(targets[r]) ^ cand for r in active])
        bs = np.concatenate([np.full(len(cand), dist[r] - 1, dtype=np.int16)
                             for r in active])
        added_arr = np.array(added, dtype=np.uint64)

        t0 = time.perf_counter()
        red = oracle(n, added_arr, xs, bs)
        if collect_timing:
            oracle_seconds += time.perf_counter() - t0
        n_queries += len(xs)

        red = red.reshape(len(active), len(cand))
        newdist = np.array([dist[r] for r in active], dtype=np.int32)[:, None] - red.astype(np.int32)
        base = sum(d for r, d in enumerate(dist) if d == 0 or r not in active)
        totals = newdist.sum(axis=0) + base
        norms = (newdist.astype(np.int64) ** 2).sum(axis=0)

        best = np.lexsort((-norms, totals))[0]
        i, j, u = int(iu[best]), int(ju[best]), int(cand[best])
        program.append((i, j))
        S.append(u)
        added.append(u)
        for idx, r in enumerate(active):
            if red[idx, best]:
                dist[r] -= 1

    return {"program": program, "steps": steps, "oracle_seconds": oracle_seconds,
            "queries": n_queries, "solved": all(d == 0 for d in dist)}
