/* q2_alloc_demo.c - why "21 free blocks" is not the same as "10 free blocks
 * in a row".  This is an extra demonstration for Task 2, not a replacement for
 * the required program.
 *
 * The state after the assignment's sequence is
 *   A A A A A A . . . . . . . . C C C C C . . . . . . . . . . . . .
 * which is 21 free blocks in two runs: 8 blocks at 6 and 13 blocks at 19.
 * The required program asks for 10 blocks and first fit finds the run at 19.
 * Growing the request by a few blocks shows the failure mode: no run is long
 * enough, although more than twice the requested space is free.
 *
 * Build: gcc -std=c11 -Wall -Wextra q2_alloc_demo.c -o q2_alloc_demo
 */
#include <stdio.h>
#include <string.h>

#define BLOCKS 32

static char disk[BLOCKS];

static int alloc_contiguous(char file, int size)
{
    int run = 0, start = -1;
    for (int b = 0; b < BLOCKS; b++) {
        if (disk[b] == '.') {
            if (run == 0) start = b;
            if (++run == size) {
                for (int k = start; k < start + size; k++) disk[k] = file;
                return start;
            }
        } else {
            run = 0;
        }
    }
    return -1;
}

static void release(char file)
{
    for (int b = 0; b < BLOCKS; b++)
        if (disk[b] == file) disk[b] = '.';
}

static void show(const char *label)
{
    printf("%-24s |%.32s|\n", label, disk);
}

int main(void)
{
    memset(disk, '.', BLOCKS);
    alloc_contiguous('A', 6);
    alloc_contiguous('B', 8);
    alloc_contiguous('C', 5);
    alloc_contiguous('D', 7);
    release('B');
    release('D');

    show("after B and D released");

    /* the free runs, counted block by block */
    int free_blocks = 0, run = 0, runs = 0, longest = 0, first_longest = -1;
    for (int b = 0; b < BLOCKS; b++) {
        if (disk[b] == '.') {
            if (run == 0) runs++;
            run++;
            free_blocks++;
            if (run > longest) { longest = run; first_longest = b - run + 1; }
        } else {
            run = 0;
        }
    }
    printf("free blocks: %d in %d runs, longest run %d blocks at %d\n",
           free_blocks, runs, longest, first_longest);

    printf("\nwhat size of request can still be met contiguously?\n");
    for (int size = 8; size <= 16; size++) {
        char copy[BLOCKS];
        memcpy(copy, disk, BLOCKS);
        int at = alloc_contiguous('X', size);
        printf("  %2d blocks -> %s", size,
               at < 0 ? "FAILED (external fragmentation)\n" : "placed at ");
        if (at >= 0) printf("%d\n", at);
        memcpy(disk, copy, BLOCKS);     /* undo, so each trial starts equal */
    }

    printf("\nthe same request met by indexed allocation\n");
    int need = 14, got = 0, idx = -1, data[32];
    for (int b = 0; b < BLOCKS && got < need; b++) {
        if (disk[b] != '.') continue;
        if (idx < 0) { idx = b; continue; }
        data[got++] = b;
    }
    disk[idx] = (char)('E' + 32);
    for (int i = 0; i < got; i++) disk[data[i]] = 'E';
    printf("14 blocks: index block %d, data blocks", idx);
    for (int i = 0; i < got; i++) printf(" %d", data[i]);
    printf("\n");
    show("after indexed allocation");
    return 0;
}
