"""Minimal GF(2^k) arithmetic and matrix-to-binary expansion.

Field elements are ints whose bit j is the coefficient of x^j.
`modulus` is the full reduction polynomial including the leading term,
e.g. 0x11B for AES's x^8 + x^4 + x^3 + x + 1.
"""
from __future__ import annotations

from typing import Sequence


class GF2k:
    def __init__(self, modulus: int):
        self.modulus = modulus
        self.k = modulus.bit_length() - 1
        if self.k <= 0:
            raise ValueError("bad modulus")

    def mul(self, a: int, b: int) -> int:
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> self.k:
                a ^= self.modulus
        return r

    def mul_matrix(self, c: int) -> list[list[int]]:
        """k x k binary matrix of the map z -> c*z, in the polynomial basis.

        Entry [i][j] is the coefficient of x^i in c * x^j.
        """
        cols = [self.mul(c, 1 << j) for j in range(self.k)]
        return [[(cols[j] >> i) & 1 for j in range(self.k)] for i in range(self.k)]


def expand_to_binary(field: GF2k, mat: Sequence[Sequence[int]]) -> list[list[int]]:
    """Expand an a x b matrix over GF(2^k) into an (a*k) x (b*k) binary matrix.

    Input word ordering is (word_0 bits 0..k-1, word_1 bits 0..k-1, ...).
    """
    a, b = len(mat), len(mat[0])
    k = field.k
    out = [[0] * (b * k) for _ in range(a * k)]
    for r in range(a):
        for c in range(b):
            block = field.mul_matrix(mat[r][c])
            for i in range(k):
                for j in range(k):
                    out[r * k + i][c * k + j] = block[i][j]
    return out


def circulant(first_row: Sequence[int]) -> list[list[int]]:
    n = len(first_row)
    return [[first_row[(j - i) % n] for j in range(n)] for i in range(n)]


def hadamard(coeffs: Sequence[int]) -> list[list[int]]:
    """had(a_0,...,a_{n-1}) with entry (i,j) = a_{i XOR j}. n must be a power of two."""
    n = len(coeffs)
    if n & (n - 1):
        raise ValueError("hadamard needs a power-of-two size")
    return [[coeffs[i ^ j] for j in range(n)] for i in range(n)]


def apply_binary(rows: Sequence[Sequence[int]], bits: Sequence[int]) -> list[int]:
    return [sum(r[j] & bits[j] for j in range(len(bits))) & 1 for r in rows]


def words_to_bits(words: Sequence[int], k: int) -> list[int]:
    return [(w >> j) & 1 for w in words for j in range(k)]


def bits_to_words(bits: Sequence[int], k: int) -> list[int]:
    return [sum(bits[i * k + j] << j for j in range(k)) for i in range(len(bits) // k)]
