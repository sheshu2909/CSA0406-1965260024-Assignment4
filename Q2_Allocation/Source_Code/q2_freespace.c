/* q2_freespace.c - Task 2.4: free-space management for a 4 TB disk.
 *
 * Part 1 calculates the size of a bit vector, a linked free list and a
 * grouped/counted free list for 4 TB with 4 KB blocks.
 *
 * Part 2 measures the two structures.  The synthetic disk is realistic: it is
 * filled with occupied runs of 4,000 to 200,000 blocks separated by free gaps,
 * so that about 40% of the blocks are in use and long free runs exist, as on a
 * real disk.  The bit vector covers the whole 4 TB disk (128 MiB of RAM); the
 * free list is measured on a one-million-block slice because the full list
 * would need gigabytes.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q2_freespace.c -o q2_freespace
 */
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BLOCK 4096ULL
#define DISK_BYTES (4ULL * 1024 * 1024 * 1024 * 1024)     /* 4 TiB */
#define NBLOCKS (DISK_BYTES / BLOCK)                      /* 1,073,741,824 */
#define NWORDS (NBLOCKS / 64)
#define LIST_BLOCKS (1ULL << 20)                          /* measured slice */

static double now_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec / 1e3;
}

static unsigned long long rng_state = 88172645463325252ULL;
static unsigned long long xorshift(void)
{
    unsigned long long x = rng_state;
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    return rng_state = x;
}

/* set every bit of [s, e) */
static void set_range(unsigned long long *bm, unsigned long long s,
                      unsigned long long e)
{
    while (s < e && (s & 63)) { bm[s >> 6] |= 1ULL << (s & 63); s++; }
    while (s + 64 <= e) { bm[s >> 6] = ~0ULL; s += 64; }
    while (s < e) { bm[s >> 6] |= 1ULL << (s & 63); s++; }
}

static int bit_set(unsigned long long *bm, unsigned long long b)
{
    return (int)((bm[b >> 6] >> (b & 63)) & 1ULL);
}

/* fill with used runs and free gaps until the requested fraction is in use */
static void build_layout(unsigned long long *bm, unsigned long long n,
                         unsigned long long seed, int target_pct)
{
    memset(bm, 0, (size_t)((n + 63) / 64) * sizeof *bm);
    rng_state = seed;
    unsigned long long pos = 0, used = 0;
    while (pos < n) {
        unsigned long long u = 4000 + xorshift() % 200000;
        unsigned long long f = 1000 + xorshift() % 300000;   /* ~40% in use */
        if (pos + u > n) u = n - pos;
        set_range(bm, pos, pos + u);
        used += u;
        pos += u + f;
    }
    (void)target_pct;
    (void)used;
}

