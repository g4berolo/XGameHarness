---
name: start
description: "Project status dashboard and task-based routing for professional developers."
argument-hint: "[no arguments]"
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Quick Start — Professional Entry Point

This skill provides a concise project status overview and routes developers
to the right workflow based on what they need to accomplish this session.

Assumes all participants are professional developers with clear objectives.

---

## Workflow

### 1. Detect Project State (Silent)

Before showing anything, silently gather project context. Do NOT display
raw detection results — they feed into the status summary in Step 2.

Check:
- **Engine configured?** The single source of truth is the project root `CLAUDE.md`
  Technology Stack block. The engine is NOT set if the `- **Engine**:` line is
  missing, empty, or still holds the template placeholder `<engine + version>`.
  `.claude/docs/technical-preferences.md` is only created by `/setup-engine`, so
  treat its absence as "not configured" rather than an error — do not require it.
- **Game concept exists?** Check for `design/gdd/game-concept.md`.
- **Source code exists?** Glob for source files in `client/Source/` (UE5 project)
  for `*.cpp`/`*.h`. Count them.
- **Prototypes exist?** Check for subdirectories in `prototypes/`.
- **Design docs exist?** Count markdown files in `design/gdd/`.
- **Systems index?** Check for `design/gdd/systems-index.md`.
- **Stage SoT?** Read `plan/stage.txt` (single line current stage) and optionally
  `plan/stage.md` (full sub-phase table).
- **Planning artifacts?** Check for files in `plan/sprints/` or `plan/milestones/`.
- **Session state?** Resolve identity from `git config user.name` via `.claude/team.json`
  and check `team/session-state/{identity}/active.md`.
- **Memo inbox?** Glob `team/memo/{identity}/open/*.md` (exclude `.gitkeep`) to detect
  unprocessed cross-developer pings. For each, read frontmatter `from` + first `# ...`
  heading for dashboard preview. Protocol detail: `${CLAUDE_PLUGIN_ROOT}/docs/team-memo-protocol.md`.

Store findings internally for Step 2.

---

### 2. Show Project Status Summary

Display a compact status dashboard in Chinese. Show only facts, no tutorials.

Format:

```
=== [项目目录名] 项目状态 ===   (用当前项目根目录名替换)
引擎: [具体引擎] 或 [未配置]
源码: N 个文件    GDD: N 篇    原型: N 个

待完成:
  - 引擎未配置           (only show lines that apply)
  - 游戏概念未创建
  - 系统索引未创建
```

If session state file exists, add:
```
上次工作状态: team/session-state/{identity}/active.md
  (建议先读取此文件恢复上下文)
```

If `team/memo/{identity}/open/` has N > 0 unprocessed memo (excluding `.gitkeep`), add:
```
📬 待处理 memo (N 条):
  - {from} → {first heading line}  ({memo path})
  - ...
```
Recipient may handle now (`git mv` open → closed when done) or defer.

If the project is fully configured and has no critical gaps, show a clean
status with no "待完成" section.

---

### 2.5 Surface R2 Language Tag

钩子 `inject-language-reminder.py` 每轮已把完整 R2 规则注入上下文，但只注入、
不校验输出。用户可在消息前缀加标签，作为生成点的高显著触发，指向已注入的规则
——比纯被动注入更强。

在状态 dashboard 后、问任务类型前，显示一次（仅提示，不阻断）：

> 📌 **R2 强化（可选）**：消息前缀加 `【中文R2】` 即可。规则正文钩子已注入，
> 标签只作生成前强提醒。术语密集任务可用 `【中文R2·严格】`。

---

### 3. Ask Task Type

Use AskUserQuestion to present task-oriented options. All options are
available to everyone — no role gating in this version.

Question (in Chinese): "这次要做什么？"

Options:

**A) 项目基建** — 引擎配置、技术选型、架构决策
**B) 设计文档** — 概念设计、系统拆解、GDD 编写
**C) 编码开发** — 实现功能、修复 bug、编写测试
**D) 项目分析** — 阶段检测、差距分析、范围审查

Wait for the user's answer.

---

### 4. Prerequisite Check + Routing

Based on the user's choice and the project state from Step 1, check
prerequisites and recommend the next action.

#### A) 项目基建

