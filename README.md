# XGameHarness — GameStudio 共享 Agent Harness

多项目共享的 Claude Code 插件市场(plugin marketplace，注册名同仓库名 XGameHarness)。
所有 GameStudio 项目从这里获取统一的 skills / agents / hooks / 流程规则；本仓库每次
commit 推送后，各项目下个 session 自动收到更新（插件不写 `version` 字段 → commit 即版本）。

> **⚡ 主推入口：`/how-to-do <想做的事>`** —— 任何时间任何情况帮你澄清目标、检索
> 匹配 skill/agent、给出完整建议流程并立刻推进（无参数 = "我现在该干嘛"）。
>
> **📖 详细操作手册**：[`plugins/game-studio-core/docs/HANDBOOK.md`](plugins/game-studio-core/docs/HANDBOOK.md)
> —— 任务导向速查（「我想写策划案」→ 用哪个 skill/agent），含 hooks 说明、rules 双层
> 管理、加插件流程、故障排查。已接入项目内 `/handbook <关键词>` 直查。
>
> agent 侧执行 **R5 Skill-first 路由**（superpowers 式强制流程）：接到任务先扫
> skill 匹配，命中即调用；SessionStart hook 每 session 注入该规则。

## 插件

| 插件 | 内容 | 适用 |
|---|---|---|
| `game-studio-core` | 23 个流程 skills（/how-to-do、/start、/brainstorm、/design-system、/sprint-plan、/gate-check、/project-init、/sync-rules、/handbook、/codex-bridge…）+ 9 个设计/制作 agents（producer、creative-director、*-designer、modeler）+ 8 个 hooks（session-state 恢复 / 身份解析 / R2 语言注入 / rules 注入 / git 校验；另有 `resolve-identity.sh` 为共享库非 hook）+ 通用 rules 源 + 流程 docs、模板、操作手册、项目接入模板 | 所有游戏项目 |
| `unreal-pack` | 5 个 UE 专家 agents（unreal-specialist、ue-blueprint/gas/umg/replication-specialist）+ UE path-scoped rules 源（gameplay/ai/ui/test） | 仅 UE 项目 |

> **调用 agent 必须带插件前缀**：`subagent_type` 取 `game-studio-core:producer` /
> `unreal-pack:ue-gas-specialist` 这种全名，裸名会直接报 `Agent type not found`。

## 新项目接入

在新项目根目录跑一次 **`/project-init`**（自动复制模板 + 填项目名 + 同步 rules +
输出收尾清单）。手动等价步骤见 HANDBOOK § 3。

每台开发机一次性配置（私有仓库自动更新需要）：

```bash
gh auth setup-git
# 环境变量：CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1
```

手动兜底：`/plugin marketplace update XGameHarness`。

## 项目契约（hooks / skills 依赖的目录约定）

hooks 以项目根为 CWD 读以下约定路径，全部有存在性守卫（缺失 = 静默跳过）：

```
design/gdd/                      # GDD（design-docs rule / detect-gaps / pre-compact 读）
plan/                            # sprint / milestone / stage.md（producer 系 skills 读）
team/session-state/{identity}/   # active.md 会话状态（session-start 恢复）
team/session-logs/{identity}/    # 月度轮转 session log（session-stop 写）
team/memo/{recipient}/           # 跨开发者 memo（/start surface）
docs/architecture/               # ADR
.claude/team.json                # 身份注册（resolve-identity 读）
.claude/rules/*.md               # path-scoped rules 项目实例（注入 hook 只读这里）
.claude/harness-config.json      # 可选：{"excludedAgents": ["unreal-pack:ue-replication-specialist"]}
                                 #   抑制 suggest-subagent 提示；填带前缀的 agent 全名
.claude/state/                   # hook 运行时状态（项目模板已带 .gitignore 忽略此目录）
```

## rules 双层管理

pack 内 `rules/` 目录是**分发源**（frontmatter 带 `managed-by: XGameHarness/<pack>`），
项目 `.claude/rules/` 是**运行实例**。用 `/sync-rules` 同步；项目定制（最常见 = 按项目
目录改 `paths:`）后删掉 managed-by 行即固定不被覆盖。详见 HANDBOOK § 4。

## 修改 harness 的规范

- 直接在 `main` 提交(commit)；推送(push)后所有项目下个 session 生效
- 改前 `claude plugin validate .`；坏改动回滚 = `git revert` + 各机
  `/plugin marketplace update XGameHarness`
- 插件内脚本引用自身文件用 `${CLAUDE_PLUGIN_ROOT}`，读项目文件用相对路径 /
  `CLAUDE_PROJECT_DIR`（勿用 `__file__` 推项目根——脚本运行在插件缓存里）
- **`.codex/hooks/` 镜像不自动同步**：项目里的 Codex CLI hook 副本独立存在，
  hooks 改动后需手动搬运（Codex 无插件机制）
- rules 源改动不会自动进入已接入项目——各项目跑 `/sync-rules` 拉取
- 加新插件流程见 HANDBOOK § 5

## 历史

从 RichLethe `.claude/`（上游 fork 自 [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
模板 v0.3.0）于 2026-07-14 抽取泛化。RichLethe 为第一个消费方。项目专属内容
（rules 实例 / team.json / 项目 docs 三件套 / engine-reference）留在各项目仓库。
同日：仓库改名 claude-harness → XGameHarness（X = owner 代号，去 claude 以便
将来容纳其他 agent 运行时的插件）；rules / 项目模板 / 操作手册 pack 化。
