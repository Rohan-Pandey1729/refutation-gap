# Running on Hyak (klone)

## One-time setup

```bash
ssh klone.hyak.uw.edu
git clone <your-remote> slp-search && cd slp-search
python3 -c "import sys; sys.path.insert(0,'.'); from slp import native; print('core built')"
```

The C core is compiled on first import and cached as `slp/libslp.so`. It is
rebuilt automatically whenever `slp/core.c` is newer, so a stale `.so` on a
shared filesystem cannot silently produce old results.

## Fill in your account

Both `.sbatch` files have `--account=CHANGE_ME`. Set it to your group's
allocation (`hyakalloc` lists what you can charge to). `--partition=ckpt` is
the free preemptable partition; jobs there can be killed and requeued, which
is fine because every run writes its own immutable record.

## Submit

```bash
sbatch scripts/slurm/baselines.sbatch                 # one task per cipher matrix
RESTARTS=2000 sbatch scripts/slurm/sweep.sbatch       # randomized-restart sweep
```

## Collect

`runs/index.jsonl` is append-only, so parallel array tasks can write to it
concurrently on a POSIX filesystem as long as each line is a single small
write. After the jobs finish:

```bash
python3 scripts/aggregate.py     # regenerates RESULTS.md
```

## Reproducing any recorded number

Each `runs/*.json` pins the git commit, the instance fingerprint, the seed and
the full emitted program. To re-check a result without re-running the search:

```bash
python3 scripts/recheck.py runs/<file>.json
```
