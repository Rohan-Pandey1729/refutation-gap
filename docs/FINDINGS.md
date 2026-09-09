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
The exact oracle is cheaper everywhere measured — by 5× at n=20 and **20× on
AES MixColumns**.

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

No published lower bound exists for the XOR count of AES MixColumns or of any
MDS/cipher diffusion matrix — independently re-confirmed against Maximov 2019/833,
Sun-Yang-Li 2025/1493, Duval-Leurent 2018/260 and Kranz et al. 2017/1151.

Using SAT (CaDiCaL) to descend from a verified heuristic upper bound until UNSAT,
**55 instances closed**:

| gap above proven optimum | instances | share |
|---:|---:|---:|
| 0 gates | 38 | 69.1% |
| 1 gate | 17 | 30.9% |

Mean gap **0.31 gates**. The best of Paar1/Paar2/BP/RNBP over hundreds of
restarts is exactly optimal about 70% of the time at n=6..8, and never more than
one gate away.

The SAT method itself is **not** new — Fuhs & Schneider-Kamp (SAT 2010) introduced
exactly this reduction, and Stoffelen (FSE 2016) applied it to linear matrices.
What is new is coverage: exact g-XOR optima for *random* GF(2) matrices, which no
prior work reports, and a systematic measurement of how far the standard
heuristics actually sit above optimal.

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

**The wall has moved, but not far.** Sixteen years of solver progress moves the
frontier from roughly n=8 to roughly n=9–10 on this problem. n=9 settles in ~10 s;
n=10 is erratic (one instance in 314 s, its sibling exhausting an 8M-conflict
budget after half an hour); n=11 did not settle at all. This is a genuinely hard
encoding, and incremental solver improvement is not going to reach the n=32
cipher matrices — a different idea is needed, not a faster solver.

Density matters as much as size: the broad sweep closes n=9 instances at density
0.3–0.5 but goes inconclusive at density 0.7.

**Every SAT call here returned SAT, not UNSAT.** At n=9 and n=10 the best of
Paar1/Paar2/BP/RNBP over hundreds of restarts was *never* optimal — the solver
improved on it every time it answered at all. That is a sharper version of the
optimality-gap result: at n≤8 the heuristics are optimal ~69% of the time, but by
n=9–10 they are leaving gates on the table consistently.

## 7. MDS matrices are out of reach for exact methods

The smallest interesting MDS instances were attempted directly. A k×k MDS matrix
over GF(2⁴) expands to a 4k×4k binary matrix, so k=2 gives n=8 and k=3 gives n=12.
(A 4×4 MDS over GF(4) would also give n=8, but none exists — it would need an MDS
code of length 8 over GF(4), beyond the q+1 = 5 limit.)

| matrix | n | naive | heuristic | **proven optimal** |
|---|---:|---:|---:|---:|
| 2×2 circulant(1,2) over GF(2⁴) | 8 | 10 | 10 | **10** (k=9 UNSAT) |
| 2×2 Hadamard(1,2) over GF(2⁴) | 8 | 10 | 10 | **10** (k=9 UNSAT) |

These are, as far as the literature check could determine, the first
proven-optimal XOR counts for MDS matrices — but they are trivial: naive equals
optimal, so no sharing is possible at all, and the result carries no information
about larger matrices.

The 3×3 case (n=12) did not settle within a 40M-conflict budget, consistent with
the random-instance frontier where n=11 also failed. **Exact optimality for any
cryptographically interesting MDS matrix is far out of reach**: the smallest one
in real use is 4×4 over GF(2⁴), i.e. n=16 with an optimum near 40 gates, several
orders of magnitude beyond where the encoding stalls.

This is worth stating plainly because it bounds the whole approach. The gap
between what SAT can close (n≈10) and what the field cares about (n=32, 64) is
not going to be crossed by better solvers or better encodings of this kind.
