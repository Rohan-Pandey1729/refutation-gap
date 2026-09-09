"""Proof-carrying optimality: DRAT certificates for the refutation side.

WHY THIS EXISTS
---------------
An optimality claim has two halves with very different verification stories.

  upper bound  "a circuit of size m exists"      -> exhibit it; re-execute it;
                                                    prove equivalence in Z3;
                                                    emit a Lean certificate.
  lower bound  "no circuit of size m-1 exists"   -> a SAT solver said UNSAT.

The first half is checkable by anyone in microseconds. The second is an
unaudited assertion by a 30k-line C program. Our own internal audit flagged this
as the single largest gap in the project: 121 optimality claims rested on
untrusted UNSAT answers.

This module closes it. Every decisive UNSAT call emits a DRAT proof, which is
checked by drat-trim -- a separate, third-party implementation that shares no
code with the solver that produced it. An optimality result is then a PAIR of
independently checkable objects:

    (verified circuit of size m,  checked DRAT refutation at k = m-1)

SOLVER NOTE
-----------
CaDiCaL is the faster solver in this pipeline, but the proof PySAT extracts from
it is not accepted by drat-trim (`s NOT VERIFIED`, "no conflict") even with an
explicit terminating empty clause appended. Glucose 4.2's proofs verify. We
therefore use Glucose for proof-carrying runs and report the cost of that choice
rather than hiding it -- at the instance sizes here Glucose was in fact the
faster of the two, but that is not guaranteed to hold as instances grow.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pysat.formula import CNF
from pysat.solvers import Cadical153, Glucose42

from .instance import SLPInstance, verify
from .optimal import _build, trivial_lower_bound

REPO = Path(__file__).resolve().parent.parent
DRAT_TRIM = REPO / "tools" / "drat-trim" / "drat-trim"

SOLVERS = {"glucose42": Glucose42, "cadical153": Cadical153}


@dataclass
class ProofResult:
    k: int
    sat: bool
    solver: str
    solve_seconds: float
    n_vars: int
    n_clauses: int
    proof_lines: int = 0
    proof_bytes: int = 0
    cnf_bytes: int = 0
    check_seconds: float = 0.0
    verdict: str = "not attempted"
    proof_sha256: str = ""
    program: Optional[list] = None
    error: str = ""


def _ensure_checker() -> None:
    if not DRAT_TRIM.exists():
        raise RuntimeError(
            f"drat-trim not found at {DRAT_TRIM}. Run tools/get_drat_trim.sh first.")


def prove_unsat(inst: SLPInstance, k: int, solver: str = "glucose42",
                workdir: Optional[Path] = None, keep_proof: bool = False,
                check_timeout: int = 1800) -> ProofResult:
    """Decide 'is there a k-gate program?' and, if UNSAT, certify it.

    Returns a ProofResult. verdict is one of:
      "VERIFIED"     drat-trim independently confirmed the refutation
      "NOT VERIFIED" drat-trim rejected the proof -- the lower bound does NOT hold
      "sat"          a k-gate program exists (no refutation to certify)
      "check timeout"/"checker error" -- inconclusive, claims nothing
    """
    _ensure_checker()
    if solver not in SOLVERS:
        raise KeyError(solver)
    pool, cls, total = _build(inst, k)
    n = inst.n_inputs

    t0 = time.time()
    with SOLVERS[solver](bootstrap_with=cls, with_proof=True) as s:
        sat = s.solve()
        proof = s.get_proof() if not sat else []
    solve_s = time.time() - t0

    res = ProofResult(k=k, sat=bool(sat), solver=solver, solve_seconds=solve_s,
                      n_vars=pool.top, n_clauses=len(cls))

    if sat:
        # Proof mode does not retain a model, so re-solve to recover the program.
        # The circuit is then checked by the ordinary verifier, independently.
        with SOLVERS[solver](bootstrap_with=cls) as s2:
            s2.solve()
            m = set(l for l in s2.get_model() if l > 0)
        prog = []
        for t in range(n, total):
            p = next(x for x in range(t) if pool.id(("sel", t, x)) in m)
            q = next(x for x in range(t) if pool.id(("selb", t, x)) in m)
            prog.append((p, q))
        verify(inst, prog)
        res.program = prog
        res.verdict = "sat"
        return res

    workdir = Path(workdir or (REPO / "runs" / "proofs"))
    workdir.mkdir(parents=True, exist_ok=True)
    stem = f"{inst.fingerprint()}_k{k}_{solver}"
    cnf_path = workdir / f"{stem}.cnf"
    drat_path = workdir / f"{stem}.drat"

    CNF(from_clauses=cls).to_file(str(cnf_path))
    lines = list(proof)
    if not lines or lines[-1].strip() != "0":
        lines.append("0")          # terminating empty clause
    text = "\n".join(lines) + "\n"
    drat_path.write_text(text)
    res.proof_lines = len(lines)
    res.proof_bytes = drat_path.stat().st_size
    res.cnf_bytes = cnf_path.stat().st_size
    res.proof_sha256 = hashlib.sha256(text.encode()).hexdigest()[:16]

    t0 = time.time()
    try:
        p = subprocess.run([str(DRAT_TRIM), str(cnf_path), str(drat_path)],
                           capture_output=True, text=True, timeout=check_timeout)
        res.check_seconds = time.time() - t0
        verdicts = [l for l in p.stdout.splitlines() if l.startswith("s ")]
        res.verdict = verdicts[0][2:].strip() if verdicts else "no verdict"
    except subprocess.TimeoutExpired:
        res.check_seconds = time.time() - t0
        res.verdict = "check timeout"
    except Exception as exc:
        res.verdict = "checker error"
        res.error = repr(exc)

    if not keep_proof:
        drat_path.unlink(missing_ok=True)
        cnf_path.unlink(missing_ok=True)
    return res


def certified_minimum(inst: SLPInstance, upper: int, upper_program,
                      solver: str = "glucose42", keep_proof: bool = False,
                      verbose: bool = False) -> dict:
    """Establish the optimum with BOTH halves independently checkable.

    Descends from a verified upper bound. Every SAT answer yields a circuit that
    is re-verified; the first UNSAT answer yields a DRAT proof that is checked by
    drat-trim. The result is only reported as proved when the checker says
    VERIFIED -- a bare solver UNSAT is not sufficient.
    """
    verify(inst, upper_program)
    lb = trivial_lower_bound(inst)
    best, best_prog = upper, list(upper_program)
    history = []
    k = upper - 1
    while k >= lb:
        r = prove_unsat(inst, k, solver=solver, keep_proof=keep_proof)
        history.append(r)
        if verbose:
            print(f"    k={k:3d} {'SAT' if r.sat else 'UNSAT':6s} "
                  f"solve={r.solve_seconds:7.2f}s proof={r.proof_lines:>9,d} lines "
                  f"check={r.check_seconds:6.2f}s -> {r.verdict}", flush=True)
        if r.sat:
            best, best_prog = k, r.program
            k -= 1
            continue
        certified = r.verdict == "VERIFIED"
        return {
            "instance": inst.name, "fingerprint": inst.fingerprint(),
            "n": inst.n_inputs, "optimal": k + 1,
            "proved": certified,
            "certificate": "drat-verified" if certified else f"uncertified ({r.verdict})",
            "program": best_prog, "history": history, "lower_bound_used": lb,
        }
    return {"instance": inst.name, "fingerprint": inst.fingerprint(),
            "n": inst.n_inputs, "optimal": best, "proved": True,
            "certificate": "reached trivial lower bound (no refutation needed)",
            "program": best_prog, "history": history, "lower_bound_used": lb}
