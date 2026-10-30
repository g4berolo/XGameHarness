# Sprint 与 XGS 格式核对（2026-10-30）

NineHundred-Civ7 的四份现有计划使用 SNN-名称.md，任务分布在中文标题和独立
Must Have 下。XGS 原先只发现 sprint-N.md，只读取 Tasks 段，因此返回零期零任务。
项目迁移元数据记录 Core 1.3.1，与本次修改前源码版本一致；未取得生成对话证据，
不能断言是旧技能或未调用技能造成。当前 skill 已规定规范文件名和 Tasks，实际文件
偏离该约定；但共享模板和 fallback 都只有整轮 DoD，未满足 XGS 的逐任务状态关联。

修正 Core 至 1.3.2，两宿主清单保持一致：sprint-plan 增加 XGS 格式契约与写后检查，
模板逐任务 DoD 示例与稳定 ID 对应；producer 要求读取技能和模板。更新原计划须保留
文件名、ID、证据和状态，不能自动补验收批准。未编辑 vendored archify、个人配置或
项目原文件。技能与模板共享，因此 Claude 与 Codex 使用同一约定。

配套 XGS 源码兼容旧文件及表头、明确提示未识别文件、保留状态说明；验收判据仍为
关联 DoD。实际读取四期共 39 个去重任务，缺逐任务 DoD 的状态保持未知。

验证：Python 3.12 环境补齐 PATH 后 unittest 33 项，30 通过、3 跳过；validate.py
通过（3 插件、29 skills、双宿主版本与 hooks）。XGS 专项回归用实际模板替换期号后
确认四个示例任务均关联 DoD，源码构建和组件渲染通过。skill-creator 的 quick_validate.py
因运行环境缺 PyYAML 未执行成功，仓库打包验证及人工 frontmatter 检查已完成。
插件安装、hook 实际触发及游戏实测不属于这些验证结论；未提交、推送或发布。
