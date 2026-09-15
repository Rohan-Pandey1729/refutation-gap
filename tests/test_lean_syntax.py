"""The emitted Lean file must be *syntactically* well formed, not merely
semantically right.

Regression test for the defect found on 2026-09-14, when a certificate for
`rand_n8_m8_d0.3_s11` was compiled for the first time. The emitter built the
namespace by stripping underscores from the instance name, which left the '.'
of the density in place. Lean reads '.' as a namespace separator, so
`namespace CertRandn8m8d0.3s11` opened `CertRandn8m8d0` and then failed on the
rest, and the matching `end` failed too. The declarations still elaborated and
`#print axioms` still reported `[propext]`, which is exactly why the existing
semantic tests did not notice: the mathematics was fine and the file was not.

Every cipher instance happens to have a dot-free name, so the 13 certificates
compiled before that date were unaffected. Only random instances, whose names
carry a density, could trigger it.
"""
import re
import pytest

from slp.benchmarks.registry import random_matrix, aes_mixcolumns, anubis, clefia_m1
from slp.verify.lean_cert import emit, _lean_namespace
from slp.native import paar

LEAN_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

NAMES = [
    "rand_n8_m8_d0.3_s11", "rand_n7_m7_d0.7_s4", "rand_n10_m10_d0.55_s2",
    "aes_mixcolumns", "anubis", "clefia_m1", "a.b.c", "0leading", "",
]


@pytest.mark.parametrize("name", NAMES)
def test_namespace_is_a_single_lean_identifier(name):
    ns = _lean_namespace(name)
    assert LEAN_IDENT.match(ns), f"{name!r} produced non-identifier namespace {ns!r}"
    assert "." not in ns, f"{name!r} leaked a namespace separator into {ns!r}"


def test_cipher_namespaces_are_unchanged():
    """The fix must not rename the namespaces of already-compiled certificates."""
    assert _lean_namespace("aes_mixcolumns") == "CertAesmixcolumns"
    assert _lean_namespace("anubis") == "CertAnubis"
    assert _lean_namespace("clefia_m1") == "CertClefiam1"


def _emit_text(inst, tmp_path):
    prog = paar(inst.n_inputs, inst.targets)
    prog = prog[0] if isinstance(prog, tuple) else prog
    return emit(inst, prog, tmp_path / "c.lean", method="test", run="test")


@pytest.mark.parametrize("factory", [
    lambda: random_matrix(8, 8, 0.3, 11),
    lambda: random_matrix(7, 7, 0.7, 4),
    lambda: aes_mixcolumns(),
    lambda: anubis(),
    lambda: clefia_m1(),
])
def test_namespace_opens_and_closes_consistently(factory, tmp_path):
    txt = _emit_text(factory(), tmp_path)
    opens = re.findall(r"^namespace\s+(\S+)\s*$", txt, re.M)
    closes = re.findall(r"^end\s+(\S+)\s*$", txt, re.M)
    assert opens, "no namespace opened"
    for ns in opens + closes:
        assert LEAN_IDENT.match(ns), f"not a Lean identifier: {ns!r}"
    # every namespace opened is closed exactly once, and vice versa
    assert sorted(opens) == sorted(closes), f"unbalanced: opened {opens}, closed {closes}"


@pytest.mark.parametrize("factory", [
    lambda: random_matrix(8, 8, 0.3, 11),
    lambda: aes_mixcolumns(),
])
def test_print_axioms_targets_resolve_inside_the_namespace(factory, tmp_path):
    """`#print axioms X` must name a declaration the file actually defines."""
    txt = _emit_text(factory(), tmp_path)
    declared = set(re.findall(r"^(?:theorem|def)\s+([A-Za-z_][A-Za-z0-9_']*)", txt, re.M))
    printed = re.findall(r"^#print\s+axioms\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*$", txt, re.M)
    assert printed, "certificate does not print its axioms"
    for target in printed:
        leaf = target.rsplit(".", 1)[-1]
        assert leaf in declared, f"#print axioms {target} names nothing declared in the file"
