#!/usr/bin/env python3
"""Certify the decisive refutation for each already-closed instance.

The optimality claim is a pair: a verified circuit of size m, and a checked
refutation at k = m-1. The circuit half is already established and stored. This
script certifies only the second half, which is the part that was uncertified --
one decisive UNSAT query per instance, rather than re-deriving the optimum.

That is both faster and a more faithful rendering of the claim: we are not
re-solving, we are supplying the missing certificate.
"""
from __future__ import annotations

import argparse, json, resource, subprocess, sys, time
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp.benchmarks import registry
from slp.certified import prove_unsat
from slp.optimal import trivial_lower_bound


def remaining(sources, out, max_n, min_n=0):
    have = set()
    if Path(out).exists():
        have = {json.loads(l)["fingerprint"]
                for l in Path(out).read_text().splitlines() if l.strip()}
    seen, todo = set(), []
    for src in sources:
        f = Path(src)
        if not f.exists():
            continue
        for l in f.read_text().splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            if not r.get("proved") or r["fingerprint"] in seen:
                continue
            seen.add(r["fingerprint"])
            if r["fingerprint"] not in have and min_n <= r["n"] <= max_n:
                todo.append(r)
    todo.sort(key=lambda r: (r["n"], r["density"], r["seed"]))
    return todo


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="+",
                    default=["runs/optimal_results.jsonl", "runs/optimal_broad.jsonl",
                             "runs/optimal_more.jsonl"])
    ap.add_argument("--out", default="runs/certified_decisive.jsonl")
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--min-n", type=int, default=0,
                    help="target the larger instances first; they are the ones that "
                         "extend the certified range rather than thicken it")
    ap.add_argument("--budget-seconds", type=float, default=480)
    ap.add_argument("--per-instance-seconds", type=float, default=180,
                    help="cap on one instance; exceeding it records the instance as "
                         "resisting certification and moves on, rather than stalling "
                         "the run behind a single hard case")
    ap.add_argument("--mem-limit-gb", type=float, default=5.0)
    ap.add_argument("--worker", default="")
    args = ap.parse_args()

    if args.worker:
        cap = int(args.mem_limit_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
        n, dens, seed, opt = json.loads(args.worker)
        inst = registry.random_matrix(n, n, dens, seed)
        lb = trivial_lower_bound(inst)
        k = opt - 1
        if k < lb:
            print(json.dumps({"fingerprint": inst.fingerprint(), "instance": inst.name,
                              "n": n, "density": dens, "seed": seed, "optimal": opt,
                              "k": k, "certified": True, "verdict": "no refutation needed",
                              "note": "optimum equals the free counting lower bound"}))
            return 0
        r = prove_unsat(inst, k)
        rec = asdict(r) | {"program": None}
        print(json.dumps({"fingerprint": inst.fingerprint(), "instance": inst.name,
                          "n": n, "density": dens, "seed": seed, "optimal": opt,
                          "k": k, "certified": r.verdict == "VERIFIED",
                          "verdict": r.verdict, "decisive": rec}))
        return 0

    todo = remaining(args.sources, args.out, args.max_n, args.min_n)
    print(f"{len(todo)} decisive refutations to certify; budget {args.budget_seconds:.0f}s")
    print(f"{'instance':26s} {'k':>4s} {'solve_s':>8s} {'proof_MB':>9s} {'check_s':>8s} {'verdict':>16s}")
    deadline = time.time() + args.budget_seconds
    done = fail = 0
    for row in todo:
        if time.time() >= deadline:
            print("-- budget exhausted --")
            break
        payload = json.dumps([row["n"], row["density"], row["seed"], row["optimal"]])
        left = max(30, min(args.per_instance_seconds, deadline - time.time()))
        try:
            proc = subprocess.run(
                [sys.executable, __file__, "--worker", payload,
                 "--mem-limit-gb", str(args.mem_limit_gb)],
                capture_output=True, text=True, timeout=left)
        except subprocess.TimeoutExpired:
            rec = {"fingerprint": row["fingerprint"], "n": row["n"],
                   "density": row["density"], "seed": row["seed"],
                   "optimal": row["optimal"], "certified": False,
                   "verdict": f"timeout at {left:.0f}s"}
            fail += 1
            print(f"{row['fingerprint'][:26]:26s} {'-':>4s} {'-':>8s} {'-':>9s} {'-':>8s} "
                  f"{'timeout':>16s}", flush=True)
            with Path(args.out).open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            continue
        line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
        if proc.returncode != 0 or not line.startswith("{"):
            reason = "memory limit" if ("MemoryError" in proc.stderr or proc.returncode == -9) \
                     else f"exit {proc.returncode}"
            rec = {"fingerprint": row["fingerprint"], "n": row["n"],
                   "density": row["density"], "seed": row["seed"],
                   "optimal": row["optimal"], "certified": False, "verdict": reason,
                   "stderr": proc.stderr[-300:]}
            fail += 1
            print(f"{rec['fingerprint'][:26]:26s} {'-':>4s} {'-':>8s} {'-':>9s} {'-':>8s} "
                  f"{reason:>16s}", flush=True)
        else:
            rec = json.loads(line)
            d = rec.get("decisive")
            done += rec["certified"]
            if not rec["certified"]:
                fail += 1
            if d:
                print(f"{rec['instance']:26s} {rec['k']:4d} {d['solve_seconds']:8.1f} "
                      f"{d['proof_bytes']/1e6:9.1f} {d['check_seconds']:8.1f} "
                      f"{rec['verdict']:>16s}", flush=True)
            else:
                print(f"{rec['instance']:26s} {rec['k']:4d} {'-':>8s} {'-':>9s} {'-':>8s} "
                      f"{rec['verdict']:>16s}", flush=True)
        with Path(args.out).open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
    print(f"\ncertified {done}, failed/inconclusive {fail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
