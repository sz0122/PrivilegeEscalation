# 第 1 题：SUID 的“老实人”

## 场景

你登录到了一台 Web 运维工作站的低权账户 `player`。运维同事说昨天有人把网站
根目录 `/srv/www` 搞乱了，但你只能看，不能改——你手上没有 root 权限。

站长的排查工具最近还在用，其中有一个专门用来“找文件”的小工具，是 root 放的。

## 目标

拿到 root 权限，读取 `/flag.txt` 并提交：

```bash
cat /flag.txt
```

## 登录

```bash
ssh -p 22001 player@<主机IP>
# 密码：Player@2026
```

## 提示（由易到难，卡住再看）

1. 有没有哪个程序跑起来时身份不是你？
   ```bash
   id
   ls -l /usr/local/bin/
   ```
2. 全盘找一找“非常规”的特殊权限文件：
   ```bash
   find / -perm -4000 -type f 2>/dev/null
   ```
3. 对比一下，哪些是系统自带的、哪些是后来放上去的？看看修改时间：
   ```bash
   ls -la /usr/local/bin/
   dpkg -V 2>/dev/null | head
   ```
4. 你会用这个工具本身吗？它支持在执行时“顺带跑一条命令”：
   ```bash
   find . -exec 命令 \;
   ```
5. 注意：用 `sh`/`bash` 起 shell 时要加 `-p`，否则 shell 会**主动**丢弃
   root 身份（安全机制）。去掉 `-p` 试试看 `id` 变成什么了。

## 评分

成功 `cat /flag.txt` 得到 `Ly_Flag{...}` 即为通过。
