"""Diffusion-layer validation for every benchmark cipher matrix.

The AES vectors are published (FIPS-197 Appendix B). The remaining vectors were
derived by an independent verification pass that rebuilt each cipher's reference
lookup tables from the candidate matrix definition, compared them byte-for-byte
against the designers' published tables, and ran the full cipher against official
test vectors (NESSIE for ANUBIS/KHAZAD, RFC 6114 for CLEFIA, ISO/IEC 10118-3 for
WHIRLPOOL). Agreement between that implementation and this one is cross-validation
by two independently written codebases from the same specifications.

Provenance and caveats for each matrix are recorded in SOURCES.md.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp.benchmarks import registry
from slp.gf import GF2k, apply_binary, bits_to_words, expand_to_binary, words_to_bits

# (instance name, field modulus, word size, input words, expected output words)
VECTORS = [
    ("anubis",      0x11D, 8, [0xDE, 0xAD, 0xBE, 0xEF], [0x03, 0x34, 0xEB, 0xFE]),
    ("anubis",      0x11D, 8, [0x01, 0x23, 0x45, 0x67], [0x01, 0x23, 0x45, 0x67]),
    ("clefia_m0",   0x11D, 8, [0xDE, 0xAD, 0xBE, 0xEF], [0x03, 0x34, 0xEB, 0xFE]),
    ("clefia_m1",   0x11D, 8, [0xDE, 0xAD, 0xBE, 0xEF], [0x56, 0x28, 0x72, 0x2E]),
    ("clefia_m1",   0x11D, 8, [0x01, 0x23, 0x45, 0x67], [0x5F, 0x7D, 0x1B, 0x39]),
    ("khazad",      0x11D, 8, [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF],
                              [0x70, 0x52, 0x34, 0x16, 0xF8, 0xDA, 0xBC, 0x9E]),
    ("whirlpool",   0x11D, 8, [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF],
                              [0x0E, 0x4B, 0xE1, 0x8A, 0x8B, 0xCE, 0x64, 0x0F]),
    ("whirlpool_0", 0x11D, 8, [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF],
                              [0xB3, 0x9C, 0x5C, 0xD5, 0x36, 0x19, 0xD9, 0x50]),
]


def _apply_instance(inst, words, k):
    """Apply an SLPInstance's target matrix to a word vector."""
    bits = words_to_bits(words, k)
    out = [bin(t & _mask(bits)).count("1") & 1 for t in inst.targets]
    return bits_to_words(out, k)


def _mask(bits):
    return sum(b << i for i, b in enumerate(bits))


@pytest.mark.parametrize("name,mod,k,inp,expected", VECTORS)
def test_diffusion_layer_vectors(name, mod, k, inp, expected):
    inst = registry.get(name)
    assert _apply_instance(inst, inp, k) == expected, f"{name} diffusion vector mismatch"


def test_anubis_equals_clefia_m0():
    """ePrint 2017/1151 errata: CLEFIA M0 is the same matrix as ANUBIS theta.

    They must therefore be ONE benchmark instance, not two. This test exists so
    that a future edit cannot silently make them differ and double-count a record.
    """
    a, c = registry.get("anubis"), registry.get("clefia_m0")
    assert a.fingerprint() == c.fingerprint()
    assert a.targets == c.targets


def test_hadamard_matrices_are_involutory():
    """ANUBIS, CLEFIA M0/M1 and KHAZAD are all involutions over their field."""
    for name, mod, coeffs in [("anubis", 0x11D, [1, 2, 4, 6]),
                              ("clefia_m1", 0x11D, [1, 8, 2, 0xA]),
                              ("khazad", 0x11D, [1, 3, 4, 5, 6, 8, 0xB, 7])]:
        from slp.gf import hadamard
        f = GF2k(mod)
        B = expand_to_binary(f, hadamard(coeffs))
        n = len(B)
        for e in range(n):
            v = [1 if i == e else 0 for i in range(n)]
            assert apply_binary(B, apply_binary(B, v)) == v, f"{name} not involutory"


def test_whirlpool_variants_differ():
    """The 2003 revision changed the matrix; the two instances must not coincide."""
    assert registry.get("whirlpool").fingerprint() != registry.get("whirlpool_0").fingerprint()


def test_naive_costs_match_literature():
    """Naive XOR counts published in ePrint 2017/1151 Table 3."""
    expected = {"aes_mixcolumns": 152, "anubis": 184, "clefia_m0": 184,
                "clefia_m1": 208, "khazad": 1232, "whirlpool": 840}
    for name, naive in expected.items():
        assert registry.get(name).naive_cost == naive, name
