# XGameHarness 操作手册

> **⚡ 主推入口：`/how-to-do <想做的事>`** —— 目标模糊、不知从哪开始、想让 agent
> 帮你组织完整流程时，任何时间任何情况直接调它（无参数 = "我现在该干嘛"模式）。
> 本手册是它背后的检索源；已明确知道要查什么时用 `/handbook <关键词>` 更快。
>
> agent 侧配套规则 **R5 Skill-first 路由**（agent-process-rules.md）：接到任务先
> 扫本手册 § 1 匹配 skill，命中即调用 —— 强制流程，不是建议。

---

## 1. 我想做什么 → 用什么

### 立项 / 规划

| 我想… | 用这个 | 说明 |
|---|---|---|
| 从零想一个游戏点子 | `/brainstorm` | 引导式创意工作坊 → 产出 `design/gdd/game-concept.md`；深挖愿景可再 spawn `game-studio-core:creative-director` subagent |
| 把游戏概念拆成系统清单 | `/map-systems` | 概念 → 系统依赖图 + 设计优先级 → `design/gdd/systems-index.md` |
| 看项目现在到什么阶段、缺什么 | `/project-stage-detect` | 全仓库扫描 → 阶段判定 + 缺口清单 + 下一步建议 |
| 排 sprint | `/sprint-plan` | 拉取 milestone/backlog/velocity → sprint 计划；复杂排期 spawn `game-studio-core:producer` |
| 估工作量 | `/estimate` | 复杂度 + 依赖 + 历史速度 → 带置信度的估算 |
| 查范围蔓延(scope creep) | `/scope-check` | 现行范围 vs 原计划 diff，量化膨胀并给砍单建议 |
| 里程碑复盘 / go-no-go | `/milestone-review` | 完成度 + 质量 + 风险 → go/no-go 建议 |
| 阶段门禁检查 | `/gate-check` | PASS / CONCERNS / FAIL 判定 + 缺失工件清单 |

### 写策划案（GDD）

| 我想… | 用这个 | 说明 |
|---|---|---|
| **写一个系统的策划案** | `/design-system` | 逐 section 引导写 8 段结构 GDD（Overview / Player Fantasy / Detailed Rules / Formulas / Edge Cases / Dependencies / Tuning Knobs / Acceptance Criteria），增量落盘 `design/gdd/` |
| 评审策划案 | `/design-review` | 完整性 / 一致性 / 可实现性检查，交给程序前必跑 |
| 顶层玩法框架拿不准 | spawn `game-studio-core:game-designer` | 核心循环 / 系统拆解层面的设计问题 |
| 数值公式 / 算例 / 曲线细化 | spawn `game-studio-core:systems-designer` | 公式推导、对位算例、交互矩阵 |
| 经济 / 掉落 / 商人设计 | spawn `game-studio-core:economy-designer` | sink-faucet 分析、掉落表、经济曲线 |
| 关卡布局 / encounter / pacing | spawn `game-studio-core:level-designer` | 空间设计、遭遇设计、难度节奏 |
| 世界观 / 角色 / 叙事架构 | spawn `game-studio-core:narrative-director` | 故事结构与方向（不写具体台词） |
| 数值平衡体检 | `/balance-check` | 扫数据表和公式找失衡点 / degenerate 策略 |
| 从已有代码反推设计文档 | `/reverse-document` | 实现 → 补写 GDD / 架构文档 |

### 写代码（含 UE）

| 我想… | 用这个 | 说明 |
|---|---|---|
| 技术选型 / 架构决策 / 写 ADR | spawn `game-studio-core:technical-director` | ADR 级决策；产出落 `docs/architecture/` |
| UE 最佳实践把关 / BP vs C++ | spawn `unreal-pack:unreal-specialist` | UE 全域权威，会转介下面的子专家 |
| Blueprint 架构 / 防 BP 面条 | spawn `unreal-pack:ue-blueprint-specialist` | BP↔C++ 边界、BP 优化 |
| GAS 技能系统 | spawn `unreal-pack:ue-gas-specialist` | GA / GE / AttributeSet / Tag |
| UMG / CommonUI 界面实现 | spawn `unreal-pack:ue-umg-specialist` | widget 层级、数据绑定、输入路由 |
| 多人网络复制 | spawn `unreal-pack:ue-replication-specialist` | 单人项目建议在 `.claude/harness-config.json` 的 excludedAgents 填该 agent 全名以屏蔽提示（模板默认不屏蔽）|
| 代码评审 | `/code-review <path>` | 编码标准 + 架构 + SOLID + 游戏性能常见坑 |
| 快速验证一个玩法点子 | `/prototype` | 放宽标准的一次性原型，产出进 `prototypes/` + 结构化报告 |
| 引擎版本固定 / 升级 | `/setup-engine` | 钉版本进 CLAUDE.md + WebSearch 生成 engine-reference 文档（LLM 知识缺口补全） |

