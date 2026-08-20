# XGameHarness 操作手册

> **⚡ 主推入口：`/how-to-do <想做的事>`** —— 目标模糊、不知从哪开始、想让 agent
> 帮你组织完整流程时，任何时间任何情况直接调它（无参数 = "我现在该干嘛"模式）。
> 本手册是它背后的检索源；已明确知道要查什么时用 `/handbook <关键词>` 更快。
>
> agent 侧配套规则 **R5 Skill-first 路由**（agent-process-rules.md）：接到任务先
> 扫本手册 § 1 匹配 skill，命中即调用 —— 强制流程，不是建议。

---

## 1. 我想做什么 → 用什么

> **关于下表里的 subagent 用什么模型**：13 个 agent 全部是 `model: inherit`
> —— **跟随你主 session 当前的模型**（`/model` 选的那个），harness 不替你锁定。
>
> **建议在 Opus 或 Fable 下调用 subagent。** 这些 agent 做的是设计决策、公式推导、
> 架构判断，输出会被写进 GDD / ADR 并被后续所有工作依赖，错了的代价远高于省下的
> 那点开销。主 session 挂在 Haiku 上图快时，别顺手 spawn subagent。
>
> 单次想换模型：调用方在 Agent 调用里传 `model` 参数即可覆盖，优先级高于 agent
> 文件里的 `inherit`，不用改文件。

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
| 阶段门禁检查 | `/gate-check` | PASS / CONCERNS / FAIL 判定 + 缺失工件清单。判据 = 通用工件底线 + `plan/stage.md` 里当前阶段所有 Critical 行 Done；没有 `plan/stage.md` 会先问你要不要从模板生成 |

### 写策划案（GDD）

| 我想… | 用这个 | 说明 |
|---|---|---|
| **想改某个系统但还没想清楚怎么改** | `/explore-design` | **不产出任何文件**的探索：读现有 GDD + 上下游 + 代码 → 摆 2-4 条路线和取舍 → 收束成一个决定再转 `/design-system`。结论只活在对话里，聊完必须收 |
| **写一个系统的策划案** | `/design-system` | **2f 先用大白话跟你确认「这系统打算做成什么样」再动笔**（索引里那一行系统描述不等于被批准的设计前提 —— 不确认就可能写完几百行才发现前提就不对）。然后定档，档位记在文档头的 `Rigor` 字段（**不是** systems-index 里那个表优先级的 `Tier`）：**Lite**（默认，意图/改动/非目标/验收）或 **Full**（8 段，仅高风险）。升级判据 = 动 2 个以上系统接口 / 改核心循环 / 涉经济 / 影响存档 / 涉联机 / 全新系统（已登记进索引≠已设计）。两档都必须带 `设计前提` / `已定决策摘要` / `本篇用到的新词` 三节 —— 前两节让约束**留在文件里**而不是随简报消失，第三节防止 agent 造完词再用这套词问你拿主意。增量落盘 `design/gdd/` |
| 评审策划案 | `/design-review` | 按档位查完整性（Lite 查 4 项、Full 查 8 段，**不拿 8 段量 Lite**）+ 一致性 + 可实现性 + 实现细节是否混入，交给程序前必跑 |
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

### 文档模板（21 份，`${CLAUDE_PLUGIN_ROOT}/docs/templates/`）

**没有对应 skill 的文档，先来这里找模板，不要凭空编结构。** 多数 skill 内部已经
自动引用了对应模板；下表是给「手写一份文档」场景用的。

