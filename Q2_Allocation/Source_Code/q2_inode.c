/* q2_inode.c - Task 2.3: the largest file an inode can describe.
 *
 * inode: 12 direct, 1 single-indirect, 1 double-indirect, 1 triple-indirect
 * pointer, 4-byte block addresses, 4 KB blocks.
 *
 * The arithmetic is done with 64-bit integers and printed step by step so the
 * result can be checked by hand.
 *
 * Build: gcc -std=c11 -Wall -Wextra q2_inode.c -o q2_inode
 */
#include <stdio.h>

#define BLOCK 4096ULL
#define PTR 4ULL                       /* bytes per block address */
#define PTRS_PER_BLOCK (BLOCK / PTR)
#define DIRECT 12ULL

static void human(unsigned long long bytes, char *out, size_t n)
{
    const char *unit[] = { "B", "KiB", "MiB", "GiB", "TiB", "PiB" };
    double v = (double)bytes;
    int u = 0;
    while (v >= 1024.0 && u < 5) { v /= 1024.0; u++; }
    snprintf(out, n, "%.3f %s", v, unit[u]);
}

int main(void)
{
    unsigned long long single = PTRS_PER_BLOCK;
    unsigned long long dbl = single * single;
    unsigned long long triple = dbl * single;

    unsigned long long blocks = DIRECT + single + dbl + triple;
    unsigned long long bytes = blocks * BLOCK;

    char h[64];
    printf("Task 2.3  maximum file size for the given inode\n");
    printf("block size        : %llu bytes\n", (unsigned long long)BLOCK);
    printf("pointer size      : %llu bytes\n", (unsigned long long)PTR);
    printf("pointers per block: %llu\n\n", (unsigned long long)PTRS_PER_BLOCK);

    printf("  direct        12 pointers -> %llu blocks\n", DIRECT);
    printf("  single       %4llu pointers -> %llu blocks\n",
           (unsigned long long)PTRS_PER_BLOCK, single);
    printf("  double  %4llu^2 pointers -> %llu blocks\n",
           (unsigned long long)PTRS_PER_BLOCK, dbl);
    printf("  triple  %4llu^3 pointers -> %llu blocks\n",
           (unsigned long long)PTRS_PER_BLOCK, triple);
    printf("  ------------------------------------------------\n");
    printf("  total                  -> %llu blocks\n", blocks);
    printf("  in bytes               -> %llu bytes\n", bytes);
    human(bytes, h, sizeof h);
    printf("  in human units         -> %s  (%.3f TB)\n\n", h,
           (double)bytes / 1e12);

    printf("reads needed to reach a block\n");
    printf("  blocks 0-11            : direct pointer       1 read\n");
    printf("  blocks 12-1035         : single indirect      2 reads\n");
    printf("  blocks 1036-1049611    : double indirect      3 reads\n");
    printf("  blocks above that      : triple indirect      4 reads\n\n");

    printf("how many bytes each level covers\n");
    printf("  direct    : %8llu bytes (%.1f KiB)\n", DIRECT * BLOCK,
           (double)(DIRECT * BLOCK) / 1024.0);
    printf("  single    : %8llu bytes (%.1f MiB)\n", single * BLOCK,
           (double)(single * BLOCK) / (1024.0 * 1024.0));
    printf("  double    : %8llu bytes (%.1f MiB)\n", dbl * BLOCK,
           (double)(dbl * BLOCK) / (1024.0 * 1024.0));
    printf("  triple    : %8llu bytes (%.3f TiB)\n", triple * BLOCK,
           (double)(triple * BLOCK) / (1024.0 * 1024.0 * 1024.0 * 1024.0));

    printf("\nthe 4 GB file of the assignment needs %llu blocks,\n",
           4ULL * 1024 * 1024 * 1024 / BLOCK);
    printf("so it is described by the direct pointers plus part of the\n");
    printf("single-indirect block: it never touches the double indirect.\n");
    return 0;
}
