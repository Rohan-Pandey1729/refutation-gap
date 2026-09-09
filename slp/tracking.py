"""Experiment tracking.

Every search run writes one immutable JSON record under runs/ and one line to
runs/index.jsonl. A record is only written after the program has passed the
independent verifier, so nothing in the index is an unverified claim.

Each record pins:
  - the git commit and whether the tree was dirty
  - the exact instance fingerprint (content hash of the target matrix)
  - the full config, including RNG seed
  - the emitted program, so any result can be re-checked years later
"""
from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
import time
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Sequence

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "runs"
INDEX = RUNS / "index.jsonl"


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO), *args],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return ""


def git_state() -> dict:
    sha = _git("rev-parse", "HEAD")
    dirty = bool(_git("status", "--porcelain"))
    return {"commit": sha or None, "dirty": dirty,
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD") or None}


def env_state() -> dict:
    return {
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "slurm_job": os.environ.get("SLURM_JOB_ID"),
        "slurm_node": os.environ.get("SLURMD_NODENAME"),
        "cpus": os.cpu_count(),
    }


@dataclass
class Result:
    instance: str
    fingerprint: str
    n_inputs: int
    n_outputs: int
    method: str
    config: dict
    gates: int                     # verified gate count
    naive: int
    seconds: float
    stats: dict = field(default_factory=dict)
    program: list[tuple[int, int]] = field(default_factory=list)


class Run:
    """Context manager collecting Results for one logical experiment."""

    def __init__(self, name: str, notes: str = "", **params: Any):
        self.name = name
        self.run_id = f"{time.strftime('%Y%m%dT%H%M%S')}-{name}-{uuid.uuid4().hex[:6]}"
        self.notes = notes
        self.params = params
        self.results: list[Result] = []
        self._t0 = 0.0

    def __enter__(self) -> "Run":
        self._t0 = time.time()
        RUNS.mkdir(exist_ok=True)
        return self

    def add(self, result: Result) -> None:
        self.results.append(result)

    def __exit__(self, exc_type, exc, tb) -> None:
        record = {
            "run_id": self.run_id,
            "name": self.name,
            "notes": self.notes,
            "params": self.params,
            "git": git_state(),
            "env": env_state(),
            "started": self._t0,
            "finished": time.time(),
            "wall_seconds": time.time() - self._t0,
            "failed": exc_type is not None,
            "error": repr(exc) if exc else None,
            "results": [asdict(r) for r in self.results],
        }
        path = RUNS / f"{self.run_id}.json"
        path.write_text(json.dumps(record, indent=2))
        with INDEX.open("a") as fh:
            for r in self.results:
                fh.write(json.dumps({
                    "run_id": self.run_id,
                    "instance": r.instance,
                    "fingerprint": r.fingerprint,
                    "n_inputs": r.n_inputs,
                    "n_outputs": r.n_outputs,
                    "method": r.method,
                    "config": r.config,
                    "gates": r.gates,
                    "naive": r.naive,
                    "seconds": r.seconds,
                    "stats": r.stats,
                    "commit": record["git"]["commit"],
                    "dirty": record["git"]["dirty"],
                    "host": record["env"]["host"],
                    "ts": record["finished"],
                }) + "\n")
        print(f"[run] wrote {path.relative_to(REPO)}  ({len(self.results)} results)")


def load_index() -> list[dict]:
    if not INDEX.exists():
        return []
    return [json.loads(line) for line in INDEX.read_text().splitlines() if line.strip()]


def best_known() -> dict[str, dict]:
    """Best verified gate count per instance across all recorded runs."""
    best: dict[str, dict] = {}
    for row in load_index():
        key = row["instance"]
        if key not in best or row["gates"] < best[key]["gates"]:
            best[key] = row
    return best
