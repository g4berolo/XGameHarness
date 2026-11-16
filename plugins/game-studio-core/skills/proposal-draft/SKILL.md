---
name: proposal-draft
description: "为多人讨论起草GDD、系统设计或Sprint候选，提供易读读本和技术原文；不自动批准或覆盖正式文档。"
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion
---

# 候选方案起草

参数：主题，分类 gdd / systems / sprint。

需要把讨论整理后提交 XGS、汇总评论或修订已有候选时，使用 [proposal-review](../proposal-review/SKILL.md)。本技能专注起草；提交通过 XGS 原生工具完成，不让用户操作 JSON。

运行时适配：读取本插件 `docs/codex-runtime.md`。Codex 用 `$proposal-draft` 或读取本文件，Claude 使用插件技能入口；相对路径从本文件向上两级为插件根。

1. 读取现有正式设计、相关决策及当前Sprint，核对设计前提。区分已定事实、建议和待决定事项。
2. 与用户讨论2–4种方案及取舍，收敛到待讨论候选；不能把讨论中的偏好写成团队已批准决定。
3. 依照 `rules/design-docs.md` 和 write-digest 技能的读本规则，写出便于其他专业同事阅读的完整说明：目的、运行方式、取舍、例子及需要讨论的问题。不要只是技术原文摘要；具体数值只以原文为准。
4. 技术原文遵守 design-system 的结构；Sprint遵守 sprint-plan 和 `docs/task-execution.md`，分离[AI]与[HUMAN]任务及验收，保留独立人工审核。
5. 将读本与技术原文保存为不覆盖人工改动的 Markdown 草稿；开发者不需要查看或编写 JSON。
6. 用户要求提交时按 proposal-review 技能调用 XGS 原生 xgs_review 工具。无需 Computer Use 或手工导入。工具未提供时说明需更新客户端/Harness，保留 Markdown 草稿，不能声称已发布。
7. 汇总讨论时引用候选版本和意见作者，保留分歧，不虚构评论、身份或批准。新版本不能把旧版意见当作新版认可。
8. 只有负责人在XGS预览正式文档并明确采纳后，才转换正式文档并归档候选。AI不得直接编辑 `team/reviews/`、伪造采纳记录或修改正式GDD来绕过此流程。

本地草稿即使同步到其他机器，也不代表已进入评审或已获认可。以原生工具确认的候选编号和版本为提交证据。
