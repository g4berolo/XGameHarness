# 山脊（代号）— Game Development Project

> harness（skills / agents / hooks / 流程规则）由 `XGameHarness` 插件市场提供
> （`g4berolo/XGameHarness` — `game-studio-core`）。R2 中文输出规则由插件
> UserPromptSubmit hook 逐条注入。通用流程文档见插件 docs/ 目录，需要时按需 Read。

> ⚠ **这是读本实验室的假项目**（harness 仓 `labs/digest-lab/`），只用来测
> `/design-system` `/write-digest` `/design-review` 和几个子 agent。
> 每次实验前整个目录会被重建，**别把它当真项目积累东西**。

## Technology Stack

- **Engine**: 未定（本实验不涉及引擎，不跑 `/setup-engine`）
- **Language**: 未定
- **Version Control**: Git（本地，没有远端）

> 首次使用？运行 `/start` 查看项目状态并开始工作。

## Project Structure

harness 项目契约（hooks / skills 依赖的目录约定）：`design/gdd/`（GDD）、
`design/digest/`（读本）、`plan/`（sprint / milestone）、`plan/stage.md`（阶段 SoT）、
`team/session-state/{identity}/`、`team/session-logs/{identity}/`、
`team/memo/{recipient}/{open,closed}/`、`docs/architecture/`（ADR）。

## Collaboration Protocol

**User-driven collaboration, not autonomous execution.**
Every task follows: **Question -> Options -> Decision -> Draft -> Approval**

- Agents MUST ask "May I write this to [filepath]?" before using Write/Edit tools
- Agents MUST show drafts or summaries before requesting approval
- Multi-file changes require explicit approval for the full changeset
- No commits without user instruction

## Language

**中文为主**。所有用户面向(user-facing)文本默认中文回复。完整 R2 词类细化规则由
XGameHarness 插件 hook 每条 prompt 自动注入；被用户指出违规时：立即承认 + 重写违规
段落 + 不辩解。
