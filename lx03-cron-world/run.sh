#!/bin/bash
# Archive job - runs as root every minute from /etc/cron.d/archive
# Collects uploads into a tarball and cleans stale temp files.
set -u

LOG=/var/log/archive.log
echo "[$(date '+%F %T')] archive job start" >> "$LOG"

# 1. Pack the upload directory as a whole (quoted: no glob injection here)
tar -czf /backup/uploads.tar.gz /srv/uploads 2>/dev/null

# 2. Clean temp files older than 7 days (quoted: no glob injection here)
find /tmp -maxdepth 1 -type f -mtime +7 -delete 2>/dev/null

echo "[$(date '+%F %T')] archive job done" >> "$LOG"
