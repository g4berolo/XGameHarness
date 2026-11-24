---
name: sprint-plan
description: "起草或更新 Sprint、创建和编辑项目任务、调整人员与进度、记录验收或查询状态。新增任务时确认直接写入正式 Sprint 或提交任务评审，按开发者的选择执行。"
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, mcp__xgs_review__xgs_project_board
---

参数：[new|update|status]


> **运行时适配**：先按需读取本插件 [`docs/codex-runtime.md`](../../docs/codex-runtime.md)。
> Codex 用 `$技能名` 或读取 SKILL.md；共享流程中的 Claude 工具名按宿主现有能力执行。
> `${CLAUDE_PLUGIN_ROOT}` 是本 SKILL.md 向上两级的插件根，不假定它在普通终端里存在。

When this skill is invoked:

## 执行类型与任务拆分（必须）

先读[任务执行规则](../../docs/task-execution.md)。新增任务按“新增任务由开发者选择去向”处理，选择评审的条目转交 `proposal-review`。任务按 AI／人工执行分开，分别记录交付、证据和进度。

## 工作室实时看板

通过 `xgs_project_board` 读取目标 Sprint、服务器修订和任务。按任务执行规则分页，核对任务编号、经办人、审批人和证据。对已迁或直接建在主看板的任务，使用工具执行用户要求的创建、编辑、改派、进度调整、证据提交、验收与关闭恢复；Sprint 和版本也使用对应 action 管理。保留当前身份权限、修订冲突和幂等重试约束，以服务器回执确认结果；不要改旧文档冒充看板写入。若宿主仍只提供 `list/get`、客户端离线或权限不足，说明哪些改动待处理。只知道旧文档里的编号时先查迁入映射。

## 文件型 Sprint 的格式契约

- 新计划使用 `plan/sprints/sprint-[N].md`，保留 `## Sprint Goal`、`## Capacity`、
  `## Tasks`、`## Definition of Done`。优先级是 Tasks 内的三级标题，不能把
  `## Must Have` 当成 Tasks 的替代。正文可以中文，结构键沿用模板。
- 任务表保留 `ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria | Status`。
  ID 必须唯一且稳定（例如 `S2-001`）；拆分后保留父子关系，不重编号已执行的任务。
- 每项任务在 DoD 中至少有一条以完整 ID 开头的复选框，例如
  `- [ ] S2-001 验收条件与证据`。`[ ]` 未验收、`[~]` 部分完成、`[x]` 全部验收通过。
  整轮“所有任务完成”的复选框不能替代逐任务记录。Status 是说明，须与 DoD 一致；
  AI技术任务与人工视觉审核必须拆开，各自按证据标记；遗留混合任务未拆分且尚未全部验收时只能部分完成。不替用户批准，不把源码测试当引擎实测。
- 更新旧计划时先读原文件并保留文件名、ID、证据和未完成项。若需要规范化结构，
  原位调整标题/列名并保留引用；不能新建一份同内容的 sprint，不能凭叙述自动补 `[x]`。
  旧格式被 XGS 兼容读取不代表它是新计划的推荐格式。
- 写入后重新读取，核对文件名、Tasks 表、唯一 ID、每项 DoD 关联、状态与证据是否一致；
  有 XGS 源码时可用 `readSprints(projectDir)` 核对实际读取数量和 warnings。
  未运行看板解析时说明只做了格式检查，不宣称客户端已验证。

## 发布仍按文件管理的正式任务

给既有 Sprint 添加正式任务时，只修改指定计划的任务行和对应 DoD。核实现有 ID、任务状态和其他开发者改动，避免重复登记。仅要求本地登记或项目未接文档服务器时，核对正式文件后报告路径及新增 ID。

文档服务器管理的文件型 Sprint 在「发布改动」面板核对差异，由开发者确认发布。请核对服务器回执后报告正式任务 ID。

## 文件型计划编排

0. **List existing sprints** — Glob `plan/sprints/*` to see what is already
   planned. (This replaces a frontmatter `context:` block that never executed —
   `context:` is not a SKILL.md field.)


