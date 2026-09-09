"""The top-K candidate prefilter must never produce an invalid circuit."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.instance import verify


@pytest.mark.parametrize("k", [5, 20, 100, 1000])
@pytest.mark.parametrize("n", [10, 14])
def test_topk_produces_valid_circuits(n, k):
    inst = registry.random_matrix(n, n, 0.5, 0)
    native.seed(1)
    gates = verify(inst, native.boyar_peralta_topk(inst.n_inputs, inst.targets, 0, 0, k))
    assert gates <= inst.naive_cost


def test_large_topk_matches_unrestricted():
    """With K larger than the candidate set, the prefilter must be a no-op."""
    for n in (10, 12, 14):
        inst = registry.random_matrix(n, n, 0.5, 0)
        native.seed(1)
        full = verify(inst, native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0))
        native.seed(1)
        big = verify(inst, native.boyar_peralta_topk(inst.n_inputs, inst.targets, 0, 0, 10**6))
        assert full == big, (n, full, big)


def test_prefilter_condition_is_sound():
    """popcount(t^u) <= dist-1 must really imply g(t^u) <= dist-1."""
    import random
    rng = random.Random(0)
    n = 12
    for _ in range(300):
        added = [rng.randrange(1, 1 << n) for _ in range(rng.randrange(0, 6))]
        x = rng.randrange(1, 1 << n)
        b = rng.randrange(0, 6)
        if bin(x).count("1") <= b:
            assert native.gval(n, x, added, b) <= b, (x, b, added)
