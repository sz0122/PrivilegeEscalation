#!/bin/sh
# lx09 runtime init:
#   1) copy the runtime-generated /flag.txt into the read-only host root view
#   2) start the read-only Docker API endpoint on /var/run/docker.sock
# Runs as root (called by the common entrypoint after flag generation).
set -u

# ---- flag copy: runtime only, never baked into the image layers ----
if [ -s /flag.txt ]; then
    mkdir -p /var/lib/dockersim/hostroot
    install -o root -g root -m 0400 /flag.txt /var/lib/dockersim/hostroot/flag.txt
else
    echo "[project-init] /flag.txt missing, host root view has no flag" >&2
fi
chown -R root:root /var/lib/dockersim
chmod 700 /var/lib/dockersim

# ---- start the endpoint ----
nohup /usr/bin/python3 /usr/local/sbin/dockerd-sim.py > /var/log/dockerd-sim.log 2>&1 &
sleep 1
if [ -S /var/run/docker.sock ]; then
    chmod 666 /var/run/docker.sock
    ls -l /var/run/docker.sock
else
    echo "[project-init] socket not ready" >&2
    cat /var/log/dockerd-sim.log >&2
fi
