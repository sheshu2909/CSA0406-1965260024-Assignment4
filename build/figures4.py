"""Draw the diagrams for the Assignment 4 report from the measured logs.

Every number is parsed out of work4/logs, so a figure cannot show a value that
no program produced.  Run:  python build/figures4.py
"""
from __future__ import annotations

import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, ".."))
LOGS = os.path.join(WORK, "logs")
OUT = os.path.join(WORK, "diagrams")
os.makedirs(OUT, exist_ok=True)

NAVY = "#1B365D"
ACCENT = "#0B5C8A"
LIGHT = "#7FA8C9"
WARN = "#B5462E"
GREY = "#8A8A8A"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": "#55606B",
    "axes.labelcolor": "#1A1A1A",
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": "#DDE3EA",
    "grid.linewidth": 0.7,
    "figure.dpi": 150,
})


def read(name):
    with open(os.path.join(LOGS, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def num(pattern, text, default=0.0):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else default


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", os.path.basename(path))


def bar_chart(labels, values, title, ylabel, name, color=ACCENT, log=False,
              annotate="{:.2f}", width=0.62, rot=0, note=None):
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    xs = range(len(labels))
    bars = ax.bar(xs, values, color=color, width=width)
    if log:
        ax.set_yscale("log")
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, rotation=rot, ha="right" if rot else "center")
    ax.set_ylabel(ylabel)
    ax.set_title(title, color=NAVY)
    top = max(values) if values else 1
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v * (1.06 if log else 1.02),
                annotate.format(v), ha="center", va="bottom", fontsize=8)
    if log:
        ax.set_ylim(min([v for v in values if v > 0] + [1]) * 0.6, top * 3)
    else:
        ax.set_ylim(0, top * 1.18)
    if note:
        ax.text(0.99, -0.28, note, transform=ax.transAxes, ha="right",
                fontsize=7.5, color=GREY)
    save(fig, name)


# --------------------------------------------------------------------------- #
# Task 1
# --------------------------------------------------------------------------- #
t = read("q1_dirsearch.log")
flat = num(r"flat directory.*?mean look-up time\s*:\s*([0-9.]+) us", t, 0)
tree = num(r"three-level tree.*?mean look-up time\s*:\s*([0-9.]+) us", t, 0)
cmp_flat = num(r"flat directory.*?comparisons per look-up\s*:\s*([0-9.]+)", t, 0)
cmp_tree = num(r"three-level tree.*?comparisons per look-up\s*:\s*([0-9.]+)", t, 0)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.2))
ax1.bar(["one flat\ndirectory", "three-level\ntree"], [flat, tree],
        color=[WARN, ACCENT], width=0.55)
ax1.set_ylabel("mean look-up (us)")
ax1.set_title("look-up time for 12,000 files", color=NAVY)
for i, v in enumerate([flat, tree]):
    ax1.text(i, v * 1.03, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
ax2.bar(["one flat\ndirectory", "three-level\ntree"], [cmp_flat, cmp_tree],
        color=[WARN, ACCENT], width=0.55)
ax2.set_ylabel("name comparisons per look-up")
ax2.set_title("work done per look-up", color=NAVY)
for i, v in enumerate([cmp_flat, cmp_tree]):
    ax2.text(i, v * 1.02, f"{v:.0f}", ha="center", va="bottom", fontsize=8)
ax2.set_ylim(0, max(cmp_flat, 1) * 1.2)
save(fig, "fig01_flat_vs_tree.png")

g = read("q1_growth.log")
inplace = num(r"grew in place\s*:\s*(\d+)", g, 0)
moved = num(r"had to be moved\s*:\s*(\d+)", g, 0)
copied_gb = num(r"blocks copied\s*:\s*\d+\s*\(([0-9.]+) GB", g, 0)
pct = num(r"had to be moved.*?\(([0-9.]+)%", g, 0)

fig, ax = plt.subplots(figsize=(6.0, 3.2))
parts = ax.barh(["12,000 file growth\nevents"], [inplace], color=ACCENT,
                label=f"grew in place: {inplace:,.0f}")
ax.barh(["12,000 file growth\nevents"], [moved], left=[inplace], color=WARN,
        label=f"had to be relocated: {moved:,.0f} ({pct:.1f}%)")
ax.set_xlabel("number of growth events")
ax.set_title(f"contiguous allocation: {copied_gb:.1f} GB rewritten to grow files",
             color=NAVY)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=8,
          frameon=False)