Recommended commands based on state:
- Engine not configured → `/setup-engine`
- Engine configured, no ADRs → suggest creating architecture decisions
- Engine configured, ADRs exist → project infrastructure is ready,
  suggest moving to design or coding

#### B) 设计文档

Recommended commands based on state:
- No game concept → `/brainstorm` to create one
- Concept exists, no systems index → `/map-systems` to decompose
- Systems index exists, GDDs incomplete → `/design-system [system-name]`
- All GDDs complete → suggest `/scope-check` or moving to coding

#### C) 编码开发

Prerequisites check:
- Engine not configured → **blocker**: "引擎未配置，建议先运行 `/setup-engine`"
- No game concept → **warning**: "游戏概念未创建，建议先完成设计文档"
- Prerequisites met → "引擎和设计文档就绪，可以直接开始。告诉我你要实现什么功能。"

#### D) 项目分析

Recommend directly:
- `/project-stage-detect` — full gap analysis
- `/scope-check` — if checking scope of existing work
- `/code-review [file]` — if reviewing code quality

---

### 5. Hand Off

Present the recommended command(s) and let the user decide. Do NOT
auto-execute any skill. The user invokes the next step themselves or
asks you to run it.

**Subagent hint**（当推荐的工作适合 subagent 加速时主动提示）:

如果用户选 B (设计文档) / C (编码) / D (分析) 且任务匹配下列模式，必须在 hand-off 文本中显式列出推荐的 subagent prompt：

agent 名必须带插件前缀（`game-studio-core:`），传裸名 Agent tool 会直接报
`Agent type not found`：

| 任务模式 | 推荐 subagent | prompt 模板示例 |
|---|---|---|
| 跑数值算例 / 公式 audit | `game-studio-core:systems-designer` | `spawn game-studio-core:systems-designer subagent: ...` |
| 商人 sink / 掉落 / 经济曲线 | `game-studio-core:economy-designer` | `spawn game-studio-core:economy-designer subagent: ...` |
| 核心循环 / 系统顶层框架 | `game-studio-core:game-designer` | `spawn game-studio-core:game-designer subagent: ...` |
| 关卡 layout / encounter | `game-studio-core:level-designer` | `spawn game-studio-core:level-designer subagent: ...` |
| 角色 / 对话 / 叙事架构 | `game-studio-core:narrative-director` | `spawn game-studio-core:narrative-director subagent: ...` |

**关键**: subagent 不自动触发，用户必须显式命名 — 详见 [agent-process-rules.md R4](../../docs/agent-process-rules.md#r4-subagent-invocation-pattern)。如果用户没意识到这点，主 agent 会接管任务并自处理（默认行为），错失 subagent 优势。

---

## Edge Cases

- **Session state exists**: Prioritize recovery. Show the state file path
  and suggest reading it before starting new work. Still show task options
  in case the user wants to start something different.
- **Project fully configured + code exists**: Skip "待完成" section entirely.
  Show clean status and go straight to task selection.
- **User's task doesn't fit any option**: Let them describe it freely.
  The 4 categories are shortcuts, not constraints.
- **Memo inbox has open items**: Surface in dashboard prominently but do NOT
  force handling. Recipient decides whether to process now or continue with
  their planned work. If they choose to handle a memo, read the memo file,
  execute the requested change, then `git mv` open → closed and commit
  with message `close memo: {topic}`.

---

## Future: Role-Based Extension

> This section is a design note for future implementation. Do not act on
> it in the current version.

When role assignments are finalized, this skill can be extended:

- Accept role parameter: `/start --role=programmer|designer|artist|producer`
- Filter task options by role:
  - **Artist**: Only show design doc reading + asset pipeline tasks.
    Scope to `assets/` and `design/` directories only.
  - **Designer**: Show design docs + project analysis. No coding tasks.
  - **Programmer**: Show all options.
  - **Producer**: Show project analysis + sprint planning.
- Role can also be auto-detected from a future team config file.
- Access control (e.g., artists cannot access root) is handled at the
  repository/permissions level, not by this skill.

---

## Collaborative Protocol

1. **Show status first** — developers see where the project stands immediately
2. **Ask task, not experience** — respect that everyone knows their job
3. **Check prerequisites** — flag blockers, don't lecture
4. **User decides** — recommend, never auto-execute
5. **Adapt** — if the user's task doesn't fit a category, listen and route
