FROM priv-base:latest

# ============================================================
# lx07 - /etc/passwd is group-writable -> append a UID 0 account
# Unique privesc surface: /etc/passwd  root:player 0664
# ============================================================

RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd


# ---- Privesc surface: a "permission batch fix" made passwd group-writable ----
RUN chown root:player /etc/passwd && chmod 664 /etc/passwd && \
    ls -l /etc/passwd /etc/shadow

# ---- Distractors / scenario noise ----
# shadow stays 640 root:shadow; player is NOT in shadow group -> no hash leak
RUN chown root:shadow /etc/shadow && chmod 640 /etc/shadow
# a commented-out old backup of passwd that is useless (no hash inside)
RUN printf '# backup taken 2021: see /var/backups\n' > /var/backups.passwd.txt 2>/dev/null || \
    mkdir -p /var/backups && printf '# backup taken 2021: see /var/backups\n' > /var/backups/passwd.old

COPY motd /etc/motd

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
