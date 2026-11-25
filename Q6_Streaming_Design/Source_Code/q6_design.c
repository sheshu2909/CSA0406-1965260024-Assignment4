/* q6_design.c - Task 6, stage 4: the capacity, throughput and read budget.
 *
 * Every number is produced from the assumptions printed at the top, so the
 * design can be re-checked with different values.  The assumptions are the
 * ones given by the start-up: 200,000 students, 4,000 lectures of 300 MB to
 * 2 GB (800 MB mean, 90 minutes), streamed at 5 Mbps, read once but played
 * many times, and a viewer may jump to any minute.
 *
 * Build: gcc -std=c11 -Wall -Wextra q6_design.c -o q6_design
 */
#include <stdio.h>

#define STUDENTS 200000
#define VIDEOS 4000
#define MEAN_MB 800.0
#define MINUTES 90.0
#define BITRATE_MBPS 5.0
#define CONCURRENT_PCT 5.0
#define SEGMENT_MB 4.0
#define VIEWS_PER_STUDENT 10.0
#define BLOCK_KB 4.0

int main(void)
{
    printf("Task 6, stage 4  design and calculations\n\n");
    printf("assumptions\n");
    printf("  students              : %d\n", STUDENTS);
    printf("  lectures              : %d, mean %.0f MB, %.0f minutes\n",
           VIDEOS, MEAN_MB, MINUTES);
    printf("  streaming bitrate     : %.0f Mbps\n", BITRATE_MBPS);
    printf("  peak concurrent share : %.0f%% of the students\n", CONCURRENT_PCT);
    printf("  segment for seeking   : %.0f MB\n\n", SEGMENT_MB);

    double catalog_gb = VIDEOS * MEAN_MB / 1000.0;
    double mb_per_min = MEAN_MB / MINUTES;
    double seg_per_min = mb_per_min / SEGMENT_MB;
    double peak_streams = STUDENTS * CONCURRENT_PCT / 100.0;
    double peak_gbps = peak_streams * BITRATE_MBPS / 1000.0;
    double egress_gb = STUDENTS * VIEWS_PER_STUDENT * MEAN_MB / 1000.0;

    printf("capacity\n");
    printf("  catalogue             : %.0f GB = %.1f TB\n", catalog_gb, catalog_gb / 1000.0);
    printf("  with two copies       : %.1f TB\n", catalog_gb * 2 / 1000.0);
    printf("  one lecture per minute: %.2f MB\n", mb_per_min);
    printf("  segments per minute   : %.2f of %.0f MB\n\n", seg_per_min, SEGMENT_MB);

    printf("reads to start playback at an arbitrary minute\n");
    printf("  contiguous allocation : 1 read (one seek to the segment)\n");
    printf("  indexed allocation    : 2 reads (the index block, then the segment)\n");
    printf("  linked allocation     : %.0f reads (walk %.0f MB of %.0f KB blocks)\n",
           SEGMENT_MB * 1024 / BLOCK_KB, SEGMENT_MB, BLOCK_KB);
    printf("  the index entry for a %.0f MB segment needs %.0f pointers of 4 bytes\n",
           SEGMENT_MB, SEGMENT_MB * 1024 / BLOCK_KB);
    printf("  with one index block per %.0f MB, the whole 2 GB lecture needs\n",
           SEGMENT_MB);
    printf("  %d segments and %d index blocks: %.0f KB of metadata per lecture\n\n",
           (int)(2 * 1024 / SEGMENT_MB), (int)(2 * 1024 / SEGMENT_MB),
           (2 * 1024 / SEGMENT_MB) * 4.0);

    printf("throughput at the peak\n");
    printf("  concurrent streams    : %.0f\n", peak_streams);
    printf("  aggregate bitrate     : %.1f Gbps\n", peak_gbps);
    printf("  two 10 Gbps server NICs would carry %.0f Gbps, so the peak\n", 20.0);
    printf("  cannot be served from one site: a CDN is required, or the peak\n");
    printf("  must be spread over many servers.\n\n");

    printf("transfer per month\n");
    printf("  %.0f views x %.0f MB = %.0f GB = %.2f PB\n",
           STUDENTS * VIEWS_PER_STUDENT, MEAN_MB, egress_gb, egress_gb / 1e6);
    printf("  at 0.02 USD per GB through a CDN: %.0f USD per month\n\n",
           egress_gb * 0.02);

    printf("capacity check for the chosen allocation\n");
    printf("  one %.0f MB segment as %.0f KB blocks = %.0f blocks\n",
           SEGMENT_MB, BLOCK_KB, SEGMENT_MB * 1024 / BLOCK_KB);
    printf("  a 4 KB index block holds %d pointers, so one index block\n", 4096 / 4);
    printf("  covers %d blocks = %.0f MB, exactly one %.0f MB segment.\n",
           1024, 1024 * BLOCK_KB / 1024, SEGMENT_MB);
    printf("  The inode's single-indirect block holds the addresses of those\n");
    printf("  segment index blocks: two levels of index for any minute.\n");
    return 0;
}
