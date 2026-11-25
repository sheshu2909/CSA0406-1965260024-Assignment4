/* q4_sched.c - Assignment 4, Task 4 "Complete the Code".
 *
 * The program given in the assignment with TODO 1 replaced by a shortest
 * seek-time-first scheduler.  Nothing else was changed.
 *
 * Expected output (from the assignment sheet):
 *   FCFS   53 98 183 37 122 14 124 65 67 -> 640 cylinders
 *   SSTF   53 65 67 37 14 98 122 124 183 -> 236 cylinders
 *   SCAN   53 37 14 0 65 67 98 122 124 183 -> 236 cylinders
 *   C-SCAN 53 ... 199, jump to 0 ... 37 -> 183 cylinders (+199 for the jump)
 *
 * Build: gcc -std=c11 -Wall -Wextra q4_sched.c -o q4_sched
 */
#include <stdio.h>
#include <stdlib.h>

#define N 8
#define MAXCYL 199

int req[N] = {98, 183, 37, 122, 14, 124, 65, 67};

int cmp(const void *a, const void *b)
{
    return *(const int *)a - *(const int *)b;
}

void show(const char *name, const int order[], int n, int head, int extra)
{
    int total = 0, pos = head;
    printf("%-6s %d", name, head);
    for (int i = 0; i < n; i++) {
        printf(" %d", order[i]);
        total += abs(order[i] - pos);
        pos = order[i];
    }
    printf(" -> %d cylinders\n", total + extra);
}

int main(void)
{
    int head = 53, order[N + 2];
    show("FCFS", req, N, head, 0);

    /* SSTF: always serve the nearest pending request */
    int done[N] = {0}, pos = head;
    for (int k = 0; k < N; k++) {
        /* TODO 1: find the pending request (done[i] == 0) with the smallest
         * distance abs(req[i] - pos), mark it done, store it in order[k] and
         * move pos to it. */
        int best = -1, best_dist = 0;
        for (int i = 0; i < N; i++) {
            if (done[i]) continue;
            int d = abs(req[i] - pos);
            if (best < 0 || d < best_dist) {
                best = i;
                best_dist = d;
            }
        }
        done[best] = 1;
        order[k] = req[best];
        pos = req[best];
    }
    show("SSTF", order, N, head, 0);

    /* SCAN (towards cylinder 0 first, like an elevator) */
    int s[N];
    for (int i = 0; i < N; i++) s[i] = req[i];
    qsort(s, N, sizeof s[0], cmp);

    int n = 0, i;
    for (i = N - 1; i >= 0; i--)
        if (s[i] < head) order[n++] = s[i];
    order[n++] = 0;
    for (i = 0; i < N; i++)
        if (s[i] > head) order[n++] = s[i];
    show("SCAN", order, n, head, 0);

    /* C-SCAN (towards the last cylinder, then jump back to 0) */
    n = 0;
    for (i = 0; i < N; i++)
        if (s[i] > head) order[n++] = s[i];
    order[n++] = MAXCYL;
    int part = 0, p = head;
    for (int k = 0; k < n; k++) {
        part += abs(order[k] - p);
        p = order[k];
    }
    int rest[N], m = 0;
    for (i = 0; i < N; i++)
        if (s[i] < head) rest[m++] = s[i];
    int back = 0;
    p = 0;
    for (int k = 0; k < m; k++) {
        back += abs(rest[k] - p);
        p = rest[k];
    }
    printf("C-SCAN %d ... %d, jump to 0 ... %d -> %d cylinders (+%d for the jump)\n",
           head, MAXCYL, rest[m - 1], part + back, MAXCYL);
    return 0;
}