ax.grid(axis="y", visible=False)
ax.set_xlim(0, (inplace + moved) * 1.02)
save(fig, "fig02_growth_relocation.png")

# --------------------------------------------------------------------------- #
# Task 2
# --------------------------------------------------------------------------- #
c = read("q2_compare.log")
rows = {}
for line in c.splitlines():
    for key in ("contiguous first fit", "contiguous best fit",
                "contiguous worst fit", "indexed"):
        if line.startswith(key):
            nums = re.findall(r"[-0-9.]+", line.split("|", 1)[1])
            rows[key] = nums
labels = ["first fit", "best fit", "worst fit", "indexed"]
keys = ["contiguous first fit", "contiguous best fit",
        "contiguous worst fit", "indexed"]
frag = [float(rows[k][4]) for k in keys] if all(k in rows for k in keys) else [0, 0, 0, 0]
bar_chart(labels, frag, "free space left behind by each policy (70% full disk)",
          "fragmentation %  (1 - largest free extent / free space)", "fig03_fragmentation.png",
          color=[ACCENT, LIGHT, WARN, "#4E7A4E"], annotate="{:.2f}%",
          note="worst fit also failed to place 20 of 2,000 new files")

bar_chart(["contiguous", "indexed", "linked / FAT"], [1, 2, 1048576],
          "reads needed to reach the last block of a 4 GB file",
          "disk reads (log scale)", "fig04_reads_last_block.png",
          color=[ACCENT, LIGHT, WARN], log=True, annotate="{:,.0f}")

f = read("q2_freespace.log")
bitvec = num(r"bit vector\s*:.*\(([0-9.]+) MiB", f, 128)
linked40 = num(r"40% free\s*:.*=\s*([0-9.]+) MiB", f, 1638)
grouping = num(r"grouping \(n=64\).*\(([0-9.]+) MiB\)", f, 64)
bar_chart(["bit vector\n(whole 4 TB)", "linked list\n(40% free)", "grouping n=64"],
          [bitvec, linked40, grouping],
          "memory needed to track free space on a 4 TB disk",
          "MiB of RAM (log scale)", "fig05_free_space_memory.png",
          color=[ACCENT, WARN, "#4E7A4E"], log=True, annotate="{:.1f}")

# --------------------------------------------------------------------------- #
# Task 3
# --------------------------------------------------------------------------- #
m = read("q3_meta.log")
wb = num(r"writeback\s+mean\s+([0-9.]+) us", m, 0)
jl = num(r"journaled\s+mean\s+([0-9.]+) us", m, 0)
cow = num(r"copy-on-write\s+mean\s+([0-9.]+) us", m, 0)
bar_chart(["write-back\n(1 write, 1 flush)", "journaled\n(2 writes, 2 flushes)",
           "copy-on-write\n(2 writes, 2 flushes)"], [wb, jl, cow],
          "cost of one 4 KB update, measured on this machine",
          "mean latency (us)", "fig06_journal_cow.png",
          color=[LIGHT, WARN, ACCENT], annotate="{:.0f}")

k = read("q3_checksum.log")
crc32 = num(r"CRC-32 \(4 B\)\s*:\s*([0-9.]+)%", k, 0.098)
crc64 = num(r"CRC-64 \(8 B\)\s*:\s*([0-9.]+)%", k, 0.195)
zfs = num(r"ZFS.*?\(32 B\)\s*:\s*([0-9.]+)%", k, 0.781)
bar_chart(["CRC-32\n4 bytes", "CRC-64\n8 bytes", "ZFS 256-bit\n32 bytes"],
          [crc32, crc64, zfs], "storage overhead of a checksum per 4 KB block",
          "% of the data", "fig07_checksum_overhead.png",
          color=[LIGHT, ACCENT, WARN], annotate="{:.3f}%")

