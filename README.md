# CSA0406 - Operating Systems - Assignment 4 (CO4)

**Optimising File Storage and Disk Access**

| | |
|---|---|
| **Student** | Sheshuraaj D |
| **Register number** | 1965260024 |
| **Department** | Computer Science and Engineering (Cyber Security) |
| **Year / semester** | I Year / II Semester |
| **Faculty** | Dr. JAYASAKTHI VELMURUGAN K |
| **Course** | CSA04 - Operating Systems |
| **Assignment** | 4, CO4, 50 marks (K5 - Evaluate) |
| **Repository** | https://github.com/sheshu2909/CSA0406-1965260024-Assignment4 |

Everything in this repository was compiled and executed on the author's machine.
No output in this repository was written by hand: `run_all.sh` produces
`logs/`, and the report reads those logs.

## Compiler, operating system and build

| | |
|---|---|
| **Compiler** | gcc (GCC) 16.2.0 |
| **Platform** | Windows 11 with the MSYS2 (MINGW64) POSIX layer, `MINGW64_NT-10.0-26340` |
| **Shell** | GNU bash 5.3.20 |
| **File system used for the measurements** | NTFS, 4,096-byte allocation unit |
| **Disk** | SanDisk SD8TN8U512G1001 SSD, SATA, 477 GB |

There is no Linux kernel on this machine, so ext4 tools and `/sys/block` are not
available. The report records the real failure of those commands and inspects
the actual NTFS volume and device instead (see Task 3.4 and Task 4.4).

Exact build commands:

```bash
export PATH="/d/FREEBUFF/tools/msys64/usr/bin:$PATH"

# every program, with warnings enabled
for f in src/*.c; do
    gcc -std=c11 -Wall -Wextra -O2 "$f" -o "bin/$(basename "${f%.c}").exe"
done

# the two programs taken from the assignment sheet, built exactly as specified
gcc -std=c11 -Wall -Wextra src/q2_alloc.c -o bin/q2_alloc.exe
gcc -std=c11 -Wall -Wextra src/q4_sched.c -o bin/q4_sched.exe
```

Run everything (writes every log, then removes the temporary data files):

```bash
./run_all.sh
```

## Repository layout

```
Q1_FileSystem_Design/    Source_Code/  Output/  Screenshots/
Q2_Allocation/           Source_Code/  Output/  Screenshots/
Q3_Modern_FileSystems/   Source_Code/  Output/  Screenshots/
Q4_Disk_Scheduling/      Source_Code/  Output/  Screenshots/
Q5_Distributed_Storage/  Source_Code/  Output/  Screenshots/
Q6_Streaming_Design/     Source_Code/  Output/  Screenshots/
Diagrams/                14 figures used in the report
01_Final_Report/         Assignment_4_Final_Report.docx and .pdf
build/                   report, figure, screenshot, verification and packaging scripts
run_all.sh               builds and runs every program into logs/
```

## Programs and how to run them

| Task | Program | Command | What it measures |
|---|---|---|---|
| 1 | `q1_dirsearch.c` | `./bin/q1_dirsearch.exe` | flat directory vs three-level tree look-up |
| 1 | `q1_growth.c` | `./bin/q1_growth.exe` | relocations and bytes copied by contiguous growth |
| 2 | `q2_alloc.c` | `./bin/q2_alloc.exe` | **required program** (TODO 1 filled) |
| 2 | `q2_alloc_demo.c` | `./bin/q2_alloc_demo.exe` | external fragmentation at 14 blocks |
| 2 | `q2_compare.c` | `./bin/q2_compare.exe` | first/best/worst fit and indexed on one workload |
| 2 | `q2_inode.c` | `./bin/q2_inode.exe` | maximum file size for 12+1+1+1 pointers |
| 2 | `q2_freespace.c` | `./bin/q2_freespace.exe` | bit vector, free list and grouping on 4 TB |
| 3 | `q3_meta.c` | `./bin/q3_meta.exe` | write-back vs journaled vs copy-on-write update cost |
| 3 | `q3_checksum.c` | `./bin/q3_checksum.exe` | CRC-32 throughput, overhead and bit-flip detection |
| 3 | `q3_inspect.sh` | `bash src/q3_inspect.sh` | stat, df -i, ls -i, tune2fs (records the failure) |
| 4 | `q4_sched.c` | `./bin/q4_sched.exe` | **required program** (TODO 1 filled) |
| 4 | `q4_all.c` | `./bin/q4_all.exe` | six algorithms, 10,000 requests at three loads |
| 4 | `q4_starve.c` | `./bin/q4_starve.exe` | starvation under SSTF |
| 4 | `q4_sched_sys.sh` | `bash src/q4_sched_sys.sh` | `/sys/block/.../scheduler` (records the failure) and the real disk |
| 5 | `q5_cache.c` | `./bin/q5_cache.exe` | buffering: 1-byte, 4 KB and buffered reads |
| 5 | `q5_replica.c` | `./bin/q5_replica.exe` | one NFS server vs three replicas |
| 6 | `q6_design.c` | `./bin/q6_design.exe` | capacity, throughput and read budget |
| 6 | `q6_measure.c` | `./bin/q6_measure.exe` | storage tier measurements of this machine |
| 6 | `q6_sim.c` | `./bin/q6_sim.exe 250 2500` | two streaming designs over 600,000 requests |

## Results at a glance

- **Task 1:** flat directory 6,009.5 comparisons and 48.16 us per look-up; three-level
  tree 10.6 comparisons and 0.49 us - a 98.3x speed-up. Contiguous growth relocated
  8,297 of 12,000 growth events and rewrote 39.22 GB.
- **Task 2:** the required program reproduces the expected output exactly. Of 21 free
  blocks in two runs (8 and 13), a 14-block request fails contiguously and succeeds
  with indexed allocation. Inode maximum 1,074,791,436 blocks = 4.004 TiB. A 4 TB
  bit vector is 128.0 MiB. Worst fit left 99.90% fragmentation and failed 20 files;
  indexed left 0.00%.
- **Task 3:** journaled and copy-on-write updates each write 8 KB and force two
  flushes, against 4 KB and one flush for write-back. CRC-32 costs 0.098% of the
  space and runs at about 500 MB/s.
- **Task 4:** FCFS 640, SSTF 236, SCAN 236, C-SCAN 183 (+199 jump), LOOK 208,
  C-LOOK 153 (+169 jump) cylinders - all reproduced by the programs. Under heavy
  load FCFS waits 42.21 ms against about 7 ms for the seek-aware algorithms. The
  request at cylinder 183 waits 10,002 ms under SSTF and 2.0 ms under SCAN/C-LOOK.
- **Task 5:** three replicas raise availability from 99.485% to 100.000% for three
  times the storage; asynchronous replication can return old data for 2.1% of
  reads. Buffering turns 0.35 MB/s (one byte per request) into 3,804 MB/s.
- **Task 6:** catalogue 3.2 TB, peak 50 Gbps, 1.6 PB per month. The own-server
  design starts playback in 201.9 ms on campus and 226.9 ms at home; the CDN
  design 221.0 ms in both places. Recommendation: hybrid.

## Verification

```bash
python build/verify4.py     # 33/33 claims verified against the logs
```