### 美术

| 我想… | 用这个 | 说明 |
|---|---|---|
| 定美术风格 / 色板 / 各类美术标准 | 拿 `${CLAUDE_PLUGIN_ROOT}/docs/templates/art-bible.md` 手写，或 spawn `game-studio-core:creative-director` 定基调 | 风格定调是项目通用的，模板保留 |
| 生图 / 图生 3D / 资产管线 | **本 harness 暂无** | 原 `/codex-bridge`、`/generate-model`、`modeler` agent 已于 2026-08-17 移除：它们绑死了一套具体的资产产出目录（`art/01_Illustration/` 等），而不同项目的产出路径差异太大。待重构后回归；在那之前美术生产走项目自己的工具 |

### 测试 / 运营

| 我想… | 用这个 | 说明 |
|---|---|---|
| 收集 / 分析试玩反馈 | `/playtest-report` | 生成模板或把散乱笔记结构化 |

### Harness 自身运维

| 我想… | 用这个 | 说明 |
|---|---|---|
| **不确定做什么 / 想让 agent 组织流程** | `/how-to-do [目标]` | 主推入口：澄清目标 → 检索本手册 → 完整建议流程 → 推进第一步；无参数 = "我现在该干嘛" |
| **新项目接入这套 harness** | `/project-init` | 复制模板 + 填项目名 + 同步 rules + 收尾清单（见 § 3） |
| 把 pack 的 rules 同步进项目 | `/sync-rules` | managed-by 标记文件跟随插件更新；定制过的不覆盖（见 § 4） |
| **看项目现在什么状态 / 今天干啥** | `/start` | 项目状态 dashboard：阶段 / 未提交改动 / 待办 memo surface（memo 只有跑它才会出）+ 按任务分流 |
| 查这本手册 | `/handbook <关键词>` | agent 检索本文件作答 |
| 改 harness 本身 | 直接改 `D:\work\GameStudio\XGameHarness` | commit + push 后所有项目下个 session 生效；先 `claude plugin validate .` |
| 加新插件到 marketplace | 见 § 5 | |

---

## 2. 自动在跑的东西（hooks，无需手动触发）

| Hook | 时机 | 干什么 |
|---|---|---|
| session-start | session 开始 | 项目横幅 + 身份识别（team.json × git user）+ active.md 恢复提示 + **全量注入项目 rules** + 注入 Agent Process Rules（整篇，现为 R1-R5）+ R5 摘要块。memo 不在此 hook，需跑 `/start` 才 surface |
| detect-gaps | session 开始 | 文档缺口快扫，提示跑 /project-stage-detect |
| inject-language-reminder | 每条 prompt | R2 中文输出词类规则注入 |
| suggest-subagent | 每条 prompt | 关键词命中时提示可用 subagent（读项目 `.claude/harness-config.json` 的 excludedAgents 屏蔽不适用者；**只提示不自动 spawn**） |
| inject-rules | 每次 Edit/Write | 按 `.claude/rules/*.md` 的 `paths:` glob 命中即注入对应规则（session 内防重复） |
| validate-git | 每条 Bash 命令前 | commit 前校验暂存 JSON（非法则**阻断**）；跨身份 session-state、无 owner 的 TODO 仅**告警**；push 到 main/master/develop 提醒 |
| pre-compact | context 压缩前 | **读** `team/session-state/{identity}/active.md` + 记忆文件并注入压缩前上下文；唯一写操作是往 `team/session-logs/{identity}/compaction-log.txt` 追加一行。active.md 需自行维护 |
| session-stop | session 结束 | 追加月度轮转 session-log（一行状态指针） |

## 3. 新项目接入（手动版清单）

