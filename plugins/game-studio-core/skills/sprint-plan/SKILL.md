---
name: sprint-plan
description: "Generates a new sprint plan or updates an existing one based on the current milestone, completed work, and available capacity. Pulls context from production documents and design backlogs."
argument-hint: "[new|update|status]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent
---

When this skill is invoked:

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
- [ ] All Must Have tasks completed
- [ ] All tasks pass acceptance criteria
- [ ] No S1 or S2 bugs in delivered features
- [ ] Design documents updated for any deviations
- [ ] Code reviewed and merged
```

6. **Write it to `plan/sprints/sprint-[N].md`** — ask first: "May I write this sprint
   plan to `plan/sprints/sprint-[N].md`?" Do not leave the plan only in the reply.

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
