"""Assemble the Assignment 4 submission folder and ZIP.

One folder per task with source, output logs and screenshots, plus the report,
the diagrams and the build scripts.  Run: python build/package4.py
"""
from __future__ import annotations

import os
import shutil
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(WORK, ".."))
PKG = os.path.join(ROOT, "CSA0406_Assignment4_Submission")
ZIP = os.path.join(ROOT, "CSA0406_Assignment4_Complete_Submission.zip")

TASKS = {
    "Q1_FileSystem_Design": {
        "src": ["q1_dirsearch.c", "q1_growth.c"],
        "logs": ["q1_dirsearch.log", "q1_growth.log"],
        "shots": ["q1_growth.png"],
        "figs": ["fig01_flat_vs_tree.png", "fig02_growth_relocation.png"],
    },
    "Q2_Allocation": {
        "src": ["q2_alloc.c", "q2_alloc_demo.c", "q2_compare.c", "q2_inode.c",
                "q2_freespace.c"],
        "logs": ["q2_alloc.log", "q2_alloc_demo.log", "q2_compare.log",
                 "q2_inode.log", "q2_freespace.log"],
        "shots": ["q2_alloc.png", "q2_compare.png", "q2_freespace.png"],
        "figs": ["fig03_fragmentation.png", "fig04_reads_last_block.png",
                 "fig05_free_space_memory.png"],
    },
    "Q3_Modern_FileSystems": {
        "src": ["q3_meta.c", "q3_checksum.c", "q3_inspect.sh"],
        "logs": ["q3_meta.log", "q3_checksum.log", "q3_inspect.log"],
        "shots": ["q3_meta.png", "q3_checksum.png"],
        "figs": ["fig06_journal_cow.png", "fig07_checksum_overhead.png"],
    },
    "Q4_Disk_Scheduling": {
        "src": ["q4_sched.c", "q4_all.c", "q4_starve.c", "q4_sched_sys.sh"],
        "logs": ["q4_sched.log", "q4_all.log", "q4_starve.log", "q4_sched_sys.log"],
        "shots": ["q4_sched.png", "q4_all.png"],
        "figs": ["fig08_sched_queue.png", "fig09_sched_load.png",
                 "fig10_starvation.png"],
    },
    "Q5_Distributed_Storage": {
        "src": ["q5_cache.c", "q5_replica.c"],
        "logs": ["q5_cache.log", "q5_replica.log"],
        "shots": ["q5_cache.png", "q5_replica.png"],
        "figs": ["fig11_buffering.png", "fig12_replication.png"],
    },
    "Q6_Streaming_Design": {
        "src": ["q6_design.c", "q6_measure.c", "q6_sim.c"],
        "logs": ["q6_design.log", "q6_measure.log", "q6_sim.log"],
        "shots": ["q6_sim.png"],
        "figs": ["fig13_startup_latency.png", "fig14_monthly_cost.png"],
    },
}


def put(src, dst):
    if os.path.exists(src):
        shutil.copy2(src, dst)
    else:
        print("  missing:", src)


def main():
    if os.path.isdir(PKG):
        shutil.rmtree(PKG)
    os.makedirs(PKG)

    for task, spec in TASKS.items():
        for sub in ("Source_Code", "Output", "Screenshots", "Diagrams"):
            os.makedirs(os.path.join(PKG, task, sub))
        for name in spec["src"]:
            put(os.path.join(WORK, "src", name), os.path.join(PKG, task, "Source_Code"))
        for name in spec["logs"]:
            put(os.path.join(WORK, "logs", name), os.path.join(PKG, task, "Output"))
        for name in spec["shots"]:
            put(os.path.join(WORK, "shots", name), os.path.join(PKG, task, "Screenshots"))
        for name in spec["figs"]:
            put(os.path.join(WORK, "diagrams", name), os.path.join(PKG, task, "Diagrams"))

    os.makedirs(os.path.join(PKG, "01_Final_Report"))
    for name in ("Assignment_4_Final_Report.docx", "Assignment_4_Final_Report.pdf"):
        put(os.path.join(ROOT, name), os.path.join(PKG, "01_Final_Report"))

    os.makedirs(os.path.join(PKG, "build"))
    for name in os.listdir(os.path.join(WORK, "build")):
        if name.endswith((".py", ".ps1")):
            put(os.path.join(WORK, "build", name), os.path.join(PKG, "build"))

    put(os.path.join(WORK, "run_all.sh"), PKG)
    put(os.path.join(WORK, "README.md"), PKG)
    put(os.path.join(WORK, "logs", "q0_environment.log"), os.path.join(PKG, "build"))
    put(os.path.join(WORK, "logs", "q0_build.log"), os.path.join(PKG, "build"))

    with open(os.path.join(PKG, "Submission_Checklist.txt"), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(
            "CSA0406 Operating Systems - Assignment 4 (CO4)\n"
            "Sheshuraaj D, 1965260024\n\n"
            "Repository : https://github.com/sheshu2909/CSA0406-1965260024-Assignment4\n"
            "Compiler   : gcc 16.2.0, -std=c11 -Wall -Wextra\n"
            "Platform   : Windows 11 + MSYS2 (POSIX layer), NTFS, SanDisk SATA SSD\n\n"
            "Contents\n"
            "  Q1..Q6          Source_Code, Output (logs), Screenshots, Diagrams\n"
            "  01_Final_Report  Assignment_4_Final_Report.docx and .pdf\n"
            "  build            report, figure, screenshot, verification, packaging scripts\n"
            "  run_all.sh       rebuilds and re-runs every program\n"
            "  README.md        student details, build commands, per-task results\n\n"
            "Verification\n"
            "  python build/verify4.py    -> 33/33 claims verified against the logs\n\n"
            "Both 'Complete the Code' programs are included with the TODO filled:\n"
            "  Q2_Allocation/Source_Code/q2_alloc.c   (first-fit contiguous allocation)\n"
            "  Q4_Disk_Scheduling/Source_Code/q4_sched.c  (SSTF)\n"
        )

    count = 0
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(PKG):
            for name in files:
                full = os.path.join(base, name)
                rel = os.path.relpath(full, PKG)
                z.write(full, os.path.join(os.path.basename(PKG), rel))
                count += 1

    print(f"{count} files -> {ZIP} ({os.path.getsize(ZIP) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
