"""Verify that every headline number quoted in the report appears in a log.

Run before building the document:  python build/verify4.py
Exit status 0 means the report's claims are backed by real program output.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, ".."))
LOGS = os.path.join(WORK, "logs")

# (log file, text that must appear, description)
CLAIMS = [
    ("q1_dirsearch.log", "comparisons per look-up : 6009.5", "flat look-up comparisons"),
    ("q1_dirsearch.log", "comparisons per look-up : 10.6", "tree look-up comparisons"),
    ("q1_dirsearch.log", "speed-up of the tree", "flat versus tree speed-up"),
    ("q1_growth.log", "had to be moved   : 8297", "files relocated by growth"),
    ("q1_growth.log", "blocks copied     : 9575619", "blocks copied by relocation"),
    ("q1_growth.log", "(39.22 GB of extra writes)", "bytes rewritten by growth"),
    ("q2_alloc.log", "E (10 blocks) contiguous: start 19", "required program, contiguous placement"),
    ("q2_alloc.log", "AAAAAAeEEEEEEECCCCCEEEEEEEEEEEEE", "required program, final disk map"),
    ("q2_alloc_demo.log", "14 blocks -> FAILED (external fragmentation)", "external fragmentation demo"),
    ("q2_compare.log", "99.90", "worst fit fragmentation"),
    ("q2_compare.log", "20 of the 2000 new files could not be placed", "worst fit placement failures"),
    ("q2_compare.log", "1048576 reads (one per block in the chain)", "linked reads to the last block"),
    ("q2_inode.log", "1074791436 blocks", "inode maximum in blocks"),
    ("q2_inode.log", "4402345721856 bytes", "inode maximum in bytes"),
    ("q2_inode.log", "4.004 TiB", "inode maximum in TiB"),
    ("q2_freespace.log", "134217728 bytes", "bit vector for 4 TB"),
    ("q2_freespace.log", "1638.4 MiB", "linked free list at 40% free"),
    ("q2_freespace.log", "67108864 bytes", "grouping free list"),
    ("q3_meta.log", "4 KB written per update", "write-back write amplification"),
    ("q3_meta.log", "8 KB written per update", "journaled and copy-on-write amplification"),
    ("q3_checksum.log", "0.098% of the data", "CRC-32 storage overhead"),
    ("q3_checksum.log", "-> detected", "a flipped bit is detected"),
    ("q3_inspect.log", "AllocationUnitSize", "real file-system inspection"),
    ("q4_sched.log", "-> 640 cylinders", "FCFS total"),
    ("q4_sched.log", "-> 183 cylinders (+199 for the jump)", "C-SCAN total"),
    ("q4_all.log", "movement 208 cylinders", "LOOK total"),
    ("q4_starve.log", "10002.0 ms", "starvation wait under SSTF"),
    ("q4_sched_sys.log", "SanDisk", "the real disk of this machine"),
    ("q5_cache.log", "4194304 device requests", "one-byte-read device requests"),
    ("q5_replica.log", "99.485%", "availability of one NFS server"),
    ("q6_design.log", "50.0 Gbps", "peak aggregate bitrate"),
    ("q6_sim.log", "221.0", "CDN mean start latency"),
    ("q6_measure.log", "sequential read", "measured storage rates"),
]


def main() -> int:
    failures = []
    for name, needle, description in CLAIMS:
        path = os.path.join(LOGS, name)
        if not os.path.exists(path):
            failures.append(f"{description}: log {name} is missing")
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        if needle not in text:
            failures.append(f"{description}: '{needle}' not found in {name}")

    for f in failures:
        print("FAIL:", f)
    print(f"{len(CLAIMS) - len(failures)}/{len(CLAIMS)} claims verified against the logs")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
