# VeriCodeGen 2026 submission

**Title:** The Refutation Gap: Certifying Both Halves of an Optimality Claim in
AI-Assisted Program Synthesis

**Venue:** VeriCodeGen @ NeurIPS 2026 — AI for Verifiable Coding.
Non-archival, 4–9 pages, double-blind.
Abstract due **Sept 11**, paper due **Sept 13**, notification Sept 29.

## Build

```bash
cd paper && latexmk -pdf main.tex        # currently 6 pages
python3 make_figs.py                     # regenerates figs/certification.pdf
```

`main.tex` uses a stand-in preamble so it compiles anywhere. To submit, paste
everything between `\begin{document}` and `\end{document}` into the official
`neurips_2026_vericode_workshop` template on Overleaf.

## Before submitting

1. **Compile the Lean certificates and paste the axiom output** into the
   Limitations section (marked in red in the .tex). This is the one blocking item.
   ```bash
   curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
   lean lean/certs/aes_mixcolumns_paar1.lean
   ```
2. **Refresh the numbers.** `runs/certified.jsonl` is still growing; re-run
   `make_figs.py` and update Table 1 from its printed summary.
3. **Double-blind:** no author names, and no repository URL — use an anonymized
   artifact link.
4. Check nothing in the text identifies the authors or institution.

## Claim-to-evidence map

| Claim in paper | Backing file |
|---|---|
| 62/62 refutations verified, 0 disagreements | `runs/certified.jsonl` |
| Proof sizes, solve/check times | `runs/certified.jsonl`, Fig. 1 |
| CaDiCaL proofs rejected by drat-trim | `slp/certified.py` docstring; reproducible via `prove_unsat(..., solver="cadical153")` |
| Four defects caught by verification layers | `docs/verification-log.md` |
| Aggregation double-count + censored statistic | `docs/verification-log.md` (audit section) |
| Published baselines reproduced | `RESULTS.md`, `SOURCES.md` §4 |
| No published lower bound for MDS matrices | `SOURCES.md` §2.2, §6b |
