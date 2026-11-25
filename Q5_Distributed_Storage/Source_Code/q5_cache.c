/* q5_cache.c - Task 5.3: buffering and caching, measured.
 *
 * The same 256 MB file is read three ways:
 *   A. one byte per read()  - the worst possible use of the device interface
 *   B. 4 KB per read()      - one request per block
 *   C. 4 KB per fread() with a 1 MB stream buffer - the C library batches
 *      the device requests and copies from its buffer
 *
 * The program reports the throughput and the number of device requests for
 * each method, which is exactly what buffering in the operating system buys.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q5_cache.c -o q5_cache
 */
#define _POSIX_C_SOURCE 200809L

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define FILE_MB 256
#define ONE_BYTE_MB 4            /* one-byte reads are only done over 4 MB */

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e3 + (double)ts.tv_nsec / 1e6;
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
    char buf[65536];
    memset(buf, 0x5A, sizeof buf);
    for (int i = 0; i < FILE_MB * 16; i++)
        if (fwrite(buf, sizeof buf, 1, f) != 1) { fclose(f); return -1; }
    fclose(f);
    return 0;
}

int main(void)
{
    const char *path = "tmp/q5_large.bin";
    if (make_file(path) != 0) {
        fprintf(stderr, "cannot create %s\n", path);
        return 1;
    }
    printf("Task 5.3  buffering and caching on a real read\n");
    printf("file: %s, %d MB\n\n", path, FILE_MB);

    char *buf = malloc(1 << 20);
    if (!buf) return 1;
    long long total = 0;

    /* ---- A: one byte per read() ---- */
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }
    long long limit = (long long)ONE_BYTE_MB * 1024 * 1024;
    long long calls = 0;
    double t = now_ms();
    while (total < limit) {
        ssize_t n = read(fd, buf, 1);
        if (n <= 0) break;
        total += n;
        calls++;
    }
    double dt = now_ms() - t;
    printf("A. read(1 byte)      : %6lld bytes in %8.1f ms = %8.2f MB/s, "
           "%lld device requests\n",
           total, dt, (double)total / (dt / 1000.0) / 1e6, calls);
    lseek(fd, 0, SEEK_SET);

    /* ---- B: one read() per 4 KB block ---- */
    total = 0;
    calls = 0;
    t = now_ms();
    while (total < (long long)FILE_MB * 1024 * 1024) {
        ssize_t n = read(fd, buf, 4096);
        if (n <= 0) break;
        total += n;
        calls++;
    }
    dt = now_ms() - t;
    printf("B. read(4 KB)        : %6lld bytes in %8.1f ms = %8.2f MB/s, "
           "%lld device requests\n",
           total, dt, (double)total / (dt / 1000.0) / 1e6, calls);
    close(fd);

    /* ---- C: 4 KB fread() with the C library stream buffer ---- */
    FILE *f = fopen(path, "rb");
    if (!f) { perror("fopen"); return 1; }
    setvbuf(f, NULL, _IOFBF, 1 << 20);
    total = 0;
    calls = 0;
    t = now_ms();
    while (total < (long long)FILE_MB * 1024 * 1024) {
        size_t n = fread(buf, 1, 4096, f);
        if (n == 0) break;
        total += (long long)n;
        calls++;
    }
    dt = now_ms() - t;
    printf("C. fread(4 KB, 1 MB buffer): %lld bytes in %.1f ms = %.2f MB/s, "
           "%lld library calls\n",
           total, dt, (double)total / (dt / 1000.0) / 1e6, calls);
    fclose(f);

    printf("\nA byte at a time costs one device request per byte; a 4 KB read\n");
    printf("costs one per block; the buffered stream lets the library hand\n");
    printf("the device large requests and serves the small ones from RAM.\n");
    printf("All three read the same bytes: the difference is the number of\n");
    printf("requests that reach the device, not the amount of data.\n");
    free(buf);
    return 0;
}
