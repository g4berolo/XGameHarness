---
name: sprint-plan
description: "Generates a new sprint plan or updates an existing one based on the current milestone, completed work, and available capacity. Pulls context from production documents and design backlogs."
allowed-tools: Read, Glob, Grep, Write, Edit, Agent
---

参数：[new|update|status]


> **运行时适配**：先按需读取本插件 [`docs/codex-runtime.md`](../../docs/codex-runtime.md)。
> Codex 用 `$技能名` 或读取 SKILL.md；共享流程中的 Claude 工具名按宿主现有能力执行。
> `${CLAUDE_PLUGIN_ROOT}` 是本 SKILL.md 向上两级的插件根，不假定它在普通终端里存在。

When this skill is invoked:

## XGS 看板格式契约

- 新计划使用 `plan/sprints/sprint-[N].md`，保留 `## Sprint Goal`、`## Capacity`、
  `## Tasks`、`## Definition of Done`。优先级是 Tasks 内的三级标题，不能把
  `## Must Have` 当成 Tasks 的替代。正文可以中文，结构键沿用模板。
- 任务表保留 `ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria | Status`。
  ID 必须唯一且稳定（例如 `S2-001`）；拆分后保留父子关系，不重编号已执行的任务。
- 每项任务在 DoD 中至少有一条以完整 ID 开头的复选框，例如
  `- [ ] S2-001 验收条件与证据`。`[ ]` 未验收、`[~]` 部分完成、`[x]` 全部验收通过。
  整轮“所有任务完成”的复选框不能替代逐任务记录。Status 是说明，须与 DoD 一致；
  技术通过但视觉待评审只可记部分完成，不替用户批准，不把源码测试当引擎实测。
- 更新旧计划时先读原文件并保留文件名、ID、证据和未完成项。若需要规范化结构，
  原位调整标题/列名并保留引用；不能新建一份同内容的 sprint，不能凭叙述自动补 `[x]`。
  旧格式被 XGS 兼容读取不代表它是新计划的推荐格式。
- 写入后重新读取，核对文件名、Tasks 表、唯一 ID、每项 DoD 关联、状态与证据是否一致；
  有 XGS 源码时可用 `readSprints(projectDir)` 核对实际读取数量和 warnings。
  未运行看板解析时说明只做了格式检查，不宣称客户端已验证。

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
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria |
|----|------|-------------|-----------|-------------|-------------------|

### Should Have
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria |
|----|------|-------------|-----------|-------------|-------------------|

### Nice to Have
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria |
|----|------|-------------|-----------|-------------|-------------------|

## Carryover from Previous Sprint
| Task | Reason | New Estimate |
|------|--------|-------------|

## Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|

## Dependencies on External Factors
- [List any external dependencies]

## Definition of Done for this Sprint
- [ ] S[N]-001 [该任务的验收条件与证据；为每个真实任务生成对应项]
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
   1. Read the newest file in `plan/sprints/`.
   2. Show the current task table and ask which rows to add / remove / re-estimate.
   3. Apply the changes with `Edit` (targeted row edits, not a rewrite).
   4. Move every removed-but-unfinished task into the Carryover table with a reason.
   5. Re-check the capacity total against the remaining days and flag any overflow.

For `status`:

5. **Generate a status report**:

```markdown
# Sprint [N] Status -- [Date]

## Progress: [X/Y tasks complete] ([Z%])

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
