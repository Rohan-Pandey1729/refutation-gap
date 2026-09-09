# Experiment log

Append-only record of every command run during this project, in order.

Each entry pins the git commit, the exit code, the wall time, and an excerpt of
the output. The complete verbatim output of every command is in
`runs/logs/<run_id>.txt`, and `runs/commands.jsonl` holds the same records in
machine-readable form.

Everything here was produced by `scripts/logged.py`, which is the only way
commands are run during unattended work:

```bash
python3 scripts/logged.py --tag <name> --note "why" -- <command>
```

Entries marked **(dirty tree)** were run with uncommitted changes present and
must not be used to support a published claim.
