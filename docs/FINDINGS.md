# Findings

A record of what this project set out to do, what happened, and what survives.
Written to be read by someone deciding whether to continue the work.

## The original thesis

Boyar–Peralta and its descendants are greedy searches wrapped around an exact
distance oracle `g(x)` = fewest currently-available signals XORing to `x`.
Computing `g` is NP-hard and the search calls it millions of times. The plan was
to replace it with a learned estimator, buying orders of magnitude more search
width at the same cost, with correctness guaranteed by a downstream verifier.

**That thesis did not survive measurement. Three separate things went wrong, and
all three are more interesting than the thesis was.**

## 1. The bottleneck is real, but the fix was wrong

Confirmed: BP spends essentially all of its time in the oracle — 3.97M calls on
AES MixColumns at ~3 µs each is the whole 11.9 s runtime.

Refuted: that this makes a learned replacement worthwhile. Measured cost per
oracle call, against measured model inference cost on the same machine:

| instance | n | oracle calls | nodes/call | µs/call (exact) |
|---|---:|---:|---:|---:|
| rand n=16 d0.5 | 16 | 306,327 | 328.6 | 0.937 |
| rand n=18 d0.5 | 18 | 582,291 | 2,224.6 | 7.446 |
| rand n=20 d0.5 | 20 | 1,054,051 | 3,460.4 | 12.061 |
| **aes_mixcolumns** | **32** | **3,970,567** | **976.7** | **3.004** |
| anubis | 32 | 5,645,379 | 654.4 | 2.273 |
| clefia_m1 | 32 | 6,718,881 | 800.6 | 2.844 |

Model inference: **59.56 µs/query** (26.9 featurize + 32.7 sklearn predict).
The exact oracle is cheaper everywhere measured.

**The size of that advantage is uncertain and should be quoted as a range, not a
figure.** Two separate measurements of the same model's inference cost exist —
59.56 µs/query (synthetic queries, n=20 featurization) and 29.04 µs/query (real
search queries, from the training run) — a 2.05× disagreement. Repeated runs of
the same deterministic BP also vary ~1.55× in wall time on this 2-core machine.
Across the project's own recordings the AES ratio spans roughly **9× to 29×**.
The conclusion (exact is cheaper, by a wide margin) is robust; the specific
multiplier is not.

Note also how `µs/call` is computed: total BP wall time divided by oracle calls.
That makes "the oracle is essentially the whole runtime" true **by construction**
rather than by measurement — nothing here isolates oracle time from the rest of
the search. The error runs in the favourable direction (true per-call oracle cost
is lower, so the refutation stands) but the stated evidence does not establish
what it appears to.

A learned per-query replacement would have to cost under ~2 µs. Python
featurization plus sklearn inference is 30× that. A C-compiled small ensemble
might reach ~0.3 µs, leaving perhaps 10× headroom — real, but nothing like the
margin the thesis assumed.

## 2. Structure makes the exact oracle cheap, and random benchmarks hide it

AES MixColumns at n=32 needs **977** DFS nodes per oracle call. A *random* matrix
at n=20 needs **3,460**. The cryptographic matrices — the ones the whole
literature is about — are far easier per call than random matrices two-thirds
their size, because their algebraic structure keeps target distances small.

This matters beyond this project. The n=8..20 random-instance scaling table,
which is the natural thing to measure first, overstates the difficulty of the
real problem by roughly 4× at the sizes that matter. Anyone extrapolating
difficulty from random GF(2) matrices to cipher diffusion layers will be wrong.

## 3. The learned oracle generalises downward, not upward

Trained on one set of instances and tested on another:

| metric | train n=10,12 → test n=8 | train n=8,10,12 → test n=15..20 |
|---|---:|---:|
| ROC AUC | 0.9999 | 0.9824 |
| average precision | 0.9994 (chance 0.0874) | 0.8451 (chance 0.0213) |
| precision @ 90% recall | 0.989 | 0.251 |
| accuracy @0.5 | 0.9979 | 0.9738 |
| constant-"no" baseline | 0.9126 | **0.9787** |

Note the last two rows of the right column: **the model's accuracy is below what
a model that always answered "no" would score.** Average precision of 0.845
against a 0.021 chance rate is a ~40× lift, so the model has learned something
real — but the direction that matters is the weak one, and accuracy would have
hidden that completely.

## 4. The prefilter works, and is prior art

Since `g(x) ≤ popcount(x)`, the condition `popcount(t ⊕ u) ≤ dist[t] − 1` is a
free *sufficient* condition for candidate `u` to reduce target `t`'s distance.
Restricting BP each step to the top-K candidates under that score:

