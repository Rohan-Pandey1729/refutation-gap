# Exact optimality results

Proven-optimal g-XOR counts for small GF(2) matrices, obtained by SAT
(CaDiCaL) descending from a verified heuristic upper bound until UNSAT.

**Prior art.** The SAT-for-SLP method is Fuhs & Schneider-Kamp, SAT 2010;
Stoffelen (FSE 2016) applied it to linear matrices. What is new here is
coverage: exact g-XOR optima for *random* GF(2) matrices, which the
existing exact work (cipher-derived submatrices, or the s-XOR metric on
hand-picked instances) does not cover. See SOURCES.md section 6b.

- instances closed: **125**
- inconclusive (conflict budget exhausted): **22**

## How far are the standard heuristics from optimal?

The upper bound is the best of Paar1, Paar2, Boyar-Peralta and RNBP
(hundreds of randomized restarts). The gap is that value minus the
proven optimum.

| gap (gates above optimum) | instances | share |
|---:|---:|---:|
| 0 | 101 | 80.8% |
| 1 | 23 | 18.4% |
| 2 | 1 | 0.8% |

Mean gap: **0.20 gates**. The heuristics are exactly optimal on **101/125** of the instances closed here (81%), and never worse than 2 gate(s) above optimum at these sizes.

## By instance size

| n | closed | heuristic optimal | mean gap | mean solve time |
|---:|---:|---:|---:|---:|
| 6 | 60 | 56/60 | 0.07 | 0.2 s |
| 7 | 54 | 38/54 | 0.30 | 6.7 s |
| 8 | 9 | 5/9 | 0.56 | 17.7 s |
| 9 | 2 | 2/2 | 0.00 | 45.0 s |

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
| rand_n6_m6_d0.3_s5 | 7 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s6 | 5 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s7 | 5 | 4 | paar1 | **4** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s8 | 9 | 7 | paar1 | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s9 | 8 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s10 | 3 | 3 | paar1 | **3** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s11 | 6 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s12 | 5 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s13 | 7 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s14 | 6 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s15 | 6 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.3_s16 | 9 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.4_s5 | 9 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.4_s6 | 7 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.4_s7 | 13 | 8 | paar1 | **8** | +0 | 0.2 s |
| rand_n6_m6_d0.4_s8 | 10 | 7 | paar1 | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.4_s9 | 9 | 7 | paar1 | **7** | +0 | 0.1 s |
| rand_n6_m6_d0.4_s10 | 13 | 8 | bp | **8** | +0 | 0.2 s |
| rand_n6_m6_d0.4_s11 | 14 | 8 | paar1 | **8** | +0 | 0.1 s |
| rand_n6_m6_d0.4_s12 | 11 | 7 | bp | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.4_s13 | 6 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.4_s14 | 8 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.4_s15 | 5 | 4 | paar1 | **4** | +0 | 0.0 s |
| rand_n6_m6_d0.4_s16 | 10 | 8 | paar1 | **7** | +1 | 0.0 s |
| rand_n6_m6_d0.5_s0 | 17 | 9 | paar1 | **9** | +0 | 0.6 s |
| rand_n6_m6_d0.5_s0 | 17 | 9 | paar1 | **9** | +0 | 0.8 s |
| rand_n6_m6_d0.5_s1 | 15 | 7 | bp | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s1 | 15 | 7 | bp | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s2 | 18 | 8 | paar1 | **8** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s2 | 18 | 8 | paar1 | **8** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s3 | 14 | 10 | paar2 | **9** | +1 | 1.6 s |
| rand_n6_m6_d0.5_s4 | 15 | 8 | bp | **8** | +0 | 0.1 s |
| rand_n6_m6_d0.5_s5 | 11 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s6 | 12 | 7 | paar1 | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s7 | 14 | 9 | paar1 | **8** | +1 | 0.1 s |
| rand_n6_m6_d0.5_s8 | 11 | 8 | paar1 | **8** | +0 | 0.5 s |
| rand_n6_m6_d0.5_s9 | 11 | 7 | paar1 | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s10 | 14 | 9 | paar1 | **9** | +0 | 0.9 s |
| rand_n6_m6_d0.5_s11 | 7 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s12 | 15 | 9 | paar1 | **9** | +0 | 0.6 s |
| rand_n6_m6_d0.5_s13 | 15 | 8 | paar1 | **7** | +1 | 0.0 s |
| rand_n6_m6_d0.5_s14 | 12 | 7 | bp | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s15 | 13 | 7 | paar1 | **7** | +0 | 0.0 s |
| rand_n6_m6_d0.5_s16 | 13 | 8 | bp | **8** | +0 | 0.1 s |
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
| rand_n7_m7_d0.3_s5 | 7 | 5 | paar1 | **5** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s6 | 10 | 8 | paar1 | **8** | +0 | 0.4 s |
| rand_n7_m7_d0.3_s7 | 3 | 3 | paar1 | **3** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s8 | 3 | 3 | paar1 | **3** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s9 | 8 | 7 | paar1 | **7** | +0 | 0.1 s |
| rand_n7_m7_d0.3_s10 | 10 | 7 | paar1 | **7** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s11 | 10 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s12 | 7 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s13 | 10 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s14 | 11 | 9 | paar1 | **9** | +0 | 4.0 s |
| rand_n7_m7_d0.3_s15 | 8 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n7_m7_d0.3_s16 | 11 | 8 | paar1 | **8** | +0 | 0.2 s |
| rand_n7_m7_d0.4_s5 | 11 | 7 | bp | **7** | +0 | 0.0 s |
| rand_n7_m7_d0.4_s6 | 13 | 9 | paar2 | **8** | +1 | 0.3 s |
| rand_n7_m7_d0.4_s7 | 15 | 10 | bp | **10** | +0 | 9.2 s |
| rand_n7_m7_d0.4_s8 | 17 | 11 | paar2 | **11** | +0 | 78.1 s |
| rand_n7_m7_d0.4_s9 | 21 | 10 | bp | **10** | +0 | 3.3 s |
| rand_n7_m7_d0.4_s10 | 18 | 9 | paar2 | **9** | +0 | 1.0 s |
| rand_n7_m7_d0.4_s11 | 16 | 8 | bp | **8** | +0 | 0.2 s |
| rand_n7_m7_d0.4_s12 | 9 | 6 | paar1 | **6** | +0 | 0.0 s |
| rand_n7_m7_d0.4_s13 | 16 | 11 | bp | **11** | +0 | 102.2 s |
| rand_n7_m7_d0.4_s14 | 12 | 8 | paar1 | **8** | +0 | 0.2 s |
| rand_n7_m7_d0.4_s15 | 9 | 8 | paar1 | **8** | +0 | 1.0 s |
| rand_n7_m7_d0.4_s16 | 12 | 8 | paar1 | **8** | +0 | 0.1 s |
| rand_n7_m7_d0.5_s0 | 22 | 11 | paar1 | **10** | +1 | 2.1 s |
| rand_n7_m7_d0.5_s0 | 22 | 11 | paar1 | **10** | +1 | 3.3 s |
| rand_n7_m7_d0.5_s1 | 22 | 11 | bp | **10** | +1 | 4.4 s |
| rand_n7_m7_d0.5_s1 | 22 | 11 | bp | **10** | +1 | 6.9 s |
| rand_n7_m7_d0.5_s2 | 19 | 12 | paar1 | **11** | +1 | 30.4 s |
| rand_n7_m7_d0.5_s2 | 19 | 12 | paar1 | **11** | +1 | 45.9 s |
| rand_n7_m7_d0.5_s3 | 13 | 9 | paar2 | **9** | +0 | 3.2 s |
| rand_n7_m7_d0.5_s4 | 14 | 8 | rnbp | **8** | +0 | 0.5 s |
| rand_n7_m7_d0.5_s5 | 18 | 8 | bp | **8** | +0 | 0.0 s |
| rand_n7_m7_d0.5_s6 | 10 | 7 | paar1 | **7** | +0 | 0.0 s |
| rand_n7_m7_d0.5_s7 | 19 | 9 | paar1 | **9** | +0 | 0.8 s |
| rand_n7_m7_d0.5_s8 | 22 | 11 | rnbp | **11** | +0 | 34.1 s |
| rand_n7_m7_d0.5_s9 | 10 | 7 | paar1 | **7** | +0 | 0.0 s |
| rand_n7_m7_d0.5_s10 | 13 | 9 | paar1 | **8** | +1 | 0.1 s |
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
| rand_n8_m8_d0.7_s2 | 39 | 14 | bp | **13** | +1 | 80.8 s |
| rand_n8_m8_d0.7_s4 | 41 | 14 | paar2 | **12** | +2 | 19.1 s |
| rand_n9_m9_d0.3_s1 | 16 | 11 | bp | **11** | +0 | 78.7 s |
| rand_n9_m9_d0.3_s4 | 15 | 10 | paar2 | **10** | +0 | 11.2 s |

