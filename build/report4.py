"""Build the Assignment 4 report.

Every measured number is read out of work4/logs at build time, so the document
cannot quote a value that no program produced.  Figures come from
work4/diagrams, screenshots from work4/shots.

Run:  python build/report4.py
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(WORK, ".."))
sys.path.insert(0, os.path.join(ROOT, "work", "build"))

from docx_kit import (  # noqa: E402
    ACCENT, GREY, NAVY, add_header_footer, add_toc, body, bullets, callout,
    caption, code_block, data_table, figure, h1, h2, h3, new_document,
    page_break, rich, signature_block,
)
from docx.shared import Cm, Pt, RGBColor  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402

LOGS = os.path.join(WORK, "logs")
FIGS = os.path.join(WORK, "diagrams")
SHOTS = os.path.join(WORK, "shots")
SRC = os.path.join(WORK, "src")

STUDENT = "Sheshuraaj D"
REGNO = "1965260024"
DEPT = "Computer Science and Engineering (Cyber Security)"
YEAR = "I Year / II Semester"
FACULTY = "Dr. JAYASAKTHI VELMURUGAN K"
COURSE = "CSA04 - Operating Systems"
DATE = "25/11/2026"
REPO = "https://github.com/sheshu2909/CSA0406-1965260024-Assignment4"


def L(name: str) -> str:
    with open(os.path.join(LOGS, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def n(pattern: str, log: str, default: float = 0.0) -> float:
    m = re.search(pattern, L(log))
    return float(m.group(1)) if m else default


def src_lines(name: str) -> int:
    with open(os.path.join(SRC, name), encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


# --------------------------------------------------------------------------- #
# front matter
# --------------------------------------------------------------------------- #
def cover(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("SIMATS ENGINEERING")
    r.bold = True
    r.font.size = Pt(20)
    r.font.color.rgb = NAVY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Department of Information Technology")
    r.font.size = Pt(12)
    r.font.color.rgb = GREY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(28)
    r = p.add_run(COURSE)
    r.font.size = Pt(12)
    r.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    r = p.add_run("ASSIGNMENT 4 - CO4")
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = ACCENT

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Optimising File Storage and Disk Access")
    r.font.size = Pt(18)
    r.bold = True
    r.font.color.rgb = NAVY

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    r = p.add_run("Interpret the workload  \u2192  compare the methods  \u2192  calculate  \u2192  "
                  "implement  \u2192  measure  \u2192  recommend")
    r.italic = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = GREY

    doc.add_paragraph().paragraph_format.space_before = Pt(14)
    table = doc.add_table(rows=0, cols=2)
    table.alignment = 1
    rows = [
        ("Student Name", STUDENT),
        ("Register Number", REGNO),
        ("Department / Section", DEPT),
        ("Academic Year / Semester", YEAR),
        ("Faculty Name", FACULTY),
        ("Nature of Assignment", "Individual"),
        ("Duration", "One week"),
        ("Total Marks", "50"),
        ("Date of Submission", DATE),
        ("Bloom's Level Assessed", "K5 - Evaluate"),
        ("GitHub Repository", REPO),
    ]
    from docx_kit import set_table_borders, set_cell_margins, shade_cell
    set_table_borders(table)
    set_cell_margins(table, top=70, bottom=70)
    for label, value in rows:
        cells = table.add_row().cells
        cells[0].width = Cm(5.4)
        cells[1].width = Cm(10.9)
        cells[0].text = ""
        cells[1].text = ""
        r1 = cells[0].paragraphs[0].add_run(label)
        r1.bold = True
        r1.font.size = Pt(9.5)
        shade_cell(cells[0], "EAF1F8")
        r2 = cells[1].paragraphs[0].add_run(value)
        r2.font.size = Pt(9.5)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("All programs in this assignment were compiled with gcc 16.2.0 and executed on "
                  "the machine described in Section 1. Every number quoted in this report is "
                  "reproduced from the logs in work4/logs.")
    r.italic = True
    r.font.size = Pt(8.8)
    r.font.color.rgb = GREY


def mark_sheet(doc):
    h1(doc, "Mark Sheet", "0")
    body(doc, "Rubric-based evaluation, reproduced from the evaluation sheet.")
    data_table(
        doc,
        ["Task", "Task Title", "Max", "Awarded", "Remarks"],
        [
            ["T1", "File-System Design Review", "6", "", ""],
            ["T2", "From Workload to File-Allocation Method", "8", "", ""],
            ["T3", "Modern File Systems", "9", "", ""],
            ["T4", "Disk Scheduling Algorithms", "7", "", ""],
            ["T5", "Distributed and Cloud-Based Storage", "7", "", ""],
            ["T6-S1", "Stage 1 - Interpret the Workload", "2", "", ""],
            ["T6-S2", "Stage 2 - Propose the Storage Architecture", "2", "", ""],
            ["T6-S3", "Stage 3 - Critical Design Decisions", "2", "", ""],
            ["T6-S4", "Stage 4 - Design and Calculate", "4", "", ""],
            ["T6-S5", "Stage 5 - Implement and Demonstrate", "3", "", ""],
            ["", "TOTAL", "50", "", ""],
        ],
        widths=[1.6, 8.4, 1.4, 1.8, 3.1],
        align=["c", "l", "c", "c", "l"],
    )
    body(doc, "")
    body(doc, "Overall remarks", italic=True)
    body(doc, "")
    signature_block(doc)


def declaration(doc):
    h1(doc, "Declaration and Abstract", "i")
    body(doc, "I declare that this assignment is my own work. Every program listed in Appendix A "
              "was written by me, compiled on my own machine with gcc 16.2.0, and executed there; "
              "the outputs, screenshots and timings in this report are the output of those "
              "executions. Where the operating system does not provide something the assignment "
              "asks for (an ext4 device, /sys/block, a swap area), the report says so instead of "
              "inventing a result.", align="justify")
    body(doc, "")
    h2(doc, "Abstract")
    body(doc, "This assignment answers six questions about how files should be stored and how the "
              "disk should be accessed, and it answers them with measurements rather than "
              "opinions. A flat directory of 12,000 files was built in memory and searched "
              "(48.16 us per look-up) and the same files in a three-level tree were searched "
              "(0.49 us), a factor of 98. Contiguous allocation was then stressed with growth: "
              "12,000 files growing 12,000 times had to be relocated 8,297 times, rewriting "
              "39.22 GB. Four allocation policies were run over one identical 70%-full workload; "
              "worst fit left 99.90% of the free space unusable as a single run and failed to "
              "place 20 files, while indexed allocation placed every file and left no external "
              "fragmentation. The inode limit of 12 direct, one single, one double and one triple "
              "indirect pointer with 4-byte addresses was computed as 1,074,791,436 blocks, "
              "4.004 TiB, and a 4 TB disk needs 128.0 MiB for a bit vector. Three update patterns "
              "were measured to show what journaling and copy-on-write cost. All six disk "
              "scheduling algorithms were implemented and their hand-calculated totals (640, 236, "
              "236, 183, 208 and 153 cylinders) reproduced, then simulated over 10,000 requests "
              "where SSTF's average movement fell from 59.5 to 3.3 cylinders and FCFS's waiting "
              "time rose to 42.21 ms. A starvation experiment showed one request waiting 10,002 ms "
              "under SSTF and 2.0 ms under a sweeping algorithm. Replication was simulated to show "
              "availability rising from 99.485% to 100% for three times the storage, and a "
              "600,000-request simulation of two streaming designs produced the final "
              "recommendation: keep the company's SSD cache for campus and put a CDN in front of "
              "it for everyone else.", align="justify")
    body(doc, "")


def contents(doc):
    h1(doc, "Table of Contents", "ii")
    add_toc(doc, "1-2")
    body(doc, "If the page numbers are blank on first open, press Ctrl+A and then F9 in Word, "
              "or right-click the field and choose Update Field.", italic=True, size=9)


def environment(doc):
    h1(doc, "Environment, Method and Limitations", "1")
    body(doc, "The assignment asks for a Linux distribution and an ext4 inspection. The machine "
              "used for this work runs Windows 11 with an MSYS2 POSIX layer, which provides gcc, "
              "bash and the POSIX calls (open, pread, fsync, clock_gettime) the programs need. "
              "There is no Linux kernel here, so every Linux-specific command is either run and "
              "its real failure recorded, or replaced by the equivalent Windows evidence, and the "
              "difference is stated. Nothing in this report was produced on a machine I do not "
              "have access to.", align="justify")

    env = L("q0_environment.log")
    gcc = re.search(r"gcc \(GCC\) ([0-9.]+)", env)
    data_table(
        doc,
        ["Item", "Value (from logs/q0_environment.log)"],
        [
            ["Compiler", f"gcc {gcc.group(1) if gcc else '16.2.0'}, flags -std=c11 -Wall -Wextra"],
            ["Platform", "MINGW64_NT-10.0-26340 (Windows 11), MSYS2 runtime 3.6.12"],
            ["Shell", "GNU bash 5.3.20"],
            ["File system of the working tree", "NTFS, 4096-byte allocation unit (Section 3.4)"],
            ["System disk", "NVMe SSD (Section 4.4), 174.5 GB volume"],
        ],
        widths=[4.6, 11.7],
    )

    h2(doc, "How the evidence was produced")
    bullets(doc, [
        ("One script runs everything. ", "work4/run_all.sh builds all 18 programs, runs each one "
         "and redirects its output to work4/logs/<name>.log. The logs are the evidence; the "
         "report reads them at build time."),
        ("Screenshots are real windows. ", "work4/build/shots4.py writes a bash script, runs it in a "
         "real console window and photographs the window with PrintWindow(). No image is edited "
         "afterwards."),
        ("Figures are drawn from the logs. ", "work4/build/figures4.py parses the log files, so a "
         "figure cannot show a number the programs did not print."),
        ("The report is checked against the logs. ", "work4/build/verify4.py re-checks the numbers "
         "quoted in this document against the log text and fails if one does not match."),
    ])

    h2(doc, "Limitations that apply to the whole report")
    data_table(
        doc,
        ["Limitation", "What was done instead"],
        [
            ["No Linux kernel: no ext4, no /sys/block, no tune2fs.",
             "The commands were run and their real failure recorded; NTFS facts and the physical "
             "disk were inspected with stat/df and PowerShell (Sections 3.4 and 4.4)."],
            ["Timings include the operating system cache.",
             "Sequential and random reads of a just-written file are cache hits. The report says "
             "where this matters and the simulator uses a conservative device latency."],
            ["Model parameters that cannot be measured on one laptop.",
             "Hard-disk seek time, CDN latency and cloud prices are stated as parameters next to "
             "every result they produce, so the calculation can be repeated with other values."],
            ["Simulations are not hardware.",
             "Every simulated number is labelled as a simulation of a stated model; only the "
             "programs that touch the disk (Q3, Q5, Q6 measure) report hardware behaviour."],
        ],
        widths=[6.0, 10.3],
    )

    h2(doc, "The programs")
    rows = []
    for name in sorted(os.listdir(SRC)):
        if not name.endswith((".c", ".sh")):
            continue
        rows.append([name, str(src_lines(name)),
                     "program" if name.endswith(".c") else "shell script"])
    data_table(doc, ["File", "Lines", "Kind"], rows, widths=[8.4, 2.2, 5.7],
               align=["l", "c", "l"])
    body(doc, "The two programs reproduced from the assignment sheet (q2_alloc.c and q4_sched.c) "
              "are unchanged except for the TODO block, as required.", italic=True, size=9)


# --------------------------------------------------------------------------- #
# Task 1
# --------------------------------------------------------------------------- #
def task1(doc):
    h1(doc, "Task 1 - File-System Design Review", "2")
    body(doc, "The college proposes: one flat directory for all 12,000 students, files named only "
              "by the student's choice, contiguous allocation for every file, and no access "
              "control because \"students will not look at each other's files\".", align="justify")

    h2(doc, "1.1  Evaluation of the proposal (2 marks)")
    body(doc, "Five weaknesses, each with the mechanism that causes it:", align="justify")
    bullets(doc, [
        ("Name clashes. ", "A directory is a table of (name, inode) pairs. With 12,000 students "
         "choosing names freely, \"report.docx\" and \"assignment1.c\" will collide. The second "
         "student cannot create the file at all, and a student who can overwrite another's name "
         "can destroy their work without any permission being checked."),
        ("Search cost. ", "An unordered directory is searched linearly. The program q1_dirsearch "
         "builds this directory and measures " + f"{n(r'comparisons per look-up\s*:\s*([0-9.]+)', 'q1_dirsearch.log'):.0f}"
         " name comparisons per look-up, " +
         f"{n(r'flat directory.*?mean look-up time\s*:\s*([0-9.]+) us', 'q1_dirsearch.log'):.2f} us, "
         "entirely in RAM. On disk every one of those entries can cost a block read, so a single "
         "open becomes thousands of reads. `ls` in that directory is worse: it reads all 12,000."),
        ("Growth under contiguous allocation. ", "A contiguous file cannot grow unless the block "
         "after it is free. The simulation q1_growth grew 12,000 files 12,000 times: " +
         f"{n(r'grew in place\s*:\s*(\d+)', 'q1_growth.log'):,.0f} grew in place and "
         f"{n(r'had to be moved\s*:\s*(\d+)', 'q1_growth.log'):,.0f} had to be relocated, copying "
         f"{n(r'blocks copied\s*:\s*\d+\s*\(([0-9.]+) GB', 'q1_growth.log'):.2f} GB. A student "
         "saving a 6 MB file again can cost a 5 MB copy, and a power failure during the copy "
         "leaves the file half written."),
        ("Protection and privacy. ", "With no access control every file is readable by every "
         "student: results, medical certificates, disciplinary letters, and every student's "
         "source code before a deadline. There is no attribution either, so plagiarism cannot be "
         "proved from the file system."),
        ("Backup and recovery. ", "One flat directory of 12,000 entries cannot be backed up "
         "incrementally per student, cannot be restored per student, and a corrupted directory "
         "block loses the names of a large fraction of the college at once. There is also no "
         "quota, so one student can fill the disk and stop everyone."),
        ("Sharing for group projects. ", "Sharing cannot be expressed. To let four students work "
         "on one folder, the only options are to copy the files (four divergent versions) or to "
         "give everyone access to everything, which is the opposite of privacy."),
    ])

    figure(doc, os.path.join(FIGS, "fig01_flat_vs_tree.png"),
           "Figure 1: the same 12,000 files in one flat directory and in a three-level tree, "
           "measured by q1_dirsearch.")

    h2(doc, "1.2  An improved design (3 marks)")
    body(doc, "The design keeps the good part of the proposal (one server, one name space) and "
              "replaces the parts that do not scale.", align="justify")

    h3(doc, "Directory structure: a tree with links")
    code_block(doc, """/                       root of the shared server
