# Verification log

Record of what was checked, by whom, when, and what it changed.

## 2026-09-09 — external source verification

Three independent verification passes were run against primary sources, with
instructions to report UNCONFIRMED rather than guess, and with news aggregators
(medium, kingy.ai, time.news, glitchwire, besthub, officechai, datastudios,
solidaitech, memesita, forkast) excluded as a basis for any claim.

**Pass A — SLP / XOR-count literature.** 83 tool calls. Sources: IACR ePrint,
ToSC/TCHES, Springer LNCS, NIST.

**Pass B — cipher diffusion matrix definitions.** 112 tool calls. Method was not
prose reading: each candidate matrix was used to rebuild the cipher's reference
lookup tables, compared byte-for-byte against the designers' published tables,
and then run through the full cipher against official test vectors (NESSIE,
RFC 6114, ISO/IEC 10118-3).

**Pass C — AI-for-mathematics motivating claims.** 84 tool calls. Sources:
primary announcements, arXiv, Quanta, and named mathematicians' own posts.

### What the passes changed

| finding | effect |
|---|---|
| AES record chain omitted 91 (CT-RSA 2021) and 89 (ePrint 2025/1493) | Corrected. Citing 94/92 → 88 would have been a stale-baseline error. |
| The 88-XOR record was itself found with LLM assistance (OpenAI codex), per the author | Novelty framing changed from "first AI applied to SLP" (refutable) to "first systematic, published, reproducible methodology". ePrint 2026/1481 must be cited and distinguished. |
| Two incompatible metrics, g-XOR and s-XOR, are routinely conflated | Leaderboard now labels the metric on every published value. Our g-XOR output must be compared against the minimum over both metrics, since s-XOR programs are valid g-XOR programs. |
| CLEFIA M0 and M1 are **Hadamard**, implemented here as circulant | **Code bug fixed.** Confirmed by CLEFIA M1 Paar1 going 134 → 121, matching Xiang et al. exactly. |
| CLEFIA M0 is the same matrix as ANUBIS | Deduplicated; guarded by `test_anubis_equals_clefia_m0`. |
| Whirlpool's 2001 revision changed the S-box; the **2003** revision changed the matrix | Documentation corrected; both matrices added as separate instances. |
| Tan–Peyrin's 94 came from A1/A2, not RNBP (which gives 95); "LocalOpt" is not their algorithm | Citations corrected. |
| 97 for AES should be cited to Kranz et al. 2017, not Boyar–Peralta 2010 | Citation corrected. |
| Fefferman's statements (C)/(D) **permit** a smooth forcing term; (A)/(B) are the ones that set f ≡ 0 | Motivation corrected. An earlier draft had this backwards. |
| Tao made no public comment on OpenAI's Navier–Stokes claim; his "strip-mining" remark predates the announcement by five days | Attribution corrected. |
| No source for Tao criticising "marketing proof points" | **Claim retracted** from this project. |
| The $2M compute figure is a single outlet's number; OpenAI published none, and estimates range to $10–40M | Downgraded to "millions of dollars, no official figure". |
| No published lower bound exists for AES MixColumns XOR count | Recorded as an open item, not a citable number. |

### Errors this project made and corrected

1. **CLEFIA implemented as circulant** — caught by Pass B, confirmed numerically.
2. **Whirlpool transposed.** On reading Pass B's remark that the spec applies
   θ as right-multiplication, the matrix was transposed via a new
   `circulant_right`. Numerical cross-validation then **failed**, and the plain
   circulant **passed**. The prose reasoning was wrong; the test was right. Reverted.
3. **Paar final-phase bug** — the loop rescanned signals it had just created,
   inflating gate counts and occasionally emitting a self-XOR. Caught by the
   independent verifier, not by inspection.
4. **Lean emitter line-wrapping** — split inside `(a, b)` tuples, producing
   malformed Lean. Caught by a round-trip test, not by reading the output.

