# VeriCodeGen 2026 submission

**Title:** The Refutation Gap: Certifying Both Halves of an Optimality Claim in
AI-Assisted Program Synthesis

**Venue (confirmed 2026-09-11 from the CFP):** VeriCodeGen: AI for Verifiable
Coding — NeurIPS 2026 workshop, Atlanta, **12 December 2026**.
Non-archival ("no formally-published proceedings"; accepted papers appear on
OpenReview). **Double-blind.** Main text **4–9 pages** excluding references;
unlimited technical appendices. Template `neurips_2026_vericode_workshop.tex`
with `neurips_2026_vericode.sty` (Overleaf link on the CFP page).
Submission: OpenReview venue `NeurIPS.cc/2026/Workshop/VERICODEGEN`.

Dates (marked *tentative* on the site, AoE): abstract **Sept 11**, paper
**Sept 13**, reviews Sept 27, notification **Sept 29**, camera-ready Oct 14.

**Note the reviewing policy:** the workshop may use LLM-assisted reviewing.
Every submission gets ≥3 reviews, ≥1 written by a human; authors must
acknowledge this at submission time.

## Build

```bash
cd paper
python3 fig_asymmetry.py fig_stack.py fig_records.py fig_anatomy.py fig_certification.py
latexmk -pdf main.tex          # main text 9 pages, references after
```

Each figure script is standalone; `figstyle.py` holds the shared style. All
figures are single-hue and legible in grayscale. `main.tex` uses a stand-in
preamble so it compiles anywhere — to submit, paste everything between
`\begin{document}` and `\end{document}` into the official template.

## Verify before submitting

```bash
python3 scripts/check_paper_numbers.py    # 29 checks against the run records
```

This recomputes every headline number in `main.tex` from
`runs/certification_final.jsonl`, `runs/lean/axioms.txt` and
`runs/layer2_timing.jsonl`, and exits non-zero on any disagreement. It caught a
real error on 2026-09-11 (a check/solve ratio written as 2.8× that is 2.7×).

## Claim → evidence map

| Claim in the paper | Where it comes from |
|---|---|
| 121 optimality results, **121 certified** | `runs/certification_final.jsonl` |
| 111 by independently checked refutation, 10 by counting bound | same, field `route` |
| 0 checker rejections, 0 disagreements | same, field `verdict`; independent re-derivation of the optimum on 84 of 121 in `runs/certified.jsonl` (`agrees_with_previous`, 84/84 true) |
| proof median 1.06 MB / max 301 MB | same |
| solve median 0.18 s / max 160 s; check median 0.24 s / max 440 s | same |
| check/solve median 1.9×, largest proof 2.7× | same |
| instances by size 51/50/18/2 | same, field `n` |
| the four hardest instances all verify | `runs/recheck_resisted.jsonl`; proofs pinned in `runs/proofs/MANIFEST.sha256` |
| 13 Lean certs, 98–121 gates, 5.0–7.6 s, all `[propext]` | `runs/lean/axioms.txt` (timings hand-transcribed — stated in the paper) |
| Figure 4 instance carries **both** halves | `runs/anatomy_instance.json` + `lean/certs/rand_n8_m8_d0.3_s11_optimal_8.lean` |
| Layer 1 = 17.5 µs | measured on the 108-gate AES MixColumns circuit |
| Layer 2 fast 0.02–0.13 s (4/5), full 2.6–4.6 s (5/5) | `runs/layer2_timing.jsonl` |
| Paar baselines 108/121/121/488/481, BP 97 | `SOURCES.md` §4, §2.6; BP mismatches on ANUBIS and CLEFIA M1 reported in the paper |
| record chain, 9 counts 2001–2026 | `SOURCES.md` §2 — every entry VERIFIED against a primary source |
| no g-XOR lower bound for AES MixColumns | `SOURCES.md` §2.2; the sw-XOR class bound that *does* exist is cited (§2.2a–b) |
| CaDiCaL/Glucose indistinguishable | `runs/certified.jsonl`, 75 paired instances |

## Open items before submitting

1. ~~Compile the new Lean certificate.~~ **Done 2026-09-15**, Lean 4.34.0,
   0 errors: `cert` depends on `[propext]`, `gate_count` on nothing. Recorded in
   `runs/anatomy_instance.json`. Every claim in the paper is now backed.
2. **Re-check ePrint** for anything superseding 88 XOR on AES MixColumns
   (last checked 2026-09-11: nothing found, 2026/1481 still v1).
3. Paste the body into the official template and confirm it still fits 9 pages.
4. Decide on the artifact link (anonymous.4open.science, or omit — the repo is
   private and named after the author).