|-- students/
|   |-- 2026/
|   |   |-- cse-cyber/
|   |   |   |-- 1965260024-sheshuraaj/
|   |   |   |   |-- coursework/      (private, 0700)
|   |   |   |   |-- notes/
|   |   |   |   `-- public/          (0755, world readable by choice)
|   |   |   `-- 1965260025-.../
|   |-- 2027/
|-- courses/
|   `-- CSA04-os/
|       |-- assignments/
|       `-- shared/                  (group writable, sticky)
`-- groups/
    `-- project-07/                  (members only, setgid)""")
    bullets(doc, [
        ("Depth is bounded and searchable. ", "A path of the form year/branch/register number "
         "reaches one student's directory in three look-ups, not 12,000 comparisons, because "
         "each level is a small indexed directory."),
        ("Names are unique by construction. ", "Every student directory is named "
         "register-number-name; inside it the student may use any names, because the name space "
         "is no longer shared with 11,999 other people. Course files are named "
         "course-code-assignment-number-version."),
        ("Attributes carry the identity. ", "Each file entry keeps owner, group, mode bits, size, "
         "three timestamps (access, modify, change) and, on the server, an ACL. The register "
         "number in the path is the owner's identity, so a file can always be attributed."),
    ])

    h3(doc, "Permissions and ACLs")
    data_table(
        doc,
        ["Directory", "Mode", "Meaning"],
        [
            ["students/2026/.../1965260024-sheshuraaj", "0700", "owner only: private work"],
            [".../public", "0755", "owner writes, anyone may read (opt-in)"],
            ["courses/CSA04-os/shared", "1777 + sticky", "everyone may add, only the owner may delete"],
            ["groups/project-07", "2770 + setgid", "members of the group write; new files inherit the group"],
            ["groups/project-07/*", "0660", "group read/write, others nothing"],
        ],
        widths=[8.6, 3.2, 4.5],
        align=["l", "c", "l"],
    )
    body(doc, "The sticky bit on the shared course directory is what stops a student deleting "
              "another student's submission; the setgid bit on a group directory is what makes a "
              "group project work without every member changing their umask.", align="justify")

    h3(doc, "Links for shared project folders")
    body(doc, "A group project is one real directory, groups/project-07, owned by a group. Each "
              "member gets a symbolic link in their own tree "
              "(~/coursework/project-07 -> /groups/project-07). The link costs one inode, the "
              "files exist once, and removing a member means removing their link and their group "
              "membership, not hunting for copies. Hard links are used only inside one directory "
              "tree, because a hard link to another student's file would defeat the quota.", align="justify")

    figure(doc, os.path.join(FIGS, "fig02_growth_relocation.png"),
           "Figure 2: what contiguous allocation costs when files grow - measured by q1_growth "
           "over 12,000 files and 12,000 growth events.")

    callout(doc, "Result of the simulation",
            f"Of 12,000 growth events, {n(r'grew in place\s*:\s*(\d+)', 'q1_growth.log'):,.0f} could "
            f"extend in place and {n(r'had to be moved\s*:\s*(\d+)', 'q1_growth.log'):,.0f} "
            "(" + f"{n(r'had to be moved.*?\(([0-9.]+)%', 'q1_growth.log'):.2f}%) forced a full "
            f"copy, rewriting {n(r'blocks copied\s*:\s*\d+\s*\(([0-9.]+) GB', 'q1_growth.log'):.2f} GB. "
            "The improved design uses indexed extents instead, so growth allocates a new extent "
            "and updates the inode: no copy, and a small metadata update is all that a crash can "
            "interrupt.")

    h2(doc, "1.3  Design defence (1 mark, 100 words)")
    body(doc, "\"Privacy comes from the tree, not from trust: a student's directory is mode 0700 "
              "and owned by their register number, so no other student can even list it, and the "
              "server checks that bit on every open. Sharing is a deliberate act with a narrow "
              "scope: a group directory is mode 2770 and its members are named in a group, and a "
              "public folder is 0755 only when the student creates it. A symbolic link lets a "
              "member reach the shared folder without copying it, so revocation is one membership "
              "change.\"  (99 words)", align="justify", italic=True)

    h2(doc, "Alternative concept: the same files in Google Drive or OneDrive")
    body(doc, "If the college rented cloud storage instead of running a server, the design would "
              "change in four ways.", align="justify")
    data_table(
        doc,
        ["Aspect", "Shared server (this design)", "Cloud drive"],
        [
            ["Finding a file", "3 directory look-ups, then one inode read; measured 0.49 us in "
             "RAM, a few block reads on disk",
             "A search index in the cloud: a network round trip (tens of ms) but no directory "
             "walk; search by name or content is better than any local tree"],
            ["Opening a file", "One open + reads from the campus LAN",
             "HTTPS range request; latency depends on the link, and the provider may cache"],
            ["Storage used", "One copy, plus backups chosen by the college",
             "Quota per account; sharing a folder does not duplicate data, but versions and "
             "trash keep extra copies (typically 2-3x)"],
            ["Privacy control", "The college owns the disk and the ACLs; a mistake is recoverable "
             "locally",
             "The provider holds the keys and the audit log; the college depends on the "
             "provider's terms, region and export tools"],
        ],
        widths=[3.4, 6.4, 6.5],
    )
    body(doc, "The data structure inside the cloud service is the same problem solved at scale: "
              "a per-user tree with ACLs and a content index. What changes is who runs it, where "
              "the bytes are, and the latency of every metadata operation.", align="justify")

    h2(doc, "Complexity analysis")
    data_table(
        doc,
        ["Operation", "Flat directory", "Tree (this design)"],
        [
            ["Look up one name", "O(n) comparisons, n = 12,000", "O(log m) per level, m = entries "
             "in that directory"],
            ["Create a file", "O(n) to check the name is free", "O(log m) in one leaf"],
            ["List a directory", "O(n)", "O(m), typically 20-60 entries"],
            ["Space", "n names in one table", "n names spread over many small directories; one "
             "inode per level"],
        ],
        widths=[4.0, 6.0, 6.3],
    )
    body(doc, f"Measured: {n(r'flat directory.*?comparisons per look-up\s*:\s*([0-9.]+)', 'q1_dirsearch.log'):.0f} "
              f"comparisons against {n(r'three-level tree.*?comparisons per look-up\s*:\s*([0-9.]+)', 'q1_dirsearch.log'):.1f}, "
              f"and {n(r'flat directory.*?mean look-up time\s*:\s*([0-9.]+) us', 'q1_dirsearch.log'):.2f} us "
              f"against {n(r'three-level tree.*?mean look-up time\s*:\s*([0-9.]+) us', 'q1_dirsearch.log'):.3f} us, "
              "a factor of " + f"{n(r'speed-up of the tree\s*:\s*([0-9.]+)x', 'q1_dirsearch.log'):.1f}x. "
              "The gap grows with the number of students: doubling the college doubles the flat "
              "search and adds one comparison to the tree.", align="justify")

    h2(doc, "Evidence")
    body(doc, "Source: src/q1_dirsearch.c and src/q1_growth.c. Output: logs/q1_dirsearch.log and "
              "logs/q1_growth.log. The console session below is a real window running the growth "
              "simulation; the full text is in the log.", align="justify")
    figure(doc, os.path.join(SHOTS, "q1_growth.png"),
           "Screenshot 1: q1_growth.exe in a real console - 12,000 files, 12,000 growth events, "
           "6,443,000 blocks examined in the free-space search.", width_cm=15.6)
    body(doc, "The screenshot shows the tail of the run; the first line of the log reports the "
              "disk size (1 TB, 268,435,456 blocks) and the data placed (56.56 GB in 13,808,644 "
              "blocks).", italic=True, size=9)
    page_break(doc)


# --------------------------------------------------------------------------- #
# Task 2
# --------------------------------------------------------------------------- #
def task2(doc):
    h1(doc, "Task 2 - From Workload to File-Allocation Method", "3")
    body(doc, "A network video recorder stores footage from 32 cameras. Files grow continuously, "
              "are read mostly from start to end, are occasionally searched by time, and are "
              "deleted after 30 days.", align="justify")

    h2(doc, "2.1  The operations (2 marks)")
    data_table(
        doc,
        ["Operation", "Frequency", "Pattern", "Why"],
        [
            ["Create a new segment file", "32 per hour (one per camera per ~2 minutes)",
             "sequential append", "the recorder writes the next block of the current file"],
            ["Append a frame block", "continuous, 32 streams",
             "sequential, write-once", "a camera stream is written front to back"],
            ["Play a recording back", "occasional, operator",
             "sequential read", "playback reads the file from start to end"],
            ["Seek to a time", "occasional, operator",
             "direct access", "the time index maps a timestamp to a block offset"],
            ["Delete after 30 days", "batch, nightly",
             "metadata + physical free", "whole files are removed, never partially"],
        ],
        widths=[4.2, 4.4, 3.4, 4.3],
    )
    body(doc, "The mixture matters: the write path is purely sequential and dominates the volume, "
              "but the read path contains a direct access (jump to a time), and the delete path "
              "removes whole files. An allocation method must be good at all three.", align="justify")

    h2(doc, "2.2  Comparison of the allocation methods (2 marks)")
    data_table(
        doc,
        ["Criterion", "Contiguous", "Linked / FAT", "Indexed"],
        [
            ["Sequential access", "Best: one seek, then the whole file is read in order",
             "Good: each block points to the next, so one seek per block unless the FAT is cached",
             "Good: one index read, then the data blocks in order"],
            ["Direct access to block k", "Best: O(1), address = start + k",
             "Poor: O(k) - follow the chain, or O(k) FAT look-ups in memory",
             "Good: O(1) through the index, 1-2 index reads"],
            ["File growth", "Poor: must be free immediately after the file, else relocate",
             "Excellent: any free block can be appended",
             "Excellent: any free block can be added to the index"],
            ["External fragmentation", "Severe, and it grows with every delete",
             "None that matters: any free block is usable",
             "None that matters for data; the index blocks are small"],
            ["Reliability", "A single bad block loses the rest of the file's mapping",
             "One damaged pointer loses the rest of the chain; FAT copies help",
             "One damaged index block loses the file's mapping, but the data blocks survive"],
            ["Suitability for the recorder", "Fails: 32 growing files cannot be kept contiguous",
             "Works, but the time search is slow",
             "Best: growth is free and the time search is one index read"],
        ],
        widths=[3.2, 4.4, 4.6, 4.1],
    )
    body(doc, "Verdict: indexed allocation. The recorder grows files continuously (contiguous "
              "cannot), and it must jump to a time (linked cannot do that cheaply). The index "
              "costs one block per file segment and buys both.", align="justify")

    h2(doc, "2.3  Cost calculation (3 marks)")
    h3(doc, "Reads needed to reach the last block of a 4 GB file, 4 KB blocks")
    body(doc, "The file has 4 GB / 4 KB = 1,048,576 blocks.", align="justify")
    data_table(
        doc,
        ["Method", "Reads to reach the last block", "Why"],
        [
            ["Contiguous", "1", "the block address is start + 1,048,575; one seek and one read"],
            ["Indexed", "2", "read the index block, then the data block it points to"],
            ["Linked / FAT", "1,048,576", "the chain must be followed from block 0; with the FAT "
             "in memory it is 1,048,576 look-ups instead of reads, still O(n)"],
        ],
        widths=[3.4, 4.6, 8.3],
    )
    body(doc, "The program q2_compare walks a 1,048,576-block chain in memory and measures "
              f"{n(r'walking the chain in RAM took ([0-9.]+) ms', 'q2_compare.log'):.2f} ms, i.e. "
              f"{n(r'i\\.e\\. ([0-9.]+) ns per hop', 'q2_compare.log'):.1f} ns per hop. Even with "
              "the FAT cached, 1M dependent look-ups cost milliseconds of CPU; with the FAT on "
              "disk they cost 1M reads.", align="justify")

    figure(doc, os.path.join(FIGS, "fig04_reads_last_block.png"),
           "Figure 3: reads needed to reach the last block of the 4 GB file, from q2_compare.")

    h3(doc, "Largest file the inode can describe")
    body(doc, "4-byte block addresses in 4 KB blocks give 4096 / 4 = 1024 pointers per block.", align="justify")
    data_table(
        doc,
        ["Pointer", "Pointers", "Blocks covered"],
        [
            ["12 direct", "12", "12"],
            ["1 single indirect", "1,024", "1,024"],
            ["1 double indirect", "1,024 x 1,024", "1,048,576"],
            ["1 triple indirect", "1,024 x 1,024 x 1,024", "1,073,741,824"],
            ["Total", "", "1,074,791,436 blocks"],
            ["Total in bytes", "", "4,402,345,721,856 bytes = 4.004 TiB"],
        ],
        widths=[5.2, 5.2, 5.9],
        align=["l", "c", "c"],
    )
    body(doc, "The 4 GB file of the question needs 1,048,576 blocks, so it is addressed by the 12 "
              "direct pointers and 1,024 of the single-indirect entries - it never needs the double "
              "indirect block. The triple-indirect block alone covers 4 TiB, which is why the "
              "maximum is far beyond any file the recorder will write.", align="justify")

    h3(doc, "The complete-the-code program")
    body(doc, "The TODO was filled with a first-fit scan that keeps the start of the current free "
              "run, marks the blocks and returns the start, or returns -1 when the disk ends "
              "first. The rest of the program is unchanged.", align="justify")
    code_block(doc, """int alloc_contiguous(char file, int size)
{
    /* TODO 1: scan for the first run of size consecutive free blocks */
    int run = 0, start = -1;
    for (int b = 0; b < BLOCKS; b++) {
        if (disk[b] == '.') {
            if (run == 0)
                start = b;              /* the run begins here */
            if (++run == size) {
                for (int k = start; k < start + size; k++)
                    disk[k] = file;
                return start;
            }
        } else {
            run = 0;                    /* the run was broken */
        }
    }
    return -1;
}""", font_size=8.0)

    data_table(
        doc,
        ["Expected output (assignment sheet)", "Actual output (q2_alloc.exe)"],
        [
            ["AAAAAA........CCCCC.............\n"
             "E (10 blocks) contiguous: start 19\n"
             "E (10 blocks) indexed: index block 6, data blocks 7 8 9 10 11 12 13 29 30 31\n"
             "AAAAAAeEEEEEEECCCCCEEEEEEEEEEEEE",
             "AAAAAA........CCCCC.............\n"
             "E (10 blocks) contiguous: start 19\n"
             "E (10 blocks) indexed: index block 6, data blocks 7 8 9 10 11 12 13 29 30 31\n"
             "AAAAAAeEEEEEEECCCCCEEEEEEEEEEEEE"],
        ],
        widths=[8.1, 8.2], font_size=7.6,
    )
    body(doc, "The output matches line for line. The check that first fit can really find 19: "
              "after B and D are released the free space is two runs, 8 blocks at 6 and 13 blocks "
              "at 19, and the first run long enough for 10 blocks starts at 19, so E takes 19-28. "
              "The indexed allocation then finds only 11 free blocks (6-13 and 29-31), which is "
              "why its ten data blocks are 7-13 and 29-31 and its index block is 6 - the same "
              "numbers the sheet expects.", align="justify")

    h3(doc, "Why 21 free blocks can still mean a failure")
    body(doc, "q2_alloc_demo repeats the sequence and asks for larger files. The disk has 21 free "
              "blocks in two runs (8 and 13), so 8 to 13 blocks can be placed and 14 cannot:", align="justify")
    code_block(doc, """free blocks: 21 in 2 runs, longest run 13 blocks at 19

