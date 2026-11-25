#!/usr/bin/env bash
# q4_sched_sys.sh - Task 4.4: which scheduler does this disk use?
#
# On Linux the answer is in /sys/block/<disk>/queue/scheduler.  This machine
# runs Windows, where /sys does not exist, so the Linux command is attempted
# (and its failure is recorded) and the real device is then described with the
# Windows storage tools, which show what kind of disk it is and therefore
# whether a seek-reordering scheduler is useful at all.
export PATH="/d/FREEBUFF/tools/msys64/usr/bin:$PATH"
cd "$(dirname "$0")/.." || exit 1

echo "== ls /sys/block =="
ls /sys/block 2>&1 | head -5
echo "exit status: $?"
echo
echo "== the Linux scheduler file =="
for d in /sys/block/*/queue/scheduler; do
    echo "$d: $(cat "$d" 2>&1)"
done 2>&1 | head -5
echo "exit status: $?"
echo
echo "== lsblk =="
lsblk 2>&1 | head -5
echo "exit status: $?"
echo
echo "== df -T . =="
df -T . 2>&1
echo
echo "== the real device of this machine (Windows) =="
powershell -NoProfile -Command "Get-PhysicalDisk | Select-Object FriendlyName,MediaType,BusType,@{n='SizeGB';e={[math]::Round(\$_.Size/1GB,0)}} | Format-Table -AutoSize"
echo "== Get-Disk =="
powershell -NoProfile -Command "Get-Disk | Select-Object Number,FriendlyName,PartitionStyle,BusType,@{n='SizeGB';e={[math]::Round(\$_.Size/1GB,0)}} | Format-Table -AutoSize"
echo "== write caching setting of the system disk =="
powershell -NoProfile -Command "Get-Disk | Where-Object {\$_.IsSystem} | Select-Object Number,FriendlyName,IsBoot,IsSystem | Format-Table -AutoSize"
