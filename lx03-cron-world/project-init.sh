#!/bin/sh
# Start the cron daemon in the background (the container has no systemd)
set -eu
mkdir -p /var/run/crond
/usr/sbin/cron
echo "[project-init] cron started: $(pgrep -x cron | tr '\n' ' ')"
