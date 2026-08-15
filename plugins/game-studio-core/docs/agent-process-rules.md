# Agent Process Rules

通用 agent 行为规则。由 game-studio-core 的 SessionStart hook 每 session 全量注入，视同 CLAUDE.md 级指令（无需在项目 CLAUDE.md 里 @ 引入）。适用所有 main agent / subagent / skill。

---

## R1 Verify-before-label

**Rule**: 向用户呈现选项（AskUserQuestion option label / Plan 阶段 recap / 任务描述）前，必须先 Read 目标文件 header + Status，验证当前真实状态。不直抄以下来源 vocabulary 作为 work label:

- `team/session-state/{identity}/active.md` 的 "下一步" 条目
- ADR 章节标题（描述原始决策时刻，常相对 pre-pivot baseline）
- GDD 头部 Status 字段单独（不读 body 时易误判）

**Why**: 这三类来源是 *intent snapshot*，不是 *current state*。会随 intermediate commit 与 review pass 失效，但不主动更新。

- `active.md "下一步"` 在 session start 时写，commit 之间不刷新
- ADR 标题 vocabulary 描述 "决策内容"（如 "招募引擎重写"），P3 反向 patch Applied 后该词已 stale
- Status `In Design (Provisional — 待 X 后冻结)` 模式下，trigger X 满足后 status word 不自动更新

**RichLethe 实例 (2026-05-18 P12)**: `/start` flow 提供 "#29 hero-recruit 重写" 选项，源于 `active.md` "下一步" + `ADR-0006 §5` 标题，均 pre-P6-Applied vocabulary。实际 GDD 已 513 行 / 8 section / design-review APPROVED WITH SHOULD-FIX 全 land，真实工作 = freeze pass (XS)，非 rewrite (L)。

**How to apply**:

1. AskUserQuestion 准备 option 前，对每个 system label 执行:
   ```
   Read [target-file]:1-30                  # header + Status
   Grep "Status|Review History|design-review" [target-file]   # 验证 status word 时效
   ```
2. 若 Status 含 "Provisional — 待 X 后冻结" 模式，主动 grep X 是否已满足，避免把 "待冻结" 当 "未起草"
3. option label 必须可追溯至 *verified file state*，不可纯凭 session-state notes 或 ADR vocabulary
4. 若 label 与文件状态冲突（如 active.md 说 "重写" 但 GDD APPROVED），在 option description 注 stale 警告或先 fix vocabulary 再呈现

---

## R2 Language preference: Chinese

**Rule**: 默认中文回应所有 user-facing 文本。

**适用**:
- 主对话回应（含 caveman mode 叠加 = 中文 caveman）
- AskUserQuestion 的 question + option label + description
- 任务计划 / Phase 命名 / 状态汇报
- TaskCreate subject + description

**例外（保持英文 / 原文）**:
- Code (C++/Blueprint identifier / 注释中已有英文模式按既有风格)
- Git commit message / PR title / body（项目惯例 — 见 `git log` 历史均英文）
- 技术名词：类名、枚举值、API 签名、UE 内置概念（`UWorldSubsystem` / `FInstancedStruct` / `Lumen` 等）
- 引用文件路径 / GDD 章节命名按既有 codebase 命名匹配（中文则中文，英文则英文）
- Error message / log 原文不翻译

**词类细化规则**（2026-05-24 用户反馈 — vocab 层细化，非 verbosity 层）:

| 词类 | 写法 | 示例 |
|---|---|---|
| 普通操作动词 | 中文为主，括号 optional 注英文 | "提交(commit)" / "推送(push)" / "拉取(pull)" / "改一下" / "合并(merge)" |
| 状态形容词 | "中文(英文)" 注解形式 | "未跟踪(untracked)" / "已暂存(staged)" / "待办(pending)" / "过期(stale)" |
| 专业名词 | 首次出现 "中文(英文)" 注解，后续段落可只用英文 | 第一次 "组件(Component)"，第二次起直接 "Component" |
| 项目代号 / 任务 ID | 原文 | `PP-E3` / `S1-T2` / `R-001` / `ADR-0005` / `sprint-001` |
| 文件路径 / 类名 / API | 原文 | `client/Source/.../RoomBase.cpp` / `ARoomBase` / `SetRelativeLocation` |
| UE 内置概念缩写 | 原文 | `PIE` / `BP` / `UMG` / `UCLASS` / `Lumen` / `Nanite` |