| 我要写… | 模板 | 被谁用 |
|---|---|---|
| 架构决策记录（ADR） | `architecture-decision-record.md` | 手写；或 spawn `game-studio-core:technical-director` |
| 从已有代码反推架构文档 | `architecture-doc-from-code.md` | `/reverse-document architecture` |
| 从已有实现反推系统设计文档 | `design-doc-from-implementation.md` | `/reverse-document design` |
| 从原型反推概念文档 | `concept-doc-from-prototype.md` | `/reverse-document concept` |
| 游戏概念 | `game-concept.md` | `/brainstorm` |
| 设计支柱 | `game-pillars.md` | `/brainstorm` |
| 系统清单 / 依赖图 | `systems-index.md` | `/map-systems` |
| 单个系统的策划案 | `game-design-document.md` | `/design-system`。**一份文件含两档模板**（Lite / Full）+ 定级判据 + 「什么不该写进 GDD」判据 |
| 经济模型（sink/faucet、掉落、曲线） | `economy-model.md` | 手写；或 spawn `game-studio-core:economy-designer` |
| 关卡文档 | `level-design-document.md` | 手写；或 spawn `game-studio-core:level-designer` |
| 阵营设定 | `faction-design.md` | 手写；或 spawn `game-studio-core:narrative-director` |
| 角色设定卡 | `narrative-character-sheet.md` | 同上 |
| 美术风格圣经 | `art-bible.md` | 手写；风格裁决 spawn `game-studio-core:creative-director` |
| 音频圣经 | `sound-bible.md` | 手写（无音频 agent） |
| **阶段 SoT** | `stage.md` | `/project-init` 必建 → `plan/stage.md`；`/gate-check` 读写 |
| 里程碑定义 | `milestone-definition.md` | 手写；或 spawn `game-studio-core:producer` |
| sprint 计划 | `sprint-plan.md` | `/sprint-plan new` |
| 风险登记条目 | `risk-register-entry.md` | 手写；或 spawn `game-studio-core:producer` |
| 项目阶段诊断报告 | `project-stage-report.md` | `/project-stage-detect` |
| 技术偏好（引擎/命名/性能预算/测试） | `technical-preferences.md` | `/setup-engine` 首建 → `.claude/docs/technical-preferences.md` |
| 立项 pitch | `pitch-document.md` | 手写 |
| 设计类 agent 的协作协议 | `collaborative-protocols/design-agent-protocol.md` | agent 内部引用 |

### Harness 自身运维

| 我想… | 用这个 | 说明 |
|---|---|---|
| **不确定做什么 / 想让 agent 组织流程** | `/how-to-do [目标]` | 主推入口：澄清目标 → 检索本手册 → 完整建议流程 → 推进第一步；无参数 = "我现在该干嘛" |
| **新项目接入这套 harness** | `/project-init` | 问询生成 `.claude/team.json`（harness 只带模板，不带可用文件）+ 复制其余模板 + 建 `plan/stage.md` + 同步 rules + 收尾清单（见 § 3） |
| **已接入的项目追上 harness 新版本** | `/harness-upgrade` | 三档一起查：① 插件本体是否过期（**不保证自动更新**，给出更新命令）② 按 `docs/project-contract.md` 查缺项目侧必需文件（如后来新增的 `plan/stage.md`）③ 转调 `/sync-rules` 同步规则。完成后写回 `syncedHarnessCommit` 水位 |
| 把 pack 的 rules 同步进项目 | `/sync-rules` | managed-by 标记文件跟随插件更新；定制过的不覆盖（见 § 4）。**只动 `.claude/rules/`**，其他项目文件归 `/harness-upgrade` 管 |
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
`design/gdd/`（策划案）｜`plan/`（sprint/milestone）｜`plan/stage.md`（**阶段 SoT**，
frontmatter `current_stage` + sub-phase 矩阵；/project-init 必建）｜
`team/session-state|session-logs|memo/{identity}/`｜`docs/architecture/`（ADR）｜
`.claude/rules|team.json|harness-config.json`

## 4. 分发三档 + rules 双层管理

harness 的内容按「怎么到达项目」分三档，**三档各有各的更新方式，不要混为一谈**：

| 档 | 内容 | 更新方式 |
|---|---|---|
| **A 插件本体** | skills / agents / hooks / docs / templates | `claude plugin marketplace update XGameHarness` + `claude plugin update <plugin>@XGameHarness` + **重启**。缓存按 commit SHA 钉版本，**不保证自动更新**（实测出现过订阅正确但停在一个月前 commit） |
| **B rules 实例** | `.claude/rules/*.md` | `/sync-rules` |
| **C 项目文件** | `plan/stage.md`、`CLAUDE.md`、`.claude/settings.json` 等 | `/harness-upgrade`，清单见 `docs/project-contract.md` |

**改 harness 时若新增了项目侧必需文件，必须同步在 `docs/project-contract.md` 加一行**
—— 否则已接入的老项目永远不会知道它的存在。

### rules 双层（B 档细节）

- **分发源**：`game-studio-core/rules/`（design-docs / prototype-code）+
  `unreal-pack/rules/`（gameplay-code / ai-code / ui-code / test-standards）
