FROM priv-base:latest

# ============================================================
# lx01 - SUID: file search gives you root
# Unique privesc surface: /usr/local/bin/find is a SUID root copy
# ============================================================

# Low-privilege account player (SSH password login)
RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd

# Generate flag

# ---- Privesc surface: SUID copy of find left behind by ops ----
# chown MUST come before chmod, otherwise chown clears the SUID bit
RUN cp /usr/bin/find /usr/local/bin/find && \
    chown root:root /usr/local/bin/find && \
    chmod 4755 /usr/local/bin/find && \
    touch -d '2024-03-11 02:14:00' /usr/local/bin/find

# ---- Distractor: an SUID shell script (kernel ignores setuid on scripts) ----
COPY healthcheck /usr/local/bin/healthcheck
RUN chown root:root /usr/local/bin/healthcheck && \
    chmod 4755 /usr/local/bin/healthcheck

# ---- Scenario material ----
RUN mkdir -p /srv/www/uploads /var/log/app && \
    printf 'user=web last_login=2024-03-10\n' > /srv/www/uploads/access.log && \
    printf '[2024-03-11] upload index.html ok\n' > /var/log/app/app.log

# Login banner (ASCII only: the issue container has no UTF-8 locale for login shells)
COPY motd /etc/motd

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