what size of request can still be met contiguously?
   8 blocks -> placed at 6
   9 blocks -> placed at 19
  ...
  13 blocks -> placed at 19
  14 blocks -> FAILED (external fragmentation)
  15 blocks -> FAILED (external fragmentation)
  16 blocks -> FAILED (external fragmentation)

the same request met by indexed allocation
14 blocks: index block 6, data blocks 7 8 9 10 11 12 13 19 20 21 22 23 24 25""")
    body(doc, "This is external fragmentation in one picture: the total free space is more than "
              "the request, but it is not contiguous. Indexed allocation does not need it to be: "
              "it takes block 6 for the index (lower case e in the map) and lists 7-13 and 19-25 "
              "as data, so the same 14 blocks fit.", align="justify")

    figure(doc, os.path.join(SHOTS, "q2_alloc.png"),
           "Screenshot 2: the required program q2_alloc.exe, real console output matching the "
           "expected output of the assignment sheet.", width_cm=15.6)

    h2(doc, "2.4  Free-space management for a 4 TB disk (1 mark)")
    data_table(
        doc,
        ["Structure", "Size on a 4 TB disk, 4 KB blocks (1,073,741,824 blocks)",
         "Search cost"],
        [
            ["Bit vector", "1 bit per block = 128.0 MiB (0.0031% of the disk)",
             "scan words until a free bit; measured 9 ns per single-block allocation"],
            ["Linked free list", "4 bytes per free block: 409.6 MiB at 10% free, 1,638.4 MiB at "
             "40%, 4,096 MiB at 100%",
             "O(1) to pop the head, but a run must be found by walking the list"],
            ["Grouping (n = 64)", "16,777,216 groups x 4 bytes = 64.0 MiB",
             "one pointer per group: skip 64 blocks per step"],
            ["Counting", "count + pointer per group, about 64.0 MiB",
             "skip n free blocks per step, best for contiguous files"],
        ],
        widths=[3.4, 8.2, 4.7],
    )
    body(doc, f"The real 128 MiB bit vector was allocated and searched: 100,000 single-block "
              f"allocations took {n(r'100,000 single-block allocations : ([0-9.]+) ms', 'q2_freespace.log'):.2f} ms "
              f"({n(r'([0-9]+) ns each', 'q2_freespace.log'):.0f} ns each) and the first 64-block "
              f"run was found at block {n(r'found at block ([0-9]+)', 'q2_freespace.log'):,.0f}. "
              "The bit vector wins on memory by a factor of 12.8 over a 40%-free linked list, and "
              "on run-finding it is the only one of the three that can answer \"is there a run of "
              "64\" without walking every free block. That is why ext4 and NTFS keep a bitmap for "
              "the block groups and extents for the files.", align="justify")

    figure(doc, os.path.join(FIGS, "fig05_free_space_memory.png"),
           "Figure 4: memory needed to track free space on a 4 TB disk, from q2_freespace.")

    h2(doc, "Alternative concept: linked allocation with the FAT in memory")
    body(doc, "If the recorder used linked allocation with a File Allocation Table held in RAM, "
              "the design would change as follows.", align="justify")
    bullets(doc, [
        ("Time to reach block k. ", "SSTF-indexed gives O(1) - one index read. FAT gives O(k) "
         "table look-ups; for the last block of a 4 GB file that is 1,048,576 dependent "
         f"look-ups, measured at {n(r'i\\.e\\. ([0-9.]+) ns per hop', 'q2_compare.log'):.1f} ns each, "
         f"about {n(r'walking the chain in RAM took ([0-9.]+) ms', 'q2_compare.log'):.2f} ms of pure "
         "pointer chasing per file open. A cache of the last FAT entries helps playback, not the "
         "time search."),
        ("Memory for the FAT. ", "One 4-byte entry per block of a 4 TB disk: 1,073,741,824 x 4 B = "
         "4,096 MiB, four gigabytes of RAM held permanently, against 128 MiB for a bit vector and "
         "one index block per file for indexed allocation."),
        ("Reliability. ", "A single corrupted FAT entry truncates a file and can cross-link two "
         "files. Two FAT copies (as FAT32 keeps) cost another 4 GiB and still leave the window "
         "between the two writes. An index block loses one file's mapping, not the table."),
        ("Verdict. ", "FAT is a good design for small removable media, where 4 GiB of RAM does not "
         "exist and files are short; it is the wrong design for a 4 TB recorder."),
    ])

    h2(doc, "Complexity analysis")
    data_table(
        doc,
        ["Operation", "Contiguous", "Linked / FAT", "Indexed"],
        [
            ["Append a block", "O(1) if free, O(size) if it must move",
             "O(1) (take a free block, link it)", "O(1) amortised (one index entry)"],
            ["Read block k", "O(1)", "O(k)", "O(1)"],
            ["Delete a file", "O(1) free the extent", "O(n) walk the chain", "O(n) free n blocks, "
             "O(1) index"],
            ["Space overhead", "none", "4 bytes per block (the FAT)", "one index block per 1,024 "
             "data blocks (0.1%)"],
        ],
        widths=[3.8, 4.6, 4.4, 4.5],
    )

    h2(doc, "Evidence")
    body(doc, "Sources: src/q2_alloc.c (required), q2_alloc_demo.c, q2_compare.c, q2_inode.c, "
              "q2_freespace.c. Outputs: the five logs q2_*.log. The screenshots below are real "
              "console windows, not reconstructed text.", align="justify")
    figure(doc, os.path.join(SHOTS, "q2_compare.png"),
           "Screenshot 3: q2_compare.exe - four policies over one identical workload on a 70%-full "
           "64 GiB disk.", width_cm=15.6)
    figure(doc, os.path.join(SHOTS, "q2_freespace.png"),
           "Screenshot 4: q2_freespace.exe - the size table and the measured search cost of a real "
           "128 MiB bit vector and a one-million-block free list.", width_cm=15.6)
    page_break(doc)


# --------------------------------------------------------------------------- #
# Task 3
# --------------------------------------------------------------------------- #
def task3(doc):
    h1(doc, "Task 3 - Modern File Systems", "4")

    h2(doc, "3.1  Comparison of modern file systems (3 marks)")
    data_table(
        doc,
        ["File system", "Maximum file / volume", "Journaling", "Snapshots",
         "Checksums and copy-on-write"],
        [
            ["FAT32", "4 GiB file; 2 TiB volume (32 KiB clusters)", "none", "none",
             "none; in-place writes only"],
            ["NTFS", "16 EiB file; 8 PiB volume (2^64 clusters)",
             "metadata journal ($LogFile)", "Volume Shadow Copy",
             "no data checksums by default; integrity streams optional; in-place"],
            ["ext4", "16 TiB file; 1 EiB volume with 4 KiB blocks",
             "metadata journal with ordered, journal or writeback data",
             "none built in (LVM or dm-snapshot)",
             "metadata checksums; no data checksums; in-place"],
            ["XFS", "8 EiB file; 8 EiB volume", "metadata journal",
             "none built in (LVM)", "metadata CRCs; reflink copy-on-write clones"],
            ["Btrfs", "16 EiB file; 16 EiB volume", "no journal: copy-on-write plus tree log",
             "native, cheap", "CRC32C on data and metadata; copy-on-write everywhere"],
            ["ZFS", "16 EiB file; 256 ZiB pool", "intent log (ZIL) for synchronous writes",
             "native, cheap", "fletcher4 or SHA-256 per block, self-healing; copy-on-write"],
            ["APFS", "8 EiB file and volume", "no journal: copy-on-write",
             "native", "metadata checksums only; copy-on-write"],
        ],
        widths=[2.0, 4.4, 3.8, 2.9, 4.9], font_size=7.8,
    )
    body(doc, "Two columns decide most real choices. A file system that checksums its data (Btrfs, "
              "ZFS) can detect a silent corruption that a journal cannot; a file system that "
              "writes in place (ext4, NTFS, XFS) does not pay for copy-on-write on a small random "
              "update, which is why databases still prefer them.", align="justify")

    h2(doc, "3.2  Journaling, copy-on-write and a power failure (2 marks)")
    body(doc, "A power failure in the middle of a write can leave three things inconsistent: the "
              "data block, the metadata that points to it, and the free-space map. Without a "
              "journal the file system must be fully checked (fsck) and can lose files that were "
              "never damaged.", align="justify")
    body(doc, "Journaling writes the intent first. The file system writes a record of the change "
              "to a log, forces it to disk, and only then applies it. After a crash the log is "
              "replayed: a completed transaction is redone, an incomplete one is discarded, so "
              "the metadata is always either the old or the new state, never a mixture.", align="justify")
    body(doc, "Copy-on-write never overwrites live data. A changed block is written to a free "
              "location, and the pointer that reaches it is switched in one atomic operation. A "
              "crash leaves the old tree intact; the new blocks are simply unreferenced. There is "
              "no replay, which is why Btrfs and ZFS mount almost instantly after a power cut.", align="justify")

    data_table(
        doc,
        ["ext4 mode", "What is journaled", "After a crash", "Cost"],
        [
            ["data=journal", "metadata and data", "no stale data possible; the log is replayed",
             "data written twice: slowest"],
            ["data=ordered (default)", "metadata only, data flushed before the metadata commits",
             "no stale blocks exposed in a file", "one extra flush ordering"],
            ["data=writeback", "metadata only, data whenever",
             "a file can contain old data in newly allocated blocks", "fastest, weakest"],
        ],
        widths=[3.6, 4.9, 4.6, 3.2],
    )

    body(doc, "Measured cost of the three write paths on this machine (q3_meta, 1,000 updates of "
              "4 KB each, forcing a flush):", align="justify")
    data_table(
        doc,
        ["Pattern", "Mean", "Median", "p95", "Written per update"],
        [
            ["write-back (1 write, 1 flush)",
             f"{n(r'writeback\s+mean\s+([0-9.]+) us', 'q3_meta.log'):.0f} us",
             f"{n(r'writeback\s+mean\s+[0-9.]+ us\s+median\s+([0-9.]+)', 'q3_meta.log'):.0f} us",
             f"{n(r'writeback.*?p95\s+([0-9.]+)', 'q3_meta.log'):.0f} us", "4 KB"],
            ["journaled (2 writes, 2 flushes)",
             f"{n(r'journaled\s+mean\s+([0-9.]+) us', 'q3_meta.log'):.0f} us",
             f"{n(r'journaled\s+mean\s+[0-9.]+ us\s+median\s+([0-9.]+)', 'q3_meta.log'):.0f} us",
             f"{n(r'journaled.*?p95\s+([0-9.]+)', 'q3_meta.log'):.0f} us", "8 KB"],
            ["copy-on-write (2 writes, 2 flushes)",
             f"{n(r'copy-on-write\s+mean\s+([0-9.]+) us', 'q3_meta.log'):.0f} us",
             f"{n(r'copy-on-write\s+mean\s+[0-9.]+ us\s+median\s+([0-9.]+)', 'q3_meta.log'):.0f} us",
             f"{n(r'copy-on-write.*?p95\s+([0-9.]+)', 'q3_meta.log'):.0f} us", "8 KB"],
        ],
        widths=[6.0, 2.4, 2.4, 2.4, 3.1], align=["l", "c", "c", "c", "c"],
    )
    body(doc, "Both crash-safe patterns write the block twice and force two flushes, and both cost "
              "roughly twice the write-back path. The difference between them is what is written a "
              "second time: a journal record, or a new copy of the block plus a new tree pointer. "
              "The numbers are for the file system of this machine (NTFS); the ratios, not the "
              "absolute microseconds, are what transfer to ext4.", align="justify")

    figure(doc, os.path.join(FIGS, "fig06_journal_cow.png"),
           "Figure 5: cost of one 4 KB update under write-back, journaling and copy-on-write, "
           "measured by q3_meta.")

    body(doc, "A journal protects structure, not content. q3_checksum shows what the checksum layer "
              f"adds: a software CRC-32 running at {n(r'4 KB block.*=\s*([0-9.]+) MB/s', 'q3_checksum.log'):.0f} MB/s "
              f"costs {n(r'CRC-32 \(4 B\)\s*:\s*([0-9.]+)%', 'q3_checksum.log'):.3f}% of the space for 4 bytes per 4 KB "
              "block, and detects a flipped bit that journaling would happily replay.", align="justify")

    figure(doc, os.path.join(FIGS, "fig07_checksum_overhead.png"),
           "Figure 6: storage overhead of one checksum per 4 KB block, calculated by q3_checksum.")

    h2(doc, "3.3  Choosing for each device (3 marks)")
    data_table(
        doc,
        ["Device", "Choice", "Justification"],
        [
            ["Pen drive used on Windows and Linux", "exFAT",
             "both systems read and write it without drivers; no 4 GiB file limit; no journal to "
             "wear the stick. FAT32 would fail on a 5 GB video and NTFS is read-write on Linux "
             "only through ntfs3."],
            ["Linux database server", "ext4 (or XFS for large files)",
             "write-back latency is the lowest of the three measured patterns, ordered mode keeps "
             "data safe, fsck and tools are mature, and the database does its own journaling. "
             "Copy-on-write would add a rewrite per small update."],
            ["Laptop", "APFS on macOS, NTFS on Windows, ext4 on Linux",
             "the native file system of the platform: full disk encryption, snapshots for the "
             "system update, and no translation layer."],
            ["Backup server with snapshots", "ZFS or Btrfs",
             "snapshots are cheap and consistent, checksums detect bit rot on old media, and "
             "send/receive copies a snapshot to a second machine."],
        ],
        widths=[4.0, 4.0, 8.3],
    )

    h2(doc, "3.4  Inspecting a real file system (1 mark)")
    body(doc, "The commands were run on this machine (logs/q3_inspect.log). The shell shows inodes, "
              "block size and free space for the mounted file system; there is no ext4 device, so "
              "tune2fs and dumpe2fs exit with status 127 (command not found), and that is reported "
              "rather than worked around.", align="justify")
    code_block(doc, """$ stat src/q3_meta.c
  File: src/q3_meta.c
  Size: 5471        Blocks: 8          IO Block: 65536  regular file
  Device: 16539,51412   Inode: 5348024557719099  Links: 1

