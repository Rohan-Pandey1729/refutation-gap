"""Search-algorithm regression tests. Every program is checked by the verifier."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks.registry import aes_mixcolumns, random_matrix
from slp.instance import SLPInstance, VerificationError, verify


def test_verifier_rejects_incomplete_program():
    inst = SLPInstance.from_binary_matrix("t", [[1, 1, 0], [0, 1, 1]])
    with pytest.raises(VerificationError):
        verify(inst, [(0, 1)])


def test_verifier_rejects_self_xor():
    inst = SLPInstance.from_binary_matrix("t", [[1, 1, 0]])
    with pytest.raises(ValueError):
        verify(inst, [(0, 0)])


def test_verifier_rejects_forward_reference():
    inst = SLPInstance.from_binary_matrix("t", [[1, 1, 0]])
    with pytest.raises(ValueError):
        verify(inst, [(0, 5)])


@pytest.mark.parametrize("n,d,seed", [(8, 0.5, 0), (10, 0.3, 1), (12, 0.7, 2)])
def test_all_methods_produce_verified_programs(n, d, seed):
    inst = random_matrix(n, n, d, seed)
    for name, call in [
        ("paar1", lambda: native.paar(inst.n_inputs, inst.targets, 0)),
        ("paar2", lambda: native.paar(inst.n_inputs, inst.targets, 1)),
        ("bp", lambda: native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0)),
        ("rnbp", lambda: native.boyar_peralta(inst.n_inputs, inst.targets, 1, 0)),
    ]:
        native.seed(seed + 1)
        gates = verify(inst, call())
        assert gates <= inst.naive_cost, f"{name} worse than naive"


def test_published_paar1_on_aes():
    """Paar1 on AES MixColumns is 108 in the literature. Regression guard."""
    inst = aes_mixcolumns()
    native.seed(1)
    assert verify(inst, native.paar(inst.n_inputs, inst.targets, 0)) == 108


@pytest.mark.slow
def test_published_bp_on_aes():
    """Boyar-Peralta on AES MixColumns is 97 in the literature. Regression guard."""
    inst = aes_mixcolumns()
    native.seed(1)
    assert verify(inst, native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0)) == 97


def test_budgeted_oracle_never_beats_exact():
    """A capped oracle can only miss reductions, so it must not do better."""
    inst = random_matrix(14, 14, 0.5, 0)
    native.seed(1)
    exact = verify(inst, native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0))
    native.seed(1)
    capped = verify(inst, native.boyar_peralta(inst.n_inputs, inst.targets, 0, 100))
    assert capped >= exact


def test_gval_matches_brute_force():
    """The C distance oracle agrees with a brute-force subset search."""
    import itertools
    n = 6
    added = [0b000111, 0b011001, 0b100100]
    basis = [1 << i for i in range(n)]
    S = basis + added
    for x in range(1, 1 << n):
        brute = min(
            k for k in range(1, len(S) + 1)
            for combo in itertools.combinations(S, k)
            if __import__("functools").reduce(lambda a, b: a ^ b, combo) == x
        ) if any(
            __import__("functools").reduce(lambda a, b: a ^ b, c) == x
            for k in range(1, len(S) + 1) for c in itertools.combinations(S, k)
        ) else None
        got = native.gval(n, x, added, ub=n + 1)
        assert got == brute, (bin(x), got, brute)
