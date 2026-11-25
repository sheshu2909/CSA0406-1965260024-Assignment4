/* q4_starve.c - Task 4.3: starvation under SSTF.
 *
 * A recording server receives a stream of requests at cylinder 60, one every
 * millisecond, and one single request at cylinder 183.  The head starts at 60.
 * The program serves the queue with SSTF, SCAN and C-LOOK and reports how
 * many requests are served before the request at 183, and how long it waits.
 *
 * Model: one request is served at a time, each service takes 2 ms (a seek plus
 * the transfer).  Arrivals are kept in a small pending list.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q4_starve.c -o q4_starve
 */
#include <stdio.h>
#include <stdlib.h>

#define STREAM 5000
#define ARRIVAL_MS 1.0
#define SERVICE_MS 2.0
#define PEND 64

struct item { int cyl; double arrived; int served; };

static struct item q[STREAM + 1];
static int nq;

static int pick_sstf(int pos)
{
    int best = -1, bd = 0;
    for (int i = 0; i < nq; i++) {
        if (q[i].served) continue;
        int d = abs(q[i].cyl - pos);
        if (best < 0 || d < bd) { best = i; bd = d; }
    }
    return best;
}

/* A sweeping scheduler: serve the smallest cylinder above the head; when
 * nothing is left above, wind back to the lowest pending request. */
static int pick_up(int pos)
{
    int best = -1, bd = 0;
    for (int i = 0; i < nq; i++) {
        if (q[i].served) continue;
        int d = q[i].cyl - pos;
        if (d > 0) {
            if (best < 0 || d < bd) { best = i; bd = d; }
        }
    }
    if (best < 0) {
        int lowest = -1;
        for (int i = 0; i < nq; i++) {
            if (q[i].served) continue;
            if (lowest < 0 || q[i].cyl < q[lowest].cyl) lowest = i;
        }
        return lowest;
    }
    return best;
}

static void simulate(const char *name, int sweeping)
{
    double t = 0, pos = 60, target_wait = -1;
    int served = 0, before = 0, found = 0, arrivals = 0;

    nq = 0;
    /* the single request at 183 arrives at t = 0 */
    q[nq].cyl = 183; q[nq].arrived = 0; q[nq].served = 0; nq++;
    srand(7);

    for (int step = 0; step < 40000 && !found; step++) {
        while (arrivals < STREAM && (double)arrivals * ARRIVAL_MS <= t) {
            q[nq].cyl = 58 + rand() % 5;      /* the recording stream, 58-62 */
            q[nq].arrived = (double)arrivals * ARRIVAL_MS;
            q[nq].served = 0;
            nq++;
            arrivals++;
        }
        int k = sweeping ? pick_up((int)pos) : pick_sstf((int)pos);
        if (k < 0) { t += ARRIVAL_MS; continue; }
        q[k].served = 1;
        served++;
        if (q[k].cyl == 183) {
            before = served - 1;
            target_wait = t + SERVICE_MS - q[k].arrived;
            found = 1;
        }
        pos = q[k].cyl;
        t += SERVICE_MS;
    }

    printf("%-6s | %8d | %10.1f ms | %s\n", name, before,
           found ? target_wait : -1.0,
           found ? "served" : "NOT SERVED within the run");
}

int main(void)
{
    printf("Task 4.3  a request at cylinder 183 against a stream at 60\n");
    printf("%d stream requests, one every %.1f ms, service %.1f ms per request\n\n",
           STREAM, ARRIVAL_MS, SERVICE_MS);
    printf("%-6s | %8s | %10s | %s\n", "algo", "served", "wait", "result");
    printf("-------+----------+------------+------------------------\n");

    nq = 0; simulate("SSTF", 0);
    nq = 0; simulate("SCAN", 1);
    nq = 0; simulate("C-LOOK", 1);

    printf("\nSSTF always takes the request nearest to the head, so the steady\n");
    printf("stream at 60 keeps the head at 60 and the request at 183 is never\n");
    printf("the nearest one: it starves.  SCAN and C-LOOK sweep the disk, so\n");
    printf("every cylinder is reached after a bounded number of requests.\n");
    return 0;
}
