# 部署与运维手册

## 一、环境要求

| 项 | 要求 |
|---|---|
| Docker | 20.10+（实测 28.5.1） |
| 宿主内核 | 任意 Linux 内核（本套题**不依赖内核漏洞**，故不受宿主内核版本影响） |
| 磁盘 | 基础镜像约 360 MB，10 题镜像共享层，总计约 **1.6 GB** |
| 内存 | 每题容器常驻约 15 MB；可同时运行多题 |
| 启动方式 | **仅需 `-p 端口:22`**，无需 `--privileged`、无需额外挂载、无需环境变量 |

## 二、一键构建

```bash
cd Linux
bash build_all.sh
```

产出镜像：

| 镜像 | 大小 |
|---|---|
| `priv-base:latest` | ~357 MB |
| `priv-lx01-suid-find:latest` … `priv-lx10-suid-librpath:latest` | 每个 ~357 MB（共享层，增量极小） |

## 三、启动（每题只用镜像名 + 端口）

```bash
docker run -d --name lx01 -p 22001:22 --restart unless-stopped priv-lx01-suid-find:latest
docker run -d --name lx02 -p 22002:22 --restart unless-stopped priv-lx02-sudo-less:latest
docker run -d --name lx03 -p 22003:22 --restart unless-stopped priv-lx03-cron-world:latest
docker run -d --name lx04 -p 22004:22 --restart unless-stopped priv-lx04-path-hijack:latest
docker run -d --name lx05 -p 22005:22 --restart unless-stopped priv-lx05-writable-service:latest
docker run -d --name lx06 -p 22006:22 --restart unless-stopped priv-lx06-capabilities:latest
docker run -d --name lx07 -p 22007:22 --restart unless-stopped priv-lx07-passwd-shadow:latest
docker run -d --name lx08 -p 22008:22 --restart unless-stopped priv-lx08-nfs-nosquash:latest
docker run -d --name lx09 -p 22009:22 --restart unless-stopped priv-lx09-docker-socket:latest
docker run -d --name lx10 -p 22010:22 --restart unless-stopped priv-lx10-suid-librpath:latest
```

学生连接：

```bash
ssh -p 22001 player@<主机IP>
# 密码统一：Player@2026
```

> **每题独立、固定 flag**：每题目录下有一份 `flag.txt`，Dockerfile 在构建时把它
> `COPY` 到 `/flag.txt` 并 `chown root:root && chmod 400`。十题十个值、互不相同；
> 同一题反复构建或起多个容器，值保持一致，评分不需要按实例取 flag。
> 改 flag 只需改题目录里的 `flag.txt` 再重建镜像（建议 `--no-cache`）。
> 注意：flag 会随镜像层进入 `docker save` 的 tar，镜像/tar 发给选手等于直接给 flag。

## 四、flag 规则

| 项 | 说明 |
|---|---|
| 位置 | `/flag.txt`（容器根目录） |
| 权限 | `root:root 0400`，低权用户不可读 |
| 格式 | `Ly_Flag{xxxxxxxx}`（8 位小写字母 + 数字） |
| 写入 | 构建时由题目录 `flag.txt` `COPY` 到 `/flag.txt`，`chown root:root && chmod 400`；十题固定值、互不相同 |
| 判分 | 学生提权后 `cat /flag.txt`，把内容提交到平台 |

## 五、题目清单与验证状态

| # | 镜像 | 提权面 | 唯一解 | 状态 |
|---|---|---|---|---|
| 1 | lx01 | SUID `find` 副本 | `find . -exec /bin/sh -p \; -quit` | ✅ 已实测 |
| 2 | lx02 | `sudo less` | less 内 `!sh` | ✅ 已实测 |
| 3 | lx03 | root cron 脚本组可写 | 追加 `chmod 4755 /bin/bash` | ✅ 已实测 |
| 4 | lx04 | PATH 劫持 | `~/bin/df-helper` 占位 | ✅ 已实测 |
| 5 | lx05 | root 监督脚本组可写 | 追加 python 代码 | ✅ 已实测 |
| 6 | lx06 | `cap_setuid` | `python3 -c 'os.setuid(0)'` | ✅ 已实测 |
| 7 | lx07 | `/etc/passwd` 可写 | 追加 UID=0 账户 | ✅ 已实测 |
| 8 | lx08 | NFS `no_root_squash` + 无 sticky | 替换 `share-check.sh` | ✅ 已实测 |
| 9 | lx09 | `docker.sock` 全局可写 | `-v /:/host` 读 flag | ✅ 已实测（只读端点，无逃逸面） |
| 10 | lx10 | SUID + RPATH 可写 | 替换 `libbackup.so` | ✅ 已实测 |

每题的负向路径（其他提权面）均已实测失败，**每题只有一个解**。

## 六、常见问题

### 1. 第 3/4/5/8 题需要等 1 分钟
这四题依赖 `cron` 每分钟执行 root 任务。容器入口 `project-init.sh` 会在启动时拉起 `cron`。
若学生等不到结果，检查：

```bash
docker exec lx03 pgrep -a cron          # 应有 /usr/sbin/cron
docker exec lx03 tail -5 /var/log/archive.log
```

### 2. 第 8/9 题是"用户态模拟"
为保证"只给端口 + 镜像名"即可启动（无需 `--privileged` / socket 挂载），
这两题用用户态组件模拟了真实行为：

- lx08：`nfsmnt.sh` 模拟 `no_root_squash` 的属主保留语义
- lx09：`dockerd-sim.py` 提供**只读** Docker API（create/start/logs/wait），实现 `-v /:/host` 的读取语义；端点只接受 `/` 作为挂载源、只接受 cat/ls/id/whoami/uname，程序内无 subprocess，不会成为真实逃逸

学生体验与真实环境一致。若需要真实版，见第七节。

### 3. 端口冲突
改 `-p` 左侧数字即可，容器内固定为 22。

### 4. 重建某题
```bash
bash build_all.sh --no-base      # 或 docker build -t priv-lx03-cron-world:latest lx03-cron-world
docker rm -f lx03 && docker run -d --name lx03 -p 22003:22 priv-lx03-cron-world:latest
```

## 七、可选：真实 NFS / 真实 Docker 版

如果实验环境允许更复杂的启动参数：

**真实 NFS（lx08）**
```bash
docker run -d --name lx08 --cap-add SYS_ADMIN --privileged \
  -p 22008:22 -p 2049:2049 priv-lx08-nfs-nosquash:real
```
需要把镜像内的 `nfsmnt.sh` 替换为真正的 `mount -t nfs <server>:/srv/nfs-share /mnt`，
并在容器内运行 `nfs-kernel-server`。默认镜像不含该实现。

**真实 Docker socket（lx09）**
```bash
docker run -d --name lx09 -p 22009:22 \
  -v /var/run/docker.sock:/var/run/docker.sock priv-lx09-docker-socket:real
```
注意：这会让学生**能操作宿主 docker**，必须在隔离的专用实验机上使用。

## 八、清理

```bash
docker rm -f lx01 lx02 lx03 lx04 lx05 lx06 lx07 lx08 lx09 lx10
docker rmi $(docker images --filter reference='priv-*' -q) priv-base:latest
```
