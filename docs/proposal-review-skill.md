# 整理并提交评审技能

## 1.3.6 评论处理规则（本地未发布）

补充 proposal-draft 提交闭环：用户选择修订旧案后，技能在当前任务中直接衔接 proposal-review，用同一候选 id 调用 revise 并 get 核验；新增也须 submit 后 get 核验。删除“优先直接编写入口”的歧义，明确不把导入 JSON、粘贴正文或手动发布交还开发者。移除 proposal-draft 仅列文件工具的 allowed-tools 清单，避免原生 MCP 入口未包含在声明中。工具不可用时报告未提交及具体阻碍，不能改走手工导入。本次并入尚未发布的 1.3.6。

新增待定、通过已合并、已取消三态；旧评论默认待定，任意项目成员可处理并留下真实身份记录。技能只在用户明确要求处理对应意见时调用原生 resolve，不能为采纳或撤回而自动清空待定项。所有版本的评论及回复处理完毕后，负责人才能在界面采纳或撤回；技能不开放采纳或撤回工具动作。需要匹配本轮 XGS 客户端与服务端更新，尚未部署。

本轮仓库校验通过（3 插件、31 技能）；单元测试 33 项，30 通过、3 环境跳过。共享技能及双宿主版本已同步至 1.3.6。skill-creator 可选 quick_validate 因缺少 PyYAML 未完成，不计为通过。未进行真实模型操作、插件安装或 hook 实测。

2026-11-16：新增共享 `proposal-review`，补齐起草后的提交、分版本评论汇总及修订交接。原 `proposal-draft` 保留起草用途。操作手册已加入发现入口，Claude/Codex 的 core 清单版本均为 1.3.5；其他插件不变。

## XGS 使用

更新 Harness 后新开对话，在技能菜单选择 `game-studio-core:proposal-review`，或发送“使用 proposal-review，把当前讨论整理成系统候选并提交评审”。Codex 也可用 `$proposal-review`，Claude 插件入口为 `/game-studio-core:proposal-review`。

读本采用插件 GDD 规则：完整、帮助理解、简洁，按档位编号，机制配图，正文白话，精确数值只在原文。Sprint 遵守相同可读性原则并保持 AI 制作与人工审核分离。

XGS 通过原生 xgs_review 工具提交，不使用 Computer Use，不让用户操作 JSON。支持读取 Markdown 并将 archify HTML/SVG 图随候选保存，其他设备不依赖本机文件。工具未提供时明确需要更新客户端/Harness并新开服务器模式对话；保留 Markdown，不冒充已发布。正式采纳仍由负责人操作。

HTML与导入SVG在隔离预览中保留图内容和样式，不运行脚本或外联；SVG代码围栏继续遵守既有主题绘图规范。相关XGS实现及隔离证据见UI仓 docs/audits/2026-11-16/native-review/。

## 验证与交付状态

- `python scripts/validate.py`：3 个插件、31 个技能，双宿主版本与包装检查通过。
- `python -m unittest discover -s tests -v`：33 项，30 项通过、3 项按环境跳过。
- XGS 的实际 `inspectProject` 读取隔离测试目录：发现 `game-studio-core:proposal-review` 及中文描述；未造身份或操作真实项目。
- XGS `checkParity`：8 项检查、0 个阻塞；既有子 agent/hook 的结构差异提示不作为运行验收。
- skill-creator 的可选 `quick_validate.py` 因宿主缺少 PyYAML 未运行成功；不计为通过。仓库必需校验已完成。
- XGS已验证临时空账号目录下的内置Codex工具发现、内置Claude工具连接，以及隔离Git/模拟身份的界面提交与采纳；零模型轮次。未进行真实模型调用、真实账号提交、插件安装、hook触发或生产采纳验收。当前修改仅在本地仓库，未提交推送或发布市场包；其他设备需分发更新后才可发现新技能。


## 1.3.5 分发回执

发行源码5ded5e1已推送origin/main。市场ZIP已生成并解包通过3插件31技能包装校验；大小与SHA256见proposal-review-1.3.5-release.json。新技能需对应XGS原生工具版本配合，新开服务器模式对话使用。未自动修改消费项目、个人配置或生产数据。
