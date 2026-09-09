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

## 20260909T062403-train_oracle_v1-d5e67d

First learned-oracle training run. Held-out split is by INSTANCE, not by random row: the question is whether the oracle generalises to an unseen matrix. Data: 27 random instances n=8,10,12.

- commit: `d23da70`
- exit code: `0`  |  wall time: 247.6s
- full output: `runs/logs/20260909T062403-train_oracle_v1-d5e67d.txt`

```
$ python3 scripts/train_oracle.py --data data/oracle --holdout-frac 0.3 --max-iter 300
train instances: 19   held-out instances: 8
held out: ['rand_n8_m8_d0.3_s1', 'rand_n8_m8_d0.3_s2', 'rand_n8_m8_d0.5_s0', 'rand_n8_m8_d0.5_s1', 'rand_n8_m8_d0.5_s2', 'rand_n8_m8_d0.7_s0', 'rand_n8_m8_d0.7_s1', 'rand_n8_m8_d0.7_s2']
train (1021576, 30)  test (58508, 30)  (4.3s to featurize)
positive rate: train 0.0434  test 0.0874

trained in 237.4s
inference: 48.82 us/query  (58,508 queries in 2.86s)

constant-'no' accuracy baseline : 0.9126
model accuracy @0.5             : 0.9979
ROC AUC                         : 0.9999
average precision (PR AUC)      : 0.9994   (chance = 0.0874)

 threshold   recall  precision  flagged/query
    0.7274   0.9896     0.9891         0.0875
    0.9999   0.9496     1.0000         0.0830
    1.0000   0.8943     1.0000         0.0782
    1.0000   0.7938     1.0000         0.0694
    1.0000   0.5000     1.0000         0.0437

saved models/oracle.joblib
```

## Note on the first oracle training run (train_oracle_v1)

The default holdout is lexicographic over filenames, which put `rand_n8_*` last
and therefore trained on n=10,12 and tested on n=8. That measures **downward**
generalisation, which is the easy direction and not the one that matters: the
exact oracle is cheap at small n (11 DFS nodes/call at n=8) and explosive at
large n (3,460 nodes/call at n=20), so a learned replacement is only valuable if
it generalises **upward**.

The headline numbers from that run (ROC AUC 0.9999, average precision 0.9994
against a 0.0874 chance rate, 98.96% recall at 98.91% precision) are therefore
**not** evidence for the claim we care about. `--train-sizes` / `--test-sizes`
were added to run the correct experiment once larger-n data is collected.

Second caveat from the same run: inference measured 48.8 us/query, which is
*more* expensive than the exact oracle at n=8. The cost argument only holds at
larger n. Model size needs to come down (fewer trees, fewer leaves) and that
tradeoff needs measuring, not assuming.
