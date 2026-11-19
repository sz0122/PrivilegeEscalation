#!/bin/sh
/usr/sbin/cron
echo "[project-init] cron started: $(pgrep -x cron | tr '\n' ' ')"
