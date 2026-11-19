#!/bin/bash
# ============================================================
# build_all.sh - 一键构建 提权 Linux 10 题的全部镜像
#
#   bash build_all.sh            # 构建基础镜像 + 10 道题
#   bash build_all.sh --no-base  # 只重建题目（基础镜像已存在时）
# ============================================================
set -euo pipefail

cd "$(dirname "$0")"
LAB="$(pwd)"
DO_BASE=1
[ "${1:-}" = "--no-base" ] && DO_BASE=0

if [ "$DO_BASE" = "1" ]; then
    echo "########## [1/2] building priv-base ##########"
    docker build -t priv-base:latest -f _common/Dockerfile.base _common
fi

TASKS="lx01-suid-find lx02-sudo-less lx03-cron-world lx04-path-hijack lx05-writable-service \
       lx06-capabilities lx07-passwd-shadow lx08-nfs-nosquash lx09-docker-socket lx10-suid-librpath"

echo "########## [2/2] building 10 challenge images ##########"
i=0
for d in $TASKS; do
    i=$((i + 1))
    num=$(printf '%02d' "$i")
    img="priv-${d}:latest"
    echo "--- [$num/10] $img"
    docker build -t "$img" "$LAB/$d"
done

echo
echo "########## DONE ##########"
docker images --filter reference='priv-*' --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}'
echo
echo "Next: see deploy.md for start commands."
