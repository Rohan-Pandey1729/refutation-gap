#!/usr/bin/env python3
"""Portfolio search: many randomized BP trajectories, varying the prefilter width.

The free candidate prefilter changes which candidate BP picks when several are
tied, so varying K produces genuinely different trajectories rather than just
different tie-breaks. Combined with RNBP's randomization this is a cheap
diversification: on ANUBIS, K=100 reached 106 gates where unrestricted BP
reached 108.

Runs until a wall-clock budget, keeps the best verified circuit per instance,
and records every improvement as it happens so a killed job loses nothing.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.instance import verify
from slp.verify.lean_cert import emit as emit_lean


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instances", nargs="+",
                    default=["anubis", "clefia_m1", "aes_mixcolumns"])
    ap.add_argument("--minutes", type=float, default=60.0)
    ap.add_argument("--ks", type=int, nargs="+", default=[0, 400, 200, 100, 50, 20, 10, 5])
    ap.add_argument("--out", default="runs/portfolio.jsonl")
    ap.add_argument("--best", default="runs/portfolio_best.json")
    args = ap.parse_args()

    deadline = time.time() + args.minutes * 60
    out = Path(args.out)
    best: dict[str, dict] = {}
    if Path(args.best).exists():
        best = json.loads(Path(args.best).read_text())

    rng = random.Random(12345)
    trials = 0
    print(f"portfolio: {args.instances}, budget {args.minutes:.0f} min, K in {args.ks}")
    while time.time() < deadline:
        for name in args.instances:
            if time.time() >= deadline:
                break
            inst = registry.get(name)
            k = rng.choice(args.ks)
            mode = rng.choice([0, 1, 1, 1])          # favour randomized tie-breaks
            seed = rng.randrange(1 << 30)
            native.seed(seed)
            t0 = time.time()
            try:
                prog = (native.boyar_peralta(inst.n_inputs, inst.targets, mode, 0)
                        if k == 0 else
                        native.boyar_peralta_topk(inst.n_inputs, inst.targets, mode, 0, k))
            except Exception as exc:
                print(f"  !! {name} k={k}: {exc}", flush=True)
                continue
            gates = verify(inst, prog)
            elapsed = time.time() - t0
            trials += 1
            rec = {"instance": name, "n": inst.n_inputs, "topk": k, "mode": mode,
                   "seed": seed, "gates": gates, "seconds": elapsed, "ts": time.time()}
            with out.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            prev = best.get(name, {}).get("gates")
            if prev is None or gates < prev:
                best[name] = {**rec, "program": prog}
                Path(args.best).write_text(json.dumps(best, indent=2))
                print(f"  NEW BEST {name}: {gates} gates (k={k}, mode={mode}, "
                      f"seed={seed}, {elapsed:.1f}s)", flush=True)
                try:
                    cert = Path(f"lean/certs/{name}_portfolio_{gates}.lean")
                    emit_lean(inst, prog, cert, method=f"portfolio_k{k}_mode{mode}",
                              run="portfolio")
                except Exception as exc:
                    print(f"     (certificate emit failed: {exc})", flush=True)
    print(f"\n{trials} trials")
    for name, b in sorted(best.items()):
        print(f"  {name:22s} best {b['gates']:5d}  (k={b['topk']}, mode={b['mode']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