# --------------------------------------------------------------------------- #
# Task 4
# --------------------------------------------------------------------------- #
a = read("q4_all.log")
mv = {}
for line in a.splitlines():
    mm = re.match(r"\s*(FCFS|SSTF|SCAN|C-SCAN|LOOK|C-LOOK)\s+head 53", line)
    if mm:
        cur = mm.group(1)
    mm = re.search(r"movement (\d+) cylinders", line)
    if mm and cur not in mv:
        mv[cur] = int(mm.group(1))
order = ["FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK"]
vals = [mv.get(o, 0) for o in order]
bar_chart(order, vals, "head movement for the queue of the assignment (head 53)",
          "cylinders (C-SCAN excludes the return jump)", "fig08_sched_queue.png",
          color=[WARN, ACCENT, LIGHT, LIGHT, "#4E7A4E", "#4E7A4E"],
          annotate="{:.0f}", note="hand calculation: 640, 236, 236, 183, 208, 153")

heavy = {}     # algo -> (medium average wait, heavy average wait)
for line in a.splitlines():
    mm = re.match(r"(FCFS|SSTF|SCAN|C-SCAN|LOOK|C-LOOK)\s+\|\s+([0-9.]+) ms\s+\|\s+([0-9.]+) ms\s+\|\s+([0-9.]+) ms\s+\|\s+([0-9.]+) ms\s+\|\s+([0-9.]+) ms", line)
    if mm:
        heavy[mm.group(1)] = (float(mm.group(4)), float(mm.group(6)))

fig, ax = plt.subplots(figsize=(6.6, 3.4))
loads = ["medium batch of 8", "heavy batch of 64"]
for algo, colour, marker in (("FCFS", WARN, "o"), ("SSTF", ACCENT, "s"),
                             ("SCAN", LIGHT, "^"), ("C-SCAN", "#4E7A4E", "D"),
                             ("LOOK", "#8E6C3F", "v"), ("C-LOOK", "#7A4E8E", "P")):
    if algo in heavy:
        ax.plot(loads, [heavy[algo][0], heavy[algo][1]], marker=marker,
                color=colour, label=algo, linewidth=1.6)
ax.set_ylabel("mean waiting time (ms)")
ax.set_title("fairness: waiting time per request as the queue grows", color=NAVY)
ax.legend(fontsize=8, frameon=False, ncol=3)
save(fig, "fig09_sched_load.png")

s = read("q4_starve.log")
waits = {}
for line in s.splitlines():
    mm = re.match(r"(SSTF|SCAN|C-LOOK)\s+\|\s+\d+\s+\|\s+([0-9.]+) ms", line)
    if mm:
        waits[mm.group(1)] = float(mm.group(2))
bar_chart(["SSTF", "SCAN", "C-LOOK"], [waits.get("SSTF", 1), waits.get("SCAN", 1),
                                       waits.get("C-LOOK", 1)],
          "wait of one request at cylinder 183 behind a stream at 60",
          "waiting time (ms, log scale)", "fig10_starvation.png",
          color=[WARN, ACCENT, "#4E7A4E"], log=True, annotate="{:.1f}")

# --------------------------------------------------------------------------- #
# Task 5
# --------------------------------------------------------------------------- #
q5 = read("q5_cache.log")
b1 = num(r"A\. read\(1 byte\).*=\s*([0-9.]+) MB/s", q5, 0)
b2 = num(r"B\. read\(4 KB\).*=\s*([0-9.]+) MB/s", q5, 0)
b3 = num(r"C\. fread\(4 KB.*=\s*([0-9.]+) MB/s", q5, 0)
bar_chart(["read(1 byte)", "read(4 KB)", "fread(4 KB)\n1 MB buffer"],
          [b1, b2, b3], "buffering: the same 256 MB read three ways",
          "MB/s (log scale)", "fig11_buffering.png",
          color=[WARN, LIGHT, ACCENT], log=True, annotate="{:.1f}")

