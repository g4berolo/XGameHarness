---
name: project-stage-detect
description: "Automatically analyze project state, detect stage, identify gaps, and recommend next steps based on existing artifacts."
argument-hint: "[optional: role filter like 'programmer' or 'designer']"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash
---

# Project Stage Detection

This skill scans your project to determine its current development stage, completeness
of artifacts, and gaps that need attention. It's especially useful when:
- Starting with an existing project
- Onboarding to a codebase
- Checking what's missing before a milestone
- Understanding "where are we?"

---

## Workflow

### 1. Scan Key Directories

Analyze project structure and content:

**Design Documentation** (`design/`):
- Count GDD files in `design/gdd/*.md`
- Check for game-concept.md, game-pillars.md, systems-index.md
- If systems-index.md exists, count total systems vs. designed systems
- Analyze completeness (Overview, Detailed Design, Edge Cases, etc.)
- Count narrative docs in `design/narrative/`
- Count level designs in `design/levels/`

**Source Code** (`client/Source/`):
- Count `*.cpp`/`*.h` files in UE5 project
- Identify major modules (subdirectories with 5+ files)
- Check for Player/, Gameplay/, AI/, UI/ subdirectories
- Estimate lines of code (rough scale)

**Planning Artifacts** (`plan/`):
- Read `plan/stage.txt` (current stage) and `plan/stage.md` (sub-phase status)
- Check for sprint plans in `plan/sprints/`
- Look for milestone definitions in `plan/milestones/`
- Find risk register in `plan/risk-register/`

**Prototypes** (`prototypes/`):
- Count prototype directories
- Check for READMEs (documented vs undocumented)
- Assess if prototypes are archived or active

**Architecture Docs** (`docs/architecture/`):
- Count ADRs (Architecture Decision Records)
- Check for overview/index documents

**Tests** (`tests/`):
- Count test files
- Estimate test coverage (rough heuristic)

### 2. Classify Project Stage

Stage SoT is `plan/stage.txt` (single line) + `plan/stage.md` (full sub-phase
table). Always prefer reading SoT directly. Auto-detect heuristic is fallback
only when SoT files don't exist.

| Stage | Indicators (fallback heuristic) |
|-------|----------------------------------|
| **Concept** | No game concept doc, brainstorming phase |
| **Pre-Production** | Concept exists; covers Systems Design + Engine Setup + Walking Skeleton + Prototype + Sprint Bootstrap (see `plan/stage.md` Pre-Production sub-phase matrix) |
| **First Playable** | Core loop walkthrough complete (RunStart→RunEnd 跑通 + 占位 art) |
| **Vertical Slice** | 1 楼层 feature-complete + ship-quality art for that slice |
| **Alpha** | Feature & content complete, asset slots filled (允许占位) |
| **Beta** | Content lock + perf pass + bug fix + localization in progress |
| **Release** | Explicit only (set by `/gate-check` Beta → Release gate) |

> 后续 stage（First Playable / Vertical Slice / Alpha / Beta / Release）通常显式经
> `/gate-check` 切换，不依赖 heuristic 自动检测。Sub-phase 详见 `plan/stage.md`。

### 3. Collaborative Gap Identification

**DO NOT** just list missing files. Instead, **ask clarifying questions**:

- "I see combat code (`client/Source/client/Gameplay/Combat/`) but no `design/gdd/combat-system.md`. Was this prototyped first, or should we reverse-document?"
- "You have 15 ADRs but no architecture overview. Should I create one to help new contributors?"
- "No sprint plans in `plan/`. Are you tracking work elsewhere (Jira, Trello, etc.)?"
- "I found a game concept but no systems index. Have you decomposed the concept into individual systems yet, or should we run `/map-systems`?"
- "Prototypes directory has 3 projects with no READMEs. Were these experiments, or do they need documentation?"

### 4. Generate Stage Report

Use template: `${CLAUDE_PLUGIN_ROOT}/docs/templates/project-stage-report.md` (bundled with this plugin)

**Report structure**:
```markdown
# Project Stage Analysis

**Date**: [date]
**Stage**: [Concept | Pre-Production | First Playable | Vertical Slice | Alpha | Beta | Release]

## Completeness Overview
- Design: [X%] ([N] docs, [gaps])
- Code: [X%] ([N] files, [systems])
- Architecture: [X%] ([N] ADRs, [gaps])
- Production: [X%] ([status])
- Tests: [X%] ([coverage estimate])

## Gaps Identified
1. [Gap description + clarifying question]
2. [Gap description + clarifying question]

## Recommended Next Steps
[Priority-ordered list based on stage and role]
```

### 5. Role-Filtered Recommendations (Optional)

If user provided a role argument (e.g., `/project-stage-detect programmer`):

**Programmer**:
- Focus on architecture docs, test coverage, missing ADRs
- Code-to-docs gaps

**Designer**:
- Focus on GDD completeness, missing design sections
- Prototype documentation

**Producer**:
- Focus on sprint plans, milestone tracking, roadmap
- Cross-team coordination docs

**General** (no role):
- Holistic view of all gaps
- Highest-priority items across domains

### 6. Request Approval Before Writing

**Collaborative protocol**:
```
I've analyzed your project. Here's what I found:

[Show summary]

Gaps identified:
1. [Gap 1 + question]
2. [Gap 2 + question]

Recommended next steps:
- [Priority 1]
- [Priority 2]
- [Priority 3]

May I write the full stage analysis to plan/project-stage-report.md?
```

Wait for user approval before creating the file.

---

## Example Usage

```bash
# General project analysis
/project-stage-detect

# Programmer-focused analysis
/project-stage-detect programmer

# Designer-focused analysis
/project-stage-detect designer
```

---

## Follow-Up Actions

After generating the report, suggest relevant next steps:

- **Concept exists but no systems index?** → `/map-systems` to decompose into systems
- **Missing design docs?** → `/reverse-document design client/Source/client/[Module]`
- **Missing architecture docs?** → `/architecture-decision` or `/reverse-document architecture`
- **Prototypes need documentation?** → `/reverse-document concept prototypes/[name]`
- **No sprint plan?** → `/sprint-plan`
- **Approaching milestone?** → `/milestone-review`

---

## Collaborative Protocol

This skill follows the collaborative design principle:

1. **Question First**: Ask about gaps, don't assume
2. **Present Options**: "Should I create X, or is it tracked elsewhere?"
3. **User Decides**: Wait for direction
4. **Show Draft**: Display report summary
5. **Get Approval**: "May I write to plan/project-stage-report.md?"

**Never** silently write files. **Always** show findings and ask before creating artifacts.
