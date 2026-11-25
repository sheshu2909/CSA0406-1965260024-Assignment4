/* q1_growth.c - Task 1.1: what contiguous allocation costs when files grow.
 *
 * The proposal stores every file contiguously.  A contiguous file can only
 * grow if the block physically after it happens to be free; otherwise the
 * whole file must be copied to a free run large enough for its new size.
 *
 * This program models a 1 TB disk (4 KB blocks, one bit per block) and
 * 12,000 student files.  It records how often files grow in place, how often
 * they must be relocated, and how many bytes have to be copied because of it.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q1_growth.c -o q1_growth
 */
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BLOCK 4096ULL
#define NBLOCKS (1ULL << 28)            /* 1 TB / 4 KB = 268,435,456 blocks */
#define NWORDS (NBLOCKS / 64)
#define NFILES 12000
#define ROUNDS 40
#define GROWS_PER_ROUND 300
#define NONE (~0ULL)

static uint64_t *bm;                    /* 1 = occupied */
static uint64_t cursor;                 /* next-fit cursor, in blocks */

struct file {
    uint64_t start;
    uint64_t len;                       /* blocks */
};

static struct file files[NFILES];

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e3 + (double)ts.tv_nsec / 1e6;
}

static int used(uint64_t b) { return (int)((bm[b >> 6] >> (b & 63)) & 1ULL); }
static void mark(uint64_t b) { bm[b >> 6] |= 1ULL << (b & 63); }
static void clear_bit(uint64_t b) { bm[b >> 6] &= ~(1ULL << (b & 63)); }

/* First fit for a run of "len" free blocks, starting at the cursor and
 * wrapping once.  Returns NONE when no run is long enough. */
static uint64_t find_run(uint64_t len, uint64_t *scanned)
{
    for (int pass = 0; pass < 2; pass++) {
        uint64_t begin = (pass == 0) ? cursor : 0;
        uint64_t end = (pass == 0) ? NBLOCKS : cursor;
        uint64_t run = 0, start = 0;
        for (uint64_t b = begin; b < end; b++) {
            (*scanned)++;
            if (bm[b >> 6] == ~0ULL) {          /* whole word full: skip it */
                b = ((b >> 6) + 1) * 64 - 1;
                run = 0;
                continue;
            }
            if (!used(b)) {
                if (run == 0)
                    start = b;
                if (++run == len)
                    return start;
            } else {
                run = 0;
            }
        }
    }
    return NONE;
}

/* Largest free run on the disk, found by scanning the bitmap once. */
static uint64_t longest_free(void)
{
    uint64_t best = 0, run = 0;
    for (uint64_t b = 0; b < NBLOCKS; b++) {
        if (!used(b)) {
            if (++run > best)
                best = run;
        } else {
            run = 0;
        }
    }
    return best;
}

