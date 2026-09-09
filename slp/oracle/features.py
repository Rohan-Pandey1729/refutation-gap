"""Cheap features for the learned distance oracle.

The oracle answers: given the current added-signal set A and a query x with
budget b, is g(x) <= b, where

    g(x) = min over T subset of A of ( |T| + popcount(x XOR XOR(T)) )

Computing that exactly is the NP-hard subroutine that dominates Boyar-Peralta's
runtime. A learned replacement is only useful if evaluating it costs less than
the DFS it replaces, so every feature here is O(|A|) with vectorised integer ops
-- comparable to a few dozen DFS nodes, against the thousands the exact oracle
needs at n=20.

Feature groups:
  query        popcount(x), budget b, |A|, n, b - popcount(x)
  single-step  statistics of popcount(x XOR a) over a in A: the best single
               added signal is the dominant term in g for small budgets
  overlap      statistics of popcount(x AND a) and popcount(a)
  reachability cheap necessary conditions, e.g. how many a reduce popcount at all
"""
from __future__ import annotations

import numpy as np

FEATURE_NAMES = [
    "n", "budget", "pc_x", "n_added", "budget_minus_pcx", "pcx_over_n",
    "min_pc_xor", "mean_pc_xor", "std_pc_xor", "second_min_pc_xor",
    "min_pc_xor_minus_pcx", "n_reducing", "frac_reducing",
    "best_gain", "mean_gain_pos", "n_gain_ge2", "n_gain_ge3", "n_gain_ge4",
    "min_pc_and", "max_pc_and", "mean_pc_and",
    "min_pc_a", "mean_pc_a", "max_pc_a",
    "budget_minus_min_pc_xor", "min_pc_xor_le_budget", "pcx_le_budget",
    "est_g_1step", "est_g_2step_lb", "slack_1step",
]
N_FEATURES = len(FEATURE_NAMES)

_POPCOUNT = np.array([bin(i).count("1") for i in range(1 << 16)], dtype=np.int16)


def popcount64(v: np.ndarray) -> np.ndarray:
    """Vectorised popcount for uint64 arrays."""
    v = v.astype(np.uint64, copy=False)
    return (_POPCOUNT[(v & np.uint64(0xFFFF)).astype(np.int64)]
            + _POPCOUNT[((v >> np.uint64(16)) & np.uint64(0xFFFF)).astype(np.int64)]
            + _POPCOUNT[((v >> np.uint64(32)) & np.uint64(0xFFFF)).astype(np.int64)]
            + _POPCOUNT[((v >> np.uint64(48)) & np.uint64(0xFFFF)).astype(np.int64)]
            ).astype(np.int16)


def featurize_one(n: int, added: np.ndarray, x: int, budget: int) -> np.ndarray:
    """Features for a single query. `added` is a uint64 array of signals in A."""
    out = np.zeros(N_FEATURES, dtype=np.float32)
    pc_x = int(popcount64(np.array([x], dtype=np.uint64))[0])
    na = len(added)
    out[0] = n
    out[1] = budget
    out[2] = pc_x
    out[3] = na
    out[4] = budget - pc_x
    out[5] = pc_x / max(1, n)

    if na == 0:
        out[6] = out[7] = out[9] = pc_x
        out[24] = budget - pc_x
        out[26] = 1.0 if pc_x <= budget else 0.0
        out[25] = out[26]
        out[27] = pc_x
        out[28] = pc_x
        return out

    xo = popcount64(np.uint64(x) ^ added).astype(np.float32)
    pa = popcount64(added).astype(np.float32)
    an = popcount64(np.uint64(x) & added).astype(np.float32)

    mn = float(xo.min())
    out[6] = mn
    out[7] = float(xo.mean())
    out[8] = float(xo.std())
    out[9] = float(np.partition(xo, 1)[1]) if na > 1 else mn
    out[10] = mn - pc_x

    gain = pc_x - xo                     # popcount reduction from using a alone
    reducing = gain > 0
    out[11] = float(reducing.sum())
    out[12] = float(reducing.mean())
    out[13] = float(gain.max())
    out[14] = float(gain[reducing].mean()) if reducing.any() else 0.0
    out[15] = float((gain >= 2).sum())
    out[16] = float((gain >= 3).sum())
    out[17] = float((gain >= 4).sum())

    out[18] = float(an.min()); out[19] = float(an.max()); out[20] = float(an.mean())
    out[21] = float(pa.min()); out[22] = float(pa.mean()); out[23] = float(pa.max())

    out[24] = budget - mn
    out[25] = 1.0 if mn + 1 <= budget else 0.0
    out[26] = 1.0 if pc_x <= budget else 0.0
    # cheap estimates of g(x)
    out[27] = min(pc_x, 1.0 + mn)                       # best 0- or 1-element T
    out[28] = max(0.0, pc_x - 2.0 * float(gain.max()))  # crude 2-step lower bound
    out[29] = out[27] - budget
    return out


