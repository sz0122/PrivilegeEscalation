# 第 2 题：sudo 里给人留的门缝

## 场景

你是运维实习生，导师给你配了“**只读看应用日志**”的权限，让你查 `/var/log/app/` 里的慢查询告警。
你登进了 `player` 账户。

## 目标

拿到 root 权限，读取 `/flag.txt`：

```bash
cat /flag.txt
```

## 登录

```bash
ssh -p 22002 player@<主机IP>
# 密码：Player@2026
```

## 提拉提示

1. 拿到 shell 第一件事——我到底能 sudo 什么？
   ```bash
   sudo -l
   ```
2. 注意 `/etc/sudoers.d/` 下有 **两个** 文件，哪一个是给 `player` 的？
   ```bash
   ls -l /etc/sudoers.d/
   cat /etc/sudoers.d/90-readlogs
   ```
3. 你被允许运行的命令真的“只是看文件”吗？想想它是个什么类型的程序：
   - 它是分页器（pager），运行中还能执行命令
4. 在 `less` 里按 `:` 或 `!` 试试——它能不能执行 shell？
5. 如果不习惯 `less`，去 GTFOBins 查 `less` 的“Shell”一节。

## 评分

成功 `cat /flag.txt` 得到 `Ly_Flag{...}` 即为通过。
