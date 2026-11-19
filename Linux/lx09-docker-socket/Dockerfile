FROM priv-base:latest

# ============================================================
# lx09 - Docker socket exposed (read-only API endpoint)
# Unique privesc surface: /var/run/docker.sock is world-writable and a
#   Docker API endpoint is listening on it.
# Solution = create a "container" with a bind of the host root, then cat
#   the flag through that bind.
# Safety: the endpoint only serves a read-only host root view; it never
#   executes anything (no subprocess at all), so it is not a real escape.
# flag: NOT baked into the image - entrypoint generates it at first start
#   and project-init copies it into the host root view.
# ============================================================

RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd

# ---- Install the API endpoint ----
COPY dockerd-sim.py /usr/local/sbin/dockerd-sim.py
RUN chmod 755 /usr/local/sbin/dockerd-sim.py

# ---- Prepare the READ-ONLY host-root view (populated at runtime) ----
# Only the daemon (root) can read this tree; the flag copy is injected by
# project-init.sh after entrypoint.sh has generated /flag.txt.
RUN groupadd -r docker && \
    mkdir -p /var/lib/dockersim/hostroot/etc /var/lib/dockersim/hostroot/root && \
    cp -a /etc/passwd /var/lib/dockersim/hostroot/etc/passwd && \
    printf 'host root view served by the docker API endpoint\n' > /var/lib/dockersim/hostroot/README && \
    chown -R root:root /var/lib/dockersim && chmod 700 /var/lib/dockersim

# ---- Runtime init: inject flag into the view, start the endpoint ----
COPY project-init.sh /usr/local/sbin/project-init.sh
RUN chmod 755 /usr/local/sbin/project-init.sh

COPY motd /etc/motd

EXPOSE 22

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
