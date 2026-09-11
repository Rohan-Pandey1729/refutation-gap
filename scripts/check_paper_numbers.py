#!/usr/bin/env python3
"""Recompute every headline number in paper/main.tex from the run records.
Run before any submission. Exits non-zero if anything disagrees."""
import json, re, sys, statistics as st

rows = [json.loads(l) for l in open("runs/certification_final.jsonl")]
ref  = [r for r in rows if r["route"] == "checked refutation"]
free = [r for r in rows if r["route"] == "counting bound"]
ver  = [r for r in ref if r["verdict"] == "VERIFIED"]
pb = [r["proof_bytes"] for r in ver]
ss = [r["solve_seconds"] for r in ver]
cs = [r["check_seconds"] for r in ver]
rat = [c / s for c, s in zip(cs, ss)]
big = max(ver, key=lambda r: r["proof_bytes"])
lean = open("runs/lean/axioms.txt").read()
lrows = re.findall(r"^# (\S+\.lean)\s+gates=\s*(\d+)\s+([\d.]+)s", lean, re.M)
lg = [int(a) for _, a, _ in lrows]; lt = [float(b) for *_, b in lrows]
l2 = [json.loads(l) for l in open("runs/layer2_timing.jsonl")]
fast = [r["fast_seconds"] for r in l2 if r["fast_ok"]]
full = [r["full_seconds"] for r in l2]

CHECKS = [
    ("total results",            len(rows),                121),
    ("checked refutation",       len(ver),                 111),
    ("counting bound",           len(free),                10),
    ("certified",                len(ver) + len(free),     121),
    ("checker rejections",       len(ref) - len(ver),      0),
    ("proof median MB",          round(st.median(pb)/1e6, 2), 1.06),
    ("proof max MB",             round(max(pb)/1e6),       301),
    ("solve median s",           round(st.median(ss), 2),  0.18),
    ("solve max s",              round(max(ss)),           160),
    ("check median s",           round(st.median(cs), 2),  0.24),
    ("check max s",              round(max(cs)),           440),
    ("ratio median",             round(st.median(rat), 1), 1.9),
    ("ratio largest proof",      round(big["check_seconds"]/big["solve_seconds"], 1), 2.7),
    ("n=6",                      sum(1 for r in rows if r["n"] == 6), 51),
    ("n=7",                      sum(1 for r in rows if r["n"] == 7), 50),
    ("n=8",                      sum(1 for r in rows if r["n"] == 8), 18),
    ("n=9",                      sum(1 for r in rows if r["n"] == 9), 2),
    ("n<=7 share",               sum(1 for r in rows if r["n"] <= 7), 101),
    ("lean certs",               len(lrows),               13),
    ("lean gates min",           min(lg),                  98),
    ("lean gates max",           max(lg),                  121),
    ("lean median s",            round(st.median(lt), 1),  5.8),
    ("lean propext lines",       lean.count("[propext]"),  13),
    ("layer2 fast ok",           len(fast),                4),
    ("layer2 fast min s",        round(min(fast), 2),      0.02),
    ("layer2 fast max s",        round(max(fast), 2),      0.13),
    ("layer2 full min s",        round(min(full), 1),      2.6),
    ("layer2 full max s",        round(max(full), 1),      4.6),
]
bad = 0
for name, got, want in CHECKS:
    ok = (got == want)
    bad += (not ok)
    print(f"  {'ok ' if ok else 'FAIL'}  {name:24s} computed={got!r:<12} paper={want!r}")
# correlation
n = len(lg); mg = sum(lg)/n; mt = sum(lt)/n
num = sum((x-mg)*(y-mt) for x, y in zip(lg, lt))
den = (sum((x-mg)**2 for x in lg) * sum((y-mt)**2 for y in lt))**0.5
corr = num/den
ok = abs(corr - 0.36) < 0.005
bad += (not ok)
print(f"  {'ok ' if ok else 'FAIL'}  {'lean correlation':24s} computed={corr:+.4f}    paper=+0.36")
print(f"\n{len(CHECKS)+1} checks, {bad} disagreements")
sys.exit(1 if bad else 0)
