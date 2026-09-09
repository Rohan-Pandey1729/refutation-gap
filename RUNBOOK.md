# Runbook

What gets run, where its output goes, and how someone else reproduces it.

## Verification: three independent layers

A circuit claim in this project has to survive three checks that share no code.
This is deliberate — the search is heuristic and may be wrong, but a *claim* must
not be.

| layer | what it checks | where | cost |
|---|---|---|---|
| 1. Bitmask verifier | re-executes the program from scratch; every target row appears as some signal | `slp/instance.py::verify` | microseconds |
| 2. Symbolic proof | `∀x. circuit(x) = Mx` over GF(2), via Z3; UNSAT of the negation | `slp/verify/symbolic.py` | ~0.1–1 s |
| 3. Lean certificate | kernel-checked `SLP.valid n targets prog = true`, self-contained, no Mathlib | `lean/certs/*.lean` | seconds, run manually |

Layer 1 runs on every search result automatically — `run_baselines.py` records
nothing that fails it. Layer 2 is run before emitting a certificate. Layer 3 is
generated for anything we would publish.

Layer 1 works on the bitmask abstraction. Layer 2 does not: it builds the
circuit and the specification independently and proves them equivalent over the
whole input space, so it catches an error in the abstraction itself. Layer 3
moves the trust base to the Lean kernel.

Negative controls exist for layers 1 and 2 (`tests/test_search.py`,
`tests/test_lean_semantics.py`): a deliberately corrupted circuit must be
rejected. A verifier that never rejects anything is not a verifier.

## Where results are stored

```
runs/<timestamp>-<name>-<id>.json   one immutable record per experiment,
                                    including the FULL emitted program
runs/index.jsonl                    append-only one line per result; safe for
                                    concurrent SLURM array tasks
runs/logs/                          stdout/stderr from batch jobs (gitignored)
data/oracle/*.npz                   labelled distance-oracle queries (gitignored)
lean/certs/*.lean                   machine-checkable certificates
RESULTS.md                          generated leaderboard; never edit by hand
SOURCES.md                          every external claim + verification status
```

Every run record pins: git commit, dirty-tree flag, instance content
fingerprint, RNG seed, full config, hostname, SLURM job id, timings, and the
program itself. A result can therefore be re-checked years later without
re-running the search.

**Commit before running anything you intend to cite.** Results produced from a
dirty tree are recorded with `dirty: true` and counted separately in
`RESULTS.md`; they are not publishable, because the code that produced them is
not recoverable.

## Commands

```bash
# tests (fast) -- matrices, verifiers, search regressions, Lean semantics
python3 -m pytest tests/ -q -m "not slow"

# tests including exact BP on 32-input instances (~10 s)
python3 -m pytest tests/ -q

# baselines on the cipher matrices
python3 scripts/run_baselines.py \
    --instances aes_mixcolumns anubis clefia_m1 khazad whirlpool \
    --methods paar1 paar2 --restarts 300 --name my_run

# regenerate the leaderboard
python3 scripts/aggregate.py

# re-verify every stored program, without re-running any search
python3 scripts/recheck.py

# collect labelled training data for the learned oracle
python3 scripts/collect_oracle_data.py --suite tiny --repeats 2
```

## Checking a Lean certificate

Certificates are self-contained: no Mathlib, no lake, no imports.

```bash
lean lean/certs/aes_mixcolumns_paar1.lean
```

Success is a clean compile. The file ends with `#print axioms cert`; an empty
axiom list means the Lean kernel checked the whole thing. If a certificate needs
`native_decide` instead of `decide` for speed, the axiom list will show
`Lean.ofReduceBool` — that trusts the compiler, and the file states so rather
than hiding it.

> **Status: the certificates in `lean/certs/` were generated but have NOT yet
> been compiled**, because the Lean toolchain host is unreachable from the
> environment they were produced in. Their *semantics* are validated by
> `tests/test_lean_semantics.py`, which re-implements the Lean definitions
> exactly and checks them against the primary verifier, including negative
> controls. That catches a wrong definition; it cannot catch a Lean syntax
> error. **First person with a Lean toolchain should compile them and record the
> result here.**

## On Hyak (klone)

```bash
sbatch scripts/slurm/baselines.sbatch              # one array task per matrix
RESTARTS=2000 sbatch scripts/slurm/sweep.sbatch    # randomized-restart sweep
```

Set `--account=` in both files first (`hyakalloc` lists your allocations).
`--partition=ckpt` is free and preemptable, which is fine here: every run writes
its own immutable record, so a killed job loses at most one task's work.

The C core rebuilds automatically when `slp/core.c` is newer than `slp/libslp.so`,
so a stale shared-filesystem build cannot silently produce old results.

## What has actually been run so far

| date | run | what | outcome |
|---|---|---|---|
| 2026-09-09 | `tiny_baselines` | Paar1/2, BP, RNBP on 27 small random instances | method ordering RNBP ≤ BP < Paar2 ≤ Paar1, matching the literature |
| 2026-09-09 | oracle profiling | exact BP on random n=8..20 | oracle cost is the bottleneck: calls ×220, work-per-call ×320 |
| 2026-09-09 | node-cap ablation | BP with oracle budgets 1e1..1e4 at n=16,18,20 | quality/time frontier established |
| 2026-09-09 | `ciphers_paar_corrected` | Paar1/2, 300 restarts, corrected matrices | **5 exact reproductions** of published Paar1 values |
| 2026-09-09 | `ciphers_bp_corrected` | exact-oracle BP on corrected matrices | AES 97 (matches); CLEFIA M1 110 vs published BP 111 |

## Known gaps

1. Lean certificates generated but not yet compiled (above).
2. Our search emits **g-XOR** programs. Several best-known values are **s-XOR**,
   a stricter metric. s-XOR counts are valid g-XOR upper bounds, so they are
   still the bar — but we cannot claim an s-XOR record without an s-XOR search.
   See `SOURCES.md` §3.
3. `whirlpool_0` has no published comparison value.
4. Instance matrices are validated against derived diffusion-layer vectors, not
   published ones, except AES. See `SOURCES.md` §5.
