---
name: handbook
description: "XGameHarness 操作手册查询。当用户问'我想做X该用什么/怎么做'（写策划案、排sprint、代码评审、新项目接入、加插件、rules同步、故障排查等），检索手册给出对应 skill/agent 和操作步骤。"
argument-hint: "[关键词或问题]"
user-invocable: true
allowed-tools: Read, Grep, Glob
---

# /handbook — 操作手册查询

1. Read `${CLAUDE_PLUGIN_ROOT}/docs/HANDBOOK.md`（本插件自带）。
2. 按用户给的关键词 / 问题在手册中定位对应条目：
   - 「做什么」类问题（写策划案 / 排期 / 评审 / 建模 / 接入新项目…）→ § 1 任务表，
     给出 skill 名或 spawn 模板 + 一句说明
   - 机制类问题（hooks 何时触发 / rules 怎么管 / 插件怎么加）→ § 2/4/5
   - 报错排障 → § 6
3. 回答要**短**：直接给「用 `/xxx`」或「spawn xxx subagent: <任务模板>」+ 两三句
   要点；用户要细节再展开或引导其读手册对应章节。
4. 手册没覆盖的问题：如实说没有现成条目，按你对 harness 结构的了解回答，并提示
   可把该场景补进 HANDBOOK.md（harness 仓库 `plugins/game-studio-core/docs/`）。
5. 无参数调用时：输出 § 1 的分组目录（立项规划 / 写策划案 / 写代码 / 美术 /
   运维），让用户挑。
