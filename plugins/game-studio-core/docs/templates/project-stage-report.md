# Project Stage Analysis Report

**Generated**: [DATE]
**Stage**: [Concept | Pre-Production | First Playable | Vertical Slice | Alpha | Beta | Release]
**Analysis Scope**: [Full project | Specific role: programmer/designer/artist/producer]

> Stage 词表 + sub-phase 详见 `plan/stage.md`。本报告是诊断快照，不替代 stage SoT。

---

## Executive Summary

[1-2 段总览：当前 stage、主要 gap、优先建议]

**Current Focus**: [项目正主动推进的 sub-phase]
**Blocking Issues**: [阻塞推进的 gap]
**Estimated Time to Next Stage**: [若可估]

---

## Completeness Overview

### Design Documentation
- **Status**: [X%] complete
- **Files Found**: [N] documents in `design/`
  - GDD sections: [N] files in `design/gdd/`
  - Narrative docs: [N] files in `design/narrative/`
  - Level designs: [N] files in `design/levels/`
- **Key Gaps**:
  - [ ] [Missing doc 1 + why it matters]
  - [ ] [Missing doc 2 + why it matters]

### Source Code
- **Status**: [X%] complete
- **Files Found**: [N] source files in `client/Source/`
- **Major Systems Identified**:
  - ✅ [System 1] (`client/Source/client/path/`) — [brief status]
  - ✅ [System 2] (`client/Source/client/path/`) — [brief status]
  - ⚠️  [System 3] (`client/Source/client/path/`) — [issue or incomplete]
- **Key Gaps**:
  - [ ] [Missing system 1 + impact]
  - [ ] [Missing system 2 + impact]

### Architecture Documentation
- **Status**: [X%] complete
- **ADRs Found**: [N] decisions documented in `docs/architecture/`
- **Coverage**:
  - ✅ [Decision area 1] — documented
  - ⚠️  [Decision area 2] — undocumented but implemented
  - ❌ [Decision area 3] — neither documented nor decided
- **Key Gaps**:
  - [ ] [Missing ADR 1 + why it's needed]
  - [ ] [Missing ADR 2 + why it's needed]

### Planning Artifacts (`plan/`)
- **Status**: [X%] complete
- **Found**:
  - Stage SoT: `plan/stage.md` [Exists — current_stage: X | Missing — stage below is a heuristic guess]
  - Sprint plans: [N] in `plan/sprints/`
  - Milestones: [N] in `plan/milestones/`
  - Risk register: [N] in `plan/risk-register/`
- **Key Gaps**:
  - [ ] [Missing artifact + impact]

### Testing
- **Status**: [X%] coverage (estimated)
- **Test Files**: [N] in `tests/`
- **Coverage by System**:
  - [System 1]: [X%] (estimated)
  - [System 2]: [X%] (estimated)
- **Key Gaps**:
  - [ ] [Missing test area + risk]

### Prototypes
- **Active Prototypes**: [N] in `prototypes/`
  - ✅ [Prototype 1] — documented with README
  - ⚠️  [Prototype 2] — no README, unclear status
- **Archived**: [N] (experiments completed)
- **Key Gaps**:
  - [ ] [Undocumented prototype + why it matters]

### Art Pipeline
- **Status**: [X%] complete
- **Art assets**: [项目自定美术目录的产出情况；harness 不再假定任何资产目录结构，
  按本项目实际路径填，没有就写 n/a]
- **UE Imported**: [N] assets in `client/Content/`
- **Key Gaps**:
  - [ ] [Missing pipeline stage / asset class]

---

## Stage Classification Rationale

**Why [Stage]?**

[基于 `plan/stage.md` 中 sub-phase 状态分布，解释为何项目处于该 stage]

**Sub-phase Snapshot** (refer to `plan/stage.md` for full table):
- Engineering: [N Done / M In Progress / K Not Started]
- Art: [N / M / K]
- Design: [N / M / K]
- Production: [N / M / K]

**Indicators for this stage**:
- [Indicator 1 that matches this stage]
- [Indicator 2 that matches this stage]

**Next stage requirements** (Critical sub-phases to gate):
- [ ] [Requirement 1 to reach next stage]
- [ ] [Requirement 2 to reach next stage]
- [ ] [Requirement 3 to reach next stage]

---

## Gaps Identified (with Clarifying Questions)

### Critical Gaps (block progress)

1. **[Gap Name]**
   - **Impact**: [Why this blocks progress]
   - **Question**: [Clarifying question before assuming solution]
   - **Suggested Action**: [What could be done, pending clarification]

### Important Gaps (affect quality/velocity)

2. **[Gap Name]**
   - **Impact**: [Why this matters]
   - **Question**: [Clarifying question]
   - **Suggested Action**: [Proposed solution]

### Nice-to-Have Gaps (polish/best practices)

3. **[Gap Name]**
   - **Impact**: [Minor but valuable]
   - **Question**: [Clarifying question]
   - **Suggested Action**: [Optional improvement]

---

## Recommended Next Steps

### Immediate Priority (Do First)
1. **[Action 1]** — [Why it's priority 1]
   - Suggested skill: `/[skill-name]` or manual work
   - Estimated effort: [S/M/L]

2. **[Action 2]** — [Why it's priority 2]
   - Suggested skill: `/[skill-name]`
   - Estimated effort: [S/M/L]

### Short-Term (This Sprint/Week)
3. **[Action 3]** — [Why it's important soon]
4. **[Action 4]** — [Why it's important soon]

### Medium-Term (Next Milestone)
5. **[Action 5]** — [Future need]
6. **[Action 6]** — [Future need]

---

## Role-Specific Recommendations

[If role filter was used, provide role-specific guidance]

### For [Role]:
- **Focus areas**: [What this role should prioritize]
- **Blockers**: [What's blocking this role's work]
- **Next tasks**:
  1. [Task 1]
  2. [Task 2]

---

## Follow-Up Skills to Run

Based on gaps identified, consider running:

- `/reverse-document [type] [path]` — [For which gap]
- ADR for [which gap] — no `/architecture-decision` skill exists; write an ADR from the `architecture-decision-record` template in the harness `docs/templates/` (or via `game-studio-core:technical-director`)
- `/sprint-plan` — [If planning artifacts missing]
- `/milestone-review` — [If approaching deadline]
- `/gate-check` — [If considering stage advancement]

---

## Appendix: File Counts by Directory

```
design/
  gdd/           [N] files
  narrative/     [N] files
  levels/        [N] files

client/
  Source/        [N] .cpp/.h files
  Content/       [N] .uasset files

docs/
  architecture/  [N] ADRs

plan/
  sprints/       [N] plans
  milestones/    [N] definitions

tests/           [N] test files
prototypes/      [N] directories
```

---

**End of Report**

*Generated by `/project-stage-detect` skill*
