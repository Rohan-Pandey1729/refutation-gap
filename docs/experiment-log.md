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

## 20260909T063315-train_oracle_upward-49fc66

THE experiment that matters: train the oracle on SMALL instances (n=8,10,12) and test on LARGE ones (n=15,16,18,20). The exact oracle is cheap at small n and explosive at large n, so a learned replacement is only useful if it generalises upward. Downward generalisation (the first run) proves nothing.

- commit: `62165b1`
- exit code: `0`  |  wall time: 257.9s
- full output: `runs/logs/20260909T063315-train_oracle_upward-49fc66.txt`

```
$ python3 scripts/train_oracle.py --data data/oracle data/oracle_large --train-sizes 8 10 12 --test-sizes 15 16 18 20 --max-iter 300 --max-per-instance 60000
train sizes: [8, 10, 12]   test sizes: [15, 16, 18, 20]
train instances: 27   held-out instances: 36
held out: ['rand_n15_m15_d0.3_s0', 'rand_n15_m15_d0.3_s1', 'rand_n15_m15_d0.3_s2', 'rand_n15_m15_d0.5_s0', 'rand_n15_m15_d0.5_s1', 'rand_n15_m15_d0.5_s2', 'rand_n15_m15_d0.7_s0', 'rand_n15_m15_d0.7_s1', 'rand_n15_m15_d0.7_s2', 'rand_n16_m16_d0.3_s0', 'rand_n16_m16_d0.3_s1', 'rand_n16_m16_d0.3_s2', 'rand_n16_m16_d0.5_s0', 'rand_n16_m16_d0.5_s1', 'rand_n16_m16_d0.5_s2', 'rand_n16_m16_d0.7_s0', 'rand_n16_m16_d0.7_s1', 'rand_n16_m16_d0.7_s2', 'rand_n18_m18_d0.3_s0', 'rand_n18_m18_d0.3_s1', 'rand_n18_m18_d0.3_s2', 'rand_n18_m18_d0.5_s0', 'rand_n18_m18_d0.5_s1', 'rand_n18_m18_d0.5_s2', 'rand_n18_m18_d0.7_s0', 'rand_n18_m18_d0.7_s1', 'rand_n18_m18_d0.7_s2', 'rand_n20_m20_d0.3_s0', 'rand_n20_m20_d0.3_s1', 'rand_n20_m20_d0.3_s2', 'rand_n20_m20_d0.5_s0', 'rand_n20_m20_d0.5_s1', 'rand_n20_m20_d0.5_s2', 'rand_n20_m20_d0.7_s0', 'rand_n20_m20_d0.7_s1', 'rand_n20_m20_d0.7_s2']
train (826243, 30)  test (2160000, 30)  (11.8s to featurize)
positive rate: train 0.0471  test 0.0213

trained in 178.4s
inference: 29.04 us/query  (2,160,000 queries in 62.73s)

constant-'no' accuracy baseline : 0.9787
model accuracy @0.5             : 0.9738
ROC AUC                         : 0.9824
average precision (PR AUC)      : 0.8451   (chance = 0.0213)

 threshold   recall  precision  flagged/query
    0.0009   0.9900     0.0788         0.2675
    0.0182   0.9500     0.1463         0.1382
    0.1201   0.9000     0.2506         0.0764
    0.7905   0.8000     0.6330         0.0269
    1.0000   0.4862     1.0000         0.0103

saved models/oracle.joblib
```

## Finding: upward generalisation, and the cost crossover (train_oracle_upward)

Training on n=8,10,12 and testing on n=15,16,18,20 — the direction that matters —
gives a much weaker picture than the downward split:

| metric | downward (train 10,12 → test 8) | upward (train 8,10,12 → test 15..20) |
|---|---:|---:|
| ROC AUC | 0.9999 | 0.9824 |
| average precision | 0.9994 (chance 0.0874) | 0.8451 (chance 0.0213) |
| recall @ 90% precision | ~0.99 | — |
| precision @ 90% recall | 0.989 | 0.251 |
| accuracy @0.5 | 0.9979 | 0.9738 |
| constant-"no" baseline | 0.9126 | **0.9787** |

