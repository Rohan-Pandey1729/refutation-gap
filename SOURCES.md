# Sources and verification status

Every external claim this project relies on is listed here with its verification
status and primary source. Verified 2026-09-09 by three independent
verification passes (see `docs/verification-log.md` for what was run).

Status vocabulary:

- **VERIFIED** — confirmed against a primary source (IACR ePrint, ToSC/TCHES,
  Springer/LNCS, NIST/FIPS, ISO, arXiv, or an author's own statement).
- **PARTIAL** — confirmed in substance, but some detail is uncertain or sources conflict.
- **UNCONFIRMED** — could not be established from a primary source. **Not usable.**
- **REFUTED** — checked and found false. Recorded so the error is not reintroduced.

Aggregator sites (medium.com, kingy.ai, time.news, glitchwire, besthub,
officechai, datastudios, solidaitech, memesita, forkast) are **not acceptable**
as the basis of any claim in this project. They were used only to locate primary
sources.

---

## 1. The problem

| # | Claim | Status | Source |
|---|---|---|---|
| 1.1 | The Shortest Linear Straight-Line Program problem is NP-hard | VERIFIED | Boyar, Matthews, Peralta, *On the Shortest Linear Straight-Line Program for Computing Linear Forms*, MFCS 2008, LNCS 5162:168–179, DOI 10.1007/978-3-540-85238-4_13 |
| 1.2 | Full proof, plus NP-completeness of the decision version over finite fields | VERIFIED | Boyar, Matthews, Peralta, *Logic Minimization Techniques with Applications to Cryptology*, J. Cryptology 26(2):280–312, 2013, DOI 10.1007/s00145-012-9124-7 (Thm 1, Thm 2, §3.1.1, reduction from VERTEX COVER) |
| 1.3 | Cancellation-free algorithms (i.e. Paar's) have approximation ratio ≥ 3/2 | VERIFIED | Same J. Cryptology 2013 paper |

**Citation trap:** do *not* cite Boyar & Peralta, SEA 2010 for NP-hardness. That
paper introduces the BP heuristic, not the hardness result.

## 2. AES MixColumns g-XOR record history

| gates | source | method | status |
|---:|---|---|---|
| 108 | Satoh, Morioka, Takano, Munetoh, ASIACRYPT 2001; Banik, Bogdanov, Regazzoni, *Atomic-AES*, INDOCRYPT 2016 / ePrint 2016/1005 | architectural / hand | VERIFIED |
| 103 | Jean, Moradi, Peyrin, Sasdrich, *Bit-Sliding*, CHES 2017 | heuristic | VERIFIED |
| 97 | Kranz, Leander, Stoffelen, Wiemer, ToSC 2017(4):188–211, ePrint 2017/1151, Tab. 3 | Boyar–Peralta | VERIFIED |
| 95 | Banik, Funabiki, Isobe, *More Results on Shortest Linear Programs*, IWSEC 2019, LNCS 11689:109–128 | heuristic | VERIFIED |
| 94 | Tan & Peyrin, *Improved Heuristics for Short Linear Programs*, TCHES 2020(1):203–230, ePrint 2019/847 | A1 and A2 (depth 6) | VERIFIED |
| 92 | Maximov, *AES MixColumn with 92 XOR gates*, ePrint 2019/833 | dedicated search (depth 6) | VERIFIED |
| 91 | Lin, Xiang, Zeng, Zhang, *A Framework to Optimize Implementations of Matrices*, CT-RSA 2021, LNCS 12704:609–632 | framework | VERIFIED |
| 89 | Sun, Yang, Li, *Revisit the Boyar-Peralta Algorithm…*, ePrint 2025/1493 | revisited BP | VERIFIED |
| **88** | **Jean, *88-XOR Implementation of the AES MixColumns Matrix*, ePrint 2026/1481** | **LLM-assisted; no method published** | **VERIFIED** |

**Correction to an earlier draft of this project:** the chain originally recorded
here was 97 → 94 → 92 → 88, omitting **91 and 89**. That would have been a
stale-baseline error. Corrected 2026-09-09.

Notes on the current record (ePrint 2026/1481, received 2026-07-20, approved
2026-07-23, preprint only, not peer reviewed, 2-page note):

- Author's own words: *"This result has been found with the help of AI, most
  specifically models from OpenAI under codex."*
- No algorithm, search procedure, methodology, reproducibility statement, or
  evaluation beyond the single matrix. Algorithm 1 lists all 88 operations.
- No depth stated, no optimality claim, no correctness-verification claim.

| # | Claim | Status | Note |
|---|---|---|---|
| 2.1 | Anything better than 88 published as of 2026-09-11 | **NONE FOUND** | Re-checked 2026-09-11 for submission. ePrint 2026/1481 is still v1, not withdrawn, not revised (received 2026-07-20, approved 2026-07-23). No count ≤ 87 found in ePrint/ToSC/TCHES/arXiv/Springer. Residual risk: eprint search is robots-disallowed here, so this is absence of evidence. |
| 2.2 | A published *lower bound* on the **g-XOR** count of AES MixColumns | **NONE FOUND** (absence of evidence) | Not in 2026/1481, 2019/833, 2025/1493, Kranz 2017, Xiang 2020, Tan–Peyrin 2020, Yuan 2024, Banik 2019, Lin 2021. Do not cite any figure. |
| 2.2a | A published lower bound on the cost of **MDS matrices as a class** | **VERIFIED — EXISTS.** Earlier entry 2.2 was too broad and is corrected. | Venkateswarlu, Kesarwani, Sarkar, *On the Lower Bound of Cost of MDS Matrices*, IACR Trans. Symmetric Cryptol. **2022(4):266–290**, DOI 10.46586/tosc.v2022.i4.266-290. Proves every 4×4 MDS matrix over GL(n,𝔽₂) has **sw-XOR** cost ≥ 8n+3 (tight: 35 at n=4, 67 at n=8). AES MixColumns is such a matrix, so the bound applies to it. |
| 2.2b | Does 2.2a give a **g-XOR** lower bound for AES MixColumns? | **NO** | sw-XOR is a word-level metric strictly more restrictive than g-XOR, so the bound implies nothing about g-XOR. The paper's own conclusion, verbatim: *"Establishing lower bounds under the metrics s-XOR or g-XOR and also considering depth is an interesting future work."* Confirmed from the CC-BY version of record (Warwick WRAP deposit) 2026-09-11. |
| 2.2c | 91 g-XOR for AES MixColumns is due solely to Lin et al. (CT-RSA 2021) | **PARTIAL — co-credit required** | Yuan, Wu, Shi, Zhang, Zhang, ToSC 2024(2):322–347 independently obtain 91 under the **stricter s-XOR** metric. Sun–Yang–Li Tab. 5 credits both. |
| 2.2d | 108 is attributable to Satoh et al., ASIACRYPT 2001 | **VERIFIED, with nuance** | Satoh et al.'s own Tab. 1 reports **152** (the naive count). Kranz et al. (ePrint 2017/1151) Tab. 3 gives the AES row in full as: Naive **152**, Literature **7 + 96**, Paar1 **108**, Paar2 **108\***, BP **97†**. Their body text reads verbatim, in full: *"An implementation with 108 XORs has been presented in [BBR16a; BBR16b; Sat+01] and an implementation with 103 XORs in [Jea+17]."* The field therefore attributes 108 jointly to Banik–Bogdanov–Regazzoni (Atomic-AES, 2016, two versions) and Satoh et al. Cite it the way the literature does. **Correction 2026-09-14:** an earlier version of this row truncated the quotation at "[Sat+01]" and omitted the Literature column, which suppressed the 103-XOR result reported in the same sentence. Both are restored above. |
| 2.3 | Tan–Peyrin's 94 was achieved by RNBP | **REFUTED** | It was A1 and A2. RNBP gives 95. *"In the case of AES, RNBP is able to yield a 95 XOR circuit."* |
| 2.4 | "LocalOpt" is a Tan–Peyrin algorithm | **REFUTED** | Their algorithms are BP, RSDF, RNBP, A1, A2. |
| 2.5 | 97 should be attributed to Boyar–Peralta (2010) | **REFUTED as a citation** | The *algorithm* is BP 2010; the *number 97 for AES* is Kranz et al. 2017. Cite Kranz et al. |
| 2.6 | 108 is specifically "Paar1" | **VERIFIED, with caveat** | Paar1 = 108 solid (Kranz et al. Tab. 3). Paar2 = 108 now also confirmed, from Kranz Tab. 3 and Xiang Tab. 1 — but Xiang credits its Paar2 column to [KLSW17], so these are two renderings of ONE measurement, not two independent ones. 108 also predates Paar as a hand implementation. Paar2 is not reported at all for KHAZAD or WHIRLPOOL; do not attribute one. |

## 3. Metric distinction (critical)

| # | Claim | Status |
|---|---|---|
| 3.1 | Two metrics are in use: **g-XOR** (arbitrary SLP, temporaries allowed) and **s-XOR** (sequential/in-place, only `x_i ← x_i ⊕ x_j`) | VERIFIED — Xiang et al., ToSC 2020(2) / ePrint 2020/903 |
| 3.2 | s-XOR is strictly more restrictive, so every s-XOR program is a valid g-XOR program and an s-XOR count is a valid g-XOR upper bound | VERIFIED |
| 3.3 | The s-XOR count is invariant under matrix inversion | VERIFIED — Xiang et al. §5.3 |

**This project produces g-XOR programs.** The bar to beat is therefore the
minimum over *both* metrics. Comparing our g-XOR output only against published
g-XOR figures would understate the bar and produce a false record claim.

## 4. Best known values per benchmark instance

| instance | best known | metric | source | status |
|---|---:|---|---|---|
| AES MixColumns | 88 | g-XOR | Jean, ePrint 2026/1481 | VERIFIED |
| AES InvMixColumns | 92 | s-XOR | Xiang et al., ToSC 2020(2), Tab. 4 | VERIFIED |
| ANUBIS | 98 | s-XOR | Xiang et al., ToSC 2020(2), Tab. 1 | VERIFIED |
| CLEFIA M0 | 97 | s-XOR | Yuan et al., ToSC 2024(2):322–347, Tab. 2 | VERIFIED |
| CLEFIA M1 | 103 | s-XOR | Xiang et al., ToSC 2020(2), Tab. 1 | VERIFIED |
| KHAZAD | 366 | s-XOR | Xiang et al., ToSC 2020(2), Tab. 1 | VERIFIED |
| WHIRLPOOL | 417 | g-XOR | Sun, Yang, Li, ePrint 2025/1493, Tab. 5 | VERIFIED |

Published heuristic values used as our reproduction targets (Xiang et al. Tab. 1):

| matrix | Paar1 | Paar2 | BP | BFI19 | Xiang 2020 (s-XOR) |
|---|---:|---:|---:|---:|---:|
| ANUBIS | 121 | 121 | 106 | 102 | 98 |
| CLEFIA M0 | 121 | 121 | 106 | 102 | 98 |
| CLEFIA M1 | 121 | 121 | 111 | 110 | 103 |
| KHAZAD | 488 | — | 507 | 492 | 366 |
| WHIRLPOOL | 481 | — | 465 | 464 | 464 |

**KHAZAD is the one instance where Paar1 (488) beats BP (507).**

**Transcription caveat:** `tosc.iacr.org` and `tches.iacr.org` are
robots.txt-disallowed and direct PDF fetch is blocked from this environment. All
ToSC numbers above come from ePrint versions and IACR CryptoDB/DOAJ metadata,
cross-checked by two independent extractions that agreed. **Page and table
numbers may differ between ePrint and typeset journal versions — verify against
the journal PDF before submission.**

## 5. Benchmark matrix definitions

All validated numerically, not by prose reading. Each was confirmed by an
independent implementation that rebuilt the cipher's reference lookup tables
from the candidate matrix and reproduced official test vectors; our
implementation then reproduced that implementation's diffusion-layer outputs
(`tests/test_ciphers.py`). Two independently written codebases from the same
specifications.

| matrix | field | structure | coefficients | status |
|---|---|---|---|---|
| AES MixColumns | GF(2⁸)/0x11B | circulant | (02,03,01,01) | VERIFIED — FIPS-197 Appendix B, 4 vectors |
| AES InvMixColumns | GF(2⁸)/0x11B | circulant | (0E,0B,0D,09) | VERIFIED — FIPS-197, roundtrip |
| ANUBIS θ | GF(2⁸)/0x11D | **Hadamard**, involutory | (01,02,04,06) | VERIFIED |
| CLEFIA M0 | GF(2⁸)/0x11D | **Hadamard**, involutory | (01,02,04,06) | VERIFIED |
| CLEFIA M1 | GF(2⁸)/0x11D | **Hadamard**, involutory | (01,08,02,0A) | VERIFIED |
| KHAZAD H | GF(2⁸)/0x11D | **Hadamard**, involutory, 8×8 | (01,03,04,05,06,08,0B,07) | VERIFIED |
| WHIRLPOOL (v3.0, 2003) | GF(2⁸)/0x11D | circulant, 8×8 | (01,01,04,01,08,05,02,09) | VERIFIED |
| WHIRLPOOL-0/T (pre-2003) | GF(2⁸)/0x11D | circulant, 8×8 | (01,01,03,01,05,08,09,05) | VERIFIED |

Bit ordering is uniform across all of them: **bit 0 (LSB) = x⁰**, bit 7 = x⁷.
Confirmed in FIPS-197, Barreto's reference code (`if (s2 >= 0x100) s2 ^= 0x11d`),
and Sony's `ClefiaMul2`.

### Errors found and corrected in this project

| # | Error | Correction | How it was caught |
|---|---|---|---|
| 5.1 | CLEFIA M0 and M1 implemented as **circulant** | They are **Hadamard**. Spec row 1 is (2,1,6,4), not (6,1,2,4). | Verification pass; confirmed when corrected CLEFIA M1 Paar1 went 134 → **121**, matching Xiang et al. |
| 5.2 | ANUBIS and CLEFIA M0 counted as two instances | They are the **same matrix** (ePrint 2017/1151 errata). One instance. | Verification pass; now guarded by `test_anubis_equals_clefia_m0` |
| 5.3 | WHIRLPOOL revision history recorded as "2001 changed the matrix" | **2001 changed the S-box; 2003 (v3.0) changed the matrix.** | Verification pass, via designers' reference-code changelog |
| 5.4 | WHIRLPOOL transposed on the basis of a "B = A·C" prose remark | The plain circulant c[(j−i) mod n] is correct. | Numerical cross-validation failed on the transposed version and passed on the original. **Prose reasoning lost to a test.** |

### Provenance caveat

The original NESSIE PDFs for ANUBIS/KHAZAD/WHIRLPOOL
(`cosic.esat.kuleuven.be/nessie/`, `larc.usp.br/~pbarreto/`) were unreachable
from the verification environment. Their *content* is confirmed via the
designers' reference implementations, IACR ePrint, ISO test vectors, and
exhaustive numerical reproduction. **To cite the specification PDFs themselves,
retrieve them on an unrestricted network.**

Only the AES vectors are *published* diffusion-layer-only vectors. For the other
ciphers no such vectors exist publicly; ours were derived and are recorded in
`tests/test_ciphers.py` with this provenance noted.

## 6. Novelty of the approach

| # | Claim | Status |
|---|---|---|
| 6.1 | No published work applies ML / NN / RL / LLM-guided search to the SLP / XOR-count problem specifically | **VERIFIED (nothing found)** across multiple search framings |
| 6.2 | arXiv 2401.12205 (*Retrieval-Guided RL for Boolean Circuit Minimization*) is prior art for SLP | **REFUTED** — it targets ABC logic-synthesis recipe sequencing and AIG area/delay. Does not mention SLP, XOR-count, GF(2), linear layers, or cryptographic matrices. |
| 6.3 | ML-in-crypto ePrint work is adjacent | Clusters in cryptanalysis (neural distinguishers, side-channel) and RL for variational quantum circuits. None address SLP. |

**⚠️ Novelty framing constraint.** The current 88-XOR record (Jean, ePrint
2026/1481) was itself produced with AI assistance. **Verified 2026-09-11 from
the PDF body** (the abstract does not say this; the Acknowledgements do),
verbatim: *"This result has been found with the help of AI, most specifically
models from OpenAI under codex."* The same note states **no** lower bound, **no**
optimality claim, and **no** correctness-verification procedure. Therefore:

- ❌ **Not defensible:** "first application of AI to the SLP problem."
- ✅ **Defensible:** "first systematic, published, reproducible *methodology* for
  learned search on SLP." ePrint 2026/1481 is a 2-page note with no algorithm,
  no search procedure, no reproducibility, and no evaluation beyond one matrix.

This paper **must be cited and explicitly distinguished.**

## 6b. PRIOR ART FOR EXACT / OPTIMAL METHODS — checked 2026-09-09

**This section exists because a novelty check overturned two of this project's
working assumptions. Read it before writing any novelty claim.**

### SAT for the SLP decision problem is NOT new. It is from 2010.

| # | Claim | Status |
|---|---|---|
| 6b.1 | "First SAT/ILP encoding of *is there an SLP with k gates?*" | **REFUTED** |
| 6b.2 | "First proof of optimality for a GF(2) linear circuit" | **REFUTED** |

- **Carsten Fuhs & Peter Schneider-Kamp, "Synthesizing Shortest Linear
  Straight-Line Programs over GF(2) Using SAT", SAT 2010, LNCS 6175:71–84,
  DOI 10.1007/978-3-642-14186-7_8.** Abstract, verbatim: *"we show how to search
  for a circuit of XOR gates with the minimal number of such gates. The approach
  is based on a reduction of the associated decision problem ('Is there a program
  of length k?') to satisfiability of propositional logic."* That is this
  project's encoding, sixteen years earlier. They proved **k=13 optimal** on an
  8-input AES S-box submatrix (k=12 UNSAT in 76.8 s with symmetry breaking, 4+
  days without). On the full 21×8 matrix they found k=23 but **could not** prove
  k=22 UNSAT: solvers ran *"more than 40 days without returning either SAT or
  UNSAT."*
- **Ko Stoffelen, "Optimizing S-box Implementations for Several Criteria using
  SAT Solvers", FSE 2016 / ePrint 2016/198.** This project previously assumed
  Stoffelen covered only *nonlinear* S-boxes. **That was backwards.** He states:
  *"Solving the SLP over GF(2) is equivalent to finding the shortest circuit to
  compute a function using only XOR gates"*, and proved a 7×7 linear matrix
  minimal, failing on a 19×5 one.
- Exhaustive-optimal work in the **s-XOR** metric also exists: Zhao, Wu, Zhang &
  Zhang, ePrint 2016/1118 (provably minimal, hand-picked 5×5 and 6×6), and
  LIGHTER (Jean, Peyrin, Sim, Tourteaux, ToSC 2017(4) / ePrint 2017/101).

### What genuinely remains open

1. **No published lower bound for AES MixColumns or any MDS/cipher diffusion
   matrix.** Independently re-confirmed: absent from Maximov 2019/833,
   Sun-Yang-Li 2025/1493, Duval-Leurent 2018/260, and Kranz et al. 2017/1151.
2. **No published exact g-XOR optima for random GF(2) matrices.** Existing exact
   work is on cipher-derived submatrices (Fuhs, Stoffelen) or in the s-XOR metric
   on hand-picked instances (Zhao, LIGHTER).
3. **No exact g-XOR results above roughly 8 inputs / ~13 gates.** The 2010 paper
   hit a solver wall and, as far as the check could find, nobody has revisited it
   with a modern solver.

**Defensible framing:** scale, metric (g-XOR), and instance class (random / MDS) —
never priority. Fuhs–Schneider-Kamp and Stoffelen must both be cited.

## 6c. PRIOR ART FOR ACCELERATING BOYAR-PERALTA — checked 2026-09-09

| # | Claim | Status |
|---|---|---|
| 6c.1 | "First work to cut BP's distance-oracle cost" | **REFUTED** |

- **Sun, Yang & Li, "Revisit the Boyar-Peralta Algorithm", ePrint 2025/1493.**
  Its stated purpose is exactly this: *"its computational inefficiency presents a
  significant limitation… This paper proposes a novel implementation framework
  for the BP algorithm based on linear combinations, significantly enhancing its
  computational efficiency."* Their **Lemma 1** gives an **exact
  necessary-and-sufficient** condition for whether a candidate pair reduces a
  target's distance — strictly stronger than this project's one-sided sufficient
  condition — and reports a **200–280x** speedup (235.99 s → 0.85 s at 20×20).
- The original **Boyar–Peralta (ePrint 2009/191)** already states both halves of
  the idea: *"Initially, Dist[i] is just one less than the Hamming weight of row
  i"*, and the "distance can only decrease by 1" pruning.
- **Tan–Peyrin** name the bottleneck and leave it: *"Most of the time is spent on
  the exhaustive computation of the Dist vector."*

The specific popcount prefilter used here (`popcount(t XOR u) <= dist[t]-1`
guarantees a reduction, since `g(x) <= popcount(x)`) was not found stated
verbatim in any source, but it follows directly from BP's own initialization
identity and a referee will read it as a consequence, not an observation.
**Position it as an implementation detail, benchmark against LCB-BP
(2025/1493), and never claim priority for reducing BP's distance computations.**

## 7. Motivating context (Navier–Stokes, September 2026)

Used only in the motivation section. Corrections to this project's earlier draft
are marked.

| # | Claim | Status | Note |
|---|---|---|---|
| 7.1 | OpenAI claims finite-time blowup, resolving Fefferman statements (C) and (D) | VERIFIED | openai.com/index/navier-stokes-solution/; Lean repo github.com/openai/NavierStokesAndEuler |
| 7.2 | The result is for the **forced** equations | VERIFIED | *"The fluid has a smooth force applied to it"* |
| 7.3 | Statements (C)/(D) *require* f ≡ 0 | **REFUTED** | Backwards. **(A)/(B)** set f ≡ 0; **(C)/(D) explicitly permit a smooth force f** subject to decay condition (5). The forced result is what (C)/(D) literally ask for. |
| 7.4 | The right criticism | — | Letter of the problem satisfied; spirit contested. Scientific American: *"The Clay problem, as written, is solved. But the Clay problem, as many experts imagine it, lacks the piece that the forcing method relies on."* |
| 7.5 | ~10,000 concurrent agents, ~88 hours, Lean formalization +17 hours, model "significantly more capable than GPT-6 Astra" | VERIFIED | OpenAI's own post |
| 7.6 | ~$2M compute | **PARTIAL — DO NOT STATE AS FACT** | OpenAI publishes no dollar figure. Fortune says ~$2M; Quanta "several million"; VentureBeat a speculative $10–40M retail-equivalent. Write "millions of dollars; no official figure." |
| 7.7 | Builds on Córdoba & Martínez-Zoroa "infinite cascades" | VERIFIED | Per Tao (mathstodon.xyz/@tao/117233527638291447) and Quanta. **OpenAI's post credits no prior technique by name.** |
| 7.8 | Buckmaster (NYU) & Alpöge (Anthropic) published first | VERIFIED in substance | Buckmaster posted 2026-09-08 03:58 UTC; OpenAI later that day. **"~12 hours" is UNCONFIRMED** — write "hours before" or "the same day." |
| 7.9 | Buckmaster *accused* OpenAI of using their work | **REFUTED as worded** | His own statement (cims.nyu.edu/~tristanb/statement.pdf): *"I am not accusing anyone of anything. I am stating what I was told, when, and what was proposed to me."* |
| 7.10 | OpenAI's response | VERIFIED as reported | Bubeck: *"We did not use their prompts or proofs…did not see any of their work."* OpenAI's hedge: *"we cannot rule out that de-identified data derived from their usage of our products helped improve our models."* |
| 7.11 | Proof independently verified by mathematicians | **NO — UNVERIFIED as of 2026-09-09** | Lean repo is public, but no public report of an independent type-check. Nothing retracted. |
| 7.12 | Whether the Lean files contain `sorry`, custom axioms, or `native_decide` | **UNRESOLVED** | Could not inspect. Material to any verification claim. |
| 7.13 | Tao commented on OpenAI's Navier–Stokes claim | **UNCONFIRMED — no such public comment exists** | His praise (mathstodon 117233527638291447) is for **Buckmaster/Alpöge**. Do not attribute OpenAI commentary to him. |
| 7.14 | Tao's "strip-mining" quote is a reaction to the OpenAI announcement | **REFUTED** | Dated 2026-09-03, five days *before*. Genuine quote, wrong context. |
| 7.15 | Tao criticised companies for using math as "marketing proof points" | **UNCONFIRMED — no source** | **Retracted from this project's earlier draft.** His criticism is ecosystem contamination, non-disclosure of negative results, and lack of process transparency. |

Tao's genuine and citable position (mathstodon 117207856734787448, 2026-09-03):
*"Prematurely solving the problem by purely AI-powered methods — particularly
without full transparency into the solution process — can contaminate this
process to the point where it actually becomes a net negative for the progress
of mathematics as a whole."*

## 8. Comparable AI-for-math systems

| # | Claim | Status |
|---|---|---|
| 8.1 | PackingStar (arXiv 2511.13391) improved kissing-number bounds in dims 25–31 and dim 13 (beating the 1130-sphere 1971 construction) | VERIFIED |
| 8.2 | Its authors name lack of rigorous optimality proof as a limitation | VERIFIED — *"machine discovery does not replace proof. The structures proposed by PackingStar require rigorous certification through linear programming, semidefinite programming, symmetry analysis and computer-assisted proof."* Nuance: they do claim optimality *under natural inner products*, i.e. within constrained configuration spaces. |
| 8.3 | ThetaEvolve (arXiv 2511.23473): new best-known bounds on circle packing (n=26, 2.63598308) and the first autocorrelation inequality (1.503133), using DeepSeek-R1-0528-Qwen3-8B on 8×A100 | VERIFIED |
| 8.4 | Erdős database counts | **PARTIAL — sources conflict.** Best defensible: "over 1,100 catalogued problems, ~565 solved and ~650 open as of August 2026 (Quanta)." A live site fetch returned 617/171, which contradicts the site's own Aug-2025 retrospective of 1,135 and is treated as stale. |

## 8b. Open anomaly: AES InvMixColumns

Our exact-oracle Boyar-Peralta produces a **verified 121-gate** circuit for AES
InvMixColumns. The value attributed to BP for that matrix in the verification
pass was ~155 (Tan & Peyrin), which would make our result better by 34 gates.

**This is recorded as an anomaly, not a claim.** Either reading is possible:

- our BP genuinely does better on this instance (the matrix is dense -- 472 ones,
  naive 440 -- so there is far more sharing available than in MixColumns); or
- the ~155 figure is for a different matrix, orientation, or metric; the
  verification pass explicitly flagged inconsistent extractions from that table.

What *is* established: the InvMixColumns matrix here is correct
(`inv(mix(x)) == x` verified on FIPS-197 vectors, `tests/test_aes.py`), the
circuit passes the bitmask verifier, and it is 121 gates. The published
comparison value is unverified.

**Before this is mentioned anywhere: read Tan & Peyrin's table in the typeset
journal PDF and confirm what matrix and metric the ~155 refers to.** Best known
for this matrix remains 92 (s-XOR, Xiang et al.), which we are nowhere near.

## 9. Open items to re-check before submission

1. Re-check ePrint for anything superseding 88 XOR on AES MixColumns.
2. Verify ToSC/TCHES table and page numbers against typeset journal PDFs.
3. Retrieve the NESSIE specification PDFs on an unrestricted network for citation.
4. Confirm whether Yuan et al.'s 91 s-XOR MixColumns implies 91 for InvMixColumns
   (follows from metric inversion-invariance, but not stated in the source).
5. Inspect OpenAI's Lean repo for `sorry` / custom axioms if item 7 is cited in print.
6. Resolve the AES InvMixColumns anomaly in §8b against the typeset Tan-Peyrin table.
7. Compile the generated Lean certificates and record the axiom lists.