| instance | full BP | K=200 | K=50 | K=20 | K=10 | K=5 |
|---|---:|---:|---:|---:|---:|---:|
| rand n=20 d0.5 | 73 | 73 | 73 | 75 | 75 | 75 |
| aes_mixcolumns | 97 | 97 | 100 | 100 | 101 | 101 |
| **anubis** | **108** | 108 | **106** | 108 | 110 | 112 |

On AES, K=5 gives a 4.8× wall-clock speedup and 11.5× fewer oracle calls for 4
extra gates. On ANUBIS, K=50 *improves* on unrestricted BP by two gates, landing
exactly on the published BP value of 106 — the restriction changes which of
several tied candidates the greedy takes, and on that instance it lands in a
better basin. A portfolio over K and randomized tie-breaks subsequently reached
**105 on ANUBIS**, one better than the published BP figure.

**But this is prior art.** Sun, Yang & Li (ePrint 2025/1493) attack exactly this
bottleneck with an *exact* necessary-and-sufficient criterion — strictly stronger
than a one-sided filter — and report a 200–280× speedup. The original
Boyar–Peralta paper already states the underlying Hamming-weight identity. This
should be positioned as an implementation detail benchmarked against LCB-BP,
never as a new idea.

## 5. What survives: the optimality gap

No published lower bound was found for the XOR count of AES MixColumns or of any
MDS/cipher diffusion matrix. That is an absence-of-evidence statement over four
papers actually checked — Maximov 2019/833, Sun-Yang-Li 2025/1493,
Duval-Leurent 2018/260, Kranz et al. 2017/1151 — not a proof that none exists.

Using SAT (CaDiCaL) to descend from a verified heuristic upper bound until UNSAT:

- distinct instances attempted: **148**
- closed (optimum proved): **121**
- inconclusive (budget exhausted): **27**, of which **11 are provably not optimal**
  (a strictly smaller circuit was found before the timeout)

### The statistic is censored, and the censoring matters

The gap can only be measured on instances the solver **closes**, and closability
is not independent of the gap: a larger gap needs more descent steps, each one a
chance to exhaust the budget. The closed-only rate is therefore biased upward.

On the 121 closed instances the heuristic was exactly optimal 101 times (83.5%),
gap 1 nineteen times, gap 2 once; mean gap 0.17. **But that figure should not be
quoted.** Over all 148 instances attempted, the true exactly-optimal rate is
bounded by

> **68.2% – 79.1%**

(lower bound: assume every inconclusive instance is suboptimal; upper bound:
assume every inconclusive instance except the 11 provably suboptimal ones is
optimal). Mean provable gap on the inconclusive set is **≥ 0.48 gates**, against
0.17 on the closed set — the excluded instances are systematically worse.

### No size trend survives

| n | closed | heuristic exactly optimal | mean gap | mean solve time |
|---:|---:|---:|---:|---:|
| 6 | 51 | 47/51 (92%) | 0.08 | 0.1 s |
| 7 | 50 | 38/50 (76%) | 0.24 | 8.3 s |
| 8 | 18 | 14/18 (78%) | 0.28 | 15.9 s |
| 9 | 2 | 2/2 (100%) | 0.00 | 45.0 s |

An earlier draft of this document claimed a monotone degradation from n=6 to n=8
(93% → 70% → 56%). **That was an artefact of a double-counting bug in the
aggregation script**, which collapsed 21 duplicate records incorrectly and
distorted the per-size split. With the bug fixed the trend is not there: n=8
(78%) is indistinguishable from n=7 (76%), and n=9 is two instances, which says
nothing. The only defensible reading is that the heuristics are near-optimal at
n=6 and somewhat worse by n=7–8, with no resolvable trend beyond that.

### The honest summary

On random GF(2) matrices at n=6–9, the best of Paar1/Paar2/BP/RNBP over hundreds
of restarts is exactly optimal on between 68% and 79% of instances, and where it
is not optimal it is almost always exactly one gate away. Nothing here licenses
extrapolation to n=32.

The SAT method itself is **not** new — Fuhs & Schneider-Kamp (SAT 2010) introduced
exactly this reduction, and Stoffelen (FSE 2016) applied it to linear matrices.
What appears new, on the strength of a bounded literature check, is coverage:
exact g-XOR optima for *random* GF(2) matrices.

## Honest assessment

This is a solid empirical contribution, not a breakthrough. The defensible claims
are:

1. A measured refutation of the learned-oracle idea, with the cost analysis that
   explains why, and the crossover argument for when it could pay.
2. The observation that structured matrices are far easier for the exact oracle
   than random ones, and that random benchmarks therefore mislead.
3. The first systematic measurement of the optimality gap of SLP heuristics.
4. A trivial-but-first lower bound of 32 for AES MixColumns (32 distinct target
   rows each need their own gate in a minimum program), against the best known
   upper bound of 88. The gap is enormous and nobody has closed any of it.

Suitable venue: an arXiv note or a workshop, not a top-tier conference. The
negative results are the most valuable part and should lead, not be buried.

