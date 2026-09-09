"""Regression tests for the SAT optimality prover.

The prover is the only component that produces LOWER bounds, so a bug here would
produce a false optimality claim -- the worst failure mode in the project. These
tests check it against cases whose answers are known independently.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slp import native
from slp.benchmarks import registry
from slp.instance import SLPInstance, verify
from slp.optimal import exists_program, minimum_size, trivial_lower_bound


def test_single_row_needs_popcount_minus_one():
    """One target of popcount w needs exactly w-1 gates; nothing can do better."""
    for w in (2, 3, 4, 5):
        inst = SLPInstance.from_binary_matrix("t", [[1] * w + [0] * (6 - w)])
        assert exists_program(inst, w - 1).sat is True
        assert exists_program(inst, w - 2).sat is False


def test_identity_rows_are_free():
    """Targets that are already inputs need no gates at all."""
    inst = SLPInstance.from_binary_matrix("t", [[1, 0, 0], [0, 1, 0], [1, 1, 0]])
    assert exists_program(inst, 1).sat is True
    assert exists_program(inst, 0).sat is False


def test_trivial_lower_bound_is_sound():
    """The free bound must never exceed a circuit we can actually build."""
    for n in (6, 8, 10):
        for d in (0.3, 0.5, 0.7):
            inst = registry.random_matrix(n, n, d, 0)
            native.seed(1)
            ub = verify(inst, native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0))
            assert trivial_lower_bound(inst) <= ub, inst.name


def test_sat_program_is_valid():
    """Any program the solver returns must pass the independent verifier."""
    inst = registry.random_matrix(6, 6, 0.5, 1)
    native.seed(1)
    ub = verify(inst, native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0))
    res = exists_program(inst, ub)
    assert res.sat
    assert verify(inst, res.program) == ub


def test_minimum_size_agrees_with_bruteforce_small():
    """On tiny instances, cross-check the proved optimum against exhaustive search."""
    import itertools

    def brute_force_min(inst, cap=6):
        n = inst.n_inputs
        targets = set(inst.targets)
        start = tuple(1 << i for i in range(n))
        frontier = {start}
        if targets <= set(start):
            return 0
        for depth in range(1, cap + 1):
            nxt = set()
            for sigs in frontier:
                for a, b in itertools.combinations(range(len(sigs)), 2):
                    v = sigs[a] ^ sigs[b]
                    if v == 0 or v in sigs:
                        continue
                    new = sigs + (v,)
                    if targets <= set(new):
                        return depth
                    nxt.add(new)
            frontier = nxt
            if not frontier:
                return None
        return None

    for seed in (0, 1, 2):
        inst = registry.random_matrix(4, 3, 0.6, seed)
        bf = brute_force_min(inst)
        if bf is None:
            continue
        native.seed(1)
        ub = verify(inst, native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0))
        res = minimum_size(inst, lower=1, upper=ub, verbose=False)
        assert res["proved"], inst.name
        assert res["optimal"] == bf, (inst.name, res["optimal"], bf)


def test_unsat_below_optimum_stays_unsat():
    """Monotonicity: if k gates are impossible, so are k-1."""
    inst = registry.random_matrix(6, 6, 0.5, 0)
    native.seed(1)
    ub = verify(inst, native.boyar_peralta(inst.n_inputs, inst.targets, 0, 0))
    res = minimum_size(inst, lower=1, upper=ub, verbose=False)
    opt = res["optimal"]
    assert exists_program(inst, opt).sat is True
    assert exists_program(inst, opt - 1).sat is False
    if opt >= 2:
        assert exists_program(inst, opt - 2).sat is False
