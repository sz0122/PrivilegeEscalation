#!/bin/bash
# share-check.sh - runs every minute as root, FROM INSIDE the NFS export.
# It lives on the share, and the share is group-writable without a sticky bit.
set -u
LOG=/var/log/share-check.log
echo "[$(date '+%F %T')] share-check running as $(id -un) on $(hostname)" >> "$LOG"

if [ -d /srv/nfs-share ]; then
    echo "[$(date '+%F %T')] export reachable, $(ls -1A /srv/nfs-share | wc -l) entries" >> "$LOG"
fi