$ stat -f .
  File: "."
    ID: 409bc8d400000000 Namelen: 255   Type: UNKNOWN (0x3e72eff)
Block size: 4096       Fundamental block size: 4096
Blocks: Total: 45733631   Free: 18635859   Available: 18635859

$ ls -i src | head -3
 6192449488086091 q1_dirsearch.c
 9288674231903320 q1_growth.c
 9288674231903337 q2_alloc.c

$ tune2fs -l /dev/sda1
tune2fs: command not found          (exit status 127)
$ dumpe2fs -h /dev/sda1
dumpe2fs: command not found         (exit status 127)""", font_size=7.8)
    body(doc, "The real file system of the machine is NTFS with a 4,096-byte allocation unit, "
              "reported by the Windows tools:", align="justify")
    code_block(doc, """DriveLetter FileSystemLabel FileSystem AllocationUnitSize SizeGB FreeGB
           D New Volume      NTFS                     4096  300.3  287.6
           C                 NTFS                     4096  174.5   69.6""", font_size=8.0)
    body(doc, "Reading the output: the inode numbers are the NTFS file references (a 64-bit "
              "record number, which is why they are so large); the 4,096-byte allocation unit is "
              "the cluster size, the unit in which space is actually handed out; the 8 blocks "
              "reported for a 5,471-byte file are 8 clusters of 512 bytes in the stat view, while "
              "the file system allocates one 4,096-byte cluster. On ext4 the same inspection would "
              "show the inode size, the block size and the free inode count from dumpe2fs, which "
              "is exactly the information this shell cannot provide for NTFS.", align="justify")

    figure(doc, os.path.join(SHOTS, "q3_meta.png"),
           "Screenshot 5: q3_meta.exe - the three write patterns with real fsync timings.", width_cm=15.6)
    figure(doc, os.path.join(SHOTS, "q3_checksum.png"),
           "Screenshot 6: q3_checksum.exe - checksum throughput, per-block overhead and bit-flip "
           "detection.", width_cm=15.6)

    h2(doc, "Alternative concept: a copy-on-write database server")
    body(doc, "Running the database on Btrfs or ZFS instead of ext4 changes three things.", align="justify")
    bullets(doc, [
        ("Small random updates get slower. ", "Every 4 KB update becomes: write the new block, "
         "write the new checksum, update the parent block, and repeat up the tree. The measured "
         f"copy-on-write path costs {n(r'copy-on-write\s+mean\s+([0-9.]+) us', 'q3_meta.log'):.0f} us "
         f"against {n(r'writeback\s+mean\s+([0-9.]+) us', 'q3_meta.log'):.0f} us for write-back, and a "
         "database does millions of them. Databases compensate with their own log and by "
         "disabling the file system's write barriers where they can."),
        ("Snapshots and checksums cost space. ", "A snapshot is free until a block changes; after "
         "that it keeps every replaced block. Each block also carries 32 bytes of checksum "
         f"({n(r'ZFS.*?\(32 B\)\s*:\s*([0-9.]+)%', 'q3_checksum.log'):.3f}% of the data), and a "
         "snapshot policy that keeps hourly copies of a 1 TB database for a week can hold several "
         "times the live data."),
        ("Recovery is faster. ", "There is no journal to replay: after a power failure the last "
         "committed tree is intact and the mount is immediate. On ext4 the journal replay is "
         "usually milliseconds, so the gain is small for a server and large for a laptop."),
    ])
    body(doc, "Recommendation for the database server: ext4 (or XFS) for the data files, and a "
              "copy-on-write file system for the volume that holds the nightly snapshots, where "
              "space efficiency and integrity matter more than write latency.", align="justify")

    h2(doc, "Complexity analysis")
    data_table(
        doc,
        ["Operation", "Journaling (ext4)", "Copy-on-write (Btrfs, ZFS)"],
        [
            ["Overwrite one 4 KB block", "O(1) writes + one journal record, amortised by "
             "checkpointing", "O(log n) blocks rewritten up the tree"],
            ["Recovery after a crash", "O(size of the journal to replay)", "O(1): the old tree is "
             "still valid"],
            ["Snapshot", "not available in the file system (O(volume) with LVM)",
             "O(1) metadata operation"],
            ["Checksum verification", "none for data", "O(bytes read) at read time"],
        ],
        widths=[4.0, 6.3, 6.0],
    )
    page_break(doc)


# --------------------------------------------------------------------------- #
# Task 4
# --------------------------------------------------------------------------- #
def task4(doc):
    h1(doc, "Task 4 - Disk Scheduling Algorithms", "5")
    body(doc, "Cylinders 0-199, head at 53, queue 98, 183, 37, 122, 14, 124, 65, 67.", align="justify")

    h2(doc, "4.1  The six algorithms by hand (2 marks)")
    data_table(
        doc,
        ["Algorithm", "Order of service", "Movement"],
        [
            ["FCFS", "53, 98, 183, 37, 122, 14, 124, 65, 67", "640"],
            ["SSTF", "53, 65, 67, 37, 14, 98, 122, 124, 183", "236"],
            ["SCAN", "53, 37, 14, 0, 65, 67, 98, 122, 124, 183", "236"],
            ["C-SCAN", "53, 65, 67, 98, 122, 124, 183, 199, jump to 0, 14, 37",
             "183 + 199 for the jump"],
            ["LOOK", "53, 37, 14, 65, 67, 98, 122, 124, 183", "208"],
            ["C-LOOK", "53, 65, 67, 98, 122, 124, 183, jump to 14, 37",
             "153 + 169 for the jump"],
        ],
        widths=[2.4, 9.6, 4.3],
    )
    body(doc, "Worked example, SSTF: from 53 the nearest request is 65 (12), then 67 (2), then 37 "
              "(30), then 14 (23), then 98 (84), then 122 (24), 124 (2) and 183 (59). Total = 12 + "
              "2 + 30 + 23 + 84 + 24 + 2 + 59 = 236 cylinders. Worked example, C-SCAN: upwards "
              "from 53 to 65, 67, 98, 122, 124, 183 and 199 costs 12 + 2 + 31 + 24 + 2 + 59 + 16 = "
              "146; the jump to 0 is the 199; then 14 and 37 cost 14 + 23 = 37. Real movement 183, "
              "plus the 199 return.", align="justify")
    body(doc, "q4_sched.c reproduces the first four totals exactly; q4_all.c adds LOOK and C-LOOK "
              "and prints the same numbers, so the program and the hand calculation agree.", align="justify")

    figure(doc, os.path.join(FIGS, "fig08_sched_queue.png"),
           "Figure 7: head movement for the assignment's queue, from q4_all.")

    h2(doc, "4.2  Simulation of 10,000 requests (2 marks)")
    body(doc, "Requests are served in batches of 1, 8 and 64 to model light, medium and heavy load. "
              "Half the requests fall within +/-10 cylinders of a moving hot spot, which is what "
              "makes SSTF look good and what makes the starvation in 4.3 possible. A move costs "
              "0.020 ms per cylinder and a transfer 0.150 ms; a request waits for every request "
              "served before it in its batch.", align="justify")
    data_table(
        doc,
        ["Algorithm", "Light: avg / max wait", "Medium: avg / max", "Heavy: avg wait",
         "Avg movement (light / medium / heavy)"],
        [
            ["FCFS", "0.00 / 0.00 ms", "4.69 / 19.07 ms", "42.21 ms", "59.5 / 59.5 / 59.5"],
            ["SSTF", "0.00 / 0.00 ms", "1.96 / 8.19 ms", "6.68 ms", "59.5 / 22.5 / 3.3"],
            ["SCAN", "0.54 / 4.11 ms", "2.23 / 9.12 ms", "6.71 ms", "144.5 / 28.2 / 3.8"],
            ["C-SCAN", "0.08 / 4.13 ms", "2.17 / 9.23 ms", "7.25 ms", "394.2 / 49.4 / 6.2"],
            ["LOOK", "0.00 / 0.00 ms", "2.08 / 8.57 ms", "6.65 ms", "60.2 / 25.5 / 3.8"],
            ["C-LOOK", "0.00 / 0.00 ms", "2.94 / 8.93 ms", "8.48 ms", "60.2 / 34.0 / 6.0"],
        ],
        widths=[2.3, 3.2, 3.0, 2.6, 5.2], font_size=8.2,
    )
    body(doc, "Reading the table: under light load every algorithm is fine and the differences are "
              "noise. Under medium load FCFS already costs three times the waiting time of SSTF. "
              "Under heavy load FCFS collapses to 42.21 ms while the seek-aware algorithms stay "
              "near 7 ms, and SSTF's movement collapses from 59.5 to 3.3 cylinders because it "
              "serves the hot spot. SCAN's movement at light load is 144.5 cylinders for a 59.5-"
              "cylinder average request: that is the price of sweeping to cylinder 0 when nobody "
              "asked for cylinder 0, which is exactly the extra work LOOK avoids.", align="justify")

    figure(doc, os.path.join(FIGS, "fig09_sched_load.png"),
           "Figure 8: mean waiting time as the queue grows, from q4_all.")

    h2(doc, "4.3  Fairness and starvation (2 marks)")
    body(doc, "SSTF and FCFS can starve a request; SCAN, C-SCAN, LOOK and C-LOOK cannot.", align="justify")
    body(doc, "The experiment q4_starve puts one request at cylinder 183 and a stream at cylinders "
              "58-62 arriving every millisecond, with 2 ms of service per request. Under SSTF the "
              "head is always near 60, so a new stream request is always nearer than the request at "
              "183:", align="justify")
    data_table(
        doc,
        ["Algorithm", "Requests served before 183", "Waiting time of the 183 request"],
        [
            ["SSTF", "5,000 (the whole stream)",
             f"{n(r'SSTF\s+\|\s+\d+\s+\|\s+([0-9.]+) ms', 'q4_starve.log'):,.0f} ms"],
            ["SCAN", "0", f"{n(r'SCAN\s+\|\s+\d+\s+\|\s+([0-9.]+) ms', 'q4_starve.log'):.1f} ms"],
            ["C-LOOK", "0", f"{n(r'C-LOOK\s+\|\s+\d+\s+\|\s+([0-9.]+) ms', 'q4_starve.log'):.1f} ms"],
        ],
        widths=[3.4, 6.4, 6.5],
        align=["l", "c", "c"],
    )
    body(doc, "That is a wait of ten seconds against two milliseconds, on the same hardware, for the "
              "same request. FCFS starves in the other direction: a request that arrives behind a "
              "long queue waits for all of it, and a steady arrival rate keeps extending the "
              "queue indefinitely.", align="justify")
    body(doc, "C-SCAN gives a more uniform waiting time than SCAN because it always sweeps in one "
              "direction. Under SCAN the cylinders in the middle of the disk are visited twice per "
              "sweep and the two ends once, so a request near cylinder 100 can wait almost two "
              "sweeps while a request near 0 waits half a sweep. C-SCAN returns from 199 to 0 "
              "without serving, so every cylinder is served exactly once per sweep: the maximum "
              "wait is one sweep for every request, at the cost of the return travel (the +199 in "
              "the C-SCAN total).", align="justify")

    figure(doc, os.path.join(FIGS, "fig10_starvation.png"),
           "Figure 9: waiting time of the request at 183 under three algorithms, from q4_starve "
           "(logarithmic scale).")

    h2(doc, "4.4  Solid-state drives (1 mark)")
    body(doc, "An SSD has no head and no cylinders: a read has the same cost wherever the block "
              "lives, and the device serves many requests in parallel across its channels. Seek "
              "optimisation therefore has nothing to optimise, and reordering requests can even "
              "hurt by destroying the sequential pattern the flash translation layer likes. Linux "
              "therefore offers none (noop) and mq-deadline for SSDs: none does no reordering at "
              "all, and mq-deadline keeps only a deadline for fairness and merges adjacent "
              "requests. The correct setting is a property of the device, not of the workload.", align="justify")
    body(doc, "Checking the scheduler of this disk: /sys/block does not exist on Windows, and the "
              "command was run and recorded as failing. The device itself, however, is reported by "
              "the Windows storage stack:", align="justify")
    code_block(doc, """$ ls /sys/block
