FROM priv-base:latest

# ============================================================
# lx06 - Capabilities: the "hidden SUID"
# Unique privesc surface: /usr/bin/python3.12 has cap_setuid+ep
# (python3 is a symlink -> setcap must target the real binary)
# ============================================================

RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd


# ---- Privesc surface: python3 got cap_setuid+ep from a "convenience" install step ----
# find -perm -4000 will NOT show this, only getcap will.
RUN setcap cap_setuid+ep "$(readlink -f /usr/bin/python3)" && \
    getcap "$(readlink -f /usr/bin/python3)" > /opt/install-note.txt && \
    printf 'install: setcap cap_setuid+ep %s\n' "$(readlink -f /usr/bin/python3)" >> /opt/install-note.txt && \
    chmod 644 /opt/install-note.txt

# ---- Distractor: a normal diagnostic tool (not SUID, no caps) ----
RUN printf '#!/bin/sh\necho "probe: all services reachable"\n' > /usr/local/bin/probe && \
    chown root:root /usr/local/bin/probe && chmod 755 /usr/local/bin/probe

# ---- Scenario noise ----
RUN mkdir -p /srv/app && printf 'v=1.4.2\n' > /srv/app/version

COPY motd /etc/motd

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
