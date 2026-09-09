# Learned search for Shortest Linear Straight-Line Programs over GF(2)

## The problem

Given a matrix `M` over GF(2), find the **minimum number of XOR gates** that
computes every row of `M` from the input variables. This is the Shortest Linear
Straight-Line Program (SLP) problem. It is NP-hard, and for essentially every
benchmark instance in the literature **the true optimum is unknown** — only a
shrinking sequence of upper bounds produced by successively better search
heuristics.

The marquee instance is the AES MixColumns matrix. Its record has moved:

| gates | who | year |
|---:|---|---|
| 108 | Paar's greedy algorithm | 1997 |
| 97 | Boyar–Peralta | 2010 |
| 94 | Tan–Peyrin, improved heuristics (TCHES) | 2020 |
| 92 | Maximov, dedicated search | 2019 |
| 88 | eprint 2026/1481 | 2026 |

Every one of those steps came from a **hand-designed search heuristic**. There
is no learning anywhere in the chain.

## The thesis

Boyar–Peralta and its descendants are greedy searches wrapped around an
**exact distance oracle**: `g(x)` = the minimum number of currently-available
signals that XOR to `x`. Computing `g` is itself NP-hard, and the outer search
calls it millions of times. That oracle is the entire cost of the method.

> **Claim.** The bottleneck in BP-style SLP search is the exact distance oracle,
> not the outer greedy. Replacing it with a learned estimator makes each query
> ~constant-time, which buys orders of magnitude more search width and depth
> within the same compute budget. Because every emitted circuit is checked by an
> exact verifier, a wrong oracle can only cost quality — never correctness.

That last sentence is why this problem is a good target: the search may be
heuristic and the network may be wrong, but **a result is a circuit, and a
circuit is checkable in microseconds**. There is no reviewer judgement involved
in whether a record has been beaten.

### Measured evidence for the bottleneck

Exact BP on random `n x n` density-0.5 instances, this repo:

| n | gates | seconds | oracle calls | oracle DFS nodes | nodes/call |
|---:|---:|---:|---:|---:|---:|
| 8 | 15 | 0.001 | 4,697 | 51,189 | 10.9 |
| 12 | 29 | 0.005 | 46,601 | 2,042,747 | 43.8 |
| 16 | 50 | 0.215 | 306,327 | 100,661,490 | 328.6 |
| 18 | 62 | 2.706 | 582,291 | 1,295,390,666 | 2,224.6 |
| 20 | 73 | 8.032 | 1,054,051 | 3,647,450,974 | 3,460.4 |

From n=8 to n=20 the number of oracle *calls* grows ~220x. The work *per call*
grows ~320x. The oracle, not the outer loop, is what explodes.

Capping the oracle's DFS budget trades quality for time, giving the frontier a
learned oracle has to beat (n=20 above):

| oracle node cap | gates | seconds |
|---|---:|---:|
| exact | 73 | 7.99 |
| 1e4 | 75 | 5.39 |
| 1e3 | 87 | 2.34 |
| 1e2 | 95 | 0.73 |

A learned oracle answering at ~1e2 cost with near-exact accuracy would sit far
above this curve.

## Status

Reproductions of published baselines, from this codebase, independently verified:

| instance | method | ours | published | status |
|---|---|---:|---:|---|
| AES MixColumns | Paar1 | **108** | 108 | match |
| AES MixColumns | Boyar–Peralta | **97** | 97 | match |

The AES MixColumns binary matrix is itself validated against four FIPS-197
MixColumns test vectors (`tests/test_aes.py`), so the pipeline is correct end to
end: field arithmetic -> binary expansion -> search -> verification.

## Plan

1. **Baselines and reproduction.** *(done)* Paar1/Paar2, BP, RNBP in C; exact
   verifier in Python; matching published numbers on AES MixColumns.
2. **Profile and characterise the oracle.** *(done for random instances)*
   Establish the quality/compute frontier of the budgeted oracle.
3. **Learned oracle.** *(data pipeline done)* Train a network to answer
   `g(x) <= b?` given the current signal set. Training data is free and exactly
   labelled: the exact oracle that BP already runs produces the labels, so every
   baseline run doubles as data collection (`scripts/collect_oracle_data.py`).
   A single pass over the `tiny` suite yields ~1.1M labelled queries in seconds.

   One property to design around: **the answer is "no" about 96% of the time.**
   A classifier that always predicts "no" scores 96% accuracy and is worthless.
   The metric that matters is recall on the positive class at a fixed inference
   budget, since a missed positive costs exactly one extra gate in the outer
   search and a false positive is caught by the verifier.
4. **Wide search with the cheap oracle.** Beam search / MCTS over the same
   action space, using the learned oracle where BP used the exact one. This is
   where the CircuitBuilder machinery transfers directly.
5. **Records.** Target the parametric MDS families and the less-attacked cipher
   matrices first, not AES MixColumns — the famous instance is the most
   optimised and the worst place to look for slack.
6. **Optimality, if time allows.** SAT/ILP lower bounds on the small GF(2^4)
   instances, to *close* cases rather than only improve upper bounds. This is
   the part nobody in the AI-for-math wave is doing.

## Layout

```
slp/instance.py        problem representation + the exact verifier (ground truth)
slp/gf.py              GF(2^k) arithmetic, matrix -> binary expansion
slp/core.c             Paar1/2, Boyar-Peralta, RNBP, distance oracle, instrumentation
slp/native.py          ctypes bindings, auto-rebuild on source change
slp/benchmarks/        cipher matrices, parametric MDS families, random instances
slp/tracking.py        immutable run records; nothing unverified is ever recorded
scripts/run_baselines.py   run + verify + record
scripts/aggregate.py       regenerate RESULTS.md from runs/index.jsonl
scripts/recheck.py         re-verify stored programs without re-running search
scripts/slurm/             Hyak (klone) submission scripts
```

## Ground rules for this project

- **Nothing enters `runs/` unverified.** `run_baselines.py` calls the verifier
  before recording; a failed verification records nothing.
- **Record claims only on `verified=True` instances.** Benchmark matrices
  transcribed from papers are marked `verified=False` until checked against the
  primary source or test vectors. AES is verified; the others are not yet.
- **Results from a dirty tree are not publishable.** Every record stores the
  commit and a dirty flag; `aggregate.py` counts them separately.
- **The verifier never imports the search code.** It re-executes programs from
  scratch, so a bug in search cannot mask itself.

## Reproducing

```bash
python3 -m pytest tests/ -q                    # matrix + verifier correctness
python3 scripts/run_baselines.py --suite tiny  # end-to-end on small instances
python3 scripts/aggregate.py                   # regenerate RESULTS.md
python3 scripts/recheck.py                     # re-verify everything recorded
```
