---
name: project-init
description: "新项目接入 XGameHarness：复制项目模板（settings.json / CLAUDE.md / team.json）、填充项目名、同步 path-scoped rules、初始化目录约定。在新项目根目录（空目录或已有代码）运行一次即可。"
argument-hint: "[项目名]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /project-init — 新项目接入 XGameHarness

在**新项目根目录**运行。完成后重启 session，harness（skills / agents / hooks）
即随 XGameHarness marketplace 自动加载并持续更新。

## 执行步骤

### 1. 收集信息（缺什么问什么，AskUserQuestion）

- **项目名**（PascalCase，如 RichLethe）：优先用参数；否则默认当前目录名，向用户确认
- **是否 UE 项目**：决定 `enabledPlugins` 是否保留 `unreal-pack@XGameHarness`，
  以及同步哪些 rules
- **团队成员**：默认复用模板里的 zhouxinyu + fro 双人配置，问一下是否沿用

### 2. 复制模板（源：`${CLAUDE_PLUGIN_ROOT}/project-template/`）

| 模板文件 | 目标 | 处理 |
|---|---|---|
| `.claude/settings.json` | 同路径 | 原样复制；非 UE 项目删掉 `"unreal-pack@XGameHarness"` 行 |
| `.claude/team.json` | 同路径 | 按步骤 1 结果调整成员 |
| `.claude/harness-config.json` | 同路径 | 单人游戏保留 excludedAgents 示例；多人游戏清空数组 |
| `CLAUDE.md` | 项目根 | 替换 `<ProjectName>` 占位；按项目类型填 Technology Stack 骨架 |

**已存在的文件一律先展示 diff 征求确认，不静默覆盖**（目标项目可能已有配置）。

### 3. 同步 rules

调用 `/sync-rules`（本插件 skill）把 core + unreal-pack（若启用）的 path-scoped
rules 实例化到 `.claude/rules/`，并按其报告提醒用户哪些 `paths:` 需要按本项目
目录结构调整。

### 4. 目录约定骨架（可选，问用户）

harness 项目契约目录按需 lazy 创建即可，但若用户愿意现在建好：
`design/gdd/`、`plan/`、`team/session-state/`、`team/session-logs/`、
`team/memo/`、`docs/architecture/`（各放 `.gitkeep`）。

### 5. 收尾清单（输出给用户）

- [ ] `git init`（若尚未）+ 首次提交（须用户明确要求才执行）
- [ ] `.gitignore` 补 `.claude/state/`、`.claude/settings.local.json`
- [ ] 重启 Claude Code session → 信任目录 → 按提示安装 XGameHarness marketplace
- [ ] 每台新机器一次性：`gh auth setup-git` + 环境变量
      `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`（私有仓库自动更新）
- [ ] UE 项目：跑 `/setup-engine` 钉引擎版本并生成 engine-reference 文档
- [ ] 跑 `/start` 验证 dashboard；查 `/handbook` 了解全部能力

## 注意

- 本 skill 不执行 git 提交/推送（遵循协作协议：No commits without user instruction）
- 模板里的 permissions 是团队基线，项目可自行增删