int main(void)
{
    bm = calloc(NWORDS, sizeof *bm);
    if (!bm) {
        fprintf(stderr, "out of memory\n");
        return 1;
    }

    srand(20261114);

    double t0 = now_ms();
    uint64_t scanned = 0;

    /* ---- create 12,000 files, 1 MB to 8 MB each ---- */
    for (int i = 0; i < NFILES; i++) {
        uint64_t blocks = 256 + (uint64_t)(rand() % (2048 - 256 + 1));
        uint64_t at = find_run(blocks, &scanned);
        if (at == NONE) {
            fprintf(stderr, "disk full while creating file %d\n", i);
            return 1;
        }
        for (uint64_t k = 0; k < blocks; k++)
            mark(at + k);
        files[i].start = at;
        files[i].len = blocks;
        cursor = at + blocks;
    }
    double t_create = now_ms() - t0;

    uint64_t total_blocks = 0;
    for (int i = 0; i < NFILES; i++)
        total_blocks += files[i].len;

    printf("Task 1.1  contiguous allocation under file growth\n");
    printf("disk              : 1 TB, 4 KB blocks, %llu blocks\n",
           (unsigned long long)NBLOCKS);
    printf("files             : %d\n", NFILES);
    printf("data placed       : %.2f GB in %llu blocks\n",
           (double)total_blocks * (double)BLOCK / 1e9,
           (unsigned long long)total_blocks);
    printf("creation          : %.1f ms, %llu blocks examined\n\n",
           t_create, (unsigned long long)scanned);

    /* ---- each round, 300 random files grow by 1 to 16 blocks ---- */
    uint64_t in_place = 0, moved = 0, moved_blocks = 0, failed = 0;
    uint64_t rescan = 0;
    double g0 = now_ms();
    for (int r = 0; r < ROUNDS; r++) {
        for (int g = 0; g < GROWS_PER_ROUND; g++) {
            int i = rand() % NFILES;
            uint64_t extra = 1 + (uint64_t)(rand() % 16);
            uint64_t next = files[i].start + files[i].len;

            if (next < NBLOCKS && !used(next) && !used(next + extra - 1)) {
                /* the blocks after the file are free: extend in place */
                for (uint64_t k = 0; k < extra; k++)
                    mark(next + k);
                files[i].len += extra;
                in_place++;
            } else {
                uint64_t need = files[i].len + extra;
                uint64_t at = find_run(need, &rescan);
                if (at == NONE) {
                    failed++;
                    continue;
                }
                for (uint64_t k = 0; k < files[i].len; k++)
                    clear_bit(files[i].start + k);
                for (uint64_t k = 0; k < need; k++)
                    mark(at + k);
                moved_blocks += files[i].len;   /* the whole file is copied */
                moved++;
                files[i].start = at;
                files[i].len = need;
                cursor = at + need;
            }
        }
    }
    double t_grow = now_ms() - g0;

    uint64_t used_blocks = 0;
    for (int i = 0; i < NFILES; i++)
        used_blocks += files[i].len;

    double t_long = now_ms();
    uint64_t longest = longest_free();
    t_long = now_ms() - t_long;

    printf("growth rounds     : %d x %d single-block growth events\n",
           ROUNDS, GROWS_PER_ROUND);
    printf("grew in place     : %llu\n", (unsigned long long)in_place);
    printf("had to be moved   : %llu  (%.2f%% of growth events)\n",
           (unsigned long long)moved,
           100.0 * (double)moved / (double)(in_place + moved + failed));
    printf("blocks copied     : %llu  (%.2f GB of extra writes)\n",
           (unsigned long long)moved_blocks,
           (double)moved_blocks * (double)BLOCK / 1e9);
    printf("growth that failed: %llu\n", (unsigned long long)failed);
    printf("time for growth   : %.1f ms\n", t_grow);
    printf("free-space scans  : %llu blocks examined while growing\n",
           (unsigned long long)rescan);

    printf("\nfinal state\n");
    printf("  used            : %.2f GB (%.2f%% of the disk)\n",
           (double)used_blocks * (double)BLOCK / 1e9,
           100.0 * (double)used_blocks / (double)NBLOCKS);
    printf("  free            : %.2f GB\n",
           (double)(NBLOCKS - used_blocks) * (double)BLOCK / 1e9);
    printf("  longest free run: %llu blocks (%.2f MB), found in %.1f ms\n",
           (unsigned long long)longest, (double)longest * (double)BLOCK / 1e6,
           t_long);

    uint64_t big = 512ULL * 1024 * 1024 / BLOCK;      /* a 512 MB file */
    uint64_t dummy = 0;
    uint64_t at = find_run(big, &dummy);
    printf("  a new 512 MB file: %s\n",
           at == NONE ? "cannot be placed - no run of 131072 blocks"
                      : "placed");
    printf("  fragmentation   : %.2f%% (1 - longest run / free blocks)\n",
           100.0 * (1.0 - (double)longest /
                          (double)(NBLOCKS - used_blocks)));

    free(bm);
    return 0;
}
