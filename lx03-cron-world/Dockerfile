FROM priv-base:latest

# ============================================================
# lx03 - cron: a root cron job runs a world-writable script
# Unique privesc surface: /opt/archive/run.sh (root cron, group-writable to web)
# ============================================================

RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd && \
    groupadd -r web && \
    usermod -aG web player


# ---- The archive job: root runs it every minute ----
# 775: executable (cron needs +x) AND group-writable (the privesc surface)
COPY run.sh /opt/archive/run.sh
RUN chown root:web /opt/archive/run.sh && \
    chmod 775 /opt/archive/run.sh && \
    chmod 755 /opt /opt/archive && \
    chown root:root /opt /opt/archive

COPY archive.cron /etc/cron.d/archive
RUN chown root:root /etc/cron.d/archive && chmod 644 /etc/cron.d/archive

# ---- Upload directory (player can write here: scenario noise) ----
RUN mkdir -p /srv/uploads /backup && \
    printf 'report-0310.pdf\n' > /srv/uploads/report-0310.pdf && \
    chown root:root /srv/uploads /backup && chmod 1777 /srv/uploads

# ---- Start cron in background from the common entrypoint hook ----
COPY project-init.sh /usr/local/sbin/project-init.sh
RUN chmod 755 /usr/local/sbin/project-init.sh

COPY motd /etc/motd

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
