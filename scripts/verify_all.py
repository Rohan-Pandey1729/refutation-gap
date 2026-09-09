#!/usr/bin/env python3
"""Run the symbolic (Z3) verifier over every program stored in runs/.

This is the heavyweight check: for each recorded circuit it proves
    forall x. circuit(x) = M x   over GF(2)
rather than relying on the bitmask abstraction the search itself uses.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp.benchmarks import registry
from slp.instance import verify
from slp.verify.symbolic import SymbolicVerificationError, verify_symbolic_fast


def rebuild(name):
    try:
        return registry.get(name)
    except KeyError:
        pass
    for suite in ("small", "random", "tiny", "ciphers"):
        for inst in registry.suite(suite):
            if inst.name == name:
                return inst
    return None


def main(paths):
    bad = 0
    seen = 0
    for p in paths:
        record = json.loads(Path(p).read_text())
        for r in record["results"]:
            inst = rebuild(r["instance"])
            if inst is None:
                print(f"  ?? {r['instance']}: cannot rebuild"); bad += 1; continue
            if inst.fingerprint() != r["fingerprint"]:
                print(f"  !! {r['instance']}: fingerprint drift"); bad += 1; continue
            prog = [tuple(op) for op in r["program"]]
            seen += 1
            t0 = time.time()
            try:
                verify(inst, prog)
                verify_symbolic_fast(inst, prog)
            except (SymbolicVerificationError, AssertionError, ValueError) as exc:
                print(f"  !! {r['instance']:22s} {r['method']:6s} {r['gates']:5d}  {exc}")
                bad += 1
                continue
            print(f"  ok {r['instance']:22s} {r['method']:6s} {r['gates']:5d} gates  "
                  f"proved over all 2^{inst.n_inputs} inputs  ({time.time()-t0:.2f}s)")
    print(f"\n{seen} circuits checked, {bad} failure(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or sorted(str(p) for p in Path("runs").glob("*.json"))))
