#!/usr/bin/env python3
"""Aggregate every SAT optimality proof into a summary table for RESULTS.md."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO = Path(__file__).resolve().parent.parent
SOURCES = ["runs/optimal_results.jsonl", "runs/optimal_broad.jsonl"]


def main() -> int:
    rows = []
    seen = set()
    for src in SOURCES:
        p = REPO / src
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            key = (r["fingerprint"], r.get("optimal"), r["proved"])
            if r["fingerprint"] in seen and not r["proved"]:
                continue
            seen.add(r["fingerprint"])
            rows.append(r)

    proved = [r for r in rows if r["proved"]]
    unproved = [r for r in rows if not r["proved"]]

    out = ["# Exact optimality results", "",
           "Proven-optimal g-XOR counts for small GF(2) matrices, obtained by SAT",
           "(CaDiCaL) descending from a verified heuristic upper bound until UNSAT.",
           "",
           "**Prior art.** The SAT-for-SLP method is Fuhs & Schneider-Kamp, SAT 2010;",
           "Stoffelen (FSE 2016) applied it to linear matrices. What is new here is",
           "coverage: exact g-XOR optima for *random* GF(2) matrices, which the",
           "existing exact work (cipher-derived submatrices, or the s-XOR metric on",
           "hand-picked instances) does not cover. See SOURCES.md section 6b.", "",
           f"- instances closed: **{len(proved)}**",
           f"- inconclusive (conflict budget exhausted): **{len(unproved)}**", ""]

    gaps = Counter(r["heuristic_ub"] - r["optimal"] for r in proved)
    total = sum(gaps.values())
    out += ["## How far are the standard heuristics from optimal?", "",
            "The upper bound is the best of Paar1, Paar2, Boyar-Peralta and RNBP",
            "(hundreds of randomized restarts). The gap is that value minus the",
            "proven optimum.", "",
            "| gap (gates above optimum) | instances | share |", "|---:|---:|---:|"]
    for g in sorted(gaps):
        out.append(f"| {g} | {gaps[g]} | {gaps[g]/total:.1%} |")
    mean_gap = sum(g * c for g, c in gaps.items()) / max(1, total)
    out += ["", f"Mean gap: **{mean_gap:.2f} gates**. The heuristics are exactly optimal "
            f"on **{gaps.get(0,0)}/{total}** of the instances closed here "
            f"({gaps.get(0,0)/max(1,total):.0%}), and never worse than "
            f"{max(gaps) if gaps else 0} gate(s) above optimum at these sizes.", ""]

    bysize = defaultdict(lambda: {"n": 0, "gap0": 0, "gapsum": 0, "secs": 0.0})
    for r in proved:
        b = bysize[r["n"]]
        b["n"] += 1
        g = r["heuristic_ub"] - r["optimal"]
        b["gap0"] += (g == 0)
        b["gapsum"] += g
        b["secs"] += r["seconds"]
    out += ["## By instance size", "",
            "| n | closed | heuristic optimal | mean gap | mean solve time |",
            "|---:|---:|---:|---:|---:|"]
    for n in sorted(bysize):
        b = bysize[n]
        out.append(f"| {n} | {b['n']} | {b['gap0']}/{b['n']} | "
                   f"{b['gapsum']/b['n']:.2f} | {b['secs']/b['n']:.1f} s |")
    out.append("")

    out += ["## Full results", "",
            "| instance | naive | heuristic | via | **optimal** | gap | solve time |",
            "|---|---:|---:|---|---:|---:|---:|"]
    for r in sorted(proved, key=lambda r: (r["n"], r["density"], r["seed"])):
        g = r["heuristic_ub"] - r["optimal"]
        out.append(f"| {r['instance']} | {r['naive']} | {r['heuristic_ub']} | "
                   f"{r['heuristic']} | **{r['optimal']}** | {g:+d} | {r['seconds']:.1f} s |")
    if unproved:
        out += ["", "## Inconclusive", "",
                "Conflict budget exhausted. Neither SAT nor UNSAT, so these establish",
                "nothing and are recorded only for completeness.", "",
                "| instance | naive | heuristic | stalled at k |", "|---|---:|---:|---:|"]
        for r in sorted(unproved, key=lambda r: (r["n"], r["seed"])):
            out.append(f"| {r['instance']} | {r['naive']} | {r['heuristic_ub']} | "
                       f"{r.get('inconclusive_at')} |")
    out.append("")

    (REPO / "docs" / "OPTIMALITY.md").write_text("\n".join(out))
    print("\n".join(out[:40]))
    print(f"\n... wrote docs/OPTIMALITY.md ({len(proved)} closed, {len(unproved)} inconclusive)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
