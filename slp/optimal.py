"""Exact optimal SLP size via SAT.

Everything else in this project produces UPPER bounds: a circuit of some size.
This module produces LOWER bounds, by deciding

    "does there exist a straight-line program with exactly k XOR gates
     computing every row of M?"

as a SAT instance. UNSAT at k = b-1, together with a circuit of size b, proves
b optimal. As of 2026-09-09 no published lower bound exists for any of the
standard benchmark matrices (see SOURCES.md), so even small closed cases are new.

ENCODING
--------
Signals 0..n-1 are the inputs (fixed basis vectors). Signals n..n+k-1 are gates.
For gate t we introduce:

  sel[t][p]         p < t      one-hot: gate t's first operand is signal p
  selb[t][q]        q < t      one-hot: gate t's second operand is signal q
  val[t][j]         j < n      the coefficient of input j in gate t's linear form

and constrain, for every ordered operand pair (p, q) with p < q < t:

  sel[t][p] & selb[t][q]  ->  ( val[t][j] <-> val[p][j] XOR val[q][j] )   for all j

Targets are matched by indicator variables:

  match[r][s]  ->  val[s][j] == target_r[j]   for all j,   and  OR_s match[r][s]

SYMMETRY BREAKING (all sound for MINIMAL programs)
--------------------------------------------------
  1. p < q            operands are an unordered pair
  2. val[t] != 0      a gate computing zero is wasted
  3. val[t] != val[u] for u < t, and val[t] != any basis vector
                      a minimal program never recomputes a value it already has
  4. gate t's operand pair is lexicographically >= gate (t-1)'s when the two
     gates are independent -- NOT applied by default, since establishing
     independence in the encoding is fiddly and unsound if done carelessly.

Constraints 2 and 3 are what make UNSAT proofs tractable: they collapse the
enormous symmetry of "which order did we build things in".

CAVEAT
------
Constraints 2 and 3 are valid only when searching for a MINIMUM-size program.
They may exclude non-minimal programs of size k. That is exactly what we want
when asking "is there a program of size k?" as part of a minimality search, and
it is why the result is stated as a bound on the minimum, not as an enumeration.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Sequence

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

from .instance import SLPInstance, verify


@dataclass
class SatResult:
    k: int
    sat: bool
    seconds: float
    program: Optional[list[tuple[int, int]]]
    n_vars: int
    n_clauses: int
    timed_out: bool = False


def _build(inst: SLPInstance, k: int):
    n = inst.n_inputs
    total = n + k
    pool = IDPool()
    cls: list[list[int]] = []

    def sel(t, p):   return pool.id(("sel", t, p))
    def selb(t, q):  return pool.id(("selb", t, q))
    def val(s, j):   return pool.id(("val", s, j))
    def match(r, s): return pool.id(("match", r, s))

    # Inputs have fixed values: signal i is the basis vector e_i.
    for i in range(n):
        for j in range(n):
            cls.append([val(i, j)] if i == j else [-val(i, j)])

    for t in range(n, total):
        preds = list(range(t))
        # exactly one first operand, exactly one second operand
        cls.extend(CardEnc.equals(lits=[sel(t, p) for p in preds], bound=1,
                                  vpool=pool, encoding=EncType.pairwise).clauses)
        cls.extend(CardEnc.equals(lits=[selb(t, q) for q in preds], bound=1,
                                  vpool=pool, encoding=EncType.pairwise).clauses)
        # symmetry: operands ordered p < q, so forbid selb(t,q) with q <= p
        for p in preds:
            for q in preds:
                if q <= p:
                    cls.append([-sel(t, p), -selb(t, q)])

        # value definition: sel(t,p) & selb(t,q) -> val[t][j] = val[p][j] xor val[q][j]
        for p in preds:
            for q in preds:
                if q <= p:
                    continue
                a, b = sel(t, p), selb(t, q)
                for j in range(n):
                    x, y, z = val(p, j), val(q, j), val(t, j)
                    # z <-> x xor y, guarded by (a & b)
                    cls.append([-a, -b, -x, -y, -z])
                    cls.append([-a, -b, -x,  y,  z])
                    cls.append([-a, -b,  x, -y,  z])
                    cls.append([-a, -b,  x,  y, -z])

        # a gate must not compute zero
        cls.append([val(t, j) for j in range(n)])

    # No two signals share a value (sound for a minimum-size program).
    for t in range(n, total):
        for u in range(t):
            diff = []
            for j in range(n):
                d = pool.id(("diff", t, u, j))
                # d <-> (val[t][j] xor val[u][j])
                x, y = val(t, j), val(u, j)
                cls.append([-d, x, y]); cls.append([-d, -x, -y])
                cls.append([d, -x, y]); cls.append([d, x, -y])
                diff.append(d)
            cls.append(diff)

    # Every target row is realised by some signal.
    for r, tgt in enumerate(inst.distinct_targets):
        cls.append([match(r, s) for s in range(total)])
        for s in range(total):
            for j in range(n):
                lit = val(s, j) if (tgt >> j) & 1 else -val(s, j)
                cls.append([-match(r, s), lit])

    return pool, cls, total


def exists_program(inst: SLPInstance, k: int, conf_budget: int = 0) -> SatResult:
    """Decide whether an SLP with exactly k gates computes the instance.

    conf_budget > 0 caps the solver's conflict count. On exhaustion the result
    is reported as timed_out, which is neither SAT nor UNSAT -- an inconclusive
    run must never be recorded as a lower bound.
    """
    n = inst.n_inputs
    pool, cls, total = _build(inst, k)
    t0 = time.time()
    timed_out = False
    with Cadical153(bootstrap_with=cls) as solver:
        if conf_budget > 0:
            solver.conf_budget(conf_budget)
            ok = solver.solve_limited()
        else:
            ok = solver.solve()
        elapsed = time.time() - t0
        prog = None
        if ok is None:
            timed_out = True
            ok = False
        elif ok:
            model = set(l for l in solver.get_model() if l > 0)
            prog = []
            for t in range(n, total):
                p = next(x for x in range(t) if pool.id(("sel", t, x)) in model)
                q = next(x for x in range(t) if pool.id(("selb", t, x)) in model)
                prog.append((p, q))
    return SatResult(k=k, sat=bool(ok), seconds=elapsed, program=prog,
                     n_vars=pool.top, n_clauses=len(cls), timed_out=timed_out)


def trivial_lower_bound(inst: SLPInstance) -> int:
    """A free lower bound on the number of XOR gates, from two observations.

    (a) Every distinct target row with popcount >= 2 must be the value of some
        gate. In a MINIMUM-size program no two signals share a value, so those
        targets need that many distinct gates.
    (b) Computing a single row of popcount w needs at least w-1 gates on its own
        dependency path.

    Both are sound for the minimum, so the bound is their maximum. It lets the
    descent stop early instead of asking the solver a question already settled.
    """
    distinct = {t for t in inst.distinct_targets if bin(t).count("1") >= 2}
    by_count = max((bin(t).count("1") - 1 for t in inst.distinct_targets), default=0)
    return max(len(distinct), by_count)


def minimum_size(inst: SLPInstance, lower: int, upper: int,
                 verbose: bool = True, conf_budget: int = 0) -> dict:
    """Find the exact minimum gate count by descending from a known upper bound.

    `upper` must be the size of a circuit we already have (a verified upper
    bound). We test k = upper-1, upper-2, ... until UNSAT. The first UNSAT at k
    proves the minimum is k+1.
    """
    history = []
    best_prog = None
    best = upper
    lb = max(lower, trivial_lower_bound(inst))
    if upper <= lb:
        # the heuristic already matches the free lower bound: optimal, no SAT needed
        return {"instance": inst.name, "fingerprint": inst.fingerprint(),
                "optimal": upper, "proved": True, "program": None,
                "proved_by": "trivial_lower_bound", "lower_bound": lb,
                "history": []}
    k = upper - 1
    while k >= lb:
        res = exists_program(inst, k, conf_budget=conf_budget)
        history.append({"k": k, "sat": res.sat, "timed_out": res.timed_out,
                        "seconds": round(res.seconds, 3),
                        "vars": res.n_vars, "clauses": res.n_clauses})
        if verbose:
            label = "TIMEOUT" if res.timed_out else ("SAT" if res.sat else "UNSAT")
            print(f"    k={k:3d}  {label:7s}  "
                  f"{res.seconds:8.2f}s  ({res.n_vars:,d} vars, {res.n_clauses:,d} clauses)",
                  flush=True)
        if res.timed_out:
            return {"instance": inst.name, "fingerprint": inst.fingerprint(),
                    "optimal": None, "proved": False, "inconclusive_at": k,
                    "best_found": best, "program": best_prog, "history": history}
        if res.sat:
            verify(inst, res.program)          # never trust the solver blindly
            best, best_prog = k, res.program
            k -= 1
        else:
            return {"instance": inst.name, "fingerprint": inst.fingerprint(),
                    "optimal": k + 1, "proved": True, "program": best_prog,
                    "lower_bound_from": k, "history": history}
    # descended to the free lower bound with every k SAT: the bound is tight
    return {"instance": inst.name, "fingerprint": inst.fingerprint(),
            "optimal": best, "proved": True, "program": best_prog,
            "proved_by": "reached_trivial_lower_bound", "lower_bound": lb,
            "history": history}
