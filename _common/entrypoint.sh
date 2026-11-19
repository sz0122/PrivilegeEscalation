#!/bin/sh
# 通用入口：首次启动时生成 /flag.txt（每个容器实例唯一），然后启动 sshd
set -eu

# ---- flag：运行时生成，构建期不再生成，避免层缓存导致多题共用同一 flag ----
if [ ! -s /flag.txt ]; then
    if ! /usr/local/sbin/make_flag.sh >/dev/null 2>&1; then
        echo "[entrypoint] flag generation failed" >&2
    fi
fi

# 允许各题追加自己的启动逻辑
if [ -x /usr/local/sbin/project-init.sh ]; then
    /usr/local/sbin/project-init.sh || echo "[entrypoint] project-init failed, continuing" >&2
fi

mkdir -p /run/sshd
chmod 755 /run/sshd

exec /usr/sbin/sshd -D -e
