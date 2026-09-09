# Learned search for Shortest Linear Straight-Line Programs over GF(2)

Given a matrix over GF(2), find the **minimum number of XOR gates** computing
every row from the inputs. NP-hard (Boyar–Matthews–Peralta, MFCS 2008). For
essentially every benchmark instance in the literature **the true optimum is
unknown** — there is only a shrinking sequence of upper bounds produced by
successively better hand-designed search heuristics.

Every claim this project makes about the outside world is recorded in
[`SOURCES.md`](SOURCES.md) with its verification status and primary source.
What we run and where the output goes is in [`RUNBOOK.md`](RUNBOOK.md).

## Record history: AES MixColumns (g-XOR)

| gates | source | method |
|---:|---|---|
| 108 | Satoh et al. ASIACRYPT 2001; Banik et al. INDOCRYPT 2016 | architectural |
| 103 | Jean, Moradi, Peyrin, Sasdrich, CHES 2017 | heuristic |
| 97 | Kranz, Leander, Stoffelen, Wiemer, ToSC 2017(4) | Boyar–Peralta |
| 95 | Banik, Funabiki, Isobe, IWSEC 2019 | heuristic |
| 94 | Tan & Peyrin, TCHES 2020(1) | A1/A2 |
| 92 | Maximov, ePrint 2019/833 | dedicated search |
| 91 | Lin, Xiang, Zeng, Zhang, CT-RSA 2021 | framework |
| 89 | Sun, Yang, Li, ePrint 2025/1493 | revisited BP |
| **88** | **Jean, ePrint 2026/1481 (2026)** | **LLM-assisted; no method published** |

Thirty years of progress, entirely from better search heuristics.

**Novelty, stated honestly.** The current record was itself found "with the help
of AI, most specifically models from OpenAI under codex" (the author's own
words). So *"first application of AI to SLP"* is refutable and we do not claim
it. What is absent from that 2-page note — and from the literature generally —
is any **method**: no algorithm, no search procedure, no reproducibility, no
evaluation beyond one matrix. The defensible contribution is the first
systematic, published, reproducible methodology for learned search on SLP.

## Thesis

Boyar–Peralta and its descendants are greedy searches wrapped around an **exact
distance oracle** `g(x)` = fewest currently-available signals XORing to `x`.
Computing `g` is itself NP-hard, and the outer search calls it millions of times.

> Replacing the exact oracle with a learned estimator makes each query
> ~constant-time, buying orders of magnitude more search width within the same
> budget. Because every emitted circuit is exactly verified, a wrong oracle
> costs quality, never correctness.

### The bottleneck, measured

Exact BP on random `n×n` density-0.5 instances:

| n | gates | seconds | oracle calls | oracle DFS nodes | nodes/call |
|---:|---:|---:|---:|---:|---:|
| 8 | 15 | 0.001 | 4,697 | 51,189 | 10.9 |
| 12 | 29 | 0.005 | 46,601 | 2,042,747 | 43.8 |
| 16 | 50 | 0.215 | 306,327 | 100,661,490 | 328.6 |
| 18 | 62 | 2.706 | 582,291 | 1,295,390,666 | 2,224.6 |
| 20 | 73 | 8.032 | 1,054,051 | 3,647,450,974 | 3,460.4 |

Calls grow ~220×; work *per call* grows ~320×. The oracle, not the outer loop,
is what explodes.

Budgeted-oracle frontier at n=20 — what a learned oracle must beat:

| oracle node cap | gates | seconds |
|---|---:|---:|
| exact | 73 | 7.99 |
| 1e4 | 75 | 5.39 |
| 1e3 | 87 | 2.34 |
| 1e2 | 95 | 0.73 |

## Status: reproduction of published baselines

Paar's algorithm is deterministic, so these must match exactly.

| instance | ours | published | source |
|---|---:|---:|---|
| AES MixColumns, Paar1 | **108** | 108 | Kranz et al., ToSC 2017(4), Tab. 3 |
| ANUBIS, Paar1 | **121** | 121 | Xiang et al., ToSC 2020(2), Tab. 1 |
| CLEFIA M1, Paar1 | **121** | 121 | Xiang et al., ToSC 2020(2), Tab. 1 |
| KHAZAD, Paar1 | **488** | 488 | Xiang et al., ToSC 2020(2), Tab. 1 |
| WHIRLPOOL, Paar1 | **481** | 481 | Xiang et al., ToSC 2020(2), Tab. 1 |
| AES MixColumns, Boyar–Peralta | **97** | 97 | Kranz et al., ToSC 2017(4), Tab. 3 |

