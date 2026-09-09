"""Shadow-evaluate the Lean certificate semantics in Python.

We cannot compile Lean in every environment, so this test re-implements the
definitions in slp/verify/lean_cert.py's PREAMBLE *exactly as written* -- same
representation (List Bool), same well-formedness rule, same acceptance
condition -- and checks it agrees with the primary verifier.

This cannot catch a Lean SYNTAX error. It does catch the more dangerous failure:
a certificate whose Lean definitions say something different from what we think
they say, e.g. a well-formedness rule that accepts a self-XOR, or an acceptance
condition satisfiable by a program that does not compute the targets.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.instance import verify


# --- Lean definitions, transcribed --------------------------------------------
def xorVec(u, v):                       # List.zipWith Bool.xor
    return [a ^ b for a, b in zip(u, v)]


def basisRow(n, i):                     # (List.range n).map (fun j => Nat.beq i j)
    return [1 if i == j else 0 for j in range(n)]


def basis(n):
    return [basisRow(n, i) for i in range(n)]


def stepOne(sigs, op):                  # sigs ++ [xorVec (getD a) (getD b)]
    a, b = op
    ga = sigs[a] if a < len(sigs) else []
    gb = sigs[b] if b < len(sigs) else []
    return sigs + [xorVec(ga, gb)]


def signals(n, prog):
    s = basis(n)
    for op in prog:
        s = stepOne(s, op)
    return s


def wellFormedAux(n, k, prog):
    if not prog:
        return True
    (a, b), rest = prog[0], prog[1:]
    return (a < n + k) and (b < n + k) and (a != b) and wellFormedAux(n, k + 1, rest)


def wellFormed(n, prog):
    return wellFormedAux(n, 0, prog)


def computesWith(sigs, targets):
    return all(any(v == t for v in sigs) for t in targets)


def valid(n, targets, prog):
    return wellFormed(n, prog) and computesWith(signals(n, prog), targets)
# -------------------------------------------------------------------------------


def _vecs(inst):
    return [[(t >> i) & 1 for i in range(inst.n_inputs)] for t in inst.targets]


@pytest.mark.parametrize("name", ["aes_mixcolumns", "anubis", "clefia_m1"])
def test_lean_semantics_accepts_valid_circuit(name):
    inst = registry.get(name)
    native.seed(1)
    prog = native.paar(inst.n_inputs, inst.targets, 0)
    verify(inst, prog)
    assert valid(inst.n_inputs, _vecs(inst), prog) is True


def test_lean_semantics_rejects_self_xor():
    """wellFormed must reject x XOR x, which computes zero and could be abused."""
    inst = registry.get("aes_mixcolumns")
    assert wellFormed(4, [(0, 0)]) is False
    assert wellFormed(4, [(0, 1)]) is True


def test_lean_semantics_rejects_forward_reference():
    """Gate k may only read signals with index < n + k."""
    assert wellFormed(4, [(0, 4)]) is False     # signal 4 does not exist yet
    assert wellFormed(4, [(0, 1), (4, 0)]) is True   # now it does


def test_lean_semantics_rejects_incomplete_circuit():
    inst = registry.get("aes_mixcolumns")
    native.seed(1)
    prog = native.paar(inst.n_inputs, inst.targets, 0)
    assert valid(inst.n_inputs, _vecs(inst), prog[:-1]) is False


def test_lean_semantics_rejects_corrupted_circuit():
    inst = registry.get("anubis")
    native.seed(1)
    prog = list(native.paar(inst.n_inputs, inst.targets, 0))
    mid = len(prog) // 2
    prog[mid] = (prog[mid][0], (prog[mid][1] + 1) % inst.n_inputs)
    assert valid(inst.n_inputs, _vecs(inst), prog) is False


def test_emitted_certificate_matches_semantics():
    """The generated .lean file's literals must match the instance and program."""
    import re
    from slp.verify.lean_cert import emit
    import tempfile
    inst = registry.get("aes_mixcolumns")
    native.seed(1)
    prog = native.paar(inst.n_inputs, inst.targets, 0)
    with tempfile.NamedTemporaryFile("w+", suffix=".lean", delete=False) as fh:
        text = emit(inst, prog, fh.name, method="paar1")
    # gate count claimed in the theorem must equal the real program length
    m = re.search(r"prog\.length = (\d+)", text)
    assert m and int(m.group(1)) == len(prog)
    # the program literal must round-trip
    ops = re.findall(r"\((\d+), (\d+)\)", text.split("def prog")[1].split("theorem")[0])
    assert [(int(a), int(b)) for a, b in ops] == list(prog)
