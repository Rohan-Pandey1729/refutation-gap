#!/usr/bin/env python3
"""Re-verify every program stored in a run record, independently of the search."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp.benchmarks import registry
from slp.instance import SLPInstance, verify


def rebuild(name: str) -> SLPInstance | None:
    try:
        return registry.get(name)
    except KeyError:
        pass
    for suite in ("small", "random", "tiny", "ciphers"):
        for inst in registry.suite(suite):
            if inst.name == name:
                return inst
    return None


def main(paths: list[str]) -> int:
    bad = 0
    for p in paths:
        record = json.loads(Path(p).read_text())
        for r in record["results"]:
            inst = rebuild(r["instance"])
            if inst is None:
                print(f"  ?? {r['instance']}: cannot rebuild instance")
                bad += 1
                continue
            if inst.fingerprint() != r["fingerprint"]:
                print(f"  !! {r['instance']}: fingerprint drift "
                      f"({inst.fingerprint()} != {r['fingerprint']})")
                bad += 1
                continue
            prog = [tuple(op) for op in r["program"]]
            try:
                gates = verify(inst, prog)
            except Exception as exc:
                print(f"  !! {r['instance']}/{r['method']}: {exc}")
                bad += 1
                continue
            ok = gates == r["gates"]
            if not ok:
                bad += 1
            print(f"  {'ok' if ok else '!!'} {r['instance']:24s} {r['method']:6s} "
                  f"recorded={r['gates']} recomputed={gates}")
    print(f"\n{'FAILED' if bad else 'ALL VERIFIED'} ({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or
                          [str(p) for p in Path("runs").glob("*.json")]))