**反例对比**:

| ❌ Before | ✅ After |
|---|---|
| "OK 跑 commit？" | "OK 提交(commit)？" |
| "保持 untracked，session-log 自动累积" | "保持未跟踪(untracked)，会话日志(session-log)自动累积" |
| "把它 patch 一下" | "改一下" / "修补(patch)一下" |
| "memory 文件不在 repo" | "记忆(memory)文件不在仓库(repo)" |
| "git status 显示 staged" | "`git status` 显示已暂存(staged)" |

**RichLethe 触发 (2026-05-24 P29)**: 用户在 session 收尾对话中 flag："OK 跑 commit？" 这类 RuMa style（中英 token 同句混搭）让中文用户在每句话内做语言上下文切换，降低阅读速度。要求细化 R2 至动词 / 状态词 / 专业名词三层。**注意**：中文化是 vocabulary 层（用什么词），不是 verbosity 层（说多少话）— caveman / fragments / 省主语风格不受影响。

**Caveman mode 协同**: caveman = 压缩规则；中文 = 语言。两者叠加 → 中文 caveman:
- ✅ "句号删；fragments OK；技术词精确"
- ❌ 不要 caveman 化技术名词或文件路径

---

## R3 Path-scoped rules awareness

**Rule**: 编辑 `.claude/rules/*.md` frontmatter `paths:` 匹配的文件时，对应规则会通过 SessionStart hook + PostToolUse hook 自动注入 agent context。Agent 必须按注入的 rules 校验所有 Edit/Write 操作，不能假装没看到。

**Why**: rules 是 path-scoped 强约束（如 `design/gdd/**` 必须 8 section / 双向依赖 / 可测试 AC）。SessionStart 全量加载 + PostToolUse 按 path 注入是 XGameHarness 自定义 convention 而非 Claude Code 官方机制，agent 看到 system reminder 中 "Active Rule:" / "Path-Scoped Rules" 段时应视同 CLAUDE.md @ 引入的指令对待。

**How to apply**:

1. session 启动时若 system reminder 含 `=== Path-Scoped Rules ===` 段，**完整读完**所有列出的 rule 文件
2. Edit `.claude/rules/*.md` `paths:` 匹配的文件后，若 tool result 含 `additionalContext` 注入新 rule，**立即按新 rule 校验本次和后续 Edit**
3. 如对 rule 有歧义或与其他指令冲突，明示问用户哪条优先，不要自行判断
4. 项目若自建了 `.claude/docs/rules-reference.md` 索引则以其为准，否则直接列 `.claude/rules/*.md`；机制原理 + 加新 rule 流程见本插件 `docs/rules-mechanism.md`

---

## R4 Subagent invocation pattern

**Rule**: harness 提供 14 个 subagent（`game-studio-core` 9 个 + `unreal-pack` 5 个，随插件分发；不在项目 `.claude/agents/` 里）。Claude Code 平台默认**不自动 spawn subagent**：要实际启用，开发者必须在 prompt 中显式命名 agent type 或显式说 "use a subagent"。主 agent 不会基于任务内容自主推断。

**关键平台事实 — agent 名必须带插件前缀**：插件提供的 subagent，其 agent type 是 `<插件名>:<agent名>`（如 `game-studio-core:producer`）。传裸名会被直接拒绝：

```
Agent type 'producer' not found. Available agents: ..., game-studio-core:producer, ...
```

这是硬失败不是降级——写 spawn 模板时务必带全前缀。

