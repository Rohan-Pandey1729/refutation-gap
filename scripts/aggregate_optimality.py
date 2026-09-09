#!/usr/bin/env python3
"""Aggregate every SAT optimality proof into a summary table for RESULTS.md."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO = Path(__file__).resolve().parent.parent
SOURCES = ["runs/optimal_results.jsonl", "runs/optimal_broad.jsonl",
           "runs/optimal_more.jsonl"]


def main() -> int:
    # Deduplicate by instance fingerprint. The same instance is re-run across
    # sweeps; counting it twice inflates every statistic below. Prefer a PROVED
    # record over an inconclusive one for the same instance.
    by_fp: dict[str, dict] = {}
    dupes = 0
    for src in SOURCES:
        p = REPO / src
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            fp = r["fingerprint"]
            if fp in by_fp:
                dupes += 1
                prev = by_fp[fp]
                if prev["proved"] and r["proved"]:
                    assert prev["optimal"] == r["optimal"], (
                        f"two runs disagree on the optimum for {r['instance']}: "
                        f"{prev['optimal']} vs {r['optimal']}")
                if r["proved"] and not prev["proved"]:
                    by_fp[fp] = r
                continue
            by_fp[fp] = r
    rows = list(by_fp.values())

    proved = [r for r in rows if r["proved"]]
    unproved = [r for r in rows if not r["proved"]]

    # Censoring analysis. The gap statistic is computed only over instances the
    # solver could CLOSE, and closability is not independent of the gap: a larger
    # gap needs more descent steps, each a chance to exhaust the budget. So the
    # closed-only rate is biased upward and must be reported with bounds.
    #
    # For an inconclusive instance stalled at k, every larger k' returned SAT, so
    # a circuit of size min(SAT k) exists and the gap is provably >= ub - that.
    provably_suboptimal = 0
    inconclusive_lb_gaps = []
    for r in unproved:
        sat_ks = [h["k"] for h in r.get("history", []) if h.get("sat")]
        if sat_ks:
            lb_gap = r["heuristic_ub"] - min(sat_ks)
            inconclusive_lb_gaps.append(lb_gap)
            if lb_gap > 0:
                provably_suboptimal += 1
        else:
            inconclusive_lb_gaps.append(0)

    out = ["# Exact optimality results", "",
           "Proven-optimal g-XOR counts for small GF(2) matrices, obtained by SAT",
           "(CaDiCaL) descending from a verified heuristic upper bound until UNSAT.",
           "",
           "**Prior art.** The SAT-for-SLP method is Fuhs & Schneider-Kamp, SAT 2010;",
           "Stoffelen (FSE 2016) applied it to linear matrices. What is new here is",
           "coverage: exact g-XOR optima for *random* GF(2) matrices, which the",
           "existing exact work (cipher-derived submatrices, or the s-XOR metric on",
           "hand-picked instances) does not cover. See SOURCES.md section 6b.", "",
           f"- distinct instances attempted: **{len(rows)}**",
           f"- closed (optimum proved): **{len(proved)}**",
           f"- inconclusive (conflict budget exhausted): **{len(unproved)}**",
           f"- duplicate records collapsed: **{dupes}**", ""]

    n_all = len(rows)
    gap0_closed = sum(1 for r in proved if r["heuristic_ub"] == r["optimal"])
    lo = gap0_closed / n_all
    hi = (gap0_closed + len(unproved) - provably_suboptimal) / n_all
    out += ["## Censoring: read this before quoting any percentage", "",
            "The gap below is measured **only on instances the solver could close**,",
            "and closability is not independent of the gap — a larger gap needs more",
            "descent steps, each one a chance to exhaust the conflict budget. The",
            "closed-only rate is therefore biased upward.", "",
            f"- of the {len(unproved)} inconclusive instances, **{provably_suboptimal}** are",
            "  *provably* not optimal (a strictly smaller circuit was found before the timeout)",
            f"- over all {n_all} attempted instances, the true exactly-optimal rate is",
            f"  bounded by **{lo:.1%} - {hi:.1%}**",
            f"- mean provable lower bound on the gap for inconclusive instances: "
            f"**>= {sum(inconclusive_lb_gaps)/max(1,len(inconclusive_lb_gaps)):.2f} gates**",
            "",
            "Quote the interval, not the closed-only figure.", ""]

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
