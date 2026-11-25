/* q2_compare.c - Task 2.2 / 2.3: contiguous first fit, best fit, worst fit
 * and indexed allocation on one and the same workload.
 *
 * A 256 GB disk (4 KB blocks) is described by a sorted list of free extents.
 * Every policy performs the identical sequence of operations:
 *   1. create 4,000 files of 1 to 16 MB,
 *   2. delete every third file,
 *   3. create 1,500 more files of the same size range.
 * The program records the placement work (free extents examined), the number
 * of failures, and the fragmentation that is left behind.  It then walks a
 * 4 GB linked chain in memory to show what "follow the pointers" costs.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q2_compare.c -o q2_compare
 */
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BLOCK_BYTES 4096ULL
#define DISK_BLOCKS (1ULL << 24)          /* 64 GiB, about 70% full */
#define N1 6000
#define N2 2000
#define MAXF (N1 + N2 + 10)
#define MAXEXT 400000
#define MAXCHUNK 128
#define LINKED_BLOCKS (1ULL << 20)        /* 4 GB file */

struct chunk { unsigned long long start, len; };

struct file {
    unsigned long long start, len;        /* contiguous policies */
    struct chunk ch[MAXCHUNK];            /* indexed policy */
    int nch;
    int alive;
};

static unsigned long long ext_start[MAXEXT], ext_len[MAXEXT];
static int nex;
static unsigned long long free_blocks = DISK_BLOCKS;
static struct file *fl;
static const char *policy_name[] = { "contiguous first fit",
                                     "contiguous best fit",
                                     "contiguous worst fit",
                                     "indexed (one index block)" };

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e3 + (double)ts.tv_nsec / 1e6;
}

/* ---- the free-space list: sorted by start, neighbours merged ---- */
static void insert_free(unsigned long long s, unsigned long long l)
{
    free_blocks += l;
    int i = 0;
    while (i < nex && ext_start[i] < s) i++;

    /* merge with the previous extent if they touch */
    if (i > 0 && ext_start[i - 1] + ext_len[i - 1] == s) {
        ext_len[i - 1] += l;
        s = ext_start[i - 1];
        l = ext_len[i - 1];
        if (i < nex && s + l == ext_start[i]) {   /* and with the next one */
            ext_len[i - 1] += ext_len[i];
            memmove(&ext_start[i], &ext_start[i + 1],
                    (size_t)(nex - i - 1) * sizeof ext_start[0]);
            memmove(&ext_len[i], &ext_len[i + 1],
                    (size_t)(nex - i - 1) * sizeof ext_len[0]);
            nex--;
        }
        return;
    }
    if (i < nex && s + l == ext_start[i]) {      /* merge with the next only */
        ext_start[i] = s;
        ext_len[i] += l;
        return;
    }
    if (nex == MAXEXT) abort();
    memmove(&ext_start[i + 1], &ext_start[i], (size_t)(nex - i) * sizeof ext_start[0]);
    memmove(&ext_len[i + 1], &ext_len[i], (size_t)(nex - i) * sizeof ext_len[0]);
    ext_start[i] = s;
    ext_len[i] = l;
    nex++;
}

static void take_head(int i, unsigned long long need, unsigned long long *at)
{
    *at = ext_start[i];
    ext_start[i] += need;
    ext_len[i] -= need;
    free_blocks -= need;
    if (ext_len[i] == 0) {
        memmove(&ext_start[i], &ext_start[i + 1],
                (size_t)(nex - i - 1) * sizeof ext_start[0]);
        memmove(&ext_len[i], &ext_len[i + 1],
                (size_t)(nex - i - 1) * sizeof ext_len[0]);
        nex--;
    }
}

static int find_fit(int policy, unsigned long long need,
                    unsigned long long *examined)
{
    int best = -1;
    unsigned long long best_len = 0;
    for (int i = 0; i < nex; i++) {
        (*examined)++;
        if (ext_len[i] < need) continue;
        if (policy == 0) return i;                    /* first fit */
        if (policy == 1) {                            /* best fit */
            if (best < 0 || ext_len[i] < best_len) { best = i; best_len = ext_len[i]; }
        } else {                                      /* worst fit */
            if (best < 0 || ext_len[i] > best_len) { best = i; best_len = ext_len[i]; }
        }
    }
    return best;
}

static int alloc_file(int policy, int idx, unsigned long long need,
                      unsigned long long *examined)
{
    struct file *f = &fl[idx];
    f->nch = 0;
    f->alive = 1;

    if (policy <= 2) {
        int i = find_fit(policy, need, examined);
        if (i < 0) { f->alive = 0; return 0; }
        take_head(i, need, &f->start);
        f->len = need;
        return 1;
    }

    /* indexed: one block for the index, then data blocks from anywhere */
    unsigned long long at;
    int i = find_fit(0, 1, examined);
    if (i < 0) { f->alive = 0; return 0; }
    take_head(i, 1, &at);
    f->start = at;                      /* the index block */
    f->len = 0;
    unsigned long long remaining = need;
    while (remaining > 0) {
        if (f->nch == MAXCHUNK) { f->alive = 0; return 0; }
        int j = find_fit(0, 1, examined);
        if (j < 0) { f->alive = 0; return 0; }
        unsigned long long take = ext_len[j] < remaining ? ext_len[j] : remaining;
        f->ch[f->nch].start = ext_start[j];
        f->ch[f->nch].len = take;
        f->nch++;
        take_head(j, take, &at);
        remaining -= take;
        f->len += take;
    }
    return 1;
}

