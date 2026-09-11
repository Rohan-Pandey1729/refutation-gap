#!/usr/bin/env python3
"""Merge the budgeted sweep with the unbudgeted re-run of the four instances
that exceeded it, into one canonical certification record.

Inputs   runs/certified_decisive.jsonl   (first sweep, per-instance budget)
         runs/recheck_resisted.jsonl     (re-run of the 4 that exceeded it)
Output   runs/certification_final.jsonl  (121 rows, one per optimality result)

Every row carries `source` so the provenance of each number stays visible.
"""
import json, pathlib

base = [json.loads(l) for l in open("runs/certified_decisive.jsonl")]
recheck = {r["fingerprint"]: r for r in
           (json.loads(l) for l in open("runs/recheck_resisted.jsonl"))}

out = []
for r in base:
    row = dict(fingerprint=r["fingerprint"], n=r["n"], density=r["density"],
               seed=r["seed"], optimal=r["optimal"])
    d = r.get("decisive")
    if d and d.get("verdict") == "VERIFIED":
        row.update(instance=r.get("instance"), k=d["k"], route="checked refutation",
                   verdict="VERIFIED", solver=d["solver"],
                   solve_seconds=d["solve_seconds"], check_seconds=d["check_seconds"],
                   proof_bytes=d["proof_bytes"], proof_lines=d["proof_lines"],
                   n_vars=d["n_vars"], n_clauses=d["n_clauses"],
                   proof_sha256=d.get("proof_sha256"), source="first sweep")
    elif r.get("certified"):
        row.update(instance=r.get("instance"), k=r.get("k"),
                   route="counting bound", verdict="no refutation needed",
                   note=r.get("note"), source="first sweep")
    else:
        n2 = recheck[r["fingerprint"]]
        row.update(instance=n2["instance"], k=n2["k"], route="checked refutation",
                   verdict=n2["verdict"], solver=n2["solver"],
                   solve_seconds=n2["solve_seconds"], check_seconds=n2["check_seconds"],
                   proof_bytes=n2["proof_bytes"], n_vars=n2["n_vars"],
                   n_clauses=n2["n_clauses"],
                   source="re-run without per-instance budget")
    out.append(row)

with open("runs/certification_final.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")

n_ref = sum(1 for r in out if r["route"] == "checked refutation")
n_free = sum(1 for r in out if r["route"] == "counting bound")
bad = [r for r in out if r["route"] == "checked refutation" and r["verdict"] != "VERIFIED"]
print(f"wrote runs/certification_final.jsonl: {len(out)} rows")
print(f"  checked refutation : {n_ref}  (VERIFIED: {n_ref - len(bad)}, other: {len(bad)})")
print(f"  counting bound     : {n_free}")
print(f"  certified          : {n_ref - len(bad) + n_free} / {len(out)}")
