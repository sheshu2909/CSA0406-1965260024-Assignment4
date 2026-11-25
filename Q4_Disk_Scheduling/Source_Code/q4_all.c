/* q4_all.c - Task 4.1 and 4.2: all six algorithms on the given queue, then a
 * simulation of 10,000 requests at three load levels.
 *
 * The six algorithms are applied to the queue of the assignment so that the
 * program's totals can be compared with the hand calculation.  The simulation
 * then serves 10,000 random requests in batches of 1, 8 and 64 ("light",
 * "medium", "heavy") and reports the average head movement and the waiting
 * time of every request.
 *
 * Service-time model (stated so the numbers can be checked):
 *   seek  = 0.020 ms per cylinder crossed
 *   transfer = 0.150 ms per request
 *   waiting time of a request = the service times of the requests that the
 *   algorithm serves before it inside the same batch.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q4_all.c -o q4_all
 */
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXCYL 199
#define BATCH 64
#define NREQ 10000
#define MS_PER_CYL 0.020
#define TRANSFER_MS 0.150

static int req8[8] = {98, 183, 37, 122, 14, 124, 65, 67};

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e3 + (double)ts.tv_nsec / 1e6;
}

static int cmp_int(const void *a, const void *b)
{
    return (*(const int *)a > *(const int *)b) - (*(const int *)a < *(const int *)b);
}

static int movement(const int *o, int n, int head)
{
    int t = 0, p = head;
    for (int i = 0; i < n; i++) { t += abs(o[i] - p); p = o[i]; }
    return t;
}

/* ---- the six algorithms: fill out[] with the service order ---- */
static int ord_fcfs(const int *r, int n, int head, int *out)
{
    (void)head;
    memcpy(out, r, (size_t)n * sizeof *out);
    return n;
}

static int ord_sstf(const int *r, int n, int head, int *out)
{
    int done[BATCH] = {0}, pos = head, k = 0;
    while (k < n) {
        int best = -1, bd = 0;
        for (int i = 0; i < n; i++) {
            if (done[i]) continue;
            int d = abs(r[i] - pos);
            if (best < 0 || d < bd) { best = i; bd = d; }
        }
        done[best] = 1;
        out[k++] = r[best];
        pos = r[best];
    }
    return n;
}

static int ord_scan(const int *r, int n, int head, int *out)
{
    int s[BATCH];
    memcpy(s, r, (size_t)n * sizeof *s);
    qsort(s, (size_t)n, sizeof *s, cmp_int);
    int k = 0;
    for (int i = n - 1; i >= 0; i--) if (s[i] < head) out[k++] = s[i];
    out[k++] = 0;
    for (int i = 0; i < n; i++) if (s[i] > head) out[k++] = s[i];
    return k;
}

static int ord_look(const int *r, int n, int head, int *out)
{
    int s[BATCH];
    memcpy(s, r, (size_t)n * sizeof *s);
    qsort(s, (size_t)n, sizeof *s, cmp_int);
    int k = 0;
    for (int i = n - 1; i >= 0; i--) if (s[i] < head) out[k++] = s[i];
    for (int i = 0; i < n; i++) if (s[i] > head) out[k++] = s[i];
    return k;
}

static int ord_cscan(const int *r, int n, int head, int *out)
{
    int s[BATCH];
    memcpy(s, r, (size_t)n * sizeof *s);
    qsort(s, (size_t)n, sizeof *s, cmp_int);
    int k = 0;
    for (int i = 0; i < n; i++) if (s[i] > head) out[k++] = s[i];
    out[k++] = MAXCYL;
    out[k++] = 0;
    for (int i = 0; i < n; i++) if (s[i] < head) out[k++] = s[i];
    return k;
}

static int ord_clook(const int *r, int n, int head, int *out)
{
    int s[BATCH];
    memcpy(s, r, (size_t)n * sizeof *s);
    qsort(s, (size_t)n, sizeof *s, cmp_int);
    int k = 0;
    for (int i = 0; i < n; i++) if (s[i] > head) out[k++] = s[i];
    for (int i = 0; i < n; i++) if (s[i] < head) out[k++] = s[i];
    return k;
}

typedef int (*algo_fn)(const int *, int, int, int *);
static const char *names[6] = { "FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK" };
static algo_fn fns[6] = { ord_fcfs, ord_sstf, ord_scan, ord_cscan, ord_look, ord_clook };

