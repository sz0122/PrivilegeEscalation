# PrivilegeEscalation

提权题目仓库，按平台分目录存放：

```
PrivilegeEscalation/
├─ Linux/                     # Linux 提权题目
│  ├─ lx01-suid-find/         # 每题一个目录：源码、flag.txt、README、解题.md
│  ├─ …
│  ├─ lx10-suid-librpath/
│  ├─ _common/                # 公共基础镜像与入口脚本
│  ├─ build_all.sh            # 批量构建
│  ├─ deploy.md               # 部署与排错
│  └─ Linux提权题目汇总.xlsx   # 考点 / 标题 / 难度 / 描述 / flag 汇总
└─ Windows/                   # Windows 提权题目（后续补充）
```

## Linux 部分

10 道题，每题一个独立 Docker 镜像，一种提权面：SUID、sudo 配置、cron 脚本权限、PATH 劫持、
服务脚本可写、文件 capabilities、`/etc/passwd` 权限、NFS `no_root_squash`、Docker socket、
SUID + RPATH。

- 统一账号：`player / Player@2026`，端口 22001–22010
- flag：`/flag.txt`，`root:root 0400`，每题固定值，来源为各题目录的 `flag.txt`
- 构建与运行见 `Linux/README.md` 与 `Linux/deploy.md`