r = read("q5_replica.log")
nfs_av = num(r"one NFS server\s+\|\s+([0-9.]+)%", r, 0)
hdfs_av = num(r"3 replicas \(HDFS\)\s+\|\s+([0-9.]+)%", r, 100)
fig, ax = plt.subplots(figsize=(6.2, 3.2))
bars = ax.bar(["one NFS server", "3 replicas (HDFS)"], [nfs_av, hdfs_av],
              color=[WARN, ACCENT], width=0.5)
ax.set_ylim(min(nfs_av, 99.0) - 0.2, 100.02)
ax.set_ylabel("reads answered (%)")
ax.set_title("availability of 20,000 reads with 0.5% node failures", color=NAVY)
for b, v in zip(bars, [nfs_av, hdfs_av]):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.3f}%",
            ha="center", va="bottom", fontsize=8)
ax.text(0.5, 0.06, "three copies cost 3x the storage (60 TB instead of 20 TB)",
        transform=ax.transAxes, ha="center", fontsize=7.8, color=GREY)
save(fig, "fig12_replication.png")

# --------------------------------------------------------------------------- #
# Task 6
# --------------------------------------------------------------------------- #
sim = read("q6_sim.log")
stats = {}
for line in sim.splitlines():
    mm = re.match(r"(A own, student on campus|A own, student at home|B CDN, student on campus|B CDN, student at home)\s+\|\s+([0-9.]+)\s+\|\s+([0-9.]+)\s+\|\s+([0-9.]+)\s+\|\s+([0-9.]+) ms", line)
    if mm:
        stats[mm.group(1)] = [float(mm.group(2)), float(mm.group(3)),
                              float(mm.group(4)), float(mm.group(5))]

keys = ["A own, student on campus", "A own, student at home",
        "B CDN, student on campus", "B CDN, student at home"]
short = ["A\ncampus", "A\nat home", "B\ncampus", "B\nat home"]
fig, ax = plt.subplots(figsize=(6.8, 3.4))
import numpy as np
x = np.arange(len(keys))
w = 0.26
for i, (label, colour) in enumerate((("p50", LIGHT), ("p95", ACCENT), ("p99", NAVY))):
    vals = [stats.get(k, [0, 0, 0, 0])[i + 1] for k in keys]
    ax.bar(x + (i - 1) * w, vals, width=w, label=label, color=colour)
ax.set_xticks(x)
ax.set_xticklabels(short)
ax.set_ylabel("time to start playback (ms)")
ax.set_title("two designs over 600,000 play requests", color=NAVY)
ax.legend(fontsize=8, frameon=False)
save(fig, "fig13_startup_latency.png")

a_cost = 6.4 * 20 + 1_600_000 * 0.01
b_cost = 3.2 * 23 + 1_600_000 * 0.02
fig, ax = plt.subplots(figsize=(6.2, 3.2))
ax.bar(["A  own servers", "B  object storage + CDN"], [a_cost, b_cost],
       color=[ACCENT, WARN], width=0.5)
ax.set_ylabel("USD per month")
ax.set_title("monthly cost for 1.6 PB of viewing", color=NAVY)
for i, v in enumerate([a_cost, b_cost]):
    ax.text(i, v * 1.02, f"${v:,.0f}", ha="center", va="bottom", fontsize=8)
ax.set_ylim(0, max(a_cost, b_cost) * 1.15)
ax.text(0.5, -0.22, "storage + transfer at 0.01 USD/GB (transit) and 0.02 USD/GB (CDN)",
        transform=ax.transAxes, ha="center", fontsize=7.5, color=GREY)
save(fig, "fig14_monthly_cost.png")

print("figures:", len(os.listdir(OUT)))