Two things to be clear about:

1. **Model accuracy (0.9738) is BELOW the constant-"no" baseline (0.9787).** A
   model that always answered "no" would score higher. This is exactly the trap
   flagged before training, and it is why accuracy is not the metric. Average
   precision of 0.845 against a chance rate of 0.021 is a ~40x lift, so the model
   is far from useless — but it is not a drop-in replacement.

2. **The cost argument currently fails at this scale.** Inference measured
   29.0 us/query. The exact oracle at n=20 averages 3,460 DFS nodes/call, and
   from the n=20 timing (3.65e9 nodes in 8.03 s) a node costs ~2.2 ns, so the
   exact oracle costs ~7.6 us/call. **The learned oracle is ~4x MORE expensive
   than the exact oracle it is supposed to replace, at n=20.**

### What this implies

Replacement is the wrong architecture. Two consequences follow:

- **Use it as a prefilter, not a replacement.** Precision losses cost nothing if
  every flagged query is then confirmed by the exact oracle — only recall losses
  cost quality. At 99% recall the model flags 26.8% of queries (3.7x fewer exact
  calls); at 95% recall, 13.8% (7.2x fewer).
- **There is a crossover in n, and it is above 20.** Exact-oracle cost per call
  grows ~2x per +1 in n in the tail; model cost is roughly flat. Extrapolating,
  crossover sits near n=22-24. The cipher matrices we care about are n=32 and
  n=64, i.e. well past it — but that must be MEASURED, not extrapolated.

Next: measure exact-oracle us/call directly at n up to 32 (AES MixColumns) and
find the actual crossover, and cut model size to move it left.

## 20260909T064226-measure_crossover-dcc596

Decisive cost measurement: is the learned oracle actually cheaper than the exact DFS it replaces, and at what n does that flip? Includes the 32-input cipher matrices we actually care about.

- commit: `140af29`
- exit code: `0`  |  wall time: 75.5s
- full output: `runs/logs/20260909T064226-measure_crossover-dcc596.txt`

```
$ python3 scripts/measure_crossover.py --sizes 8 10 12 14 16 18 20 --ciphers aes_mixcolumns anubis clefia_m1
instance                 n  gates    wall_s        calls   nodes/call    us/call
rand_n8_d0.5             8     15     0.001        4,697         10.9      0.272
rand_n10_d0.5           10     22     0.004       18,150          8.6      0.215
rand_n12_d0.5           12     29     0.005       46,601         43.8      0.114
rand_n14_d0.5           14     36     0.038      120,666         62.6      0.313
rand_n16_d0.5           16     50     0.287      306,327        328.6      0.937
rand_n18_d0.5           18     62     4.336      582,291       2224.6      7.446
rand_n20_d0.5           20     73    12.712    1,054,051       3460.4     12.061
aes_mixcolumns          32     97    11.929    3,970,567        976.7      3.004
anubis                  32    108    12.830    5,645,379        654.4      2.273
clefia_m1               32    110    19.110    6,718,881        800.6      2.844

model inference: 59.561 us/query (featurize 26.903 + predict 32.658)

instance                us/call exact  us/query model    ratio  verdict
rand_n8_d0.5                    0.272          59.561     0.00  exact cheaper
rand_n10_d0.5                   0.215          59.561     0.00  exact cheaper
rand_n12_d0.5                   0.114          59.561     0.00  exact cheaper
rand_n14_d0.5                   0.313          59.561     0.01  exact cheaper
rand_n16_d0.5                   0.937          59.561     0.02  exact cheaper
rand_n18_d0.5                   7.446          59.561     0.13  exact cheaper
rand_n20_d0.5                  12.061          59.561     0.20  exact cheaper
aes_mixcolumns                  3.004          59.561     0.05  exact cheaper
anubis                          2.273          59.561     0.04  exact cheaper
clefia_m1                       2.844          59.561     0.05  exact cheaper
```

## KEY NEGATIVE RESULT: the learned-oracle thesis, as originally stated, is refuted (measure_crossover)

