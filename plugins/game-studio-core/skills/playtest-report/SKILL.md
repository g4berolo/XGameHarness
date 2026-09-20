---
name: playtest-report
description: "Generates a structured playtest report template or analyzes existing playtest notes into a structured format. Use this to standardize playtest feedback collection and analysis."
allowed-tools: Read, Glob, Grep, Write
---

参数：[new|analyze path-to-notes]


> **运行时适配**：先按需读取本插件 [`docs/codex-runtime.md`](../../docs/codex-runtime.md)。
> Codex 用 `$技能名` 或读取 SKILL.md；共享流程中的 Claude 工具名按宿主现有能力执行。
> `${CLAUDE_PLUGIN_ROOT}` 是本 SKILL.md 向上两级的插件根，不假定它在普通终端里存在。

When invoked with `new`, generate this template:

```markdown
# Playtest Report

## Session Info
- **Date**: [Date]
- **Build**: [Version/Commit]
- **Duration**: [Time played]
- **Tester**: [Name/ID]
- **Platform**: [PC/Console/Mobile]
- **Input Method**: [KB+M / Gamepad / Touch]
- **Session Type**: [First time / Returning / Targeted test]

## Test Focus
[What specific features or flows were being tested]

## First Impressions (First 5 minutes)
- **Understood the goal?** [Yes/No/Partially]
- **Understood the controls?** [Yes/No/Partially]
- **Emotional response**: [Engaged/Confused/Bored/Frustrated/Excited]
- **Notes**: [Observations]

## Gameplay Flow
### What worked well
- [Observation 1]
- [Observation 2]

### Pain points
- [Issue 1 -- Severity: High/Medium/Low]
- [Issue 2 -- Severity: High/Medium/Low]

### Confusion points
- [Where the player was confused and why]

### Moments of delight
- [What surprised or pleased the player]

## Bugs Encountered
| # | Description | Severity | Reproducible |
|---|-------------|----------|-------------|

## Feature-Specific Feedback
### [Feature 1]
- **Understood purpose?** [Yes/No]
- **Found engaging?** [Yes/No]
- **Suggestions**: [Tester suggestions]

## Quantitative Data (if available)
- **Deaths**: [Count and locations]
- **Time per area**: [Breakdown]
- **Items used**: [What and when]
- **Features discovered vs missed**: [List]

## Overall Assessment
- **Would play again?** [Yes/No/Maybe]
- **Difficulty**: [Too Easy / Just Right / Too Hard]
- **Pacing**: [Too Slow / Good / Too Fast]
- **Session length preference**: [Shorter / Good / Longer]

## Top 3 Priorities from this session
1. [Most important finding]
2. [Second priority]
3. [Third priority]
```

When invoked with `analyze`, read the raw notes, cross-reference with existing
design documents, and fill in the template above with structured findings.
Flag any playtest observations that conflict with design intent.

## Output Path

Both modes write to `plan/playtests/playtest-YYYY-MM-DD-<focus>.md` — that is the
directory `/gate-check` scans for the First Playable gate, so a report left only in
the conversation does not count as evidence there.

Ask before writing: "May I write this playtest report to
`plan/playtests/playtest-<date>-<focus>.md`?" Create `plan/playtests/` if missing.
