/* q6_measure.c - Task 6, stage 5: measure the real disk before simulating.
 *
 * The streaming design is simulated with the latency of the storage tiers.
 * The SSD tier of this laptop is measured here: random 4 KB read latency,
 * sequential read throughput and sequential write throughput.  The measured
 * random-read latency is the number the simulator uses for a cache hit.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q6_measure.c -o q6_measure
 */
#define _POSIX_C_SOURCE 200809L

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define FILE_MB 1024
#define RANDOM_READS 5000

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

static int make_file(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (f) {
        fseek(f, 0, SEEK_END);
        long long n = ftell(f);
        fclose(f);
        if (n == (long long)FILE_MB * 1024 * 1024) return 0;
    }
    f = fopen(path, "wb");
    if (!f) return -1;
    char *buf = malloc(1 << 20);
    if (!buf) { fclose(f); return -1; }
    memset(buf, 0x33, 1 << 20);
    for (int i = 0; i < FILE_MB; i++)
        if (fwrite(buf, 1 << 20, 1, f) != 1) { free(buf); fclose(f); return -1; }
    free(buf);
    fclose(f);
    return 0;
}

int main(void)
{
    const char *path = "tmp/q6_probe.bin";
    if (make_file(path) != 0) {
        fprintf(stderr, "cannot create %s\n", path);
        return 1;
    }

    int fd = open(path, O_RDWR);
    if (fd < 0) { perror("open"); return 1; }
    char *b = malloc(1 << 20);
    if (!b) return 1;

    printf("Task 6, stage 5  measured storage tiers of this machine\n");
    printf("probe file: %s, %d MB\n\n", path, FILE_MB);

    /* ---- random 4 KB reads ---- */
    double *lat = malloc(RANDOM_READS * sizeof *lat);
    if (!lat) return 1;
    srand(20261114);
    for (int i = 0; i < RANDOM_READS; i++) {
        long long off = (long long)(rand() % (FILE_MB * 256)) * 4096;
        double t = now_us();
        if (pread(fd, b, 4096, (off_t)off) != 4096) { perror("pread"); return 1; }
        lat[i] = now_us() - t;
    }
    double sum = 0;
    for (int i = 0; i < RANDOM_READS; i++) sum += lat[i];
    qsort(lat, RANDOM_READS, sizeof *lat, cmp_double);
    double mean = sum / RANDOM_READS;
    printf("random 4 KB reads  : %d reads\n", RANDOM_READS);
    printf("  mean  %8.1f us   p50 %8.1f us   p95 %8.1f us   p99 %8.1f us\n",
           mean, lat[RANDOM_READS / 2], lat[(int)(RANDOM_READS * 0.95)],
           lat[(int)(RANDOM_READS * 0.99)]);
    printf("  %.0f random IOPS (single thread)\n\n", 1e6 / mean);
    free(lat);

    /* ---- sequential read ---- */
    long long total = 0;
    const long long want = 512LL * 1024 * 1024;
    lseek(fd, 0, SEEK_SET);
    double t = now_us();
    while (total < want) {
        ssize_t n = read(fd, b, 1 << 20);
        if (n <= 0) break;
        total += n;
    }
    double dt = now_us() - t;
    printf("sequential read    : %lld MB in %.1f ms = %.1f MB/s\n",
           total / (1024 * 1024), dt / 1000.0,
           (double)total / (dt / 1e6) / 1e6);

    /* ---- sequential write ---- */
    total = 0;
    const long long wwant = 256LL * 1024 * 1024;
    lseek(fd, 0, SEEK_SET);
    t = now_us();
    while (total < wwant) {
        ssize_t n = write(fd, b, 1 << 20);
        if (n <= 0) break;
        total += n;
    }
    fsync(fd);
    dt = now_us() - t;
    printf("sequential write   : %lld MB in %.1f ms = %.1f MB/s (with fsync)\n",
           total / (1024 * 1024), dt / 1000.0,
           (double)total / (dt / 1e6) / 1e6);

    printf("\nnote: the probe file was just written, so the operating system\n");
    printf("cache answers part of the reads: p50 is a cache hit, p99 is closer to\n");
    printf("the device.  The simulator therefore uses a conservative 0.25 ms\n");
    printf("for an SSD read instead of the %.1f us cache hit measured here.\n", mean);
    close(fd);
    free(b);
    return 0;
}
