"""Capture genuine console screenshots for Assignment 4.

Each shot is a real bash session: the script is written to disk, run inside a
real console window, and the window is photographed with PrintWindow().
Nothing in the images is drawn or edited afterwards.
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.abspath(os.path.join(HERE, ".."))
SHOTS = os.path.join(WORK, "shots")
SCRIPTS = os.path.join(SHOTS, "scripts")
CAPTURE = os.path.abspath(os.path.join(WORK, "..", "work", "build", "capture_terminal.ps1"))
MSYS = "/d/FREEBUFF/tools/msys64/usr/bin"

HEAD = f"""
export PATH="{MSYS}:$PATH"
cd "{WORK.replace(chr(92), '/')}"
"""

SHOTS_DEF = {
    "q2_alloc": ("""
set -x
./bin/q2_alloc.exe
set +x
""", 6, 12),

    "q2_compare": ("""
set -x
./bin/q2_compare.exe
set +x
""", 8, 30),

    "q1_growth": ("""
set -x
./bin/q1_growth.exe
set +x
""", 8, 28),

    "q2_freespace": ("""
set -x
./bin/q2_freespace.exe
set +x
""", 8, 34),

    "q3_meta": ("""
set -x
./bin/q3_meta.exe
set +x
""", 14, 16),

    "q3_checksum": ("""
set -x
./bin/q3_checksum.exe
set +x
""", 8, 24),

    "q4_sched": ("""
set -x
./bin/q4_sched.exe
set +x
""", 7, 10),

    "q4_all": ("""
set -x
./bin/q4_all.exe
set +x
""", 8, 40),

    "q4_starve": ("""
set -x
./bin/q4_starve.exe
set +x
""", 7, 18),

    "q5_cache": ("""
set -x
./bin/q5_cache.exe
set +x
""", 16, 18),

    "q5_replica": ("""
set -x
./bin/q5_replica.exe
set +x
""", 8, 26),

    "q6_sim": ("""
set -x
./bin/q6_sim.exe 250 2500
set +x
""", 8, 32),
}


def main(only=None):
    os.makedirs(SCRIPTS, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    names = [only] if only else list(SHOTS_DEF)
    for name in names:
        body, wait, lines = SHOTS_DEF[name]
        script = os.path.join(SCRIPTS, f"{name}.sh")
        with open(script, "w", newline="\n") as f:
            f.write(HEAD + body)
        out = os.path.join(SHOTS, f"{name}.png")
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", CAPTURE,
            "-Title", f"SHOT-{name}",
            "-Script", posix(script),
            "-OutPath", out,
            "-WaitSeconds", str(wait),
            "-Cols", "126",
            "-Lines", str(lines),
        ]
        print(f"capturing {name} ...", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip()[:300])
        if not os.path.exists(out):
            print(f"  WARNING: {name} produced no image")
    print("done")


def posix(path: str) -> str:
    """C:\\a\\b -> /c/a/b, the form bash -l can open."""
    p = os.path.abspath(path).replace("\\", "/")
    if len(p) > 1 and p[1] == ":":
        p = "/" + p[0].lower() + p[2:]
    return p


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
