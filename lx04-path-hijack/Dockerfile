FROM priv-base:latest

# ============================================================
# lx04 - PATH hijack: a root job runs a command by bare name
# Unique privesc surface: /etc/cron.d/disk-report -> disk-report.sh runs "df-helper"
#                         with PATH=/home/player/bin first
# ============================================================

RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd && \
    mkdir -p /home/player/bin && \
    chown player:player /home/player/bin


# ---- The root job script ----
COPY disk-report.sh /usr/local/bin/disk-report.sh
RUN chown root:root /usr/local/bin/disk-report.sh && chmod 755 /usr/local/bin/disk-report.sh

# ---- Real helper lives in a root-only dir, but the job calls it by bare name ----
COPY df-helper /usr/local/lib/df-helper.real
RUN chown root:root /usr/local/lib/df-helper.real && chmod 755 /usr/local/lib/df-helper.real
# the name the job expects, resolvable via the second PATH entry (dir is root-owned, not writable)
RUN ln -s /usr/local/lib/df-helper.real /usr/local/lib/df-helper && \
    chown -h root:root /usr/local/lib/df-helper

COPY disk-report.cron /etc/cron.d/disk-report
RUN chown root:root /etc/cron.d/disk-report && chmod 644 /etc/cron.d/disk-report

# ---- Generate the report dir ----
RUN mkdir -p /var/reports && chown root:root /var/reports

COPY project-init.sh /usr/local/sbin/project-init.sh
RUN chmod 755 /usr/local/sbin/project-init.sh

COPY motd /etc/motd

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
