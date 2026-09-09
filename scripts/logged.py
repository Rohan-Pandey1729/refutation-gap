#!/usr/bin/env python3
"""Run a command, capture everything, and append an immutable entry to the experiment log.

Everything executed during autonomous work goes through this, so that
docs/experiment-log.md is a complete, ordered record of what was run, when,
against which commit, and what it printed. Full output is kept verbatim in
runs/logs/<id>.txt; the markdown log carries a head/tail excerpt plus a pointer.

Usage:
    python3 scripts/logged.py --tag my_experiment -- python3 scripts/foo.py --bar
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOGDIR = REPO / "runs" / "logs"
MD = REPO / "docs" / "experiment-log.md"
JSONL = REPO / "runs" / "commands.jsonl"

HEAD_LINES = 40
TAIL_LINES = 25


def git(*args):
    try:
        return subprocess.run(["git", "-C", str(REPO), *args],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--note", default="")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd
    if not cmd:
        print("no command given", file=sys.stderr)
        return 2

    LOGDIR.mkdir(parents=True, exist_ok=True)
    MD.parent.mkdir(parents=True, exist_ok=True)
    run_id = f"{time.strftime('%Y%m%dT%H%M%S')}-{args.tag}-{uuid.uuid4().hex[:6]}"
    commit = git("rev-parse", "--short", "HEAD")
    dirty = bool(git("status", "--porcelain"))

    t0 = time.time()
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    elapsed = time.time() - t0

    out = (proc.stdout or "") + (("\n--- stderr ---\n" + proc.stderr) if proc.stderr else "")
    (LOGDIR / f"{run_id}.txt").write_text(
        f"$ {' '.join(cmd)}\n# commit {commit} dirty={dirty}\n"
        f"# exit {proc.returncode} in {elapsed:.1f}s\n\n{out}")

    lines = out.splitlines()
    if len(lines) <= HEAD_LINES + TAIL_LINES:
        excerpt = "\n".join(lines)
    else:
        excerpt = "\n".join(lines[:HEAD_LINES] +
                            [f"... [{len(lines) - HEAD_LINES - TAIL_LINES} lines omitted] ..."] +
                            lines[-TAIL_LINES:])

    with MD.open("a") as fh:
        fh.write(f"\n## {run_id}\n\n")
        if args.note:
            fh.write(f"{args.note}\n\n")
        fh.write(f"- commit: `{commit}`{' **(dirty tree)**' if dirty else ''}\n")
        fh.write(f"- exit code: `{proc.returncode}`  |  wall time: {elapsed:.1f}s\n")
        fh.write(f"- full output: `runs/logs/{run_id}.txt`\n\n")
        fh.write("```\n$ " + " ".join(cmd) + "\n" + excerpt + "\n```\n")

    with JSONL.open("a") as fh:
        fh.write(json.dumps({"run_id": run_id, "tag": args.tag, "cmd": cmd,
                             "commit": commit, "dirty": dirty, "exit": proc.returncode,
                             "seconds": elapsed, "ts": time.time(),
                             "note": args.note}) + "\n")

    sys.stdout.write(out)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
