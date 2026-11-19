FROM priv-base:latest

# ============================================================
# lx08 - NFS export without root_squash (user-space simulation)
# Story: /srv/nfs-share is exported with no_root_squash. A root job
#        "mounts" the share every minute and then runs /srv/nfs-share/share-check.sh
#        DIRECTLY FROM THE SHARE. Because the export has no sticky bit and is
#        group-writable to "nfs", a share member can replace that script.
# Unique privesc surface: replacing /srv/nfs-share/share-check.sh
# ============================================================

RUN useradd -m -s /bin/bash player && \
    echo 'player:Player@2026' | chpasswd && \
    groupadd -r nfs && usermod -aG nfs player


# ---- The export directory ----
# 0775 root:nfs (group writable) and NO sticky bit: this is what makes
# replacing files possible. A sticky bit would block it, which is normal for /tmp
# but NOT normal for an NFS export used by a team.
RUN mkdir -p /srv/nfs-share /etc/exports.d /var/nfs/client && \
    chown root:nfs /srv/nfs-share && chmod 0775 /srv/nfs-share && \
    printf '/srv/nfs-share 192.168.0.0/16(rw,sync,no_root_squash,insecure)\n' > /etc/exports && \
    printf '/srv/nfs-share 192.168.0.0/16(rw,sync,no_root_squash,insecure)\n' > /etc/exports.d/share.exports

# ---- Root job: "mounts" (syncs) the share, then runs the check script FROM it ----
COPY nfsmnt.sh /usr/local/sbin/nfsmnt.sh
RUN chmod 755 /usr/local/sbin/nfsmnt.sh

COPY share-check.sh /srv/nfs-share/share-check.sh
RUN chown root:root /srv/nfs-share/share-check.sh && chmod 755 /srv/nfs-share/share-check.sh

COPY share.cron /etc/cron.d/share
RUN chown root:root /etc/cron.d/share && chmod 644 /etc/cron.d/share

COPY project-init.sh /usr/local/sbin/project-init.sh
RUN chmod 755 /usr/local/sbin/project-init.sh

COPY motd /etc/motd

# ---- flag：本题目固定值（flag.txt），构建时写入 /flag.txt，root 0400 ----
COPY flag.txt /flag.txt
RUN chown root:root /flag.txt && chmod 400 /flag.txt
