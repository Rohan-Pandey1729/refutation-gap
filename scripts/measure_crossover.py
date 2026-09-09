#!/usr/bin/env python3
"""Measure where a learned oracle could pay: exact-oracle cost per call vs n.

The learned oracle is only worth using where it is CHEAPER than the exact DFS it
replaces. This measures the exact oracle's real cost per call as a function of
instance size, on the query distribution the search actually produces, and
compares it against measured model inference cost.
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


def measure(inst, label):
    native.seed(1)
    native.reset_stats()
    t0 = time.time()
    prog = native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0)
    wall = time.time() - t0
    gates = verify(inst, prog)
    s = native.get_stats()
    calls = max(1, s["oracle_calls"])
    return {
        "instance": label, "n": inst.n_inputs, "gates": gates,
        "wall_s": wall, "oracle_calls": s["oracle_calls"],
        "oracle_nodes": s["oracle_nodes"],
        "nodes_per_call": s["oracle_nodes"] / calls,
        "us_per_call": wall / calls * 1e6,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[8, 10, 12, 14, 16, 18, 20])
    ap.add_argument("--ciphers", nargs="*", default=["aes_mixcolumns", "anubis", "clefia_m1"])
    ap.add_argument("--model", default="models/oracle.joblib")
    ap.add_argument("--out", default="runs/crossover.jsonl")
    args = ap.parse_args()

    rows = []
    print(f"{'instance':22s} {'n':>3s} {'gates':>6s} {'wall_s':>9s} "
          f"{'calls':>12s} {'nodes/call':>12s} {'us/call':>10s}")
    for n in args.sizes:
        r = measure(registry.random_matrix(n, n, 0.5, 0), f"rand_n{n}_d0.5")
        rows.append(r)
        print(f"{r['instance']:22s} {r['n']:3d} {r['gates']:6d} {r['wall_s']:9.3f} "
              f"{r['oracle_calls']:12,d} {r['nodes_per_call']:12.1f} {r['us_per_call']:10.3f}",
              flush=True)
    for name in args.ciphers:
        inst = registry.get(name)
        r = measure(inst, name)
        rows.append(r)
        print(f"{r['instance']:22s} {r['n']:3d} {r['gates']:6d} {r['wall_s']:9.3f} "
              f"{r['oracle_calls']:12,d} {r['nodes_per_call']:12.1f} {r['us_per_call']:10.3f}",
              flush=True)

    # measured model inference cost, same machine
    model_us = None
    if Path(args.model).exists():
        import joblib
        from slp.oracle.features import featurize_batch
        clf = joblib.load(args.model)["model"]
        rng = np.random.default_rng(0)
        added = rng.integers(1, 1 << 20, size=80, dtype=np.uint64)
        xs = rng.integers(1, 1 << 20, size=200_000, dtype=np.uint64)
        bs = rng.integers(0, 5, size=200_000).astype(np.int16)
        t0 = time.time(); X = featurize_batch(20, added, xs, bs); feat_s = time.time() - t0
        t0 = time.time(); clf.predict_proba(X); pred_s = time.time() - t0
        model_us = (feat_s + pred_s) / len(xs) * 1e6
        print(f"\nmodel inference: {model_us:.3f} us/query "
              f"(featurize {feat_s/len(xs)*1e6:.3f} + predict {pred_s/len(xs)*1e6:.3f})")

    if model_us:
        print(f"\n{'instance':22s} {'us/call exact':>14s} {'us/query model':>15s} {'ratio':>8s}  verdict")
        for r in rows:
            ratio = r["us_per_call"] / model_us
            verdict = "model cheaper" if ratio > 1 else "exact cheaper"
            print(f"{r['instance']:22s} {r['us_per_call']:14.3f} {model_us:15.3f} "
                  f"{ratio:8.2f}  {verdict}")

    Path(args.out).write_text("\n".join(json.dumps(r) for r in rows) +
                              (f"\n{json.dumps({'model_us_per_query': model_us})}\n" if model_us else "\n"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