Measured exact-oracle cost per call against measured model inference cost, on the
same machine, including the cipher matrices the project actually targets:

| instance | n | gates | oracle calls | nodes/call | us/call (exact) |
|---|---:|---:|---:|---:|---:|
| rand n=8 d0.5 | 8 | 15 | 4,697 | 10.9 | 0.272 |
| rand n=12 d0.5 | 12 | 29 | 46,601 | 43.8 | 0.114 |
| rand n=16 d0.5 | 16 | 50 | 306,327 | 328.6 | 0.937 |
| rand n=18 d0.5 | 18 | 62 | 582,291 | 2,224.6 | 7.446 |
| rand n=20 d0.5 | 20 | 73 | 1,054,051 | 3,460.4 | 12.061 |
| **aes_mixcolumns** | **32** | **97** | **3,970,567** | **976.7** | **3.004** |
| anubis | 32 | 108 | 5,645,379 | 654.4 | 2.273 |
| clefia_m1 | 32 | 110 | 6,718,881 | 800.6 | 2.844 |

Model inference: **59.56 us/query** (26.9 featurize + 32.7 sklearn predict).

**The exact oracle is cheaper than the learned oracle at every size measured**,
by 5x at n=20 and by 20x on AES MixColumns. The original thesis — replace the
oracle with a cheap learned estimator — does not survive contact with the
measurement.

### Two things the measurement revealed

**1. Structure makes the exact oracle dramatically cheaper.** AES MixColumns at
n=32 needs 977 DFS nodes/call; a *random* matrix at n=20 needs 3,460. The
cryptographic matrices are far easier per call than random matrices of similar or
smaller size, because their algebraic structure keeps distances small. Random
benchmark instances are a misleading proxy for the real targets — the earlier
n=8..20 scaling table, taken alone, overstated the difficulty of the real problem.

**2. The bottleneck claim is still true; the proposed fix was wrong.** BP does
3.97M oracle calls on AES at ~3 us each, which is essentially the entire 11.9 s
runtime. The oracle *is* where the time goes. But its per-call cost is small, so
a per-query learned replacement must cost under ~2 us to pay. Python featurization
plus sklearn inference costs 30x that. A C-compiled small ensemble might reach
~0.3 us, leaving perhaps 10x headroom — real, but far less than assumed.

### Redirect

The better target for learning is not the oracle's ANSWER but the search's
CANDIDATE SET. BP evaluates every pair of signals against every unsolved target
each step: on AES that is millions of oracle calls, the overwhelming majority on
pairs that are obviously useless. A model that ranks candidate PAIRS amortises
one inference over many queries, instead of competing with a 3 us DFS on every
single query.

That is the next experiment. This negative result is kept in full, and in the
paper: the dead end is the finding.

## 20260909T064813-candidate_ranking_free_baseline-7f6130

Establish the FREE baseline before any learning: rank candidate pairs by the number of targets satisfying popcount(t^u) <= dist-1, a sufficient condition for a reduction since g <= popcount. Measures recall@K, i.e. how often an optimal candidate lands in the top K.

- commit: `d599686` **(dirty tree)**
- exit code: `0`  |  wall time: 37.3s
- full output: `runs/logs/20260909T064813-candidate_ranking_free_baseline-7f6130.txt`

```
$ python3 scripts/eval_candidate_ranking.py --sizes 12 14 16 --instances anubis clefia_m1
instance              steps  cands/step     r@1     r@2     r@3     r@5    r@10    r@20    r@50   r@100  frac@best
rand_n12                 29       317.5   0.793   0.793   0.793   0.828   0.931   0.966   0.966   0.966     0.0445
rand_n14                 36       480.8   0.611   0.639   0.639   0.694   0.778   0.833   0.889   0.889     0.0344
rand_n16                 50       829.0   0.600   0.640   0.700   0.740   0.800   0.840   0.880   0.900     0.0278
anubis                  108      3937.2   0.787   0.787   0.787   0.787   0.833   0.843   0.870   0.889     0.0194
clefia_m1               110      4035.7   0.809   0.818   0.827   0.827   0.864   0.882   0.882   0.891     0.0138
```

