/* slp_core.c -- fast primitives for Shortest Linear Straight-Line Program search.
 *
 * Signals are uint64_t bitmasks over up to 64 input variables.
 * Programs are emitted as flat int arrays [a0,b0,a1,b1,...] meaning
 * signal_{n+k} = signal_{a_k} XOR signal_{b_k}.
 *
 * Everything here is a *heuristic*; correctness of any emitted program is
 * established independently by the Python verifier in slp/instance.py.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXSIG 4096
#define MAXTGT 512

typedef unsigned long long u64;

/* ---------------- instrumentation ---------------- */
typedef struct {
    long long oracle_calls;   /* number of reach() invocations            */
    long long oracle_nodes;   /* DFS nodes expanded inside reach()        */
    long long pair_evals;     /* candidate pairs scored                   */
    double    seconds;
} Stats;

static Stats g_stats;

void slp_reset_stats(void) { memset(&g_stats, 0, sizeof(g_stats)); }
void slp_get_stats(double *out) {
    out[0] = (double)g_stats.oracle_calls;
    out[1] = (double)g_stats.oracle_nodes;
    out[2] = (double)g_stats.pair_evals;
    out[3] = g_stats.seconds;
}

static inline int pc(u64 x) { return __builtin_popcountll(x); }

/* ---------------- oracle query log ----------------
 * Supervised training data for a learned distance oracle. Each record is
 *   (step, x, budget, label)
 * where `step` indexes the emitted program prefix (the added-set A at the time
 * of the query is exactly the first `step` ops of the program), and
 *   label = 1  iff  g(x) <= budget   under that A,
 *   label = 0  iff  g(x) >  budget,
 *   label = -1 iff  the exact search hit its node cap (unlabelled).
 * Reconstructing A from the program prefix keeps records tiny and exact.
 */
static long long *g_log = 0;
static long long  g_log_cap = 0, g_log_len = 0;
static int        g_log_step = 0;

void slp_log_begin(long long *buf, long long cap) {
    g_log = buf; g_log_cap = cap; g_log_len = 0; g_log_step = 0;
}
long long slp_log_len(void) { return g_log_len; }
void slp_log_end(void) { g_log = 0; g_log_cap = 0; }

static inline void log_query(u64 x, int budget, int label) {
    if (!g_log || g_log_len + 4 > g_log_cap) return;
    g_log[g_log_len++] = g_log_step;
    g_log[g_log_len++] = (long long)x;
    g_log[g_log_len++] = budget;
    g_log[g_log_len++] = label;
}


/* ---------------- rng ---------------- */
static u64 rng_state = 88172645463325252ULL;
void slp_seed(u64 s) { rng_state = s ? s : 88172645463325252ULL; }
static inline u64 xorshift(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return rng_state;
}
static inline int rnd_below(int k) { return (int)(xorshift() % (u64)k); }

/* =====================================================================
 * Paar's algorithm.
 * Works on the target matrix expressed over the current signal set.
 * Repeatedly pick the pair of signals co-occurring in the most rows.
 * mode 0 = Paar1 (first max wins), mode 1 = Paar2 (uniform random among maxima).
 * ===================================================================== */
/* Paar's greedy algorithm.
 *
 * colrows[s] is a bitmask over output rows: bit r set iff row r currently
 * contains signal s. Co-occurrence of a signal pair is then a single
 * popcount of an AND, so each greedy step is O(ns^2) rather than O(ns^2 * m).
 * Requires m <= 64 rows.
 */
