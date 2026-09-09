"""Benchmark instances for the SLP problem.

Every instance carries a `source` and a `verified` flag:

  verified=True   the binary matrix has been checked against published test
                  vectors or an independent reference implementation.
  verified=False  the field/coefficients are transcribed from the literature
                  and still need to be checked against the primary source
                  before any record claim is published.

Record claims may only be made on verified instances.
"""
from __future__ import annotations

import random

from ..gf import GF2k, circulant, expand_to_binary, hadamard
from ..instance import SLPInstance


def _from_field_matrix(name, modulus, mat, source, verified=False, **meta):
    field = GF2k(modulus)
    binary = expand_to_binary(field, mat)
    return SLPInstance.from_binary_matrix(
        name, binary, source=source, verified=verified,
        field=f"GF(2^{field.k})/{modulus:#x}", **meta,
    )


# --------------------------------------------------------------------------
# Cipher diffusion layers
# --------------------------------------------------------------------------
def aes_mixcolumns() -> SLPInstance:
    """AES MixColumns. Verified against four FIPS-197 test vectors (tests/test_aes.py)."""
    return _from_field_matrix(
        "aes_mixcolumns", 0x11B, circulant([2, 3, 1, 1]),
        source="FIPS-197", verified=True,
        best_known=88, best_known_ref="eprint 2026/1481",
        notes="record history 97 -> 94 -> 92 -> 88 (2018-2026)",
    )


def aes_inv_mixcolumns() -> SLPInstance:
    return _from_field_matrix(
        "aes_inv_mixcolumns", 0x11B, circulant([0xE, 0xB, 0xD, 9]),
        source="FIPS-197", verified=True,
    )


def anubis() -> SLPInstance:
    return _from_field_matrix(
        "anubis", 0x11D, hadamard([1, 2, 4, 6]),
        source="Barreto-Rijmen, ANUBIS", verified=False,
    )


def clefia_m0() -> SLPInstance:
    return _from_field_matrix(
        "clefia_m0", 0x11D, circulant([1, 2, 4, 6]),
        source="CLEFIA", verified=False,
    )


def clefia_m1() -> SLPInstance:
    return _from_field_matrix(
        "clefia_m1", 0x11D, circulant([1, 8, 2, 0xA]),
        source="CLEFIA", verified=False,
    )


def khazad() -> SLPInstance:
    return _from_field_matrix(
        "khazad", 0x11D, hadamard([1, 3, 4, 5, 6, 8, 0xB, 7]),
        source="KHAZAD", verified=False,
    )


def whirlpool() -> SLPInstance:
    return _from_field_matrix(
        "whirlpool", 0x11D, circulant([1, 1, 4, 1, 8, 5, 2, 9]),
        source="WHIRLPOOL", verified=False,
    )


# --------------------------------------------------------------------------
# Parametric MDS families over GF(2^4) -- small, exactly solvable, good for
# establishing optimality gaps.
# --------------------------------------------------------------------------
def hadamard_gf16(coeffs, name=None) -> SLPInstance:
    return _from_field_matrix(
        name or f"had16_{'_'.join(f'{c:x}' for c in coeffs)}", 0x13,
        hadamard(list(coeffs)), source="parametric", verified=False,
    )


def circulant_gf16(coeffs, name=None) -> SLPInstance:
    return _from_field_matrix(
        name or f"circ16_{'_'.join(f'{c:x}' for c in coeffs)}", 0x13,
        circulant(list(coeffs)), source="parametric", verified=False,
    )


# --------------------------------------------------------------------------
# Random matrices -- the Tan-Peyrin style benchmark family.
# --------------------------------------------------------------------------
def random_matrix(n: int, m: int, density: float, seed: int) -> SLPInstance:
    rng = random.Random((seed, n, m, round(density * 1000)).__hash__() & 0xFFFFFFFF)
    rows = []
    while len(rows) < m:
        row = [1 if rng.random() < density else 0 for _ in range(n)]
        if any(row):
            rows.append(row)
    return SLPInstance.from_binary_matrix(
        f"rand_n{n}_m{m}_d{density:.1f}_s{seed}", rows,
        source="generated", verified=True, density=density, seed=seed,
    )


CIPHERS = {
    "aes_mixcolumns": aes_mixcolumns,
    "aes_inv_mixcolumns": aes_inv_mixcolumns,
    "anubis": anubis,
    "clefia_m0": clefia_m0,
    "clefia_m1": clefia_m1,
    "khazad": khazad,
    "whirlpool": whirlpool,
}


def suite(kind: str = "small") -> list[SLPInstance]:
    """Named benchmark suites."""
    if kind == "ciphers":
        return [f() for f in CIPHERS.values()]
    if kind == "small":
        # 16x16 instances: small enough for exact BP and for SAT lower bounds
        out = [anubis(), clefia_m0(), clefia_m1()]
        out += [hadamard_gf16([1, 2, 4, 6]), hadamard_gf16([1, 2, 8, 9]),
                circulant_gf16([1, 2, 4, 6])]
        return out
    if kind == "random":
        return [random_matrix(n, n, d, s)
                for n in (15, 16, 18, 20)
                for d in (0.3, 0.5, 0.7)
                for s in range(3)]
    if kind == "tiny":
        return [random_matrix(n, n, d, s)
                for n in (8, 10, 12)
                for d in (0.3, 0.5, 0.7)
                for s in range(3)]
    raise KeyError(kind)


def get(name: str) -> SLPInstance:
    if name in CIPHERS:
        return CIPHERS[name]()
    raise KeyError(name)
