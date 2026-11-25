/* q3_meta.c - Task 3.2 / 3.3: what a write costs with journaling and with
 * copy-on-write.
 *
 * Three update patterns are measured on the real disk of this machine:
 *
 *   writeback   : overwrite 4 KB in place, then fsync.        (1 data write)
 *   journaled   : append the 4 KB to a journal, fsync, then overwrite the
 *                 data block, fsync.                           (2 writes)
 *   copy-on-write: write the 4 KB to a fresh block, fsync, then write the
 *                 pointer that switches the tree, fsync.       (2 writes)
 *
 * The point is the number of forced flushes and the bytes written for one
 * 4 KB logical update, not the exact behaviour of ext4 or Btrfs.  The file
 * system of this machine is reported by the program so that the result is
 * not mistaken for an ext4 measurement.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q3_meta.c -o q3_meta
 */
#define _POSIX_C_SOURCE 200809L

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define UPDATES 1000
#define BLK 4096
#define DATA_BYTES (64ULL * 1024 * 1024)     /* 16,384 blocks */

static double now_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec / 1e3;
}

static int cmp_double(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static void stats(const char *name, double *v, int n, unsigned long long bytes)
{
    qsort(v, (size_t)n, sizeof v[0], cmp_double);
    double sum = 0;
    for (int i = 0; i < n; i++) sum += v[i];
    printf("%-13s mean %8.1f us   median %8.1f us   p95 %8.1f us   "
           "%.0f KB written per update\n",
           name, sum / n, v[n / 2], v[(int)(n * 0.95)],
           (double)bytes / (double)n / 1024.0);
}

static void put(int fd, long long off, const void *buf, size_t n)
{
    if (pwrite(fd, buf, n, (off_t)off) != (ssize_t)n) {
        perror("pwrite");
        exit(1);
    }
}

int main(void)
{
    char buf[BLK];
    memset(buf, 0xA5, sizeof buf);
    double *times = malloc(UPDATES * sizeof *times);
    if (!times) return 1;

    printf("Task 3.2  cost of one 4 KB update on this machine\n");
    printf("file system of the working directory: see 'stat -f .' below\n");
    fflush(stdout);
    if (system("stat -f -c '  type=%T block=%S' . 2>/dev/null || echo '  stat -f unavailable'") != 0) { }

    /* ---- 1. write-back: one write, one flush ---- */
    int fd = open("logs/q3_writeback.dat", O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { perror("open"); return 1; }
    for (unsigned long long off = 0; off < DATA_BYTES; off += BLK) put(fd, (long long)off, buf, BLK);
    fsync(fd);

    unsigned long long bytes = 0;
    for (int i = 0; i < UPDATES; i++) {
        long long off = (long long)((rand() % (DATA_BYTES / BLK)) * BLK);
        double t = now_us();
        put(fd, off, buf, BLK);
        fsync(fd);
        times[i] = now_us() - t;
        bytes += BLK;
    }
    stats("writeback", times, UPDATES, bytes);
    close(fd);

    /* ---- 2. journaled: append the record, flush, then the data ---- */
    int jfd = open("logs/q3_journal.dat", O_RDWR | O_CREAT | O_TRUNC, 0644);
    fd = open("logs/q3_journaled.dat", O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (jfd < 0 || fd < 0) { perror("open journal"); return 1; }
    for (unsigned long long off = 0; off < DATA_BYTES; off += BLK) put(fd, (long long)off, buf, BLK);
    fsync(fd);
    lseek(jfd, 0, SEEK_SET);

    bytes = 0;
    for (int i = 0; i < UPDATES; i++) {
        long long off = (long long)((rand() % (DATA_BYTES / BLK)) * BLK);
        double t = now_us();
        put(jfd, (long long)i * BLK, buf, BLK);   /* the journal record */
        fsync(jfd);                               /* committed to the journal */
        put(fd, off, buf, BLK);                   /* the real block */
        fsync(fd);
        times[i] = now_us() - t;
        bytes += 2 * BLK;
    }
    stats("journaled", times, UPDATES, bytes);
    close(fd);
    close(jfd);

    /* ---- 3. copy-on-write: new block, then the new root pointer ---- */
    int rfd = open("logs/q3_cow_root.dat", O_RDWR | O_CREAT | O_TRUNC, 0644);
    fd = open("logs/q3_cow.dat", O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (rfd < 0 || fd < 0) { perror("open cow"); return 1; }
    for (unsigned long long off = 0; off < DATA_BYTES; off += BLK) put(fd, (long long)off, buf, BLK);
    fsync(fd);

    bytes = 0;
    unsigned long long next_free = DATA_BYTES;        /* append a new block */
    for (int i = 0; i < UPDATES; i++) {
        long long off = (long long)next_free;
        next_free += BLK;
        double t = now_us();
        put(fd, off, buf, BLK);                       /* write the new copy */
        fsync(fd);
        put(rfd, 0, &off, sizeof off);                /* switch the tree */
        fsync(rfd);
        times[i] = now_us() - t;
        bytes += BLK + BLK;                           /* data + metadata block */
    }
    stats("copy-on-write", times, UPDATES, bytes);
    close(fd);
    close(rfd);

    printf("\nUpdates measured : %d per pattern\n", UPDATES);
    printf("The journaled and copy-on-write patterns each write the 4 KB twice\n");
    printf("and force two flushes; write-back writes it once and forces one.\n");
    printf("That is the price of being able to recover after a power failure.\n");
    free(times);
    return 0;
}
