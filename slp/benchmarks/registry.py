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

from ..gf import GF2k, circulant, circulant_right, expand_to_binary, hadamard
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
    """ANUBIS theta. Hadamard, involutory.

    NOTE: this is the SAME MATRIX as CLEFIA M0 (confirmed by the ePrint 2017/1151
    errata). They are one benchmark instance, not two -- do not count both.
    """
    return _from_field_matrix(
        "anubis", 0x11D, hadamard([0x01, 0x02, 0x04, 0x06]),
        source="Barreto-Rijmen, ANUBIS (NESSIE 2000, tweaked 2001; matrix unchanged "
               "by the tweak)", verified=True,
        best_known=98, best_known_metric="s-XOR",
        best_known_ref="Xiang et al., ToSC 2020(2) / ePrint 2020/903, Table 1",
        notes="identical matrix to clefia_m0; 97 s-XOR follows from Yuan et al. 2024 "
              "via that identity but is not stated for ANUBIS explicitly",
    )


def clefia_m0() -> SLPInstance:
    """CLEFIA M0. HADAMARD, not circulant -- spec row 1 is (2,1,6,4), not (6,1,2,4)."""
    return _from_field_matrix(
        "clefia_m0", 0x11D, hadamard([0x01, 0x02, 0x04, 0x06]),
        source="Sony, CLEFIA Algorithm Specification Rev 1.0 (2007); RFC 6114",
        verified=True,
        best_known=97, best_known_metric="s-XOR",
        best_known_ref="Yuan et al., ToSC 2024(2):322-347, Table 2",
        notes="identical matrix to anubis",
    )


def clefia_m1() -> SLPInstance:
    """CLEFIA M1. HADAMARD, not circulant."""
    return _from_field_matrix(
        "clefia_m1", 0x11D, hadamard([0x01, 0x08, 0x02, 0x0A]),
        source="Sony, CLEFIA Algorithm Specification Rev 1.0 (2007); RFC 6114",
        verified=True,
        best_known=103, best_known_metric="s-XOR",
        best_known_ref="Xiang et al. ToSC 2020(2), Table 1; confirmed Yuan et al. 2024",
    )


def khazad() -> SLPInstance:
    """KHAZAD H. 8x8 Hadamard, involutory."""
    return _from_field_matrix(
        "khazad", 0x11D, hadamard([0x01, 0x03, 0x04, 0x05, 0x06, 0x08, 0x0B, 0x07]),
        source="Barreto-Rijmen, KHAZAD (NESSIE 2000, tweaked 2001)", verified=True,
        best_known=366, best_known_metric="s-XOR",
        best_known_ref="Xiang et al., ToSC 2020(2), Table 1",
        notes="the one instance where Paar1 (488) beats Boyar-Peralta (507) in g-XOR",
    )


def whirlpool() -> SLPInstance:
    """WHIRLPOOL (final, version 3.0, 2003) diffusion matrix.

    Orientation resolved empirically, NOT by reading the spec prose: the standard
    circulant c[(j-i) mod n] is the one that reproduces the independently derived
    diffusion-layer vectors (tests/test_ciphers.py). Under this convention the image
    of e_0 is column 0 = (01,09,02,05,08,01,04,01), which is what the "B = A*C"
    right-multiplication description in the spec amounts to. Applying an extra
    transpose on top of that -- an easy mistake -- gives a different linear map with
    a different circuit size.

    The 2001 revision changed only the S-box; the MATRIX changed in 2003 (v3.0).
    """
    return _from_field_matrix(
        "whirlpool", 0x11D, circulant([0x01, 0x01, 0x04, 0x01, 0x08, 0x05, 0x02, 0x09]),
        source="Barreto-Rijmen, The Whirlpool Hashing Function, v3.0 (2003-03-12); "
               "ISO/IEC 10118-3", verified=True,
        best_known=417, best_known_metric="g-XOR",
        best_known_ref="Sun, Yang, Li, ePrint 2025/1493, Table 5",
    )


def whirlpool_0() -> SLPInstance:
    """WHIRLPOOL-0 / WHIRLPOOL-T diffusion matrix (pre-2003)."""
    return _from_field_matrix(
        "whirlpool_0", 0x11D, circulant([0x01, 0x01, 0x03, 0x01, 0x05, 0x08, 0x09, 0x05]),
        source="Barreto-Rijmen, Whirlpool v1.0 (2000) / v2.1 (2001)", verified=True,
        notes="superseded matrix; kept as an extra benchmark instance",
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
    "whirlpool_0": whirlpool_0,
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