## Finding: the free candidate prefilter (eval_topk)

Restricting each BP step to the ~K candidates surviving the free sufficient
condition `popcount(t XOR u) <= dist[t]-1`:

| instance | n | full BP | K=200 | K=50 | K=20 | K=10 | K=5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rand n=16 d0.5 | 16 | 50 | 50 | 50 | 52 | 51 | 51 |
| rand n=18 d0.5 | 18 | 62 | 62 | 62 | 64 | 64 | 65 |
| rand n=20 d0.5 | 20 | 73 | 73 | 73 | 75 | 75 | 75 |
| aes_mixcolumns | 32 | 97 | 97 | 100 | 100 | 101 | 101 |
| **anubis** | 32 | **108** | 108 | **106** | 108 | 110 | 112 |
| clefia_m1 | 32 | 110 | 110 | — | — | — | — |

Two results:

**1. The prefilter is a diversifier, not just a speedup.** On ANUBIS, K=50 and
K=100 reach **106 gates, two better than unrestricted BP's 108** — and 106 is
exactly the published Boyar-Peralta value (Kranz et al. 2017, via Xiang et al.
Table 1). Restricting the candidate set changes which of several tied candidates
the greedy takes, and on this instance that lands in a better basin. This is
cheap diversification, and it motivates the portfolio search.

**2. Cost/quality is instance-dependent and not uniformly favourable.** On AES,
K=5 gives a 4.8x wall-clock speedup (2.65 s vs 12.68 s) and 11.5x fewer oracle
calls, at a cost of 4 gates. On ANUBIS, the K=100 run was *slower* in wall time
(68.9 s vs 12.8 s) despite 12% fewer oracle calls, because the different
trajectory keeps target distances larger for longer and the surviving oracle
calls are individually much more expensive. Fewer oracle calls does not imply
less oracle work.

Note also that our unrestricted BP gives CLEFIA M1 = 110 against the published
BP value of 111, and ANUBIS = 108 against 106. BP's tie-breaking rule is
unspecified in the published work, so our implementation differs in both
directions; this is the reference-vs-exact distinction already recorded in
RESULTS.md.

## PRIOR-ART CHECK OVERTURNS TWO OF TONIGHT'S DIRECTIONS

A novelty verification pass (88 tool calls, primary sources only) found that both
of the directions taken tonight are substantially prior art:

1. **SAT-based optimality for SLP over GF(2) is from 2010** — Fuhs &
   Schneider-Kamp, SAT 2010. Same decision problem, same reduction, same purpose.
   Stoffelen (FSE 2016) applied it to *linear* matrices too; this project had
   assumed that work was confined to nonlinear S-boxes, which was backwards.
