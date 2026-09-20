---
name: session-checkpoint
description: "保存或恢复游戏项目任务摘要、验证证据和下一步；适用于跨会话交接、长任务与上下文压缩。"
---

# 任务检查点

先读取本插件 `docs/codex-runtime.md` 中的记忆约定及项目 `.claude/team.json`。
Codex 与 Claude 共用团队目录。不要改动宿主的个人自动记忆文件。

1. 根据 Git 用户解析身份，无法解析时先解决映射，不写 `unknown` 公共目录。
2. 恢复：读取 active.md 与本任务摘要，再核验 Git HEAD、工作区和相关文件。
   旧「下一步」仅是线索。缺失证据不能改写为成功。
3. 保存：并发任务写 `team/session-state/{identity}/sessions/{session-key}.md`。
   Codex SessionStart 会给出 session-key；未提供时使用任务唯一短标识，不抢写 active.md。
4. 摘要只记录目标、约束、文件、已完成事实、验证命令及结果、未验证项、阻碍、下一步。
   长期决策归 ADR，设计归 GDD，摘要引用它们，不复制整段历史。
5. 单任务或明确交接时才合并 active.md。自动机械检查点在 `.codex/state/sessions/`，
   可恢复未提交摘要但不能替代语义总结。团队共享摘要是否提交遵循当前用户授权。

输出保存位置、已验证到哪一步及继续任务所需的一件事。
