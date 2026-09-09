"""ctypes bindings to the C search core, with automatic rebuild."""
from __future__ import annotations

import ctypes
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SRC = _HERE / "core.c"
_LIB = _HERE / "libslp.so"

PROG_CAP = 200_000


def _build() -> None:
    for flags in (["-O3", "-march=native"], ["-O3"]):
        cmd = ["gcc", *flags, "-shared", "-fPIC", "-o", str(_LIB), str(_SRC)]
        if subprocess.run(cmd, capture_output=True).returncode == 0:
            return
    raise RuntimeError("failed to compile slp/core.c")


def _load() -> ctypes.CDLL:
    if not _LIB.exists() or _LIB.stat().st_mtime < _SRC.stat().st_mtime:
        _build()
    lib = ctypes.CDLL(str(_LIB))
    u64p = ctypes.POINTER(ctypes.c_uint64)
    intp = ctypes.POINTER(ctypes.c_int)
    lib.slp_paar.argtypes = [ctypes.c_int, ctypes.c_int, u64p, ctypes.c_int, intp, ctypes.c_int]
    lib.slp_paar.restype = ctypes.c_int
    lib.slp_bp.argtypes = [ctypes.c_int, ctypes.c_int, u64p, ctypes.c_int,
                           ctypes.c_longlong, intp, ctypes.c_int]
    lib.slp_bp.restype = ctypes.c_int
    lib.slp_bp_topk.argtypes = [ctypes.c_int, ctypes.c_int, u64p, ctypes.c_int,
                                ctypes.c_longlong, ctypes.c_int, intp, ctypes.c_int]
    lib.slp_bp_topk.restype = ctypes.c_int
    lib.slp_gval.argtypes = [ctypes.c_int, ctypes.c_uint64, u64p, ctypes.c_int,
                             ctypes.c_int, ctypes.c_longlong]
    lib.slp_gval.restype = ctypes.c_int
    lib.slp_seed.argtypes = [ctypes.c_uint64]
    lib.slp_log_begin.argtypes = [ctypes.POINTER(ctypes.c_longlong), ctypes.c_longlong]
    lib.slp_log_len.restype = ctypes.c_longlong
    lib.slp_log_end.argtypes = []
    lib.slp_clog_begin.argtypes = [ctypes.POINTER(ctypes.c_longlong), ctypes.c_longlong]
    lib.slp_clog_len.restype = ctypes.c_longlong
    lib.slp_clog_end.argtypes = []
    lib.slp_reset_stats.argtypes = []
    lib.slp_get_stats.argtypes = [ctypes.POINTER(ctypes.c_double)]
    return lib


LIB = _load()


def _targets_array(targets):
    arr = (ctypes.c_uint64 * len(targets))(*targets)
    return arr


def _prog_buffer():
    return (ctypes.c_int * (2 * PROG_CAP))()


def _to_pairs(buf, nops):
    return [(buf[2 * k], buf[2 * k + 1]) for k in range(nops)]


def get_stats() -> dict:
    out = (ctypes.c_double * 4)()
    LIB.slp_get_stats(out)
    return {
        "oracle_calls": int(out[0]),
        "oracle_nodes": int(out[1]),
        "pair_evals": int(out[2]),
        "core_seconds": float(out[3]),
    }


def reset_stats() -> None:
    LIB.slp_reset_stats()


def seed(value: int) -> None:
    LIB.slp_seed(ctypes.c_uint64(value & 0xFFFFFFFFFFFFFFFF))


def paar(n_inputs: int, targets, mode: int = 0):
    buf = _prog_buffer()
    nops = LIB.slp_paar(n_inputs, len(targets), _targets_array(targets), mode, buf, 2 * PROG_CAP)
    if nops < 0:
        raise RuntimeError("slp_paar failed (capacity or bad input)")
    return _to_pairs(buf, nops)


def boyar_peralta(n_inputs: int, targets, mode: int = 0, node_cap: int = 0):
    buf = _prog_buffer()
    nops = LIB.slp_bp(n_inputs, len(targets), _targets_array(targets), mode,
                      ctypes.c_longlong(node_cap), buf, 2 * PROG_CAP)
    if nops < 0:
        raise RuntimeError("slp_bp failed (capacity or bad input)")
    return _to_pairs(buf, nops)


def boyar_peralta_topk(n_inputs: int, targets, mode: int = 0, node_cap: int = 0,
                       topk: int = 100):
    """BP restricted each step to the ~topk candidates surviving the free prefilter."""
    buf = _prog_buffer()
    nops = LIB.slp_bp_topk(n_inputs, len(targets), _targets_array(targets), mode,
                           ctypes.c_longlong(node_cap), topk, buf, 2 * PROG_CAP)
    if nops < 0:
        raise RuntimeError("slp_bp_topk failed")
    return _to_pairs(buf, nops)


def gval(n_inputs: int, x: int, added, ub: int, node_cap: int = 0) -> int:
    arr = (ctypes.c_uint64 * max(1, len(added)))(*(added or [0]))
    return LIB.slp_gval(n_inputs, ctypes.c_uint64(x), arr, len(added), ub,
                        ctypes.c_longlong(node_cap))


def boyar_peralta_logged(n_inputs: int, targets, mode: int = 0, node_cap: int = 0,
                         log_cap: int = 40_000_000):
    """Run BP while logging every distance-oracle query.

    Returns (program, records) where records is a list of
    (step, x, budget, label) tuples. `step` is the length of the program prefix
    that defines the added-set at query time, so the search state for any record
    is exactly `program[:step]`. label is 1 / 0 / -1 (reachable / not / capped).
    """
    buf = (ctypes.c_longlong * log_cap)()
    LIB.slp_log_begin(buf, log_cap)
    try:
        prog = boyar_peralta(n_inputs, targets, mode, node_cap)
        n = LIB.slp_log_len()
    finally:
        LIB.slp_log_end()
    records = [(buf[i], buf[i + 1], buf[i + 2], buf[i + 3]) for i in range(0, n, 4)]
    return prog, records


def boyar_peralta_candidates(n_inputs: int, targets, mode: int = 0, node_cap: int = 0,
                             log_cap: int = 60_000_000):
    """Run BP while logging every scored CANDIDATE pair.

    Returns (program, records) where each record is (step, u, total, base):
    at that step, adding signal u would leave the summed target distance at
    `total`, against `base` before any addition. The step's chosen candidate is
    the one minimising `total`.
    """
    buf = (ctypes.c_longlong * log_cap)()
    LIB.slp_clog_begin(buf, log_cap)
    try:
        prog = boyar_peralta(n_inputs, targets, mode, node_cap)
        n = LIB.slp_clog_len()
    finally:
        LIB.slp_clog_end()
    return prog, [(buf[i], buf[i+1], buf[i+2], buf[i+3]) for i in range(0, n, 4)]