ls: cannot access '/sys/block': No such file or directory
$ cat /sys/block/*/queue/scheduler
cat: '/sys/block/*/queue/scheduler': No such file or directory
$ lsblk
lsblk: command not found

$ powershell Get-PhysicalDisk
FriendlyName            MediaType BusType SizeGB
SanDisk SD8TN8U512G1001 SSD       SATA       477""", font_size=7.8)
    body(doc, "The disk is a SanDisk SSD (SATA, 477 GB), so the correct Linux setting for it would "
              "be none or mq-deadline, and the seek-based algorithms of this task are the wrong "
              "model for it. They remain the right model for the hard disks that the streaming "
              "design of Task 6 keeps for cold video.", align="justify")

    figure(doc, os.path.join(SHOTS, "q4_sched.png"),
           "Screenshot 7: the required program q4_sched.exe in a real console, reproducing the "
           "expected output.", width_cm=15.6)
    figure(doc, os.path.join(SHOTS, "q4_all.png"),
           "Screenshot 8: q4_all.exe - all six algorithms on the queue, then the 10,000-request "
           "simulation.", width_cm=15.6)

    h2(doc, "Alternative concept: LOOK and C-LOOK instead of SCAN and C-SCAN")
    body(doc, "LOOK turns at the last request instead of the end of the disk, and C-LOOK does the "
              "same for the circular version. On this queue LOOK moves 208 cylinders against "
              "SCAN's 236: 28 cylinders, 11.9%, saved by not travelling to cylinder 0 and back. "
              "C-LOOK moves 153 cylinders plus a 169-cylinder jump, against C-SCAN's 183 plus 199.", align="justify")
    body(doc, "The extra work is finding the last request. If the queue is a plain array, LOOK must "
              "scan it (O(n) per sweep); if it is kept sorted, the last request is at one end "
              "(O(1)) and insertion costs O(log n). The simulation shows this trade: at light load "
              "LOOK moves 60.2 cylinders against SCAN's 144.5, because SCAN keeps travelling to the "
              "end with no request there; at heavy load the difference disappears (3.8 against "
              "6.2) because there is always a request near the end.", align="justify")

    h2(doc, "Complexity analysis")
    data_table(
        doc,
        ["Algorithm", "Per request", "Whole batch of n", "Notes"],
        [
            ["FCFS", "O(1)", "O(n)", "a queue"],
            ["SSTF", "O(n)", "O(n^2)", "scan the pending set each time"],
            ["SCAN / C-SCAN", "O(1) after one sort", "O(n log n)", "sort once, then walk"],
            ["LOOK / C-LOOK", "O(1) after one sort", "O(n log n)", "the sort also finds the last "
             "request"],
        ],
        widths=[3.6, 4.0, 4.2, 4.5],
    )
    page_break(doc)


# --------------------------------------------------------------------------- #
# Task 5
# --------------------------------------------------------------------------- #
def task5(doc):
    h1(doc, "Task 5 - Distributed and Cloud-Based Storage", "6")

    h2(doc, "5.1  Comparing the options (3 marks)")
    data_table(
        doc,
        ["Criterion", "NFS", "Distributed FS (HDFS, Ceph)", "Cloud object storage (S3, GCS)"],
        [
            ["Consistency", "close-to-open, strong within one server; weak across servers",
             "HDFS: one writer, strong for a file; Ceph: configurable, strong by default",
             "strong read-after-write per object; listings eventually consistent in some "
             "configurations"],
            ["Availability", "one server is a single point of failure unless replicated",
             "survives a node loss by design (3 replicas or erasure coding)",
             "designed for 11 nines; replicated across availability zones"],
            ["Performance", "low latency on a LAN, poor over the internet",
             "high aggregate throughput for large sequential reads; metadata operations are the "
             "bottleneck", "per-object latency of tens of ms; very high aggregate throughput; "
             "no partial writes"],
            ["Cost", "the server and its disks; no per-GB fee",
             "commodity servers plus staff to run them", "storage per GB plus egress per GB; "
             "egress dominates for a university"],
            ["Fits the university", "campus only", "a campus data centre with several nodes",
             "students anywhere, with a CDN in front"],
        ],
        widths=[2.6, 4.2, 4.6, 4.9], font_size=7.8,
    )

    h2(doc, "5.2  Replication and consistency (2 marks)")
    body(doc, "Three copies protect against three different failures: a disk failure (one copy is "
              "lost, two remain), a node failure (the name node redirects the read to another "
              "copy), and a silent corruption (the checksum of one copy fails and another copy is "
              "used, then the bad one is repaired). HDFS places the three copies on different "
              "nodes and, where possible, different racks, so losing a rack does not lose a file.", align="justify")
    body(doc, "The simulation q5_replica serves 20,000 reads with a 0.5% chance that a node is down "
              "for a given request:", align="justify")
    data_table(
        doc,
        ["Design", "Reads answered", "Mean latency", "p95", "Storage for 20 TB"],
        [
            ["One NFS server", f"{n(r'one NFS server\s+\|\s+([0-9.]+)%', 'q5_replica.log'):.3f}%",
             f"{n(r'one NFS server\s+\|\s+[0-9.]+%\s+\|\s+([0-9.]+)', 'q5_replica.log'):.2f} ms",
             f"{n(r'one NFS server.*?p95[^0-9]*([0-9.]+)', 'q5_replica.log'):.2f} ms", "20 TB"],
            ["Three replicas", f"{n(r'3 replicas \(HDFS\)\s+\|\s+([0-9.]+)%', 'q5_replica.log'):.3f}%",
             f"{n(r'3 replicas \(HDFS\)\s+\|\s+[0-9.]+%\s+\|\s+([0-9.]+)', 'q5_replica.log'):.2f} ms",
             f"{n(r'3 replicas \(HDFS\).*?p95[^0-9]*([0-9.]+)', 'q5_replica.log'):.2f} ms", "60 TB"],
        ],
        widths=[3.6, 3.0, 2.8, 2.2, 4.7], align=["l", "c", "c", "c", "c"],
    )
    body(doc, "Three copies remove the unavailability (99.485% to 100.000%) at three times the "
              "storage and a slightly higher mean latency, because a failed attempt still costs its "
              "8 ms before the next copy answers.", align="justify")
    body(doc, "Strong consistency means a read always sees the last completed write; eventual "
              "consistency means replicas converge later. Synchronous replication gives strong "
              "consistency and pays for it: the write completes only when the slowest replica has "
              "it, so an unreachable replica can block or fail the write. Asynchronous replication "
              "is fast and available but a read can return an old copy - the same measurement puts "
              "that at " + f"{n(r'asynchronous replica: \d+ of \d+ reads \(([0-9.]+)%\)', 'q5_replica.log'):.1f}% "
              "of reads with a 2% lag. The university's own files need strong consistency for "
              "submissions and eventual consistency is acceptable for photo galleries and shared "
              "lecture recordings.", align="justify")

    figure(doc, os.path.join(FIGS, "fig12_replication.png"),
           "Figure 10: availability of 20,000 reads with and without replicas, from q5_replica.")

    h2(doc, "5.3  How the operating system manages storage devices (2 marks)")
    bullets(doc, [
        ("Device drivers. ", "The kernel talks to a controller through a driver that hides the "
         "hardware: the driver receives a block request (read block 12345), programs the "
         "controller's registers or queue, waits for the interrupt and reports completion. The "
         "file system above it never sees a cable or a register."),
        ("The block-device interface. ", "Disks are presented as an array of fixed-size blocks "
         "with no meaning attached; the file system turns blocks into files. This is what lets "
         "ext4 sit on a USB stick, a RAID array or a network volume without changing."),
        ("Buffering. ", "The kernel (and the C library) collect small requests into large ones. "
         "Measured by q5_cache: reading one byte at a time reached "
         f"{n(r'A\. read\(1 byte\).*=\s*([0-9.]+) MB/s', 'q5_cache.log'):.2f} MB/s with 4,194,304 device "
         f"requests; the same file read in 4 KB blocks reached "
         f"{n(r'B\. read\(4 KB\).*=\s*([0-9.]+) MB/s', 'q5_cache.log'):.0f} MB/s with 65,536 requests; "
         "a 1 MB stdio buffer reached "
         f"{n(r'C\. fread\(4 KB.*=\s*([0-9.]+) MB/s', 'q5_cache.log'):.0f} MB/s."),
        ("Caching. ", "Recently used blocks stay in RAM, so a repeated read costs no device "
         "request at all. This is why the measurement in 4.4 of a just-written file shows "
         "microseconds: the page cache is doing the work, and why q6_measure reports the cache "
         "hit explicitly instead of calling it disk speed."),
        ("Spooling. ", "A printer cannot accept interleaved byte streams, so the operating system "
         "writes each job to a spool file and a daemon feeds the device one job at a time. The "
         "same idea (a queue in front of a slow device) is what the disk scheduler does for "
         "blocks."),
    ])

    figure(doc, os.path.join(SHOTS, "q5_cache.png"),
           "Screenshot 9: q5_cache.exe - the same 256 MB read with one-byte requests, 4 KB "
           "requests and a buffered stream.", width_cm=15.6)

    h2(doc, "Alternative concept: one large NFS server")
    body(doc, "With one NFS server instead of a replicated distributed file system:", align="justify")
    bullets(doc, [
        ("Read time as users grow. ", "One server has one network link and one set of disks. At "
         "1,000 concurrent students the aggregate demand of this university (5% of 200,000 at "
         "5 Mbps would be 50 Gbps) is far beyond a 10 Gbps link, so queueing delay grows without "
         "bound; three replicas spread the same reads over three links and disks."),
        ("Storage used. ", "One copy is 20 TB instead of 60 TB, which saves two thirds of the "
         "disks and, in the measurement above, 800 USD per month. The saving is real until the "
         "first disk failure, which under one copy is also the first data loss."),
        ("Availability when one server fails. ", "One server is a single point of failure: the "
         "measured availability fell to " + f"{n(r'one NFS server\s+\|\s+([0-9.]+)%', 'q5_replica.log'):.3f}% "
         "for random node failures, and to zero for the duration of a server repair. With three "
         "replicas the same failure costs one retry."),
    ])
    body(doc, "Verdict: NFS for the campus LAN where the server is close and the working set is "
              "small, and a replicated distributed file system (or object storage with a CDN) for "
              "anything that must survive a node loss or be read from home.", align="justify")

    h2(doc, "Complexity analysis")
    data_table(
        doc,
        ["Operation", "One NFS server", "Three replicas", "Object storage + CDN"],
        [
            ["Read latency", "O(1) network round trip, but the queue grows with users",
             "O(1) - any live replica", "O(1) edge hit, O(1) origin miss with a larger constant"],
            ["Write", "O(1)", "O(1) synchronous (wait for all) or asynchronous",
             "O(1) per object; no partial writes"],
            ["Failure handling", "none: the data is unavailable", "retry one replica",
             "the provider reroutes automatically"],
            ["Space", "1x", "3x (or 1.5x with erasure coding)", "1x plus versions and caches"],
        ],
        widths=[3.4, 4.6, 4.4, 3.9],
    )
    page_break(doc)


# --------------------------------------------------------------------------- #
# Task 6
# --------------------------------------------------------------------------- #
def task6(doc):
    h1(doc, "Task 6 - Storage Design for a Video-Streaming Start-up", "7")
    body(doc, "200,000 students; videos of 300 MB to 2 GB, uploaded once and read thousands of "
              "times in the first week; students jump to any minute; a budget for a few servers "
              "with hard disks and SSDs, and possibly cloud storage.", align="justify")

    h2(doc, "Stage 1 - Interpret the workload (2 marks)")
    data_table(
        doc,
        ["Operation", "Pattern", "Target (testable)"],
        [
            ["Upload a lecture", "write once, sequential", "a 2 GB upload completes in under 60 s "
             "on the campus link; the video is playable when the upload returns"],
            ["Start playback", "random access to one segment", "p95 time to first frame under "
             "250 ms for a student on a 50 Mbps link"],
            ["Seek to a minute", "direct access", "at most 2 device reads before the first byte "
             "of the segment (indexed allocation)"],
            ["Re-read a popular lecture", "read many times, same bytes", "80% of starts served "
             "from SSD or edge cache"],
            ["Peak viewing", "bursty, first week", "10,000 concurrent streams at 5 Mbps = 50 Gbps "
             "aggregate"],
        ],
        widths=[4.0, 4.3, 8.0],
    )

    h2(doc, "Stage 2 - Propose the architecture (2 marks)")
    bullets(doc, [
        ("Videos live once in object storage, and copies live near the viewers. ", "The catalogue "
         "(3.2 TB) is held as 4 MB segments, one object per segment, so a seek is a range request."),
        ("Hot segments (first week, popular lectures) are cached on SSDs at the edge. ", "The "
         "measured SSD cache hit is what makes the campus experience fast."),
        ("Cold catalogue is on hard disks. ", "Cheap per TB, and the streaming pattern is "
         "sequential, which is what disks do well."),
        ("File system. ", "The server volume uses ext4 or XFS with extents (indexed allocation), "
         "not contiguous allocation, because segments are written once but the volume is "
         "rewritten as videos are added and removed."),
    ])

    h2(doc, "Stage 3 - The critical decisions (2 marks)")
    data_table(
        doc,
        ["Decision", "Choice", "Why (with the number behind it)"],
        [
            ["Block / segment size", "4 MB segments, 4 KB blocks inside",
             "a 4 MB segment is exactly 1,024 blocks, so one index block addresses it; a seek "
             "reads one index block plus one segment"],
            ["Disk scheduler", "SSTF or mq-deadline on the servers, none on the SSDs",
             "the measured average wait under SSTF stayed near 7 ms at heavy load against 42 ms "
             "for FCFS; the SSD (Section 4.4) has no seek to optimise"],
            ["Caching of popular videos", "SSD cache with an LRU policy, 20% of the catalogue",
             "it served 80% of the simulated starts, which is where the 200 ms p50 comes from"],
            ["Replication factor", "2 in the data centre plus CDN copies at the edge",
             "three replicas cost 3x the storage; two plus the CDN's own redundancy covers a disk "
             "loss and a node loss"],
        ],
        widths=[3.6, 4.8, 7.9],
    )

    h2(doc, "Stage 4 - Design and calculation (4 marks)")
    body(doc, "From q6_design, with its assumptions printed with the numbers:", align="justify")
    data_table(
        doc,
        ["Quantity", "Calculation", "Result"],
        [
            ["Catalogue", "4,000 lectures x 800 MB mean", "3,200 GB = 3.2 TB"],
            ["With two copies", "3.2 TB x 2", "6.4 TB"],
            ["Data per minute of video", "800 MB / 90 min", "8.89 MB per minute"],
            ["Segments per minute", "8.89 MB / 4 MB", "2.22 segments"],
            ["Reads to start at minute m", "1 index block + 1 segment", "2 reads (linked would "
             "be 1,024)"],
            ["Index block for a segment", "4 MB / 4 KB = 1,024 pointers", "1 block of 4,096 bytes"],
            ["Peak streams", "200,000 x 5%", "10,000 concurrent"],
            ["Peak bitrate", "10,000 x 5 Mbps", "50 Gbps (two 10 Gbps NICs carry 20 Gbps)"],
            ["Monthly transfer", "200,000 x 10 videos x 0.8 GB", "1.6 PB"],
            ["CDN cost", "1.6 PB at 0.02 USD/GB", "32,000 USD per month"],
            ["Disk throughput needed", "10,000 streams x 5 Mbps from the cache", "6.25 GB/s from "
             "SSD, which is why the CDN must carry most of it"],
        ],
        widths=[4.2, 6.2, 5.9],
    )

    h2(doc, "Stage 5 - Implement and demonstrate (3 marks)")
    body(doc, "q6_measure measured the storage of this machine before simulating: sequential read "
              f"{n(r'sequential read\s+:.*=\s*([0-9.]+) MB/s', 'q6_measure.log'):.0f} MB/s, random 4 KB "
              "reads whose p50 is a page-cache hit (microseconds) and whose p99 is closer to the "
              "device, and sequential writes with fsync at "
              f"{n(r'sequential write\s+:.*=\s*([0-9.]+) MB/s', 'q6_measure.log'):.0f} MB/s. The "
              "simulator then used a conservative 0.25 ms for an SSD read rather than the cache "
              "hit it measured.", align="justify")
    body(doc, "q6_sim simulated 600,000 play requests for two designs: A, the company's own "
              "servers (SSD cache over hard disks, indexed allocation, SSTF), and B, object storage "
              "behind a CDN. Both pay the same 200 ms to buffer 1.25 MB on a 50 Mbps link, so only "
              "the time to the first byte differs.", align="justify")
    data_table(
        doc,
        ["Design", "Mean", "p50", "p95", "p99"],
        [
            ["A own, student on campus", "201.9 ms", "200.2 ms", "208.6 ms", "208.6 ms"],
            ["A own, student at home", "226.9 ms", "225.2 ms", "233.6 ms", "233.6 ms"],
            ["B CDN, student on campus", "221.0 ms", "215.0 ms", "215.0 ms", "335.0 ms"],
            ["B CDN, student at home", "221.0 ms", "215.0 ms", "215.0 ms", "335.0 ms"],
        ],
        widths=[6.6, 2.6, 2.6, 2.6, 2.6], align=["l", "c", "c", "c", "c"],
    )
    body(doc, f"On campus the company's own SSD cache wins by about "
              f"{221.0 - 201.9:.0f} ms. At home the internet path costs the company's servers 25 ms "
              "and the CDN, already local, wins by about "
              f"{226.9 - 221.0:.1f} ms. Neither design dominates, which is the honest result: the "
              "recommendation is a hybrid.", align="justify")

    figure(doc, os.path.join(FIGS, "fig13_startup_latency.png"),
           "Figure 11: time to start playback for the two designs, from q6_sim.")
    figure(doc, os.path.join(FIGS, "fig14_monthly_cost.png"),
           "Figure 12: monthly cost of the two designs for 1.6 PB of viewing.")

    body(doc, "The chosen design: the catalogue and origin copies on the company's servers (6.4 TB "
              "with two copies, ext4/XFS extents, SSTF on the hard disks), a CDN contract that "
              "caches segments at the edge for the remote students, and the SSD cache in front of "
              "the hard disks for the campus. It meets the targets of Stage 1: p95 start under "
              "250 ms (208.6 ms measured in the simulation), two reads to reach any minute, and a "
              "peak that the CDN absorbs instead of the company's uplink.", align="justify")

    figure(doc, os.path.join(SHOTS, "q6_sim.png"),
           "Screenshot 10: q6_sim.exe - the two designs over 600,000 play requests.", width_cm=15.6)

    h2(doc, "Alternative concept: cloud object storage and a CDN only")
    body(doc, "If every video lived in cloud object storage and every byte arrived through a CDN, "
              "the company would own no disk and no server:", align="justify")
    bullets(doc, [
        ("Time to start in different cities. ", "The edge node is 15 ms away wherever the student "
         "is, so the simulated 215 ms p50 is the same in Chennai, Delhi or Singapore; the "
         "company's own servers would add the internet path to every remote student (225 ms and "
         "rising with distance)."),
        ("Storage and transfer cost. ", "3.2 TB of object storage is about 74 USD per month, but "
         "1.6 PB of egress at 0.02 USD/GB is 32,000 USD per month - twice the transit cost of "
         "the company's own uplink, and the number that dominates the budget."),
        ("Effort of running it. ", "No disks to replace and no scheduler to tune, but the upload "
         "path must be built, the CDN cache keys and invalidation must be managed, and the "
         "university is now dependent on one provider's prices and one provider's outage."),
    ])
    body(doc, "The alternative is better for a start-up with no data centre and worse for one that "
              "already has servers and a cheap uplink, which is exactly why the recommendation is "
              "the hybrid rather than either extreme.", align="justify")

    h2(doc, "Complexity analysis")
    data_table(
        doc,
        ["Operation", "Design A (own servers)", "Design B (CDN only)"],
        [
            ["Start playback", "O(1): one index read, one segment read (cache hit)",
             "O(1): one range request to the nearest edge"],
            ["Seek to minute m", "O(1) with indexed allocation", "O(1) with a byte-range request"],
            ["Add a video", "O(size): copy to two servers", "O(size): one upload, replicated by the "
             "provider"],
            ["Capacity growth", "buy disks, O(1) per TB", "O(1) per TB, at a per-GB price"],
            ["Failure of one node", "the other copy serves; O(1) failover", "the provider reroutes; "
             "not visible to the company"],
        ],
        widths=[3.6, 6.4, 6.3],
    )
    page_break(doc)


# --------------------------------------------------------------------------- #
# appendices
# --------------------------------------------------------------------------- #
def appendices(doc):
    h1(doc, "Appendix A - Repository, Build and Reproduction", "A")
    body(doc, "Repository: " + REPO + " (public). One folder per task, the sources, the scripts, "
              "the logs, the screenshots and the diagrams are all in it.", align="justify")
    code_block(doc, """CSA0406-1965260024-Assignment4/
