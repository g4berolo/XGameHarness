---
name: project-init
description: "新项目接入 XGameHarness：复制项目模板（settings.json / CLAUDE.md / team.json）、填充项目名、同步 path-scoped rules、初始化目录约定。在新项目根目录（空目录或已有代码）运行一次即可。"
argument-hint: "[项目名]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Skill
---

# /project-init — 新项目接入 XGameHarness

在**新项目根目录**运行。完成后重启 session，harness（skills / agents / hooks）
即随 XGameHarness marketplace 自动加载并持续更新。

## 执行步骤

### 1. 收集信息（缺什么问什么，AskUserQuestion）

- **项目名**（PascalCase，如 RichLethe）：优先用参数；否则默认当前目录名，向用户确认
- **是否 UE 项目**：决定 `enabledPlugins` 是否保留 `unreal-pack@XGameHarness`，
  以及同步哪些 rules
- **团队成员**：模板 `team.json` 只有占位条目，必须填真实身份。至少拿到当前用户的
  `git config user.name` / `user.email`（直接读，不要问），据此生成第一条 identity；
  identity key 用小写字母/下划线（它会成为 `team/session-state/<key>/` 目录名）。
  再问是否还有其他成员要一并登记

### 2. 复制模板（源：`${CLAUDE_PLUGIN_ROOT}/project-template/`）

| 模板文件 | 目标 | 处理 |
|---|---|---|
| `.claude/settings.json` | 同路径 | 原样复制；非 UE 项目删掉 `"unreal-pack@XGameHarness"` 行 |
| `.claude/team.json` | 同路径 | **必须替换全部 `<...>` 占位**，否则身份解析退化为 `unknown` |
| `.claude/harness-config.json` | 同路径 | 默认 `excludedAgents: []`；单人游戏可填 `["unreal-pack:ue-replication-specialist"]`，非 UE 项目无需填（hook 已按 enabledPlugins 自动跳过 unreal-pack agents）|
| `.gitignore` | 项目根 | 已有则合并两行（`.claude/state/`、`.claude/settings.local.json`），不覆盖 |
| `CLAUDE.md` | 项目根 | 替换 `<ProjectName>` 占位；按项目类型填 Technology Stack 骨架 |

**已存在的文件一律先展示 diff 征求确认，不静默覆盖**（目标项目可能已有配置）。

### 3. 同步 rules

调用 `/sync-rules`（本插件 skill）把 core + unreal-pack（若启用）的 path-scoped
rules 实例化到 `.claude/rules/`，并按其报告提醒用户哪些 `paths:` 需要按本项目
目录结构调整。

### 4. 目录约定骨架（可选，问用户）

harness 项目契约目录按需 lazy 创建即可，但若用户愿意现在建好（`{identity}` 用
第 1 步已解析出的 key，`.gitkeep` 放最底层目录）：

```
design/gdd/
plan/
team/session-state/{identity}/
team/session-logs/{identity}/
team/memo/{identity}/open/
team/memo/{identity}/closed/
docs/architecture/
```

memo 必须是 `team/memo/{recipient}/{open,closed}/` 两层 —— 平铺一层 `team/memo/` 不符合
CLAUDE.md 契约，`/start` 的 `team/memo/{identity}/open/*.md` 会扫不到任何东西。

### 5. 收尾清单（输出给用户）

- [ ] `git init`（若尚未）+ 首次提交（须用户明确要求才执行）
- [ ] 确认 `.gitignore` 含 `.claude/state/`、`.claude/settings.local.json`（模板已带）
- [ ] 确认 `team.json` 里没有残留的 `<...>` 占位（跑一次 `/start` 看 Developer 是否解析出来）
- [ ] 重启 Claude Code session → 信任目录 → 按提示安装 XGameHarness marketplace
- [ ] 每台新机器一次性：`gh auth setup-git` + 环境变量
      `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`（私有仓库自动更新）
- [ ] UE 项目：跑 `/setup-engine` 钉引擎版本并生成 engine-reference 文档
- [ ] 跑 `/start` 验证 dashboard；查 `/handbook` 了解全部能力

## 注意

- 本 skill 不执行 git 提交/推送（遵循协作协议：No commits without user instruction）
- 模板里的 permissions 是团队基线，项目可自行增删
