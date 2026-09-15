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

---

## 2026-09-11 — pre-submission audit round

Run against the revised paper draft by two independent subagents (an adversarial
claim auditor with access to the raw run records, and a source re-checker),
under the project's standing rule that no claim ships without a primary source.

### Errors found in our own claims (all now corrected)

5. **A failure tail manufactured by our own harness.** The draft reported that
   4 of 121 instances "resisted certification within a 150 s per-instance cap."
   The auditor re-ran the four DRAT proofs, which were still in `runs/proofs/`.
   **All four verify.** One (`28e392ecbac11b09`, n=9) checks in 83.9 s — inside
   the cap we claimed had excluded it. Its JSONL row reads `"timeout at 123s"`,
   not 150 s: `certify_decisive.py` computes the per-instance allowance as
   `min(cap, deadline - now)`, so it silently inherited the remainder of the
   global `--budget-seconds`. We described a cap we did not apply and then
   reported the artifact as a property of the problem.
   *Fix:* `scripts/merge_certification.py` merges the budgeted sweep with an
   unbudgeted re-run of the four (`runs/recheck_resisted.jsonl`) into
   `runs/certification_final.jsonl`. Result: **121/121 certified, 111 by checked
   refutation, 10 by counting bound, 0 rejected, 0 disagreements.**

6. **"No published lower bound for any MDS diffusion matrix" was false.**
   Venkateswarlu, Kesarwani & Sarkar (ToSC 2022(4):266–290) prove every 4×4 MDS
   matrix over GL(n,𝔽₂) costs ≥ 8n+3 in **sw-XOR**. AES MixColumns is such a
   matrix. The narrower claim — no lower bound on the **g-XOR** count in which
   the record chain is stated — does hold, and those authors list g-XOR lower
   bounds as future work. *Fix:* paper now states the narrow claim and cites the
   paper that would otherwise refute it. See SOURCES.md §2.2a–2.2b.

7. **Layer 2's cost was asserted, not measured — and understated ~3×.** The
   draft said "0.1–1 s per circuit". Measured (`runs/layer2_timing.jsonl`): the
   complete encoding is **2.59–4.58 s** over five cipher matrices; the fast
   encoding the pipeline actually calls is **0.020–0.131 s** but returns
   `unknown` after 120 s on AES InvMixColumns — **4 of 5**. Both numbers and the
   silent failure are now in the paper.

8. **Record-marker bug in the records figure.** `is_rec` was computed as
   `g == min(gg for yy, gg, *_ in PUB if yy <= y)`, so within-year ties resolved
   by value rather than publication date, drawing 103 (Bit-Sliding, CHES 2017)
   and 95 (Banik et al., IWSEC 2019) as *non*-records. Both were records when
   published. Record status is now set explicitly from SOURCES.md §2.

9. **"CaDiCaL is the faster solver" was unsupported.** On 75 paired instances
   Glucose-with-proof and CaDiCaL are 0.4% apart in total solve time, against
   ~1.3× run-to-run variance. Paper now says "indistinguishable at these sizes".

10. **BP reproduction was reported only where it succeeded.** RESULTS.md records
    ANUBIS 108 vs published 106 and CLEFIA M1 110 vs 111. The paper now reports
    both, and flags that attributing them to BP's unspecified tie-breaking is
    itself a natural-language argument.

### Claims re-checked and found correct
121/117→121 counts, all proof/solve/check medians and maxima, the check/solve
ratios, the 13 Lean certificates (98–121 gates, 4.99–7.60 s, all `[propext]`),
correlation +0.36, the 20% dedup inflation, the censored-statistic interval, all
five Paar baselines, the CLEFIA 134→121 correction, and every year and
attribution in the nine-entry record chain.

### Artifacts added
- `runs/recheck_resisted.jsonl` — unbudgeted re-run of the four
- `runs/certification_final.jsonl` — canonical 121-row record, `source` per row
- `runs/layer2_timing.jsonl` — measured Z3 cost, both encodings
- `runs/anatomy_instance.json` — the Figure 4 instance, all three layers
- `lean/certs/rand_n8_m8_d0.3_s11_optimal_8.lean` — first certificate paired
  with a checked refutation for the *same* instance
- `scripts/merge_certification.py`

---

## 2026-09-14 (later) — defect 11, found by a compile, not by our tests

11. **The Lean emitter produced a syntactically invalid namespace for any
    instance whose name contains a dot.** `emit()` built the namespace as
    `"Cert" + name.replace("_", "").capitalize()`, which leaves the '.' of a
    density in place: `rand_n8_m8_d0.3_s11` became
    `namespace CertRandn8m8d0.3s11`. Lean reads '.' as a namespace separator,
    so it opened `CertRandn8m8d0`, failed on the remainder, and failed again on
    the matching `end`.

    **Why nothing caught it.** All 13 certificates compiled on 2026-09-10 were
    cipher matrices (`aes_mixcolumns`, `anubis`, `clefia_m1`), whose names are
    dot-free. Only random instances carry a density in the name, and until
    2026-09-14 no random instance had ever been emitted as a certificate. The
    existing semantic tests (`tests/test_lean_semantics.py`) and the shadow
    evaluator both check what the file *means*, and the meaning was correct:
    Lean elaborated the declarations anyway and `#print axioms` still reported
    `cert` depending only on `[propext]` and `gate_count` depending on none.
    A file can be semantically right and syntactically broken at the same time,
    and we had no test for the second.

    **This is defect (iii) recurring in a case its regression test did not
    cover.** (iii) was line-wrapping inside `(a, b)` tuples, caught by a
    round-trip parse of the *program*. That test reads the gate list back and
    never looks at the surrounding Lean scaffolding, so a broken namespace
    passes it.

    *Fix:* `slp/verify/lean_cert._lean_namespace()` now keeps only alphanumeric
    characters. Cipher namespaces are unchanged (`CertAesmixcolumns`,
    `CertAnubis`, `CertClefiam1`), so the 13 existing certificates remain valid
    and do not need recompiling. `tests/test_lean_syntax.py` adds 17 checks on
    the emitted file as *syntax*: namespaces must be single Lean identifiers,
    every `namespace` must be closed by a matching `end`, and every
    `#print axioms` target must name a declaration the file defines. Verified
    to fail (6 failures) against the pre-fix emitter.

    *Credit:* found by Rohan running `lean` on the certificate, which is the
    first time a certificate for a random instance had ever been compiled.