Naive XOR counts also match Table 3 exactly (152 / 184 / 184 / 208 / 1232 / 840),
and every cipher matrix is validated against diffusion-layer test vectors.

## Two metrics — do not conflate them

- **g-XOR**: arbitrary straight-line program, temporary registers allowed.
- **s-XOR**: sequential/in-place, only `x_i ← x_i ⊕ x_j`, no new registers.

s-XOR is strictly more restrictive, so **every s-XOR program is a valid g-XOR
program** and an s-XOR count is a valid g-XOR upper bound — but not conversely.
This project emits g-XOR programs, so the bar to beat is the minimum over *both*
metrics, which for several instances is the s-XOR figure. Comparing our g-XOR
output only against published g-XOR numbers would understate the bar and produce
a false record claim.

## Verification: three independent layers

| layer | checks | cost |
|---|---|---|
| bitmask verifier | re-executes the program; every target appears as a signal | microseconds |
| symbolic proof (Z3) | `∀x. circuit(x) = Mx` over GF(2) — the whole input space | ~0.1–1 s |
| Lean certificate | kernel-checked, self-contained, no Mathlib | seconds |

The verifiers share no code with the search or with each other, and each has a
negative control: a deliberately corrupted circuit must be rejected. This is not
ceremony — it has already caught four real bugs, listed in
[`docs/verification-log.md`](docs/verification-log.md).

## Plan

1. **Baselines and reproduction** — done, six exact matches
2. **Profile the oracle** — done
3. **Learned oracle** — data pipeline done (labels are free: the exact oracle BP
   already runs produces them; ~1.1M labelled queries from one pass over the
   small suite). Model next.
4. **Wide beam/MCTS search** using the cheap oracle
5. **Records** — target the parametric MDS families and less-attacked matrices
   first, *not* AES MixColumns, which is the most optimised instance in the field
6. **Optimality** via SAT/ILP lower bounds on small GF(2⁴) instances, to *close*
   cases rather than only improve upper bounds. No published lower bound exists
   for any of these matrices — this is the part nobody in the current
   AI-for-mathematics wave is doing.

**Design constraint for step 3:** the oracle's answer is "no" ~96% of the time.
A classifier that always says "no" scores 96% accuracy and is worthless. The
metric is recall on positives at fixed inference budget — a missed positive costs
one extra gate, a false positive is caught by the verifier.

## Layout

```
slp/instance.py          representation + the exact verifier (ground truth)
slp/gf.py                GF(2^k) arithmetic, matrix -> binary expansion
slp/core.c               Paar1/2, Boyar-Peralta, RNBP, distance oracle, instrumentation
slp/native.py            ctypes bindings, auto-rebuild on source change
slp/benchmarks/          cipher matrices, parametric MDS families, random instances
slp/verify/symbolic.py   Z3 proof over the whole input space
slp/verify/lean_cert.py  self-contained Lean 4 certificate emitter
slp/tracking.py          immutable run records; nothing unverified is recorded
scripts/                 run, aggregate, recheck, collect training data
scripts/slurm/           Hyak (klone) submission scripts
lean/certs/              generated certificates: `lean <file>` to check
```

## Ground rules

- **Nothing enters `runs/` unverified.** A failed verification records nothing.
- **Record claims only on `verified=True` instances**, and only against the
  best-known value across *both* metrics.
- **Results from a dirty tree are not publishable.** Every record stores the
  commit and a dirty flag; `aggregate.py` counts them separately.
- **The verifier never imports the search code**, so a bug in search cannot mask
  itself.
- **A numerical check beats a prose argument.** When they disagreed here, the
  prose was wrong — twice.

## Quick start

```bash
python3 -m pytest tests/ -q                    # 34 tests
python3 scripts/run_baselines.py --suite tiny  # end-to-end
python3 scripts/aggregate.py                   # regenerate RESULTS.md
python3 scripts/recheck.py                     # re-verify everything recorded
```
