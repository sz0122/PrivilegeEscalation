FROM priv-base:latest

# ============================================================
# lx02 - sudo: a "read-only" log view is still a root shell
# Unique privesc surface: sudo NOPASSWD /usr/bin/less on one layer of /var/log/app
# ============================================================

RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd


# ---- Application logs the intern is allowed to read ----
RUN mkdir -p /var/log/app && \
    printf '[2024-03-11 09:00:01] app started\n[2024-03-11 09:01:12] db connect ok\n[2024-03-11 09:05:40] WARN slow query 1.2s\n' \
        > /var/log/app/app.log && \
    printf '[2024-03-10 23:59:59] rotation\n' > /var/log/app/app.log.1 && \
    chown -R root:root /var/log/app && chmod 750 /var/log/app && chmod 640 /var/log/app/*

# ---- sudo grant: ONLY less on the app log directory ----
# No tar/find/awk/vi grants -> the less pager is the single escape hatch.
# Args use an anchored regex, NOT a bare "*": sudo's fnmatch lets "*" swallow
# "/" and spaces, which allowed "less /var/log/app/../../../flag.txt" and
# "less /var/log/app/app.log /etc/shadow". The regex only admits a single
# filename under /var/log/app (no slash, no "..", no extra args).
RUN printf 'player ALL=(root) NOPASSWD: /usr/bin/less ^/var/log/app/[A-Za-z0-9._-]+$\n' \
        > /etc/sudoers.d/90-readlogs && \
    chown root:root /etc/sudoers.d/90-readlogs && \
    chmod 440 /etc/sudoers.d/90-readlogs && \
    visudo -c -f /etc/sudoers.d/90-readlogs

# ---- Distractor: a second sudoers file that looks suspicious but is NOT player's ----
RUN printf 'web ALL=(root) NOPASSWD: /usr/bin/tar -czf /tmp/* /var/log/app/\n' \
        > /etc/sudoers.d/91-archive && \
    chown root:root /etc/sudoers.d/91-archive && \
    chmod 440 /etc/sudoers.d/91-archive && \
    useradd -r -s /usr/sbin/nologin web

COPY motd /etc/motd

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
