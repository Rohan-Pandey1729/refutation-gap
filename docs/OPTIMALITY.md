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
| rand_n6_m6_d0.3_s0 | 10 | 8 | paar1 | **8** | +0 | 0.5 s |
| rand_n6_m6_d0.3_s1 | 6 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s1 | 6 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s2 | 7 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s2 | 7 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s3 | 5 | 4 | paar1 | **4** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s4 | 7 | 4 | paar1 | **4** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s0 | 17 | 9 | paar1 | **9** | +0 | 0.6 s |
| rand_n6_m6_d0.5_s0 | 17 | 9 | paar1 | **9** | +0 | 0.8 s |
| rand_n6_m6_d0.5_s1 | 15 | 7 | bp | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s1 | 15 | 7 | bp | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s2 | 18 | 8 | paar1 | **8** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s2 | 18 | 8 | paar1 | **8** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s3 | 14 | 10 | paar2 | **9** | +1 | 1.6 s |
| rand_n6_m6_d0.5_s4 | 15 | 8 | bp | **8** | +0 | 0.1 s |
| rand_n6_m6_d0.7_s0 | 18 | 9 | bp | **9** | +0 | 0.2 s |
| rand_n6_m6_d0.7_s0 | 18 | 9 | bp | **9** | +0 | 0.2 s |
| rand_n6_m6_d0.7_s1 | 24 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.7_s1 | 24 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.7_s2 | 15 | 8 | paar1 | **8** | +0 | 0.4 s |
| rand_n6_m6_d0.7_s2 | 15 | 8 | paar1 | **8** | +0 | 0.7 s |
| rand_n6_m6_d0.7_s3 | 16 | 8 | rnbp | **8** | +0 | 0.3 s |
| rand_n6_m6_d0.7_s4 | 19 | 9 | bp | **9** | +0 | 0.2 s |
| rand_n7_m7_d0.3_s0 | 7 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s0 | 7 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s1 | 4 | 4 | paar1 | **4** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s1 | 4 | 4 | paar1 | **4** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s2 | 10 | 8 | paar1 | **8** | +0 | 0.3 s |
| rand_n7_m7_d0.3_s2 | 10 | 8 | paar1 | **8** | +0 | 0.4 s |
| rand_n7_m7_d0.3_s3 | 11 | 7 | paar2 | **7** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s4 | 13 | 8 | paar1 | **8** | +0 | 0.6 s |
| rand_n7_m7_d0.5_s0 | 22 | 11 | paar1 | **10** | +1 | 2.1 s |
| rand_n7_m7_d0.5_s0 | 22 | 11 | paar1 | **10** | +1 | 3.3 s |
| rand_n7_m7_d0.5_s1 | 22 | 11 | bp | **10** | +1 | 4.4 s |
| rand_n7_m7_d0.5_s1 | 22 | 11 | bp | **10** | +1 | 6.9 s |
| rand_n7_m7_d0.5_s2 | 19 | 12 | paar1 | **11** | +1 | 30.4 s |
| rand_n7_m7_d0.5_s2 | 19 | 12 | paar1 | **11** | +1 | 45.9 s |
| rand_n7_m7_d0.5_s3 | 13 | 9 | paar2 | **9** | +0 | 3.2 s |
| rand_n7_m7_d0.5_s4 | 14 | 8 | rnbp | **8** | +0 | 0.5 s |
| rand_n7_m7_d0.7_s0 | 27 | 12 | paar2 | **11** | +1 | 4.9 s |
| rand_n7_m7_d0.7_s0 | 27 | 12 | paar2 | **11** | +1 | 7.0 s |
| rand_n7_m7_d0.7_s1 | 29 | 10 | rnbp | **9** | +1 | 0.1 s |
| rand_n7_m7_d0.7_s1 | 29 | 10 | rnbp | **9** | +1 | 0.2 s |
| rand_n7_m7_d0.7_s2 | 27 | 11 | bp | **10** | +1 | 2.5 s |
| rand_n7_m7_d0.7_s2 | 27 | 11 | bp | **10** | +1 | 3.7 s |
| rand_n7_m7_d0.7_s3 | 30 | 10 | bp | **9** | +1 | 0.3 s |
| rand_n7_m7_d0.7_s4 | 19 | 11 | bp | **10** | +1 | 8.0 s |
| rand_n8_m8_d0.3_s0 | 14 | 11 | paar1 | **10** | +1 | 9.9 s |
| rand_n8_m8_d0.3_s0 | 14 | 11 | paar1 | **10** | +1 | 14.3 s |
| rand_n8_m8_d0.3_s1 | 13 | 10 | bp | **10** | +0 | 12.5 s |
| rand_n8_m8_d0.3_s1 | 13 | 10 | bp | **10** | +0 | 15.5 s |
| rand_n8_m8_d0.3_s2 | 12 | 9 | paar1 | **9** | +0 | 1.8 s |
| rand_n8_m8_d0.3_s2 | 12 | 9 | paar1 | **9** | +0 | 2.7 s |
| rand_n8_m8_d0.3_s4 | 10 | 9 | paar1 | **9** | +0 | 2.8 s |

## Inconclusive

Conflict budget exhausted. Neither SAT nor UNSAT, so these establish
nothing and are recorded only for completeness.

| instance | naive | heuristic | stalled at k |
|---|---:|---:|---:|
| rand_n8_m8_d0.5_s0 | 28 | 14 | 13 |
| rand_n8_m8_d0.5_s1 | 21 | 12 | 11 |
| rand_n8_m8_d0.5_s2 | 20 | 15 | 13 |
| rand_n8_m8_d0.3_s3 | 18 | 12 | 11 |
| rand_n8_m8_d0.5_s3 | 22 | 11 | 10 |
