# <ProjectName> — Game Development Project

> harness（skills / agents / hooks / 流程规则）由 `XGameHarness` 插件市场提供
> （`g4berolo/XGameHarness` — `game-studio-core` + `unreal-pack`），随该仓库
> 发布新版本后显式更新。R2 中文输出规则由插件 UserPromptSubmit hook 逐条注入。
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
`plan/`（sprint / milestone）、`plan/stage.md`（阶段 SoT：frontmatter
`current_stage` + sub-phase 矩阵）、`team/session-state/{identity}/`、
`team/session-logs/{identity}/`、`team/memo/{recipient}/{open,closed}/`、
`docs/architecture/`（ADR）。目录按需 lazy 创建，缺失时 hooks 静默降级。

## Technical Preferences

<!-- @.claude/docs/technical-preferences.md -->

## Coding Standards

编辑源码前，按文件路径读取 `.claude/rules/` 中匹配的规则。UE C++ 的排版约定位于
`.claude/rules/ue-cpp-readability.md`（随 unreal-pack 同步）。项目另有编码规范或
`.clang-format` 时，优先采用适用于当前文件的项目约定。

## Collaboration Protocol

**User-directed work with evidence-based delivery.**
Complete the requested work, verify it, and report results and unresolved decisions.

- Complete reversible file edits already authorized by the task without asking again
- Ask when a material product decision or missing information blocks correct work
- Obtain authorization for external publication or destructive changes beyond the task
- No commits without user instruction

## Language

**中文为主**。所有用户面向(user-facing)文本默认中文回复。完整 R2 词类细化规则由
XGameHarness 插件 hook 每条 prompt 自动注入；被用户指出违规时：立即承认 + 重写违规
段落 + 不辩解。


## AI执行与人工任务分离

起草、拆解、估算、执行或汇报任务时，遵守本插件 `docs/task-execution.md`（相对插件根目录）。实时看板用纯任务名 title 和独立 kind/category/sprintId 字段，显示编号 sprintCode 由服务器生成；文件型计划在 Task 标题标[AI]或[HUMAN]，编号单列并保留历史 ID。人工操作/审核与AI制作使用独立ID、验收及状态；文件型 Sprint 末尾集中列人工项，但前置人工依赖仍按需先执行。AI完成不等于人工批准或Sprint完成，分别统计进度。不得升级时静默重写既有项目计划。
