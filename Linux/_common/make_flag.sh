#!/bin/sh
# 运行时生成 Ly_Flag{8位小写字母+数字}，写入 /flag.txt 并设为 root:root 0400
# 已存在则直接退出（幂等，容器重启不会换 flag）；不打印 flag 值，避免日志泄漏
set -eu

if [ -s /flag.txt ]; then
    exit 0
fi

alphabet='abcdefghijklmnopqrstuvwxyz0123456789'
suffix=''
i=0
while [ "$i" -lt 8 ]; do
    # 从 /dev/urandom 取一个字节，取模得到索引
    n=$(od -An -N1 -tu1 /dev/urandom | tr -d ' ')
    idx=$((n % 36))
    ch=$(printf '%s' "$alphabet" | cut -c$((idx + 1)))
    suffix="${suffix}${ch}"
    i=$((i + 1))
done

printf 'Ly_Flag{%s}\n' "$suffix" > /flag.txt
chown root:root /flag.txt
chmod 0400 /flag.txt
echo "[make_flag] /flag.txt created (value not logged)"