int slp_paar(int n, int m, const u64 *targets, int mode, int *prog_out, int prog_cap) {
    clock_t t0 = clock();
    static u64 sig[MAXSIG];
    static u64 colrows[MAXSIG];
    int ns = n, nops = 0;

    if (n > 64 || m > 64) return -1;
    for (int i = 0; i < n; i++) {
        sig[i] = 1ULL << i;
        u64 rows = 0;
        for (int r = 0; r < m; r++) if (targets[r] >> i & 1) rows |= 1ULL << r;
        colrows[i] = rows;
    }

    while (ns < MAXSIG) {
        int besti = -1, bestj = -1, bestc = 1, ties = 0;
        for (int i = 0; i < ns; i++) {
            if (pc(colrows[i]) < 2) continue;      /* cannot be in a pair of >=2 rows */
            for (int j = i + 1; j < ns; j++) {
                int c = pc(colrows[i] & colrows[j]);
                if (c > bestc) { bestc = c; besti = i; bestj = j; ties = 1; }
                else if (c == bestc && c > 1) {
                    ties++;
                    if (mode == 1 && rnd_below(ties) == 0) { besti = i; bestj = j; }
                }
            }
        }
        if (besti < 0) break;
        if (nops * 2 + 1 >= prog_cap) return -1;
        prog_out[2 * nops] = besti; prog_out[2 * nops + 1] = bestj; nops++;
        sig[ns] = sig[besti] ^ sig[bestj];
        u64 shared = colrows[besti] & colrows[bestj];
        colrows[besti] &= ~shared;
        colrows[bestj] &= ~shared;
        colrows[ns] = shared;
        ns++;
    }

    /* finish each row by chaining its remaining signals.
     * ns_end is fixed before the loop: signals created *here* must not be
     * rescanned as if they were still pending row members. */
    const int ns_end = ns;
    for (int r = 0; r < m; r++) {
        int acc = -1;
        for (int s = 0; s < ns_end; s++) {
            if (!(colrows[s] >> r & 1)) continue;
            if (acc < 0) { acc = s; continue; }
            if (nops * 2 + 1 >= prog_cap || ns >= MAXSIG) return -1;
            prog_out[2 * nops] = acc; prog_out[2 * nops + 1] = s; nops++;
            sig[ns] = sig[acc] ^ sig[s];
            colrows[ns] = 0;
            acc = ns; ns++;
        }
        if (acc < 0) return -1;                    /* zero row */
    }
    g_stats.seconds += (double)(clock() - t0) / CLOCKS_PER_SEC;
    return nops;
}

/* =====================================================================
 * Boyar-Peralta.
 *
 * S = basis(n) union A (added signals).  g(x) = min #elements of S summing to x
 *   = min over T subset of A of ( |T| + popcount(x ^ XOR(T)) )
 * Dist[t] = g(t) - 1 = additions still needed for target t.
 *
 * reach(x, budget) decides g(x) <= budget by DFS over A.
 * ===================================================================== */
typedef struct {
    u64 A[MAXSIG];
    int na;
    int maxpc;          /* max popcount over A, for pruning */
    long long node_cap; /* per-call DFS node budget; <=0 means unlimited */
    long long nodes;
} Oracle;

static int reach_dfs(Oracle *o, u64 r, int budget, int start) {
    o->nodes++;
    g_stats.oracle_nodes++;
    if (o->node_cap > 0 && o->nodes > o->node_cap) return -1;   /* gave up */
    if (pc(r) <= budget) return 1;
    if (budget == 0) return 0;
    /* prune: each added element cuts popcount by at most maxpc */
    if (o->maxpc > 0 && pc(r) - budget * o->maxpc > budget) return 0;
    int gaveup = 0;
    for (int i = start; i < o->na; i++) {
        int v = reach_dfs(o, r ^ o->A[i], budget - 1, i + 1);
        if (v == 1) return 1;
        if (v < 0) gaveup = 1;
    }
    return gaveup ? -1 : 0;
}

static int reach(Oracle *o, u64 x, int budget) {
    g_stats.oracle_calls++;
    if (budget < 0) return 0;
    o->nodes = 0;
    int r = reach_dfs(o, x, budget, 0);
    log_query(x, budget, r);
    return r;
}