static void free_file(int policy, int idx)
{
    struct file *f = &fl[idx];
    if (!f->alive) return;
    if (policy <= 2) {
        insert_free(f->start, f->len);
    } else {
        insert_free(f->start, 1);
        for (int c = 0; c < f->nch; c++)
            insert_free(f->ch[c].start, f->ch[c].len);
    }
    f->alive = 0;
}

static void run(int policy)
{
    memset(fl, 0, sizeof(struct file) * MAXF);
    nex = 1;
    ext_start[0] = 0;
    ext_len[0] = DISK_BLOCKS;
    free_blocks = DISK_BLOCKS;

    srand(4242);                       /* identical workload for every policy */
    unsigned long long examined = 0, fail = 0;
    double t0 = now_ms();

    for (int i = 0; i < N1; i++) {
        unsigned long long size = 256 + (unsigned long long)(rand() % 3841);
        if (!alloc_file(policy, i, size, &examined)) fail++;
    }
    for (int i = 0; i < N1; i += 3)
        free_file(policy, i);

    int made = 0;
    for (int k = 0; k < N2; k++) {
        unsigned long long size = 256 + (unsigned long long)(rand() % 3841);
        if (!alloc_file(policy, N1 + k, size, &examined)) fail++;
        else made++;
    }
    double dt = now_ms() - t0;

    double largest = 0;
    for (int i = 0; i < nex; i++)
        if ((double)ext_len[i] > largest) largest = (double)ext_len[i];

    unsigned long long dummy = 0;
    int big = find_fit(0, 262144, &dummy);     /* a 1 GB file */

    double frag = 100.0 * (1.0 - largest / (double)free_blocks);
    printf("%-24s | %7.1f | %9llu | %6llu | %10.2f | %6.2f | %5s\n",
           policy_name[policy], dt, (unsigned long long)examined,
           (unsigned long long)fail, largest * (double)BLOCK_BYTES / 1e9,
           frag, big >= 0 ? "yes" : "no");

    if (made < N2) printf("   (%llu of the %d new files could not be placed)\n",
                          (unsigned long long)(N2 - made), N2);
}

static void linked_walk(void)
{
    /* A 4 GB file in 4 KB blocks has 1,048,576 blocks.  With linked
     * allocation the disk controller can only find block k by following the
     * chain from block 0, so reaching the last block costs one read per block. */
    uint32_t *next = malloc((size_t)LINKED_BLOCKS * sizeof *next);
    if (!next) return;
    for (unsigned long long i = 0; i < LINKED_BLOCKS - 1; i++)
        next[i] = (uint32_t)(i + 1);
    next[LINKED_BLOCKS - 1] = 0xFFFFFFFFu;

    double t0 = now_ms();
    unsigned long long hops = 0, b = 0;
    while (next[b] != 0xFFFFFFFFu) { b = next[b]; hops++; }
    double dt = now_ms() - t0;

    printf("\nreads needed to reach the last block of a 4 GB file (4 KB blocks)\n");
    printf("  contiguous : 1 read  (one seek to start + length)\n");
    printf("  indexed    : 2 reads (the index block, then the data block)\n");
    printf("  linked/FAT : %llu reads (one per block in the chain)\n",
           (unsigned long long)(hops + 1));
    printf("  walking the chain in RAM took %.2f ms, i.e. %.1f ns per hop;\n",
           dt, dt * 1e6 / (double)(hops + 1));
    printf("  on a disk each hop is a seek, so the same walk costs seconds.\n");
    free(next);
}

int main(void)
{
    fl = calloc(MAXF, sizeof *fl);
    if (!fl) return 1;

    printf("Task 2.2 / 2.3  allocation policies on the same workload\n");
    printf("disk %llu GB, block %llu B, %d + %d files, every third file deleted\n\n",
           (unsigned long long)(DISK_BLOCKS * BLOCK_BYTES / 1000000000ULL),
           (unsigned long long)BLOCK_BYTES, N1, N2);
    printf("%-24s | %7s | %9s | %6s | %10s | %6s | %5s\n",
           "policy", "time ms", "extents", "failed", "largest GB", "frag %", "1 GB?");
    printf("-------------------------+---------+-----------+--------+------------+--------+------\n");
    for (int p = 0; p < 4; p++)
        run(p);

    printf("\nextents = free extents examined to place every file;\n");
    printf("frag %%  = 1 - largest free extent / all free blocks\n");
    linked_walk();
    free(fl);
    return 0;
}