## Inconclusive

Conflict budget exhausted. Neither SAT nor UNSAT, so these establish
nothing and are recorded only for completeness.

| instance | naive | heuristic | stalled at k |
|---|---:|---:|---:|
| rand_n8_m8_d0.5_s0 | 28 | 14 | 13 |
| rand_n8_m8_d0.7_s0 | 34 | 14 | 12 |
| rand_n8_m8_d0.5_s1 | 21 | 12 | 11 |
| rand_n8_m8_d0.7_s1 | 35 | 13 | 12 |
| rand_n8_m8_d0.5_s2 | 20 | 15 | 13 |
| rand_n8_m8_d0.3_s3 | 18 | 12 | 11 |
| rand_n8_m8_d0.5_s3 | 22 | 11 | 10 |
| rand_n8_m8_d0.7_s3 | 31 | 15 | 12 |
| rand_n8_m8_d0.5_s4 | 27 | 13 | 12 |
| rand_n9_m9_d0.3_s0 | 17 | 12 | 11 |
| rand_n9_m9_d0.5_s0 | 26 | 14 | 12 |
| rand_n9_m9_d0.7_s0 | 48 | 18 | 17 |
| rand_n9_m9_d0.5_s1 | 38 | 16 | 15 |
| rand_n9_m9_d0.7_s1 | 45 | 17 | 15 |
| rand_n9_m9_d0.3_s2 | 17 | 12 | 11 |
| rand_n9_m9_d0.5_s2 | 28 | 18 | 16 |
| rand_n9_m9_d0.7_s2 | 49 | 16 | 14 |
| rand_n9_m9_d0.3_s3 | 17 | 13 | 12 |
| rand_n9_m9_d0.5_s3 | 39 | 18 | 16 |
| rand_n9_m9_d0.7_s3 | 45 | 18 | 17 |
| rand_n9_m9_d0.5_s4 | 32 | 17 | 14 |
| rand_n9_m9_d0.7_s4 | 49 | 18 | 16 |
