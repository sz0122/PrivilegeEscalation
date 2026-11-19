# 提权 · Linux 10 题 Docker 工程

每道题一个独立的 Docker 镜像，一题一种提权方式。学生用 SSH 连入低权账户，通过
唯一的提权路径拿到 root，读取 `/flag.txt`。

## 统一约定

| 项 | 约定 |
|---|---|
| flag | `/flag.txt`，root:root 0400，格式 `Ly_Flag{xxxxxxxx}`（8 位小写字母/数字），构建镜像时随机生成 |
| 登录 | `ssh -p <端口> player@<host>`，密码写在每题 README |
| 判分 | 学生用提权后的 root 执行 `cat /flag.txt`，把内容提交到平台 |
| 启动 | `docker run -d --name <名字> -p <端口>:22 <镜像名>`，**只需端口 + 镜像名** |
| 唯一解 | 每题只保留一个可利用的提权面，其余均为“看似危险但不可利用”的干扰项 |

## 镜像与端口

| # | 镜像 | 题目 | 端口 | 提权面 |
|---|---|---|---|---|
| 1 | `priv-lx01-suid-find:latest` | SUID 的 find | 22001 | SUID 二进制滥用 |
| 2 | `priv-lx02-sudo-less:latest` | sudo 受限命令逃逸 | 22002 | sudo 配置错误 |
| 3 | `priv-lx03-cron-world:latest` | root cron 脚本可写 | 22003 | 计划任务 |
| 4 | `priv-lx04-path-hijack:latest` | PATH 劫持 | 22004 | 相对路径 + PATH |
| 5 | `priv-lx05-writable-service:latest` | root 监督脚本可写 | 22005 | 服务配置错误 |
| 6 | `priv-lx06-capabilities:latest` | 文件 capabilities | 22006 | cap_setuid |
| 7 | `priv-lx07-passwd-shadow:latest` | /etc/passwd 可写 | 22007 | 关键文件权限 |
| 8 | `priv-lx08-nfs-nosquash:latest` | NFS no_root_squash（用户态模拟） | 22008 | NFS 导出配置 |
| 9 | `priv-lx09-docker-socket:latest` | Docker socket（用户态模拟） | 22009 | socket/API 授权 |
| 10 | `priv-lx10-suid-librpath:latest` | SUID + RPATH 库劫持 | 22010 | 动态链接器路径 |

## 目录结构

```
Linux/
├─ _common/                  # 共享构建资源（基础镜像、入口脚本模板）
│   ├─ Dockerfile.base       # ubuntu:24.04 + sshd + 常用提权工具
│   ├─ entrypoint.sh         # 启动 sshd，等待 22 端口
│   └─ make_flag.sh          # 历史遗留脚本（现在 flag 由各题目录 flag.txt 构建时写入）
├─ lx01-suid-find/           # 每题一个目录
├─ …
├─ build_all.sh              # 批量构建
└─ deploy.md                 # 部署与排错
```

## 快速开始

```bash
bash build_all.sh                       # 构建 10 个镜像
docker run -d --name lx01 -p 22001:22 priv-lx01-suid-find:latest
ssh -p 22001 player@<host>              # 密码见 lx01-suid-find/README.md
```
