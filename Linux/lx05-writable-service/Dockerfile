FROM priv-base:latest

# ============================================================
# lx05 - Writable service script: root re-runs a file you can edit
# Unique privesc surface: /opt/monitor/supervisor.py  (root:web, group writable)
#                         launched by root every minute by cron
# ============================================================

RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd && \
    groupadd -r web && \
    usermod -aG web player


# ---- The monitored app (runs as www-data in real life; here it is just data) ----
RUN mkdir -p /opt/monitor /var/log/monitor && \
    printf 'import time\nprint("worker tick")\n' > /opt/monitor/app.py && \
    chown root:root /opt/monitor/app.py && chmod 644 /opt/monitor/app.py

# ---- The supervisor that root runs: group-writable -> the privesc surface ----
COPY supervisor.py /opt/monitor/supervisor.py
RUN chown root:web /opt/monitor/supervisor.py && \
    chmod 664 /opt/monitor/supervisor.py && \
    chown root:root /opt/monitor && chmod 755 /opt/monitor && \
    chown root:root /var/log/monitor && chmod 755 /var/log/monitor

COPY monitor.cron /etc/cron.d/monitor
RUN chown root:root /etc/cron.d/monitor && chmod 644 /etc/cron.d/monitor

COPY project-init.sh /usr/local/sbin/project-init.sh
RUN chmod 755 /usr/local/sbin/project-init.sh

COPY motd /etc/motd

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
