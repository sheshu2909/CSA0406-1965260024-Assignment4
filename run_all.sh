#!/usr/bin/env bash
# run_all.sh - build and execute every Assignment 4 program and keep the
# output as evidence.  Run from work4/ with the MSYS2 toolchain on PATH.
set -u
export PATH="/d/FREEBUFF/tools/msys64/usr/bin:$PATH"

cd "$(dirname "$0")" || exit 1
mkdir -p logs bin tmp

say() { echo "== $* =="; }

say "toolchain"
{
  echo "# gcc version"
  gcc --version | head -1
  echo "# platform"
  uname -a
  echo "# shell"
  bash --version | head -1
} > logs/q0_environment.log 2>&1

say "building"
{
  for f in src/*.c; do
    echo "\$ gcc -std=c11 -Wall -Wextra -O2 $f -o bin/$(basename "${f%.c}").exe"
    gcc -std=c11 -Wall -Wextra -O2 "$f" -o "bin/$(basename "${f%.c}").exe" || echo "BUILD FAILED: $f"
  done
  echo "# the two programs of the assignment sheet are also built without -O2"
  echo "\$ gcc -std=c11 -Wall -Wextra src/q2_alloc.c -o bin/q2_alloc.exe"
  gcc -std=c11 -Wall -Wextra src/q2_alloc.c -o bin/q2_alloc.exe
  echo "\$ gcc -std=c11 -Wall -Wextra src/q4_sched.c -o bin/q4_sched.exe"
  gcc -std=c11 -Wall -Wextra src/q4_sched.c -o bin/q4_sched.exe
} > logs/q0_build.log 2>&1

say "Task 1"
{ echo "# q1_dirsearch"; ./bin/q1_dirsearch.exe; } > logs/q1_dirsearch.log 2>&1
{ echo "# q1_growth";     ./bin/q1_growth.exe; }    > logs/q1_growth.log 2>&1

say "Task 2"
{ echo "# q2_alloc (required program)"; ./bin/q2_alloc.exe; } > logs/q2_alloc.log 2>&1
{ echo "# q2_alloc_demo"; ./bin/q2_alloc_demo.exe; }        > logs/q2_alloc_demo.log 2>&1
{ echo "# q2_compare";    ./bin/q2_compare.exe; }           > logs/q2_compare.log 2>&1
{ echo "# q2_inode";      ./bin/q2_inode.exe; }             > logs/q2_inode.log 2>&1
{ echo "# q2_freespace";  ./bin/q2_freespace.exe; }         > logs/q2_freespace.log 2>&1

say "Task 3"
{ echo "# q3_meta";     ./bin/q3_meta.exe; }     > logs/q3_meta.log 2>&1
{ echo "# q3_checksum"; ./bin/q3_checksum.exe; } > logs/q3_checksum.log 2>&1
{ echo "# q3_inspect";  bash src/q3_inspect.sh; } > logs/q3_inspect.log 2>&1

say "Task 4"
{ echo "# q4_sched (required program)"; ./bin/q4_sched.exe; } > logs/q4_sched.log 2>&1
{ echo "# q4_all";    ./bin/q4_all.exe; }    > logs/q4_all.log 2>&1
{ echo "# q4_starve"; ./bin/q4_starve.exe; } > logs/q4_starve.log 2>&1
{ echo "# q4_sched_sys"; bash src/q4_sched_sys.sh; } > logs/q4_sched_sys.log 2>&1

say "Task 5"
{ echo "# q5_cache";   ./bin/q5_cache.exe; }   > logs/q5_cache.log 2>&1
{ echo "# q5_replica"; ./bin/q5_replica.exe; } > logs/q5_replica.log 2>&1

say "Task 6"
{ echo "# q6_design";  ./bin/q6_design.exe; }  > logs/q6_design.log 2>&1
{ echo "# q6_measure"; ./bin/q6_measure.exe; } > logs/q6_measure.log 2>&1
# The measured random reads are served from the file cache (a few us), so
# they are the best case, not a device latency.  The simulator is given a
# conservative 0.25 ms for the SSD tier and the measured sequential rate.
SSD_US=250
SEQ=$(grep -o 'sequential read *:.*MB/s' logs/q6_measure.log | grep -o '[0-9.]* MB/s' | head -1 | cut -d' ' -f1)
SEQ=${SEQ:-3000}
{ echo "# q6_sim $SSD_US $SEQ"; ./bin/q6_sim.exe "$SSD_US" "$SEQ"; } > logs/q6_sim.log 2>&1

say "done"
ls -1 logs | wc -l
rm -f tmp/q3_*.dat
