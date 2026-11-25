/* q3_checksum.c - Task 3.1: what checksums cost and what they detect.
 *
 * A software CRC-32 is computed over buffers of 4 KB (one block) and 128 KB
 * (one ZFS record), and the throughput is measured.  The storage overhead of
 * keeping a checksum per block is then calculated, and one flipped bit is used
 * to show that the check actually fires.
 *
 * Build: gcc -std=c11 -Wall -Wextra -O2 q3_checksum.c -o q3_checksum
 */
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static unsigned int table[256];
static double now_ms(void);

static void build_table(void)
{
    for (unsigned int i = 0; i < 256; i++) {
        unsigned int c = i;
        for (int k = 0; k < 8; k++)
            c = (c & 1u) ? 0xEDB88320u ^ (c >> 1) : c >> 1;
        table[i] = c;
    }
}

static unsigned int crc32(const unsigned char *p, size_t n)
{
    unsigned int c = 0xFFFFFFFFu;
    for (size_t i = 0; i < n; i++)
        c = table[(c ^ p[i]) & 0xFF] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}

int main(void)
{
    build_table();

    const size_t small = 4096, big = 128 * 1024;
    unsigned char *a = malloc(small), *b = malloc(big);
    if (!a || !b) return 1;
    for (size_t i = 0; i < small; i++) a[i] = (unsigned char)(i * 7 + 3);
    for (size_t i = 0; i < big; i++) b[i] = (unsigned char)(i * 13 + 5);

    printf("Task 3.1  checksum cost and overhead\n\n");

    /* warm up, then measure 200 MB through each block size */
    unsigned int sink = crc32(a, small) ^ crc32(b, big);
    const size_t total = 200ULL * 1024 * 1024;
    const char *label[2] = { "4 KB block", "128 KB record" };
    unsigned char *buf[2] = { a, b };
    size_t len[2] = { small, big };

    for (int k = 0; k < 2; k++) {
        size_t blocks = total / len[k];
        double t = now_ms();
        for (size_t i = 0; i < blocks; i++)
            sink ^= crc32(buf[k], len[k]);
        double dt = now_ms() - t;
        double mb = (double)blocks * (double)len[k] / (1024.0 * 1024.0);
        printf("  %-13s : %zu checksums over %.0f MiB in %.1f ms = %.0f MB/s "
               "(%.1f ns per block)\n",
               label[k], blocks, mb, dt, mb / (dt / 1000.0),
               dt * 1e6 / (double)blocks);
    }
    printf("  (checksum of the test data: %08X)\n\n", sink);

    printf("storage overhead of one checksum per 4 KB block\n");
    struct { const char *name; double bytes; } kinds[] = {
        { "CRC-32 (4 B)", 4 },
        { "CRC-64 (8 B)", 8 },
        { "ZFS fletcher/256-bit (32 B)", 32 },
    };
    for (int i = 0; i < 3; i++) {
        double pct = 100.0 * kinds[i].bytes / 4096.0;
        printf("  %-30s : %.3f%% of the data, %.1f GB on a 4 TB disk\n",
               kinds[i].name, pct, kinds[i].bytes / 4096.0 * 4000.0);
    }

    /* detection: flip one bit and check that the checksum changes */
    unsigned int before = crc32(a, small);
    a[1000] ^= 0x01;
    unsigned int after = crc32(a, small);
    printf("\n  one flipped bit: before %08X, after %08X -> %s\n",
           before, after, before != after ? "detected" : "MISSED");

    /* a second corruption that keeps the same parity is still detected,
     * which is what a checksum buys over a parity bit */
    a[2000] ^= 0x80;
    unsigned int third = crc32(a, small);
    printf("  a second flipped bit: %08X -> %s\n", third,
           third != after ? "detected" : "MISSED");

    free(a);
    free(b);
    return 0;
}

#include <time.h>

static double now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e3 + (double)ts.tv_nsec / 1e6;
}