推荐直接跑 `/project-init`。手动等价步骤：

1. 复制插件缓存里 `game-studio-core/project-template/` 的 4 个文件到项目根
   （`.claude/settings.json` / `.claude/harness-config.json` /
   `.gitignore`（已有则合并两行，不覆盖）/ `CLAUDE.md`）
2. **手写 `.claude/team.json`**：模板是 `project-template/.claude/team.json.template`，
   harness 里没有可直接用的 team.json。按 `git config user.name` / `user.email` 填出
   第一条 identity（key 只能小写字母/数字/下划线，会成为 `team/*/<key>/` 目录名），
   删掉 `_template` / `_privacy` 说明字段。**公开仓库**建议 `git_emails: []`，
   只靠 `git_users` 匹配 —— 邮箱一旦进历史就删不掉
3. 非 UE 项目：settings.json 删 `"unreal-pack@XGameHarness"` 行
4. CLAUDE.md 替换 `<ProjectName>` 占位、填技术栈
5. `/sync-rules` 实例化 rules，按项目目录改 `paths:`（改后删 managed-by 行）
6. 重启 session → 信任目录 → 按提示装 marketplace
7. 每台新机器一次性：`gh auth setup-git` + env `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`

**项目目录契约**（hooks/skills 依赖的约定，按需 lazy 创建，缺失静默降级）：
`design/gdd/`（策划案）｜`plan/`（sprint/milestone/stage.md）｜
`team/session-state|session-logs|memo/{identity}/`｜`docs/architecture/`（ADR）｜
`.claude/rules|team.json|harness-config.json`

## 4. rules 双层管理

- **分发源**：`game-studio-core/rules/`（design-docs / prototype-code）+
  `unreal-pack/rules/`（gameplay-code / ai-code / ui-code / test-standards）
- **项目实例**：`.claude/rules/*.md` —— 注入 hook 只读这里
- 带 `managed-by: XGameHarness/<pack>` frontmatter = 跟随插件更新（/sync-rules 覆盖）
- 项目要定制（最常见：改 `paths:` 适配项目目录）→ 改完**删掉 managed-by 行**即固定
- 项目专属事实文档（directory-structure / technical-preferences / coding-standards）
  **不进 harness** —— 它们是各项目的 SoT，模板见 project-template/CLAUDE.md 占位注释

## 5. 在 marketplace 里加新插件

1. 建 `plugins/<name>/.claude-plugin/plugin.json`（`{"name": "...", "description": "..."}`，
   kebab-case；**不写 version** = commit 即版本）
2. 按需加 `skills/<skill>/SKILL.md`、`agents/*.md`、`hooks/hooks.json`（脚本引用自身用
   `${CLAUDE_PLUGIN_ROOT}`，读项目文件用 `CLAUDE_PROJECT_DIR`（勿用 `__file__` 推项目根——脚本跑在插件缓存里；裸相对路径仅在确认 CWD=项目根时可用））
3. `marketplace.json` 的 `plugins` 数组加 `{"name", "source": "./plugins/<name>", "description"}`
4. `claude plugin validate .` → commit → push
5. 各项目启用：settings.json `enabledPlugins` 加 `"<name>@XGameHarness": true`（团队统一）
   或本机 `/plugin install <name>@XGameHarness`
6. 改名 / 删插件：marketplace.json 加 `renames` 映射，否则老用户 plugin-not-found

## 6. 故障排查

| 症状 | 处理 |
|---|---|
| 插件没更新到最新 | `/plugin marketplace update XGameHarness`；私有仓库后台拉取失败见 § 3 第 6 条 |
| skill/agent 找不到 | 重启 session；确认 settings.json `enabledPlugins` 键为 `xxx@XGameHarness` |
| rules 没注入 | rules 在项目 `.claude/rules/` 吗（不是插件里）？`paths:` glob 与被编辑文件匹配吗？看 `.claude/state/inject-rules.log` |
| hook 报错 / 无输出 | 项目缺契约目录属正常静默降级；真报错看对应 hook 脚本 + `.claude/state/` 日志 |
| harness 改坏了所有项目 | `git revert` XGameHarness 对应 commit + push + 各机 `/plugin marketplace update XGameHarness` |
| `.codex/hooks/` 行为不一致 | Codex 镜像不自动同步，从 harness `hooks/` 手动搬 |
