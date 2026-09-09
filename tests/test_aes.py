"""Correctness of the GF(2^k) expansion, against published AES test vectors."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp.gf import (GF2k, apply_binary, bits_to_words, circulant,
                    expand_to_binary, hadamard, words_to_bits)
from slp.benchmarks.registry import aes_mixcolumns


def test_field_multiplication():
    aes = GF2k(0x11B)
    assert aes.mul(0x57, 0x83) == 0xC1
    assert aes.mul(0x57, 0x13) == 0xFE
    assert aes.mul(0x00, 0xFF) == 0x00
    assert aes.mul(0x01, 0xAB) == 0xAB


def test_mixcolumns_vectors():
    """FIPS-197 and standard MixColumns test vectors."""
    aes = GF2k(0x11B)
    B = expand_to_binary(aes, circulant([2, 3, 1, 1]))
    cases = [
        ([0xDB, 0x13, 0x53, 0x45], [0x8E, 0x4D, 0xA1, 0xBC]),
        ([0xF2, 0x0A, 0x22, 0x5C], [0x9F, 0xDC, 0x58, 0x9D]),
        ([0x01, 0x01, 0x01, 0x01], [0x01, 0x01, 0x01, 0x01]),
        ([0xC6, 0xC6, 0xC6, 0xC6], [0xC6, 0xC6, 0xC6, 0xC6]),
        ([0xD4, 0xBF, 0x5D, 0x30], [0x04, 0x66, 0x81, 0xE5]),
    ]
    for inp, expected in cases:
        got = bits_to_words(apply_binary(B, words_to_bits(inp, 8)), 8)
        assert got == expected, (inp, got, expected)


def test_mixcolumns_inverse_roundtrip():
    aes = GF2k(0x11B)
    F = expand_to_binary(aes, circulant([2, 3, 1, 1]))
    G = expand_to_binary(aes, circulant([0xE, 0xB, 0xD, 9]))
    for words in ([0xDB, 0x13, 0x53, 0x45], [0x00, 0xFF, 0x10, 0x7A]):
        bits = words_to_bits(words, 8)
        assert bits_to_words(apply_binary(G, apply_binary(F, bits)), 8) == words


def test_hadamard_shape():
    H = hadamard([1, 2, 4, 6])
    assert H[0] == [1, 2, 4, 6]
    assert H[1] == [2, 1, 6, 4]
    assert H[2][3] == 2      # a_{2 xor 3} = a_1 = 2


def test_instance_metadata():
    inst = aes_mixcolumns()
    assert inst.n_inputs == 32 and inst.n_outputs == 32
    assert inst.naive_cost == 152
    assert inst.meta["verified"] is True
