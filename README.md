# XGameHarness — GameStudio 共享 Agent Harness

多项目共享的 Claude Code 插件市场(plugin marketplace，注册名同仓库名 XGameHarness)。所有 GameStudio 项目从这里
获取统一的 skills / agents / hooks / 流程规则；本仓库每次 commit 推送后，各项目
下个 session 自动收到更新（插件不写 `version` 字段 → commit 即版本）。

## 插件

| 插件 | 内容 | 适用 |
|---|---|---|
| `game-studio-core` | 18 个流程 skills（/start、/sprint-plan、/design-system、/gate-check…）+ 9 个设计/制作 agents（producer、creative-director、*-designer…）+ 9 个 hooks（session-state 恢复 / 身份解析 / R2 语言注入 / path-scoped rules 注入 / git 校验）+ 流程 docs 与模板 | 所有游戏项目 |
| `unreal-pack` | 5 个 UE 专家 agents（unreal-specialist、ue-blueprint/gas/umg/replication-specialist）+ UE path-scoped rules 模板 | 仅 UE 项目 |

## 新项目接入 checklist

1. 复制 `project-template/` 内容到新项目根（`.claude/settings.json` 已含 marketplace
   引用；非 UE 项目删掉 `enabledPlugins` 里的 `unreal-pack@XGameHarness` 行）
2. 按项目改写 `CLAUDE.md`（模板内有占位注释）与 `.claude/team.json`
3. 从插件复制 path-scoped rules 模板到项目 `.claude/rules/`，按项目目录改 frontmatter `paths:`：
   - 通用：`plugins/game-studio-core/docs/templates/rules/`（design-docs / prototype-code）
   - UE：`plugins/unreal-pack/templates/rules/`（gameplay-code / ai-code / ui-code / test-standards）
4. 打开 Claude Code → 信任项目文件夹 → 按提示安装 `XGameHarness` marketplace 插件
5. 跑 `/start` 验证（新项目缺 team/ plan/ 目录时 hooks 静默降级，属正常）

## 项目契约（hooks / skills 依赖的目录约定）

hooks 以项目根为 CWD 读以下约定路径，全部有存在性守卫（缺失 = 跳过，不报错）：

```
design/gdd/                      # GDD（design-docs rule / detect-gaps / pre-compact 读）
plan/                            # sprint / milestone / stage.md（producer 系 skills 读）
team/session-state/{identity}/   # active.md 会话状态（session-start 恢复）
team/session-logs/{identity}/    # 月度轮转 session log（session-stop 写）
team/memo/{recipient}/           # 跨开发者 memo（/start surface）
docs/architecture/               # ADR
.claude/team.json                # 身份注册（resolve-identity 读）
.claude/rules/*.md               # path-scoped rules（SessionStart 全量 + PostToolUse 按 path 注入）
.claude/harness-config.json      # 可选：{"excludedAgents": [...]} 抑制 suggest-subagent 提示
.claude/state/                   # hook 运行时状态（加入项目 .gitignore）
```

## 每台开发机一次性配置（私有仓库自动更新）

后台自动更新对 HTTPS 私有仓库默认无法认证（Claude Code 禁用 credential helper），需：

```bash
gh auth setup-git        # 让 re-clone fallback 能认证
```

并在环境变量加 `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`（后台拉取失败时
保留现有克隆）。任何时候可手动 `/plugin marketplace update XGameHarness` 强制同步。

## 修改 harness 的规范

- 直接在 `main` 提交(commit)；推送(push)后所有项目下个 session 生效
- 坏改动回滚：`git revert` 本仓库 + 各项目 `/plugin marketplace update XGameHarness`
- 改 hooks 后本地先验证：`claude plugin validate .` + 在任一项目开新 session 观察
  SessionStart 输出
- **`.codex/hooks/` 镜像不自动同步**：RichLethe 等项目的 Codex CLI hook 副本独立
  存在，本仓库 hooks 改动后需手动同步各项目 `.codex/hooks/`（Codex 无插件机制）
- rules 模板（`templates/rules/`）改进不会自动进入已接入项目 —— rules 是
  per-project 文件（`paths:` 与项目目录耦合），需要时手动搬运

## 历史

从 RichLethe `.claude/`（上游 fork 自 Claude-Code-Game-Studios 模板）于 2026-07-14
抽取泛化。RichLethe 为第一个消费方。项目专属内容（rules 实例 / team.json / 项目
docs 三件套 / engine-reference）留在各项目仓库。
