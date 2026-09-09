"""Core representation for the Shortest Linear Straight-Line Program (SLP) problem.

Problem
-------
Given a matrix M in GF(2)^{m x n}, find the shortest sequence of XOR operations
computing all m rows of M from the n input variables x_0..x_{n-1}.

Representation
--------------
Every intermediate signal is a bitmask over the n inputs: bit i set means x_i
participates in that XOR. Signal 0..n-1 are the inputs themselves (e_i = 1<<i).
A program is a list of ops (a, b) meaning "signal_{k} = signal_a XOR signal_b",
where k is the index of the newly created signal.

Cost is the number of ops. This is exactly the XOR gate count.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Iterable, Sequence


@dataclass(frozen=True)
class SLPInstance:
    """A target linear map over GF(2)."""

    name: str
    n_inputs: int
    targets: tuple[int, ...]  # bitmasks over inputs, one per output row
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.n_inputs > 64:
            raise ValueError("n_inputs > 64 not supported by the bitmask core")
        mask = (1 << self.n_inputs) - 1
        for t in self.targets:
            if t & ~mask:
                raise ValueError(f"target {t:#x} has bits outside n_inputs={self.n_inputs}")
            if t == 0:
                raise ValueError("zero target row is degenerate; drop it before constructing")

    @property
    def n_outputs(self) -> int:
        return len(self.targets)

    @property
    def naive_cost(self) -> int:
        """XOR count with no sharing at all: sum over rows of (popcount - 1)."""
        return sum(bin(t).count("1") - 1 for t in self.targets)

    @property
    def distinct_targets(self) -> tuple[int, ...]:
        """Deduplicated targets. Repeated rows are free after the first."""
        seen: dict[int, None] = {}
        for t in self.targets:
            seen.setdefault(t, None)
        return tuple(seen)

    def matrix_rows(self) -> list[list[int]]:
        return [[(t >> i) & 1 for i in range(self.n_inputs)] for t in self.targets]

    def fingerprint(self) -> str:
        """Stable content hash. Two instances with the same hash are the same problem."""
        payload = json.dumps(
            {"n": self.n_inputs, "targets": sorted(self.targets)}, sort_keys=True
        ).encode()
        return hashlib.sha256(payload).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "n_inputs": self.n_inputs,
            "targets": list(self.targets),
            "meta": self.meta,
            "fingerprint": self.fingerprint(),
        }

    @staticmethod
    def from_dict(d: dict) -> "SLPInstance":
        return SLPInstance(
            name=d["name"],
            n_inputs=d["n_inputs"],
            targets=tuple(d["targets"]),
            meta=d.get("meta", {}),
        )

    @staticmethod
    def from_binary_matrix(name: str, rows: Sequence[Sequence[int]], **meta) -> "SLPInstance":
        """Build from an m x n 0/1 matrix given as nested sequences."""
        n = len(rows[0])
        targets = []
        for r in rows:
            if len(r) != n:
                raise ValueError("ragged matrix")
            v = 0
            for i, bit in enumerate(r):
                if bit & 1:
                    v |= 1 << i
            targets.append(v)
        return SLPInstance(name=name, n_inputs=n, targets=tuple(targets), meta=dict(meta))


def apply_program(n_inputs: int, program: Sequence[tuple[int, int]]) -> list[int]:
    """Execute a program symbolically, returning the bitmask of every signal."""
    signals = [1 << i for i in range(n_inputs)]
    for k, (a, b) in enumerate(program):
        idx = n_inputs + k
        if not (0 <= a < idx and 0 <= b < idx):
            raise ValueError(f"op {k} references signal out of range: ({a}, {b})")
        if a == b:
            raise ValueError(f"op {k} is a self-XOR (always zero): ({a}, {b})")
        signals.append(signals[a] ^ signals[b])
    return signals


class VerificationError(AssertionError):
    pass


def verify(instance: SLPInstance, program: Sequence[tuple[int, int]]) -> int:
    """Exactly verify that `program` computes every target row. Returns the gate count.

    This is the ground truth for every claim the project makes. It is deliberately
    independent of any search code: it re-executes the program from scratch.
    """
    signals = apply_program(instance.n_inputs, program)
    available = set(signals)
    missing = [t for t in instance.targets if t not in available]
    if missing:
        raise VerificationError(
            f"{instance.name}: {len(missing)} target(s) not computed, "
            f"e.g. {missing[0]:#0{instance.n_inputs // 4 + 2}x}"
        )
    return len(program)
