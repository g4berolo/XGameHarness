---
name: proposal-draft
description: "为多人讨论起草GDD、系统设计或Sprint候选，提供易读读本和技术原文；不自动批准或覆盖正式文档。"
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion
---

# 候选方案起草

参数：主题，分类 gdd / systems / sprint。

运行时适配：读取本插件 `docs/codex-runtime.md`。Codex 用 `$proposal-draft` 或读取本文件，Claude 使用插件技能入口；相对路径从本文件向上两级为插件根。

1. 读取现有正式设计、相关决策及当前Sprint，核对设计前提。区分已定事实、建议和待决定事项。
2. 与用户讨论2–4种方案及取舍，收敛到待讨论候选；不能把讨论中的偏好写成团队已批准决定。
3. 依照 `rules/design-docs.md` 和 write-digest 技能的读本规则，写出便于其他专业同事阅读的完整说明：目的、运行方式、取舍、例子及需要讨论的问题。不要只是技术原文摘要；具体数值只以原文为准。
4. 技术原文遵守 design-system 的结构；Sprint遵守 sprint-plan 和 `docs/task-execution.md`，分离[AI]与[HUMAN]任务及验收，保留独立人工审核。
5. 将候选存为 `design/proposals/<唯一主题编号>.draft.json`，字段为 `kind`、`title`、`reader`、`source`，后三者均为字符串。reader/source使用Markdown。不得覆盖已有草稿，必须先读并询问是修订还是新候选。
6. 告知用户在XGS对应看板的“评审”页签导入JSON，检查读本与原文后点击“发布候选”。导入本身不会发布。发布者为该候选负责人，所有当前项目成员可以评论和回复，无指定评审人。
7. 汇总讨论时引用候选版本和意见作者，保留分歧，不虚构评论、身份或批准。新版本不能把旧版意见当作新版认可。
8. 只有负责人在XGS预览正式文档并明确采纳后，才转换正式文档并归档候选。AI不得直接编辑 `team/reviews/`、伪造采纳记录或修改正式GDD来绕过此流程。

候选JSON是待发布草稿，即使文件经项目同步到其他机器，也不代表已进入评审或已获认可。无法访问XGS评审接口时必须如实报告，由用户导入发布；不要声称其他成员已收到。
