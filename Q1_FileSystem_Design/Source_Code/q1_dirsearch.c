/* q1_dirsearch.c - Task 1.1: the cost of one flat directory.
 *
 * The proposal puts 12,000 students' files in a single flat directory.  A
 * directory is an unordered list, so a lookup is a linear scan of the whole
 * directory.  This program builds exactly that directory in memory and
 * measures the look-up cost, then builds a three-level tree
 * (department / year / student) and measures the same operation.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q1_dirsearch.c -o q1_dirsearch
 */
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define STUDENTS 12000
#define SEARCHES 2000
#define DEPTS 4
#define YEARS 4
#define PER_LEAF (STUDENTS / (DEPTS * YEARS))

static double now_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec / 1e3;
}

static void make_name(char *buf, size_t n, int id)
{
    snprintf(buf, n, "student_%05d_os_assignment_v3.docx", id);
}

/* one flat directory: an unordered array of names */
static char flat[STUDENTS][64];

/* three-level tree: dept -> year -> leaf directory of PER_LEAF sorted names */
static char tree[DEPTS][YEARS][PER_LEAF][64];

int main(void)
{
    for (int i = 0; i < STUDENTS; i++) {
        make_name(flat[i], sizeof flat[i], i);
        int d = i % DEPTS;
        int y = (i / DEPTS) % YEARS;
        int s = i / (DEPTS * YEARS);
        make_name(tree[d][y][s], 64, i);
    }

    /* Sort each leaf so that the tree can use binary search, as a real
     * directory with an index would. */
    for (int d = 0; d < DEPTS; d++)
        for (int y = 0; y < YEARS; y++)
            for (int a = 1; a < PER_LEAF; a++) {
                char key[64];
                memcpy(key, tree[d][y][a], 64);
                int b = a - 1;
                while (b >= 0 && strcmp(tree[d][y][b], key) > 0) {
                    memcpy(tree[d][y][b + 1], tree[d][y][b], 64);
                    b--;
                }
                memcpy(tree[d][y][b + 1], key, 64);
            }

    char target[64];
    long cmp_flat = 0, cmp_tree = 0;
    int found_flat = 0, found_tree = 0;

    /* ---- flat directory: linear search ---- */
    double t0 = now_us();
    for (int r = 0; r < SEARCHES; r++) {
        make_name(target, sizeof target, (r * 7919) % STUDENTS);
        for (int i = 0; i < STUDENTS; i++) {
            cmp_flat++;
            if (strcmp(flat[i], target) == 0) {
                found_flat++;
                break;
            }
        }
    }
    double t_flat = now_us() - t0;

    /* ---- tree: choose dept, choose year, binary search the leaf ---- */
    t0 = now_us();
    for (int r = 0; r < SEARCHES; r++) {
        int id = (r * 7919) % STUDENTS;
        make_name(target, sizeof target, id);
        int d = id % DEPTS, y = (id / DEPTS) % YEARS;
        /* the hash of the student id replaces the scan of the two upper levels */
        cmp_tree += 2;
        int lo = 0, hi = PER_LEAF - 1;
        while (lo <= hi) {
            int mid = (lo + hi) / 2;
            cmp_tree++;
            int c = strcmp(tree[d][y][mid], target);
            if (c == 0) {
                found_tree++;
                break;
            }
            if (c < 0)
                lo = mid + 1;
            else
                hi = mid - 1;
        }
    }
    double t_tree = now_us() - t0;

    printf("Task 1.1  one flat directory versus a directory tree\n");
    printf("students in the directory : %d\n", STUDENTS);
    printf("look-ups performed        : %d each\n\n", SEARCHES);

    printf("flat directory (unordered, linear scan)\n");
    printf("  comparisons per look-up : %.1f\n", (double)cmp_flat / SEARCHES);
    printf("  mean look-up time       : %.3f us\n", t_flat / SEARCHES);
    printf("  total for %4d searches : %.2f ms\n", SEARCHES, t_flat / 1000.0);
    printf("  found                   : %d\n\n", found_flat);

    printf("three-level tree (dept / year / student, indexed leaf)\n");
    printf("  comparisons per look-up : %.1f\n", (double)cmp_tree / SEARCHES);
    printf("  mean look-up time       : %.3f us\n", t_tree / SEARCHES);
    printf("  total for %4d searches : %.2f ms\n", SEARCHES, t_tree / 1000.0);
    printf("  found                   : %d\n\n", found_tree);

    printf("speed-up of the tree    : %.1fx\n", t_flat / t_tree);
    printf("comparison ratio        : %.1fx fewer name comparisons\n",
           (double)cmp_flat / (double)cmp_tree);

    /* Note: both directories are held in RAM, so these numbers compare the
     * search algorithms and not the disk.  On disk the flat case is far worse:
     * every one of the ~6000 entries examined may cost a block read. */
    return 0;
}