2. **Accelerating BP by cutting distance-oracle work is published** — Sun, Yang
   & Li, ePrint 2025/1493, whose Lemma 1 is an exact necessary-and-sufficient
   condition (strictly stronger than tonight's one-sided popcount filter) with a
   reported 200–280x speedup.

Full detail and citations are in SOURCES.md sections 6b and 6c.

### What this leaves

Three things survive the check as genuinely open, all confirmed absent from the
literature by an independent pass:

- No published lower bound for AES MixColumns or any MDS/cipher diffusion matrix.
- No published exact g-XOR optima for random GF(2) matrices.
- No exact g-XOR results above roughly 8 inputs / ~13 gates — the 2010 solver
  wall has apparently never been revisited with a modern solver.

So the surviving contribution is **coverage and scale, not method**: a systematic
measurement of how far standard SLP heuristics sit above the true optimum, on
instance classes and at sizes nobody has closed before. That is a real but modest
empirical contribution, and it must be framed that way.

Tonight's three substantive results are therefore:
1. A measured refutation of the learned-oracle thesis on cost grounds.
2. A prior-art refutation of the prefilter's novelty.
3. The optimality-gap data, which stands.

## 20260909T072543-aggregate_optimality-3de3ec

Aggregate all SAT optimality proofs

- commit: `a0134eb` **(dirty tree)**
- exit code: `0`  |  wall time: 0.1s
- full output: `runs/logs/20260909T072543-aggregate_optimality-3de3ec.txt`

```
$ python3 scripts/aggregate_optimality.py
# Exact optimality results

Proven-optimal g-XOR counts for small GF(2) matrices, obtained by SAT
(CaDiCaL) descending from a verified heuristic upper bound until UNSAT.

**Prior art.** The SAT-for-SLP method is Fuhs & Schneider-Kamp, SAT 2010;
Stoffelen (FSE 2016) applied it to linear matrices. What is new here is
coverage: exact g-XOR optima for *random* GF(2) matrices, which the
existing exact work (cipher-derived submatrices, or the s-XOR metric on
hand-picked instances) does not cover. See SOURCES.md section 6b.

- instances closed: **55**
- inconclusive (conflict budget exhausted): **5**

## How far are the standard heuristics from optimal?

The upper bound is the best of Paar1, Paar2, Boyar-Peralta and RNBP
(hundreds of randomized restarts). The gap is that value minus the
proven optimum.

| gap (gates above optimum) | instances | share |
|---:|---:|---:|
| 0 | 38 | 69.1% |
| 1 | 17 | 30.9% |

Mean gap: **0.31 gates**. The heuristics are exactly optimal on **38/55** of the instances closed here (69%), and never worse than 1 gate(s) above optimum at these sizes.

## By instance size

| n | closed | heuristic optimal | mean gap | mean solve time |
|---:|---:|---:|---:|---:|
| 6 | 24 | 23/24 | 0.04 | 0.3 s |
| 7 | 24 | 10/24 | 0.58 | 5.2 s |
| 8 | 7 | 5/7 | 0.29 | 8.5 s |

## Full results

| instance | naive | heuristic | via | **optimal** | gap | solve time |
|---|---:|---:|---|---:|---:|---:|
| rand_n6_m6_d0.3_s0 | 10 | 8 | paar1 | **8** | +0 | 0.3 s |

... wrote docs/OPTIMALITY.md (55 closed, 5 inconclusive)
```

## 20260909T073440-regen_results-467012

Regenerate leaderboard after the night's runs

- commit: `d507d64` **(dirty tree)**
- exit code: `0`  |  wall time: 0.1s
- full output: `runs/logs/20260909T073440-regen_results-467012.txt`

```
$ python3 scripts/aggregate.py
# Results

Auto-generated by `scripts/aggregate.py` from `runs/index.jsonl`.
Every number below is a **verified** gate count: the program was re-executed
from scratch by `slp.instance.verify` before being recorded.

## Exact reproduction of published baselines

Paar's algorithm is deterministic, so these must match exactly.
A mismatch here is a bug, not a result.

| instance | method | ours | published | status | source |
|---|---|---:|---:|---|---|
| aes_mixcolumns | bp | 97 | 97 | match | Kranz et al., ToSC 2017(4), Tab. 3 |
| aes_mixcolumns | paar1 | 108 | 108 | match | Kranz et al., ToSC 2017(4), Tab. 3 |
| anubis | paar1 | 121 | 121 | match | Xiang et al., ToSC 2020(2), Tab. 1 |
| clefia_m0 | paar1 | - | 121 | not run | Xiang et al., ToSC 2020(2), Tab. 1 |
| clefia_m1 | paar1 | 121 | 121 | match | Xiang et al., ToSC 2020(2), Tab. 1 |
| khazad | paar1 | 488 | 488 | match | Xiang et al., ToSC 2020(2), Tab. 1 |
| whirlpool | paar1 | 481 | 481 | match | Xiang et al., ToSC 2020(2), Tab. 1 |

## Reference comparison (tie-break sensitive)

Boyar-Peralta's tie-breaking rule is unspecified in the published work,
so differences of a few gates in either direction are expected and are
not bugs.

| instance | method | ours | reference | delta | source |
|---|---|---:|---:|---:|---|
| anubis | bp | 108 | 106 | +2 | Kranz et al. 2017, via Xiang Tab. 1 |
| clefia_m0 | bp | - | 106 | - | Kranz et al. 2017, via Xiang Tab. 1 |
| clefia_m1 | bp | 110 | 111 | -1 | Kranz et al. 2017, via Xiang Tab. 1 |
| khazad | bp | - | 507 | - | Kranz et al. 2017, via Xiang Tab. 1 |
| whirlpool | bp | - | 465 | - | Kranz et al. 2017, via Xiang Tab. 1 |

## Leaderboard

| instance | n | naive | bp | paar1 | paar2 | best (g-XOR) | best published | gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| aes_inv_mixcolumns | 32 | 440 | 121 | 170 | 165 | 121 | 92 (s-XOR) | +29 |
... [5 lines omitted] ...
| whirlpool_0 | 64 | 968 | - | 477 | 463 | 463 | - |  |

## Provenance

- recorded results: **18**
- distinct instances: **7**
- results per method: `bp`=4, `paar1`=7, `paar2`=7
- dirty-tree results: **18** (these must not be used for any published claim)

## AES MixColumns g-XOR record history

| gates | source | method |
|---:|---|---|
| 108 | Satoh et al. ASIACRYPT 2001 / Banik et al. INDOCRYPT 2016 | architectural |
| 103 | Jean, Moradi, Peyrin, Sasdrich, Bit-Sliding, CHES 2017 | heuristic |
| 97 | Kranz, Leander, Stoffelen, Wiemer, ToSC 2017(4) | Boyar-Peralta |
| 95 | Banik, Funabiki, Isobe, IWSEC 2019 | heuristic |
| 94 | Tan & Peyrin, TCHES 2020(1) | A1/A2 heuristics |
| 92 | Maximov, ePrint 2019/833 | dedicated search |
| 91 | Lin, Xiang, Zeng, Zhang, CT-RSA 2021 | framework |
| 89 | Sun, Yang, Li, ePrint 2025/1493 | revisited Boyar-Peralta |
| 88 | Jean, ePrint 2026/1481 | LLM-assisted (OpenAI codex), no method published |

Our search produces **g-XOR** programs. Where the best published figure above is s-XOR, it is still the bar to beat: s-XOR programs are valid g-XOR programs, so an s-XOR count is a g-XOR upper bound.

```

## 20260909T074559-certify_portfolio-c6637d

Symbolically prove (over all 2^n inputs) and emit Lean certificates for the best circuits found overnight.

- commit: `52b8ddc`
- exit code: `0`  |  wall time: 3.5s
- full output: `runs/logs/20260909T074559-certify_portfolio-c6637d.txt`

```
$ python3 -c 
import sys, json, time; sys.path.insert(0,'.')
from pathlib import Path
from slp.benchmarks import registry
from slp.instance import verify
from slp.verify.symbolic import verify_symbolic_fast
from slp.verify.lean_cert import emit
best = json.loads(Path('runs/portfolio_best.json').read_text())
for name, b in sorted(best.items()):
    inst = registry.get(name)
    prog = [tuple(op) for op in b['program']]
    g = verify(inst, prog)
    t0=time.time(); res = verify_symbolic_fast(inst, prog); dt=time.time()-t0
    cert = Path(f'lean/certs/{name}_best_{g}.lean')
    emit(inst, prog, cert, method=f"portfolio k={b['topk']} mode={b['mode']} seed={b['seed']}", run='portfolio_overnight')
    print(f'  {name:20s} {g:4d} gates  bitmask=OK  symbolic={res["z3_result"]} ({dt:.2f}s)  -> {cert}')

  aes_mixcolumns         98 gates  bitmask=OK  symbolic=unsat (proved) (0.35s)  -> lean/certs/aes_mixcolumns_best_98.lean
  anubis                105 gates  bitmask=OK  symbolic=unsat (proved) (0.42s)  -> lean/certs/anubis_best_105.lean
  clefia_m1             110 gates  bitmask=OK  symbolic=unsat (proved) (0.70s)  -> lean/certs/clefia_m1_best_110.lean
```
