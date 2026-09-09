#!/usr/bin/env python3
"""Operational comparison: exact vs budgeted vs learned distance oracle.

This is the experiment that matters. Accuracy on held-out queries is a proxy;
what we actually care about is what happens when the oracle is dropped into the
search loop:

    gates produced   (quality)   vs   oracle time   (cost)

All three oracles run inside the SAME outer loop (slp/oracle/search.py), so the
only thing varying is the oracle. Every circuit produced is verified.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.instance import verify
from slp.oracle.features import featurize_batch
from slp.oracle.search import boyar_peralta as bp_pluggable


def exact_oracle(n, added, xs, budgets):
    from slp.native import gval
    al = [int(a) for a in added]
    out = np.zeros(len(xs), dtype=bool)
    for i in range(len(xs)):
        b = int(budgets[i])
        if b < 0:
            continue
        out[i] = gval(n, int(xs[i]), al, b) <= b
    return out


def budgeted_oracle_factory(cap):
    from slp.native import gval

    def fn(n, added, xs, budgets):
        al = [int(a) for a in added]
        out = np.zeros(len(xs), dtype=bool)
        for i in range(len(xs)):
            b = int(budgets[i])
            if b < 0:
                continue
            out[i] = gval(n, int(xs[i]), al, b, node_cap=cap) <= b
        return out
    return fn


def learned_oracle_factory(model_path, threshold):
    import joblib
    bundle = joblib.load(model_path)
    clf = bundle["model"]

    def fn(n, added, xs, budgets):
        if len(xs) == 0:
            return np.zeros(0, dtype=bool)
        X = featurize_batch(n, np.asarray(added, dtype=np.uint64),
                            np.asarray(xs, dtype=np.uint64),
                            np.asarray(budgets, dtype=np.int16))
        return clf.predict_proba(X)[:, 1] >= threshold
    return fn


def run_one(inst, name, oracle):
    t0 = time.time()
    res = bp_pluggable(inst, oracle)
    wall = time.time() - t0
    if not res["solved"]:
        return {"oracle": name, "gates": None, "solved": False, "wall": wall}
    gates = verify(inst, res["program"])
    return {"oracle": name, "gates": gates, "solved": True, "wall": wall,
            "oracle_seconds": res["oracle_seconds"], "queries": res["queries"],
            "steps": res["steps"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[12, 14, 16])
    ap.add_argument("--densities", type=float, nargs="+", default=[0.5])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1])
    ap.add_argument("--model", default="models/oracle.joblib")
    ap.add_argument("--thresholds", type=float, nargs="+", default=[0.5, 0.2, 0.05])
    ap.add_argument("--caps", type=int, nargs="+", default=[1000, 100])
    ap.add_argument("--out", default="runs/oracle_comparison.jsonl")
    args = ap.parse_args()

    have_model = Path(args.model).exists()
    if not have_model:
        print(f"WARNING: {args.model} not found; skipping learned oracle", file=sys.stderr)

    out = Path(args.out)
    rows = []
    hdr = f"{'instance':24s} {'oracle':>16s} {'gates':>6s} {'wall':>9s} {'oracle_s':>9s} {'queries':>10s}"
    print(hdr)
    print("-" * len(hdr))
    for n in args.sizes:
        for d in args.densities:
            for s in args.seeds:
                inst = registry.random_matrix(n, n, d, s)
                # C reference, for sanity
                native.seed(1)
                c_gates = verify(inst, native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0))

                configs = [("exact", exact_oracle)]
                for cap in args.caps:
                    configs.append((f"capped_{cap}", budgeted_oracle_factory(cap)))
                if have_model:
                    for th in args.thresholds:
                        configs.append((f"learned_{th}", learned_oracle_factory(args.model, th)))

                for name, oracle in configs:
                    r = run_one(inst, name, oracle)
                    r.update({"instance": inst.name, "n": n, "density": d, "seed": s,
                              "c_reference_gates": c_gates})
                    rows.append(r)
                    with out.open("a") as fh:
                        fh.write(json.dumps(r) + "\n")
                    g = r["gates"] if r["gates"] is not None else -1
                    print(f"{inst.name:24s} {name:>16s} {g:6d} {r['wall']:9.3f} "
                          f"{r.get('oracle_seconds', 0):9.3f} {r.get('queries', 0):10,d}",
                          flush=True)
                print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