1. **Read the current milestone** from `plan/milestones/`.

2. **Read the previous sprint** (if any) from `plan/sprints/` to
   understand velocity and carryover.

3. **Scan design documents** in `design/gdd/` for features tagged as ready
   for implementation.

4. **Check the risk register** at `plan/risk-register/`.

For `new`:

5. **Generate a sprint plan** from the shipped template — Read
   `${CLAUDE_PLUGIN_ROOT}/docs/templates/sprint-plan.md` and fill it in. It is more
   complete than the outline below (Milestone Context, per-discipline capacity, task
   Status column, `S[N]-001` id convention). The outline below is only a fallback for
   when that template cannot be read:

```markdown
# Sprint [N] -- [Start Date] to [End Date]

## Sprint Goal
[One sentence describing what this sprint achieves toward the milestone]

## Capacity
- Total days: [X]
- Buffer (20%): [Y days reserved for unplanned work]
- Available: [Z days]

## Tasks

### Must Have (Critical Path)
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria | Status |
|----|------|-------------|-----------|-------------|-------------------|--------|

### Should Have
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria | Status |
|----|------|-------------|-----------|-------------|-------------------|--------|

### Nice to Have
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria | Status |
|----|------|-------------|-----------|-------------|-------------------|--------|

### Human Actions & Review
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria | Status |
|----|------|-------------|-----------|-------------|-------------------|--------|
| S[N]-H01 | [HUMAN] [独立人工操作或审核；注明必要/可选] | 待指定 | 待估 | [AI任务ID] | [真人执行证据/结论] | Not Started |

## Carryover from Previous Sprint
| Task | Reason | New Estimate |
|------|--------|-------------|

## Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|

## Dependencies on External Factors
- [List any external dependencies]

## Definition of Done
### AI Execution
- [ ] S[N]-001 [该任务的验收条件与证据；为每个真实任务生成对应项]
### Human Actions & Review
- [ ] S[N]-H01 [对应人工任务的操作/批准证据]

- [ ] All Must Have tasks completed
- [ ] All tasks pass acceptance criteria
- [ ] No S1 or S2 bugs in delivered features
- [ ] Design documents updated for any deviations
- [ ] Code reviewed and merged
```

6. **Write it to `plan/sprints/sprint-[N].md`** within the user's requested scope.
   Do not leave an explicitly requested plan only in the reply. Then perform the format checks above.

For `update`:

5. **Edit the existing sprint in place** — never regenerate it, that would discard
   completed status and carryover:
   1. Read the target sprint in `plan/sprints/`. Use the project's active sprint if no sprint was named and it is unambiguous.
   2. Match the requested changes to existing tasks and IDs. Ask only if the target sprint or scope remains unclear.
   3. Apply the changes with `Edit` (targeted row edits, not a rewrite).
   4. Move every removed-but-unfinished task into the Carryover table with a reason.
   5. Re-check the capacity total against the remaining days and flag any overflow.

For `status`:

5. **Generate a status report**:

```markdown
# Sprint [N] Status -- [Date]

## Progress
- AI: [完成/总数；无任务则不适用]
- Human: [完成/总数；待人工ID与负责人]
- Overall: [必要人工项未完成时不得报告Sprint全部完成]

### Completed
| Task | Completed By | Notes |
|------|-------------|-------|

### In Progress
| Task | Owner | % Done | Blockers |
|------|-------|--------|----------|

### Not Started
| Task | Owner | At Risk? | Notes |
|------|-------|----------|-------|

### Blocked
| Task | Blocker | Owner of Blocker | ETA |
|------|---------|-----------------|-----|

## Burndown Assessment
[On track / Behind / Ahead]
[If behind: What is being cut or deferred]

## Emerging Risks
- [Any new risks identified this sprint]
```

### Agent Consultation

For comprehensive sprint planning, consider consulting:
- `game-studio-core:producer` agent for capacity planning, risk assessment, and cross-department coordination
- `game-studio-core:game-designer` agent for feature prioritization and design readiness assessment
