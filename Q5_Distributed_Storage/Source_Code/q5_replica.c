/* q5_replica.c - Task 5.2: what three replicas buy, and what they cost.
 *
 * Two designs answer the same 20,000 reads:
 *   one NFS server            : 1 copy, no failover
 *   HDFS with 3 replicas      : 3 copies, the read is served by any live copy
 *
 * Node availability is drawn per request (0.5% chance that a node is down for
 * that request).  A read costs 8 ms when it is served normally and 8 ms more
 * for every failed attempt before it.  The program also simulates read-your-
 * write under an asynchronous replica (2% stale) and a synchronous one (0%),
 * and reports the storage and cost of both designs.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q5_replica.c -o q5_replica
 */
#include <stdio.h>
#include <stdlib.h>

#define READS 20000
#define NODE_MS 8.0
#define P_DOWN 0.005
#define DATA_TB 20.0
#define COST_PER_TB_MONTH 20.0

static int cmp_double(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static double urand(void) { return (double)rand() / ((double)RAND_MAX + 1.0); }

int main(void)
{
    double *lat_nfs = malloc(READS * sizeof *lat_nfs);
    double *lat_hdfs = malloc(READS * sizeof *lat_hdfs);
    if (!lat_nfs || !lat_hdfs) return 1;

    srand(20261114);
    long long ok_nfs = 0, ok_hdfs = 0;
    long long attempts_hdfs = 0, stale = 0;

    for (int i = 0; i < READS; i++) {
        /* one NFS server */
        if (urand() < P_DOWN) {
            lat_nfs[i] = -1;                       /* unavailable */
        } else {
            lat_nfs[i] = NODE_MS + urand() * 2.0;
            ok_nfs++;
        }

        /* three replicas: try each until one answers */
        double t = 0;
        int served = 0;
        for (int r = 0; r < 3; r++) {
            attempts_hdfs++;
            t += NODE_MS;
            if (urand() >= P_DOWN) { served = 1; break; }
        }
        if (served) {
            lat_hdfs[i] = t + urand() * 2.0;
            ok_hdfs++;
        } else {
            lat_hdfs[i] = -1;
        }
        if (urand() < 0.02) stale++;               /* async replica lag */
    }

    int n_ok = 0;
    for (int i = 0; i < READS; i++)
        if (lat_nfs[i] > 0) lat_nfs[n_ok++] = lat_nfs[i];
    qsort(lat_nfs, (size_t)n_ok, sizeof *lat_nfs, cmp_double);
    double sum = 0;
    for (int i = 0; i < n_ok; i++) sum += lat_nfs[i];

    int h_ok = 0;
    for (int i = 0; i < READS; i++)
        if (lat_hdfs[i] > 0) lat_hdfs[h_ok++] = lat_hdfs[i];
    qsort(lat_hdfs, (size_t)h_ok, sizeof *lat_hdfs, cmp_double);
    double hsum = 0;
    for (int i = 0; i < h_ok; i++) hsum += lat_hdfs[i];

    printf("Task 5.2  one NFS server against three HDFS replicas\n");
    printf("%d reads, node down with probability %.1f%% per request, "
           "%.0f ms per attempt\n\n", READS, P_DOWN * 100, NODE_MS);

    printf("design            | available | mean   | p50    | p95\n");
    printf("------------------+-----------+--------+--------+-------\n");
    printf("one NFS server    |  %6.3f%%  | %5.2f  | %5.2f  | %5.2f ms\n",
           100.0 * (double)ok_nfs / READS, sum / n_ok, lat_nfs[n_ok / 2],
           lat_nfs[(int)(n_ok * 0.95)]);
    printf("3 replicas (HDFS) |  %6.3f%%  | %5.2f  | %5.2f  | %5.2f ms\n",
           100.0 * (double)ok_hdfs / READS, hsum / h_ok, lat_hdfs[h_ok / 2],
           lat_hdfs[(int)(h_ok * 0.95)]);

    printf("\nreplica fetches attempted: %lld for %d reads (%.3f per read)\n",
           attempts_hdfs, READS, (double)attempts_hdfs / READS);

    printf("\nstorage and cost for %.0f TB of data\n", DATA_TB);
    printf("  one copy  : %5.1f TB, %.0f USD per month\n", DATA_TB,
           DATA_TB * COST_PER_TB_MONTH);
    printf("  three copies: %5.1f TB, %.0f USD per month, %.0f%% more storage\n",
           3 * DATA_TB, 3 * DATA_TB * COST_PER_TB_MONTH, 200.0);

    printf("\nconsistency\n");
    printf("  asynchronous replica: %lld of %d reads (%.1f%%) could return old data\n",
           stale, READS, 100.0 * (double)stale / READS);
    printf("  synchronous replica : 0 stale reads, but every write waits for the\n");
    printf("  slowest copy, so writes are slower and an unreachable copy can\n");
    printf("  block the writer (the CAP trade-off).\n");

    free(lat_nfs);
    free(lat_hdfs);
    return 0;
}
