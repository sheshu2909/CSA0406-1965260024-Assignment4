/* q2_alloc.c - Assignment 4, Task 2 "Complete the Code".
 *
 * The program given in the assignment, with TODO 1 replaced by a first-fit
 * contiguous allocator.  Nothing else in the given code was changed.
 *
 * Expected output (from the assignment sheet):
 *   AAAAAA........CCCCC.............
 *   E (10 blocks) contiguous: start 19
 *   E (10 blocks) indexed: index block 6, data blocks 7 8 9 10 11 12 13 29 30 31
 *   AAAAAAeEEEEEEECCCCCEEEEEEEEEEEEE
 *
 * Build: gcc -std=c11 -Wall -Wextra q2_alloc.c -o q2_alloc
 */
#include <stdio.h>
#include <string.h>

#define BLOCKS 32

char disk[BLOCKS];   /* '.' = free, otherwise the file letter */

/* Contiguous allocation, first fit: returns the start block or -1. */
int alloc_contiguous(char file, int size)
{
    /* TODO 1: Scan the disk for the first run of size consecutive free blocks;
     * mark them with the file letter and return the start block, or return -1
     * if no run is long enough. */
    int run = 0, start = -1;
    for (int b = 0; b < BLOCKS; b++) {
        if (disk[b] == '.') {
            if (run == 0)
                start = b;          /* the run begins here */
            if (++run == size) {
                for (int k = start; k < start + size; k++)
                    disk[k] = file;
                return start;
            }
        } else {
            run = 0;                /* the run was broken */
        }
    }
    return -1;
}

/* Indexed allocation: one index block plus any free data blocks. */
int alloc_indexed(char file, int size, int index[])
{
    int got = 0, idx = -1;
    for (int b = 0; b < BLOCKS && got <= size; b++) {
        if (disk[b] != '.') continue;
        if (idx < 0) idx = b;               /* first free block holds the index */
        else index[got++] = b;
        if (got == size) break;
    }
    if (idx < 0 || got < size) return -1;
    disk[idx] = (char)(file + 32);          /* lowercase letter = index block */
    for (int i = 0; i < size; i++) disk[index[i]] = file;
    return idx;
}

void release(char file)
{
    for (int b = 0; b < BLOCKS; b++)
        if (disk[b] == file) disk[b] = '.';
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
    printf("%.32s\n", disk);

    printf("E (10 blocks) contiguous: start %d\n", alloc_contiguous('E', 10));

    int index[16];
    int ib = alloc_indexed('E', 10, index);
    printf("E (10 blocks) indexed: index block %d, data blocks", ib);
    for (int i = 0; i < 10; i++) printf(" %d", index[i]);
    printf("\n%.32s\n", disk);
    return 0;
}
