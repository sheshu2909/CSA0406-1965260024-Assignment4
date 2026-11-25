#!/usr/bin/env bash
# q3_inspect.sh - Task 3.4: inspect a real file system.
#
# The commands asked for by the assignment are stat, df -i, ls -i and
# tune2fs -l / dumpe2fs -h.  This machine runs Windows, so the MSYS2 shell
# can show inodes, block size and free space for the mounted file system, but
# there is no ext4 device for tune2fs to read.  The Windows tools are run as
# well so that the real file system of the machine is documented too.
export PATH="/d/FREEBUFF/tools/msys64/usr/bin:$PATH"
cd "$(dirname "$0")/.." || exit 1

echo "== uname -a =="
uname -a
echo
echo "== stat src/q3_meta.c =="
stat src/q3_meta.c
echo
echo "== stat -f . (file-system type, block size, free blocks) =="
stat -f .
echo
echo "== df -i . (inodes) =="
df -i .
echo
echo "== df -h . (space) =="
df -h .
echo
echo "== ls -i src | head -8 (inode numbers) =="
ls -i src | head -8
echo
echo "== tune2fs -l /dev/sda1 =="
tune2fs -l /dev/sda1 > /tmp/tune2fs.out 2>&1
status=$?
head -4 /tmp/tune2fs.out
echo "tune2fs exit status: $status"
echo
echo "== dumpe2fs -h /dev/sda1 =="
dumpe2fs -h /dev/sda1 > /tmp/dumpe2fs.out 2>&1
status=$?
head -4 /tmp/dumpe2fs.out
echo "dumpe2fs exit status: $status"
echo
echo "== ext4 tools available here =="
command -v tune2fs dumpe2fs mkfs.ext4 2>&1
echo
echo "== the real file system of this machine (Windows) =="
powershell -NoProfile -Command "Get-Volume | Where-Object {\$_.DriveLetter} | Select-Object DriveLetter,FileSystemLabel,FileSystem,AllocationUnitSize,@{n='SizeGB';e={[math]::Round(\$_.Size/1GB,1)}},@{n='FreeGB';e={[math]::Round(\$_.SizeRemaining/1GB,1)}} | Format-Table -AutoSize"
echo "== fsutil fsinfo volumeinfo C: =="
fsutil fsinfo volumeinfo C: 2>&1 | head -12