All four were caught by a check that did not share code with the thing it was
checking. That is the pattern worth keeping.

## Standing verification tasks

Re-check before any submission:

1. Anything on ePrint superseding 88 XOR for AES MixColumns.
2. ToSC/TCHES table and page numbers against typeset journal PDFs (the ePrint
   and journal versions may differ).
3. NESSIE specification PDFs, retrieved on an unrestricted network, for citation.
4. Whether Yuan et al.'s 91 s-XOR for MixColumns implies 91 for InvMixColumns.
5. Whether OpenAI's Lean repo contains `sorry`, custom axioms, or `native_decide`,
   if that work is cited in print.

## 2026-09-09 — internal audit of the overnight run

An adversarial audit was run against the night's write-up, checking every
quantitative claim in `FINDINGS.md` and `README.md` against the raw data in
`runs/`. It found substantive problems, all now corrected:

| finding | correction |
|---|---|
| `aggregate_optimality.py` computed a dedup key and never used it, so any instance appearing in two sweeps was **counted twice**. 125 "closed" was really 104. | Dedup fixed; the script now also asserts that two runs never disagree on an optimum. Regenerated: 148 attempted, 121 closed, 21 duplicates collapsed. |
| **The optimality-gap statistic was censored and the censoring undisclosed.** It was computed only over instances the solver could close, and closability correlates with a small gap. The published 80.8% lay *outside* the interval the full sample supports. | Censoring analysis added to the aggregator. Reported as an interval (68.2%–79.1%), with the 11 provably-suboptimal inconclusive instances counted. |
| The headline "monotone degradation 93% → 70% → 56% from n=6 to n=8" was an artefact of the dedup bug. | Removed. With the bug fixed there is no resolvable trend (92% → 76% → 78%). |
| README claimed 55 instances, 69%, and "never more than one gate above" — all stale, and the last falsified by an existing gap-2 instance. | Rewritten. |
| Two README tables (a budgeted-oracle frontier and a wall-time column) had **no backing data in `runs/`** — they predated the logging harness. | Removed rather than re-stated from memory, with a provenance note. |
| The "20× cheaper" figure spans 9×–29× across the project's own recordings; two model-inference measurements differ by 2.05× and only one was reported. | Restated as a range, with both measurements disclosed. |
| `µs/call` is wall-time ÷ oracle-calls, making "the oracle is the whole runtime" true by construction. | Disclosed in the text. |
| Two MDS "results" were one matrix (2×2 circulant and Hadamard coincide; identical fingerprint). | Corrected to a single closed case. |
| An n=12 MDS timeout was claimed with no record in `runs/`. | Claim withdrawn. |
| The density claim ("closes at 0.3–0.5, inconclusive at 0.7") was false — every density-0.5 n=9 instance also went inconclusive. | Corrected. |
| Portfolio AES best stated as 97; the portfolio's best is 98 (97 is unrestricted BP). | Corrected. |
| README said 34 tests; 51 collect. | Corrected. |

**Known issues left open, deliberately:**

- Every record in `runs/index.jsonl` carries `dirty: true`, violating this
  project's own stated rule that dirty-tree results are not publishable. The
  numbers are reproducible from the committed code, but the rule was not followed
  and the reproduction figures in README technically fall under it.
- `docs/experiment-log.md` claims to record *every* command; several early runs
  (the first optimality sweep, the top-K table, the portfolio, the MDS run)
  predate or bypassed `scripts/logged.py` and are absent.
- **The UNSAT side is unverified.** All three verification layers check circuits,
  i.e. upper bounds. No DRAT proof is emitted or checked for any UNSAT answer, so
  every lower bound rests on trusting CaDiCaL plus the symmetry-breaking argument
  in `slp/optimal.py`'s docstring. The only independent cross-check is a
  brute-force test at n=4 with ≤6 gates, well below the n=6–9 range where results
  are claimed. **This is the most important gap in the project.**