int main(void)
{
    printf("Task 2.4  free-space management on a 4 TB disk\n");
    printf("disk %llu bytes, block %llu bytes, %llu blocks\n\n",
           (unsigned long long)DISK_BYTES, (unsigned long long)BLOCK,
           (unsigned long long)NBLOCKS);

    /* ---------- part 1: sizes ---------- */
    unsigned long long bitvec = (NBLOCKS + 7) / 8;

    printf("bit vector       : %llu bits = %llu bytes", (unsigned long long)NBLOCKS,
           (unsigned long long)bitvec);
    printf("  (%.1f MiB, %.4f%% of the disk)\n",
           (double)bitvec / (1024.0 * 1024.0),
           100.0 * (double)bitvec / (double)DISK_BYTES);

    printf("linked free list : 4 bytes per free block\n");
    for (int pct = 10; pct <= 100; pct += 30) {
        unsigned long long free_b = NBLOCKS * (unsigned long long)pct / 100;
        printf("   %3d%% free      : %llu entries = %.1f MiB\n", pct,
               (unsigned long long)free_b,
               (double)free_b * 4.0 / (1024.0 * 1024.0));
    }

    unsigned long long group = 64;
    unsigned long long groups = (NBLOCKS + group - 1) / group;
    printf("grouping (n=%llu)  : %llu groups x 4 bytes = %llu bytes (%.1f MiB)\n",
           (unsigned long long)group, (unsigned long long)groups,
           (unsigned long long)(groups * 4),
           (double)(groups * 4) / (1024.0 * 1024.0));
    printf("counting          : a count plus a pointer per group, about the same\n");
    printf("                    %.1f MiB, but it can skip %llu free blocks per step\n\n",
           (double)(groups * 4) / (1024.0 * 1024.0), (unsigned long long)group);

    /* ---------- part 2a: a real 4 TB bit vector ---------- */
    unsigned long long *bm = malloc((size_t)NWORDS * sizeof *bm);
    if (!bm) { fprintf(stderr, "no memory for the bit vector\n"); return 1; }
    build_layout(bm, NBLOCKS, 4242, 40);

    unsigned long long used = 0;
    for (unsigned long long w = 0; w < NWORDS; w++)
        used += (unsigned long long)__builtin_popcountll(bm[w]);
    printf("synthetic layout : %.2f%% of the blocks in use\n",
           100.0 * (double)used / (double)NBLOCKS);

    unsigned long long cursor = 0, got = 0;
    double t0 = now_us();
    while (got < 100000) {
        while (cursor < NBLOCKS && bit_set(bm, cursor)) cursor++;
        if (cursor >= NBLOCKS) cursor = 0;
        bm[cursor >> 6] |= 1ULL << (cursor & 63);
        got++;
    }
    double t_bit_alloc = now_us() - t0;

    /* the first run of 64 consecutive free blocks */
    t0 = now_us();
    unsigned long long run = 0, start = 0, found = NBLOCKS;
    for (unsigned long long b = 0; b < NBLOCKS; b++) {
        if (!bit_set(bm, b)) {
            if (run == 0) start = b;
            if (++run == 64) { found = start; break; }
        } else {
            run = 0;
        }
    }
    double t_bit_run = now_us() - t0;
    free(bm);

    /* ---------- part 2b: a free list over a one-million-block slice ---------- */
    unsigned long long *slice = calloc((size_t)(LIST_BLOCKS / 64), sizeof *slice);
    if (!slice) { fprintf(stderr, "no memory for the slice\n"); return 1; }
    build_layout(slice, LIST_BLOCKS, 4242, 40);

    /* the free blocks in address order, linked one to the next */
    unsigned int *block = malloc((size_t)LIST_BLOCKS * sizeof *block);
    unsigned int *nxt = malloc((size_t)LIST_BLOCKS * sizeof *nxt);
    if (!block || !nxt) { fprintf(stderr, "no memory for the list\n"); return 1; }
    unsigned long long nfree = 0;
    for (unsigned long long b = 0; b < LIST_BLOCKS; b++)
        if (!bit_set(slice, b)) block[nfree++] = (unsigned int)b;
    for (unsigned long long i = 0; i < nfree; i++)
        nxt[i] = (unsigned int)(i + 1);
    nxt[nfree - 1] = 0xFFFFFFFFu;

    t0 = now_us();
    volatile unsigned long long acc = 0;
    unsigned int cur = 0;
    for (int k = 0; k < 100000 && cur != 0xFFFFFFFFu; k++) {
        acc += block[cur];
        cur = nxt[cur];
    }
    double t_list_alloc = now_us() - t0;

    t0 = now_us();
    unsigned long long run2 = 0, pos2 = 0;
    for (unsigned long long i = 0; i + 1 < nfree; i++) {
        run2 = (block[i + 1] == block[i] + 1) ? run2 + 1 : 0;
        if (run2 == 63) { pos2 = block[i - 62]; break; }
    }
    double t_list_run = now_us() - t0;
    free(nxt); free(block); free(slice);

    printf("\nmeasured search cost\n");
    printf("  bit vector, whole 4 TB disk\n");
    printf("    100,000 single-block allocations : %.2f ms total, %.0f ns each\n",
           t_bit_alloc / 1000.0, t_bit_alloc * 1000.0 / 100000.0);
    printf("    first 64-block free run          : %.3f ms, found at block %llu\n",
           t_bit_run / 1000.0, (unsigned long long)found);
    printf("  free list, 1 M-block slice (%.1f%% free)\n",
           100.0 * (double)nfree / (double)LIST_BLOCKS);
    printf("    100,000 pops from the head       : %.3f ms total, %.1f ns each\n",
           t_list_alloc / 1000.0, t_list_alloc * 1000.0 / 100000.0);
    printf("    first 64-block run in the list   : %.3f ms, found at block %llu\n",
           t_list_run / 1000.0, (unsigned long long)pos2);
    printf("    (checksum over the popped blocks: %llu)\n",
           (unsigned long long)acc);

    printf("\nConclusion: the bit vector describes the whole 4 TB disk in %.1f MiB\n",
           (double)bitvec / (1024.0 * 1024.0));
    printf("and a run is found by reading words; the linked list pops in O(1)\n");
    printf("but costs 4 bytes per free block and must be walked to find a run.\n");
    printf("Grouping and counting cut that memory by the group size, which is\n");
    printf("why real file systems combine a bit vector or counts with extents.\n");
    return 0;
}
