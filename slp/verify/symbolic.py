"""Independent symbolic verification of an SLP certificate.

The primary verifier (`slp.instance.verify`) works on the bitmask abstraction:
a signal is represented by the SET of inputs XORed to produce it, and a target is
computed iff some signal's bitmask equals the target's. That abstraction is sound
for linear circuits, but it is an abstraction, and it shares code paths with how
instances are built.

This module discharges a strictly stronger obligation, with no shared code:

    for ALL 2^n input assignments x,  circuit(x) = M x  over GF(2)

It does so with Z3 over Booleans -- XOR is native, so the query is pure
propositional logic. UNSAT of the negation is a machine-checked proof over the
entire input space. If Z3 returns unsat for every output row, the circuit is
correct on all 2^n inputs, not merely on the abstraction we used to search.

This catches a class of bug the bitmask verifier structurally cannot: an error in
the bitmask semantics itself, or in how the target matrix was expanded.
"""
from __future__ import annotations

from typing import Sequence

import z3

from ..instance import SLPInstance


class SymbolicVerificationError(AssertionError):
    pass


def verify_symbolic(inst: SLPInstance, program: Sequence[tuple[int, int]],
                    timeout_ms: int = 60_000) -> dict:
    """Prove the program computes every target row, for all inputs.

    Returns a dict of per-row results. Raises SymbolicVerificationError if any
    row is not proved.
    """
    n = inst.n_inputs
    x = [z3.Bool(f"x{i}") for i in range(n)]

    # Build the circuit symbolically from the program alone.
    sig: list[z3.BoolRef] = list(x)
    for k, (a, b) in enumerate(program):
        idx = n + k
        if not (0 <= a < idx and 0 <= b < idx):
            raise SymbolicVerificationError(f"op {k} references signal out of range")
        if a == b:
            raise SymbolicVerificationError(f"op {k} is a self-XOR")
        sig.append(z3.Xor(sig[a], sig[b]))

    # Build the specification directly from the target matrix.
    def spec_row(t: int) -> z3.BoolRef:
        terms = [x[i] for i in range(n) if (t >> i) & 1]
        if not terms:
            return z3.BoolVal(False)
        acc = terms[0]
        for term in terms[1:]:
            acc = z3.Xor(acc, term)
        return acc

    results = {}
    for r, t in enumerate(inst.targets):
        want = spec_row(t)
        # Find a signal claimed to implement this row (bitmask-free: we test
        # each candidate by proving equivalence, not by comparing bitmasks).
        proved_by = None
        for j, s in enumerate(sig):
            solver = z3.Solver()
            solver.set("timeout", timeout_ms)
            solver.add(z3.Not(s == want))
            res = solver.check()
            if res == z3.unsat:
                proved_by = j
                break
            if res == z3.unknown:
                raise SymbolicVerificationError(
                    f"row {r}: Z3 returned unknown (timeout {timeout_ms}ms)")
        if proved_by is None:
            raise SymbolicVerificationError(
                f"row {r} (target {t:#x}) is NOT computed by any signal in the program")
        results[r] = proved_by
    return {"rows_proved": len(results), "signal_for_row": results,
            "n_inputs": n, "gates": len(program)}


def verify_symbolic_fast(inst: SLPInstance, program: Sequence[tuple[int, int]],
                         timeout_ms: int = 120_000) -> dict:
    """Same obligation, one solver query instead of |rows| x |signals|.

    Uses the bitmask verifier only to PROPOSE which signal implements each row,
    then proves all those equivalences simultaneously. The proof obligation is
    identical; only the search for the witness is cheaper.
    """
    from ..instance import apply_program

    n = inst.n_inputs
    masks = apply_program(n, program)
    pos = {}
    for v, m in enumerate(masks):
        pos.setdefault(m, v)
    witness = {}
    for r, t in enumerate(inst.targets):
        if t not in pos:
            raise SymbolicVerificationError(
                f"row {r} (target {t:#x}) has no candidate signal")
        witness[r] = pos[t]

    x = [z3.Bool(f"x{i}") for i in range(n)]
    sig: list[z3.BoolRef] = list(x)
    for k, (a, b) in enumerate(program):
        sig.append(z3.Xor(sig[a], sig[b]))

    def spec_row(t: int):
        terms = [x[i] for i in range(n) if (t >> i) & 1]
        acc = terms[0]
        for term in terms[1:]:
            acc = z3.Xor(acc, term)
        return acc

    conj = [sig[witness[r]] == spec_row(t) for r, t in enumerate(inst.targets)]
    solver = z3.Solver()
    solver.set("timeout", timeout_ms)
    solver.add(z3.Not(z3.And(conj)))
    res = solver.check()
    if res == z3.sat:
        raise SymbolicVerificationError(
            f"circuit does NOT implement the matrix; counterexample: {solver.model()}")
    if res == z3.unknown:
        raise SymbolicVerificationError(f"Z3 unknown (timeout {timeout_ms}ms)")
    return {"rows_proved": len(conj), "signal_for_row": witness,
            "n_inputs": n, "gates": len(program), "z3_result": "unsat (proved)"}