- **项目实例**：`.claude/rules/*.md` —— 注入 hook 只读这里
- 带 `managed-by: XGameHarness/<pack>` frontmatter = 跟随插件更新（/sync-rules 覆盖）
- 项目要定制（最常见：改 `paths:` 适配项目目录）→ 改完**删掉 managed-by 行**即固定
- 项目专属事实文档的**内容**（directory-structure / technical-preferences /
  coding-standards）**不进 harness** —— 它们是各项目的 SoT。但**空骨架模板可以**进：
  `docs/templates/technical-preferences.md` 就是一份（`/setup-engine` 首建时拿它填）。
  区别在于「模板在 harness，实例在项目」，跟 rules 双层是同一个模型

## 5. 在 marketplace 里加新插件

1. 建 `plugins/<name>/.claude-plugin/plugin.json`（`{"name": "...", "description": "..."}`，
   kebab-case；**不写 version** = commit 即版本）
2. 按需加 `skills/<skill>/SKILL.md`、`agents/*.md`、`hooks/hooks.json`（脚本引用自身用
   `${CLAUDE_PLUGIN_ROOT}`，读项目文件用 `CLAUDE_PROJECT_DIR`（勿用 `__file__` 推项目根——脚本跑在插件缓存里；裸相对路径仅在确认 CWD=项目根时可用））
2b. **Python hook 必须走 wrapper**：hooks.json 里写
   `bash "${CLAUDE_PLUGIN_ROOT}/hooks/run-python.sh" "${CLAUDE_PLUGIN_ROOT}/hooks/<script>.py"`，
   **不要**直接写 `python xxx.py` —— 大多数 Linux/macOS 只有 `python3`，裸 `python`
   会让 hook 静默失效（不报错、什么都不发生）。wrapper 依次探测 `python3/python/py`
   并实跑一次 `-c ""` 验证（Windows 商店别名能被 `command -v` 找到但跑不起来）
2c. **写 agent 时记住它只能作为 subagent 运行**：一个任务简报进、一条最终消息出，
   中途没有人在看。由此有两条硬约束：
   - **`tools:` 绝对不要写 `AskUserQuestion`** —— 平台会从 subagent 剥离它，声明
     无效，反而会让正文理直气壮地依赖一个拿不到的工具。上游
     `Claude-Code-Game-Studios` 的 49 个 agent **无一声明**；XGameHarness 曾在抽取时
     "顺手补全"了 8 个，导致 agent 卡在等一个永远不会来的回答（2026-08-19 修复）。
     需要用户裁定时，把决策写进最终报告让主 agent 转呈。
   - **不要写 `Task`** —— subagent 不能再 spawn subagent。上游给 15 个专家配了
     `Task`，抽取时全部去掉是对的。要转介就在报告里写"建议主 agent 调用 X"。
   - 同理，agent 正文里凡是"向用户提问""等待批准后再写"的措辞都要改成
     "取一个可辩护的默认值 + 在报告里列为可推翻的决策"，否则严格执行就是死锁：
     它问不了、而任何 agent 消息都不构成用户同意。
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
| Python hook（rules 注入 / R2 语言 / subagent 提示）完全不工作 | 本机有可用解释器吗：`python3 -c ""` / `python -c ""` 都试。三个 python hook 都经 `run-python.sh` 探测 `python3→python→py`，全找不到就静默放行（设计如此，不阻断） |
| `git commit` 被 hook 阻断 | 只有一种情况会阻断：暂存的 `.json` 解析失败。报错行会指出是哪个文件、哪一行。UTF-8 BOM 不再误伤；若提示「JSON validation did not run」说明解释器起不来，此时**未做校验**而不是校验通过 |
| 阶段类 skill 说不出项目在哪个阶段 | 项目有 `plan/stage.md` 吗？没有就跑 `/project-init` 或让 `/gate-check` 从模板生成。它是 gate-check / project-stage-detect / start / how-to-do 的唯一真相源 |
| harness 改坏了所有项目 | `git revert` XGameHarness 对应 commit + push + 各机 `/plugin marketplace update XGameHarness` |
| `.codex/hooks/` 行为不一致 | 指的是项目里**同时用 Codex CLI 当第二个 agent 运行时**的场景：Codex 无插件机制，它那份 hook 副本不会跟随 XGameHarness 更新，改了 harness hooks 要手动搬。与已移除的 `/codex-bridge` skill 无关 |