/* mode 0 = deterministic BP, mode 1 = RNBP (random tie-break)
 * node_cap <= 0 : exact oracle.  node_cap > 0 : budgeted (approximate) oracle;
 *                 an exhausted search is treated as "no reduction found".
 */
int slp_bp(int n, int m, const u64 *targets, int mode, long long node_cap,
           int *prog_out, int prog_cap) {
    clock_t t0 = clock();
    u64 S[MAXSIG];
    int dist[MAXTGT];
    u64 tg[MAXTGT];
    int ns = n, nops = 0, mm = 0;
    Oracle o;
    o.na = 0; o.maxpc = 0; o.node_cap = node_cap; o.nodes = 0;

    if (n > 64 || m > MAXTGT) return -1;
    for (int i = 0; i < n; i++) S[i] = 1ULL << i;

    /* drop targets that are already inputs, and dedupe */
    for (int r = 0; r < m; r++) {
        u64 t = targets[r];
        if (pc(t) == 1) continue;
        int dup = 0;
        for (int q = 0; q < mm; q++) if (tg[q] == t) { dup = 1; break; }
        if (!dup) { tg[mm] = t; dist[mm] = pc(t) - 1; mm++; }
    }

    while (1) {
        int remaining = 0;
        for (int r = 0; r < mm; r++) if (dist[r] > 0) remaining++;
        if (remaining == 0) break;

        int besti = -1, bestj = -1, best_total = 1 << 30;
        long long best_norm = -1;
        int ties = 0;

        for (int i = 0; i < ns; i++) {
            for (int j = i + 1; j < ns; j++) {
                u64 u = S[i] ^ S[j];
                if (u == 0) continue;
                int seen = 0;
                for (int q = 0; q < ns; q++) if (S[q] == u) { seen = 1; break; }
                if (seen) continue;

                g_stats.pair_evals++;
                int total = 0;
                long long norm = 0;
                for (int r = 0; r < mm; r++) {
                    int d = dist[r];
                    if (d > 0) {
                        int red = reach(&o, tg[r] ^ u, d - 1);
                        if (red == 1) d = dist[r] - 1;
                    }
                    total += d;
                    norm += (long long)d * d;
                }
                if (total < best_total || (total == best_total && norm > best_norm)) {
                    best_total = total; best_norm = norm;
                    besti = i; bestj = j; ties = 1;
                } else if (mode == 1 && total == best_total && norm == best_norm) {
                    ties++;
                    if (rnd_below(ties) == 0) { besti = i; bestj = j; }
                }
            }
        }
        if (besti < 0) return -1;

        if (nops * 2 + 1 >= prog_cap) return -1;
        prog_out[2 * nops] = besti;
        prog_out[2 * nops + 1] = bestj;
        nops++;
        u64 u = S[besti] ^ S[bestj];
        S[ns++] = u;
        o.A[o.na++] = u;
        g_log_step = nops;                 /* A == first `nops` ops of the program */
        if (pc(u) > o.maxpc) o.maxpc = pc(u);
        if (ns >= MAXSIG) return -1;

        for (int r = 0; r < mm; r++) {
            if (dist[r] > 0 && reach(&o, tg[r] ^ u, dist[r] - 1) == 1) dist[r]--;
        }
    }
    g_stats.seconds += (double)(clock() - t0) / CLOCKS_PER_SEC;
    return nops;
}

/* Exposed oracle for profiling / for training-data generation:
 * returns capped g(x) given an explicit added-set A.
 */
int slp_gval(int n, u64 x, const u64 *A, int na, int ub, long long node_cap) {
    Oracle o;
    o.na = na; o.node_cap = node_cap; o.nodes = 0; o.maxpc = 0;
    for (int i = 0; i < na; i++) { o.A[i] = A[i]; if (pc(A[i]) > o.maxpc) o.maxpc = pc(A[i]); }
    for (int b = 0; b <= ub; b++) {
        if (reach(&o, x, b) == 1) return b;
    }
    return ub + 1;
}
