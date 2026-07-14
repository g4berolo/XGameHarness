# <ProjectName> — Game Development Project

> harness（skills / agents / hooks / 流程规则）由 `XGameHarness` 插件市场提供
> （`g4berolo/XGameHarness` — `game-studio-core` + `unreal-pack`），随该仓库
> 每次 commit 自动更新。R2 中文输出规则由插件 UserPromptSubmit hook 逐条注入。
> 通用流程文档（agent-process-rules / context-management / team-memo-protocol /
> rules-mechanism）见插件 docs/ 目录，需要时按需 Read。

## Technology Stack

- **Engine**: <engine + version>（UE 项目跑 `/setup-engine` 生成 engine-reference）
- **Language**: <languages>
- **Version Control**: Git

## Engine Version Reference

<!-- UE 项目: @docs/engine-reference/unreal/VERSION.md -->

> 首次使用？运行 `/start` 查看项目状态并开始工作。

## Project Structure

<!-- 写项目自己的 directory-structure 后引入: @.claude/docs/directory-structure.md -->

harness 项目契约（hooks / skills 依赖的目录约定）：`design/gdd/`（GDD）、
`plan/`（sprint / milestone / stage.md）、`team/session-state/{identity}/`、
`team/session-logs/{identity}/`、`team/memo/{recipient}/{open,closed}/`、
`docs/architecture/`（ADR）。目录按需 lazy 创建，缺失时 hooks 静默降级。

## Technical Preferences

<!-- @.claude/docs/technical-preferences.md -->

## Coding Standards

<!-- @.claude/docs/coding-standards.md -->

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