**关键平台事实 — subagent 不能 spawn subagent**：Claude Code 在 subagent 上下文中静默过滤 `Task`/`Agent` 原语，即便 agent frontmatter 声明了 `Task` 工具也无效（见 [issue #61993](https://github.com/anthropics/claude-code/issues/61993) / [#19077](https://github.com/anthropics/claude-code/issues/19077)）。因此 `producer` / `creative-director` / `technical-director` / `unreal-specialist` 等"协调/编排型" agent 的 "Delegation Map" / "Sub-Specialist Routing" 段**不是真的 spawn**，而是产出一份"建议主 agent 该调用哪个 agent"的文本，由主 agent（orchestrator 这一层）再去 spawn。嵌套委派改用 Skill 串联或主对话依次 chain。

**Why**: 平台层 Agent tool description 明文 "Do not spawn agents unless the user asks"；项目层 CLAUDE.md "User-driven collaboration" 协议同向加固。agent description 字段的 "Use this agent for X" 是给主 agent **选择哪个 agent** 的参考（当用户决定 spawn 时），不是触发条件。

**Available subagents**（下表 Agent 列即 Agent tool 的 `subagent_type` 取值，可直接复制）:

`game-studio-core`（所有项目）:

| Agent | 何时显式调用 |
|---|---|
| `game-studio-core:producer` | sprint 规划 / 里程碑追踪 / 风险管理 / 范围谈判 / 跨部门协调（最高层协调 agent；自带 skills: sprint-plan/scope-check/estimate/milestone-review） |
| `game-studio-core:creative-director` | 游戏愿景 / 基调 / pillar 冲突裁决 / 设计-美术-叙事跨域决策（自带 skills: brainstorm/design-review） |
| `game-studio-core:technical-director` | 引擎架构 / 技术选型 / 性能策略 / 技术风险（ADR 级决策） |
| `game-studio-core:game-designer` | 核心循环 / 系统拆解 / 战斗 / 经济顶层框架问题 |
| `game-studio-core:systems-designer` | 子系统数值公式 / 进阶曲线 / 交互矩阵详细推导 |
| `game-studio-core:economy-designer` | 商人 sink/faucet / 掉落表 / 经济曲线校准 |
| `game-studio-core:narrative-director` | 故事架构 / 角色背景 / 对话策略 |
| `game-studio-core:level-designer` | 关卡布局 / encounter pacing / 空间叙事 |
| `game-studio-core:modeler` | AI 图生 3D 管线（Tripo3D；需项目配好 tripo-ai MCP server） |

`unreal-pack`（仅 UE 项目，未启用该插件时下列 agent 不存在）:

| Agent | 何时显式调用 |
|---|---|
| `unreal-pack:unreal-specialist` | UE 全域权威 — BP vs C++ 决策 / Subsystem 用法 / 引擎最佳实践把关 |
| `unreal-pack:ue-blueprint-specialist` | Blueprint 架构 / BP↔C++ 边界 / 防 BP spaghetti |
| `unreal-pack:ue-gas-specialist` | Gameplay Ability System（GA / GE / AttributeSet / Tag） |
| `unreal-pack:ue-umg-specialist` | UMG / CommonUI — widget 层级 / 数据绑定 / 输入路由 |
| `unreal-pack:ue-replication-specialist` | 多人网络复制（单人项目 future/reference 用，应用前先 flag 与单人 pillar 冲突） |

> 移植自上游模板 `Claude-Code-Game-Studios`（2026-06-03，P38）。适配：路径
> `production/`→`plan/`；删除 ue-* agent 的 `Task` 工具（嵌套 spawn 不支持）+ 改写
> `unreal-specialist` 的 orchestration 段为"推荐主 agent 调用"。上游模板里存在但本
> harness **未移植**的 agent（`lead-programmer` / `art-director` / `illustrator` /
> `analytics-engineer` 等）：遇到引用时不要尝试 spawn，改向用户汇报缺口。

**推荐 prompt 模板**（直接 copy-paste；注意 agent 名带插件前缀）:

```
spawn game-studio-core:systems-designer subagent: 跑 design/gdd/combat-formulas.md
3 对位算例（warrior vs warrior / warrior vs mage / mage vs assassin）× Lv1/Lv5/Lv10
= 9 算例，识别 dmg > 50% target HP 的失衡点，结果写入 GDD 末尾 ## Audit Log section。
```

```
spawn game-studio-core:economy-designer subagent: audit design/gdd/economy.md
4 商人 sink/faucet 的产销平衡，逐项给出当前产出与消耗估算，
标出净产出为正的项，结果写入 GDD 末尾 ## Audit Log section。
```

**How to apply**:

1. 任务计划阶段，**主 agent 必须在选项呈现时提示 "此任务适合 subagent，推荐 prompt: ..."** — 不能假设用户知道触发机制
2. 当用户在 sprint plan / task spec 看到 "agent 兜底" / "用 X agent" 字样时，那只是 **意图标注**，要实际启动需在 session 内显式命名
3. 显式命名后主 agent **不再自处理**，转用 Agent tool 启动 subagent；subagent 完成后主 agent 汇总结果给用户审批
4. session-log 应记录 subagent invocation 痕迹（如 "spawn game-studio-core:systems-designer @ combat-formulas audit"）
5. 报 `Agent type not found` 时先查前缀：`game-studio-core:` 还是 `unreal-pack:`；
   非 UE 项目未启用 `unreal-pack`，其 5 个 ue-* agent 本就不存在，不要绕过去硬试

---

## R5 Skill-first 路由

**Rule**: 主 agent 接到任何任务，动手前**必须**先对照可用 skills（速查表 =
XGameHarness 插件 `docs/HANDBOOK.md` § 1 + system prompt 中的 skill 列表）检查
是否有匹配 skill。这是**强制流程，不是可选建议**（参照 superpowers 的
"mandatory workflows, not suggestions" 模式）。

**判定顺序**：

1. **有匹配 skill** → 直接用 Skill tool 调用，不要徒手复刻其流程（徒手复刻 =
   丢失该 skill 固化的结构、模板与检查项）
2. **目标模糊 / 用户不确定做什么 / 明显是多步工作流** → 调 `/how-to-do`
   （主推入口 — 目标澄清 + 手册检索 + 完整建议流程），任何时间任何情况均可用
3. **确认无匹配** → 自行处理，但在回应中留一句"本任务无匹配 skill，直接处理"
   的判定痕迹（防静默跳过）

**与 R4 的边界**：skill 是流程指令（主 agent 自己执行），命中即可直接调用；
subagent 仍按 R4 显式触发协议——提示用户推荐 spawn 模板，不自动 spawn。

**Why**: RichLethe P31 review 曾发现 7 个 subagent 零调用；skill 同样存在
"装了但被遗忘"问题——主 agent 默认倾向徒手做而不查工具箱。触发点前移到
任务开始时强制自检，成本一次扫表，收益是流程资产真正被复用。

**How to apply**:

1. 每个新任务（用户消息含行动请求时）第一步：心中对照 HANDBOOK § 1 分组
   （立项规划 / 写策划案 / 写代码 / 美术 / 运维）扫一遍
2. 命中但用户没点名 → 直接调用并告知"本任务走 /xxx skill"；用户明确拒绝后不再坚持
3. 用户说"不知道下一步干嘛"/"帮我推进" → `/how-to-do` 无参数模式
4. 判定为无匹配时，若事后发现其实有匹配 skill，视同 R5 违规——承认 + 改用 skill 重做

---

## 修订历史

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-18 | 初稿 R1 + R2 | P12 #29 误判 rewrite 触发；用户偏好中文显式化 |
| 2026-05-22 | 加 R3 path-scoped rules awareness | P29 激活 rules 机制 — 让 agent 知道注入内容应视同 CLAUDE.md 指令 |
| 2026-05-23 | 加 R4 subagent invocation pattern | P31 review 发现 7 subagent 零调用；fro 未知需显式触发，固化触发协议 + prompt 模板 |
| 2026-05-24 | R2 词类细化（动词 / 状态词 / 专业名词三层）+ 反例对比 + RichLethe 触发说明 | P29 session 末用户反馈："OK 跑 commit？" 类混搭降低中文用户阅读流畅度，要求 vocab 层细化 |
| 2026-06-03 | R4 名册 7→15（移植 producer / creative-director / technical-director / unreal-specialist + 4 ue-* specialist）+ 补 "subagent 不能 spawn subagent" 平台事实 | P38 用户从上游模板补项目管理 / 分析 / UE 专家 agent；移植中发现模板的 unreal-specialist Task-orchestration 在 Claude Code 跑不通，固化平台限制说明 |
| 2026-07-14 | 加 R5 skill-first 路由 + /how-to-do 主推入口 | harness 抽取为 XGameHarness marketplace 后 skill 数达 22，"装了但被遗忘"风险同 R4 教训；参照 superpowers mandatory-workflow 模式前移触发点 |
| 2026-08-13 | R4 名册加插件前缀（`game-studio-core:` / `unreal-pack:`）+ 删除未移植的 `illustrator` + 15→14 + 澄清 agent 不在项目 `.claude/agents/` | harness 全量审查：实测裸名 `subagent_type` 直接报 `Agent type not found`，而全仓 0 处带前缀 —— R4 推荐的所有 spawn 模板均不可用；`illustrator` 已于 2026-07-04 随 LiblibAI 停用删除但名册未同步 |
