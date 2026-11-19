#!/bin/bash
# nfsmnt.sh - user-space NFS "mount" helper for the no_root_squash export.
# Runs as root from the cron job, right before the health check.
#
# With no_root_squash the server does NOT map a client's root to nobody,
# so files the client root writes arrive on the export with root ownership.
# We emulate the client mount by syncing /var/nfs/client back into the share
# while PRESERVING ownership (cp -a), which is exactly the no_root_squash effect.
#
# Copy the ENTRIES, never "client/." : the latter would also copy the client
# directory's own mode/owner onto the share and silently reset its 0775 root:nfs.
set -u
SHARE=/srv/nfs-share
CLIENT=/var/nfs/client

mkdir -p "$CLIENT"
find "$CLIENT" -mindepth 1 -maxdepth 1 -print0 2>/dev/null | \
    xargs -0 -r cp -a -t "$SHARE" 2>/dev/null || true

# marker the health check expects
touch "$SHARE/.mounted"
