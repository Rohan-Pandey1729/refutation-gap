#!/usr/bin/env python3
"""Collect exactly-labelled training data for a learned distance oracle.

The label is free: it is produced by the exact oracle that BP already runs.
Each record is (step, x, budget, label); the search state for a record is the
program prefix program[:step], from which the added-set A is reconstructed.
"""
from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.instance import apply_program, verify


def collect(inst, mode: int, node_cap: int, seed: int):
    native.seed(seed)
    t0 = time.time()
    prog, records = native.boyar_peralta_logged(
        inst.n_inputs, inst.targets, mode, node_cap)
    gates = verify(inst, prog)
    return prog, records, gates, time.time() - t0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", default="tiny")
    ap.add_argument("--instances", nargs="*", default=None)
    ap.add_argument("--mode", type=int, default=1, help="0=BP, 1=RNBP (more diverse states)")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--node-cap", type=int, default=0)
    ap.add_argument("--out", default="data/oracle")
    args = ap.parse_args()

    insts = ([registry.get(n) for n in args.instances] if args.instances
             else registry.suite(args.suite))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for inst in insts:
        all_steps, all_x, all_b, all_y, all_rep = [], [], [], [], []
        programs = []
        for rep in range(args.repeats):
            prog, records, gates, secs = collect(inst, args.mode, args.node_cap, seed=1 + rep)
            programs.append(prog)
            for (step, x, budget, label) in records:
                all_rep.append(rep); all_steps.append(step)
                all_x.append(x); all_b.append(budget); all_y.append(label)
            print(f"  {inst.name:26s} rep={rep} gates={gates} "
                  f"queries={len(records):>9,d} {secs:6.2f}s", flush=True)
        if not all_x:
            continue
        y = np.array(all_y, dtype=np.int8)
        path = out_dir / f"{inst.name}.npz"
        np.savez_compressed(
            path,
            rep=np.array(all_rep, dtype=np.int32),
            step=np.array(all_steps, dtype=np.int32),
            x=np.array(all_x, dtype=np.uint64),
            budget=np.array(all_b, dtype=np.int16),
            label=y,
            programs=np.array([np.array(p, dtype=np.int32) for p in programs], dtype=object),
            n_inputs=inst.n_inputs,
            targets=np.array(inst.targets, dtype=np.uint64),
            fingerprint=inst.fingerprint(),
        )
        dist = Counter(y.tolist())
        total += len(y)
        print(f"  -> {path}  {len(y):,d} records  "
              f"pos={dist.get(1,0):,d} neg={dist.get(0,0):,d} capped={dist.get(-1,0):,d}")
    print(f"\ntotal records: {total:,d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
