#!/bin/bash
# Disk usage report - runs as root every minute
# NOTE: the helper is invoked by bare name on purpose (that is the lesson).
set -u

export PATH=/home/player/bin:/usr/local/lib:/usr/local/bin:/usr/bin:/bin

OUT=/var/reports/disk-$(date +%Y%m%d-%H%M).txt
{
  echo "=== disk usage report $(date '+%F %T') ==="
  df-helper
} > "$OUT" 2>&1

# keep only the last 20 reports
ls -1t /var/reports/disk-*.txt 2>/dev/null | tail -n +21 | xargs -r rm -f
