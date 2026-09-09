#!/usr/bin/env python3
"""Exact optimal XOR counts for small MDS matrices over GF(2^4).

MDS diffusion matrices are the objects the XOR-count literature actually cares
about, and no proven-optimal XOR count exists for any of them (SOURCES.md 6b).
The smallest interesting ones are within reach of SAT: a k x k MDS matrix over
GF(2^4) expands to a 4k x 4k binary matrix, so k=2 gives n=8 and k=3 gives n=12.

(A 4x4 MDS matrix over GF(4) would give n=8 too, but none exists: it would need
an MDS code of length 8 over GF(4), beyond the q+1 = 5 limit.)

A matrix is MDS iff every square submatrix is nonsingular. We search small
circulant and Hadamard candidates over GF(2^4) for MDS ones, then prove the
minimum XOR count of the expanded binary matrix.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.gf import GF2k, circulant, expand_to_binary, hadamard
from slp.instance import SLPInstance, verify
from slp.optimal import exists_program, trivial_lower_bound


def det(field, m):
    """Determinant over GF(2^k) by Gaussian elimination."""
    n = len(m)
    a = [row[:] for row in m]
    result = 1
    for col in range(n):
        piv = next((r for r in range(col, n) if a[r][col]), None)
        if piv is None:
            return 0
        if piv != col:
            a[col], a[piv] = a[piv], a[col]
        result = field.mul(result, a[col][col])
        inv = next(x for x in range(1, 1 << field.k) if field.mul(x, a[col][col]) == 1)
        for r in range(col + 1, n):
            if a[r][col]:
                f = field.mul(a[r][col], inv)
                for c in range(col, n):
                    a[r][c] ^= field.mul(f, a[col][c])
    return result


def is_mds(field, m):
    n = len(m)
    for size in range(1, n + 1):
        for rows in itertools.combinations(range(n), size):
            for cols in itertools.combinations(range(n), size):
                sub = [[m[r][c] for c in cols] for r in rows]
                if det(field, sub) == 0:
                    return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dims", type=int, nargs="+", default=[2, 3])
    ap.add_argument("--modulus", type=lambda x: int(x, 0), default=0x13)
    ap.add_argument("--max-candidates", type=int, default=6)
    ap.add_argument("--conf-budget", type=int, default=40_000_000)
    ap.add_argument("--restarts", type=int, default=600)
    ap.add_argument("--out", default="runs/mds_optimal.jsonl")
    args = ap.parse_args()

    field = GF2k(args.modulus)
    out = Path(args.out)
    print(f"field GF(2^{field.k}) / {args.modulus:#x}")

    for dim in args.dims:
        found = 0
        print(f"\n--- {dim}x{dim} MDS over GF(2^{field.k})  ->  binary {dim*field.k}x{dim*field.k}")
        for coeffs in itertools.product(range(1, 1 << field.k), repeat=dim):
            if found >= args.max_candidates:
                break
            for kind, build in (("circ", circulant), ("had", hadamard)):
                if kind == "had" and (dim & (dim - 1)):
                    continue
                m = build(list(coeffs))
                if not is_mds(field, m):
                    continue
                found += 1
                binary = expand_to_binary(field, m)
                name = f"mds{dim}_{kind}_" + "_".join(f"{c:x}" for c in coeffs)
                inst = SLPInstance.from_binary_matrix(
                    name, binary, source="generated MDS", verified=True)
                # best heuristic upper bound
                best, prog = None, None
                for mode in (0, 1):
                    for r in range(args.restarts if mode else 1):
                        native.seed(9000 + r)
                        p = native.paar(inst.n_inputs, inst.targets, mode)
                        g = verify(inst, p)
                        if best is None or g < best:
                            best, prog = g, p
                for mode in (0, 1):
                    for r in range(60 if mode else 1):
                        native.seed(9500 + r)
                        p = native.boyar_peralta(inst.n_inputs, inst.targets, mode, 0)
                        g = verify(inst, p)
                        if g < best:
                            best, prog = g, p
                lb = trivial_lower_bound(inst)
                print(f"  {name:24s} n={inst.n_inputs:3d} naive={inst.naive_cost:4d} "
                      f"heuristic={best:3d} trivial_lb={lb:3d}", flush=True)

                k = best - 1
                opt = None
                hist = []
                while k >= lb:
                    t0 = time.time()
                    res = exists_program(inst, k, conf_budget=args.conf_budget)
                    secs = time.time() - t0
                    label = "TIMEOUT" if res.timed_out else ("SAT" if res.sat else "UNSAT")
                    hist.append({"k": k, "result": label, "seconds": round(secs, 2),
                                 "clauses": res.n_clauses})
                    print(f"      k={k:3d}  {label:8s} {secs:9.2f}s  "
                          f"({res.n_clauses:,d} clauses)", flush=True)
                    if res.timed_out:
                        break
                    if res.sat:
                        verify(inst, res.program)
                        best, prog = k, res.program
                        k -= 1
                    else:
                        opt = k + 1
                        break
                else:
                    opt = best
                with out.open("a") as fh:
                    fh.write(json.dumps({
                        "name": name, "dim": dim, "kind": kind,
                        "coeffs": list(coeffs), "modulus": args.modulus,
                        "n": inst.n_inputs, "naive": inst.naive_cost,
                        "heuristic_ub": best, "trivial_lb": lb,
                        "optimal": opt, "proved": opt is not None,
                        "history": hist,
                        "program": prog if opt is not None else None}) + "\n")
                if opt is not None:
                    print(f"      => PROVEN OPTIMAL: {opt} XOR gates", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
