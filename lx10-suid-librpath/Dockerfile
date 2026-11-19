FROM priv-base:latest

# ============================================================
# lx10 - SUID binary + RPATH library hijack
# Story: a SUID root helper "backup-tool" was compiled with
#        -Wl,-rpath,/opt/backup/lib, and that directory is writable by the
#        "ops" group. Replacing libbackup.so => code runs as root.
# Unique privesc surface: /opt/backup/lib (root:ops 2775) + libbackup.so (664)
# ============================================================

RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd && \
    groupadd -r ops && usermod -aG ops player


# ---- 1. build the shared library FIRST so the tool links successfully ----
COPY libbackup.c /tmp/libbackup.c
RUN mkdir -p /opt/backup/lib /opt/backup/bin && \
    gcc -O2 -shared -fPIC -o /opt/backup/lib/libbackup.so /tmp/libbackup.c && \
    rm -f /tmp/libbackup.c

# ---- 2. build the SUID helper against that library ----
COPY backup-tool.c /tmp/backup-tool.c
RUN gcc -O2 -o /opt/backup/bin/backup-tool /tmp/backup-tool.c \
        -L/opt/backup/lib -lbackup -Wl,-rpath,/opt/backup/lib && \
    rm -f /tmp/backup-tool.c && \
    chown root:root /opt/backup/bin/backup-tool && \
    chmod 4755 /opt/backup/bin/backup-tool

# ---- 3. permissions: bin dir read-only, lib dir writable by ops ----
RUN chown root:root /opt/backup/bin && chmod 755 /opt/backup/bin && \
    chown root:ops /opt/backup/lib && chmod 2775 /opt/backup/lib && \
    chown root:ops /opt/backup/lib/libbackup.so && chmod 664 /opt/backup/lib/libbackup.so && \
    ldconfig 2>/dev/null || true

COPY motd /etc/motd

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