def featurize_batch(n: int, added: np.ndarray, xs: np.ndarray,
                    budgets: np.ndarray) -> np.ndarray:
    """Features for many queries sharing one added-set. Vectorised over queries."""
    q = len(xs)
    out = np.zeros((q, N_FEATURES), dtype=np.float32)
    pc_x = popcount64(xs).astype(np.float32)
    na = len(added)
    out[:, 0] = n
    out[:, 1] = budgets
    out[:, 2] = pc_x
    out[:, 3] = na
    out[:, 4] = budgets - pc_x
    out[:, 5] = pc_x / max(1, n)

    if na == 0:
        out[:, 6] = out[:, 7] = out[:, 9] = pc_x
        out[:, 24] = budgets - pc_x
        out[:, 26] = (pc_x <= budgets).astype(np.float32)
        out[:, 25] = out[:, 26]
        out[:, 27] = pc_x
        out[:, 28] = pc_x
        return out

    # (q, na) matrices
    xo = popcount64((xs[:, None].astype(np.uint64) ^ added[None, :])).astype(np.float32)
    an = popcount64((xs[:, None].astype(np.uint64) & added[None, :])).astype(np.float32)
    pa = popcount64(added).astype(np.float32)

    mn = xo.min(axis=1)
    out[:, 6] = mn
    out[:, 7] = xo.mean(axis=1)
    out[:, 8] = xo.std(axis=1)
    out[:, 9] = np.partition(xo, 1, axis=1)[:, 1] if na > 1 else mn
    out[:, 10] = mn - pc_x

    gain = pc_x[:, None] - xo
    reducing = gain > 0
    out[:, 11] = reducing.sum(axis=1)
    out[:, 12] = reducing.mean(axis=1)
    out[:, 13] = gain.max(axis=1)
    pos_sum = np.where(reducing, gain, 0.0).sum(axis=1)
    pos_cnt = reducing.sum(axis=1)
    out[:, 14] = np.where(pos_cnt > 0, pos_sum / np.maximum(pos_cnt, 1), 0.0)
    out[:, 15] = (gain >= 2).sum(axis=1)
    out[:, 16] = (gain >= 3).sum(axis=1)
    out[:, 17] = (gain >= 4).sum(axis=1)

    out[:, 18] = an.min(axis=1); out[:, 19] = an.max(axis=1); out[:, 20] = an.mean(axis=1)
    out[:, 21] = pa.min(); out[:, 22] = pa.mean(); out[:, 23] = pa.max()

    out[:, 24] = budgets - mn
    out[:, 25] = ((mn + 1) <= budgets).astype(np.float32)
    out[:, 26] = (pc_x <= budgets).astype(np.float32)
    out[:, 27] = np.minimum(pc_x, 1.0 + mn)
    out[:, 28] = np.maximum(0.0, pc_x - 2.0 * gain.max(axis=1))
    out[:, 29] = out[:, 27] - budgets
    return out