static void part_a(void)
{
    printf("Task 4.1  the queue of the assignment (cylinders 0-%d, head %d)\n\n",
           MAXCYL, 53);
    for (int a = 0; a < 6; a++) {
        int out[BATCH + 2];
        int n = fns[a](req8, 8, 53, out);
        printf("  %-6s head 53", names[a]);
        for (int i = 0; i < n; i++) printf(" %d", out[i]);
        int mv = movement(out, n, 53);
        if (a == 3) mv -= MAXCYL;                 /* the return jump */
        if (a == 5) {
            /* C-LOOK: subtract the jump from the highest to the lowest */
            int hi = out[0];
            for (int i = 0; i < n; i++) if (out[i] > hi) hi = out[i];
            int lo = out[0];
            for (int i = 0; i < n; i++) if (out[i] < lo) lo = out[i];
            mv -= hi - lo;
        }
        printf("\n         movement %d cylinders", mv);
        if (a == 3) printf(" (+%d for the return jump)", MAXCYL);
        if (a == 5) printf(" (+ jump back to the lowest request)");
        printf("\n");
    }
    printf("\n  hand check: FCFS 640, SSTF 236, SCAN 236, C-SCAN 183 (+199),\n");
    printf("  LOOK 208 and C-LOOK 153 of real movement plus the jump of 169.\n\n");
}

static void part_b(void)
{
    static int r[NREQ];
    srand(20261114);
    int hot = 100;
    for (int i = 0; i < NREQ; i++) {
        if (rand() % 2) hot = rand() % (MAXCYL + 1);
        if (rand() % 100 < 50) {
            int d = (rand() % 21) - 10;           /* half stay near the hot spot */
            r[i] = hot + d;
            if (r[i] < 0) r[i] = 0;
            if (r[i] > MAXCYL) r[i] = MAXCYL;
        } else {
            r[i] = rand() % (MAXCYL + 1);
        }
    }

    printf("Task 4.2  %d requests, batches of 1, 8 and 64\n", NREQ);
    printf("service model: %.3f ms per cylinder + %.3f ms per request\n\n",
           MS_PER_CYL, TRANSFER_MS);
    printf("%-7s | %8s | %8s | %10s | %10s | %10s\n",
           "algo", "light avg", "light max", "medium avg", "medium max", "heavy avg");
    printf("-------+----------+----------+------------+------------+-----------\n");

    for (int a = 0; a < 6; a++) {
        double res[3][2];       /* [load][mean,max] of the waiting time */
        double avg_move[3] = {0, 0, 0};
        int loads[3] = {1, 8, 64};
        for (int L = 0; L < 3; L++) {
            int q = loads[L], head = r[0];
            long long total_mv = 0;
            double total_wait = 0, max_wait = 0;
            int served = 0;
            for (int base = 0; base < NREQ; base += q) {
                int n = (base + q <= NREQ) ? q : NREQ - base;
                int out[BATCH + 2];
                int m = fns[a](&r[base], n, head, out);
                /* service time of each entry, and the wait it imposes */
                double clock = 0;
                int pos = head;
                for (int i = 0; i < m; i++) {
                    double seek = abs(out[i] - pos) * MS_PER_CYL;
                    /* endpoints inserted by SCAN/C-SCAN are not requests */
                    int is_req = 0;
                    for (int j = 0; j < n; j++)
                        if (r[base + j] == out[i]) { is_req = 1; break; }
                    if (is_req) {
                        total_wait += clock;
                        if (clock > max_wait) max_wait = clock;
                        served++;
                    }
                    total_mv += abs(out[i] - pos);
                    clock += seek + TRANSFER_MS;
                    pos = out[i];
                }
                head = pos;
            }
            res[L][0] = total_wait / (double)served;
            res[L][1] = max_wait;
            avg_move[L] = (double)total_mv / (double)served;
        }
        printf("%-7s | %6.2f ms | %6.2f ms | %6.2f ms | %8.2f ms | %6.2f ms\n",
               names[a], res[0][0], res[0][1], res[1][0], res[1][1], res[2][0]);
        printf("        | movement %5.1f |          | movement %5.1f |            | movement %5.1f\n",
               avg_move[0], avg_move[1], avg_move[2]);
    }
}

int main(void)
{
    double t0 = now_ms();
    part_a();
    part_b();
    printf("\nsimulation time: %.0f ms\n", now_ms() - t0);
    return 0;
}