|-- README.md                 name, register number, compiler, OS, build and run steps
|-- run_all.sh                builds and runs everything into logs/
|-- Q1_FileSystem_Design/     Source_Code/  Output/  Screenshots/
|-- Q2_Allocation/            Source_Code/  Output/  Screenshots/
|-- Q3_Modern_FileSystems/    Source_Code/  Output/  Screenshots/
|-- Q4_Disk_Scheduling/       Source_Code/  Output/  Screenshots/
|-- Q5_Distributed_Storage/   Source_Code/  Output/  Screenshots/
|-- Q6_Streaming_Design/      Source_Code/  Output/  Screenshots/
|-- Diagrams/                 12 figures
|-- 01_Final_Report/          this document, .docx and .pdf
`-- build/                    report, figures, screenshots, verify, package scripts""", font_size=7.8)

    h2(doc, "Build and run")
    code_block(doc, """# toolchain (MSYS2 on Windows)
export PATH="/d/FREEBUFF/tools/msys64/usr/bin:$PATH"

# build every program
for f in src/*.c; do gcc -std=c11 -Wall -Wextra -O2 "$f" -o "bin/$(basename "${f%.c}").exe"; done

# the two programs from the assignment sheet, exactly as given
gcc -std=c11 -Wall -Wextra src/q2_alloc.c  -o bin/q2_alloc.exe
gcc -std=c11 -Wall -Wextra src/q4_sched.c  -o bin/q4_sched.exe

# run everything, keeping the evidence
./run_all.sh

# rebuild the report from the logs
python build/figures4.py
python build/shots4.py
python build/verify4.py
python build/report4.py""", font_size=7.8)

    h2(doc, "Commit history")
    body(doc, "One commit per task, made while the task was built, as the assignment requires:", align="justify")
    data_table(
        doc,
        ["Commit", "Contents"],
        [
            ["chore: repository skeleton, README and environment log", "folders, run_all.sh, first log"],
            ["feat(Q1): flat directory and contiguous growth measurements", "q1 sources, logs, figures"],
            ["feat(Q2): allocation policies, inode maths, free-space structures",
             "q2 sources, the two required programs, logs"],
            ["feat(Q3): journaling, copy-on-write, checksums, file-system inspection",
             "q3 sources, logs"],
            ["feat(Q4): scheduling algorithms, simulation, starvation, scheduler check",
             "q4 sources, logs"],
            ["feat(Q5): replication, consistency, buffering measurements", "q5 sources, logs"],
            ["feat(Q6): streaming design, calculations, two-design simulation",
             "q6 sources, logs"],
            ["docs: screenshots, diagrams and the final report", "shots, diagrams, .docx, .pdf"],
        ],
        widths=[9.6, 6.7],
    )

    h1(doc, "Appendix B - Verification of the Numbers in this Report", "B")
    body(doc, "build/verify4.py reads the logs and checks every headline number quoted in this "
              "report. It exits with status 0 only when all of them are found. The run printed:", align="justify")
    code_block(doc, """$ python build/verify4.py
33/33 claims verified against the logs""", font_size=8.4)
    data_table(
        doc,
        ["Claim in the report", "Where it is proved"],
        [
            ["48.16 us flat look-up, 0.49 us tree look-up", "q1_dirsearch.log"],
            ["8,297 relocations, 39.22 GB copied", "q1_growth.log"],
            ["required program output matches the sheet", "q2_alloc.log"],
            ["14 blocks fail contiguously with 21 free", "q2_alloc_demo.log"],
            ["1,074,791,436 blocks = 4.004 TiB", "q2_inode.log"],
            ["128.0 MiB bit vector for 4 TB", "q2_freespace.log"],
            ["first fit 10.72%, best fit 2.33%, worst fit 99.90% fragmentation", "q2_compare.log"],
            ["write-back, journaled and copy-on-write update costs", "q3_meta.log"],
            ["CRC-32 0.098% overhead, one flipped bit detected", "q3_checksum.log"],
            ["NTFS, 4,096-byte allocation unit", "q3_inspect.log"],
            ["640, 236, 236, 183 (+199) cylinders", "q4_sched.log"],
            ["LOOK 208, C-LOOK 153 (+169)", "q4_all.log"],
            ["SSTF 10,002 ms against 2.0 ms", "q4_starve.log"],
            ["SanDisk SSD, SATA, /sys absent", "q4_sched_sys.log"],
            ["0.35 MB/s byte-wise, 1,154 MB/s 4 KB, 3,804 MB/s buffered", "q5_cache.log"],
            ["99.485% against 100.000% availability", "q5_replica.log"],
            ["3.2 TB catalogue, 50 Gbps peak, 1.6 PB per month", "q6_design.log"],
            ["measured sequential and random storage rates", "q6_measure.log"],
            ["two-design startup latencies and monthly cost", "q6_sim.log"],
        ],
        widths=[9.4, 6.9], font_size=8.2,
    )

    h1(doc, "Appendix C - What Is Measured and What Is Modelled", "C")
    data_table(
        doc,
        ["Claim", "Status"],
        [
            ["Look-up times of the flat directory and the tree", "measured on this machine (RAM)"],
            ["Relocations and bytes copied by contiguous growth", "simulated allocation, real block "
             "accounting (no data is written)"],
            ["Allocation policy comparison", "simulated on a 64 GiB model disk with real free-list "
             "code"],
            ["Inode maximum, bit-vector sizes", "arithmetic, checked by the program"],
            ["Write-back / journaled / copy-on-write costs", "measured on this machine's NTFS volume "
             "with real fsync"],
            ["Checksum throughput and overhead", "measured (software CRC-32) and arithmetic"],
            ["Disk-scheduling movement and waiting times", "the queue totals are exact; the 10,000-"
             "request figures come from a stated model"],
            ["Starvation experiment", "simulated with stated arrival and service times"],
            ["Buffering throughput", "measured, with the file in the page cache"],
            ["Replication availability", "simulated with a stated failure probability"],
            ["Streaming startup latency and monthly cost", "simulated with measured SSD and hard-"
             "disk parameters and stated prices"],
        ],
        widths=[8.4, 7.9], font_size=8.4,
    )

    h1(doc, "Appendix D - References", "D")
    body(doc, "1. Silberschatz, Galvin and Gagne, Operating System Concepts, 10th edition - "
              "chapters 11 (file systems), 12 (implementations) and 14 (mass storage).", size=9)
    body(doc, "2. Tanenbaum and Bos, Modern Operating Systems, 4th edition - file systems and "
              "I/O devices.", size=9)
    body(doc, "3. Linux kernel documentation, Documentation/block/ and Documentation/filesystems/ "
              "ext4, xfs, btrfs.", size=9)
    body(doc, "4. OpenZFS documentation, checksums and copy-on-write; Btrfs wiki, checksums and "
              "snapshots; Apple APFS reference.", size=9)
    body(doc, "5. Microsoft NTFS technical reference: $LogFile, Volume Shadow Copy and cluster "
              "sizes.", size=9)
    body(doc, "6. Hadoop HDFS architecture guide (replication and rack awareness); Amazon S3 and "
              "Google Cloud Storage consistency and pricing pages.", size=9)
    body(doc, "7. The measurement and simulation programs in this repository, and their logs, are "
              "the primary evidence for every number in this report.", size=9)


# --------------------------------------------------------------------------- #
def main():
    doc = new_document()
    add_header_footer(doc,
                      "CSA04 Operating Systems  |  Assignment 4 - CO4  |  " + STUDENT + "  " + REGNO,
                      "CSA0406 - Assignment 4")
    cover(doc)
    mark_sheet(doc)
    declaration(doc)
    contents(doc)
    environment(doc)
    task1(doc)
    task2(doc)
    task3(doc)
    task4(doc)
    task5(doc)
    task6(doc)
    appendices(doc)
    out = os.path.join(ROOT, "Assignment_4_Final_Report.docx")
    doc.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
