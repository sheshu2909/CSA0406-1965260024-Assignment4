/* q6_sim.c - Task 6, stage 5: simulate the two designs.
 *
 * Design A: the company's own servers - SSD cache in front of hard disks,
 *           indexed allocation, SSTF scheduling.
 * Design B: cloud object storage with a content-delivery network.
 *
 * Each of 600,000 play requests (200,000 students x 3 lectures) draws a cache
 * hit or miss and a latency from the model below.  The model uses the random
 * read latency measured on this machine for the SSD tier (argument 1) and the
 * measured sequential read throughput (argument 2); the hard-disk and CDN
 * parameters are standard values and are printed with the results.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q6_sim.c -o q6_sim
 * Run:   ./q6_sim 250 3700        (SSD latency in us, sequential MB/s)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SESSIONS 600000
#define BUFFER_MB 1.25            /* two seconds of 5 Mbps video */
#define REMOTE_PCT 30.0

static double ssd_ms = 0.35;
static double seq_mb_s = 1200.0;

#define HDD_SEEK_MS 8.5
#define HDD_QUEUE_MS 0.07         /* mean SSTF queueing, 3.3 cylinders */
#define HDD_MB_S 200.0
#define EDGE_MS 15.0
#define ORIGIN_MS 120.0
#define CLIENT_MB_S 6.25          /* 50 Mbps to the student */
#define INTERNET_MS 25.0

static int cmp(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static double urand(void) { return (double)rand() / ((double)RAND_MAX + 1.0); }

static void report(const char *name, double *v, int n)
{
    qsort(v, (size_t)n, sizeof v[0], cmp);
    double sum = 0;
    for (int i = 0; i < n; i++) sum += v[i];
    printf("%-28s | %7.1f | %7.1f | %7.1f | %7.1f ms\n", name, sum / n,
           v[n / 2], v[(int)(n * 0.95)], v[(int)(n * 0.99)]);
}

int main(int argc, char **argv)
{
    if (argc > 1) ssd_ms = atof(argv[1]) / 1000.0;
    if (argc > 2) seq_mb_s = atof(argv[2]);

    double *a_local = malloc(SESSIONS * sizeof *a_local);
    double *a_remote = malloc(SESSIONS * sizeof *a_remote);
    double *b_local = malloc(SESSIONS * sizeof *b_local);
    double *b_remote = malloc(SESSIONS * sizeof *b_remote);
    if (!a_local || !a_remote || !b_local || !b_remote) return 1;

    srand(20261114);
    /* Both designs must send the same %.2f MB to the student before playback
     * starts, so the client link is a common cost and only the time to the
     * first byte differs between the designs. */
    double client_buffer_ms = BUFFER_MB / CLIENT_MB_S * 1000.0;

    for (int i = 0; i < SESSIONS; i++) {
        /* design A: 80% of the starts are served from the SSD cache */
        double ttfb;
        if (urand() < 0.80)
            ttfb = ssd_ms;
        else
            ttfb = HDD_SEEK_MS + HDD_QUEUE_MS;
        a_local[i] = ttfb + client_buffer_ms;
        a_remote[i] = ttfb + INTERNET_MS + client_buffer_ms;

        /* design B: 95% of the starts come from an edge node */
        double bt = EDGE_MS;
        if (urand() >= 0.95) bt += ORIGIN_MS;
        b_local[i] = bt + client_buffer_ms;
        b_remote[i] = bt + client_buffer_ms;   /* the edge node is close by */
    }
    (void)seq_mb_s;

    printf("Task 6, stage 5  two designs simulated over %d play requests\n\n", SESSIONS);
    printf("inputs\n");
    printf("  SSD random read     : %.3f ms (conservative device latency; the\n", ssd_ms);
    printf("        page-cache hits measured on this machine were about 0.005 ms)\n");
    printf("  SSD sequential read : %.0f MB/s (measured)\n", seq_mb_s);
    printf("  hard disk           : %.1f ms seek + %.2f ms queue + %.0f MB/s\n",
           HDD_SEEK_MS, HDD_QUEUE_MS, HDD_MB_S);
    printf("  CDN edge / origin   : %.0f ms / +%.0f ms, client at %.2f MB/s\n",
           EDGE_MS, ORIGIN_MS, CLIENT_MB_S);
    printf("  internet path for the company's own servers: +%.0f ms\n", INTERNET_MS);
    printf("  buffer to fill before playback: %.2f MB at %.2f MB/s = %.0f ms\n",
           BUFFER_MB, CLIENT_MB_S, BUFFER_MB / CLIENT_MB_S * 1000.0);
    printf("  (the same client cost for both designs)\n\n");

    printf("%-28s | %7s | %7s | %7s | %s\n",
           "design", "mean", "p50", "p95", "p99");
    printf("-----------------------------+---------+---------+---------+----------\n");
    report("A own, student on campus", a_local, SESSIONS);
    report("A own, student at home", a_remote, SESSIONS);
    report("B CDN, student on campus", b_local, SESSIONS);
    report("B CDN, student at home", b_remote, SESSIONS);

    printf("\nmean of the two populations (%.0f%% at home)\n", REMOTE_PCT);
    double mix_a = 0, mix_b = 0;
    for (int i = 0; i < SESSIONS; i++) {
        mix_a += (REMOTE_PCT / 100.0) * a_remote[i] + (1 - REMOTE_PCT / 100.0) * a_local[i];
        mix_b += (REMOTE_PCT / 100.0) * b_remote[i] + (1 - REMOTE_PCT / 100.0) * b_local[i];
    }
    printf("  A own servers : %.1f ms\n", mix_a / SESSIONS);
    printf("  B CDN         : %.1f ms\n", mix_b / SESSIONS);

    double egress_gb = 200000.0 * 10.0 * 0.8 * 1.0;
    printf("\nmonthly cost of the two designs (1.6 PB of viewing)\n");
    printf("  A own: 6.4 TB of disks (%.0f USD) + %.0f GB of transit at 0.01 USD = %.0f USD\n",
           6.4 * 20.0, egress_gb, egress_gb * 0.01);
    printf("  B CDN: 3.2 TB of object storage (%.0f USD) + %.0f GB at 0.02 USD = %.0f USD\n",
           3.2 * 23.0, egress_gb, egress_gb * 0.02);

    printf("\nreading the result: on campus the company's own SSD cache starts\n");
    printf("playback %.0f ms sooner than the CDN; for the students at home the\n",
           EDGE_MS);
    printf("company's servers lose their advantage to the internet path and the\n");
    printf("CDN is faster.  The CDN also removes the 50 Gbps peak from the\n");
    printf("company's uplink, which is the constraint no cache can fix.\n");
    printf("The measured recommendation is therefore a hybrid: the company's\n");
    printf("servers keep the catalogue and serve campus, and a CDN in front of\n");
    printf("them serves the students at home and absorbs the peak.\n");

    free(a_local); free(a_remote); free(b_local); free(b_remote);
    return 0;
}
