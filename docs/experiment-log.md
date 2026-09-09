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

## 20260909T062942-collect_oracle_large-396059

Collect exact-oracle training data at n=14,16,18 so the learned oracle can be tested on UPWARD generalisation (train small, test large), which is the case that matters: the exact oracle is cheap at small n and explosive at large n.

- commit: `6a74deb`
- exit code: `0`  |  wall time: 162.9s
- full output: `runs/logs/20260909T062942-collect_oracle_large-396059.txt`

```
$ python3 scripts/collect_oracle_data.py --instances --suite random --repeats 1 --out data/oracle_large
  rand_n15_m15_d0.3_s0       rep=0 gates=36 queries=  108,821   1.87s
  -> data/oracle_large/rand_n15_m15_d0.3_s0.npz  108,821 records  pos=2,346 neg=106,475 capped=0
  rand_n15_m15_d0.3_s1       rep=0 gates=32 queries=   73,726   0.47s
  -> data/oracle_large/rand_n15_m15_d0.3_s1.npz  73,726 records  pos=1,296 neg=72,430 capped=0
  rand_n15_m15_d0.3_s2       rep=0 gates=32 queries=   76,198   0.49s
  -> data/oracle_large/rand_n15_m15_d0.3_s2.npz  76,198 records  pos=1,693 neg=74,505 capped=0
  rand_n15_m15_d0.5_s0       rep=0 gates=46 queries=  212,283   0.55s
  -> data/oracle_large/rand_n15_m15_d0.5_s0.npz  212,283 records  pos=4,524 neg=207,759 capped=0
  rand_n15_m15_d0.5_s1       rep=0 gates=46 queries=  194,353   0.87s
  -> data/oracle_large/rand_n15_m15_d0.5_s1.npz  194,353 records  pos=6,482 neg=187,871 capped=0
  rand_n15_m15_d0.5_s2       rep=0 gates=40 queries=  161,887   0.29s
  -> data/oracle_large/rand_n15_m15_d0.5_s2.npz  161,887 records  pos=4,414 neg=157,473 capped=0
  rand_n15_m15_d0.7_s0       rep=0 gates=46 queries=  201,924   0.45s
  -> data/oracle_large/rand_n15_m15_d0.7_s0.npz  201,924 records  pos=6,687 neg=195,237 capped=0
  rand_n15_m15_d0.7_s1       rep=0 gates=43 queries=  168,186   0.84s
  -> data/oracle_large/rand_n15_m15_d0.7_s1.npz  168,186 records  pos=6,588 neg=161,598 capped=0
  rand_n15_m15_d0.7_s2       rep=0 gates=45 queries=  206,450   1.14s
  -> data/oracle_large/rand_n15_m15_d0.7_s2.npz  206,450 records  pos=7,000 neg=199,450 capped=0
  rand_n16_m16_d0.3_s0       rep=0 gates=36 queries=  108,520   0.28s
  -> data/oracle_large/rand_n16_m16_d0.3_s0.npz  108,520 records  pos=1,965 neg=106,555 capped=0
  rand_n16_m16_d0.3_s1       rep=0 gates=38 queries=  134,584   0.33s
  -> data/oracle_large/rand_n16_m16_d0.3_s1.npz  134,584 records  pos=1,978 neg=132,606 capped=0
  rand_n16_m16_d0.3_s2       rep=0 gates=41 queries=  157,853   0.40s
  -> data/oracle_large/rand_n16_m16_d0.3_s2.npz  157,853 records  pos=2,396 neg=155,457 capped=0
  rand_n16_m16_d0.5_s0       rep=0 gates=50 queries=  307,345   0.72s
  -> data/oracle_large/rand_n16_m16_d0.5_s0.npz  307,345 records  pos=5,508 neg=301,837 capped=0
  rand_n16_m16_d0.5_s1       rep=0 gates=50 queries=  298,596   0.70s
  -> data/oracle_large/rand_n16_m16_d0.5_s1.npz  298,596 records  pos=6,761 neg=291,835 capped=0
  rand_n16_m16_d0.5_s2       rep=0 gates=48 queries=  272,364   0.50s
  -> data/oracle_large/rand_n16_m16_d0.5_s2.npz  272,364 records  pos=4,792 neg=267,572 capped=0
  rand_n16_m16_d0.7_s0       rep=0 gates=46 queries=  249,970   0.48s
  -> data/oracle_large/rand_n16_m16_d0.7_s0.npz  249,970 records  pos=8,515 neg=241,455 capped=0
  rand_n16_m16_d0.7_s1       rep=0 gates=48 queries=  258,869   0.60s
  -> data/oracle_large/rand_n16_m16_d0.7_s1.npz  258,869 records  pos=9,191 neg=249,678 capped=0
  rand_n16_m16_d0.7_s2       rep=0 gates=51 queries=  348,669   0.82s
  -> data/oracle_large/rand_n16_m16_d0.7_s2.npz  348,669 records  pos=8,936 neg=339,733 capped=0
  rand_n18_m18_d0.3_s0       rep=0 gates=38 queries=  149,294   0.30s
  -> data/oracle_large/rand_n18_m18_d0.3_s0.npz  149,294 records  pos=2,290 neg=147,004 capped=0
  rand_n18_m18_d0.3_s1       rep=0 gates=54 queries=  439,807   0.67s
  -> data/oracle_large/rand_n18_m18_d0.3_s1.npz  439,807 records  pos=4,819 neg=434,988 capped=0
... [9 lines omitted] ...
  -> data/oracle_large/rand_n18_m18_d0.7_s0.npz  485,447 records  pos=13,167 neg=472,280 capped=0
  rand_n18_m18_d0.7_s1       rep=0 gates=62 queries=  542,137   5.56s
  -> data/oracle_large/rand_n18_m18_d0.7_s1.npz  542,137 records  pos=15,520 neg=526,617 capped=0
  rand_n18_m18_d0.7_s2       rep=0 gates=60 queries=  579,375   2.84s
  -> data/oracle_large/rand_n18_m18_d0.7_s2.npz  579,375 records  pos=14,899 neg=564,476 capped=0
  rand_n20_m20_d0.3_s0       rep=0 gates=59 queries=  522,436   3.54s
  -> data/oracle_large/rand_n20_m20_d0.3_s0.npz  522,436 records  pos=6,232 neg=516,204 capped=0
  rand_n20_m20_d0.3_s1       rep=0 gates=59 queries=  549,408   9.47s
  -> data/oracle_large/rand_n20_m20_d0.3_s1.npz  549,408 records  pos=7,137 neg=542,271 capped=0
  rand_n20_m20_d0.3_s2       rep=0 gates=63 queries=  584,569   4.40s
  -> data/oracle_large/rand_n20_m20_d0.3_s2.npz  584,569 records  pos=6,556 neg=578,013 capped=0
  rand_n20_m20_d0.5_s0       rep=0 gates=74 queries=1,041,962  23.89s
  -> data/oracle_large/rand_n20_m20_d0.5_s0.npz  1,041,962 records  pos=15,405 neg=1,026,557 capped=0
  rand_n20_m20_d0.5_s1       rep=0 gates=76 queries=1,166,317  13.95s
  -> data/oracle_large/rand_n20_m20_d0.5_s1.npz  1,166,317 records  pos=15,236 neg=1,151,081 capped=0
  rand_n20_m20_d0.5_s2       rep=0 gates=77 queries=1,252,925  15.09s
  -> data/oracle_large/rand_n20_m20_d0.5_s2.npz  1,252,925 records  pos=16,229 neg=1,236,696 capped=0
  rand_n20_m20_d0.7_s0       rep=0 gates=75 queries=1,072,558  16.73s
  -> data/oracle_large/rand_n20_m20_d0.7_s0.npz  1,072,558 records  pos=22,047 neg=1,050,511 capped=0
  rand_n20_m20_d0.7_s1       rep=0 gates=77 queries=1,225,713  16.58s
  -> data/oracle_large/rand_n20_m20_d0.7_s1.npz  1,225,713 records  pos=22,735 neg=1,202,978 capped=0
  rand_n20_m20_d0.7_s2       rep=0 gates=70 queries=  925,826   9.37s
  -> data/oracle_large/rand_n20_m20_d0.7_s2.npz  925,826 records  pos=22,091 neg=903,735 capped=0

total records: 16,073,581
```
