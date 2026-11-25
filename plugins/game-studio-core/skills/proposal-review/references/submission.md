# 原生评审工具调用

XGS 为 Claude 和 Codex 提供同一个 `xgs_review` 工具，可能带 MCP 服务名前缀。参数是内部协议，不向用户展示 JSON。

## 操作

| action | 用途与必要参数 |
| --- | --- |
| list | 当前项目候选摘要及当前身份 |
| get | `id`，读取该候选全部版本、读本和评论 |
| submit | `operationId`、`kind`、`title`、`reader`、`source`；可用 `readerFile`/`sourceFile` 代替正文 |
| revise | `id`、`operationId`、最新 `revision`/`version`、`title`、读本和原文；只有负责人可改 |
| resolve | `id`、`commentId`、`operationId`、`status`、`expectedStatus`；任意项目成员明确处理评论，三状态为pending/merged/cancelled |
| comment | `id`、`operationId`、评论所对应 `version`、`body`；回复另传 `replyTo` |

`kind` 为 gdd、systems 或 sprint。`operationId` 是每次逻辑操作的唯一编号，只用字母、数字、下划线和短横线，最长80字符；网络失败重试复用它。服务端决定真实作者，不能传 owner 或伪造意见。正式 adopt/归档不开放给模型工具。

## 图示

读本含相对 HTML/SVG 链接时，优先传 readerFile，让工具按该 Markdown 所在目录读取并嵌入图内容；直接传 reader 字符串时，链接必须是完整的项目相对路径。新增和修订后用 get 确认图内容已保存在读本中，不能只核对链接文字。不要留下依赖原设备或原草稿目录的裸文件名链接；技术原文中的图链接也应使用项目相对路径，并确保评审读本包含对应图示。

读本内直接使用 svg 代码围栏。完整 HTML 文档使用 html 围栏。现有 archify 文件通过 `diagrams` 附加，每项包含 `path` 和可选 `caption`，工具会将完整内容嵌入读本并随候选同步；最多4项，每个文件不超过1MB，合并读本不超过1000000个UTF-16码元。路径必须在当前项目内，不能指向隐藏配置、凭据或项目外文件。

优先将图放在解释对应机制的小节。若通过 diagrams 追加在文末，在正文明确图注与所解释内容的关系。不要仅交本机绝对路径，也不要让其他评审人自行找图。HTML 安全预览保留文档和内联SVG，不运行脚本或访问外网；需要动态图内操作时如实说明限制。

## 提交与失败

新增：submit → 用回执 id 调用 get → 核对标题、读本、原文及版本。修订：get 旧案 → 使用同一 id 和最新 revision/version 调用 revise → 再 get 核对。用户选择修订旧案后继续执行整个流程；不能以保存本地 Markdown/JSON 代替修订，也不能创建同名案绕过权限。任何一步失败都明确尚未提交或尚未确认，不要求开发者手动导入、粘贴正文或点击发布。

先核对项目、分类、标题、读本与原文一致，再调用。成功回复中的编号、版本及位置才是提交依据。冲突先重新 get 并整理最新意见，不覆盖别人更新。工具缺失时提醒更新 XGS/Harness 并新开服务器模式对话，保留 Markdown 草稿，不生成用户必须操作的 JSON，不用 Computer Use 绕过。

GDD/系统正式路径为 design/gdd/，同名读本为 design/digest/；Sprint为 plan/sprints/。候选负责人或已绑定任务的当前指定审批人在 XGS 预览差异并明确采纳，服务器确认事务成功后候选才归档。本技能可以准备目标和采纳说明，不替人决定。

所有评论（含回复、旧版意见）都必须脱离待定，才允许负责人采纳或提出者撤回。无状态的旧评论视为待定。处理保留真实作者及历史；并发冲突刷新后重试，不默默覆盖。撤回和采纳仍是界面人工操作。

## 与任务绑定

按 [设计交付规则](../../../docs/design-delivery.md)，候选负责人在提交/修订回读后，通过看板 task.update 写入 reviewId、reviewVersion；需要正式交付时设 requiresAdoption。绑定不会自动验收。以服务器返回的 capabilities.canAdopt 判定当前身份的采纳权限；旧服务无该能力时按实际回执说明升级需求。