## What we did not do

- Did not beat any record. Best portfolio results are ANUBIS 105 (published BP
  106, best known 98 s-XOR), CLEFIA M1 110 (published BP 111, best known 103),
  AES MixColumns 97 (best known 88). We are competitive with the 2017 BP baseline
  and well short of 2019–2026 methods, which we have not implemented.
- Did not compile the Lean certificates (no toolchain in the working environment).
- Did not implement the s-XOR metric, so several best-known values are not
  directly comparable to our output.
- Did not resolve the AES InvMixColumns anomaly (SOURCES.md 8b).

## 6. Where modern SAT stalls

Fuhs & Schneider-Kamp (SAT 2010) proved a 13-gate 8-input instance optimal and
failed to settle a 21×8 instance at k=22 after 40+ days of solver time. An
independent literature check found no evidence that anyone has revisited that
wall with a modern solver.

Measured here with CaDiCaL, on random density-0.4 instances, asking only the
single decisive question "is there a program with one fewer gate than the best
heuristic found?":

| instance | trivial lb | heuristic ub | k | result | time | clauses |
|---|---:|---:|---:|---|---:|---:|
| rand n=9 s0 | 8 | 14 | 13 | **SAT** | 10.9 s | 66,105 |
| rand n=9 s1 | 9 | 17 | 16 | **SAT** | 9.4 s | 98,619 |
| rand n=10 s0 | 9 | 19 | 18 | **TIMEOUT** (8M conflicts) | 1,863.2 s | 152,377 |
| rand n=10 s1 | 10 | 20 | 19 | **SAT** | 314.3 s | 170,191 |
| rand n=11 s0 | 11 | 24 | 23 | **TIMEOUT** (8M conflicts) | 1,766.0 s | 301,084 |

Two observations.

**The encoding is hard, and getting harder fast with n.** These single decisive
queries answer in ~10 s at n=9, take 314 s or time out at n=10, and time out at
n=11. Note this is *not* a like-for-like comparison with the 2010 wall: Fuhs &
Schneider-Kamp proved **optimality** (an UNSAT answer) on a cipher-derived 21×8
submatrix, whereas these are **SAT** answers on random square matrices. A SAT
answer shows the heuristic was beatable; it proves nothing about optimality. The
two results are not on the same axis and should not be presented as a single
moved frontier.

What can be said: no n=10 instance was ever fully closed in this project, and
n=11 did not answer even the single easiest question. Incremental solver progress
is not going to reach the n=32 cipher matrices.

Density matters as much as size. Among n=9 instances, only density-0.3 ones
closed; every density-0.5 and density-0.7 instance attempted went inconclusive.

**Where the solver answered, it always improved on the heuristic.** Three of the
five calls returned an answer, and all three were SAT — a circuit one gate smaller
than the best heuristic result existed in every case. The other two timed out and
are unknown.

This is a three-instance observation and nothing more. It is also in tension with
§5, where the two n=9 instances that were fully closed showed gap 0. Those are
different instances at a different density (§5's are density 0.3; these are 0.4),
so there is no contradiction — but the n≥9 picture is genuinely unresolved on this
sample, and no general claim about n=9–10 is supportable.

## 7. MDS matrices are out of reach for exact methods

The smallest interesting MDS instances were attempted directly. A k×k MDS matrix
over GF(2⁴) expands to a 4k×4k binary matrix, so k=2 gives n=8 and k=3 gives n=12.
(A 4×4 MDS over GF(4) would also give n=8, but none exists — it would need an MDS
code of length 8 over GF(4), beyond the q+1 = 5 limit.)

| matrix | n | naive | heuristic | **proven optimal** |
|---|---:|---:|---:|---:|
| 2×2 over GF(2⁴), circulant(1,2) | 8 | 10 | 10 | **10** (k=9 UNSAT) |

**This is one matrix, not two.** The run also emitted a `2×2 Hadamard(1,2)` row,
but for a 2×2 matrix the circulant and Hadamard constructions coincide: identical
targets, identical fingerprint `67dc686f30e48098`, identical solver instance. An
earlier draft listed both as separate results. It is a single closed case.

It is also a trivial one: naive equals optimal, so no sharing is possible at all,
and it carries no information about larger matrices.

The 3×3 case (n=12) was launched but **produced no record before the run was
stopped**, so nothing is claimed about it. Given that n=11 random instances did
not answer even a single decisive query, exact optimality for a
cryptographically interesting MDS matrix — the smallest in real use is 4×4 over
GF(2⁴), i.e. n=16 — is far out of reach of this encoding.

This is worth stating plainly because it bounds the whole approach. The gap
between what SAT can close (n≈10) and what the field cares about (n=32, 64) is
not going to be crossed by better solvers or better encodings of this kind.
