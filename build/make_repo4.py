"""Build the GitHub repository with one commit per task.

Creates work4/github_repo, copies each task's sources, logs, screenshots and
diagrams into its folder, commits it, and finally adds the report and the
build scripts.  The repository is then pushed to the URL in REMOTE.

Run: python build/make_repo4.py [remote-url]
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(WORK, ".."))
REPO = os.path.join(WORK, "github_repo")
DEFAULT_REMOTE = "https://github.com/sheshu2909/CSA0406-1965260024-Assignment4.git"

TASKS = [
    ("Q1_FileSystem_Design", "feat(Q1): flat directory cost and contiguous-growth measurements",
     ["q1_dirsearch.c", "q1_growth.c"],
     ["q1_dirsearch.log", "q1_growth.log"], ["q1_growth.png"],
     ["fig01_flat_vs_tree.png", "fig02_growth_relocation.png"]),
    ("Q2_Allocation", "feat(Q2): allocation policies, inode limit and free-space structures",
     ["q2_alloc.c", "q2_alloc_demo.c", "q2_compare.c", "q2_inode.c", "q2_freespace.c"],
     ["q2_alloc.log", "q2_alloc_demo.log", "q2_compare.log", "q2_inode.log",
      "q2_freespace.log"],
     ["q2_alloc.png", "q2_compare.png", "q2_freespace.png"],
     ["fig03_fragmentation.png", "fig04_reads_last_block.png",
      "fig05_free_space_memory.png"]),
    ("Q3_Modern_FileSystems", "feat(Q3): journaling, copy-on-write, checksums and file-system inspection",
     ["q3_meta.c", "q3_checksum.c", "q3_inspect.sh"],
     ["q3_meta.log", "q3_checksum.log", "q3_inspect.log"],
     ["q3_meta.png", "q3_checksum.png"],
     ["fig06_journal_cow.png", "fig07_checksum_overhead.png"]),
    ("Q4_Disk_Scheduling", "feat(Q4): six scheduling algorithms, simulation, starvation and SSD check",
     ["q4_sched.c", "q4_all.c", "q4_starve.c", "q4_sched_sys.sh"],
     ["q4_sched.log", "q4_all.log", "q4_starve.log", "q4_sched_sys.log"],
     ["q4_sched.png", "q4_all.png"],
     ["fig08_sched_queue.png", "fig09_sched_load.png", "fig10_starvation.png"]),
    ("Q5_Distributed_Storage", "feat(Q5): replication, consistency and device buffering",
     ["q5_cache.c", "q5_replica.c"],
     ["q5_cache.log", "q5_replica.log"],
     ["q5_cache.png", "q5_replica.png"],
     ["fig11_buffering.png", "fig12_replication.png"]),
    ("Q6_Streaming_Design", "feat(Q6): streaming design, calculations and two-design simulation",
     ["q6_design.c", "q6_measure.c", "q6_sim.c"],
     ["q6_design.log", "q6_measure.log", "q6_sim.log"],
     ["q6_sim.png"],
     ["fig13_startup_latency.png", "fig14_monthly_cost.png"]),
]


def git(*args, check=True):
    r = subprocess.run(["git"] + list(args), cwd=REPO, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print(out.splitlines()[-1])
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed")
    return r


def copy(src, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    if os.path.exists(src):
        shutil.copy2(src, dst_dir)
    else:
        print("  missing:", src)


def main():
    remote = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REMOTE

    if os.path.isdir(REPO):
        # Windows marks git objects read-only; clear the attribute and retry.
        def handler(func, path, _exc):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass
        shutil.rmtree(REPO, onerror=handler)
    os.makedirs(REPO)

    with open(os.path.join(REPO, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("bin/\ntmp/\n__pycache__/\n*.pyc\n")

    git("init", "-b", "main")
    git("config", "user.name", "Sheshuraaj D")
    git("config", "user.email", "sheshuraaj@example.com")

    # commit 1: skeleton
    copy(os.path.join(WORK, "README.md"), REPO)
    copy(os.path.join(WORK, "run_all.sh"), REPO)
    os.makedirs(os.path.join(REPO, "build"))
    for name in ("q0_environment.log", "q0_build.log"):
        copy(os.path.join(WORK, "logs", name), os.path.join(REPO, "build"))
    git("add", "-A")
    git("commit", "-m", "chore: repository skeleton, README, run script and environment log")

    # one commit per task
    for folder, message, sources, logs, shots, figs in TASKS:
        base = os.path.join(REPO, folder)
        for sub in ("Source_Code", "Output", "Screenshots", "Diagrams"):
            os.makedirs(os.path.join(base, sub), exist_ok=True)
        for name in sources:
            copy(os.path.join(WORK, "src", name), os.path.join(base, "Source_Code"))
        for name in logs:
            copy(os.path.join(WORK, "logs", name), os.path.join(base, "Output"))
        for name in shots:
            copy(os.path.join(WORK, "shots", name), os.path.join(base, "Screenshots"))
        for name in figs:
            copy(os.path.join(WORK, "diagrams", name), os.path.join(base, "Diagrams"))
        git("add", "-A")
        git("commit", "-m", message)

    # final commit: report and scripts
    os.makedirs(os.path.join(REPO, "01_Final_Report"), exist_ok=True)
    for name in ("Assignment_4_Final_Report.docx", "Assignment_4_Final_Report.pdf"):
        copy(os.path.join(ROOT, name), os.path.join(REPO, "01_Final_Report"))
    for name in os.listdir(os.path.join(WORK, "build")):
        if name.endswith((".py", ".ps1")):
            copy(os.path.join(WORK, "build", name), os.path.join(REPO, "build"))
    git("add", "-A")
    git("commit", "-m",
        "docs: final report (38 pages), diagrams, verification and packaging scripts")

    git("remote", "add", "origin", remote, check=False)
    print("commits:", git("rev-list", "--count", "HEAD").stdout.strip()
          if False else subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=REPO,
                                       capture_output=True, text=True).stdout.strip())
    print("files:", len(subprocess.run(["git", "ls-files"], cwd=REPO,
                                       capture_output=True, text=True).stdout.splitlines()))
    print("pushing ...")
    r = subprocess.run(["git", "-c", "credential.helper=manager", "push", "-u", "origin", "main"],
                       cwd=REPO, capture_output=True, text=True)
    print((r.stdout + r.stderr).strip()[-400:])
    if r.returncode != 0:
        raise SystemExit("push failed")


if __name__ == "__main__":
    main()
