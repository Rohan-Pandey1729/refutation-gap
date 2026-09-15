"""Emit self-contained Lean 4 certificates for SLP circuits.

Design choice: each certificate is a SINGLE self-contained .lean file with no
imports, no Mathlib, and no lake project. It is checked with one command:

    lean certs/<name>.lean

That makes a certificate independently checkable by anyone with a Lean toolchain
and nothing else -- no dependency resolution, no version pinning of a library
that may have moved. The checker definitions are duplicated into every file on
purpose; the duplication is what buys the reproducibility.

Representation: a signal is a `List Bool` of length n -- the coefficient vector
of the linear form over GF(2). XOR is `List.zipWith Bool.xor`. This is chosen
over Nat bitmasks because the Lean kernel evaluates list/Bool structural
recursion predictably, whereas `Nat.xor` has no kernel acceleration.

Trust base: the file ends with `#print axioms cert`. If that reports no axioms,
the result is fully kernel-checked. If `decide` is too slow and `native_decide`
is used instead, the axiom list will show `Lean.ofReduceBool`, which trusts the
compiler -- the file says so explicitly rather than hiding it.
"""
from __future__ import annotations

from typing import Sequence

from ..instance import SLPInstance, verify

PREAMBLE = r'''/-
  Machine-checkable certificate for a Shortest Linear Straight-Line Program.

  Instance    : {name}
  Fingerprint : {fingerprint}
  Inputs      : {n} variables over GF(2)
  Outputs     : {m} linear forms
  Gate count  : {gates} XOR gates
  Produced by : {method}
  Source run  : {run}

  WHAT THIS FILE PROVES

    SLP.valid n targets prog = true

  which unfolds to two conjuncts:

    (1) wellFormed  -- every gate reads only earlier signals, and no gate is a
                       self-XOR (x XOR x = 0, which would be a way to cheat).
    (2) computes    -- every one of the {m} target linear forms appears among the
                       signals the program actually produces.

  Signals are coefficient vectors over GF(2), so signal equality IS equality of
  linear forms. There is no abstraction gap to argue about.

  HOW TO CHECK IT

    lean {file}

  No Mathlib, no lake, no imports. If it compiles with no errors, the circuit is
  correct. The final `#print axioms` line reports the trust base; an empty axiom
  list means the Lean kernel checked everything itself.

  This file is generated. Do not edit by hand.
-/

set_option maxRecDepth 1000000

namespace SLP

/-- A linear form over GF(2), as its coefficient vector. -/
abbrev Vec := List Bool

/-- Addition in GF(2)^n. -/
def xorVec (u v : Vec) : Vec := List.zipWith Bool.xor u v

/-- The i-th standard basis vector in GF(2)^n, i.e. the input variable x_i. -/
def basisRow (n i : Nat) : Vec := (List.range n).map (fun j => Nat.beq i j)

/-- The n input variables. -/
def basis (n : Nat) : List Vec := (List.range n).map (basisRow n)

/-- Append one gate: a new signal equal to the XOR of two existing ones. -/
def stepOne (sigs : List Vec) (op : Nat × Nat) : List Vec :=
  sigs ++ [xorVec (sigs.getD op.1 []) (sigs.getD op.2 [])]

/-- Run the whole program, returning every signal it computes. -/
def signals (n : Nat) (prog : List (Nat × Nat)) : List Vec :=
  prog.foldl stepOne (basis n)

/-- Gate k may only read signals with index < n + k, and may not read the same
    signal twice (which would compute the zero vector). -/
def wellFormedAux (n : Nat) : Nat -> List (Nat × Nat) -> Bool
  | _, [] => true
  | k, (a, b) :: rest =>
      Nat.blt a (n + k) && Nat.blt b (n + k) && (! Nat.beq a b) &&
        wellFormedAux n (k + 1) rest

def wellFormed (n : Nat) (prog : List (Nat × Nat)) : Bool := wellFormedAux n 0 prog

/-- Every target linear form is realised by some signal. -/
def computesWith (sigs : List Vec) (targets : List Vec) : Bool :=
  targets.all (fun t => sigs.any (fun v => v == t))

def valid (n : Nat) (targets : List Vec) (prog : List (Nat × Nat)) : Bool :=
  wellFormed n prog && computesWith (signals n prog) targets

end SLP

'''


def _vec_literal(mask: int, n: int) -> str:
    return "[" + ", ".join("true" if (mask >> i) & 1 else "false" for i in range(n)) + "]"


def _lean_namespace(name: str) -> str:
    """A Lean 4 identifier for this instance's namespace.

    Lean treats '.' as a namespace separator, so any character that is not
    alphanumeric must go. Instance names carry densities ("rand_n8_m8_d0.3_s11"),
    and an unsanitised '.' silently splits the namespace in two: the file still
    elaborates, but it no longer parses as one unit and `end` fails to match.
    Caught by a compile on 2026-09-14, not by our tests; see the regression test
    in tests/test_lean_cert.py.
    """
    ident = "".join(ch for ch in name if ch.isalnum())
    if not ident:
        ident = "instance"
    return "Cert" + ident[0].upper() + ident[1:]


def emit(inst: SLPInstance, program: Sequence[tuple[int, int]], path,
         method: str = "unknown", run: str = "unrecorded",
         tactic: str = "decide") -> str:
    """Write a self-contained Lean certificate. Returns the file contents."""
    gates = verify(inst, program)          # never emit an unverified certificate
    n = inst.n_inputs
    body = [PREAMBLE.format(
        name=inst.name, fingerprint=inst.fingerprint(), n=n, m=inst.n_outputs,
        gates=gates, method=method, run=run, file=str(path))]

    body.append(f"namespace {_lean_namespace(inst.name)}\n")
    body.append(f"def n : Nat := {n}\n")

    body.append("/-- The target matrix: one coefficient vector per output row. -/")
    body.append("def targets : List SLP.Vec :=")
    rows = [f"  {_vec_literal(t, n)}" for t in inst.targets]
    body.append("  [\n" + ",\n".join("  " + r.strip() for r in rows) + "\n  ]\n")

    body.append("/-- The circuit: gate k computes signal (n+k) = signal a XOR signal b. -/")
    body.append("def prog : List (Nat × Nat) :=")
    op_strs = [f"({a}, {b})" for a, b in program]
    wrapped, line = [], "  ["
    for i, chunk in enumerate(op_strs):
        piece = chunk + ("" if i == len(op_strs) - 1 else ", ")
        if len(line) + len(piece) > 96:
            wrapped.append(line)
            line = "   "
        line += piece
    wrapped.append(line + "]")
    body.append("\n".join(wrapped) + "\n")

    body.append(f"/-- The circuit uses exactly {gates} XOR gates. -/")
    body.append(f"theorem gate_count : prog.length = {gates} := by rfl\n")

    body.append("/-- MAIN RESULT: the circuit is well formed and computes every target. -/")
    body.append(f"theorem cert : SLP.valid n targets prog = true := by {tactic}\n")

    body.append("-- Trust base. An empty axiom list means the kernel checked everything.")
    body.append("#print axioms cert")
    body.append("#print axioms gate_count\n")
    body.append(f"end {_lean_namespace(inst.name)}")

    text = "\n".join(body)
    from pathlib import Path
    Path(path).write_text(text)
    return text
