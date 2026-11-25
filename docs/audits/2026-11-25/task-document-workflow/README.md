# 设计起草与任务资料关联验证

2026-11-25，基于 origin/main ba669f1 的独立工作树。game-studio-core 两宿主清单准备为 1.3.15；未提交、推送、安装升级。原主工作区的未提交内容保留。

新增共用规则 docs/design-delivery.md，接入 proposal-draft、proposal-review、design-system、write-digest、sprint-plan、brainstorm、map-systems、reverse-document。明确一次选择草案或直接正式、实际文件路径、任务目标核对、候选ID/版本绑定、当前任务修订证据、跨作者指定审批人采纳与真实发布后验收。

- python -m unittest discover -s tests -v：37项，4项因环境跳过，其余通过。
- python scripts/validate.py：3插件、32技能与两宿主版本/Hook命令通过。
- skill-creator quick_validate.py：8个修改技能通过。校验器所需PyYAML仅安装在独立tmp依赖目录。
- 独立前向推演覆盖模糊起草请求、直接正式且不提交、候选v1→v2及不同作者审批人遇到待定评论；已修复证据失效顺序、草稿/读本强制正式路径、恢复状态和任务编号主题冲突。

这是源码、格式和静态技能推演验证；未运行真实收费模型对话，未声称插件安装、Hook实际触发或同事设备已升级。XGS接口和UI验证在XGameHarnessUI对应2026-11-25/task-document-workflow审计目录。
